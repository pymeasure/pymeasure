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

import csv
import logging
import math
import numbers
import time
from collections.abc import Callable
from types import TracebackType
from typing import Any, Literal, TypeVar, overload

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.common_base import InstrumentProperty
from pymeasure.instruments.validators import strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

FUNCTION_PATHS = {
    "DCV": "VOLT",
    "DCI": "CURR",
    "RES": "RES",
    "FRES": "FRES",
    "FREQ": "FREQ",
    "PER": "PER",
    "CONT": "CONT",
    "DIOD": "DIOD",
}
_FUNCTION_REPLIES = {
    "VOLT": "DCV",
    "VOLT:DC": "DCV",
    "CURR": "DCI",
    "CURR:DC": "DCI",
    "RES": "RES",
    "FRES": "FRES",
    "FREQ": "FREQ",
    "FREQ:VOLT": "FREQ",
    "PER": "PER",
    "PER:VOLT": "PER",
    "CONT": "CONT",
    "DIOD": "DIOD",
}
_RANGE_LIMITS = {
    "DCV": (0.1, 1000.0),
    "DCI": (1e-5, 10.0),
    "RES": (10.0, 1e9),
    "FRES": (1.0, 1e9),
    "FREQ": (0.1, 700.0),
    "PER": (0.1, 700.0),
}
_NPLC_FUNCTIONS = {"DCV", "DCI", "RES", "FRES"}
_AUTOZERO_FUNCTIONS = {"DCV", "DCI", "RES", "FRES"}
_DEFAULT_BUFFER = "defbuffer1"
_MAX_COUNT = 1_000_000
_SCPI_ERROR_QUEUE_LIMIT = 100
_POST_NPLC_SETTLE_S = 0.2
_POLL_INTERVAL_S = 0.05
_TRIGGER_STATES = {
    "IDLE", "RUNNING", "WAITING", "EMPTY", "PAUSED", "BUILDING", "FAILED",
    "ABORTING", "ABORTED",
}


class DMM7510MeasurementError(RuntimeError):
    """Report invalid, incomplete, or unavailable DMM7510 measurement data."""


class DMM7510SCPIError(RuntimeError):
    """Report an error returned by the DMM7510 SCPI error queue."""


def _strip_reply(value: str) -> str:
    return value.strip().strip('"').upper()


def _parse_float_reply(value: str) -> float:
    try:
        result = float(value.strip())
    except (AttributeError, TypeError, ValueError) as exc:
        raise DMM7510MeasurementError(f"Invalid numeric DMM7510 response: {value!r}.") from exc
    if not math.isfinite(result):
        raise DMM7510MeasurementError(f"Nonfinite numeric DMM7510 response: {value!r}.")
    return result


def _parse_int_reply(value: str) -> int:
    number = _parse_float_reply(value)
    if not number.is_integer():
        raise DMM7510MeasurementError(f"Invalid integer DMM7510 response: {value!r}.")
    return int(number)


def _normalize_on_off(value: str) -> str:
    state = _strip_reply(value)
    if state in {"1", "ON"}:
        return "ON"
    if state in {"0", "OFF"}:
        return "OFF"
    raise DMM7510MeasurementError(f"Invalid ON/OFF DMM7510 response: {value!r}.")


def _validate_finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise TypeError(f"{name} must be a finite number, not {value!r}.")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite, not {value!r}.")
    return result


def _validate_range(value: Any, bounds: tuple[float, float]) -> float:
    result = _validate_finite_number(value, "range")
    low, high = bounds
    if not low <= result <= high:
        raise ValueError(f"range must be from {low:g} through {high:g}; got {value!r}.")
    return result


def _range_validator(value: Any, bounds: tuple[float, float]) -> float:
    return _validate_range(value, bounds)


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return repr(value)


def _boolean_mapping() -> dict[bool, str]:
    return {True: "ON", False: "OFF"}


def _validate_boolean_property(value: Any, values: Any) -> bool:
    if not isinstance(value, bool) or value not in values:
        raise TypeError("Boolean instrument properties require bool values.")
    return value


def _validate_count(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise TypeError("count must be a positive integer and must not be bool.")
    number = float(value)
    if not math.isfinite(number) or not number.is_integer():
        raise ValueError("count must be a finite positive integer.")
    count = int(number)
    if not 1 <= count <= _MAX_COUNT:
        raise ValueError(f"count must be from 1 through {_MAX_COUNT}.")
    return count


def _validate_bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be bool.")
    return value


_T = TypeVar("_T")


class _DMM7510Property(InstrumentProperty[_T]):
    """Define a DMM7510 property whose instance docstring works on Python 3.10."""

    @overload
    def __init__(
        self,
        fget: Callable[[Any], _T],
        fset: Callable[[Any, _T], None] | None = None,
        fdel: Callable[[Any], None] | None = None,
        doc: str | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        fget: None = None,
        fset: Callable[[Any, _T], None] | None = None,
        fdel: Callable[[Any], None] | None = None,
        doc: str | None = None,
    ) -> None: ...

    def __init__(
        self,
        fget: Callable[[Any], _T] | None = None,
        fset: Callable[[Any, _T], None] | None = None,
        fdel: Callable[[Any], None] | None = None,
        doc: str | None = None,
    ) -> None:
        self._explicit_doc = doc is not None
        if not self._explicit_doc and fget is not None:
            doc = getattr(fget, "__doc__", None)
        super().__init__(fget, fset, fdel, doc)
        # Python 3.10 property subclasses keep their class docstring even when a
        # different doc argument is supplied, so apply the instance doc explicitly.
        self.__doc__ = doc

    def getter(self, fget: Callable[[Any], Any], /) -> _DMM7510Property[Any]:
        doc = self.__doc__ if self._explicit_doc else None
        return type(self)(fget, self.fset, self.fdel, doc)

    def setter(self, fset: Callable[[Any, Any], None], /) -> _DMM7510Property[Any]:
        doc = self.__doc__ if self._explicit_doc else None
        return type(self)(self.fget, fset, self.fdel, doc)

    def deleter(self, fdel: Callable[[Any], None], /) -> _DMM7510Property[Any]:
        doc = self.__doc__ if self._explicit_doc else None
        return type(self)(self.fget, self.fset, fdel, doc)


class _LoggedExceptionSuppressor:
    def __init__(self, message: str) -> None:
        self.message = message

    def __enter__(self) -> None:
        return None

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        if isinstance(exc_value, Exception):
            log.warning("%s: %s", self.message, exc_value)
            return True
        return False


class _CaptureException:
    def __init__(self) -> None:
        self.exception: Exception | None = None

    def __enter__(self) -> None:
        return None

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        if isinstance(exc_value, Exception):
            self.exception = exc_value
            return True
        return False


class _CleanupOnFailure:
    def __init__(self, instrument: KeithleyDMM7510) -> None:
        self.instrument = instrument

    def __enter__(self) -> None:
        return None

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        if exc_type is not None:
            with _LoggedExceptionSuppressor("DMM7510 acquisition cleanup failed"):
                self.instrument._cleanup_after_error()
        return False


class KeithleyDMM7510(SCPIMixin, Instrument):
    """Control a Keithley DMM7510 using its native SCPI command set.

    The instrument must already be in native SCPI mode. Construction does not
    change its command set or issue identification, reset, or setup commands.
    """

    function: InstrumentProperty[str] = _DMM7510Property(
        fget=lambda self: self._get_function(),
        fset=lambda self, value: self._set_function(value),
        doc="""Control the active function: DCV, DCI, RES, FRES, FREQ, PER, CONT, or DIOD.""",
    )

    line_frequency: InstrumentProperty[float] = _DMM7510Property(
        fget=lambda self: self._query_float_property(":SYST:LFR?"),
        doc="""Get the detected power-line frequency in Hz.""",
    )

    voltage_autorange: InstrumentProperty[bool] = Instrument.control(
        ":SENS:VOLT:RANG:AUTO?",
        ":SENS:VOLT:RANG:AUTO %s",
        """Control DC voltage autoranging.""",
        validator=_validate_boolean_property,
        values=_boolean_mapping(),
        map_values=True,
        cast=str,
        get_process=_normalize_on_off,
        check_get_errors=True,
        check_set_errors=True,
    )
    voltage_range: InstrumentProperty[float] = Instrument.control(
        ":SENS:VOLT:RANG?",
        ":SENS:VOLT:RANG:AUTO OFF;:SENS:VOLT:RANG %s",
        """Control expected DC voltage magnitude in V (0.1 to 1000). The DMM7510
        selects the next sufficient fixed range, so read-back can differ.""",
        validator=_range_validator,
        values=_RANGE_LIMITS["DCV"],
        set_process=_format_number,
        cast=str,
        get_process=_parse_float_reply,
        check_get_errors=True,
        check_set_errors=True,
    )
    current_autorange: InstrumentProperty[bool] = Instrument.control(
        ":SENS:CURR:RANG:AUTO?",
        ":SENS:CURR:RANG:AUTO %s",
        """Control DC current autoranging. On REAR terminals autoranging tops out at 3 A.""",
        validator=_validate_boolean_property,
        values=_boolean_mapping(),
        map_values=True,
        cast=str,
        get_process=_normalize_on_off,
        check_get_errors=True,
        check_set_errors=True,
    )
    resistance_autorange: InstrumentProperty[bool] = Instrument.control(
        ":SENS:RES:RANG:AUTO?",
        ":SENS:RES:RANG:AUTO %s",
        """Control two-wire resistance autoranging.""",
        validator=_validate_boolean_property,
        values=_boolean_mapping(),
        map_values=True,
        cast=str,
        get_process=_normalize_on_off,
        check_get_errors=True,
        check_set_errors=True,
    )
    resistance_range: InstrumentProperty[float] = Instrument.control(
        ":SENS:RES:RANG?",
        ":SENS:RES:RANG:AUTO OFF;:SENS:RES:RANG %s",
        """Control expected two-wire resistance magnitude in ohms (10 to 1 GΩ).
        The DMM7510 selects the next sufficient fixed range.""",
        validator=_range_validator,
        values=_RANGE_LIMITS["RES"],
        set_process=_format_number,
        cast=str,
        get_process=_parse_float_reply,
        check_get_errors=True,
        check_set_errors=True,
    )
    four_wire_resistance_autorange: InstrumentProperty[bool] = Instrument.control(
        ":SENS:FRES:RANG:AUTO?",
        ":SENS:FRES:RANG:AUTO %s",
        """Control four-wire resistance autoranging.""",
        validator=_validate_boolean_property,
        values=_boolean_mapping(),
        map_values=True,
        cast=str,
        get_process=_normalize_on_off,
        check_get_errors=True,
        check_set_errors=True,
    )

    voltage_autozero_enabled: InstrumentProperty[bool] = Instrument.control(
        ":SENS:VOLT:AZER:STAT?",
        ":SENS:VOLT:AZER:STAT %s",
        """Control DC voltage autozero with a bool.""",
        validator=_validate_boolean_property,
        values=_boolean_mapping(),
        map_values=True,
        cast=str,
        get_process=_normalize_on_off,
        check_get_errors=True,
        check_set_errors=True,
    )
    current_autozero_enabled: InstrumentProperty[bool] = Instrument.control(
        ":SENS:CURR:AZER:STAT?",
        ":SENS:CURR:AZER:STAT %s",
        """Control DC current autozero with a bool.""",
        validator=_validate_boolean_property,
        values=_boolean_mapping(),
        map_values=True,
        cast=str,
        get_process=_normalize_on_off,
        check_get_errors=True,
        check_set_errors=True,
    )
    resistance_autozero_enabled: InstrumentProperty[bool] = Instrument.control(
        ":SENS:RES:AZER:STAT?",
        ":SENS:RES:AZER:STAT %s",
        """Control two-wire resistance autozero with a bool.""",
        validator=_validate_boolean_property,
        values=_boolean_mapping(),
        map_values=True,
        cast=str,
        get_process=_normalize_on_off,
        check_get_errors=True,
        check_set_errors=True,
    )
    four_wire_resistance_autozero_enabled: InstrumentProperty[bool] = Instrument.control(
        ":SENS:FRES:AZER:STAT?",
        ":SENS:FRES:AZER:STAT %s",
        """Control four-wire resistance autozero with a bool.""",
        validator=_validate_boolean_property,
        values=_boolean_mapping(),
        map_values=True,
        cast=str,
        get_process=_normalize_on_off,
        check_get_errors=True,
        check_set_errors=True,
    )

    four_wire_offset_compensation: InstrumentProperty[str] = _DMM7510Property(
        fget=lambda self: self._query_offset_compensation(),
        fset=lambda self, value: self._set_offset_compensation(value),
        doc="""Control four-wire offset compensation: OFF, ON, or AUTO. ON is unavailable
        above 100 kΩ; dry circuit enables offset compensation.""",
    )

    frequency_threshold_autorange: InstrumentProperty[bool] = Instrument.control(
        ":SENS:FREQ:THR:RANG:AUTO?",
        ":SENS:FREQ:THR:RANG:AUTO %s",
        """Control frequency input-voltage threshold autoranging.""",
        validator=_validate_boolean_property,
        values=_boolean_mapping(),
        map_values=True,
        cast=str,
        get_process=_normalize_on_off,
        check_get_errors=True,
        check_set_errors=True,
    )
    frequency_threshold_range: InstrumentProperty[float] = Instrument.control(
        ":SENS:FREQ:THR:RANG?",
        ":SENS:FREQ:THR:RANG:AUTO OFF;:SENS:FREQ:THR:RANG %s",
        """Control expected frequency input voltage in V (0.1 to 700), not frequency.
        The DMM7510 selects the next sufficient threshold range.""",
        validator=_range_validator,
        values=_RANGE_LIMITS["FREQ"],
        set_process=_format_number,
        cast=str,
        get_process=_parse_float_reply,
        check_get_errors=True,
        check_set_errors=True,
    )
    period_threshold_autorange: InstrumentProperty[bool] = Instrument.control(
        ":SENS:PER:THR:RANG:AUTO?",
        ":SENS:PER:THR:RANG:AUTO %s",
        """Control period input-voltage threshold autoranging.""",
        validator=_validate_boolean_property,
        values=_boolean_mapping(),
        map_values=True,
        cast=str,
        get_process=_normalize_on_off,
        check_get_errors=True,
        check_set_errors=True,
    )
    period_threshold_range: InstrumentProperty[float] = Instrument.control(
        ":SENS:PER:THR:RANG?",
        ":SENS:PER:THR:RANG:AUTO OFF;:SENS:PER:THR:RANG %s",
        """Control expected period input voltage in V (0.1 to 700), not period.
        The DMM7510 selects the next sufficient threshold range.""",
        validator=_range_validator,
        values=_RANGE_LIMITS["PER"],
        set_process=_format_number,
        cast=str,
        get_process=_parse_float_reply,
        check_get_errors=True,
        check_set_errors=True,
    )

    dry_circuit_enabled: InstrumentProperty[bool] = _DMM7510Property(
        fget=lambda self: self._get_on_off_property(":SENS:FRES:DCIR?"),
        fset=lambda self, value: self._set_dry_circuit(value),
        doc="""Control four-wire dry circuit. It limits open-circuit voltage below 20 mV
        and is available for 1 Ω to 10 kΩ ranges.""",
    )
    display_brightness: InstrumentProperty[str] = Instrument.control(
        ":DISP:LIGHT:STAT?",
        ":DISP:LIGHT:STAT %s",
        """Control brightness: ON100, ON75, ON50, ON25, OFF, or BLACKOUT.""",
        validator=strict_discrete_set,
        values=("ON100", "ON75", "ON50", "ON25", "OFF", "BLACKOUT"),
        cast=str,
        get_process=_strip_reply,
        check_get_errors=True,
        check_set_errors=True,
    )

    terminal_selection: InstrumentProperty[str] = _DMM7510Property(
        fget=lambda self: self._query_terminal_selection(),
        doc="""Get FRONT or REAR terminal selection; it can only be changed physically.""",
    )
    reading_buffer_count: InstrumentProperty[int] = _DMM7510Property(
        fget=lambda self: self._query_int_property(':TRAC:ACT? "defbuffer1"'),
        doc="""Get the current number of readings in defbuffer1.""",
    )
    reading_buffer_capacity: InstrumentProperty[int] = _DMM7510Property(
        fget=lambda self: self._query_int_property(':TRAC:POIN? "defbuffer1"'),
        doc="""Get the current capacity of defbuffer1.""",
    )

    current_range: InstrumentProperty[float] = _DMM7510Property(
        fget=lambda self: self._get_range("CURR"),
        fset=lambda self, value: self._set_range("DCI", "CURR", value),
        doc="""Control expected DC current magnitude in A (10 µA to 10 A). The 10 A
        range requires REAR terminals; FRONT terminals support at most 3 A. The
        DMM7510 selects the next sufficient fixed range.""",
    )
    four_wire_resistance_range: InstrumentProperty[float] = _DMM7510Property(
        fget=lambda self: self._get_range("FRES"),
        fset=lambda self, value: self._set_range("FRES", "FRES", value),
        doc="""Control expected four-wire resistance magnitude in ohms (1 Ω to 1 GΩ).
        Offset compensation ON is limited to 100 kΩ and dry circuit to 10 kΩ.
        The DMM7510 selects the next sufficient fixed range.""",
    )

    voltage_nplc: InstrumentProperty[float] = _DMM7510Property(
        fget=lambda self: self._get_nplc("VOLT"),
        fset=lambda self, value: self._set_nplc("VOLT", value),
        doc="""Control DC voltage integration in PLC (0.0005 to 12 at 50 Hz or 15 at
        60 Hz). Values above 12 first query line frequency.""",
    )
    current_nplc: InstrumentProperty[float] = _DMM7510Property(
        fget=lambda self: self._get_nplc("CURR"),
        fset=lambda self, value: self._set_nplc("CURR", value),
        doc="""Control DC current integration in PLC (0.0005 to 12 at 50 Hz or 15 at
        60 Hz). Values above 12 first query line frequency.""",
    )
    resistance_nplc: InstrumentProperty[float] = _DMM7510Property(
        fget=lambda self: self._get_nplc("RES"),
        fset=lambda self, value: self._set_nplc("RES", value),
        doc="""Control two-wire resistance integration in PLC (0.0005 to 12 at 50 Hz or
        15 at 60 Hz). Values above 12 first query line frequency.""",
    )
    four_wire_resistance_nplc: InstrumentProperty[float] = _DMM7510Property(
        fget=lambda self: self._get_nplc("FRES"),
        fset=lambda self, value: self._set_nplc("FRES", value),
        doc="""Control four-wire resistance integration in PLC (0.0005 to 12 at 50 Hz or
        15 at 60 Hz). Values above 12 first query line frequency.""",
    )
    reading_count: InstrumentProperty[int] = _DMM7510Property(
        fget=lambda self: self._get_reading_count(),
        fset=lambda self, value: self._set_reading_count(value),
        doc="""Control reading count from 1 through 1,000,000 and no greater than the
        current defbuffer1 capacity.""",
    )

    def __init__(
        self,
        adapter: Any,
        name: str = "Keithley DMM7510 7½ Digit Multimeter",
        **kwargs: Any,
    ) -> None:
        super().__init__(adapter, name, **kwargs)
        self._pending_count: int | None = None
        self._pending_mode: str | None = None

    def write(self, command: str, **kwargs: Any) -> None:
        """Write a command and clean up a pending acquisition if it fails."""
        try:
            super().write(command, **kwargs)
        except Exception:
            if self._pending_mode is not None:
                self._cleanup_after_error()
            raise

    def ask(self, command: str, query_delay: float | None = None) -> str:
        """Query the instrument and clean up a pending acquisition on failure."""
        with _CleanupOnFailure(self):
            return super().ask(command, query_delay)

    def values(
        self,
        command: str,
        separator: str | None = ",",
        cast: type[Any] | Callable[[str], Any] = float,
        preprocess_reply: Callable[[str], str] | None = None,
        maxsplit: int = -1,
        **kwargs: Any,
    ) -> list[Any]:
        """Read a property value and clean up when communication or parsing fails."""
        with _CleanupOnFailure(self):
            return super().values(
                command,
                separator=separator,
                cast=cast,
                preprocess_reply=preprocess_reply,
                maxsplit=maxsplit,
                **kwargs,
            )

    def _get_function(self) -> str:
        with _CleanupOnFailure(self):
            response = self.ask(":SENS:FUNC?")
            self.check_get_errors()
            function_key = _FUNCTION_REPLIES.get(_strip_reply(response))
            if function_key is not None:
                return function_key
            raise DMM7510MeasurementError(
                f"Unsupported DMM7510 function response: {response!r}."
            )

    def _set_function(self, value: str) -> None:
        function_key = self._validate_function(value)
        if self._pending_mode is not None:
            raise DMM7510MeasurementError(
                "A DMM7510 acquisition is pending; fetch it or abort it before "
                "changing the function."
            )
        with _CleanupOnFailure(self):
            self.write(f':SENS:FUNC "{FUNCTION_PATHS[function_key]}"')
            self.check_set_errors()

    def configure(
        self,
        function: str,
        *,
        range_: float | None = None,
        nplc: float | None = None,
        autozero: bool | str | None = None,
    ) -> None:
        """Configure a supported function and its optional range, NPLC, and autozero.

        :param function: DCV, DCI, RES, FRES, FREQ, PER, CONT, or DIOD.
        :param range_: Expected input magnitude in V, A, or Ω. For FREQ and PER this
            is input voltage. None selects supported autoranging.
        :param nplc: Integration time in power-line cycles for DCV, DCI, RES, or FRES.
        :param autozero: bool to enable/disable autozero, or ONCE for one reference refresh.
        """
        function_key = self._validate_function(function)
        function_path = FUNCTION_PATHS[function_key]
        range_value = self._validate_config_range(function_key, range_)
        nplc_value = self._validate_config_nplc(function_key, nplc)
        autozero_value = self._validate_config_autozero(function_key, autozero)
        if self._pending_mode is not None:
            raise DMM7510MeasurementError(
                "A DMM7510 acquisition is pending; fetch it or abort it before reconfiguration."
            )

        if (
            function_key == "DCI"
            and range_value is not None
            and range_value > 3
            and self._query_terminal_selection() != "REAR"
        ):
            raise ValueError("The 10 A current range requires REAR terminals.")
        if function_key == "FRES" and range_value is not None:
            self._validate_four_wire_range_compatibility(range_value)
        if nplc_value is not None and nplc_value > 12:
            self._validate_line_frequency_for_nplc()

        with _CleanupOnFailure(self):
            self.write(f':SENS:FUNC "{function_path}"')
            if function_key in _RANGE_LIMITS:
                range_path = "THR:RANG" if function_key in {"FREQ", "PER"} else "RANG"
                if range_value is None:
                    self.write(f":SENS:{function_path}:{range_path}:AUTO ON")
                else:
                    self.write(f":SENS:{function_path}:{range_path}:AUTO OFF")
                    self.write(
                        f":SENS:{function_path}:{range_path} {_format_number(range_value)}"
                    )

            if autozero_value is not None:
                if autozero_value == "ONCE":
                    self.write(":SENS:AZER:ONCE")
                else:
                    state = "ON" if autozero_value else "OFF"
                    self.write(f":SENS:{function_path}:AZER:STAT {state}")
                self.write("*WAI")

            if nplc_value is not None:
                self._write_nplc(function_path, nplc_value)

            self._raise_queued_errors()

    def measure(self) -> float:
        """Make one immediate measurement and return its numeric reading."""
        return self.acquire(1)[0]

    def acquire(self, count: int, *, timeout: float = 10.0) -> list[float]:
        """Take an immediate finite group and return all readings in order.

        This helper replaces defbuffer1 contents and its acquisition settings.
        :param count: Positive integer count not greater than defbuffer1 capacity.
        :param timeout: Maximum wait in seconds for completion.
        """
        normalized_count = _validate_count(count)
        normalized_timeout = self._validate_timeout(timeout)
        self._preflight_buffer_capacity(normalized_count)
        with _CleanupOnFailure(self):
            self._abort_and_disable_stimulus()
            self._prepare_finite_buffer()
            self.write(f":SENS:COUN {normalized_count}")
            self._pending_count = normalized_count
            self._pending_mode = "immediate"
            self._raise_queued_errors()
            self.write(f':TRAC:TRIG "{_DEFAULT_BUFFER}"')
            self._raise_queued_errors()
            self._wait_for_buffer_count(normalized_count, normalized_timeout)
            readings = self._read_exact_buffer(normalized_count)
            self._finish_acquisition()
            return readings

    def initiate(self, count: int, *, delay: float = 0.0) -> None:
        """Start a finite SimpleLoop acquisition into defbuffer1.

        The trigger-model count is separate from SENS:COUN. One reading is
        requested per SimpleLoop iteration.
        :param count: Positive integer loop count not greater than buffer capacity.
        :param delay: Zero or a delay from 167 ns through 10,000 s.
        """
        normalized_count = _validate_count(count)
        normalized_delay = self._validate_delay(delay)
        self._preflight_buffer_capacity(normalized_count)
        with _CleanupOnFailure(self):
            self._abort_and_disable_stimulus()
            self._prepare_finite_buffer()
            self.write(":SENS:COUN 1")
            self.write(
                f':TRIG:LOAD "SimpleLoop", {normalized_count}, '
                f'{_format_number(normalized_delay)}, '
                f'"{_DEFAULT_BUFFER}"'
            )
            self._pending_count = normalized_count
            self._pending_mode = "simple_loop"
            self.write(":INIT")
            self._raise_queued_errors()

    def arm(self, count: int) -> None:
        """Arm one command-triggered burst into defbuffer1.

        Call :meth:`trigger` once for this burst. A second command trigger can
        latch another burst on the instrument.
        :param count: Positive integer burst size not greater than buffer capacity.
        """
        normalized_count = _validate_count(count)
        self._preflight_buffer_capacity(normalized_count)
        with _CleanupOnFailure(self):
            self._abort_and_disable_stimulus()
            self._prepare_finite_buffer()
            self.write(f":SENS:COUN {normalized_count}")
            self._pending_count = normalized_count
            self._pending_mode = "bus_armed"
            self.write(":SENS:TRIG:MEAS:STIM COMM")
            self._raise_queued_errors()

    def trigger(self) -> None:
        """Send one IEEE 488.2 command trigger for a previously armed burst."""
        if self._pending_mode != "bus_armed":
            raise DMM7510MeasurementError("Call arm(count) before trigger().")
        with _CleanupOnFailure(self):
            self.write("*TRG")
            self._raise_queued_errors()
            self._pending_mode = "bus_triggered"

    def fetch(self, *, timeout: float = 10.0) -> list[float]:
        """Fetch readings for a pending acquisition without initiating or triggering it.

        :param timeout: Maximum wait in seconds for completion.
        :raises DMM7510MeasurementError: If there is no pending acquisition.
        """
        normalized_timeout = self._validate_timeout(timeout)
        if self._pending_count is None or self._pending_mode is None:
            raise DMM7510MeasurementError("There is no pending DMM7510 acquisition to fetch.")
        if self._pending_mode == "bus_armed":
            with _CleanupOnFailure(self):
                raise DMM7510MeasurementError(
                    "The command-triggered acquisition has not been triggered."
                )

        expected_count = self._pending_count
        with _CleanupOnFailure(self):
            if self._pending_mode == "simple_loop":
                self._wait_for_trigger_model(expected_count, normalized_timeout)
            elif self._pending_mode == "bus_triggered":
                self._wait_for_buffer_count(expected_count, normalized_timeout)
            else:
                raise DMM7510MeasurementError(
                    f"Unknown pending acquisition state {self._pending_mode!r}."
                )
            readings = self._read_exact_buffer(expected_count)
            self._finish_acquisition()
            return readings

    def abort(self) -> None:
        """Abort the trigger model and disable command-trigger stimulus."""
        self._abort_and_disable_stimulus()

    def clear_buffer(self) -> None:
        """Abort pending work and clear readings and statistics from defbuffer1."""
        with _CleanupOnFailure(self):
            self._abort_and_disable_stimulus()
            self.write(f':TRAC:CLE "{_DEFAULT_BUFFER}"')
            self._clear_acquisition_state()
            self._raise_queued_errors()

    def reset(self) -> None:
        """Reset the instrument and clear the local acquisition state."""
        try:
            self.write("*RST")
        finally:
            self._clear_acquisition_state()

    def check_errors(self) -> list[list[float | str]]:
        """Read errors with DMM7510 SYST:ERR:NEXT? semantics, up to the queue limit."""
        with _CleanupOnFailure(self):
            errors = self._drain_scpi_errors()
        if errors and self._pending_mode is not None:
            self._disable_after_scpi_error()
            with _LoggedExceptionSuppressor(
                "DMM7510 error cleanup could not drain follow-up errors"
            ):
                errors.extend(self._drain_scpi_errors())
        return errors

    def check_get_errors(self) -> list[list[float | str]]:
        """Raise an actionable exception for a nonzero property-query SCPI error."""
        return self._checked_errors()

    def check_set_errors(self) -> list[list[float | str]]:
        """Raise an actionable exception for a nonzero property-set SCPI error."""
        return self._checked_errors()

    @staticmethod
    def _validate_function(function: str) -> str:
        if not isinstance(function, str):
            raise TypeError("function must be a supported DMM7510 function name.")
        normalized = function.strip().upper()
        if normalized not in FUNCTION_PATHS:
            choices = ", ".join(FUNCTION_PATHS)
            raise ValueError(f"Unsupported function {function!r}; expected one of {choices}.")
        return normalized

    @staticmethod
    def _validate_config_range(function: str, value: float | None) -> float | None:
        if value is None:
            return None
        if function not in _RANGE_LIMITS:
            raise ValueError(f"{function} does not support a range option.")
        return _validate_range(value, _RANGE_LIMITS[function])

    @staticmethod
    def _validate_config_nplc(function: str, value: float | None) -> float | None:
        if value is None:
            return None
        if function not in _NPLC_FUNCTIONS:
            raise ValueError(f"{function} does not support NPLC in this driver.")
        return _validate_range(value, (0.0005, 15.0))

    @staticmethod
    def _validate_config_autozero(
        function: str, value: bool | str | None
    ) -> bool | str | None:
        if value is None:
            return None
        if function not in _AUTOZERO_FUNCTIONS:
            raise ValueError(f"{function} does not support autozero in this driver.")
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.strip().upper() == "ONCE":
            return "ONCE"
        raise ValueError("autozero must be bool, 'ONCE', or None.")

    @staticmethod
    def _validate_timeout(timeout: float) -> float:
        value = _validate_finite_number(timeout, "timeout")
        if value <= 0:
            raise ValueError("timeout must be greater than zero seconds.")
        return value

    @staticmethod
    def _validate_delay(delay: float) -> float:
        value = _validate_finite_number(delay, "delay")
        if value != 0 and not 167e-9 <= value <= 10_000:
            raise ValueError("delay must be zero or from 167 ns through 10,000 s.")
        return value

    def _preflight_buffer_capacity(self, count: int) -> None:
        capacity = self.reading_buffer_capacity
        if count > capacity:
            raise ValueError(f"count {count} exceeds defbuffer1 capacity {capacity}.")

    def _validate_line_frequency_for_nplc(self) -> None:
        with _CleanupOnFailure(self):
            response = self.ask(":SYST:LFR?")
            self._raise_queued_errors()
            try:
                frequency = _parse_float_reply(response)
            except DMM7510MeasurementError as exc:
                raise ValueError(
                    "Cannot validate NPLC above 12 with ambiguous line frequency."
                ) from exc
        if frequency == 50:
            raise ValueError("NPLC above 12 is unsupported at 50 Hz.")
        if frequency != 60:
            raise ValueError(
                f"NPLC above 12 requires verified 60 Hz line frequency, got {frequency:g} Hz."
            )

    def _validate_four_wire_range_compatibility(self, expected: float) -> None:
        dry_enabled = self._query_on_off(":SENS:FRES:DCIR?")
        if dry_enabled and expected > 10_000:
            raise ValueError("Four-wire dry circuit is limited to ranges through 10 kΩ.")
        if expected > 100_000 and self._query_offset_compensation() == "ON":
            raise ValueError("Four-wire offset compensation ON is limited to 100 kΩ.")

    def _prepare_finite_buffer(self) -> None:
        self.write(f':DISP:BUFF:ACT "{_DEFAULT_BUFFER}"')
        self.write(":FORM:DATA ASC")
        self.write(f':TRAC:FILL:MODE ONCE, "{_DEFAULT_BUFFER}"')
        self.write(f':TRAC:CLE "{_DEFAULT_BUFFER}"')

    def _wait_for_buffer_count(self, expected: int, timeout: float) -> None:
        deadline = time.monotonic() + timeout
        while True:
            actual = self.reading_buffer_count
            if actual > expected:
                raise DMM7510MeasurementError(
                    f"Expected {expected} readings in defbuffer1; found {actual}."
                )
            if actual == expected:
                return
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(
                    f"Timed out after {timeout:g} s waiting for {expected} DMM7510 readings; "
                    f"found {actual}."
                )
            time.sleep(min(_POLL_INTERVAL_S, remaining))

    def _wait_for_trigger_model(self, expected: int, timeout: float) -> None:
        deadline = time.monotonic() + timeout
        while True:
            response = self.ask(":TRIG:STAT?").strip().upper()
            self._raise_queued_errors()
            fields = response.split(";")
            if len(fields) != 3 or not fields[0].strip() or not fields[1].strip():
                raise DMM7510MeasurementError(f"Malformed DMM7510 trigger state {response!r}.")
            states = [field.strip() for field in fields[:2]]
            try:
                int(fields[2].strip())
            except ValueError as exc:
                raise DMM7510MeasurementError(
                    f"Malformed DMM7510 trigger block index in {response!r}."
                ) from exc
            for state in states:
                if state not in _TRIGGER_STATES:
                    raise DMM7510MeasurementError(
                        f"Unknown DMM7510 trigger model state {state!r}."
                    )
                if state in {"FAILED", "ABORTED", "EMPTY"}:
                    raise DMM7510MeasurementError(
                        f"DMM7510 trigger model ended in state {state}: {response}."
                    )
            if states == ["IDLE", "IDLE"]:
                return
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(
                    f"Timed out after {timeout:g} s waiting for {expected} DMM7510 readings."
                )
            time.sleep(min(_POLL_INTERVAL_S, remaining))

    def _read_exact_buffer(self, expected: int) -> list[float]:
        actual = self.reading_buffer_count
        if actual != expected:
            raise DMM7510MeasurementError(
                f"Expected {expected} readings in defbuffer1; found {actual}."
            )
        response = self.ask(f':TRAC:DATA? 1, {expected}, "{_DEFAULT_BUFFER}", READ')
        self._raise_queued_errors()
        readings = self._parse_readings(response)
        if len(readings) != expected:
            raise DMM7510MeasurementError(
                f"Expected {expected} readings; received {len(readings)} values."
            )
        return readings

    @staticmethod
    def _parse_readings(response: str) -> list[float]:
        text = response.strip()
        if not text:
            raise DMM7510MeasurementError("DMM7510 returned an empty reading response.")
        readings: list[float] = []
        for token in text.split(","):
            token = token.strip()
            if not token:
                raise DMM7510MeasurementError(
                    f"DMM7510 returned an empty reading field in {response!r}."
                )
            try:
                value = float(token)
            except ValueError as exc:
                raise DMM7510MeasurementError(
                    f"Malformed DMM7510 reading {token!r} in {response!r}."
                ) from exc
            if not math.isfinite(value):
                raise DMM7510MeasurementError(
                    f"Nonfinite DMM7510 reading {token!r} in {response!r}."
                )
            readings.append(value)
        return readings

    def _finish_acquisition(self) -> None:
        self.write(":SENS:TRIG:MEAS:STIM NONE")
        self._raise_queued_errors()
        self._clear_acquisition_state()

    def _abort_and_disable_stimulus(self) -> None:
        self._clear_acquisition_state()
        first_error: Exception | None = None
        for command in (":ABOR", ":SENS:TRIG:MEAS:STIM NONE"):
            error = self._write_best_effort(command)
            if first_error is None and error is not None:
                first_error = error
        if first_error is not None:
            raise first_error
        self._raise_queued_errors()

    def _write_best_effort(self, command: str) -> Exception | None:
        capture = _CaptureException()
        with capture:
            self.write(command)
        return capture.exception

    def _cleanup_after_error(self) -> None:
        if self._pending_mode is None:
            self._clear_acquisition_state()
            return
        try:
            with _LoggedExceptionSuppressor("DMM7510 acquisition cleanup failed"):
                self._abort_and_disable_stimulus()
        finally:
            self._clear_acquisition_state()

    def _clear_acquisition_state(self) -> None:
        self._pending_count = None
        self._pending_mode = None

    def _drain_scpi_errors(self) -> list[list[float | str]]:
        errors: list[list[float | str]] = []
        for _ in range(_SCPI_ERROR_QUEUE_LIMIT):
            response = self.ask(":SYST:ERR:NEXT?").strip()
            try:
                fields = next(csv.reader([response], skipinitialspace=True))
                code_value = float(fields[0].strip())
                if not math.isfinite(code_value) or not code_value.is_integer():
                    raise ValueError
                code = int(code_value)
            except (ValueError, IndexError, csv.Error) as exc:
                raise DMM7510SCPIError(
                    f"Malformed DMM7510 SYST:ERR:NEXT? response: {response!r}."
                ) from exc
            if code == 0:
                return errors
            message = fields[1].strip() if len(fields) > 1 else "Unspecified SCPI error"
            errors.append([code, message])
            log.error("%s: %s: %s", self.name, code, message)
        raise DMM7510SCPIError(
            f"DMM7510 error queue did not terminate after {_SCPI_ERROR_QUEUE_LIMIT} entries."
        )

    def _disable_after_scpi_error(self) -> None:
        for command in (":ABOR", ":SENS:TRIG:MEAS:STIM NONE"):
            cleanup_error = self._write_best_effort(command)
            if cleanup_error is not None:
                log.warning(
                    "DMM7510 trigger cleanup failed after an SCPI error: %s", cleanup_error
                )
        self._clear_acquisition_state()

    def _checked_errors(self) -> list[list[float | str]]:
        errors = self.check_errors()
        if errors:
            self._clear_acquisition_state()
            details = "; ".join(f"{error[0]}: {error[1]}" for error in errors)
            raise DMM7510SCPIError("DMM7510 SCPI errors: " + details)
        return []

    def _raise_queued_errors(self) -> None:
        self._checked_errors()

    def _query_float_property(self, command: str) -> float:
        with _CleanupOnFailure(self):
            response = self.ask(command)
            self.check_get_errors()
            return _parse_float_reply(response)

    def _query_int_property(self, command: str) -> int:
        with _CleanupOnFailure(self):
            response = self.ask(command)
            self.check_get_errors()
            return _parse_int_reply(response)

    def _query_terminal_selection(self) -> str:
        with _CleanupOnFailure(self):
            response = self.ask(":ROUT:TERM?")
            self._raise_queued_errors()
            return _normalize_terminal(response)

    def _query_on_off(self, command: str) -> bool:
        with _CleanupOnFailure(self):
            response = self.ask(command)
            self._raise_queued_errors()
            return _normalize_on_off(response) == "ON"

    def _query_offset_compensation(self) -> str:
        with _CleanupOnFailure(self):
            response = self.ask(":SENS:FRES:OCOM?")
            self._raise_queued_errors()
            option = _strip_reply(response)
            if option == "0":
                option = "OFF"
            elif option == "1":
                option = "ON"
            if option not in {"OFF", "ON", "AUTO"}:
                raise DMM7510MeasurementError(
                    f"Invalid four-wire offset compensation response: {response!r}."
                )
            return option

    def _get_on_off_property(self, command: str) -> bool:
        return self._query_on_off(command)

    def _set_dry_circuit(self, value: bool) -> None:
        enabled = _validate_bool(value, "dry_circuit_enabled")
        if enabled and self._get_range("FRES") > 10_000:
            raise ValueError("Four-wire dry circuit is limited to ranges through 10 kΩ.")
        self.write(f":SENS:FRES:DCIR {'ON' if enabled else 'OFF'}")
        self._raise_queued_errors()

    def _set_offset_compensation(self, value: str) -> None:
        if not isinstance(value, str) or value.strip().upper() not in {"OFF", "ON", "AUTO"}:
            raise ValueError("four_wire_offset_compensation must be OFF, ON, or AUTO.")
        option = value.strip().upper()
        if option == "ON" and self._get_range("FRES") > 100_000:
            raise ValueError(
                "Four-wire offset compensation ON is limited to ranges through 100 kΩ."
            )
        self.write(f":SENS:FRES:OCOM {option}")
        self._raise_queued_errors()

    def _get_range(self, function_path: str) -> float:
        with _CleanupOnFailure(self):
            response = self.ask(f":SENS:{function_path}:RANG?")
            self._raise_queued_errors()
            return _parse_float_reply(response)

    def _set_range(self, function_key: str, function_path: str, value: float) -> None:
        range_value = _validate_range(value, _RANGE_LIMITS[function_key])
        if (
            function_key == "DCI"
            and range_value > 3
            and self._query_terminal_selection() != "REAR"
        ):
            raise ValueError("The 10 A current range requires REAR terminals.")
        if function_key == "FRES":
            self._validate_four_wire_range_compatibility(range_value)
        self.write(
            f":SENS:{function_path}:RANG:AUTO OFF;:SENS:{function_path}:RANG "
            f"{_format_number(range_value)}"
        )
        self._raise_queued_errors()

    def _get_nplc(self, function_path: str) -> float:
        with _CleanupOnFailure(self):
            response = self.ask(f":SENS:{function_path}:NPLC?")
            self._raise_queued_errors()
            return _parse_float_reply(response)

    def _set_nplc(self, function_path: str, value: float) -> None:
        nplc = _validate_range(value, (0.0005, 15.0))
        if nplc > 12:
            self._validate_line_frequency_for_nplc()
        self._write_nplc(function_path, nplc)
        self._raise_queued_errors()

    def _write_nplc(self, function_path: str, nplc: float) -> None:
        self.write(f":SENS:{function_path}:NPLC {_format_number(nplc)}")
        # Inherited JLDevKit DMM7510 firmware evidence showed immediate follow-up
        # access could time out.
        time.sleep(_POST_NPLC_SETTLE_S)

    def _get_reading_count(self) -> int:
        with _CleanupOnFailure(self):
            response = self.ask(":SENS:COUN?")
            self._raise_queued_errors()
            return _parse_int_reply(response)

    def _set_reading_count(self, value: int) -> None:
        count = _validate_count(value)
        self._preflight_buffer_capacity(count)
        self.write(f":SENS:COUN {count}")
        self._raise_queued_errors()


def _normalize_terminal(value: str) -> str:
    terminal = _strip_reply(value)
    if terminal == "FRON":
        return "FRONT"
    if terminal in {"FRONT", "REAR"}:
        return terminal
    raise DMM7510MeasurementError(f"Invalid DMM7510 terminal response: {value!r}.")


__all__ = ["DMM7510MeasurementError", "DMM7510SCPIError", "KeithleyDMM7510"]
