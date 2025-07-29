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
from pymeasure.instruments.keithley import Keithley4200
from pymeasure.instruments.keithley.keithley4200 import StatusCode

INITIALIZATION = ("*OPT?", "SMU1,SMUPA2,SMU3,SMU4,VM1,VS2,CVU1")


@pytest.mark.parametrize("ch", [1, 2, 3, 4])
class TestKeithley4200SMU:
    def test_disable(self, ch):
        with expected_protocol(
            Keithley4200,
            [INITIALIZATION,
             (f"US;DV{ch}", "ACK"),
             ],
        ) as inst:
            assert inst.smu[ch].disable() is None

    @pytest.mark.parametrize("range, voltage, compliance", [
         (0, 0, 0.1),
         (1, 1.345E2, 1e-6),
         (5, -25.45E1, 3e-3),
         ])
    def test_voltage_setpoint(self, ch, range, voltage, compliance):
        with expected_protocol(
            Keithley4200,
            [INITIALIZATION,
             (f"US;DV{ch},{range:d},{voltage:g},{compliance:g}", "ACK"),
             ],
        ) as inst:
            inst.smu[ch].voltage_setpoint = (range, voltage, compliance)

    @pytest.mark.parametrize("voltage", [0, 1.345E2, -25.45E1])
    def test_voltage(self, ch, voltage):
        with expected_protocol(
            Keithley4200,
            [INITIALIZATION,
             (f"US;TV{ch}", f"NAV{voltage}"),
             ],
        ) as inst:
            assert voltage == inst.smu[ch].voltage

    @pytest.mark.parametrize("range, current, compliance", [
         (0, 0, 12.1),
         (2, 1.345, 1.3e1),
         (4, -2.5E-6, 23.34),
         ])
    def test_current_setpoint(self, ch, range, current, compliance):
        with expected_protocol(
            Keithley4200,
            [INITIALIZATION,
             (f"US;DI{ch},{range:d},{current:g},{compliance:g}", "ACK"),
             ],
        ) as inst:
            inst.smu[ch].current_setpoint = (range, current, compliance)

    @pytest.mark.parametrize("current", [0, 1.345, -2.5E-6])
    def test_current(self, ch, current):
        with expected_protocol(
            Keithley4200,
            [INITIALIZATION,
             (f"US;TI{ch}", f"CBI{current}"),
             ],
        ) as inst:
            assert current == inst.smu[ch].current


class TestKeithley4200:
    def test_id(self):
        with expected_protocol(
            Keithley4200,
            [INITIALIZATION,
             ("ID", "KI4200A V4.6.0")
             ],
        ) as inst:
            assert inst.id == "KI4200A V4.6.0"

    @pytest.mark.parametrize("status_byte, status_code", [
         (0, StatusCode.NONE),
         (1, StatusCode.DATA_READY),
         (2, StatusCode.SYNTAX_ERROR),
         (4, StatusCode.B2),
         (8, StatusCode.B3),
         (16, StatusCode.BUSY),
         (32, StatusCode.B5),
         (64, StatusCode.SERVICE_REQUEST),
         (128, StatusCode.B7),
         (66, StatusCode.SERVICE_REQUEST | StatusCode.SYNTAX_ERROR),
         (255, 255),
         ])
    def test_status(self, status_byte, status_code):
        with expected_protocol(
            Keithley4200,
            [INITIALIZATION,
             ("SP", status_byte),
             ],
        ) as inst:
            assert inst.status == status_code

    def test_options(self):
        with expected_protocol(
            Keithley4200,
            [INITIALIZATION,
             ("*OPT?", "SMU1,SMUPA2,SMU3,SMU4,VM1,VS1,CVU1"),
             ],
        ) as inst:
            assert inst.options == ["SMU1", "SMUPA2", "SMU3", "SMU4", "VM1", "VS1", "CVU1"]
