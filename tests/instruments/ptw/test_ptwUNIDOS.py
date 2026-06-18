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
from pymeasure.instruments.ptw.ptwUNIDOS import ptwUNIDOS

# JSON and methods are tested with the device

RANGES = ["VERY_LOW", "LOW", "MEDIUM", "HIGH"]
LEVELS = ["LOW", "MEDIUM", "HIGH"]


class TestMethods:
    def test_clear(self):
        with expected_protocol(
            ptwUNIDOS,
            [("CHR", "CHR")]
        ) as inst:
            inst.clear()

    def test_hold(self):
        with expected_protocol(
            ptwUNIDOS,
            [("HLD", "HLD")]
        ) as inst:
            inst.hold()

    def test_interval_measurement(self):
        with expected_protocol(
            ptwUNIDOS,
            [("INT", "INT")]
        ) as inst:
            inst.interval_measurement()

    def test_intervall_deprecation_warning(self):
        with pytest.warns(FutureWarning):
            with expected_protocol(
                ptwUNIDOS,
                [("INT", "INT")]
            ) as inst:
                inst.intervall()

    def test_measure(self):
        with expected_protocol(
            ptwUNIDOS,
            [("STA", "STA")]
        ) as inst:
            inst.measure()

    def test_reset(self):
        with expected_protocol(
            ptwUNIDOS,
            [("RES", "RES")]
        ) as inst:
            inst.reset()

    def test_selftest(self):
        with expected_protocol(
            ptwUNIDOS,
            [("AST", "AST")]
        ) as inst:
            inst.selftest()

    def test_zero(self):
        with expected_protocol(
            ptwUNIDOS,
            [("NUL", "NUL")]
        ) as inst:
            inst.zero()


class TestProperties:
    @pytest.mark.parametrize("level", LEVELS)
    def test_autostart_level(self, level):
        with expected_protocol(
            ptwUNIDOS,
            [(f"ASL;{level}", f"ASL;{level}"),
             ("ASL", f"ASL;{level}")],
        ) as inst:
            inst.autostart_level = level
            assert inst.autostart_level == level

    def test_id(self):
        with expected_protocol(
            ptwUNIDOS,
            [("PTW", "PTW;UNIDOS Tango;TM10052;1.2.4;A16")],
        ) as inst:
            assert inst.id == ["UNIDOS Tango", "TM10052", "1.2.4", "A16"]

    @pytest.mark.parametrize("it", [1, 600, 1E6])
    def test_integration_time(self, it):
        it = int(it)
        with expected_protocol(
            ptwUNIDOS,
            [(f"IT;{it}", f"IT;{it}"),
             ("IT", f"IT;{it}")]
        ) as inst:
            inst.integration_time = it
            assert inst.integration_time == it

    @pytest.mark.parametrize("it", [-3, 0, 1E12])
    def test_integration_time_limits(self, it):
        with expected_protocol(ptwUNIDOS, []) as inst:
            with pytest.raises(ValueError):
                inst.integration_time = it

    def test_mac_address(self):
        with expected_protocol(
            ptwUNIDOS,
            [("MAC", "MAC;xx-xx-xx-xx-xx-xx")],
        ) as inst:
            assert inst.mac_address == "xx-xx-xx-xx-xx-xx"

    def test_measurement_result(self):
        with expected_protocol(
            ptwUNIDOS,
            [("MV", "MV;RES;0.0;E-12;p;C;0.0;E-12;p;A;;0.0;ms;200;V;0x0"),
             ("MV", "MV;RES;2.6;E-3;m;Gy;5.6;E-09;n;Gy;min;3000.0;ms;300.0;V;0x0")]
        ) as inst:
            assert inst.measurement_result == {"status": "RES",
                                               "charge": 0,
                                               "dose": 0,
                                               "current": 0,
                                               "doserate": 0,
                                               "timebase": "",
                                               "time": 0,
                                               "voltage": 200,
                                               "error": "0x0"}
            assert inst.measurement_result == {"status": "RES",
                                               "charge": 2.6E-3,
                                               "dose": 2.6E-3,
                                               "current": 5.6E-9,
                                               "doserate": 5.6E-9,
                                               "timebase": "min",
                                               "time": 3000,
                                               "voltage": 300,
                                               "error": "0x0"}

    @pytest.mark.parametrize("measurement_range", RANGES)
    def test_range(self, measurement_range):
        with expected_protocol(
            ptwUNIDOS,
            [(f"RGE;{measurement_range}", f"RGE;{measurement_range}"),
             ("RGE", f"RGE;{measurement_range}")],
        ) as inst:
            inst.range = measurement_range
            assert inst.range == measurement_range

    def test_range_max(self):
        with expected_protocol(
            ptwUNIDOS,
            [("MVM", "MVM;MEDIUM;1.65;E-06;µ;Gy;min")]
        ) as inst:
            assert inst.range_max == {"range": "MEDIUM",
                                      "current": 1.65e-06,
                                      "doserate": 1.65e-06,
                                      "timebase": "min"}

    def test_range_res(self):
        with expected_protocol(
            ptwUNIDOS,
            [("MVR", "MVR;MEDIUM;0.5;E-12;p;Gy;0.003;E-09;n;Gy;min")]
        ) as inst:
            assert inst.range_res == {"range": "MEDIUM",
                                      "charge": 5e-13,
                                      "dose": 5e-13,
                                      "current": 3e-12,
                                      "doserate": 3e-12,
                                      "timebase": "min"}

    def test_selftest_result(self):
        with expected_protocol(
            ptwUNIDOS,
            [("ASS",
              "ASS;Passed;0;89000;Low; 136.6;E-12;p;C;Med; 1.500;E-09;n;C;High; 13.50;E-09;n;C"
              )]
        ) as inst:
            assert inst.selftest_result == {"status": "Passed",
                                            "time_remaining": 0,
                                            "time_total": 89000,
                                            "low": 1.366e-10,
                                            "medium": 1.5e-09,
                                            "high": 1.35e-08}

    def test_serial_number(self):
        with expected_protocol(
            ptwUNIDOS,
            [("SER", "SER;123456")]
        ) as inst:
            assert inst.serial_number == 123456

    def test_status(self):
        with expected_protocol(
            ptwUNIDOS,
            [("S", "S;RES")]
        ) as inst:
            assert inst.status == "RES"

    def test_tfi(self):
        with expected_protocol(
            ptwUNIDOS,
            [("TFI", "TFI;-")]
        ) as inst:
            assert inst.tfi == "-"

    def test_autostart_enabled(self):
        with expected_protocol(
            ptwUNIDOS,
            [("ASE;true", "ASE;true"),
             ("ASE", "ASE;false")]
        ) as inst:
            inst.autostart_enabled = True
            assert inst.autostart_enabled is False

    def test_autoreset_enabled(self):
        with expected_protocol(
            ptwUNIDOS,
            [("ASR;true", "ASR;true"),
             ("ASR", "ASR;false")]
        ) as inst:
            inst.autoreset_enabled = True
            assert inst.autoreset_enabled is False

    def test_electrical_units_enabled(self):
        with expected_protocol(
            ptwUNIDOS,
            [("UEL;true", "UEL;true"),
             ("UEL", "UEL;false")]
        ) as inst:
            inst.electrical_units_enabled = True
            assert inst.electrical_units_enabled is False

    @pytest.mark.parametrize("voltage", [-400, -13, 0, 10, 400])
    def test_voltage(self, voltage):
        with expected_protocol(
            ptwUNIDOS,
            [(f"HV;{voltage}", f"HV;{voltage}"),
             ("HV", f"HV;{voltage}")]
        ) as inst:
            inst.voltage = voltage
            assert inst.voltage == voltage

    @pytest.mark.parametrize("voltage", [-401, 401, 1E3])
    def test_voltage_limits(self, voltage):
        with expected_protocol(ptwUNIDOS, []) as inst:
            with pytest.raises(ValueError):
                inst.voltage = voltage

    def test_write_enabled(self):
        with expected_protocol(
            ptwUNIDOS,
            [("TOK", "TOK;true"),
             ("TOK;0", "TOK;0;true"),
             ("TOK;1", "TOK;1;true"),
             ("TOK;1", "TOK;1;false")]
        ) as inst:
            inst.write_enabled = True
            inst.write_enabled = False
            assert inst.write_enabled is True
            assert inst.write_enabled is False

    def test_zero_status(self):
        with expected_protocol(
            ptwUNIDOS,
            [("NUS", "NUS;Passed;0;82000")]
        ) as inst:
            assert inst.zero_status == {"status": "Passed",
                                        "time_remaining": 0.0,
                                        "time_total": 82000.0}


class TestJSON:
    def test_read_detector(self):
        with expected_protocol(
            ptwUNIDOS,
            [("RDA", 'RDA;[{"key1":1,"key2":2};{"key3":3,"key4":"4"}]')]
        ) as inst:
            assert inst.read_detector() == [{"key1": 1, "key2": 2},
                                            {"key3": 3, "key4": "4"},
                                            ]

    def test_read_detector_with_guid(self):
        with expected_protocol(
            ptwUNIDOS,
            [("RDR;detector_guid", 'RDR;guid;{"key1":"value1";"key2":"value2"}')]
        ) as inst:
            assert inst.read_detector("detector_guid") == {"key1": "value1",
                                                           "key2": "value2",
                                                           }

    def test_lan_config(self):
        with expected_protocol(
            ptwUNIDOS,
            [("REC", 'REC;{"key1":"value1";"key2":"value2"}')]
        ) as inst:
            assert inst.lan_config == {"key1": "value1",
                                       "key2": "value2",
                                       }

    def test_measurement_history(self):
        with expected_protocol(
            ptwUNIDOS,
            [("RHR", 'RHR;[{"key1":"value1"};{"key2":"value2"}]')]
        ) as inst:
            assert inst.measurement_history == [{"key1": "value1"},
                                                {"key2": "value2"},
                                                ]

    def test_measurement_parameters(self):
        with expected_protocol(
            ptwUNIDOS,
            [("RMR", 'RMR;{"key1":"value1";"key2":"value2"}')]
        ) as inst:
            assert inst.measurement_parameters == {"key1": "value1",
                                                   "key2": "value2",
                                                   }

    def test_system_info(self):
        with expected_protocol(
            ptwUNIDOS,
            [("RIR", 'RIR;{"key1":"value1";"key2":"value2"}')]
        ) as inst:
            assert inst.system_info == {"key1": "value1",
                                        "key2": "value2",
                                        }

    def test_system_settings(self):
        with expected_protocol(
            ptwUNIDOS,
            [("RSR", 'RSR;{"key1":"value1";"key2":"value2"}')]
        ) as inst:
            assert inst.system_settings == {"key1": "value1",
                                            "key2": "value2",
                                            }

    def test_wlan_config(self):
        with expected_protocol(
            ptwUNIDOS,
            [("RAC", 'RAC;{"key1":"value1";"key2":"value2"}')]
        ) as inst:
            assert inst.wlan_config == {"key1": "value1",
                                        "key2": "value2",
                                        }
