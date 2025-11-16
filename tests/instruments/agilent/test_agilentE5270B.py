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
from pymeasure.instruments.agilent.agilentE5270B import AgilentE5270B

INITIALIZATION = ("UNT?", "E5281B,0;E5281B,0;E5281B,0;E5281B,0;0,0;E5280B,0;0,0;E5280B,0")


class TestMain:
    def test_clear(self):
        with pytest.raises(NotImplementedError):
            with expected_protocol(
                AgilentE5270B,
                [INITIALIZATION]
            ) as inst:
                inst.clear()

    def test_get_error_message(self):
        with expected_protocol(
            AgilentE5270B,
            [INITIALIZATION,
             ("EMG? 100", "Undefined GPIB command"),
             ]
        ) as inst:
            got = inst.get_error_message(100)
            assert "Undefined GPIB command" == got

    def test_check_errors(self):
        with expected_protocol(
            AgilentE5270B,
            [INITIALIZATION,
             ("ERR?", "120,0,200,0"),
             ("EMG? 120", "Fake error message for 120"),
             ("EMG? 200", "Fake error message for 200"),
             ]
        ) as inst:
            assert [120, 200] == inst.check_errors()

    def test_options(self):
        with expected_protocol(
            AgilentE5270B,
            [INITIALIZATION,
             ("UNT?", "E5281B,0;0,0;E5280B,0"),
             ]
        ) as inst:
            options = inst.options
            assert ["E5281B,0", "0,0", "E5280B,0"] == options

    def test_smu_naming(self):
        with pytest.raises(AttributeError):
            with expected_protocol(
                AgilentE5270B,
                [INITIALIZATION,
                 ("CN5", None),
                 ("ERR?", "0,0,0,0"),
                 ("CN7", None),
                 ("ERR?", "0,0,0,0"),
                 ]
            ) as inst:
                inst.smu5.enabled = True
                inst.smu7.enabled = True


class TestSMU:
    @pytest.mark.parametrize("slot", [1, 2, 3, 4, 6, 8])
    def test_enabled(self, slot):
        with expected_protocol(
            AgilentE5270B,
            [INITIALIZATION,
             (f"CN{slot}", None),
             ("ERR?", "0,0,0,0"),
             (f"CL{slot}", None),
             ("ERR?", "0,0,0,0"),
             ]
        ) as inst:
            inst.channels[slot].enabled = True
            inst.channels[slot].enabled = False

    def test_current_setpoint(self):
        with expected_protocol(
            AgilentE5270B,
            [INITIALIZATION,
             ("DI1,0,0.001,5", None),
             ("ERR?", "0,0,0,0"),
             ]
        ) as inst:
            inst.smu1.current_setpoint = (0, 1e-3, 5)

    def test_current(self):
        with expected_protocol(
            AgilentE5270B,
            [INITIALIZATION,
             ("TI1", "NAI+1.234e-6"),
             ]
        ) as inst:
            assert 1.234e-6 == inst.smu1.current

    def test_voltage_setpoint(self):
        with expected_protocol(
            AgilentE5270B,
            [INITIALIZATION,
             ("DV1,200,11.33,0.03", None),
             ("ERR?", "0,0,0,0"),
             ]
        ) as inst:
            inst.smu1.voltage_setpoint = (200, 11.33, 0.03)

    def test_voltage(self):
        with expected_protocol(
            AgilentE5270B,
            [INITIALIZATION,
             ("TV1", "NAV-1.234e-6"),
             ]
        ) as inst:
            assert -1.234e-6 == inst.smu1.voltage


class TestDisplay:
    @pytest.mark.parametrize("enabled, mapping", [(True, 1), (False, 0)])
    def test_enabled(self, enabled, mapping):
        with expected_protocol(
            AgilentE5270B,
            [INITIALIZATION,
             (f"RED {mapping}", None),
             ]
        ) as inst:
            inst.display.enabled = enabled

    @pytest.mark.parametrize("engineering_format_enabled, mapping", [(True, 0), (False, 1)])
    def test_engineering_format_enabled(self, engineering_format_enabled, mapping):
        with expected_protocol(
            AgilentE5270B,
            [INITIALIZATION,
             (f"DFM {mapping}", None),
             ]
        ) as inst:
            inst.display.engineering_format_enabled = engineering_format_enabled

    def test_measurement_channel(self):
        with expected_protocol(
            AgilentE5270B,
            [INITIALIZATION,
             ("MCH 1", None),
             ]
        ) as inst:
            inst.display.measurement_smu = 1

    def test_measurement_smu_validator(self):
        with pytest.raises(ValueError):
            with expected_protocol(
                AgilentE5270B,
                [INITIALIZATION,
                 ("MCH 9", None),
                 ]
            ) as inst:
                inst.display.measurement_smu = 9

    @pytest.mark.parametrize("measurement_parameter, mapping",
                             [("result", 1),
                              ("result_and_source", 2),
                              ("resistance", 3),
                              ("power", 4),
                              ]
                             )
    def test_measurement_parameter(self, measurement_parameter, mapping):
        with expected_protocol(
            AgilentE5270B,
            [INITIALIZATION,
             (f"MPA {mapping}", None),
             ]
        ) as inst:
            inst.display.measurement_parameter = measurement_parameter

    def test_source_smu(self):
        with expected_protocol(
            AgilentE5270B,
            [INITIALIZATION,
             ("SCH 1", None),
             ]
        ) as inst:
            inst.display.source_smu = 1

    def test_source_smu_validator(self):
        with pytest.raises(ValueError):
            with expected_protocol(
                AgilentE5270B,
                [INITIALIZATION,
                 ("SCH 9", None),
                 ]
            ) as inst:
                inst.display.source_smu = 9

    @pytest.mark.parametrize("source_parameter, mapping",
                             [("set_point", 1),
                              ("compliance", 2),
                              ("voltage_range", 3),
                              ("current_range", 4),
                              ("error", 5),
                              ]
                             )
    def test_source_parameter(self, source_parameter, mapping):
        with expected_protocol(
            AgilentE5270B,
            [INITIALIZATION,
             (f"SPA 1,{mapping}", None),
             (f"SPA 2,{mapping}", None),
             ]
        ) as inst:
            inst.display.source_parameter1 = source_parameter
            inst.display.source_parameter2 = source_parameter
