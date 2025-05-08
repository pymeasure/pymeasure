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
from pymeasure.instruments.texio.texioPSW360L30 import TexioPSW360L30


def test_name():
    texio = TexioPSW360L30(adapter=None)
    assert "TEXIO" in texio.name.upper()


def test_output_enabled():
    with expected_protocol(
            TexioPSW360L30,
            [(b"OUTPut?", b"1"),
             (b"OUTPut 1", None),
             (b"OUTPut?", b"0"),
             (b"OUTPut 0", None),
             ],
    ) as inst:
        assert inst.output_enabled is True
        inst.output_enabled = True
        assert inst.output_enabled is False
        inst.output_enabled = False


def test_current_limit():
    with expected_protocol(
            TexioPSW360L30,
            [(b":SOUR:CURR?", b"+5.120"),
             (b":SOUR:CURR 5", None)
             ],
    ) as inst:
        assert inst.current_limit == 5.12
        inst.current_limit = 5


def test_voltage_setpoint():
    with expected_protocol(
            TexioPSW360L30,
            [(b":SOUR:VOLT?", b"+10.000"),
             (b":SOUR:VOLT 10", None)
             ],
    ) as inst:
        assert inst.voltage_setpoint == 10.
        inst.voltage_setpoint = 10


def test_measure_power():
    with expected_protocol(
            TexioPSW360L30,
            [(b":MEAS:POW?", b"+51.200"),
             ],
    ) as inst:
        assert inst.power == 51.2


def test_measure_voltage():
    with expected_protocol(
            TexioPSW360L30,
            [(b":MEAS:VOLT?", b"+10.000"),
             ],
    ) as inst:
        assert inst.voltage == 10.


def test_measure_current():
    with expected_protocol(
            TexioPSW360L30,
            [(b":MEAS:CURR?", b"+5.120"),
             ],
    ) as inst:
        assert inst.current == 5.12


def test_applied():
    with expected_protocol(
            TexioPSW360L30,
            [(b":APPly?", b"+5.050, +1.100"),
             (b":APPly 5.05,1.1", None)
             ],
    ) as inst:
        assert inst.applied == [5.05, 1.1]
        inst.applied = (5.05, 1.1)


if __name__ == '__main__':
    pytest.main()
