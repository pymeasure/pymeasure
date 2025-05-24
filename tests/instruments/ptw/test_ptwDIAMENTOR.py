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
from pymeasure.test import expected_protocol
from pymeasure.instruments.ptw.ptwDIAMENTOR import ptwDIAMENTOR


def test_baudrate():
    """Verify the communication of the baudrate getter/setter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [("BR4", "BR4"),
         ("BR", "BR0")],
    ) as inst:
        inst.baudrate = 115200
        assert inst.baudrate == 9600


def test_selftest_passed():
    """Verify the communication of the selftest_passed getter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [("TST", ""),
         ("TST", "E1")],
    ) as inst:
        assert inst.selftest_passed is True
        try:
            assert inst.selftest_passed is False
        except ValueError:
            pass


def test_constancy_check_passed():
    """Verify the communication of the constancy_check_passed getter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [("G", "GP"),
         ("G", "GF")],
    ) as inst:
        assert inst.constancy_check_passed is True
        assert inst.constancy_check_passed is False


def test_is_calibrated():
    """Verify the communication of the is_calibrated getter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [("CRC", "CRC0,0"),
         ("CRC", "CRC0,1")],
    ) as inst:
        assert inst.is_calibrated is True
        assert inst.is_calibrated is False


def test_is_eeprom_ok():
    """Verify the communication of the is_eeprom_ok getter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [("CRC", "CRC0,1"),
         ("CRC", "CRC1,1")],
    ) as inst:
        assert inst.is_eeprom_ok is True
        assert inst.is_eeprom_ok is False


@pytest.mark.parametrize("pressure", [500, 1500])
def test_pressure(pressure):
    """Verify the communication of the pressure getter/setter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [(f"PRE{pressure:04d}", f"PRE{pressure:04d}"),
         ("PRE", f"PRE{pressure:04d}")]
    ) as inst:
        inst.pressure = pressure
        assert inst.pressure == pressure


def test_id():
    """Verify the communication of the ID getter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [('PTW', 'CRS 1.2.4')],
    ) as inst:
        assert inst.id == 'CRS 1.2.4'


def test_measurement():
    """Verify the communication of the measurement getter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [("M", "M9999.99,8888.88,222,33,eeee.ee,ffff.ff,mmm,ss,34567")],
    ) as inst:
        assert inst.measurement == {"dap": 9999.99,
                                    "dap_rate": 8888.88,
                                    "time": 13353
                                    }


def test_serial_number():
    """Verify the communication of the serial number getter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [("SER", "SER345678")]
    ) as inst:
        assert inst.serial_number == 345678


@pytest.mark.parametrize("temperature", [0, 1, 30])
def test_temperature(temperature):
    """Verify the communication of the temperature getter/setter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [(f"TMPA{temperature:02d}", f"TMPA{temperature:02d}"),
         ('TMPA', f"TMPA{temperature:02d}")]
    ) as inst:
        inst.temperature = temperature
        assert inst.temperature == temperature


def test_dap_unit():
    """Verify the communication of the dap_unit getter/setter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [("U", "U1"),
         ("U3", "U3")
         ]
    ) as inst:
        assert inst.dap_unit == "cGycm2"
        inst.dap_unit = "uGym2"


def test_calibration_factor():
    """Verify the communication of the calibration_factor getter/setter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [("KA4.3000E09", "KA4.3000E09"),
         ("KA", "KA1.3356E11")
         ]
    ) as inst:
        inst.calibration_factor = 4.3E9
        assert inst.calibration_factor == 1.3356E11


def test_correction_factor():
    """Verify the communication of the correction_factor getter/setter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [("KFA", "KFA1.010"),
         ("KFA3.870", "KFA3.870")
         ]
    ) as inst:
        assert inst.correction_factor == 1.01
        inst.correction_factor = 3.87
