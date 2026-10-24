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

from unittest.mock import Mock

import pytest

from pymeasure.instruments.keithley import (
    DMM7510MeasurementError,
    DMM7510SCPIError,
    KeithleyDMM7510,
)
from pymeasure.test import expected_protocol


def _error_ok() -> tuple[bytes, bytes]:
    return b":SYST:ERR:NEXT?", b'0,"No error"'


def _capacity(count: int = 100) -> list[tuple[bytes, bytes | None]]:
    return [(b':TRAC:POIN? "defbuffer1"', str(count).encode()), _error_ok()]


def _acquire_protocol(count: int, data: bytes) -> list[tuple[bytes, bytes | None]]:
    pairs: list[tuple[bytes, bytes | None]] = _capacity(max(count, 100))
    pairs.extend([
        (b":ABOR", None),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
        _error_ok(),
        (b':DISP:BUFF:ACT "defbuffer1"', None),
        (b":FORM:DATA ASC", None),
        (b':TRAC:FILL:MODE ONCE, "defbuffer1"', None),
        (b':TRAC:CLE "defbuffer1"', None),
        (f":SENS:COUN {count}".encode(), None),
        _error_ok(),
        (b':TRAC:TRIG "defbuffer1"', None),
        _error_ok(),
        (b':TRAC:ACT? "defbuffer1"', str(count).encode()),
        _error_ok(),
        (b':TRAC:ACT? "defbuffer1"', str(count).encode()),
        _error_ok(),
        (f':TRAC:DATA? 1, {count}, "defbuffer1", READ'.encode(), data),
        _error_ok(),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
        _error_ok(),
    ])
    return pairs


def _arm_protocol() -> list[tuple[bytes, bytes | None]]:
    pairs = _capacity()
    pairs.extend([
        (b":ABOR", None),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
        _error_ok(),
        (b':DISP:BUFF:ACT "defbuffer1"', None),
        (b":FORM:DATA ASC", None),
        (b':TRAC:FILL:MODE ONCE, "defbuffer1"', None),
        (b':TRAC:CLE "defbuffer1"', None),
        (b":SENS:COUN 2", None),
        (b":SENS:TRIG:MEAS:STIM COMM", None),
        _error_ok(),
    ])
    return pairs


def test_constructor_is_silent_and_does_not_change_scpi_mode():
    with expected_protocol(KeithleyDMM7510, []):
        pass


def test_function_property_maps_native_function_names():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b":SENS:FUNC?", b'"VOLT:DC"'),
            _error_ok(),
        ],
    ) as instrument:
        assert instrument.function == "DCV"


def test_configure_uses_frequency_input_voltage_threshold_range():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b':SENS:FUNC "FREQ"', None),
            (b":SENS:FREQ:THR:RANG:AUTO OFF", None),
            (b":SENS:FREQ:THR:RANG 90", None),
            _error_ok(),
        ],
    ) as instrument:
        instrument.configure("FREQ", range_=90)


@pytest.mark.parametrize(
    ("function", "range_value", "commands", "preflight"),
    [
        (
            "DCV",
            0.1,
            [
                (b':SENS:FUNC "VOLT"', None),
                (b":SENS:VOLT:RANG:AUTO OFF", None),
                (b":SENS:VOLT:RANG 0.1", None),
            ],
            [],
        ),
        (
            "RES",
            9_000,
            [
                (b':SENS:FUNC "RES"', None),
                (b":SENS:RES:RANG:AUTO OFF", None),
                (b":SENS:RES:RANG 9000", None),
            ],
            [],
        ),
        (
            "FRES",
            9_000,
            [
                (b':SENS:FUNC "FRES"', None),
                (b":SENS:FRES:RANG:AUTO OFF", None),
                (b":SENS:FRES:RANG 9000", None),
            ],
            [(b":SENS:FRES:DCIR?", b"OFF"), _error_ok()],
        ),
        (
            "PER",
            90,
            [
                (b':SENS:FUNC "PER"', None),
                (b":SENS:PER:THR:RANG:AUTO OFF", None),
                (b":SENS:PER:THR:RANG 90", None),
            ],
            [],
        ),
    ],
)
def test_configure_manual_ranges_use_expected_magnitude(function, range_value, commands, preflight):
    pairs = list(preflight) + commands + [_error_ok()]
    with expected_protocol(KeithleyDMM7510, pairs) as instrument:
        instrument.configure(function, range_=range_value)


def test_voltage_range_property_preserves_expected_magnitude_precision():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (
                b":SENS:VOLT:RANG:AUTO OFF;:SENS:VOLT:RANG 10.000001",
                None,
            ),
            _error_ok(),
        ],
    ) as instrument:
        instrument.voltage_range = 10.000001


@pytest.mark.parametrize(
    "kwargs",
    [
        {"range_": 1.0},
        {"nplc": 1.0},
        {"autozero": True},
    ],
)
@pytest.mark.parametrize("function", ["CONT", "DIOD"])
def test_fixed_range_functions_reject_unsupported_options_before_io(function, kwargs):
    with expected_protocol(KeithleyDMM7510, []) as instrument, pytest.raises(ValueError):
        instrument.configure(function, **kwargs)


@pytest.mark.parametrize(
    ("function", "kwargs"),
    [
        ("FREQ", {"nplc": 1.0}),
        ("FREQ", {"autozero": False}),
        ("PER", {"nplc": 1.0}),
        ("PER", {"autozero": "ONCE"}),
        ("DCV", {"range_": 0.1, "nplc": True}),
        ("DCI", {"range_": 1.0, "autozero": "YES"}),
        ("RES", {"range_": float("nan")}),
        ("FRES", {"nplc": float("inf")}),
    ],
)
def test_invalid_composite_configuration_has_no_hardware_writes(function, kwargs):
    with expected_protocol(KeithleyDMM7510, []) as instrument, pytest.raises(
        (TypeError, ValueError)
    ):
        instrument.configure(function, **kwargs)


def test_unknown_function_is_rejected_before_io():
    with expected_protocol(KeithleyDMM7510, []) as instrument, pytest.raises(
        ValueError, match="Unsupported function"
    ):
        instrument.configure("ACV")


def test_configure_requires_pending_acquisition_to_be_fetched_or_aborted():
    with expected_protocol(KeithleyDMM7510, []) as instrument, pytest.raises(
        DMM7510MeasurementError, match="pending"
    ):
        instrument._pending_count = 2
        instrument._pending_mode = "bus_armed"
        instrument.configure("DCV")
    assert instrument._pending_count == 2
    assert instrument._pending_mode == "bus_armed"


def test_function_property_cannot_change_during_pending_acquisition():
    with expected_protocol(KeithleyDMM7510, []) as instrument, pytest.raises(
        DMM7510MeasurementError, match="pending"
    ):
        instrument._pending_count = 2
        instrument._pending_mode = "bus_armed"
        instrument.function = "DCV"
    assert instrument._pending_count == 2
    assert instrument._pending_mode == "bus_armed"


def test_front_terminals_reject_expected_current_above_three_amps_before_writes():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b":ROUT:TERM?", b"FRON"),
            _error_ok(),
        ],
    ) as instrument, pytest.raises(ValueError, match="REAR"):
        instrument.configure("DCI", range_=9.0)


def test_rear_terminals_allow_ten_amp_range_and_disable_autorange():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b":ROUT:TERM?", b"REAR"),
            _error_ok(),
            (b':SENS:FUNC "CURR"', None),
            (b":SENS:CURR:RANG:AUTO OFF", None),
            (b":SENS:CURR:RANG 9", None),
            _error_ok(),
        ],
    ) as instrument:
        instrument.configure("DCI", range_=9.0)


def test_current_range_property_checks_terminals_before_writing():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b":ROUT:TERM?", b"FRONT"),
            _error_ok(),
        ],
    ) as instrument, pytest.raises(ValueError, match="REAR"):
        instrument.current_range = 10.0


def test_configure_nplc_through_twelve_does_not_query_line_frequency():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b':SENS:FUNC "VOLT"', None),
            (b":SENS:VOLT:RANG:AUTO ON", None),
            (b":SENS:VOLT:NPLC 12", None),
            _error_ok(),
        ],
    ) as instrument:
        instrument.configure("DCV", nplc=12)


def test_configure_rejects_nplc_above_twelve_at_fifty_hertz_before_write():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b":SYST:LFR?", b"50"),
            _error_ok(),
        ],
    ) as instrument, pytest.raises(ValueError, match="50 Hz"):
        instrument.configure("DCV", nplc=12.1)


def test_configure_rejects_unsupported_nplc_when_line_frequency_is_ambiguous():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b":SYST:LFR?", b"400"),
            _error_ok(),
        ],
    ) as instrument, pytest.raises(ValueError, match="60 Hz"):
        instrument.configure("DCV", nplc=13)


def test_configure_accepts_nplc_above_twelve_at_sixty_hertz_and_settles(monkeypatch):
    sleep = Mock()
    monkeypatch.setattr("pymeasure.instruments.keithley.keithleydmm7510.time.sleep", sleep)
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b":SYST:LFR?", b"60"),
            _error_ok(),
            (b':SENS:FUNC "VOLT"', None),
            (b":SENS:VOLT:RANG:AUTO ON", None),
            (b":SENS:VOLT:NPLC 12.5", None),
            _error_ok(),
        ],
    ) as instrument:
        instrument.configure("DCV", nplc=12.5)
    sleep.assert_called_once_with(0.2)


def test_autozero_once_is_synchronized_before_nplc(monkeypatch):
    sleep = Mock()
    monkeypatch.setattr("pymeasure.instruments.keithley.keithleydmm7510.time.sleep", sleep)
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b':SENS:FUNC "VOLT"', None),
            (b":SENS:VOLT:RANG:AUTO ON", None),
            (b":SENS:AZER:ONCE", None),
            (b"*WAI", None),
            (b":SENS:VOLT:NPLC 0.5", None),
            _error_ok(),
        ],
    ) as instrument:
        instrument.configure("DCV", autozero="ONCE", nplc=0.5)
    sleep.assert_called_once_with(0.2)


def test_four_wire_range_rejects_dry_circuit_conflict_before_writes():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b":SENS:FRES:DCIR?", b"1"),
            _error_ok(),
        ],
    ) as instrument, pytest.raises(ValueError, match="10 kΩ"):
        instrument.configure("FRES", range_=20_000)


def test_four_wire_range_rejects_offset_compensation_conflict_before_writes():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b":SENS:FRES:DCIR?", b"OFF"),
            _error_ok(),
            (b":SENS:FRES:OCOM?", b"ON"),
            _error_ok(),
        ],
    ) as instrument, pytest.raises(ValueError, match="100 kΩ"):
        instrument.configure("FRES", range_=200_000)


def test_offset_compensation_and_dry_circuit_controls():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b":SENS:FRES:OCOM AUTO", None),
            _error_ok(),
            (b":SENS:FRES:RANG?", b"1000"),
            _error_ok(),
            (b":SENS:FRES:DCIR ON", None),
            _error_ok(),
        ],
    ) as instrument:
        instrument.four_wire_offset_compensation = "AUTO"
        instrument.dry_circuit_enabled = True


def test_boolean_autozero_property_uses_function_specific_command():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b":SENS:CURR:AZER:STAT ON", None),
            _error_ok(),
        ],
    ) as instrument:
        instrument.current_autozero_enabled = True


def test_boolean_configuration_property_rejects_integer_before_io():
    with expected_protocol(KeithleyDMM7510, []) as instrument, pytest.raises(
        TypeError, match="bool values"
    ):
        instrument.voltage_autorange = 1


def test_reading_count_property_checks_capacity_before_writing():
    with expected_protocol(
        KeithleyDMM7510,
        _capacity(8)
        + [
            (b":SENS:COUN 8", None),
            _error_ok(),
        ],
    ) as instrument:
        instrument.reading_count = 8


def test_clear_buffer_aborts_and_clears_only_defbuffer1():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b":ABOR", None),
            (b":SENS:TRIG:MEAS:STIM NONE", None),
            _error_ok(),
            (b':TRAC:CLE "defbuffer1"', None),
            _error_ok(),
        ],
    ) as instrument:
        instrument.clear_buffer()


def test_acquire_preserves_order_sign_scientific_values_and_overload():
    readings = b"-1.25E-3, 4.5e+2, 9.9e37"
    with expected_protocol(KeithleyDMM7510, _acquire_protocol(3, readings)) as instrument:
        assert instrument.acquire(3) == [-0.00125, 450.0, 9.9e37]


def test_single_after_group_restores_count_and_immediate_mode_across_functions():
    pairs = _acquire_protocol(2, b"1,2")
    pairs.extend([
        (b':SENS:FUNC "CURR"', None),
        (b":SENS:CURR:RANG:AUTO ON", None),
        _error_ok(),
    ])
    pairs.extend(_acquire_protocol(1, b"-0.25"))
    with expected_protocol(KeithleyDMM7510, pairs) as instrument:
        assert instrument.acquire(2) == [1.0, 2.0]
        instrument.configure("DCI")
        assert instrument.measure() == -0.25


def test_count_one_group_returns_a_list():
    with expected_protocol(KeithleyDMM7510, _acquire_protocol(1, b"-0.5")) as instrument:
        assert instrument.acquire(1) == [-0.5]


def test_acquire_count_validation_precedes_capacity_query():
    invalid_counts = [True, 0, -1, 1.5, float("nan"), float("inf"), 1_000_001]
    for count in invalid_counts:
        with expected_protocol(KeithleyDMM7510, []) as instrument, pytest.raises(
            (TypeError, ValueError)
        ):
            instrument.acquire(count)


def test_acquire_rejects_count_above_actual_buffer_capacity_before_clearing():
    with expected_protocol(KeithleyDMM7510, _capacity(2)) as instrument, pytest.raises(
        ValueError, match="capacity 2"
    ):
        instrument.acquire(3)


def test_read_exact_buffer_rejects_partial_count_before_data_query():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b':TRAC:ACT? "defbuffer1"', b"1"),
            _error_ok(),
        ],
    ) as instrument, pytest.raises(DMM7510MeasurementError, match="Expected 2 readings"):
        instrument._read_exact_buffer(2)


def test_read_exact_buffer_rejects_excess_count_before_data_query():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b':TRAC:ACT? "defbuffer1"', b"3"),
            _error_ok(),
        ],
    ) as instrument, pytest.raises(DMM7510MeasurementError, match="found 3"):
        instrument._read_exact_buffer(2)


def test_read_exact_buffer_rejects_partial_data_response():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b':TRAC:ACT? "defbuffer1"', b"3"),
            _error_ok(),
            (b':TRAC:DATA? 1, 3, "defbuffer1", READ', b"1.0,2.0"),
            _error_ok(),
        ],
    ) as instrument, pytest.raises(DMM7510MeasurementError, match="received 2 values"):
        instrument._read_exact_buffer(3)


def test_read_exact_buffer_rejects_excess_data_response():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b':TRAC:ACT? "defbuffer1"', b"2"),
            _error_ok(),
            (b':TRAC:DATA? 1, 2, "defbuffer1", READ', b"1.0,2.0,3.0"),
            _error_ok(),
        ],
    ) as instrument, pytest.raises(DMM7510MeasurementError, match="received 3 values"):
        instrument._read_exact_buffer(2)


@pytest.mark.parametrize("response", [b"", b"1,,2", b"1,broken", b"nan", b"inf"])
def test_read_exact_buffer_rejects_empty_malformed_or_nonfinite_data(response):
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b':TRAC:ACT? "defbuffer1"', b"1"),
            _error_ok(),
            (b':TRAC:DATA? 1, 1, "defbuffer1", READ', response),
            _error_ok(),
        ],
    ) as instrument, pytest.raises(DMM7510MeasurementError):
        instrument._read_exact_buffer(1)


def test_initiate_uses_simple_loop_and_fetch_waits_for_idle():
    pairs = _capacity()
    pairs.extend([
        (b":ABOR", None),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
        _error_ok(),
        (b':DISP:BUFF:ACT "defbuffer1"', None),
        (b":FORM:DATA ASC", None),
        (b':TRAC:FILL:MODE ONCE, "defbuffer1"', None),
        (b':TRAC:CLE "defbuffer1"', None),
        (b":SENS:COUN 1", None),
        (b':TRIG:LOAD "SimpleLoop", 3, 0.001, "defbuffer1"', None),
        (b":INIT", None),
        _error_ok(),
        (b":TRIG:STAT?", b"IDLE;IDLE;9"),
        _error_ok(),
        (b':TRAC:ACT? "defbuffer1"', b"3"),
        _error_ok(),
        (b':TRAC:DATA? 1, 3, "defbuffer1", READ', b"1,2,3"),
        _error_ok(),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
        _error_ok(),
    ])
    with expected_protocol(KeithleyDMM7510, pairs) as instrument:
        instrument.initiate(3, delay=0.001)
        assert instrument.fetch() == [1.0, 2.0, 3.0]


def test_trigger_model_polling_accepts_running_then_idle(monkeypatch):
    monkeypatch.setattr(
        "pymeasure.instruments.keithley.keithleydmm7510.time.monotonic", lambda: 0.0
    )
    sleep = Mock()
    monkeypatch.setattr("pymeasure.instruments.keithley.keithleydmm7510.time.sleep", sleep)
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b":TRIG:STAT?", b"RUNNING;WAITING;4"),
            _error_ok(),
            (b":TRIG:STAT?", b"IDLE;IDLE;9"),
            _error_ok(),
        ],
    ) as instrument:
        instrument._wait_for_trigger_model(2, 1.0)
    sleep.assert_called_once_with(0.05)


@pytest.mark.parametrize(
    "state",
    [
        "FAILED;FAILED;9",
        "ABORTED;IDLE;9",
        "EMPTY;EMPTY;0",
        "IDLE;IDLE",
        "IDLE;IDLE;block",
        "UNKNOWN;IDLE;0",
    ],
)
def test_trigger_model_failed_aborted_and_malformed_states_are_explicit(state):
    with expected_protocol(
        KeithleyDMM7510,
        [(b":TRIG:STAT?", state.encode()), _error_ok()],
    ) as instrument, pytest.raises(DMM7510MeasurementError):
        instrument._wait_for_trigger_model(1, 1.0)


def test_fetch_after_arm_does_not_trigger_and_disarms():
    pairs = _capacity()
    pairs.extend([
        (b":ABOR", None),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
        _error_ok(),
        (b':DISP:BUFF:ACT "defbuffer1"', None),
        (b":FORM:DATA ASC", None),
        (b':TRAC:FILL:MODE ONCE, "defbuffer1"', None),
        (b':TRAC:CLE "defbuffer1"', None),
        (b":SENS:COUN 2", None),
        (b":SENS:TRIG:MEAS:STIM COMM", None),
        _error_ok(),
        (b":ABOR", None),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
        _error_ok(),
    ])
    with expected_protocol(KeithleyDMM7510, pairs) as instrument, pytest.raises(
        DMM7510MeasurementError, match="has not been triggered"
    ):
        instrument.arm(2)
        instrument.fetch()


def test_bus_trigger_is_separate_from_arm_and_fetch():
    pairs = _capacity()
    pairs.extend([
        (b":ABOR", None),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
        _error_ok(),
        (b':DISP:BUFF:ACT "defbuffer1"', None),
        (b":FORM:DATA ASC", None),
        (b':TRAC:FILL:MODE ONCE, "defbuffer1"', None),
        (b':TRAC:CLE "defbuffer1"', None),
        (b":SENS:COUN 2", None),
        (b":SENS:TRIG:MEAS:STIM COMM", None),
        _error_ok(),
        (b"*TRG", None),
        _error_ok(),
        (b':TRAC:ACT? "defbuffer1"', b"2"),
        _error_ok(),
        (b':TRAC:ACT? "defbuffer1"', b"2"),
        _error_ok(),
        (b':TRAC:DATA? 1, 2, "defbuffer1", READ', b"-2,3"),
        _error_ok(),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
        _error_ok(),
    ])
    with expected_protocol(KeithleyDMM7510, pairs) as instrument:
        instrument.arm(2)
        instrument.trigger()
        assert instrument.fetch() == [-2.0, 3.0]


def test_single_after_bus_burst_disarms_stimulus_and_restores_count_one():
    pairs = _capacity()
    pairs.extend([
        (b":ABOR", None),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
        _error_ok(),
        (b':DISP:BUFF:ACT "defbuffer1"', None),
        (b":FORM:DATA ASC", None),
        (b':TRAC:FILL:MODE ONCE, "defbuffer1"', None),
        (b':TRAC:CLE "defbuffer1"', None),
        (b":SENS:COUN 1", None),
        (b":SENS:TRIG:MEAS:STIM COMM", None),
        _error_ok(),
        (b"*TRG", None),
        _error_ok(),
        (b':TRAC:ACT? "defbuffer1"', b"1"),
        _error_ok(),
        (b':TRAC:ACT? "defbuffer1"', b"1"),
        _error_ok(),
        (b':TRAC:DATA? 1, 1, "defbuffer1", READ', b"0.5"),
        _error_ok(),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
        _error_ok(),
    ])
    pairs.extend(_acquire_protocol(1, b"0.75"))
    with expected_protocol(KeithleyDMM7510, pairs) as instrument:
        instrument.arm(1)
        instrument.trigger()
        assert instrument.fetch() == [0.5]
        assert instrument.acquire(1) == [0.75]


def test_simple_loop_delay_validation_precedes_capacity_query():
    with expected_protocol(KeithleyDMM7510, []) as instrument, pytest.raises(ValueError):
        instrument.initiate(2, delay=1e-9)


def test_buffer_timeout_aborts_and_disables_stimulus(monkeypatch):
    ticks = iter([0.0, 1.0])
    monkeypatch.setattr(
        "pymeasure.instruments.keithley.keithleydmm7510.time.monotonic",
        lambda: next(ticks),
    )
    monkeypatch.setattr("pymeasure.instruments.keithley.keithleydmm7510.time.sleep", Mock())
    pairs = _capacity()
    pairs.extend([
        (b":ABOR", None),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
        _error_ok(),
        (b':DISP:BUFF:ACT "defbuffer1"', None),
        (b":FORM:DATA ASC", None),
        (b':TRAC:FILL:MODE ONCE, "defbuffer1"', None),
        (b':TRAC:CLE "defbuffer1"', None),
        (b":SENS:COUN 2", None),
        _error_ok(),
        (b':TRAC:TRIG "defbuffer1"', None),
        _error_ok(),
        (b':TRAC:ACT? "defbuffer1"', b"0"),
        _error_ok(),
        (b":ABOR", None),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
        _error_ok(),
    ])
    with expected_protocol(KeithleyDMM7510, pairs) as instrument, pytest.raises(
        TimeoutError, match="2 DMM7510 readings"
    ):
        instrument.acquire(2, timeout=0.1)
    assert instrument._pending_count is None
    assert instrument._pending_mode is None


def test_abort_clears_local_acquisition_state():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b":ABOR", None),
            (b":SENS:TRIG:MEAS:STIM NONE", None),
            _error_ok(),
        ],
    ) as instrument:
        instrument._pending_count = 5
        instrument._pending_mode = "simple_loop"
        instrument.abort()
        assert instrument._pending_count is None
        assert instrument._pending_mode is None


def test_reset_clears_local_acquisition_state():
    with expected_protocol(KeithleyDMM7510, [(b"*RST", None)]) as instrument:
        instrument._pending_count = 4
        instrument._pending_mode = "bus_armed"
        instrument.reset()
        assert instrument._pending_count is None
        assert instrument._pending_mode is None


def test_scpi_error_is_actionable_and_drained():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b":DISP:LIGHT:STAT ON50", None),
            (b":SYST:ERR:NEXT?", b'-113,"Undefined header"'),
            _error_ok(),
        ],
    ) as instrument, pytest.raises(DMM7510SCPIError, match="-113: Undefined header"):
        instrument.display_brightness = "ON50"


def test_scpi_error_disarms_pending_command_trigger_and_preserves_error():
    with expected_protocol(
        KeithleyDMM7510,
        [
            (b":SYST:ERR:NEXT?", b'-200,"Trigger model error"'),
            _error_ok(),
            (b":ABOR", None),
            (b":SENS:TRIG:MEAS:STIM NONE", None),
            _error_ok(),
        ],
    ) as instrument, pytest.raises(DMM7510SCPIError, match="-200: Trigger model error"):
        instrument._pending_count = 2
        instrument._pending_mode = "bus_armed"
        instrument.check_set_errors()
    assert instrument._pending_count is None
    assert instrument._pending_mode is None


def test_transport_error_is_not_hidden_by_abort_cleanup():
    with expected_protocol(KeithleyDMM7510, []) as instrument:
        instrument.adapter.write = Mock(side_effect=OSError("transport failed"))
        with pytest.raises(OSError, match="transport failed"):
            instrument.abort()


def test_property_query_transport_error_disarms_pending_acquisition():
    pairs = _capacity()
    pairs.extend([
        (b":ABOR", None),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
        _error_ok(),
        (b':DISP:BUFF:ACT "defbuffer1"', None),
        (b":FORM:DATA ASC", None),
        (b':TRAC:FILL:MODE ONCE, "defbuffer1"', None),
        (b':TRAC:CLE "defbuffer1"', None),
        (b":SENS:COUN 2", None),
        (b":SENS:TRIG:MEAS:STIM COMM", None),
        _error_ok(),
        (b":ABOR", None),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
        _error_ok(),
    ])
    with expected_protocol(KeithleyDMM7510, pairs) as instrument:
        instrument.arm(2)

        original_ask = instrument.ask

        def fail_reading_count(command, query_delay=None):
            if command == ':TRAC:ACT? "defbuffer1"':
                raise OSError("transport failed")
            return original_ask(command, query_delay)

        instrument.ask = fail_reading_count
        with pytest.raises(OSError, match="transport failed"):
            _ = instrument.reading_buffer_count
    assert instrument._pending_count is None
    assert instrument._pending_mode is None


def test_nplc_write_transport_error_disarms_and_preserves_error_when_cleanup_fails():
    pairs = _arm_protocol()
    pairs.extend([
        (b":SENS:VOLT:NPLC 1.5", None),
        (b":ABOR", None),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
    ])
    original_error = OSError("NPLC transport failed")
    cleanup_error = OSError("abort cleanup failed")
    with expected_protocol(KeithleyDMM7510, pairs) as instrument:
        instrument.arm(2)
        protocol_write = instrument.adapter.write
        attempted = []

        def fail_writes(command, **kwargs):
            attempted.append(command)
            protocol_write(command, **kwargs)
            if command == ":SENS:VOLT:NPLC 1.5":
                raise original_error
            if command == ":ABOR":
                raise cleanup_error

        instrument.adapter.write = fail_writes
        with pytest.raises(OSError) as error:
            instrument.voltage_nplc = 1.5

        assert error.value is original_error
        assert attempted == [
            ":SENS:VOLT:NPLC 1.5",
            ":ABOR",
            ":SENS:TRIG:MEAS:STIM NONE",
        ]
        assert instrument._pending_count is None
        assert instrument._pending_mode is None


def test_control_property_write_transport_error_disarms_pending_acquisition():
    pairs = _arm_protocol()
    pairs.extend([
        (b":DISP:LIGHT:STAT ON50", None),
        (b":ABOR", None),
        (b":SENS:TRIG:MEAS:STIM NONE", None),
        _error_ok(),
    ])
    original_error = OSError("display transport failed")
    with expected_protocol(KeithleyDMM7510, pairs) as instrument:
        instrument.arm(2)
        protocol_write = instrument.adapter.write
        attempted = []

        def fail_display_write(command, **kwargs):
            attempted.append(command)
            protocol_write(command, **kwargs)
            if command == ":DISP:LIGHT:STAT ON50":
                raise original_error

        instrument.adapter.write = fail_display_write
        with pytest.raises(OSError) as error:
            instrument.display_brightness = "ON50"

        assert error.value is original_error
        assert attempted == [
            ":DISP:LIGHT:STAT ON50",
            ":ABOR",
            ":SENS:TRIG:MEAS:STIM NONE",
            ":SYST:ERR:NEXT?",
        ]
        assert instrument._pending_count is None
        assert instrument._pending_mode is None
