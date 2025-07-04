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
from pymeasure.instruments.spellmanhv.spellmanXRV import SpellmanXRV, StatusCode, ErrorCode

STX = chr(2)
ETX = chr(3)

# communication during class initialization
INITIALIZATION = (f"{STX}28,j{ETX}", f"{STX}28,160,30,0,|")


def checksum(string_to_check):
    ascii_sum = 0
    for char in string_to_check:
        ascii_sum += ord(char)  # add ascii values together

    csb1 = 0x100 - ascii_sum  # two's complement
    csb2 = 0x7F & csb1  # bitwise AND 0x7F: truncate to the last 7 bits
    csb3 = 0x40 | csb2  # bitwise OR 0x40: set bit 6
    return chr(csb3)


class TestSpellmanXRV:
    """Tests for the Spellman XRV HV power supplies"""

    @pytest.mark.parametrize("baudrate, mapping",
                             [(9600, 1),
                              (19200, 2),
                              (38400, 3),
                              (57600, 4),
                              (115200, 5)])
    def test_baudrate(self, baudrate, mapping):
        set_cmd = f"07,{mapping},"
        set_cmd_csum = checksum(set_cmd)
        set_got = "07,$,"
        set_got_csum = checksum(set_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}{set_cmd_csum}{ETX}", f"{STX}{set_got}{set_got_csum}"),
             ],
        ) as inst:
            inst.baudrate = baudrate

    @pytest.mark.parametrize("voltage_setpoint, mapping",
                             [(0, 0),
                              (19.54, 1),
                              (50e3, 1280),
                              (160000, 4095)])
    def test_voltage_setpoint(self, voltage_setpoint, mapping):
        set_cmd = f"10,{mapping},"
        set_cmd_csum = checksum(set_cmd)
        set_got = "10,$,"
        set_got_csum = checksum(set_got)

        get_cmd = "14,"
        get_cmd_csum = checksum(get_cmd)
        get_got = f"14,{mapping},"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}{set_cmd_csum}{ETX}", f"{STX}{set_got}{set_got_csum}"),
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            inst.voltage_setpoint = voltage_setpoint
            assert voltage_setpoint == pytest.approx(inst.voltage_setpoint, abs=0.5*160e3/4095)

    @pytest.mark.parametrize("current_setpoint, mapping", [(0, 0), (0.0035, 478), (30e-3, 4095)])
    def test_current_setpoint(self, current_setpoint, mapping):
        set_cmd = f"11,{mapping},"
        set_cmd_csum = checksum(set_cmd)
        set_got = "11,$,"
        set_got_csum = checksum(set_got)

        get_cmd = "15,"
        get_cmd_csum = checksum(get_cmd)
        get_got = f"15,{mapping},"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}{set_cmd_csum}{ETX}", f"{STX}{set_got}{set_got_csum}"),
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            inst.current_setpoint = current_setpoint
            assert current_setpoint == pytest.approx(inst.current_setpoint, abs=0.5*30e-3/4095)

    def test_analog_monitor(self):
        get_cmd = "19,"
        get_cmd_csum = checksum(get_cmd)
        get_got = "19,1234,2977,3783,512,768,6,7,899,"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            got = inst.analog_monitor

        assert got["voltage"] == pytest.approx(1.2*160e3*1234/4095)
        assert got["current"] == pytest.approx(1.2*0.03*2977/4095)
        assert got["filament"] == 3783
        assert got["voltage_setpoint"] == 512
        assert got["current_setpoint"] == 768
        assert got["limit"] == 6
        assert got["preheat"] == 7
        assert got["anode_current"] == pytest.approx(1.2*0.03*899/4095)

    @pytest.mark.parametrize("hv_on_timer", [0, 1.6, 300.67, 1e3, 2.565e4])
    def test_hv_on_timer(self, hv_on_timer):
        get_cmd = "21,"
        get_cmd_csum = checksum(get_cmd)
        get_got = f"21,{hv_on_timer:f},"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            assert hv_on_timer == inst.hv_on_timer

    @pytest.mark.parametrize("status, mapping", [
        (StatusCode.HV_ENABLED, "1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (StatusCode.INTERLOCK_1_CLOSED, "0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (StatusCode.INTERLOCK_2_CLOSED, "0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (StatusCode.ECR_MODE_ACTIVE, "0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (StatusCode.POWER_SUPPLY_FAULT, "0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0"),
        (StatusCode.LOCAL_MODE, "0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0"),
        (StatusCode.FILAMENT_ENABLED, "0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0"),
        (StatusCode.LARGE_FILAMENT, "0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0"),
        (StatusCode.XRAYS_EMINENT, "0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0"),
        (StatusCode.LARGE_FILAMENT_CONFIRMATION, "0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0"),
        (StatusCode.SMALL_FILAMENT_CONFIRMATION, "0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0"),
        (StatusCode.RESERVED1, "0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0"),
        (StatusCode.RESERVED2, "0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0"),
        (StatusCode.RESERVED3, "0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0"),
        (StatusCode.RESERVED4, "0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0"),
        (StatusCode.POWER_SUPPLY_READY, "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0"),
        (StatusCode.INTERNAL_INTERLOCK_CLOSED, "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1"),
        (2**17-1, "1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1"),
        ])
    def test_status(self, status, mapping):
        get_cmd = "22,"
        get_cmd_csum = checksum(get_cmd)
        get_got = f"22,{mapping},"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            assert status == inst.status

    def test_dsp(self):
        get_cmd = "23,"
        get_cmd_csum = checksum(get_cmd)
        get_got = "23,SWM9999-999,56234,"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            got = inst.dsp
            assert "SWM9999-999" == got["part_number"]
            assert 56234 == got["version"]

    def test_configuration(self):
        get_cmd = "27,"
        get_cmd_csum = checksum(get_cmd)
        get_got = "27,1,2,3,4,5,6,7,8,9,10,11,12,"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            got = inst.configuration
            assert got["reserved1"] == 1
            assert got["over_voltage_percentage"] == 2
            assert got["voltage_ramp_rate"] == 3
            assert got["current_ramp_rate"] == 4
            assert got["pre_warning_time"] == 5
            assert got["arc_count"] == 6
            assert got["reserved2"] == 7
            assert got["quench_time"] == 8
            assert got["max_kV"] == 10
            assert got["max_mA"] == 11
            assert got["watchdog_timer"] == 12

    def test_scaling(self):
        get_cmd = "28,"
        get_cmd_csum = checksum(get_cmd)
        get_got = "28,160,30,0,"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            got = inst.scaling
            assert got["voltage"] == 160000
            assert got["current"] == 30e-3
            assert got["polarity"] == 0

    def test_reset_hv_on_timer(self):
        get_cmd = "30,"
        get_cmd_csum = checksum(get_cmd)
        get_got = "30,$,"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            inst.reset_hv_on_timer()

    def test_reset_errors(self):
        get_cmd = "31,"
        get_cmd_csum = checksum(get_cmd)
        get_got = "31,$,"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            inst.reset_errors()

    @pytest.mark.parametrize("power_limits", [(110, 20), (3000, 1568), (4500, 3000)])
    def test_power_limits(self, power_limits):
        set_cmd = f"97,{power_limits[0]},{power_limits[1]},"
        set_cmd_csum = checksum(set_cmd)
        set_got = "97,$,"
        set_got_csum = checksum(set_got)

        get_cmd = "38,"
        get_cmd_csum = checksum(get_cmd)
        get_got = f"38,{power_limits[0]},{power_limits[1]},3,4,5,6,"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}{set_cmd_csum}{ETX}", f"{STX}{set_got}{set_got_csum}"),
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            inst.power_limits = power_limits
            assert power_limits == tuple(inst.power_limits)

    def test_fpga(self):
        get_cmd = "43,"
        get_cmd_csum = checksum(get_cmd)
        get_got = "43,SWM00199-001,3261,"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            got = inst.fpga
            assert got["part_number"] == "SWM00199-001"
            assert got["version"] == 3261

    @pytest.mark.parametrize("errors, mapping", [
        (ErrorCode.NO_ERROR,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.FILAMENT_SELECT_FAULT,
            "1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.OVER_TEMP_APPROACH,
            "0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.OVER_VOLTAGE,
            "0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.UNDER_VOLTAGE,
            "0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.OVER_CURRENT,
            "0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.UNDER_CURRENT,
            "0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.OVER_TEMP_ANODE,
            "0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.OVER_TEMP_CATHODE,
            "0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.INVERTER_FAULT_ANODE,
            "0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.INVERTER_FAULT_CATHODE,
            "0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.FILAMENT_FEEDBACK_FAULT,
            "0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.ANODE_ARC,
            "0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.CATHODE_ARC,
            "0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.CABLE_CONNECT_ANODE_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.CABLE_CONNECT_CATHODE_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.AC_LINE_MON_ANODE_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.AC_LINE_MON_CATHODE_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.DC_RAIL_MON_ANODE_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0"),
        (ErrorCode.DC_RAIL_MON_FAULT_CATHODE,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0"),
        (ErrorCode.LVPS_NEG_15_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0"),
        (ErrorCode.LVPS_POS_15_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0"),
        (ErrorCode.WATCH_DOG_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0"),
        (ErrorCode.BOARD_OVER_TEMP,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0"),
        (ErrorCode.OVERPOWER_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0"),
        (ErrorCode.KV_DIFF,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0"),
        (ErrorCode.MA_DIFF,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0"),
        (ErrorCode.INVERTER_NOT_READY,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1"),
        (2**27-1,
            "1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1"),
        ])
    def test_errors(self, errors, mapping):
        get_cmd = "68,"
        get_cmd_csum = checksum(get_cmd)
        get_got = f"68,{mapping},"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            assert errors == inst.errors

    @pytest.mark.parametrize("output_enabled, mapping", [(True, 1), (False, 0)])
    def test_output_enabled(self, output_enabled, mapping):
        set_cmd = f"98,{mapping},"
        set_cmd_csum = checksum(set_cmd)
        set_got = "98,$,"
        set_got_csum = checksum(set_got)

        get_cmd = "22,"
        get_cmd_csum = checksum(get_cmd)
        get_got = f"22,{mapping},0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}{set_cmd_csum}{ETX}", f"{STX}{set_got}{set_got_csum}"),
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            inst.output_enabled = output_enabled
            assert output_enabled == inst.output_enabled

    def test_voltage(self):
        get_cmd = "60,"
        get_cmd_csum = checksum(get_cmd)
        get_got = "60,4095,"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            assert 1.2*160000 == inst.voltage

    def test_system_voltages(self):
        get_cmd = "69,"
        get_cmd_csum = checksum(get_cmd)
        get_got = "69,1,2,3,4,5,6,7,8,9,10,"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            got = inst.system_voltages

        assert got["temperature"] == 1*0.05911815
        assert got["reserved"] == 2
        assert got["anode"] == pytest.approx(3*1.2*160000/4095)
        assert got["cathode"] == pytest.approx(4*1.2*160000/4095)
        assert got["ac_line_cathode"] == 5*0.088610
        assert got["dc_rail_cathode"] == 6*0.11399241
        assert got["ac_line_anode"] == 7*0.088610
        assert got["dc_rail_anode"] == 8*0.11399241
        assert got["lvps_pos"] == 9*0.00427407
        assert got["lvps_neg"] == 10*0.00576703

    @pytest.mark.parametrize("temperature", [0, 156, 4095])
    def test_temperature(self, temperature):
        get_cmd = "69,"
        get_cmd_csum = checksum(get_cmd)
        get_got = f"69,{temperature},0,23,24,"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            assert 0.05911815*temperature == inst.temperature


class TestChannelFilament:
    """Tests for the 'filament' channel functions."""

    @pytest.mark.parametrize("limit", [0, 367, 4095])
    def test_limit(self, limit):
        set_cmd = f"12,{limit},"
        set_cmd_csum = checksum(set_cmd)
        set_got = "12,$,"
        set_got_csum = checksum(set_got)

        get_cmd = "16,"
        get_cmd_csum = checksum(get_cmd)
        get_got = f"16,{limit},"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}{set_cmd_csum}{ETX}", f"{STX}{set_got}{set_got_csum}"),
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            inst.filament.limit = limit
            assert limit == inst.filament.limit

    @pytest.mark.parametrize("preheat", [0, 987, 4095])
    def test_preheat(self, preheat):
        set_cmd = f"13,{preheat},"
        set_cmd_csum = checksum(set_cmd)
        set_got = "13,$,"
        set_got_csum = checksum(set_got)

        get_cmd = "17,"
        get_cmd_csum = checksum(get_cmd)
        get_got = f"17,{preheat},"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}{set_cmd_csum}{ETX}", f"{STX}{set_got}{set_got_csum}"),
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            inst.filament.preheat = preheat
            assert preheat == inst.filament.preheat

    @pytest.mark.parametrize("size, mapping", [("large", 1), ("small", 0)])
    def test_size(self, size, mapping):
        set_cmd = f"32,{mapping},"
        set_cmd_csum = checksum(set_cmd)
        set_got = "32,$,"
        set_got_csum = checksum(set_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}{set_cmd_csum}{ETX}", f"{STX}{set_got}{set_got_csum}"),
             ],
        ) as inst:
            inst.filament.size = size

    @pytest.mark.parametrize("enabled, mapping", [(True, 1), (False, 0)])
    def test_enabled(self, enabled, mapping):
        set_cmd = f"70,{mapping},"
        set_cmd_csum = checksum(set_cmd)
        set_got = "70,$,"
        set_got_csum = checksum(set_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}{set_cmd_csum}{ETX}", f"{STX}{set_got}{set_got_csum}"),
             ],
        ) as inst:
            inst.filament.enabled = enabled


class TestChannelUnscaled:
    """Tests for the 'unscaled' channel functions."""

    @pytest.mark.parametrize("voltage_setpoint", [0, 367, 4095])
    def test_voltage_setpoint(self, voltage_setpoint):
        set_cmd = f"10,{voltage_setpoint},"
        set_cmd_csum = checksum(set_cmd)
        set_got = "10,$,"
        set_got_csum = checksum(set_got)

        get_cmd = "14,"
        get_cmd_csum = checksum(get_cmd)
        get_got = f"14,{voltage_setpoint},"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}{set_cmd_csum}{ETX}", f"{STX}{set_got}{set_got_csum}"),
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            inst.unscaled.voltage_setpoint = voltage_setpoint
            assert voltage_setpoint == inst.unscaled.voltage_setpoint

    @pytest.mark.parametrize("current_setpoint", [0, 183, 4095])
    def test_current_setpoint(self, current_setpoint):
        set_cmd = f"11,{current_setpoint},"
        set_cmd_csum = checksum(set_cmd)
        set_got = "11,$,"
        set_got_csum = checksum(set_got)

        get_cmd = "15,"
        get_cmd_csum = checksum(get_cmd)
        get_got = f"15,{current_setpoint},"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}{set_cmd_csum}{ETX}", f"{STX}{set_got}{set_got_csum}"),
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            inst.unscaled.current_setpoint = current_setpoint
            assert current_setpoint == inst.unscaled.current_setpoint

    def test_analog_monitor(self):
        get_cmd = "19,"
        get_cmd_csum = checksum(get_cmd)
        get_got = "19,1,2,3,4,5,6,7,8,"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            got = inst.unscaled.analog_monitor

        assert got["voltage"] == 1
        assert got["current"] == 2
        assert got["filament"] == 3
        assert got["voltage_setpoint"] == 4
        assert got["current_setpoint"] == 5
        assert got["limit"] == 6
        assert got["preheat"] == 7
        assert got["anode_current"] == 8

    @pytest.mark.parametrize("voltage", [0, 298, 4095])
    def test_voltage(self, voltage):
        get_cmd = "60,"
        get_cmd_csum = checksum(get_cmd)
        get_got = f"60,{voltage},"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            assert voltage == inst.unscaled.voltage

    @pytest.mark.parametrize("lvps_monitor", [0, 1768, 4095])
    def test_lvps_monitor(self, lvps_monitor):
        get_cmd = "65,"
        get_cmd_csum = checksum(get_cmd)
        get_got = f"65,{lvps_monitor},"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            assert lvps_monitor == inst.unscaled.lvps_monitor

    def test_system_voltages(self):
        get_cmd = "69,"
        get_cmd_csum = checksum(get_cmd)
        get_got = "69,1,2,3,4,5,6,7,8,9,10,"
        get_got_csum = checksum(get_got)

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{get_cmd}{get_cmd_csum}{ETX}", f"{STX}{get_got}{get_got_csum}"),
             ],
        ) as inst:
            got = inst.unscaled.system_voltages

        assert got["temperature"] == 1
        assert got["reserved"] == 2
        assert got["anode"] == 3
        assert got["cathode"] == 4
        assert got["ac_line_cathode"] == 5
        assert got["dc_rail_cathode"] == 6
        assert got["ac_line_anode"] == 7
        assert got["dc_rail_anode"] == 8
        assert got["lvps_pos"] == 9
        assert got["lvps_neg"] == 10
