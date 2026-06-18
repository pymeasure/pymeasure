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

import pytest
from pymeasure.test import expected_protocol
from pymeasure.instruments.ptw.ptwDIAMENTOR import ptwDIAMENTOR


def test_baudrate():
    with expected_protocol(
        ptwDIAMENTOR,
        [("BR4", "BR4"),
         ("BR", "BR0")],
    ) as inst:
        inst.baudrate = 115200
        assert inst.baudrate == 9600


def test_execute_selftest():
    with expected_protocol(
        ptwDIAMENTOR,
        [("TST", ""),
         ("TST", "E1")],
    ) as inst:
        inst.execute_selftest()
        try:
            inst.execute_selftest()
        except ValueError:
            pass


def test_constancy_check_passed():
    with expected_protocol(
        ptwDIAMENTOR,
        [("G", "GP"),
         ("G", "GF")],
    ) as inst:
        assert inst.constancy_check_passed is True
        assert inst.constancy_check_passed is False


def test_is_calibrated():
    with expected_protocol(
        ptwDIAMENTOR,
        [("CRC", "CRC0,0"),
         ("CRC", "CRC0,1")],
    ) as inst:
        assert inst.is_calibrated is True
        assert inst.is_calibrated is False


def test_is_eeprom_ok():
    with expected_protocol(
        ptwDIAMENTOR,
        [("CRC", "CRC0,1"),
         ("CRC", "CRC1,1")],
    ) as inst:
        assert inst.is_eeprom_ok is True
        assert inst.is_eeprom_ok is False


@pytest.mark.parametrize("pressure", [500, 1500])
def test_pressure(pressure):
    with expected_protocol(
        ptwDIAMENTOR,
        [(f"PRE{pressure:04d}", f"PRE{pressure:04d}"),
         ("PRE", f"PRE{pressure:04d}")]
    ) as inst:
        inst.pressure = pressure
        assert inst.pressure == pressure


def test_id():
    with expected_protocol(
        ptwDIAMENTOR,
        [('PTW', 'CRS 1.2.4')],
    ) as inst:
        assert inst.id == 'CRS 1.2.4'


def test_measurement():
    with expected_protocol(
        ptwDIAMENTOR,
        [("M", "M9999.99,8888.88,222,33,eeee.ee,ffff.ff,mmm,ss,34567")],
    ) as inst:
        assert inst.measurement == {"dap": 9999.99,
                                    "dap_rate": 8888.88,
                                    "time": 13353
                                    }


def test_serial_number():
    with expected_protocol(
        ptwDIAMENTOR,
        [("SER", "SER345678")]
    ) as inst:
        assert inst.serial_number == 345678


@pytest.mark.parametrize("temperature", [0, 1, 30])
def test_temperature(temperature):
    with expected_protocol(
        ptwDIAMENTOR,
        [(f"TMPA{temperature:02d}", f"TMPA{temperature:02d}"),
         ('TMPA', f"TMPA{temperature:02d}")]
    ) as inst:
        inst.temperature = temperature
        assert inst.temperature == temperature


def test_dap_unit():
    with expected_protocol(
        ptwDIAMENTOR,
        [("U", "U1"),
         ("U3", "U3")
         ]
    ) as inst:
        assert inst.dap_unit == "cGycm2"
        inst.dap_unit = "uGym2"


def test_calibration_factor():
    with expected_protocol(
        ptwDIAMENTOR,
        [("KA4.3000E09", "KA4.3000E09"),
         ("KA", "KA1.3356E11")
         ]
    ) as inst:
        inst.calibration_factor = 4.3E9
        assert inst.calibration_factor == 1.3356E11


def test_correction_factor():
    with expected_protocol(
        ptwDIAMENTOR,
        [("KFA", "KFA1.010"),
         ("KFA3.870", "KFA3.870")
         ]
    ) as inst:
        assert inst.correction_factor == 1.01
        inst.correction_factor = 3.87
