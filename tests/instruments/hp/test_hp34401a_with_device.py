#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

import pytest
import time
import logging
from pymeasure.instruments.hp.hp34401A import HP34401A

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

FUNCTIONS = ["DCV", "DCV_RATIO", "ACV", "DCI", "ACI", "R2W",
             "R4W", "FREQ", "PERIOD", "CONTINUITY", "DIODE"]

FUNCTIONS_WITH_RANGE = ["DCV", "ACV", "DCI", "ACI",
                        "R2W", "R4W", "FREQ", "PERIOD"]

TEST_RANGES = {
    "DCV": [0.1, 1, 10], "ACV": [0.1, 1, 10], "DCI": [0.1, 1, 3],
    "ACI": [1, 3], "R2W": [100, 1e3, 10e3], "R4W": [100, 1e3, 10e3],
    "FREQ": [0.1, 1, 10], "PERIOD": [0.1, 1, 10]}


@pytest.fixture(scope="module")
def hp34401a(connected_device_address):
    instr = HP34401A(connected_device_address)
    return instr


@pytest.fixture
def resetted_hp34401a(hp34401a):
    hp34401a.clear()
    hp34401a.write("*RST")
    return hp34401a


def test_correct_model_by_idn(resetted_hp34401a):
    assert "34401a" in resetted_hp34401a.id.lower()


@pytest.mark.parametrize("function_", FUNCTIONS)
def test_given_function_when_set_then_function_is_set(resetted_hp34401a, function_):
    resetted_hp34401a.function_ = function_
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.function_ == function_


@pytest.mark.parametrize("function_", FUNCTIONS)
def test_given_function_is_set_then_reading_avaliable(resetted_hp34401a, function_):
    resetted_hp34401a.function_ = function_
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.reading is not None


@pytest.mark.parametrize("function_", FUNCTIONS_WITH_RANGE)
def test_given_function_is_set_then_range_avaliable(resetted_hp34401a, function_):
    resetted_hp34401a.function_ = function_
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.range_ is not None


@pytest.mark.parametrize("function_", FUNCTIONS_WITH_RANGE)
def test_given_function_set_then_autorange_enabled(resetted_hp34401a, function_):
    resetted_hp34401a.function_ = function_
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.autorange is True


@pytest.mark.parametrize("function_", FUNCTIONS_WITH_RANGE)
def test_given_range_set_then_range_correct(resetted_hp34401a, function_):
    for range in TEST_RANGES[function_]:
        resetted_hp34401a.function_ = function_
        resetted_hp34401a.range_ = range
        assert len(resetted_hp34401a.check_errors()) == 0
        assert resetted_hp34401a.range_ == range


@pytest.mark.parametrize("function_", FUNCTIONS_WITH_RANGE)
def test_autorange_enable(resetted_hp34401a, function_):
    resetted_hp34401a.function_ = function_
    resetted_hp34401a.autorange = True
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.autorange is True


@pytest.mark.parametrize("function_", FUNCTIONS_WITH_RANGE)
def test_autorange_disable(resetted_hp34401a, function_):
    resetted_hp34401a.function_ = function_
    resetted_hp34401a.autorange = False
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.autorange is False


def test_dcv_range_min_max(resetted_hp34401a):
    resetted_hp34401a.function_ = "DCV"
    resetted_hp34401a.range_ = "MIN"
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.range_ == 0.1
    resetted_hp34401a.range_ = "MAX"
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.range_ == 1000


@pytest.mark.parametrize("enabled", [True, False])
def test_display_enabled(resetted_hp34401a, enabled):
    resetted_hp34401a.display_enabled = enabled
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.display_enabled == enabled


@pytest.mark.parametrize("function_", ["DCV", "ACV", "DCI", "R2W"])
def test_resolution(resetted_hp34401a, function_):
    resetted_hp34401a.function_ = function_
    resetted_hp34401a.range_ = 1
    resetted_hp34401a.resolution = 0.0001
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.resolution == 0.0001


@pytest.mark.parametrize("function_", ["DCV", "DCI", "R2W"])
@pytest.mark.parametrize("nplc", [0.02, 1, 100])
def test_nplc(resetted_hp34401a, function_, nplc):
    resetted_hp34401a.function_ = function_
    resetted_hp34401a.nplc = nplc
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.nplc == nplc


@pytest.mark.parametrize("function_", ["FREQ", "PERIOD"])
@pytest.mark.parametrize("gate_time", [0.01, 0.01, 1])
def test_gate_time(resetted_hp34401a, function_, gate_time):
    resetted_hp34401a.function_ = function_
    resetted_hp34401a.gate_time = gate_time
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.gate_time == gate_time


@pytest.mark.parametrize("detector_bandwidth", [3, 20, 200])
def test_detector_bandwidth(resetted_hp34401a, detector_bandwidth):
    resetted_hp34401a.function_ = "FREQ"
    resetted_hp34401a.detector_bandwidth = detector_bandwidth
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.detector_bandwidth == detector_bandwidth


@pytest.mark.parametrize("enable", [True, False])
def test_autozero(resetted_hp34401a, enable):
    resetted_hp34401a.autozero_enabled = enable
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.autozero_enabled == enable


def test_single_autozero(resetted_hp34401a):
    resetted_hp34401a.autozero_enabled = True
    resetted_hp34401a.trigger_single_autozero()
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.autozero_enabled is False


def test_auto_input_impedance(resetted_hp34401a):
    resetted_hp34401a.auto_input_impedance_enabled = True
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.auto_input_impedance_enabled is True
    resetted_hp34401a.auto_input_impedance_enabled = False
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.auto_input_impedance_enabled is False


def test_terminals_used(resetted_hp34401a):
    assert resetted_hp34401a.terminals_used in ["FRONT", "REAR"]
    assert len(resetted_hp34401a.check_errors()) == 0


def test_when_init_trigger_called_then_no_error(resetted_hp34401a):
    resetted_hp34401a.init_trigger()
    assert len(resetted_hp34401a.check_errors()) == 0


@pytest.mark.parametrize("trigger_source", ["IMM", "BUS", "EXT"])
def test_trigger_source(resetted_hp34401a, trigger_source):
    resetted_hp34401a.trigger_source = trigger_source
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.trigger_source == trigger_source


def test_trigger_delay(resetted_hp34401a):
    resetted_hp34401a.trigger_delay = 10.5
    trigger_delay = resetted_hp34401a.trigger_delay
    assert len(resetted_hp34401a.check_errors()) == 0
    assert trigger_delay == 10.5


@pytest.mark.parametrize("enabled", [True, False])
def test_trigger_auto_delay_enabled(resetted_hp34401a, enabled):
    resetted_hp34401a.trigger_auto_delay_enabled = enabled
    trigger_auto_delay_enabled = resetted_hp34401a.trigger_auto_delay_enabled
    assert len(resetted_hp34401a.check_errors()) == 0
    assert trigger_auto_delay_enabled == enabled


def test_sample_count(resetted_hp34401a):
    resetted_hp34401a.sample_count = 10
    assert resetted_hp34401a.sample_count == 10
    assert len(resetted_hp34401a.check_errors()) == 0


def test_trigger_count(resetted_hp34401a):
    resetted_hp34401a.trigger_count = 10
    assert len(resetted_hp34401a.check_errors()) == 0
    assert resetted_hp34401a.trigger_count == 10


def test_read_stored_reading_multiple_readings(resetted_hp34401a):
    resetted_hp34401a: HP34401A = resetted_hp34401a
    resetted_hp34401a.sample_count = 10
    resetted_hp34401a.trigger_source = "IMM"
    resetted_hp34401a.nplc = 0.02
    resetted_hp34401a.init_trigger()
    resetted_hp34401a.complete
    readings = resetted_hp34401a.stored_reading
    print(readings)
    assert len(resetted_hp34401a.check_errors()) == 0
    assert len(readings) == 10


def test_displayed_text(resetted_hp34401a):
    resetted_hp34401a.displayed_text = "Hello World"
    assert resetted_hp34401a.displayed_text == "Hello World"
    assert len(resetted_hp34401a.check_errors()) == 0


def test_beep(resetted_hp34401a):
    resetted_hp34401a.beep()
    assert len(resetted_hp34401a.check_errors()) == 0


@pytest.mark.parametrize("enabled", [True, False])
def test_beeper_enabled(resetted_hp34401a, enabled):
    resetted_hp34401a.beeper_enabled = enabled
    assert resetted_hp34401a.beeper_enabled == enabled
    assert len(resetted_hp34401a.check_errors()) == 0


def test_scpi_version(resetted_hp34401a):
    assert len(str(resetted_hp34401a.scpi_version)) > 0
    assert len(resetted_hp34401a.check_errors()) == 0


def test_stored_readings_count(resetted_hp34401a):
    resetted_hp34401a.nplc = 0.02
    resetted_hp34401a.sample_count = 10
    resetted_hp34401a.trigger_source = "IMM"
    resetted_hp34401a.init_trigger()
    time.sleep(1)
    assert resetted_hp34401a.stored_readings_count == 10
    assert len(resetted_hp34401a.check_errors()) == 0


def test_self_test_result(resetted_hp34401a):
    resetted_hp34401a.adapter.connection.timeout = 60000
    assert resetted_hp34401a.self_test_result in [True, False]
    assert len(resetted_hp34401a.check_errors()) == 0
