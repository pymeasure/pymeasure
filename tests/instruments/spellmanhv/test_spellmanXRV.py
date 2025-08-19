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

# communication during class initialization
INITIALIZATION = (f"{STX}28,j", f"{STX}28,160,30,0,|")


class TestSpellmanXRV:
    """Tests for the Spellman XRV HV power supplies"""

    @pytest.mark.parametrize("baudrate, mapping, set_csum",
                             [(9600, 1, "P"),
                              (19200, 2, "O"),
                              (38400, 3, "N"),
                              (57600, 4, "M"),
                              (115200, 5, "L")])
    def test_baudrate(self, baudrate, mapping, set_csum):
        set_cmd = f"07,{mapping},{set_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}", f"{STX}07,$,]"),
             ],
        ) as inst:
            inst.baudrate = baudrate

    @pytest.mark.parametrize("voltage_setpoint, mapping, set_csum, got_csum",
                             [(0, 0, "W", "S"),
                              (19.54, 1, "V", "R"),
                              (50e3, 1280, "|", "x"),
                              (160000, 4095, "u", "q")])
    def test_voltage_setpoint(self, voltage_setpoint, mapping, set_csum, got_csum):
        set_cmd = f"10,{mapping},{set_csum}"
        get_got = f"14,{mapping},{got_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}", f"{STX}10,$,c"),
             (f"{STX}14,o", f"{STX}{get_got}"),
             ],
        ) as inst:
            inst.voltage_setpoint = voltage_setpoint
            assert voltage_setpoint == pytest.approx(inst.voltage_setpoint, abs=0.5*160e3/4095)

    @pytest.mark.parametrize("current_setpoint, mapping, set_csum, got_csum",
                             [(0, 0, "V", "R"),
                              (0.0035, 478, "c", "_"),
                              (30e-3, 4095, "t", "p")])
    def test_current_setpoint(self, current_setpoint, mapping, set_csum, got_csum):
        set_cmd = f"11,{mapping},{set_csum}"
        get_got = f"15,{mapping},{got_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}", f"{STX}11,$,b"),
             (f"{STX}15,n", f"{STX}{get_got}"),
             ],
        ) as inst:
            inst.current_setpoint = current_setpoint
            assert current_setpoint == pytest.approx(inst.current_setpoint, abs=0.5*30e-3/4095)

    def test_analog_monitor(self):
        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}19,j", f"{STX}19,1234,2977,3783,512,768,6,7,899,~"),
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

    @pytest.mark.parametrize("hv_on_timer, got_csum",
                             [(0, "G"),
                              (1.6, "@"),
                              (300.67, "W"),
                              (1e3, "v"),
                              (2.565e4, "u")])
    def test_hv_on_timer(self, hv_on_timer, got_csum):
        get_got = f"21,{hv_on_timer:f},{got_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}21,q", f"{STX}{get_got}"),
             ],
        ) as inst:
            assert hv_on_timer == inst.hv_on_timer

    @pytest.mark.parametrize("status, mapping, got_csum", [
        (StatusCode.HV_ENABLED, "1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "S"),
        (StatusCode.INTERLOCK_1_CLOSED, "0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "S"),
        (StatusCode.INTERLOCK_2_CLOSED, "0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "S"),
        (StatusCode.ECR_MODE_ACTIVE, "0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0", "S"),
        (StatusCode.POWER_SUPPLY_FAULT, "0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0", "S"),
        (StatusCode.LOCAL_MODE, "0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0", "S"),
        (StatusCode.FILAMENT_ENABLED, "0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0", "S"),
        (StatusCode.LARGE_FILAMENT, "0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0", "S"),
        (StatusCode.XRAYS_EMINENT, "0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0", "S"),
        (StatusCode.LARGE_FILAMENT_CONFIRMATION, "0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0", "S"),
        (StatusCode.SMALL_FILAMENT_CONFIRMATION, "0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0", "S"),
        (StatusCode.RESERVED1, "0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0", "S"),
        (StatusCode.RESERVED2, "0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0", "S"),
        (StatusCode.RESERVED3, "0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0", "S"),
        (StatusCode.RESERVED4, "0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0", "S"),
        (StatusCode.POWER_SUPPLY_READY, "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0", "S"),
        (StatusCode.INTERNAL_INTERLOCK_CLOSED, "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1", "S"),
        (2**17-1, "1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1", "C"),
        ])
    def test_status(self, status, mapping, got_csum):
        get_got = f"22,{mapping},{got_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}22,p", f"{STX}{get_got}"),
             ],
        ) as inst:
            assert status == inst.status

    def test_dsp(self):
        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}23,o", f"{STX}23,SWM9999-999,56234,`"),
             ],
        ) as inst:
            got = inst.dsp
            assert ["SWM9999-999", 56234] == got

    def test_configuration(self):
        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}27,k", f"{STX}27,1,2,3,4,5,6,7,8,9,10,11,12,X"),
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
        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}28,j", f"{STX}28,160,30,0,|"),
             ],
        ) as inst:
            got = inst.scaling
            assert got["voltage"] == 160000
            assert got["current"] == 30e-3
            assert got["polarity"] == 0

    def test_reset_hv_on_timer(self):
        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}30,q", f"{STX}30,$,a"),
             ],
        ) as inst:
            inst.reset_hv_on_timer()

    def test_reset_errors(self):
        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}31,p", f"{STX}31,$,`"),
             ],
        ) as inst:
            inst.reset_errors()

    @pytest.mark.parametrize("power_limits, set_csum, got_csum",
                             [((110, 20), "X", "["),
                              ((3000, 1568), "u", "x"),
                              ((4500, 3000), "@", "C")])
    def test_power_limits(self, power_limits, set_csum, got_csum):
        set_cmd = f"97,{power_limits[0]},{power_limits[1]},{set_csum}"
        get_got = f"38,{power_limits[0]},{power_limits[1]},3,4,5,6,{got_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}", f"{STX}97,$,T"),
             (f"{STX}38,i", f"{STX}{get_got}"),
             ],
        ) as inst:
            inst.power_limits = power_limits
            assert power_limits == tuple(inst.power_limits)

    def test_fpga(self):
        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}43,m", f"{STX}43,SWM00199-001,3261,Q"),
             ],
        ) as inst:
            got = inst.fpga
            assert ["SWM00199-001", 3261] == got

    @pytest.mark.parametrize("errors, mapping, got_csum", [
        (ErrorCode.NO_ERROR,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "r"),
        (ErrorCode.FILAMENT_SELECT_FAULT,
            "1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.OVER_TEMP_APPROACH,
            "0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.OVER_VOLTAGE,
            "0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.UNDER_VOLTAGE,
            "0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.OVER_CURRENT,
            "0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.UNDER_CURRENT,
            "0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.OVER_TEMP_ANODE,
            "0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.OVER_TEMP_CATHODE,
            "0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.INVERTER_FAULT_ANODE,
            "0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.INVERTER_FAULT_CATHODE,
            "0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.FILAMENT_FEEDBACK_FAULT,
            "0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.ANODE_ARC,
            "0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.CATHODE_ARC,
            "0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.CABLE_CONNECT_ANODE_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.CABLE_CONNECT_CATHODE_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.AC_LINE_MON_ANODE_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.AC_LINE_MON_CATHODE_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.DC_RAIL_MON_ANODE_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.DC_RAIL_MON_FAULT_CATHODE,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0", "q"),
        (ErrorCode.LVPS_NEG_15_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0", "q"),
        (ErrorCode.LVPS_POS_15_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0", "q"),
        (ErrorCode.WATCH_DOG_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0", "q"),
        (ErrorCode.BOARD_OVER_TEMP,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0", "q"),
        (ErrorCode.OVERPOWER_FAULT,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0", "q"),
        (ErrorCode.KV_DIFF,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0", "q"),
        (ErrorCode.MA_DIFF,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0", "q"),
        (ErrorCode.INVERTER_NOT_READY,
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1", "q"),
        (2**27-1,
            "1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1", "W"),
        ])
    def test_errors(self, errors, mapping, got_csum):
        get_got = f"68,{mapping},{got_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}68,f", f"{STX}{get_got}"),
             ],
        ) as inst:
            assert errors == inst.errors

    @pytest.mark.parametrize("output_enabled, mapping, set_csum, got_csum",
                             [(True, 1, "F", "Q"),
                              (False, 0, "G", "R")])
    def test_output_enabled(self, output_enabled, mapping, set_csum, got_csum):
        set_cmd = f"98,{mapping},{set_csum}"
        get_got = f"22,{mapping},0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,{got_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}", f"{STX}98,$,S"),
             (f"{STX}22,p", f"{STX}{get_got}"),
             ],
        ) as inst:
            inst.output_enabled = output_enabled
            assert output_enabled == inst.output_enabled

    def test_voltage(self):
        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}60,n", f"{STX}60,4095,p"),
             ],
        ) as inst:
            assert 1.2*160000 == inst.voltage

    def test_system_voltages(self):
        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}69,e", f"{STX}69,1,2,3,4,5,6,7,8,9,10,o"),
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

    @pytest.mark.parametrize("temperature, got_csum",
                             [(0, "J"),
                              (156, "^"),
                              (4095, "h")])
    def test_temperature(self, temperature, got_csum):
        get_got = f"69,{temperature},0,23,24,{got_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}69,e", f"{STX}{get_got}"),
             ],
        ) as inst:
            assert 0.05911815*temperature == inst.temperature


class TestChannelFilament:
    """Tests for the 'filament' channel functions."""

    @pytest.mark.parametrize("limit, set_csum, got_csum",
                             [(0, "U", "Q"),
                              (367, "e", "a"),
                              (4095, "s", "o")])
    def test_limit(self, limit, set_csum, got_csum):
        set_cmd = f"12,{limit},{set_csum}"
        get_got = f"16,{limit},{got_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}", f"{STX}12,$,a"),
             (f"{STX}16,m", f"{STX}{get_got}"),
             ],
        ) as inst:
            inst.filament.limit = limit
            assert limit == inst.filament.limit

    @pytest.mark.parametrize("preheat, set_csum, got_csum",
                             [(0, "T", "P"),
                              (987, "\\", "X"),
                              (4095, "r", "n")])
    def test_preheat(self, preheat, set_csum, got_csum):
        set_cmd = f"13,{preheat},{set_csum}"
        get_got = f"17,{preheat},{got_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}", f"{STX}13,$,`"),
             (f"{STX}17,l", f"{STX}{get_got}"),
             ],
        ) as inst:
            inst.filament.preheat = preheat
            assert preheat == inst.filament.preheat

    @pytest.mark.parametrize("enabled, mapping, set_csum",
                             [(True, 1, "R"),
                              (False, 0, "S")])
    def test_large_size_enabled(self, enabled, mapping, set_csum):
        set_cmd = f"32,{mapping},{set_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}", f"{STX}32,$,_"),
             ],
        ) as inst:
            inst.filament.large_size_enabled = enabled

    @pytest.mark.parametrize("enabled, mapping, set_csum",
                             [(True, 1, "P"),
                              (False, 0, "Q")])
    def test_enabled(self, enabled, mapping, set_csum):
        set_cmd = f"70,{mapping},{set_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}", f"{STX}70,$,]"),
             ],
        ) as inst:
            inst.filament.enabled = enabled


class TestChannelUnscaled:
    """Tests for the 'unscaled' channel functions."""

    @pytest.mark.parametrize("voltage_setpoint, set_csum, got_csum",
                             [(0, "W", "S"),
                              (367, "g", "c"),
                              (4095, "u", "q")])
    def test_voltage_setpoint(self, voltage_setpoint, set_csum, got_csum):
        set_cmd = f"10,{voltage_setpoint},{set_csum}"
        get_got = f"14,{voltage_setpoint},{got_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}", f"{STX}10,$,c"),
             (f"{STX}14,o", f"{STX}{get_got}"),
             ],
        ) as inst:
            inst.unscaled.voltage_setpoint = voltage_setpoint
            assert voltage_setpoint == inst.unscaled.voltage_setpoint

    @pytest.mark.parametrize("current_setpoint, set_csum, got_csum",
                             [(0, "V", "R"),
                              (183, "j", "f"),
                              (4095, "t", "p")])
    def test_current_setpoint(self, current_setpoint, set_csum, got_csum):
        set_cmd = f"11,{current_setpoint},{set_csum}"
        get_got = f"15,{current_setpoint},{got_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}{set_cmd}", f"{STX}11,$,b"),
             (f"{STX}15,n", f"{STX}{get_got}"),
             ],
        ) as inst:
            inst.unscaled.current_setpoint = current_setpoint
            assert current_setpoint == inst.unscaled.current_setpoint

    def test_analog_monitor(self):
        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}19,j", f"{STX}19,1,2,3,4,5,6,7,8,f"),
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

    @pytest.mark.parametrize("voltage, got_csum",
                             [(0, "R"),
                              (298, "_"),
                              (4095, "p")])
    def test_voltage(self, voltage, got_csum):
        get_got = f"60,{voltage},{got_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}60,n", f"{STX}{get_got}"),
             ],
        ) as inst:
            assert voltage == inst.unscaled.voltage

    @pytest.mark.parametrize("lvps_monitor, got_csum",
                             [(0, "M"),
                              (1768, "g"),
                              (4095, "k")])
    def test_lvps_monitor(self, lvps_monitor, got_csum):
        get_got = f"65,{lvps_monitor},{got_csum}"

        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}65,i", f"{STX}{get_got}"),
             ],
        ) as inst:
            assert lvps_monitor == inst.unscaled.lvps_monitor

    def test_system_voltages(self):
        with expected_protocol(
            SpellmanXRV,
            [INITIALIZATION,
             (f"{STX}69,e", f"{STX}69,1,2,3,4,5,6,7,8,9,10,o"),
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
