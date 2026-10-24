#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

from __future__ import annotations

import math
import re
from numbers import Real

from pymeasure.instruments import AdapterType, Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_case_insensitive_set

_BOOL_VALUES = {True: 1, False: 0}
_DC_VOLTAGE_RANGES = (0.1, 1.0, 10.0, 100.0, 1000.0)
_CURRENT_RANGES = (0.0001, 0.001, 0.01, 0.1, 1.0, 3.0, 10.0)
_CURRENT_SENSE_RANGES = (0.000001, 0.00001, *_CURRENT_RANGES[:-1])
_RESISTANCE_RANGES = (
    100.0,
    1_000.0,
    10_000.0,
    100_000.0,
    1_000_000.0,
    10_000_000.0,
    100_000_000.0,
    1_000_000_000.0,
)
_BASE_NPLC_VALUES = (0.02, 0.06, 0.2, 1.0, 10.0, 100.0)
_DIG_NPLC_VALUES = (0.001, 0.002, 0.006)
_TRIGGER_SOURCES = ("IMM", "EXT", "BUS")
_ALL_TRIGGER_SOURCES = (*_TRIGGER_SOURCES, "INT")
_MAX_HARDWARE_COUNT = 1_000_000_000
_MAX_CONVENIENCE_SAMPLES = 50_000


class MeasurementError(RuntimeError):
    """Report an empty, malformed, or incomplete measurement response."""


def _validate_bool(value: object, values: object) -> bool:
    if not isinstance(value, bool):
        raise TypeError("Value must be True or False")
    return value


def _validate_count(value: object, limits: tuple[int, int]) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("Count must be an integer")
    if not limits[0] <= value <= limits[1]:
        raise ValueError(f"Count must be between {limits[0]} and {limits[1]}")
    return value


def _validate_delay(value: object, limits: tuple[float, float]) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError("Trigger delay must be a finite number of seconds")
    delay = float(value)
    if not math.isfinite(delay) or not limits[0] <= delay <= limits[1]:
        raise ValueError(f"Trigger delay must be between {limits[0]} and {limits[1]} seconds")
    return delay


def _validate_discrete_number(value: object, allowed: tuple[float, ...]) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"Value must be one of {allowed}")
    number = float(value)
    if not math.isfinite(number) or number not in allowed:
        raise ValueError(f"Value must be one of {allowed}")
    return number


def _validate_nplc(value: object, allowed: tuple[float, ...]) -> float:
    return _validate_discrete_number(value, allowed)


def _normalize_function(function: object) -> str:
    if not isinstance(function, str):
        raise TypeError(
            "Function must be one of DCV, DCI, RES, FRES, FREQ, PER, CONT, or DIOD"
        )
    normalized = function.upper()
    if normalized not in Keysight34465A.FUNCTIONS:
        raise ValueError(
            "Function must be one of DCV, DCI, RES, FRES, FREQ, PER, CONT, or DIOD"
        )
    return normalized


def _validate_config_range(function: str, value: object) -> float | str:
    if function == "DCV":
        allowed = _DC_VOLTAGE_RANGES
    elif function == "DCI":
        allowed = _CURRENT_RANGES
    elif function in ("RES", "FRES"):
        allowed = _RESISTANCE_RANGES
    elif function in ("FREQ", "PER"):
        allowed = _DC_VOLTAGE_RANGES
    else:
        raise ValueError(f"Function {function} does not support a selectable range")
    if isinstance(value, str) and value.upper() == "AUTO":
        return "AUTO"
    return _validate_discrete_number(value, allowed)


def _format_scpi_number(value: float) -> str:
    """Format a supported finite value without scientific notation."""
    return f"{value:.12f}".rstrip("0").rstrip(".")


def _parse_integer_reply(value: float) -> int:
    if not math.isfinite(value) or not value.is_integer():
        raise ValueError(f"Instrument returned a non-integer count: {value}")
    return int(value)


class Keysight34465A(SCPIMixin, Instrument):
    """Control a Keysight 34465A Truevolt digital multimeter.

    The driver supports only the 34465A model. Construction does not reset or
    otherwise configure the instrument. Use :meth:`configure` to select a
    measurement function and :meth:`measure` or :meth:`acquire` to read it.
    """

    FUNCTIONS = {
        "DCV": "VOLT:DC",
        "DCI": "CURR:DC",
        "RES": "RES",
        "FRES": "FRES",
        "FREQ": "FREQ",
        "PER": "PER",
        "CONT": "CONT",
        "DIOD": "DIOD",
    }

    def __init__(
        self,
        adapter: AdapterType,
        name="Keysight 34465A Truevolt Digital Multimeter",
        **kwargs,
    ):
        super().__init__(adapter, name, **kwargs)
        self._expected_readings: int | None = None

    voltage_range = Instrument.control(
        "VOLT:DC:RANG?",
        "VOLT:DC:RANG %s",
        "Control the fixed DC voltage range in Volts.",
        validator=_validate_discrete_number,
        values=_DC_VOLTAGE_RANGES,
        cast=float,
        set_process=_format_scpi_number,
        check_set_errors=True,
    )

    voltage_autorange_enabled = Instrument.control(
        "VOLT:DC:RANG:AUTO?",
        "VOLT:DC:RANG:AUTO %d",
        "Control autoranging for DC voltage measurements.",
        validator=_validate_bool,
        values=_BOOL_VALUES,
        map_values=True,
        check_set_errors=True,
    )

    current_range = Instrument.control(
        "CURR:DC:RANG?",
        "CURR:DC:RANG %s",
        "Control the fixed DC current range on the 3 A terminals, in Amps.",
        validator=_validate_discrete_number,
        values=_CURRENT_SENSE_RANGES,
        cast=float,
        set_process=_format_scpi_number,
        check_set_errors=True,
    )

    current_autorange_enabled = Instrument.control(
        "CURR:DC:RANG:AUTO?",
        "CURR:DC:RANG:AUTO %d",
        "Control autoranging for DC current measurements.",
        validator=_validate_bool,
        values=_BOOL_VALUES,
        map_values=True,
        check_set_errors=True,
    )

    resistance_range = Instrument.control(
        "RES:RANG?",
        "RES:RANG %s",
        "Control the fixed 2-wire and 4-wire resistance range, in Ohms.",
        validator=_validate_discrete_number,
        values=_RESISTANCE_RANGES,
        cast=float,
        set_process=_format_scpi_number,
        check_set_errors=True,
    )

    resistance_autorange_enabled = Instrument.control(
        "RES:RANG:AUTO?",
        "RES:RANG:AUTO %d",
        "Control autoranging for 2-wire and 4-wire resistance measurements.",
        validator=_validate_bool,
        values=_BOOL_VALUES,
        map_values=True,
        check_set_errors=True,
    )

    frequency_input_voltage_range = Instrument.control(
        "FREQ:VOLT:RANG?",
        "FREQ:VOLT:RANG %s",
        "Control the fixed input-voltage range for frequency and period measurements, in Volts.",
        validator=_validate_discrete_number,
        values=_DC_VOLTAGE_RANGES,
        cast=float,
        set_process=_format_scpi_number,
        check_set_errors=True,
    )

    frequency_input_voltage_autorange_enabled = Instrument.control(
        "FREQ:VOLT:RANG:AUTO?",
        "FREQ:VOLT:RANG:AUTO %d",
        "Control input-voltage autoranging for frequency and period measurements.",
        validator=_validate_bool,
        values=_BOOL_VALUES,
        map_values=True,
        check_set_errors=True,
    )

    voltage_nplc = Instrument.control(
        "VOLT:DC:NPLC?",
        "VOLT:DC:NPLC %s",
        "Control DC voltage integration time in power line cycles (base values).",
        validator=_validate_nplc,
        values=_BASE_NPLC_VALUES,
        cast=float,
        set_process=_format_scpi_number,
        check_set_errors=True,
    )

    current_nplc = Instrument.control(
        "CURR:DC:NPLC?",
        "CURR:DC:NPLC %s",
        "Control DC current integration time in power line cycles (base values).",
        validator=_validate_nplc,
        values=_BASE_NPLC_VALUES,
        cast=float,
        set_process=_format_scpi_number,
        check_set_errors=True,
    )

    resistance_nplc = Instrument.control(
        "RES:NPLC?",
        "RES:NPLC %s",
        "Control 2-wire and 4-wire resistance integration time in power line cycles "
        "(base values).",
        validator=_validate_nplc,
        values=_BASE_NPLC_VALUES,
        cast=float,
        set_process=_format_scpi_number,
        check_set_errors=True,
    )

    voltage_autozero_enabled = Instrument.control(
        "VOLT:DC:ZERO:AUTO?",
        "VOLT:DC:ZERO:AUTO %d",
        "Control autozero for DC voltage measurements.",
        validator=_validate_bool,
        values=_BOOL_VALUES,
        map_values=True,
        check_set_errors=True,
    )

    current_autozero_enabled = Instrument.control(
        "CURR:DC:ZERO:AUTO?",
        "CURR:DC:ZERO:AUTO %d",
        "Control autozero for DC current measurements.",
        validator=_validate_bool,
        values=_BOOL_VALUES,
        map_values=True,
        check_set_errors=True,
    )

    resistance_autozero_enabled = Instrument.control(
        "RES:ZERO:AUTO?",
        "RES:ZERO:AUTO %d",
        "Control the documented 2-wire resistance autozero setting.",
        validator=_validate_bool,
        values=_BOOL_VALUES,
        map_values=True,
        check_set_errors=True,
    )

    display_enabled = Instrument.control(
        "DISP:STAT?",
        "DISP:STAT %d",
        "Control whether the front-panel display is enabled.",
        validator=_validate_bool,
        values=_BOOL_VALUES,
        map_values=True,
        check_set_errors=True,
    )

    trigger_source = Instrument.control(
        "TRIG:SOUR?",
        "TRIG:SOUR %s",
        "Control the trigger source (IMM, EXT, or BUS). Use set_trigger_source for DIG INT.",
        validator=strict_discrete_case_insensitive_set,
        values=_TRIGGER_SOURCES,
        cast=str,
        get_process=str.upper,
        check_set_errors=True,
    )

    sample_count = Instrument.control(
        "SAMP:COUN?",
        "SAMP:COUN %s",
        "Control the hardware sample count per trigger (integer from 1 to 1e9).",
        validator=_validate_count,
        values=(1, _MAX_HARDWARE_COUNT),
        cast=float,
        get_process=_parse_integer_reply,
        check_set_errors=True,
    )

    trigger_count = Instrument.control(
        "TRIG:COUN?",
        "TRIG:COUN %s",
        "Control the finite hardware trigger count (integer from 1 to 1e9).",
        validator=_validate_count,
        values=(1, _MAX_HARDWARE_COUNT),
        cast=float,
        get_process=_parse_integer_reply,
        check_set_errors=True,
    )

    trigger_delay = Instrument.control(
        "TRIG:DEL?",
        "TRIG:DEL %s",
        "Control the trigger delay in seconds (finite from 0 to approximately 3600).",
        validator=_validate_delay,
        values=(0.0, 3600.0),
        cast=float,
        check_set_errors=True,
    )

    def configure(
        self,
        function: str,
        range_: float | str | None = None,
        nplc: float | None = None,
        autozero_enabled: bool | None = None,
    ) -> None:
        """Configure a supported measurement function and its optional range and timing.

        :param function: One of ``DCV``, ``DCI``, ``RES``, ``FRES``, ``FREQ``, ``PER``,
            ``CONT``, or ``DIOD``.
        :param range_: A documented fixed range or ``"AUTO"``. For frequency and period,
            this is the input-voltage range.
        :param nplc: Integration time for DC voltage, DC current, or resistance functions.
            Values 0.001, 0.002, and 0.006 require the optional DIG option.
        :param autozero_enabled: Set autozero for DC voltage, DC current, or resistance.
            The RES command does not change 4-wire resistance autozero behavior.
        :raises ValueError: If any argument is unsupported or invalid for the function.
        :raises RuntimeError: If the instrument reports an SCPI command error.
        """
        function = _normalize_function(function)
        selected_range = None
        if range_ is not None:
            selected_range = _validate_config_range(function, range_)

        if nplc is not None:
            if function not in ("DCV", "DCI", "RES", "FRES"):
                raise ValueError(f"Function {function} does not support NPLC")
            nplc = _validate_nplc(nplc, (*_BASE_NPLC_VALUES, *_DIG_NPLC_VALUES))

        if autozero_enabled is not None:
            if function not in ("DCV", "DCI", "RES", "FRES"):
                raise ValueError(f"Function {function} does not support autozero control")
            autozero_enabled = _validate_bool(autozero_enabled, _BOOL_VALUES)

        if nplc in _DIG_NPLC_VALUES:
            self._require_option("DIG", "NPLC values 0.001, 0.002, and 0.006")

        self._expected_readings = None
        command = f"CONF:{self.FUNCTIONS[function]}"
        if selected_range is not None and function not in ("FREQ", "PER"):
            if isinstance(selected_range, str):
                command += f" {selected_range}"
            else:
                command += f" {_format_scpi_number(selected_range)}"
        self._write_checked(command)

        if selected_range is not None and function in ("FREQ", "PER"):
            if isinstance(selected_range, str):
                self._write_checked("FREQ:VOLT:RANG:AUTO ON")
            else:
                self._write_checked(
                    f"FREQ:VOLT:RANG {_format_scpi_number(selected_range)}"
                )

        if nplc is not None:
            nplc_command = {
                "DCV": "VOLT:DC:NPLC",
                "DCI": "CURR:DC:NPLC",
                "RES": "RES:NPLC",
                "FRES": "FRES:NPLC",
            }[function]
            self._write_checked(f"{nplc_command} {_format_scpi_number(nplc)}")

        if autozero_enabled is not None:
            autozero_command = {
                "DCV": "VOLT:DC:ZERO:AUTO",
                "DCI": "CURR:DC:ZERO:AUTO",
                "RES": "RES:ZERO:AUTO",
                "FRES": "RES:ZERO:AUTO",
            }[function]
            self._write_checked(f"{autozero_command} {int(autozero_enabled)}")

    def set_trigger_source(self, source: str) -> None:
        """Set a trigger source, checking DIG before selecting the optional INT source.

        :param source: ``IMM``, ``EXT``, ``BUS``, or ``INT``.
        :raises ValueError: If the source is invalid or ``INT`` is selected without DIG.
        :raises RuntimeError: If the instrument reports an SCPI command error.
        """
        if not isinstance(source, str):
            raise TypeError("Trigger source must be IMM, EXT, BUS, or INT")
        normalized = strict_discrete_case_insensitive_set(source, _ALL_TRIGGER_SOURCES)
        if normalized == "INT":
            self._require_option("DIG", "The INT trigger source")
        self._write_checked(f"TRIG:SOUR {normalized}")

    def check_set_errors(self) -> list[list[float | str]]:
        """Raise when the instrument reports an error after a setting command."""
        errors = super().check_set_errors()
        if errors:
            raise RuntimeError(f"{self.name} reported SCPI errors: {errors}")
        return errors

    def _write_checked(self, command: str) -> None:
        """Write a command and raise if the instrument rejects it."""
        self.write(command)
        self.check_set_errors()

    def _require_option(self, option: str, feature: str) -> None:
        options = self.options
        option_values = options if isinstance(options, (list, tuple)) else [options]
        tokens = {
            token.upper()
            for value in option_values
            for token in re.split(r"[,;\s]+", str(value).strip())
            if token
        }
        if option not in tokens:
            raise ValueError(f"{feature} requires the optional {option} option")

    def abort(self) -> None:
        """Abort an acquisition in progress and clear the expected result count.

        :raises RuntimeError: If the instrument reports an SCPI command error.
        """
        self._write_checked("ABOR")
        self._expected_readings = None

    def arm(
        self,
        sample_count: int,
        trigger_count: int = 1,
        trigger_delay: float | None = None,
    ) -> None:
        """Arm a finite BUS acquisition without sending its software trigger.

        :param sample_count: Hardware samples per trigger, from 1 to 1e9.
        :param trigger_count: Finite hardware triggers, from 1 to 1e9.
        :param trigger_delay: Optional trigger delay in seconds from 0 to approximately 3600.
            If omitted, automatic trigger delay is restored.
        :raises ValueError: If either count or the trigger delay is invalid.
        :raises RuntimeError: If the instrument reports an SCPI command error.
        """
        sample_count = _validate_count(sample_count, (1, _MAX_HARDWARE_COUNT))
        trigger_count = _validate_count(trigger_count, (1, _MAX_HARDWARE_COUNT))
        delay = (
            None
            if trigger_delay is None
            else _validate_delay(trigger_delay, (0.0, 3600.0))
        )
        self._start_acquisition("BUS", sample_count, trigger_count, delay)

    def trigger(self) -> None:
        """Send one software trigger using the IEEE 488.2 ``*TRG`` command.

        :raises RuntimeError: If the instrument reports an SCPI command error.
        """
        self._write_checked("*TRG")

    def fetch(self) -> list[float]:
        """Fetch readings already in reading memory without starting a measurement.

        :raises MeasurementError: If the reply is empty, malformed, or has an unexpected length.
        :raises RuntimeError: If the instrument reports an SCPI command error.
        """
        return self._fetch_readings(self._expected_readings)

    def measure(self, trigger_delay: float | None = None) -> float:
        """Take one immediate-trigger measurement and return its scalar reading.

        This method resets the source and counts before every measurement so a prior group or
        BUS acquisition cannot leak its sample count or trigger source into the one-shot read.

        :param trigger_delay: Optional trigger delay in seconds from 0 to approximately 3600.
            If omitted, automatic trigger delay is restored.
        :raises MeasurementError: If the reply is empty, malformed, or has an unexpected length.
        :raises ValueError: If the trigger delay is invalid.
        :raises RuntimeError: If the instrument reports an SCPI command error.
        """
        readings = self.acquire(1, trigger_delay=trigger_delay)
        return readings[0]

    def acquire(self, sample_count: int, trigger_delay: float | None = None) -> list[float]:
        """Take a finite immediate-trigger group and return readings in acquisition order.

        :param sample_count: Explicit positive sample count, at most 50,000 readings.
        :param trigger_delay: Optional trigger delay in seconds from 0 to approximately 3600.
            If omitted, automatic trigger delay is restored.
        :raises MeasurementError: If the reply is empty, malformed, or has an unexpected length.
        :raises ValueError: If the count or delay is invalid.
        :raises RuntimeError: If the instrument reports an SCPI command error.
        """
        sample_count = _validate_count(sample_count, (1, _MAX_CONVENIENCE_SAMPLES))
        delay = None if trigger_delay is None else _validate_delay(trigger_delay, (0.0, 3600.0))
        self._start_acquisition("IMM", sample_count, 1, delay)
        return self._fetch_readings(sample_count)

    def _start_acquisition(
        self,
        source: str,
        sample_count: int,
        trigger_count: int,
        trigger_delay: float | None,
    ) -> None:
        self._expected_readings = None
        self._write_checked("ABOR")
        self._write_checked(f"TRIG:SOUR {source}")
        self._write_checked(f"SAMP:COUN {sample_count}")
        self._write_checked(f"TRIG:COUN {trigger_count}")
        if trigger_delay is None:
            self._write_checked("TRIG:DEL:AUTO ON")
        else:
            self._write_checked(f"TRIG:DEL {trigger_delay:.12g}")
        self._write_checked("INIT")
        self._expected_readings = sample_count * trigger_count

    def _fetch_readings(self, expected_count: int | None) -> list[float]:
        # FORM:DATA may persist as REAL across sessions; the parser below expects ASCII.
        # Keysight Truevolt manual 34460-90901, Edition 7, PDF pp. 260-261.
        self._write_checked("FORM:DATA ASC")
        raw_values = self.values("FETC?", separator=",", cast=str)
        self.check_set_errors()
        if not raw_values or (len(raw_values) == 1 and not raw_values[0].strip()):
            raise MeasurementError("Instrument returned no readings")
        try:
            values = [float(value.strip()) for value in raw_values]
        except ValueError as exc:
            raise MeasurementError(
                f"Instrument returned malformed readings: {raw_values!r}"
            ) from exc
        if any(not math.isfinite(value) for value in values):
            raise MeasurementError(f"Instrument returned malformed readings: {raw_values!r}")
        if expected_count is not None and len(values) != expected_count:
            raise MeasurementError(
                f"Instrument returned {len(values)} readings; expected {expected_count}"
            )
        return values
