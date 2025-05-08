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
import logging
from pymeasure.instruments.keithley import KeithleyDMM6500

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

FUNCTIONS = [
    "voltage",
    "voltage ac",
    "current",
    "current ac",
    "resistance",
    "resistance 4W",
    "diode",
    "capacitance",
    "temperature",
    "continuity",
    "period",
    "frequency",
    "voltage ratio",
]


FUNCTION_METHODS = {
    "voltage": "measure_voltage",
    "voltage ac": "measure_voltage",
    "current": "measure_current",
    "current ac": "measure_current",
    "resistance": "measure_resistance",
    "resistance 4W": "measure_resistance",
    "diode": "measure_diode",
    "capacitance": "measure_capacitance",
    "temperature": "measure_temperature",
    "period": "measure_period",
    "frequency": "measure_frequency",
}

FUNCTIONS_WITH_RANGE = (
    "current",
    "current ac",
    "voltage",
    "voltage ac",
    "resistance",
    "resistance 4W",
    "capacitance",
)

FUNCTIONS_HAVE_AUTORANGE = (
    "current",
    "current ac",
    "voltage",
    "voltage ac",
    "resistance",
    "resistance 4W",
    "capacitance",
)

FUNCTIONS_HAVE_NPLC = (
    "voltage",
    "current",
    "resistance",
    "resistance 4W",
    "diode",
    "temperature",
    "voltage ratio",
)

FUNCTIONS_HAVE_SAME_APERTURE = FUNCTIONS_HAVE_NPLC

FUNCTIONS_HAVE_AUTOZERO = FUNCTIONS_HAVE_NPLC

SCREEN_DISPLAY_SELS = (
    "HOME",
    "HOME_LARG",
    "READ",
    "HIST",
    "SWIPE_FUNC",
    "SWIPE_GRAP",
    "SWIPE_SEC",
    "SWIPE_SETT",
    "SWIPE_STAT",
    "SWIPE_USER",
    "SWIPE_CHAN",
    "SWIPE_NONS",
    "SWIPE_SCAN",
    "CHANNEL_CONT",
    "CHANNEL_SETT",
    "CHANNEL_SCAN",
    "PROC",
)


@pytest.fixture(scope="module")
def dmm6500(connected_device_address):
    instr = KeithleyDMM6500(connected_device_address)
    instr.adapter.connection.timeout = 10000
    return instr


@pytest.fixture
def resetted_dmm6500(dmm6500):
    dmm6500.clear()
    dmm6500.reset()
    return dmm6500


def test_correct_model_by_idn(resetted_dmm6500):
    assert "6500" in resetted_dmm6500.id.lower()


@pytest.mark.parametrize("function_", FUNCTIONS)
def test_given_function_when_set_then_function_is_set(resetted_dmm6500, function_):
    resetted_dmm6500.mode = function_
    assert len(resetted_dmm6500.check_errors()) == 0
    assert resetted_dmm6500.mode == function_


@pytest.mark.parametrize("key", FUNCTION_METHODS)
def test_given_function_by_measure_xxx(resetted_dmm6500, key):
    measure_xxx = getattr(resetted_dmm6500, FUNCTION_METHODS[key])
    if key[-2:] == "ac":
        measure_xxx(ac=True)
    elif key[-2:] == "4W":
        measure_xxx(wires=4)
    else:
        measure_xxx()

    assert len(resetted_dmm6500.check_errors()) == 0
    assert resetted_dmm6500.mode == key


@pytest.mark.parametrize("key", FUNCTION_METHODS)
def test_given_function_is_set_then_reading_avaliable(resetted_dmm6500, key):
    if key[-2:] == "ac":
        getattr(resetted_dmm6500, FUNCTION_METHODS[key])(ac=True)
    elif key[-2:] == "4W":
        getattr(resetted_dmm6500, FUNCTION_METHODS[key])(wires=4)
    else:
        getattr(resetted_dmm6500, FUNCTION_METHODS[key])()

    value = getattr(resetted_dmm6500, key.split(" ")[0])
    assert len(resetted_dmm6500.check_errors()) == 0
    assert value is not None


@pytest.mark.parametrize("function_", FUNCTIONS_WITH_RANGE)
def test_given_function_is_set_then_range_available(resetted_dmm6500, function_):
    resetted_dmm6500.mode = function_
    assert len(resetted_dmm6500.check_errors()) == 0
    new = function_ + " range"
    new = new.replace(" ", "_")
    range_ = getattr(resetted_dmm6500, new)
    assert range_ is not None


@pytest.mark.parametrize("key", FUNCTION_METHODS)
def test_given_function_set_then_autorange_enabled(resetted_dmm6500, key):
    if key[-2:] == "ac":
        getattr(resetted_dmm6500, FUNCTION_METHODS[key])(ac=True)
    elif key[-2:] == "4W":
        getattr(resetted_dmm6500, FUNCTION_METHODS[key])(wires=4)
    else:
        getattr(resetted_dmm6500, FUNCTION_METHODS[key])()

    # resetted_dmm6500.mode = function_
    assert len(resetted_dmm6500.check_errors()) == 0
    assert resetted_dmm6500.auto_range_status() is False
    resetted_dmm6500.auto_range()
    if key in FUNCTIONS_HAVE_AUTORANGE:
        assert resetted_dmm6500.auto_range_status() is True
    else:
        assert resetted_dmm6500.auto_range_status() is False


@pytest.mark.parametrize("function_", FUNCTIONS_HAVE_AUTORANGE)
def test_given_function_set_then_autorange(resetted_dmm6500, function_):
    resetted_dmm6500.mode = function_
    assert len(resetted_dmm6500.check_errors()) == 0
    assert resetted_dmm6500.autorange_enabled
    resetted_dmm6500.autorange_enabled = False
    assert not resetted_dmm6500.autorange_enabled
    assert len(resetted_dmm6500.check_errors()) == 0


def test_dcv_range_min_def_max(resetted_dmm6500):
    resetted_dmm6500.measure_voltage()
    assert len(resetted_dmm6500.check_errors()) == 0

    resetted_dmm6500.range = "MIN"
    assert len(resetted_dmm6500.check_errors()) == 0
    assert resetted_dmm6500.range == 0.1

    resetted_dmm6500.range = "MAX"
    assert len(resetted_dmm6500.check_errors()) == 0
    assert resetted_dmm6500.range == 1000

    resetted_dmm6500.range = "DEF"
    assert len(resetted_dmm6500.check_errors()) == 0
    assert resetted_dmm6500.range == 1000


@pytest.mark.parametrize("function_", FUNCTIONS_HAVE_NPLC)
@pytest.mark.parametrize("nplc", [0.0005, 2, 15])
def test_nplc(resetted_dmm6500, function_, nplc):
    resetted_dmm6500.mode = function_
    resetted_dmm6500.nplc = nplc
    assert len(resetted_dmm6500.check_errors()) == 0
    assert resetted_dmm6500.nplc == nplc


@pytest.mark.parametrize("function_", FUNCTIONS_HAVE_SAME_APERTURE)
@pytest.mark.parametrize("aperture", ["MIN", "MAX", "DEF", 16.0e-3])
def test_general_aperture(resetted_dmm6500, function_, aperture):
    resetted_dmm6500.mode = function_
    resetted_dmm6500.aperture = aperture
    assert len(resetted_dmm6500.check_errors()) == 0
    expected_value = {"MIN": 8.33e-6, "MAX": 0.25, "DEF": 0.0166667, 16.0e-3: 16.0e-3}
    assert resetted_dmm6500.aperture == expected_value[aperture]


@pytest.mark.parametrize("function_", ("frequency", "period"))
@pytest.mark.parametrize("aperture", ["MIN", "MAX", "DEF", 16.0e-3])
def test_freq_period_aperture(resetted_dmm6500, function_, aperture):
    resetted_dmm6500.mode = function_
    resetted_dmm6500.aperture = aperture
    assert len(resetted_dmm6500.check_errors()) == 0
    expected_value = {"MIN": 2e-3, "MAX": 273e-3, "DEF": 200e-3, 16.0e-3: 16.0e-3}
    assert resetted_dmm6500.aperture == expected_value[aperture]


@pytest.mark.parametrize("function_", ("voltage ac", "current ac"))
@pytest.mark.parametrize("detector_bandwidth", [3, 30, 300])
def test_detector_bandwidth(resetted_dmm6500, function_, detector_bandwidth):
    resetted_dmm6500.mode = function_
    resetted_dmm6500.detector_bandwidth = detector_bandwidth
    assert len(resetted_dmm6500.check_errors()) == 0
    assert resetted_dmm6500.detector_bandwidth == detector_bandwidth


@pytest.mark.parametrize("function_", FUNCTIONS_HAVE_AUTOZERO)
@pytest.mark.parametrize("enable", [True, False])
def test_autozero(resetted_dmm6500, function_, enable):
    resetted_dmm6500.mode = function_
    resetted_dmm6500.autozero_enabled = enable
    assert len(resetted_dmm6500.check_errors()) == 0
    assert resetted_dmm6500.autozero_enabled == enable


def test_single_autozero(resetted_dmm6500):
    resetted_dmm6500.autozero = True
    resetted_dmm6500.trigger_single_autozero()
    assert len(resetted_dmm6500.check_errors()) == 0
    assert not resetted_dmm6500.autozero_enabled


def test_terminals_used(resetted_dmm6500):
    assert resetted_dmm6500.terminals_used in ["FRONT", "REAR"]
    assert len(resetted_dmm6500.check_errors()) == 0


@pytest.mark.parametrize("selection", SCREEN_DISPLAY_SELS)
def test_display_screen(resetted_dmm6500, selection):
    resetted_dmm6500.screen_display = selection
    assert len(resetted_dmm6500.check_errors()) == 0


def test_displayed_text(resetted_dmm6500):
    resetted_dmm6500.displayed_text("Hello World", "Running test...")
    assert len(resetted_dmm6500.check_errors()) == 0
    resetted_dmm6500.displayed_text()
    assert len(resetted_dmm6500.check_errors()) == 0
    resetted_dmm6500.displayed_text("", "")
    assert len(resetted_dmm6500.check_errors()) == 0


def test_beep(resetted_dmm6500):  # Ambulance siren
    for i in range(4):
        resetted_dmm6500.beep(700, 0.5)
        resetted_dmm6500.beep(950, 0.5)
    assert len(resetted_dmm6500.check_errors()) == 0
