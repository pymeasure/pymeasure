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

from time import perf_counter_ns

import pytest

from pymeasure.instruments.temptronic.temptronic_base import (
    ATSBase,
    ErrorCode,
    TemperatureStatusCode,
)
from pymeasure.test import expected_protocol


def test_check_query_delay():
    with expected_protocol(ATSBase, [("TTIM?", "7")]) as inst:
        start = perf_counter_ns()
        assert inst.maximum_test_time == 7
        delay = perf_counter_ns() - start
        # HACK acceptable factor is needed, as in CI under windows (Py38, Py39) the `sleep` interval
        # is slightly shorter than the given argument.
        acceptable_factor = 0.8
        assert delay > 0.05 * 1e9 * acceptable_factor


# ---------------------------------------------------------------------------
# Boolean / string setting properties
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value, command", [(True, "%RM"), (False, "%GL")])
def test_remote_mode(value, command):
    with expected_protocol(ATSBase, [(command, None)]) as inst:
        inst.remote_mode = value


@pytest.mark.parametrize("value, command", [("up", "HEAD 0"), ("down", "HEAD 1")])
def test_head(value, command):
    with expected_protocol(ATSBase, [(command, None), ("HEAD?", command[-1])]) as inst:
        inst.head = value
        assert inst.head == value


@pytest.mark.parametrize("value, command", [(True, "FLOW 1"), (False, "FLOW 0")])
def test_enable_air_flow(value, command):
    with expected_protocol(ATSBase, [(command, None)]) as inst:
        inst.enable_air_flow = value


@pytest.mark.parametrize("value, command", [(True, "%LL"), (False, "%GL")])
def test_local_lockout(value, command):
    with expected_protocol(ATSBase, [(command, None)]) as inst:
        inst.local_lockout = value


@pytest.mark.parametrize("value, command", [(True, "COOL 1"), (False, "COOL 0")])
def test_compressor_enable(value, command):
    with expected_protocol(ATSBase, [(command, None)]) as inst:
        inst.compressor_enable = value


@pytest.mark.parametrize("value, command", [(True, "CYCL 1"), (False, "CYCL 0")])
def test_cycling_enable(value, command):
    with expected_protocol(ATSBase, [(command, None)]) as inst:
        inst.cycling_enable = value


@pytest.mark.parametrize("value, command", [(True, "LRNM 1"), (False, "LRNM 0")])
def test_learn_mode(value, command):
    with expected_protocol(ATSBase, [
        (command, None),
        ("LRNM?", command[-1]),
    ]) as inst:
        inst.learn_mode = value
        assert inst.learn_mode == value


@pytest.mark.parametrize("value, command", [("ON", "DUTM 1"), ("OFF", "DUTM 0")])
def test_dut_mode(value, command):
    with expected_protocol(ATSBase, [
        (command, None),
        ("DUTM?", command[-1]),
    ]) as inst:
        inst.dut_mode = value
        assert inst.dut_mode == value


# ---------------------------------------------------------------------------
# Numeric control properties
# ---------------------------------------------------------------------------


def test_maximum_test_time():
    with expected_protocol(ATSBase, [
        ("TTIM 100", None),
        ("TTIM?", "100"),
    ]) as inst:
        inst.maximum_test_time = 100
        assert inst.maximum_test_time == 100


def test_dut_constant():
    with expected_protocol(ATSBase, [
        ("DUTC 100", None),
        ("DUTC?", "100"),
    ]) as inst:
        inst.dut_constant = 100
        assert inst.dut_constant == 100


def test_temperature_limit_air_low():
    with expected_protocol(ATSBase, [
        ("LLIM -60", None),
        ("LLIM?", "-60"),
    ]) as inst:
        inst.temperature_limit_air_low = -60
        assert inst.temperature_limit_air_low == -60


def test_temperature_limit_air_high():
    with expected_protocol(ATSBase, [
        ("ULIM 220", None),
        ("ULIM?", "220"),
    ]) as inst:
        inst.temperature_limit_air_high = 220
        assert inst.temperature_limit_air_high == 220


def test_temperature_limit_air_dut():
    with expected_protocol(ATSBase, [
        ("ADMD 50", None),
        ("ADMD?", "50"),
    ]) as inst:
        inst.temperature_limit_air_dut = 50
        assert inst.temperature_limit_air_dut == 50


def test_temperature_setpoint():
    with expected_protocol(ATSBase, [
        ("SETP 25", None),
        ("SETP?", "25"),
    ]) as inst:
        inst.temperature_setpoint = 25
        assert inst.temperature_setpoint == 25


def test_temperature_setpoint_window():
    with expected_protocol(ATSBase, [
        ("WNDW 1", None),
        ("WNDW?", "1"),
    ]) as inst:
        inst.temperature_setpoint_window = 1
        assert inst.temperature_setpoint_window == 1


def test_temperature_soak_time():
    with expected_protocol(ATSBase, [
        ("SOAK 30", None),
        ("SOAK?", "30"),
    ]) as inst:
        inst.temperature_soak_time = 30
        assert inst.temperature_soak_time == 30


def test_set_point_number():
    with expected_protocol(ATSBase, [
        ("SETN 2", None),
        ("SETN?", "2"),
    ]) as inst:
        inst.set_point_number = 2
        assert inst.set_point_number == 2


def test_total_cycle_count():
    with expected_protocol(ATSBase, [
        ("CYCC 10", None),
        ("CYCC?", "10"),
    ]) as inst:
        inst.total_cycle_count = 10
        assert inst.total_cycle_count == 10


@pytest.mark.parametrize("value", [0.1, 10, 100, 99.9, 9999])
def test_ramp_rate(value):
    with expected_protocol(ATSBase, [
        (f"RAMP {value:g}", None),
        ("RAMP?", f"{value:g}"),
    ]) as inst:
        inst.ramp_rate = value
        assert inst.ramp_rate == value


def test_load_setup_file():
    with expected_protocol(ATSBase, [("SFIL 3", None)]) as inst:
        inst.load_setup_file = 3


def test_copy_active_setup_file():
    with expected_protocol(ATSBase, [("CFIL 3", None)]) as inst:
        inst.copy_active_setup_file = 3


# ---------------------------------------------------------------------------
# Measurement properties
# ---------------------------------------------------------------------------


def test_temperature():
    with expected_protocol(ATSBase, [("TEMP?", "25.5")]) as inst:
        assert inst.temperature == 25.5


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("0", TemperatureStatusCode.NO_STATUS),
        ("1", TemperatureStatusCode.AT_TEMPERATURE),
        ("2", TemperatureStatusCode.NOT_AT_TEMPERATURE),
        ("4", TemperatureStatusCode.END_OF_TEST),
        ("8", TemperatureStatusCode.END_OF_ONE_CYCLE),
        ("16", TemperatureStatusCode.END_OF_ALL_CYCLES),
        ("32", TemperatureStatusCode.CYCLING_STOPPED),
        # combined flag value: AT_TEMPERATURE | END_OF_TEST == 1 | 4 == 5
        ("5", TemperatureStatusCode.AT_TEMPERATURE | TemperatureStatusCode.END_OF_TEST),
    ],
)
def test_temperature_condition_status_code(raw, expected):
    with expected_protocol(ATSBase, [("TECR?", raw)]) as inst:
        assert inst.temperature_condition_status_code == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("0", ErrorCode.OK),
        ("1", ErrorCode.OVERHEAT),
        ("8", ErrorCode.LOW_FLOW),
        ("16", ErrorCode.LOW_INPUT_AIR_PRESSURE),
        ("32", ErrorCode.AIR_SENSOR_OPEN),
        ("128", ErrorCode.INTERNAL_ERROR),
        ("512", ErrorCode.FLOW_SENSOR_HARDWARE_ERROR),
        ("1024", ErrorCode.NO_LINE_SENSE),
        ("2048", ErrorCode.NVRAM_FAULT),
        ("4096", ErrorCode.BVRAM_FAULT),
        ("16384", ErrorCode.NO_DUT_SENSOR_SELECTED),
        # combined: OVERHEAT | LOW_FLOW == 1 | 8 == 9
        ("9", ErrorCode.OVERHEAT | ErrorCode.LOW_FLOW),
    ],
)
def test_error_code(raw, expected):
    with expected_protocol(ATSBase, [("EROR?", raw)]) as inst:
        assert inst.error_code == expected


def test_auxiliary_condition_code():
    with expected_protocol(ATSBase, [("AUXC?", "1024")]) as inst:
        assert inst.auxiliary_condition_code == 1024


def test_nozzle_air_flow_rate():
    with expected_protocol(ATSBase, [("FLWR?", "12.5")]) as inst:
        assert inst.nozzle_air_flow_rate == 12.5


def test_main_air_flow_rate():
    with expected_protocol(ATSBase, [("FLRL?", "5.5")]) as inst:
        assert inst.main_air_flow_rate == 5.5


def test_dynamic_temperature_setpoint():
    with expected_protocol(ATSBase, [("SETD?", "42.0")]) as inst:
        assert inst.dynamic_temperature_setpoint == 42.0


def test_temperature_event_status():
    with expected_protocol(ATSBase, [("TESR?", "1")]) as inst:
        assert inst.temperature_event_status == 1


def test_air_temperature():
    with expected_protocol(ATSBase, [("TMPA?", "23.1")]) as inst:
        assert inst.air_temperature == 23.1


def test_dut_temperature():
    with expected_protocol(ATSBase, [("TMPD?", "27.7")]) as inst:
        assert inst.dut_temperature == 27.7


@pytest.mark.parametrize(
    "raw, expected", [("5", "manual"), ("6", "program")]
)
def test_mode(raw, expected):
    with expected_protocol(ATSBase, [("WHAT?", raw)]) as inst:
        assert inst.mode == expected


# ---------------------------------------------------------------------------
# dut_type
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value, command",
    [(None, "DSNS 0"), ("T", "DSNS 1"), ("K", "DSNS 2")],
)
def test_dut_type(value, command):
    with expected_protocol(ATSBase, [
        (command, None),
        ("DSNS?", command[-1]),
    ]) as inst:
        inst.dut_type = value
        assert inst.dut_type == value


# ---------------------------------------------------------------------------
# Command methods
# ---------------------------------------------------------------------------


def test_reset():
    with expected_protocol(ATSBase, [("RSTO", None)]) as inst:
        result = inst.reset()
        assert result is inst


def test_enter_cycle():
    with expected_protocol(ATSBase, [("RMPC 1", None)]) as inst:
        result = inst.enter_cycle()
        assert result is inst


def test_enter_ramp():
    with expected_protocol(ATSBase, [("RMPS 0", None)]) as inst:
        result = inst.enter_ramp()
        assert result is inst


def test_clear():
    with expected_protocol(ATSBase, [("CLER", None)]) as inst:
        result = inst.clear()
        assert result is inst


def test_next_setpoint():
    with expected_protocol(ATSBase, [("NEXT", None)]) as inst:
        inst.next_setpoint()


# ---------------------------------------------------------------------------
# Convenience methods
# ---------------------------------------------------------------------------


def test_configure_default():
    with expected_protocol(ATSBase, [
        ("WNDW 1", None),
        ("LLIM -60", None),
        ("ULIM 220", None),
        ("DSNS 1", None),
        ("TTIM 1000", None),
        ("DUTC 100", None),
        ("DUTM 1", None),
        ("ADMD 50", None),
        ("SOAK 30", None),
        # read-backs in the logging section of configure:
        ("WNDW?", "1"),
        ("LLIM?", "-60"),
        ("ULIM?", "220"),
        ("DSNS?", "1"),
        ("TTIM?", "1000"),
        ("ADMD?", "50"),
        ("SOAK?", "30"),
    ]) as inst:
        result = inst.configure()
        assert result is inst


def test_configure_dut_type_none():
    with expected_protocol(ATSBase, [
        ("WNDW 1", None),
        ("LLIM -60", None),
        ("ULIM 220", None),
        ("DSNS 0", None),
        ("TTIM 1000", None),
        # dut_type is None: dut_mode set to OFF, dut_constant not configured
        ("DUTM 0", None),
        ("ADMD 50", None),
        ("SOAK 30", None),
        ("WNDW?", "1"),
        ("LLIM?", "-60"),
        ("ULIM?", "220"),
        ("DSNS?", "0"),
        ("TTIM?", "1000"),
        ("ADMD?", "50"),
        ("SOAK?", "30"),
    ]) as inst:
        result = inst.configure(dut_type=None)
        assert result is inst


@pytest.mark.parametrize(
    "set_temp, set_point",
    [
        (15, 2),   # cold (< 20)
        (25, 1),   # ambient (20 <= t < 30)
        (50, 0),   # hot (>= 30)
    ],
)
def test_set_temperature(set_temp, set_point):
    with expected_protocol(ATSBase, [
        ("WHAT?", "5"),  # mode == manual
        (f"SETN {set_point}", None),
        (f"SETP {set_temp:g}", None),
    ]) as inst:
        result = inst.set_temperature(set_temp)
        assert result is inst


def test_shutdown_no_head():
    with expected_protocol(ATSBase, [
        ("FLOW 0", None),
        ("%GL", None),
    ]) as inst:
        result = inst.shutdown()
        assert result is inst
        assert inst.isShutdown is True


def test_shutdown_with_head():
    with expected_protocol(ATSBase, [
        ("FLOW 0", None),
        ("%GL", None),
        ("HEAD 0", None),
    ]) as inst:
        result = inst.shutdown(head=True)
        assert result is inst
        assert inst.isShutdown is True


def test_start_default():
    with expected_protocol(ATSBase, [
        ("%RM", None),
        ("FLOW 1", None),
    ]) as inst:
        result = inst.start()
        assert result is inst


def test_start_no_air_flow():
    with expected_protocol(ATSBase, [
        ("%RM", None),
        ("FLOW 0", None),
    ]) as inst:
        result = inst.start(enable_air_flow=False)
        assert result is inst


def test_error_status_ok():
    with expected_protocol(ATSBase, [("EROR?", "0")]) as inst:
        assert inst.error_status() == ErrorCode.OK


def test_error_status_with_error():
    with expected_protocol(ATSBase, [("EROR?", "1")]) as inst:
        assert inst.error_status() == ErrorCode.OVERHEAT


# ---------------------------------------------------------------------------
# Status-check helpers (mock temperature_condition_status_code)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method_name, raw, expected",
    [
        ("cycling_stopped", "32", True),
        ("end_of_all_cycles", "16", True),
        ("end_of_one_cycle", "8", True),
        ("end_of_test", "4", True),
        ("not_at_temperature", "2", True),
        ("at_temperature", "1", True),
    ],
)
def test_status_helpers_true(method_name, raw, expected):
    with expected_protocol(ATSBase, [("TECR?", raw)]) as inst:
        assert getattr(inst, method_name)() is expected


@pytest.mark.parametrize(
    "method_name",
    [
        "cycling_stopped",
        "end_of_all_cycles",
        "end_of_one_cycle",
        "end_of_test",
        "not_at_temperature",
        "at_temperature",
    ],
)
def test_status_helpers_false(method_name):
    # NO_STATUS (0): none of the bits set
    with expected_protocol(ATSBase, [("TECR?", "0")]) as inst:
        assert getattr(inst, method_name)() is False


@pytest.mark.parametrize(
    "method_name, other_raw",
    [
        ("cycling_stopped", "1"),     # only AT_TEMPERATURE set
        ("end_of_all_cycles", "1"),
        ("end_of_one_cycle", "1"),
        ("end_of_test", "1"),
        ("not_at_temperature", "1"),
        ("at_temperature", "2"),      # only NOT_AT_TEMPERATURE set
    ],
)
def test_status_helpers_other_bit_set(method_name, other_raw):
    with expected_protocol(ATSBase, [("TECR?", other_raw)]) as inst:
        assert getattr(inst, method_name)() is False


# ---------------------------------------------------------------------------
# IntFlag enum combinations
# ---------------------------------------------------------------------------


def test_temperature_status_code_combined_flags():
    combined = TemperatureStatusCode.AT_TEMPERATURE | TemperatureStatusCode.END_OF_TEST
    assert int(combined) == 5
    assert TemperatureStatusCode.AT_TEMPERATURE in combined
    assert TemperatureStatusCode.END_OF_TEST in combined
    assert TemperatureStatusCode.NOT_AT_TEMPERATURE not in combined


def test_error_code_combined_flags():
    combined = ErrorCode.OVERHEAT | ErrorCode.LOW_FLOW
    assert int(combined) == 9
    assert ErrorCode.OVERHEAT in combined
    assert ErrorCode.LOW_FLOW in combined
    assert ErrorCode.AIR_OPEN_LOOP not in combined


def test_at_temperature_with_combined_status():
    # AT_TEMPERATURE | END_OF_TEST (5) -> at_temperature(), end_of_test() True
    with expected_protocol(ATSBase, [
        ("TECR?", "5"),
        ("TECR?", "5"),
        ("TECR?", "5"),
    ]) as inst:
        assert inst.at_temperature() is True
        assert inst.end_of_test() is True
        assert inst.not_at_temperature() is False
