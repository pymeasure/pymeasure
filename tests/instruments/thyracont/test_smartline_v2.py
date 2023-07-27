#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
from pymeasure.instruments import Instrument
from pymeasure.test import expected_protocol

# File to test
from pymeasure.instruments.thyracont.smartline_v2 import (SmartlineV2, HotCathode, Pirani,
                                                          calculateChecksum, Piezo)

SmartlineV2.hot_cathode = Instrument.ChannelCreator(cls=HotCathode)
SmartlineV2.pirani = Instrument.ChannelCreator(cls=Pirani)
SmartlineV2.piezo = Instrument.ChannelCreator(cls=Piezo)


@pytest.mark.parametrize(
    "address, pars, message, answer",
    [
        (1, (0, "MR"), "0010MR00@\r", "0011MR11H1.2e3L1e-4w\r"),
        (1, (0, "MV"), "0010MV00D\r", "0011MV079.734e2h\r"),
        (2, (2, "R1", "T0.1F1.5"), "0022R108T0.1F1.5l\r", "0023R100h\r"),
        (2, (2, "DU", "mbar"), "0022DU04mbarc\r", "0023DU00~\r"),
        (1, (2, "AH", 981.5), "0012AH05981.5v\r", "0013AH00m\r"),
    ],
)
def test_query(address, pars, message, answer):
    with expected_protocol(SmartlineV2, [(message.rstrip("\r"), answer)], address=address) as inst:
        inst.query(*pars)


def test_calculateChecksum():
    assert calculateChecksum("0010MV00") == "D"


# Test communication
def test_transmitter_error():
    with expected_protocol(SmartlineV2, [("0010MV00D", "0017MV00ERROR1X\r")]) as inst:
        with pytest.raises(ConnectionError) as exc:
            inst.pressure
        assert exc.value.args[0] == "Sensor defect or stacked out."


def test_wrong_answer_command():
    with expected_protocol(SmartlineV2, [("0010MV00D", "0011MX00ERROR1X\r")]) as inst:
        with pytest.raises(ConnectionError, match="Wrong response to MV: '0011MX00ERROR1X'."):
            inst.pressure


def test_wrong_answer_checksum():
    with expected_protocol(SmartlineV2, [("0010MV00D", "0011MV00ERROR1X\r")]) as inst:
        with pytest.raises(ConnectionError, match="Response checksum is wrong."):
            inst.pressure


# Test properties
def test_range():
    with expected_protocol(SmartlineV2, [("0010MR00@", "0011MR11H1.2e3L1e-4w\r")]) as inst:
        assert inst.range == [1.2e3, 1e-4]


def test_pressure():
    with expected_protocol(SmartlineV2, [("0010MV00D", "0011MV079.734e2h\r")]) as inst:
        assert inst.pressure == 973.4


def test_pressure_over_range():
    with expected_protocol(SmartlineV2, [("0010MV00D", "0011MV02ORh\r")]) as inst:
        assert inst.pressure == float("inf")


def test_pressure_under_range():
    with expected_protocol(SmartlineV2, [("0010MV00D", "0011MV02URn\r")]) as inst:
        assert inst.pressure == 0


def test_display_unit_getter():
    with expected_protocol(SmartlineV2, [("0010DU00z", "0011DU03mbar`\r")]) as inst:
        assert inst.display_unit == "mbar"


def test_display_unit_setter():
    with expected_protocol(SmartlineV2, [("0022DU04mbarc", "0023DU00~\r")]) as inst:
        inst.address = 2
        inst.display_unit = "mbar"


def test_display_unit_setter_wrong():
    with expected_protocol(SmartlineV2, []) as inst:
        with pytest.raises(ValueError):
            inst.display_unit = "abc"


def test_display_orientation_getter():
    with expected_protocol(SmartlineV2, [("0010DO00t", "0011DO010f\r")]) as inst:
        assert inst.display_orientation == "top"


def test_display_orientation_setter():
    with expected_protocol(SmartlineV2, [("0012DO010g", "0013DO00w\r")]) as inst:
        inst.display_orientation = "top"


def test_display_data_getter():
    with expected_protocol(SmartlineV2, [("0010DD00i", "0011DD017b\r")]) as inst:
        assert inst.display_data == "relative"


def test_display_data_Setter():
    with expected_protocol(SmartlineV2, [("0012DD017c", "0013DD00l\r")]) as inst:
        inst.display_data = "relative"


def test_setHigh():
    with expected_protocol(SmartlineV2, [("0012AH041000q", "0013AH00m\r")]) as inst:
        inst.setHigh(1000)


def test_setLow():
    with expected_protocol(SmartlineV2, [("0012AL0250W", "0013AL00q\r")]) as inst:
        inst.setLow(50)


def test_device_type():
    with expected_protocol(SmartlineV2, [("0010TD00y", "0011TD06VSR205R\r")]) as inst:
        assert inst.device_type == "VSR205"


def test_operating_hours():
    with expected_protocol(SmartlineV2,
                           [("0010OH00x", "0011OH0285h\r")],
                           ) as inst:
        assert inst.operating_hours == 21.25


def test_operating_hours_cathod():
    """For a cathode transmitter also cathode hours are returned."""
    with expected_protocol(SmartlineV2,
                           [("0010OH00x", "0011OH0542C36P\r")],
                           ) as inst:
        assert inst.operating_hours == [10.5, 9]


# Test methods
@pytest.mark.parametrize("mode, values, comm_pairs", (
        ("continuous", (), [(b'0012ST011|', "0013ST00K\r")]),
        ("continuous", (1, 2), [(b'0012ST04F1T2K', "0013ST00K\r")]),
        ("direct", (5,), [(b'0012ST02D5E', "0013ST00K\r")]),
))
def test_set_sensor_transition_success(mode, values, comm_pairs):
    with expected_protocol(SmartlineV2,
                           comm_pairs,
                           ) as inst:
        print(comm_pairs)
        inst.setSensorTransition(mode, *values)


@pytest.mark.parametrize("mode, values", (
        ("continuous", (5,)),
        ("continuous", (5, 6, 7)),
        ("direct", ()),
        ("direct", (1, 2)),
))
def test_set_sensor_transition_fail(mode, values):
    with expected_protocol(SmartlineV2,
                           [],
                           ) as inst:
        with pytest.raises(ValueError):
            inst.setSensorTransition(mode, *values)


# Pirani tests
def test_pressure_pirani():
    with expected_protocol(SmartlineV2, [("0010M100_", "0011M1079.734e2C\r")]) as inst:
        assert inst.pirani.pressure == 973.4


def test_pirani_statistics():
    with expected_protocol(SmartlineV2,
                           [("0010PM011p", b'0011PM06W0A382j\r')],
                           ) as inst:
        assert inst.pirani.statistics == (0, 95.5)


# Piezo tests
def test_pressure_piezo():
    with expected_protocol(SmartlineV2, [("0010M200`", "0011M2079.734e2D\r")]) as inst:
        assert inst.piezo.pressure == 973.4


# Hot Cathode tests
def test_pressure_hot_cathode():
    with expected_protocol(SmartlineV2, [("0010M300a", "0011M3079.734e2E\r")]) as inst:
        assert inst.hot_cathode.pressure == 973.4


def test_filament_mode_getter():
    with expected_protocol(SmartlineV2, [("0010FC00j", "0011FC011]\r")]) as inst:
        assert inst.hot_cathode.filament_mode == "Filament1"


def test_filament_mode_setter():
    with expected_protocol(SmartlineV2, [("0012FC012_", "0013FC00m\r")]) as inst:
        inst.hot_cathode.filament_mode = "Filament2"


def test_filament_status():
    with expected_protocol(SmartlineV2, [("0010FS00z", "0011FS011m\r")]) as inst:
        assert inst.hot_cathode.filament_status == "Filament 1 defective"
