#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
# Copyright (c) 2026 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""Keysight B2910BL single-channel source measure unit support."""

from __future__ import annotations

import logging
import math
import re
import time
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from numbers import Real
from typing import Any

from pymeasure.instruments import (
    AdapterType,
    Channel,
    Instrument,
    InstrumentProperty,
    SCPIMixin,
)
from pymeasure.instruments.validators import strict_discrete_case_insensitive_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

VOLTAGE_RANGE_VALUES = (0.2, 2.0, 20.0, 200.0)
CURRENT_RANGE_VALUES = (10e-9, 100e-9, 1e-6, 10e-6, 100e-6, 1e-3, 10e-3, 100e-3, 1.0, 1.5)
SOURCE_CURRENT_RANGE_VALUES = CURRENT_RANGE_VALUES
SOURCE_VOLTAGE_RANGE_VALUES = VOLTAGE_RANGE_VALUES
MAX_VOLTAGE = 210.0
MAX_CURRENT = 1.515
HIGH_VOLTAGE_THRESHOLD = 42.0
MAX_SWEEP_POINTS = 100_000
MISSING_SENTINEL = 9.91e37
POSITIVE_INFINITY_SENTINEL = 9.90e37
NEGATIVE_INFINITY_SENTINEL = -9.90e37


@dataclass(frozen=True)
class B2910BLReading:
    """Store one paired voltage, current, source-setting, and compliance reading."""

    voltage_V: float
    current_A: float
    source_setting: float
    compliance: bool


@dataclass(frozen=True)
class B2910BLSweepPoint:
    """Store a requested sweep setpoint and its paired instrument reading."""

    requested_setpoint: float
    voltage_V: float
    current_A: float
    source_setting: float
    compliance: bool


class SweepShutdownError(RuntimeError):
    """Report a scan failure together with a failure to confirm output shutdown."""

    def __init__(self, scan_error: BaseException, shutdown_error: BaseException):
        self.scan_error = scan_error
        self.shutdown_error = shutdown_error
        super().__init__(
            f"The sweep failed ({scan_error}); output shutdown also failed "
            f"({shutdown_error})."
        )


def _finite_range(value: Any, bounds: tuple[float, float]) -> float:
    """Reject booleans and non-finite values before applying a strict range."""
    if isinstance(value, bool):
        raise TypeError(f"Expected a finite number, got {value!r}.")
    if not isinstance(value, (Real, Decimal)):
        raise TypeError(f"Expected a finite number, got {value!r}.")
    try:
        number = float(value)
    except OverflowError as exc:
        raise ValueError(f"Expected a finite number, got {value!r}.") from exc
    if not math.isfinite(number):
        raise ValueError(f"Expected a finite number, got {value!r}.")
    return float(strict_range(number, bounds))


def _positive_finite(value: Any, maximum: float) -> float:
    """Validate a positive finite compliance value."""
    number = _finite_range(value, (0.0, maximum))
    if number <= 0:
        raise ValueError("Compliance must be greater than zero.")
    return number


def _strict_bool(value: Any, values: Any = None) -> bool:
    """Accept actual booleans only."""
    if not isinstance(value, bool):
        raise TypeError(f"Expected True or False, got {value!r}.")
    return bool(strict_discrete_case_insensitive_set(value, (False, True)))


def _strict_mode(value: Any, values: Any = None) -> str:
    """Validate a voltage or current source mode and return its SCPI spelling."""
    return strict_discrete_case_insensitive_set(value, ("VOLT", "CURR"))


def _strict_off_mode(value: Any, values: Any = None) -> str:
    """Validate an output-off mode and return its SCPI spelling."""
    return strict_discrete_case_insensitive_set(value, ("ZERO", "HIZ", "NORM"))


def _strict_range(value: Any, values: tuple[float, ...]) -> float:
    """Accept one of the documented B2910BL measurement or source ranges."""
    number = _finite_range(value, (min(values), max(values)))
    if number not in values:
        raise ValueError(f"Range {number:g} is not one of {values!r}.")
    return number


def _parse_float(value: Any) -> float:
    """Parse one finite numeric value returned by the instrument."""
    try:
        number = float(value)
    except (OverflowError, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid numeric response {value!r}.") from exc
    if not math.isfinite(number):
        raise ValueError(f"Non-finite numeric response {value!r}.")
    return number


def _parse_mode(value: Any) -> str:
    """Parse the instrument's source-mode response."""
    mode = str(value).strip().upper()
    if mode not in ("VOLT", "CURR"):
        raise ValueError(f"Invalid source-mode response {value!r}.")
    return mode


def _parse_off_mode(value: Any) -> str:
    """Parse the instrument's output-off-mode response."""
    mode = str(value).strip().upper()
    if mode not in ("ZERO", "HIZ", "NORM"):
        raise ValueError(f"Invalid output-off-mode response {value!r}.")
    return mode


def _parse_binary(value: Any) -> bool:
    """Parse a documented NR1 boolean response without truthy coercion."""
    response = str(value).strip()
    if not re.fullmatch(r"[+-]?\d+", response):
        raise ValueError(f"Expected an NR1 boolean response of 0 or 1, got {value!r}.")
    number = int(response)
    if number not in (0, 1):
        raise ValueError(f"Expected an NR1 boolean response of 0 or 1, got {value!r}.")
    return number == 1


def _parse_single_binary(values: list[str]) -> bool:
    """Parse one NR1 boolean and reject a comma-separated response."""
    if len(values) != 1:
        raise ValueError(f"Expected one NR1 boolean response, got {values!r}.")
    return _parse_binary(values[0])


def _parse_sample(response: str, expected_fields: int) -> tuple[float, ...]:
    """Parse an ASCII result and reject missing or overflow sentinel values."""
    fields = response.strip().split(",")
    if len(fields) != expected_fields or any(not field.strip() for field in fields):
        raise ValueError(
            f"Expected exactly {expected_fields} comma-separated ASCII values, "
            f"received {response!r}."
        )
    values: list[float] = []
    for field in fields:
        value = _parse_float(field.strip())
        if value == MISSING_SENTINEL:
            raise ValueError("The instrument reported its +9.91e37 missing-reading sentinel.")
        if value in (POSITIVE_INFINITY_SENTINEL, NEGATIVE_INFINITY_SENTINEL):
            raise OverflowError("The instrument reported an ASCII infinity sentinel.")
        values.append(value)
    return tuple(values)


def _range_selection(value: Any, ranges: tuple[float, ...]) -> float | None:
    """Validate an AUTO request or one documented numeric range."""
    if isinstance(value, str) and value.strip().upper() == "AUTO":
        return None
    return _strict_range(value, ranges)


def _validate_envelope(voltage: float, current: float) -> None:
    """Validate one operating point against the B2910BL DC output envelope."""
    if abs(voltage) > MAX_VOLTAGE:
        raise ValueError(f"Voltage magnitude exceeds the B2910BL limit of {MAX_VOLTAGE:g} V.")
    if abs(current) > MAX_CURRENT:
        raise ValueError(f"Current magnitude exceeds the B2910BL limit of {MAX_CURRENT:g} A.")
    current_limit = 1.515 if abs(voltage) <= 21.0 else 0.105
    if abs(current) > current_limit:
        raise ValueError(
            f"The B2910BL envelope allows at most {current_limit:g} A at "
            f"{abs(voltage):g} V."
        )


def _materialize_points(
    points: Iterable[float], minimum: float, maximum: float
) -> list[float]:
    """Validate a bounded sequence of finite setpoints before any instrument write."""
    if isinstance(points, (str, bytes)):
        raise TypeError("Sweep points must be a finite iterable of numbers.")
    try:
        iterator = iter(points)
    except TypeError as exc:
        raise TypeError("Sweep points must be an iterable of numbers.") from exc
    result: list[float] = []
    for point in iterator:
        if len(result) == MAX_SWEEP_POINTS:
            raise ValueError(f"A sweep may contain at most {MAX_SWEEP_POINTS} points.")
        result.append(_finite_range(point, (minimum, maximum)))
    if not result:
        raise ValueError("A sweep requires at least one point.")
    return result


def _validate_nplc(value: Any) -> float:
    """Validate the convenience API's conservative shared NPLC range."""
    return _finite_range(value, (0.01, 100.0))


def _validate_native_nplc(nplc: float, line_frequency: float) -> None:
    """Validate a native integration value against the selected line frequency."""
    if line_frequency == 50.0:
        valid = 0.0004 <= nplc <= 100.0
    elif line_frequency == 60.0:
        valid = 0.00048 <= nplc <= 120.0
    else:
        raise ValueError(
            f"Unsupported B2910BL line-frequency response {line_frequency:g} Hz."
        )
    if not valid:
        raise ValueError(
            f"NPLC {nplc:g} is outside the native range at {line_frequency:g} Hz."
        )


def _validate_settle(value: Any) -> float:
    """Validate a finite, non-negative host-side settling interval."""
    delay = _finite_range(value, (0.0, float("inf")))
    return delay


class B2910BLChannel(Channel):
    """Control the single source-measure channel on a Keysight B2910BL."""

    source_mode = Channel.control(
        ":SOURce{ch}:FUNCtion:MODE?",
        ":SOURce{ch}:FUNCtion:MODE %s",
        """Control the source mode (VOLT or CURR).""",
        validator=_strict_mode,
        cast=str,
        get_process=_parse_mode,
        check_set_errors=True,
        check_get_errors=True,
    )

    source_voltage = Channel.control(
        ":SOURce{ch}:VOLTage:LEVel:IMMediate:AMPLitude?",
        ":SOURce{ch}:VOLTage:LEVel:IMMediate:AMPLitude %g",
        """Control the voltage source level in Volts (finite from -210 to 210).""",
        validator=_finite_range,
        values=(-MAX_VOLTAGE, MAX_VOLTAGE),
        cast=float,
        get_process=_parse_float,
        check_set_errors=True,
        check_get_errors=True,
    )

    source_current = Channel.control(
        ":SOURce{ch}:CURRent:LEVel:IMMediate:AMPLitude?",
        ":SOURce{ch}:CURRent:LEVel:IMMediate:AMPLitude %g",
        """Control the current source level in Amperes (finite from -1.515 to 1.515).""",
        validator=_finite_range,
        values=(-MAX_CURRENT, MAX_CURRENT),
        cast=float,
        get_process=_parse_float,
        check_set_errors=True,
        check_get_errors=True,
    )

    voltage_limit = Channel.control(
        ":SENSe{ch}:VOLTage:DC:PROTection:LEVel?",
        ":SENSe{ch}:VOLTage:DC:PROTection:LEVel %g",
        """Control symmetric voltage compliance magnitude in Volts (finite above 0 to 210).""",
        validator=_positive_finite,
        values=MAX_VOLTAGE,
        cast=float,
        get_process=_parse_float,
        check_set_errors=True,
        check_get_errors=True,
    )

    current_limit = Channel.control(
        ":SENSe{ch}:CURRent:DC:PROTection:LEVel?",
        ":SENSe{ch}:CURRent:DC:PROTection:LEVel %g",
        """Control symmetric current compliance magnitude in Amperes (finite above 0 to 1.515).""",
        validator=_positive_finite,
        values=MAX_CURRENT,
        cast=float,
        get_process=_parse_float,
        check_set_errors=True,
        check_get_errors=True,
    )

    output_enabled = Channel.control(
        ":OUTPut{ch}?",
        ":OUTPut{ch} %d",
        """Control whether the channel output is enabled (boolean).""",
        validator=_strict_bool,
        values={False: 0, True: 1},
        map_values=True,
        cast=str,
        get_process=_parse_binary,
        get_process_list=_parse_single_binary,
        check_set_errors=True,
        check_get_errors=True,
    )

    source_voltage_range = Channel.control(
        ":SOURce{ch}:VOLTage:RANGe?",
        ":SOURce{ch}:VOLTage:RANGe %g",
        """Control the source voltage range in Volts (0.2, 2, 20, or 200).""",
        validator=_strict_range,
        values=SOURCE_VOLTAGE_RANGE_VALUES,
        cast=float,
        get_process=_parse_float,
        check_set_errors=True,
        check_get_errors=True,
    )

    source_current_range = Channel.control(
        ":SOURce{ch}:CURRent:RANGe?",
        ":SOURce{ch}:CURRent:RANGe %g",
        """Control the source current range in Amperes (10 nA through 1.5 A).""",
        validator=_strict_range,
        values=SOURCE_CURRENT_RANGE_VALUES,
        cast=float,
        get_process=_parse_float,
        check_set_errors=True,
        check_get_errors=True,
    )

    source_voltage_autorange = Channel.control(
        ":SOURce{ch}:VOLTage:RANGe:AUTO?",
        ":SOURce{ch}:VOLTage:RANGe:AUTO %d",
        """Control automatic source voltage ranging (boolean).""",
        validator=_strict_bool,
        values={False: 0, True: 1},
        map_values=True,
        cast=str,
        get_process=_parse_binary,
        get_process_list=_parse_single_binary,
        check_set_errors=True,
        check_get_errors=True,
    )

    source_current_autorange = Channel.control(
        ":SOURce{ch}:CURRent:RANGe:AUTO?",
        ":SOURce{ch}:CURRent:RANGe:AUTO %d",
        """Control automatic source current ranging (boolean).""",
        validator=_strict_bool,
        values={False: 0, True: 1},
        map_values=True,
        cast=str,
        get_process=_parse_binary,
        get_process_list=_parse_single_binary,
        check_set_errors=True,
        check_get_errors=True,
    )

    voltage_range = Channel.control(
        ":SENSe{ch}:VOLTage:DC:RANGe?",
        ":SENSe{ch}:VOLTage:DC:RANGe %g",
        """Control the voltage measurement range in Volts (0.2, 2, 20, or 200).""",
        validator=_strict_range,
        values=VOLTAGE_RANGE_VALUES,
        cast=float,
        get_process=_parse_float,
        check_set_errors=True,
        check_get_errors=True,
    )

    current_range = Channel.control(
        ":SENSe{ch}:CURRent:DC:RANGe?",
        ":SENSe{ch}:CURRent:DC:RANGe %g",
        """Control the current measurement range in Amperes (10 nA through 1.5 A).""",
        validator=_strict_range,
        values=CURRENT_RANGE_VALUES,
        cast=float,
        get_process=_parse_float,
        check_set_errors=True,
        check_get_errors=True,
    )

    voltage_autorange = Channel.control(
        ":SENSe{ch}:VOLTage:DC:RANGe:AUTO?",
        ":SENSe{ch}:VOLTage:DC:RANGe:AUTO %d",
        """Control automatic voltage measurement ranging (boolean).""",
        validator=_strict_bool,
        values={False: 0, True: 1},
        map_values=True,
        cast=str,
        get_process=_parse_binary,
        get_process_list=_parse_single_binary,
        check_set_errors=True,
        check_get_errors=True,
    )

    current_autorange = Channel.control(
        ":SENSe{ch}:CURRent:DC:RANGe:AUTO?",
        ":SENSe{ch}:CURRent:DC:RANGe:AUTO %d",
        """Control automatic current measurement ranging (boolean).""",
        validator=_strict_bool,
        values={False: 0, True: 1},
        map_values=True,
        cast=str,
        get_process=_parse_binary,
        get_process_list=_parse_single_binary,
        check_set_errors=True,
        check_get_errors=True,
    )

    nplc: InstrumentProperty[float] = Channel.control(
        ":SENSe{ch}:VOLTage:DC:NPLCycles?",
        ":SENSe{ch}:VOLTage:DC:NPLCycles %g",
        """Control shared integration time in power-line cycles (native range).

        Setting a fixed value disables automatic aperture and NPLC. The valid native range
        depends on the selected line frequency.
        """,
        validator=_finite_range,
        values=(0.0004, 120.0),
        cast=float,
        get_process=_parse_float,
        check_get_errors=True,
        check_set_errors=True,
    )

    nplc_autorange_enabled = Channel.control(
        ":SENSe{ch}:VOLTage:DC:NPLCycles:AUTO?",
        ":SENSe{ch}:VOLTage:DC:NPLCycles:AUTO %d",
        """Control automatic NPLC integration (common to all sense functions).""",
        validator=_strict_bool,
        values={False: 0, True: 1},
        map_values=True,
        cast=str,
        get_process=_parse_binary,
        get_process_list=_parse_single_binary,
        check_set_errors=True,
        check_get_errors=True,
    )

    aperture_autorange_enabled = Channel.control(
        ":SENSe{ch}:VOLTage:DC:APERture:AUTO?",
        ":SENSe{ch}:VOLTage:DC:APERture:AUTO %d",
        """Control automatic aperture integration (common to all sense functions).""",
        validator=_strict_bool,
        values={False: 0, True: 1},
        map_values=True,
        cast=str,
        get_process=_parse_binary,
        get_process_list=_parse_single_binary,
        check_set_errors=True,
        check_get_errors=True,
    )

    remote_sense_enabled = Channel.control(
        ":SENSe{ch}:REMote?",
        ":SENSe{ch}:REMote %d",
        """Control remote sensing (boolean).""",
        validator=_strict_bool,
        values={False: 0, True: 1},
        map_values=True,
        cast=str,
        get_process=_parse_binary,
        get_process_list=_parse_single_binary,
        check_set_errors=True,
        check_get_errors=True,
    )

    auto_output_on_enabled = Channel.control(
        ":OUTPut{ch}:ON:AUTO?",
        ":OUTPut{ch}:ON:AUTO %d",
        """Control automatic output-on behavior during READ or INIT (boolean).""",
        validator=_strict_bool,
        values={False: 0, True: 1},
        map_values=True,
        cast=str,
        get_process=_parse_binary,
        get_process_list=_parse_single_binary,
        check_set_errors=True,
        check_get_errors=True,
    )

    auto_output_off_enabled = Channel.control(
        ":OUTPut{ch}:OFF:AUTO?",
        ":OUTPut{ch}:OFF:AUTO %d",
        """Control automatic output-off behavior when an action becomes idle (boolean).""",
        validator=_strict_bool,
        values={False: 0, True: 1},
        map_values=True,
        cast=str,
        get_process=_parse_binary,
        get_process_list=_parse_single_binary,
        check_set_errors=True,
        check_get_errors=True,
    )

    output_off_mode = Channel.control(
        ":OUTPut{ch}:OFF:MODE?",
        ":OUTPut{ch}:OFF:MODE %s",
        """Control the source condition after output off (ZERO, HIZ, or NORM).""",
        validator=_strict_off_mode,
        cast=str,
        get_process=_parse_off_mode,
        check_set_errors=True,
        check_get_errors=True,
    )

    voltage_compliance_tripped = Channel.measurement(
        ":SENSe{ch}:VOLTage:DC:PROTection:TRIPped?",
        """Get whether voltage compliance is tripped (boolean NR1).""",
        cast=str,
        get_process=_parse_binary,
        get_process_list=_parse_single_binary,
        check_get_errors=True,
    )

    current_compliance_tripped = Channel.measurement(
        ":SENSe{ch}:CURRent:DC:PROTection:TRIPped?",
        """Get whether current compliance is tripped (boolean NR1).""",
        cast=str,
        get_process=_parse_binary,
        get_process_list=_parse_single_binary,
        check_get_errors=True,
    )

    @property
    def voltage(self) -> float:
        """Measure the voltage in Volts with the instrument's one-shot DC measurement."""
        reading = _parse_sample(self.ask(":MEASure:VOLTage:DC? (@1)"), 1)[0]
        self.check_get_errors()
        return reading

    @property
    def current(self) -> float:
        """Measure the current in Amperes with the instrument's one-shot DC measurement."""
        reading = _parse_sample(self.ask(":MEASure:CURRent:DC? (@1)"), 1)[0]
        self.check_get_errors()
        return reading

    def write(self, command: str, **kwargs) -> None:
        """Check high-voltage changes before forwarding a channel command."""
        rendered = self.insert_id(command)
        header, _, parameter = rendered.strip().partition(" ")
        normalized_header = header.upper()
        normalized_parameter = parameter.strip().upper()

        if normalized_header == ":OUTPUT1" and normalized_parameter in ("1", "ON"):
            self._check_active_high_voltage()
        elif normalized_header == ":SOURCE1:FUNCTION:MODE":
            mode = _parse_mode(normalized_parameter)
            limit = self._query_number(
                ":SENSe1:VOLTage:DC:PROTection:LEVel?" if mode == "CURR"
                else ":SOURce1:VOLTage:LEVel:IMMediate:AMPLitude?"
            )
            if abs(limit) > HIGH_VOLTAGE_THRESHOLD:
                self._require_closed_interlock()
        elif normalized_header in {
            ":SOURCE1:VOLTAGE:LEVEL:IMMEDIATE:AMPLITUDE",
            ":SOURCE1:VOLTAGE:LEVEL:TRIGGERED:AMPLITUDE",
            ":SENSE1:VOLTAGE:DC:PROTECTION:LEVEL",
            ":SOURCE1:VOLTAGE:RANGE",
        }:
            if abs(_parse_float(parameter)) > HIGH_VOLTAGE_THRESHOLD:
                self._require_closed_interlock()
        elif (
            normalized_header == ":SOURCE1:VOLTAGE:RANGE:AUTO"
            and normalized_parameter in ("1", "ON")
        ):
            self._check_active_high_voltage()
        elif normalized_header == ":SENSE1:VOLTAGE:DC:NPLCYCLES":
            integration = _parse_float(parameter)
            self._validate_native_nplc(integration)
            self._write_checked(":SENSe1:VOLTage:DC:APERture:AUTO 0")
            self._write_checked(":SENSe1:VOLTage:DC:NPLCycles:AUTO 0")

        self.parent.write(rendered, **kwargs)

    def _query_number(self, command: str) -> float:
        """Read and parse one numeric value without changing the instrument."""
        number = _parse_float(self.ask(command))
        self.check_get_errors()
        return number

    def _require_closed_interlock(self) -> None:
        """Require the documented B2900 interlock query to report a closed circuit."""
        tripped = _parse_binary(self.ask(":SYSTem:INTerlock:TRIPped?"))
        self.check_get_errors()
        if tripped:
            raise RuntimeError(
                "The B2910BL interlock reports open; high-voltage commands are blocked."
            )

    def _validate_native_nplc(self, nplc: float) -> None:
        """Check a fixed integration value against the selected line frequency."""
        line_frequency = self._query_number(":SYSTem:LFRequency?")
        _validate_native_nplc(nplc, line_frequency)

    def _check_active_high_voltage(self) -> None:
        """Check the active source's voltage level or compliance before output enable."""
        mode = _parse_mode(self.ask(":SOURce1:FUNCtion:MODE?"))
        self.check_get_errors()
        if mode == "VOLT":
            high_voltage = self._query_number(
                ":SOURce1:VOLTage:LEVel:IMMediate:AMPLitude?"
            )
        else:
            high_voltage = self._query_number(":SENSe1:VOLTage:DC:PROTection:LEVel?")
        if abs(high_voltage) > HIGH_VOLTAGE_THRESHOLD:
            self._require_closed_interlock()

    def _write_checked(self, command: str) -> None:
        """Write one configuration command and fail immediately on a SCPI error."""
        self.write(command)
        errors = self.check_errors()
        if errors:
            rendered_errors = "; ".join(
                f"{float(code):g}: {message}" for code, message in errors
            )
            raise RuntimeError(f"B2910BL rejected {command!r}: {rendered_errors}")

    def abort(self) -> None:
        """Abort pending source and acquisition activity without changing output state."""
        self._write_checked(":ABORt:ALL (@1)")

    def _validate_voltage_config(
        self,
        voltage: Any,
        current_limit: Any,
        nplc: Any,
        voltage_range: Any,
        current_range: Any,
    ) -> tuple[float, float, float, float | None, float | None]:
        """Validate every voltage-source configuration argument before writing."""
        source_value = _finite_range(voltage, (-MAX_VOLTAGE, MAX_VOLTAGE))
        compliance = _positive_finite(current_limit, MAX_CURRENT)
        integration = _validate_nplc(nplc)
        selected_voltage_range = _range_selection(voltage_range, VOLTAGE_RANGE_VALUES)
        selected_current_range = _range_selection(current_range, CURRENT_RANGE_VALUES)
        _validate_envelope(source_value, compliance)
        return (
            source_value,
            compliance,
            integration,
            selected_voltage_range,
            selected_current_range,
        )

    def _validate_current_config(
        self,
        current: Any,
        voltage_limit: Any,
        nplc: Any,
        voltage_range: Any,
        current_range: Any,
    ) -> tuple[float, float, float, float | None, float | None]:
        """Validate every current-source configuration argument before writing."""
        source_value = _finite_range(current, (-MAX_CURRENT, MAX_CURRENT))
        compliance = _positive_finite(voltage_limit, MAX_VOLTAGE)
        integration = _validate_nplc(nplc)
        selected_voltage_range = _range_selection(voltage_range, VOLTAGE_RANGE_VALUES)
        selected_current_range = _range_selection(current_range, CURRENT_RANGE_VALUES)
        _validate_envelope(compliance, source_value)
        return (
            source_value,
            compliance,
            integration,
            selected_voltage_range,
            selected_current_range,
        )

    def _configure(
        self,
        mode: str,
        source_value: float,
        compliance: float,
        nplc: float,
        voltage_range: float | None,
        current_range: float | None,
        require_closed_interlock: bool = False,
    ) -> None:
        """Establish a deterministic, output-off fixed DC source and acquisition state."""
        self._write_checked(":OUTPut1 0")
        if self.output_enabled:
            raise RuntimeError("B2910BL still reports output enabled after output-off request.")
        self.abort()
        if require_closed_interlock or (
            mode == "VOLT" and abs(source_value) > HIGH_VOLTAGE_THRESHOLD
        ) or (mode == "CURR" and compliance > HIGH_VOLTAGE_THRESHOLD):
            self._require_closed_interlock()
        self._write_checked(":SOURce1:FUNCtion:SHAPe DC")
        self._write_checked(":SOURce1:VOLTage:MODE FIXed")
        self._write_checked(":SOURce1:CURRent:MODE FIXed")

        compliance_function = "CURRent" if mode == "VOLT" else "VOLTage"
        self._write_checked(
            f":SENSe1:{compliance_function}:DC:PROTection:LEVel {compliance:g}"
        )
        self._write_checked(":SOURce1:VOLTage:RANGe:AUTO 1")
        self._write_checked(":SOURce1:CURRent:RANGe:AUTO 1")
        source_function = "VOLTage" if mode == "VOLT" else "CURRent"
        self._write_checked(
            f":SOURce1:{source_function}:LEVel:IMMediate:AMPLitude {source_value:g}"
        )
        self._write_checked(
            f":SOURce1:{source_function}:LEVel:TRIGgered:AMPLitude {source_value:g}"
        )
        self._write_checked(f":SOURce1:FUNCtion:MODE {mode}")

        self._write_checked(':SENSe1:FUNCtion:ON "VOLT","CURR"')
        self._write_checked(
            f":SENSe1:VOLTage:DC:RANGe:AUTO {1 if voltage_range is None else 0}"
        )
        if voltage_range is not None:
            self._write_checked(f":SENSe1:VOLTage:DC:RANGe {voltage_range:g}")
        self._write_checked(
            f":SENSe1:CURRent:DC:RANGe:AUTO {1 if current_range is None else 0}"
        )
        if current_range is not None:
            self._write_checked(f":SENSe1:CURRent:DC:RANGe {current_range:g}")

        self._write_checked(f":SENSe1:VOLTage:DC:NPLCycles {nplc:g}")
        self._write_checked(":OUTPut1:ON:AUTO 0")
        self._write_checked(":OUTPut1:OFF:AUTO 0")

        self._configure_single_acquisition()

    def _configure_single_acquisition(self) -> None:
        """Select one internally triggered acquisition and source action."""
        for action in ("ACQuire", "TRANsient"):
            self._write_checked(f":ARM1:{action}:COUNt 1")
            self._write_checked(f":ARM1:{action}:SOURce AINT")
            self._write_checked(f":TRIGger1:{action}:COUNt 1")
            self._write_checked(f":TRIGger1:{action}:SOURce AINT")

    def configure_voltage(
        self,
        voltage: float,
        current_limit: float,
        *,
        nplc: float = 0.1,
        voltage_range: float | str = "AUTO",
        current_range: float | str = "AUTO",
    ) -> None:
        """Configure constant-voltage source and measurement settings with output off.

        :param voltage: Voltage source level in Volts.
        :param current_limit: Current compliance in Amperes.
        :param nplc: Shared integration time in power-line cycles, from 0.01 to 100.
        :param voltage_range: Voltage measurement range or ``"AUTO"``.
        :param current_range: Current measurement range or ``"AUTO"``.
        """
        values = self._validate_voltage_config(
            voltage, current_limit, nplc, voltage_range, current_range
        )
        self._configure("VOLT", *values)

    def configure_current(
        self,
        current: float,
        voltage_limit: float,
        *,
        nplc: float = 0.1,
        voltage_range: float | str = "AUTO",
        current_range: float | str = "AUTO",
    ) -> None:
        """Configure constant-current source and measurement settings with output off.

        :param current: Current source level in Amperes.
        :param voltage_limit: Voltage compliance in Volts.
        :param nplc: Shared integration time in power-line cycles, from 0.01 to 100.
        :param voltage_range: Voltage measurement range or ``"AUTO"``.
        :param current_range: Current measurement range or ``"AUTO"``.
        """
        values = self._validate_current_config(
            current, voltage_limit, nplc, voltage_range, current_range
        )
        self._configure("CURR", *values)

    def read_point(self) -> B2910BLReading:
        """Read paired DC voltage, current, source setting, and compliance status.

        The source setting is the instrument-reported programmed value, not a measured
        voltage or current. The paired voltage and current are returned from one acquisition.
        """
        self._write_checked(":OUTPut1:ON:AUTO 0")
        self._write_checked(":OUTPut1:OFF:AUTO 0")
        self.abort()
        self._write_checked(":SOURce1:FUNCtion:SHAPe DC")
        self._write_checked(":SOURce1:VOLTage:MODE FIXed")
        self._write_checked(":SOURce1:CURRent:MODE FIXed")
        self._write_checked(':SENSe1:FUNCtion:ON "VOLT","CURR"')
        self._configure_single_acquisition()
        self._write_checked(":FORMat:DATA ASCii")
        self._write_checked(":FORMat:ELEMents:SENSe VOLT,CURR,SOUR")
        mode = _parse_mode(self.ask(":SOURce1:FUNCtion:MODE?"))
        self.check_get_errors()
        source_function = "VOLTage" if mode == "VOLT" else "CURRent"
        source_value = _parse_float(
            self.ask(f":SOURce1:{source_function}:LEVel:IMMediate:AMPLitude?")
        )
        self.check_get_errors()
        self._write_checked(
            f":SOURce1:{source_function}:LEVel:TRIGgered:AMPLitude {source_value:g}"
        )
        values = _parse_sample(self.ask(":READ? (@1)"), 3)
        self.check_get_errors()
        trip_command = (
            ":SENSe1:CURRent:DC:PROTection:TRIPped?"
            if mode == "VOLT"
            else ":SENSe1:VOLTage:DC:PROTection:TRIPped?"
        )
        compliance = _parse_binary(self.ask(trip_command))
        self.check_get_errors()
        return B2910BLReading(values[0], values[1], values[2], compliance)

    def _request_output_off_and_verify(self) -> None:
        """Request output off and confirm its reported state."""
        request_error: BaseException | None = None
        try:
            self.output_enabled = False
        except BaseException as exc:  # noqa: BLE001 - ensure cleanup on KeyboardInterrupt
            request_error = exc

        try:
            output_enabled = self.output_enabled
        except BaseException as exc:  # noqa: BLE001 - classify interrupted state as unknown
            raise RuntimeError(
                "B2910BL output state is UNKNOWN after requesting output off."
            ) from (request_error or exc)

        if output_enabled:
            error = RuntimeError("B2910BL still reports output enabled after shutdown.")
            if request_error is not None:
                raise error from request_error
            raise error
        if request_error is not None:
            raise RuntimeError(
                "B2910BL reports output off, but the output-off request reported an error."
            ) from request_error

    def _run_sweep(
        self,
        mode: str,
        points: list[float],
        compliance: float,
        nplc: float,
        settle: float,
        voltage_range: float | None,
        current_range: float | None,
    ) -> list[B2910BLSweepPoint]:
        """Apply validated host-side setpoints and guarantee an output-off request."""
        sweep_points: list[B2910BLSweepPoint] = []
        scan_error: BaseException | None = None
        try:
            require_interlock = mode == "VOLT" and any(
                abs(point) > HIGH_VOLTAGE_THRESHOLD for point in points
            )
            require_interlock = require_interlock or (
                mode == "CURR" and compliance > HIGH_VOLTAGE_THRESHOLD
            )
            self._configure(
                mode,
                points[0],
                compliance,
                nplc,
                voltage_range,
                current_range,
                require_interlock,
            )
            self.output_enabled = True
            for index, point in enumerate(points):
                if not self.output_enabled:
                    raise RuntimeError(
                        f"B2910BL output turned off before sweep point {index + 1}."
                    )
                if index:
                    if mode == "VOLT":
                        self.source_voltage = point
                    else:
                        self.source_current = point
                if settle:
                    time.sleep(settle)
                reading = self.read_point()
                if not self.output_enabled:
                    raise RuntimeError(
                        f"B2910BL output turned off after sweep point {index + 1}."
                    )
                sweep_points.append(
                    B2910BLSweepPoint(
                        point,
                        reading.voltage_V,
                        reading.current_A,
                        reading.source_setting,
                        reading.compliance,
                    )
                )
        except BaseException as exc:
            scan_error = exc
            raise
        finally:
            try:
                self._request_output_off_and_verify()
            except BaseException as shutdown_error:
                if scan_error is not None:
                    raise SweepShutdownError(scan_error, shutdown_error) from scan_error
                raise
        return sweep_points

    def sweep_voltage(
        self,
        points: Iterable[float],
        current_limit: float,
        *,
        nplc: float = 0.1,
        settle: float = 0.0,
        voltage_range: float | str = "AUTO",
        current_range: float | str = "AUTO",
    ) -> list[B2910BLSweepPoint]:
        """Run an ordered host-stepped voltage sweep and request output off afterward.

        :param points: Finite iterable of voltage setpoints in Volts.
        :param current_limit: Current compliance in Amperes.
        :param nplc: Shared integration time in power-line cycles, from 0.01 to 100.
        :param settle: Host-side delay in seconds after enabling and each setpoint change.
        :param voltage_range: Voltage measurement range or ``"AUTO"``.
        :param current_range: Current measurement range or ``"AUTO"``.
        """
        voltage_points = _materialize_points(points, -MAX_VOLTAGE, MAX_VOLTAGE)
        compliance = _positive_finite(current_limit, MAX_CURRENT)
        integration = _validate_nplc(nplc)
        delay = _validate_settle(settle)
        selected_voltage_range = _range_selection(voltage_range, VOLTAGE_RANGE_VALUES)
        selected_current_range = _range_selection(current_range, CURRENT_RANGE_VALUES)
        for voltage in voltage_points:
            _validate_envelope(voltage, compliance)
        return self._run_sweep(
            "VOLT",
            voltage_points,
            compliance,
            integration,
            delay,
            selected_voltage_range,
            selected_current_range,
        )

    def sweep_current(
        self,
        points: Iterable[float],
        voltage_limit: float,
        *,
        nplc: float = 0.1,
        settle: float = 0.0,
        voltage_range: float | str = "AUTO",
        current_range: float | str = "AUTO",
    ) -> list[B2910BLSweepPoint]:
        """Run an ordered host-stepped current sweep and request output off afterward.

        :param points: Finite iterable of current setpoints in Amperes.
        :param voltage_limit: Voltage compliance in Volts.
        :param nplc: Shared integration time in power-line cycles, from 0.01 to 100.
        :param settle: Host-side delay in seconds after enabling and each setpoint change.
        :param voltage_range: Voltage measurement range or ``"AUTO"``.
        :param current_range: Current measurement range or ``"AUTO"``.
        """
        current_points = _materialize_points(points, -MAX_CURRENT, MAX_CURRENT)
        compliance = _positive_finite(voltage_limit, MAX_VOLTAGE)
        integration = _validate_nplc(nplc)
        delay = _validate_settle(settle)
        selected_voltage_range = _range_selection(voltage_range, VOLTAGE_RANGE_VALUES)
        selected_current_range = _range_selection(current_range, CURRENT_RANGE_VALUES)
        for current in current_points:
            _validate_envelope(compliance, current)
        return self._run_sweep(
            "CURR",
            current_points,
            compliance,
            integration,
            delay,
            selected_voltage_range,
            selected_current_range,
        )


class KeysightB2910BL(SCPIMixin, Instrument):
    """Interface for the single-channel Keysight B2910BL precision SMU."""

    ch1 = Instrument.ChannelCreator(B2910BLChannel, 1)

    def __init__(
        self,
        adapter: AdapterType,
        name: str = "Keysight B2910BL",
        **kwargs: Any,
    ) -> None:
        """Create the channel interface without issuing commands to the instrument.

        :param adapter: An adapter, VISA resource name, or GPIB address.
        :param name: Instrument display name.
        :param kwargs: Arguments forwarded to :class:`~pymeasure.instruments.Instrument`.
        """
        super().__init__(adapter, name, **kwargs)

    def check_errors(self) -> list[list[float | str]]:
        """Drain and strictly parse the SCPI error queue.

        :returns: Error entries as ``[code, message]`` pairs.
        :raises ValueError: If the instrument returns a malformed error entry.
        """
        errors: list[list[float | str]] = []
        for _ in range(100):
            response = self.ask("SYST:ERR?").strip()
            code_text, separator, message_text = response.partition(",")
            if not separator or not re.fullmatch(r"[+-]?\d+", code_text.strip()):
                raise ValueError(f"Malformed B2910BL SCPI error response {response!r}.")
            if len(message_text) < 2 or message_text[0] != '"' or message_text[-1] != '"':
                raise ValueError(f"Malformed B2910BL SCPI error message {response!r}.")
            code = int(code_text)
            message = message_text[1:-1]
            if code == 0:
                return errors
            entry: list[float | str] = [float(code), message]
            errors.append(entry)
            log.error("%s: %s, %s", self.name, code, message)
        raise RuntimeError(
            "B2910BL SCPI error queue did not return an empty entry within 100 reads."
        )

    def check_set_errors(self) -> list[list[float | str]]:
        """Raise an actionable error after a command is rejected by the instrument."""
        errors = self.check_errors()
        if errors:
            detail = "; ".join(f"{float(code):g}: {message}" for code, message in errors)
            raise RuntimeError(f"B2910BL rejected the last command: {detail}")
        return errors

    def check_get_errors(self) -> list[list[float | str]]:
        """Raise an actionable error if a property query generated a SCPI error."""
        errors = self.check_errors()
        if errors:
            detail = "; ".join(f"{float(code):g}: {message}" for code, message in errors)
            raise RuntimeError(f"B2910BL reported an error while reading a property: {detail}")
        return errors
