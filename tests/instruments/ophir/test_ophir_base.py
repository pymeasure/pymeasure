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


from pytest import raises

from pymeasure.test import expected_protocol

from pymeasure.instruments.ophir.ophir_base import OphirBase, Modes, ScreenModes, Capabilities


def test_read_processes_response():
    with expected_protocol(
        OphirBase,
        [(None, "* Afas 23 45e-3")],
    ) as inst:
        assert inst.read() == " Afas 23 45e-3"


def test_read_raises_error():
    with expected_protocol(
        OphirBase,
        [(None, "?COM ERROR")],
    ) as inst:
        with raises(ConnectionError) as exc:
            inst.read()
        assert str(exc.value) == "COM ERROR"


def test_init():
    with expected_protocol(OphirBase, []):
        pass  # verify init communication


# INFORMATION ABOUT DEVICE AND HEAD
def test_id():
    with expected_protocol(
        OphirBase, [("$II", "* USBD 113217 SH2USB")]
    ) as instr:
        assert instr.id == ["USBD", "113217", "SH2USB"]


def test_head1():
    # From manual
    with expected_protocol(
        OphirBase, [("$HI", "* TH 12345 03AP 00000183")]
    ) as instr:
        assert instr.head_information == {
            "sensortype": "TH",
            "serialnumber": "12345",
            "name": "03AP",
            "capabilities": Capabilities.POWER | Capabilities.ENERGY | Capabilities(384),
        }


def test_head2():
    # From manual
    with expected_protocol(
        OphirBase, [("$HI", "* PY 22323 PE10-C 80000003")]
    ) as instr:
        assert instr.head_information == {
            "sensortype": "PY",
            "serialnumber": "22323",
            "name": "PE10-C",
            "capabilities": Capabilities.POWER | Capabilities.ENERGY | Capabilities.FREQUENCY,
        }


# CONFIG
# In general


def test_mode_getter():
    with expected_protocol(OphirBase, [("$MM0", "*2")]) as instr:
        assert instr.mode == Modes.POWER


def test_mode_setter():
    with expected_protocol(OphirBase, [("$MM3", "*")]) as instr:
        instr.mode = Modes.ENERGY


def test_units():
    with expected_protocol(OphirBase, [("$SI", "* W")]) as instr:
        assert instr.units == "W"


# Range
def test_range_getter():
    with expected_protocol(OphirBase, [("$RN", "*4")]) as instr:
        assert instr.range == 4


def test_range_setter():
    with expected_protocol(OphirBase, [("$WN1", "*")]) as instr:
        instr.range = 1


def test_range_values():
    with expected_protocol(OphirBase, [("$WN-1", "*")]) as instr:
        instr.range_map_values = True
        instr.range_values = {
            "AUTO": -1,
            "30.0mW": 0,
            "3.00mW": 1,
            "300uW": 2,
            "30.0uW": 3,
            "3.00uW": 4,
            "300nW": 5,
            "30.0nW": 6,
        }
        instr.range = "AUTO"


def test_getAllRanges():
    with expected_protocol(
        OphirBase,
        [("$AR", "* 3 AUTO 30.0mW 3.00mW 300uW 30.0uW 3.00uW 300nW 30.0nW")],
    ) as instr:
        assert instr.getAllRanges() == {
            "AUTO": -1,
            "30.0mW": 0,
            "3.00mW": 1,
            "300uW": 2,
            "30.0uW": 3,
            "3.00uW": 4,
            "300nW": 5,
            "30.0nW": 6,
        }


# Wavelength


# Special measurement


def test_diffuser_getter():
    with expected_protocol(
        OphirBase, [("$DQ", "*1 OUT IN")]
    ) as instr:
        assert instr.diffuser == "OUT"


def test_diffuser_setter():
    with expected_protocol(
        OphirBase, [("$DQ2", "*2 OUT IN")]
    ) as instr:
        instr.diffuser = "IN"


def test_filter_getter():
    with expected_protocol(
        OphirBase, [("$FQ", "*1 OUT IN")]
    ) as instr:
        assert instr.filter == "OUT"


def test_filter_setter():
    with expected_protocol(
        OphirBase, [("$FQ2", "*2 OUT IN")]
    ) as instr:
        instr.filter = "IN"


def test_mains_getter():
    with expected_protocol(
        OphirBase, [("$MA", "* 1 50Hz 60Hz")]
    ) as instr:
        assert instr.mains == "50Hz"


def test_mains_setter():
    with expected_protocol(
        OphirBase, [("$MA1", "*1 50Hz 60Hz")]
    ) as instr:
        instr.mains = "50Hz"


# Other settings


def test_screen_mode_setter():
    with expected_protocol(OphirBase, [("$FS1", "*")]) as instr:
        instr.screen_mode = ScreenModes.ENERGY


# Measurements


def test_energy():
    with expected_protocol(
        OphirBase, [("$SE", "*1.300E-5")]
    ) as instr:
        assert instr.energy == 1.3e-5


def test_energy_flag():
    with expected_protocol(OphirBase, [("$EF", "*1")]) as instr:
        assert instr.energy_flag is True


def test_frequency():
    with expected_protocol(
        OphirBase, [("$SF", "*1.000E3")]
    ) as instr:
        assert instr.frequency == 1000


def test_power():
    with expected_protocol(
        OphirBase, [("$SP", "*1.300E-5")]
    ) as instr:
        assert instr.power == 1.3e-5


def test_position():
    with expected_protocol(
        OphirBase,
        [("$BT", "* F 00000000 X -1.50 Y -0.9 S 6.50")],
    ) as instr:
        assert instr.position == [-1.5, -0.9, 6.5]
