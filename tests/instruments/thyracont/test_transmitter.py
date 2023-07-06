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
from pymeasure.instruments.thyracont import transmitter as thyracont
from pymeasure.instruments.thyracont import VSR as Transmitter, HotCathode

Transmitter.hot_cathode = Instrument.ChannelCreator(HotCathode, prefix=None)


class Mock_Transmitter(Instrument):
    source = {
        "combination": 0,
        "pirani": 1,
        "piezo": 2,
        "hotCathode": 3,
        "coldCathode": 4,
        "ambient": 6,
        "relative": 7,
    }
    errors = {
        "NO_DEF": "Invalid command for this device.",
        "_LOGIC": "Access Code is invalid or illogical command.",
        "_RANGE": "Value sent is out of range.",
        "ERROR1": "Sensor defect or stacked out.",
        "SYNTAX": "Wrong syntax or mode in data is invalid for this device.",
        "LENGTH": "Length of data is out of expected range.",
        "_CD_RE": "Calibration Data Read Error.",
        "_EP_RE": "EEPROM Read Error.",
        "_UNSUP": "Unsupported Data, invalid baud rate.",
        "_SEDIS": "Sensor element disabled.",
    }

    def __init__(self):
        self.data = None
        super().__init__(Mock_Connection(), name="Mock_Transmitter")

    def write(self, command):
        Transmitter.write(self, command)

    def write_composition(self, accessCode, command, data=""):
        self.sent = [accessCode, command, data]

    def read(self):
        return self.data

    def query(self, accessCode, command, data=""):
        self.write_composition(accessCode, command, data)
        return self.read()


class Mock_Connection:
    def __init__(self):
        self.answer = None

    def query(self, message):
        self.message = f"{message}\r"
        return self.answer.replace("\r", "")

    def write(self, message):
        self.message = f"{message}\r"
        self.i = 0

    def read_bytes(self, number):
        data = self.answer[self.i: self.i + number]
        self.i += number
        return bytes(data, "ascii")


@pytest.fixture
def transmitter():
    t = Transmitter(Mock_Connection())
    t.data = None
    return t


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
    with expected_protocol(Transmitter, [(message.rstrip("\r"), answer)], address=address) as inst:
        inst.query(*pars)


def test_calculateChecksum(transmitter):
    assert thyracont.calculateChecksum("0010MV00") == "D"


# Test communication
def test_transmitter_error():
    with expected_protocol(Transmitter, [("0010MV00D", "0017MV00ERROR1X\r")]) as inst:
        with pytest.raises(ConnectionError) as exc:
            inst.pressure
        assert exc.value.args[0] == "Sensor defect or stacked out."


def test_wrong_answer_command():
    with expected_protocol(Transmitter, [("0010MV00D", "0011MX00ERROR1X\r")]) as inst:
        with pytest.raises(ConnectionError, match="Wrong response to MV: '0011MX00ERROR1X'."):
            inst.pressure


def test_wrong_answer_checksum():
    with expected_protocol(Transmitter, [("0010MV00D", "0011MV00ERROR1X\r")]) as inst:
        with pytest.raises(ConnectionError, match="Response checksum is wrong."):
            inst.pressure


# Test properties
def test_range():
    with expected_protocol(Transmitter, [("0010MR00@", "0011MR11H1.2e3L1e-4w\r")]) as inst:
        assert inst.range == [1.2e3, 1e-4]


def test_pressure():
    with expected_protocol(Transmitter, [("0010MV00D", "0011MV079.734e2h\r")]) as inst:
        assert inst.pressure == 973.4


def test_pressure_pirani():
    with expected_protocol(Transmitter, [("0010M100_", "0011M1079.734e2C\r")]) as inst:
        assert inst.pirani.pressure == 973.4


def test_pressure_piezo():
    with expected_protocol(Transmitter, [("0010M200`", "0011M2079.734e2D\r")]) as inst:
        assert inst.piezo.pressure == 973.4


def test_pressure_hot_cathode():
    with expected_protocol(Transmitter, [("0010M300a", "0011M3079.734e2E\r")]) as inst:
        assert inst.hot_cathode.pressure == 973.4


def test_pressure_over_range():
    with expected_protocol(Transmitter, [("0010MV00D", "0011MV02ORh\r")]) as inst:
        assert inst.pressure == float("inf")


def test_pressure_under_range():
    with expected_protocol(Transmitter, [("0010MV00D", "0011MV02URn\r")]) as inst:
        assert inst.pressure == 0


def test_display_unit_getter():
    with expected_protocol(Transmitter, [("0010DU00z", "0011DU03mbar`\r")]) as inst:
        assert inst.display_unit == "mbar"


def test_display_unit_setter():
    with expected_protocol(Transmitter, [("0022DU04mbarc", "0023DU00~\r")]) as inst:
        inst.address = 2
        inst.display_unit = "mbar"


def test_display_unit_setter_wrong():
    with expected_protocol(Transmitter, []) as inst:
        with pytest.raises(ValueError):
            inst.display_unit = "abc"


def test_display_orientation_getter():
    with expected_protocol(Transmitter, [("0010DO00t", "0011DO010f\r")]) as inst:
        assert inst.display_orientation == "top"


def test_display_orientation_setter():
    with expected_protocol(Transmitter, [("0012DO010g", "0013DO00w\r")]) as inst:
        inst.display_orientation = "top"


def test_display_data_getter():
    with expected_protocol(Transmitter, [("0010DD00i", "0011DD017b\r")]) as inst:
        assert inst.display_data == "relative"


def test_display_data_Setter():
    with expected_protocol(Transmitter, [("0012DD017c", "0013DD00l\r")]) as inst:
        inst.display_data = "relative"


def test_setHigh():
    with expected_protocol(Transmitter, [("0012AH041000q", "0013AH00m\r")]) as inst:
        inst.setHigh(1000)


def test_setLow():
    with expected_protocol(Transmitter, [("0012AL0250W", "0013AL00q\r")]) as inst:
        inst.setLow(50)


def test_filament_mode_getter():
    with expected_protocol(Transmitter, [("0010FC00j", "0011FC011]\r")]) as inst:
        assert inst.hot_cathode.filament_mode == "Filament1"


def test_filament_mode_setter():
    with expected_protocol(Transmitter, [("0012FC012_", "0013FC00m\r")]) as inst:
        inst.hot_cathode.filament_mode = "Filament2"


def test_filament_status():
    with expected_protocol(Transmitter, [("0010FS00z", "0011FS011m\r")]) as inst:
        assert inst.hot_cathode.filament_status == "Filament 1 defective"


def test_device_type():
    with expected_protocol(Transmitter, [("0010TD00y", "0011TD06VSR205R\r")]) as inst:
        assert inst.device_type == "VSR205"


def test_operating_hours():
    with expected_protocol(Transmitter,
                           [("0010OH00x", "0011OH0285h\r")],
                           ) as inst:
        assert inst.operating_hours == 21.25


def test_operating_hours_cathod():
    """For a cathode transmitter also cathode hours are returned."""
    with expected_protocol(Transmitter,
                           [("0010OH00x", "0011OH0542C36P\r")],
                           ) as inst:
        assert inst.operating_hours == [10.5, 9]
