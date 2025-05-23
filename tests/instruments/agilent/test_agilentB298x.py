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
from pymeasure.instruments.agilent.agilentB298x import AgilentB2987


TRIGGER_LAYERS = {'ALL': 'all',
                  'ACQ': 'acquisition',
                  'TRAN': 'transient',
                  }

SUB_SYSTEMS = {'ARM': 'arm',
               'TRIG': 'trigger',
               }


class TestBattery:
    """Tests of the battery functions"""

    def test_battery_level(self):
        """Verify the communication of the battery_level getter."""
        with expected_protocol(
            AgilentB2987,
            [(":SYST:BATT?", "38")]
        ) as inst:
            assert inst.battery_level == 38

    def test_battery_cycles(self):
        """Verify the communication of the battery_cycles getter."""
        with expected_protocol(
            AgilentB2987,
            [(":SYST:BATT:CYCL?", "42")]
        ) as inst:
            assert inst.battery_cycles == 42

    @pytest.mark.parametrize("state", [True, False])
    def test_battery_selftest_passed(self, state):
        """Verify the communication of the battery_selftest_passed getter."""
        mapping = {True: 0, False: 1}
        with expected_protocol(
            AgilentB2987,
            [(":SYST:BATT:TEST?", mapping[state])]
        ) as inst:
            assert state == inst.battery_selftest_passed


class TestAmmeter:
    """Tests of the ammeter functions"""

    @pytest.mark.parametrize("state", [True, False])
    def test_input_enabled(self, state):
        """Verify the communication of the input_enabled getter/setter."""
        mapping = {True: 1, False: 0}
        with expected_protocol(
            AgilentB2987,
            [(f":INP {mapping[state]}", None),
             (":INP?", mapping[state])]
        ) as inst:
            inst.input_enabled = state
            assert state == inst.input_enabled

    @pytest.mark.parametrize("state", [True, False])
    def test_zero_corrected(self, state):
        """Verify the communication of the zero correct function getter/setter."""
        mapping = {True: 1, False: 0}
        with expected_protocol(
            AgilentB2987,
            [(f":INP:ZCOR {mapping[state]}", None),
             (":INP:ZCOR?", mapping[state])]
        ) as inst:
            inst.zero_corrected = state
            assert state == inst.zero_corrected

    def test_measure(self):
        """Verify the communication of the measure getter."""
        with expected_protocol(
            AgilentB2987,
            [(":MEAS?", "1.24E-13"),
             (":MEAS?", "1E-3,4895")]
        ) as inst:
            assert inst.measure == 1.24E-13
            assert inst.measure == [1E-3, 4895]

    def test_current(self):
        """Verify the communication of the current getter."""
        with expected_protocol(
            AgilentB2987,
            [(":MEAS:CURR?", "2.24E-14")]
        ) as inst:
            assert inst.current == 2.24E-14

    @pytest.mark.parametrize("range", ['MIN', 20E-6])
    def test_current_range(self, range):
        """Verify the communication of the current_range getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":CURR:RANG {range}", None),
             (":CURR:RANG?", range)]
        ) as inst:
            inst.current_range = range
            assert range == inst.current_range

    def test_interlock_enabled(self):
        """Verify the communication of the interlock_enabled getter."""
        with expected_protocol(
            AgilentB2987,
            [(":SYST:INT:TRIP?", "0"),
             (":SYST:INT:TRIP?", "1")]
        ) as inst:
            assert inst.interlock_enabled is True
            assert inst.interlock_enabled is False

    def test_data_buffer_size(self):
        """Verify the communication of the data_buffer_size getter."""
        with expected_protocol(
            AgilentB2987,
            [(":SYST:DATA:QUAN?", "14")]
        ) as inst:
            assert inst.data_buffer_size == 14


class TestTrigger:
    """Tests of the trigger methods"""

    def test_abort(self):
        """Verify the communication of the abort method."""
        with expected_protocol(
            AgilentB2987,
            [(":ABOR:ALL", None)]
        ) as inst:
            inst.abort()

    def test_abort_aquisition(self):
        """Verify the communication of the abort_acqisition method."""
        with expected_protocol(
            AgilentB2987,
            [(":ABOR:ACQ", None)]
        ) as inst:
            inst.abort_acquisition()

    def test_abort_transient(self):
        """Verify the communication of the abort_transient method."""
        with expected_protocol(
            AgilentB2987,
            [(":ABOR:TRAN", None)]
        ) as inst:
            inst.abort_transient()

    def test_arm(self):
        """Verify the communication of the arm method."""
        with expected_protocol(
            AgilentB2987,
            [(":ARM:ALL", None)]
        ) as inst:
            inst.arm()

    def test_arm_acquisition(self):
        """Verify the communication of the arm_acquisition method."""
        with expected_protocol(
            AgilentB2987,
            [(":ARM:ACQ", None)]
        ) as inst:
            inst.arm_acquisition()

    def test_arm_transient(self):
        """Verify the communication of the arm_transient method."""
        with expected_protocol(
            AgilentB2987,
            [(":ARM:TRAN", None)]
        ) as inst:
            inst.arm_transient()

    def test_init(self):
        """Verify the communication of the trigger init method."""
        with expected_protocol(
            AgilentB2987,
            [(":INIT:ALL", None)]
        ) as inst:
            inst.init()

    def test_init_acquisition(self):
        """Verify the communication of the trigger init_acquisition method."""
        with expected_protocol(
            AgilentB2987,
            [(":INIT:ACQ", None)]
        ) as inst:
            inst.init_acquisition()

    def test_init_transient(self):
        """Verify the communication of the trigger init_transient method."""
        with expected_protocol(
            AgilentB2987,
            [(":INIT:TRAN", None)]
        ) as inst:
            inst.init_transient()

    @pytest.mark.parametrize("layer", ["ALL", "ACQ", "TRAN"])
    @pytest.mark.parametrize("state", [True, False])
    def test_trigger_is_idle(self, layer, state):
        """Verify the communication of the trigger idle getter/setter."""
        mapping = {True: 1, False: 0}
        with expected_protocol(
            AgilentB2987,
            [(f":IDLE:{layer}?", mapping[state])]
        ) as inst:
            assert state == getattr(inst, f"trigger_{TRIGGER_LAYERS[layer]}_is_idle")


@pytest.mark.parametrize("layer", ['ACQ', 'TRAN'])
@pytest.mark.parametrize("sub_system", ['ARM', 'TRIG'])
class TestTriggerProperties:
    """Tests of the trigger properties"""

    @pytest.mark.parametrize("state", [True, False])
    def test_bypass_once_enabled(self, sub_system, layer, state):
        """Verify the communication of the arm/trigger_bypass_once_enabled getter/setter."""
        mapping = {True: 'ONCE', False: 'OFF'}
        with expected_protocol(
            AgilentB2987,
            [(f":{sub_system}:{layer}:BYP {mapping[state]}", None),
             (f":{sub_system}:{layer}:BYP?", mapping[state])]
        ) as inst:
            setattr(inst,
                    f"{SUB_SYSTEMS[sub_system]}_{TRIGGER_LAYERS[layer]}_bypass_once_enabled",
                    state)
            assert state == getattr(inst,
                   f"{SUB_SYSTEMS[sub_system]}_{TRIGGER_LAYERS[layer]}_bypass_once_enabled")

    @pytest.mark.parametrize("count", [1, 10, 1e3])
    def test_count(self, sub_system, layer, count):
        """Verify the communication of the arm/trigger_count getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":{sub_system}:{layer}:COUN {count}", None),
             (f":{sub_system}:{layer}:COUN?", count)]
        ) as inst:
            setattr(inst, f"{SUB_SYSTEMS[sub_system]}_{TRIGGER_LAYERS[layer]}_count", count)
            assert count == getattr(inst,
                   f"{SUB_SYSTEMS[sub_system]}_{TRIGGER_LAYERS[layer]}_count")

    @pytest.mark.parametrize("delay", [0, 10, 1e3, 'MAX'])
    def test_delay(self, sub_system, layer, delay):
        """Verify the communication of the arm/trigger_delay getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":{sub_system}:{layer}:DEL {delay}", None),
             (f":{sub_system}:{layer}:DEL?", delay)]
        ) as inst:
            setattr(inst, f"{SUB_SYSTEMS[sub_system]}_{TRIGGER_LAYERS[layer]}_delay", delay)
            assert delay == getattr(inst,
                   f"{SUB_SYSTEMS[sub_system]}_{TRIGGER_LAYERS[layer]}_delay")

    @pytest.mark.parametrize("source", ['AINT', 'BUS', 'EXT2'])
    def test_source(self, sub_system, layer, source):
        """Verify the communication of the arm/trigger_source getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":{sub_system}:{layer}:SOUR {source}", None),
             (f":{sub_system}:{layer}:SOUR?", source)]
        ) as inst:
            setattr(inst, f"{SUB_SYSTEMS[sub_system]}_{TRIGGER_LAYERS[layer]}_source", source)
            assert source == getattr(inst,
                   f"{SUB_SYSTEMS[sub_system]}_{TRIGGER_LAYERS[layer]}_source")

    @pytest.mark.parametrize("lan_id", ['LAN0', 'LAN7'])
    def test_source_lan_id(self, sub_system, layer, lan_id):
        """Verify the communication of the arm/trigger_source_lan_id getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":{sub_system}:{layer}:SOUR:LAN {lan_id}", None),
             (f":{sub_system}:{layer}:SOUR:LAN?", lan_id)]
        ) as inst:
            setattr(inst,
                    f"{SUB_SYSTEMS[sub_system]}_{TRIGGER_LAYERS[layer]}_source_lan_id",
                    lan_id)
            assert lan_id == getattr(inst,
                   f"{SUB_SYSTEMS[sub_system]}_{TRIGGER_LAYERS[layer]}_source_lan_id")

    @pytest.mark.parametrize("timer", ['MIN', 1E-5, 0.12, 100000])
    def test_timer(self, sub_system, layer, timer):
        """Verify the communication of the arm/trigger_timer getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":{sub_system}:{layer}:TIM {timer}", None),
             (f":{sub_system}:{layer}:TIM?", timer)]
        ) as inst:
            setattr(inst, f"{SUB_SYSTEMS[sub_system]}_{TRIGGER_LAYERS[layer]}_timer", timer)
            assert timer == getattr(inst,
                   f"{SUB_SYSTEMS[sub_system]}_{TRIGGER_LAYERS[layer]}_timer")

    @pytest.mark.parametrize("output_signal", ['INT1', 'TOUT', 'EXT3'])
    def test_output_signal(self, sub_system, layer, output_signal):
        """Verify the communication of the arm/trigger_output_signal getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":{sub_system}:{layer}:TOUT:SIGN {output_signal}", None),
             (f":{sub_system}:{layer}:TOUT:SIGN?", output_signal)]
        ) as inst:
            setattr(inst,
                    f"{SUB_SYSTEMS[sub_system]}_{TRIGGER_LAYERS[layer]}_output_signal",
                    output_signal)
            assert output_signal == getattr(inst,
                   f"{SUB_SYSTEMS[sub_system]}_{TRIGGER_LAYERS[layer]}_output_signal")

    @pytest.mark.parametrize("state", [True, False])
    def test_output_enabled(self, sub_system, layer, state):
        """Verify the communication of the arm/trigger_output_enabled getter/setter."""
        mapping = {True: 1, False: 0}
        with expected_protocol(
            AgilentB2987,
            [(f":{sub_system}:{layer}:TOUT {mapping[state]}", None),
             (f":{sub_system}:{layer}:TOUT?", mapping[state])]
        ) as inst:
            setattr(inst,
                    f"{SUB_SYSTEMS[sub_system]}_{TRIGGER_LAYERS[layer]}_output_enabled",
                    state)
            assert state == getattr(inst,
                   f"{SUB_SYSTEMS[sub_system]}_{TRIGGER_LAYERS[layer]}_output_enabled")


@pytest.mark.parametrize("sub_system", ['ARM', 'TRIG'])
class TestTriggerPropertiesAllLayer:
    """Tests of the trigger properties for the ALL layer"""

    @pytest.mark.parametrize("state", [True, False])
    def test_bypass_once_enabled(self, sub_system, state):
        """Verify the communication of the arm/trigger_bypass_once_enabled setter."""
        mapping = {True: 'ONCE', False: 'OFF'}
        with expected_protocol(
            AgilentB2987,
            [(f":{sub_system}:ALL:BYP {mapping[state]}", None)]
        ) as inst:
            setattr(inst,
                    f"{SUB_SYSTEMS[sub_system]}_all_bypass_once_enabled",
                    state)

    @pytest.mark.parametrize("count", [1, 10, 1e3])
    def test_count(self, sub_system, count):
        """Verify the communication of the arm/trigger_count setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":{sub_system}:ALL:COUN {count}", None)]
        ) as inst:
            setattr(inst, f"{SUB_SYSTEMS[sub_system]}_all_count", count)

    @pytest.mark.parametrize("delay", [0, 10, 1e3, 'MAX'])
    def test_delay(self, sub_system, delay):
        """Verify the communication of the arm/trigger_delay setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":{sub_system}:ALL:DEL {delay}", None)]
        ) as inst:
            setattr(inst, f"{SUB_SYSTEMS[sub_system]}_all_delay", delay)

    @pytest.mark.parametrize("source", ['AINT', 'BUS', 'EXT2'])
    def test_source(self, sub_system, source):
        """Verify the communication of the arm/trigger_source setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":{sub_system}:ALL:SOUR {source}", None)]
        ) as inst:
            setattr(inst, f"{SUB_SYSTEMS[sub_system]}_all_source", source)

    @pytest.mark.parametrize("lan_id", ['LAN0', 'LAN7'])
    def test_source_lan_id(self, sub_system, lan_id):
        """Verify the communication of the arm/trigger_source_lan_id setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":{sub_system}:ALL:SOUR:LAN {lan_id}", None)]
        ) as inst:
            setattr(inst,
                    f"{SUB_SYSTEMS[sub_system]}_all_source_lan_id",
                    lan_id)

    @pytest.mark.parametrize("timer", ['MIN', 1E-5, 0.12, 100000])
    def test_timer(self, sub_system, timer):
        """Verify the communication of the arm/trigger_timer setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":{sub_system}:ALL:TIM {timer}", None)]
        ) as inst:
            setattr(inst, f"{SUB_SYSTEMS[sub_system]}_all_timer", timer)

    @pytest.mark.parametrize("output_signal", ['INT1', 'TOUT', 'EXT3'])
    def test_output_signal(self, sub_system, output_signal):
        """Verify the communication of the arm/trigger_output_signal setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":{sub_system}:ALL:TOUT:SIGN {output_signal}", None)]
        ) as inst:
            setattr(inst,
                    f"{SUB_SYSTEMS[sub_system]}_all_output_signal",
                    output_signal)

    @pytest.mark.parametrize("state", [True, False])
    def test_output_enabled(self, sub_system, state):
        """Verify the communication of the arm/trigger_output_enabled setter."""
        mapping = {True: 1, False: 0}
        with expected_protocol(
            AgilentB2987,
            [(f":{sub_system}:ALL:TOUT {mapping[state]}", None)]
        ) as inst:
            setattr(inst,
                    f"{SUB_SYSTEMS[sub_system]}_all_output_enabled",
                    state)


class TestElectrometer:
    """Tests of the electrometer functions"""

    @pytest.mark.parametrize("function", ['CURR', 'CHAR', 'VOLT'])
    def test_function(self, function):
        """Verify the communication of the function getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":FUNC '{function}'", None),
             (":FUNC?", function)]
        ) as inst:
            inst.function = function
            assert function == inst.function

    def test_function_res(self):
        """Verify the communication of the function getter/setter if 'RES'."""
        with expected_protocol(
            AgilentB2987,
            [(":FUNC 'RES'", None),
             (":FUNC?", '"VOLT","CURR","RES"')]
        ) as inst:
            inst.function = "RES"
            assert ['VOLT', 'CURR', 'RES'] == inst.function

    def test_charge(self):
        """Verify the communication of the charge getter."""
        with expected_protocol(
            AgilentB2987,
            [(":MEAS:CHAR?", "5E-9")]
        ) as inst:
            assert inst.charge == 5E-9

    @pytest.mark.parametrize("range", ['MIN', 2E-6])
    def test_charge_range(self, range):
        """Verify the communication of the charge_range getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":CHAR:RANG {range}", None),
             (":CHAR:RANG?", range)]
        ) as inst:
            inst.charge_range = range
            assert range == inst.charge_range

    def test_resistance(self):
        """Verify the communication of the resistance getter."""
        with expected_protocol(
            AgilentB2987,
            [(":MEAS:RES?", "5E9")]
        ) as inst:
            assert inst.resistance == 5E9

    @pytest.mark.parametrize("range", ['MIN', 1E12])
    def test_resistance_range(self, range):
        """Verify the communication of the resistance_range getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":RES:RANG {range}", None),
             (":RES:RANG?", range)]
        ) as inst:
            inst.resistance_range = range
            assert range == inst.resistance_range

    def test_voltage(self):
        """Verify the communication of the voltage getter."""
        with expected_protocol(
            AgilentB2987,
            [(":MEAS:VOLT?", "11.34")]
        ) as inst:
            assert inst.voltage == 11.34

    @pytest.mark.parametrize("range", ['DEF', 20])
    def test_voltage_range(self, range):
        """Verify the communication of the voltage_range getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":VOLT:RANG {range}", None),
             (":VOLT:RANG?", range)]
        ) as inst:
            inst.voltage_range = range
            assert range == inst.voltage_range

    def test_humidity(self):
        """Verify the communication of the humidity getter."""
        with expected_protocol(
            AgilentB2987,
            [(":SYST:HUM?", "53.6")]
        ) as inst:
            assert inst.humidity == 53.6

    def test_temperature(self):
        """Verify the communication of the temperature getter."""
        with expected_protocol(
            AgilentB2987,
            [(":SYST:TEMP?", "23.8")]
        ) as inst:
            assert inst.temperature == 23.8

    @pytest.mark.parametrize("sensor", ['TC', 'HSEN'])
    def test_temperature_sensor(self, sensor):
        """Verify the communication of the temperature_sensor getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":SYST:TEMP:SEL {sensor}", None),
             (":SYST:TEMP:SEL?", sensor)]
        ) as inst:
            inst.temperature_sensor = sensor
            assert sensor == inst.temperature_sensor

    @pytest.mark.parametrize("unit", ['C', 'F', 'K'])
    def test_temperature_unit(self, unit):
        """Verify the communication of the temperature_unit getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":SYST:TEMP:UNIT {unit}", None),
             (":SYST:TEMP:UNIT?", unit)]
        ) as inst:
            inst.temperature_unit = unit
            assert unit == inst.temperature_unit


class TestSource:
    """Tests of the source functions"""

    @pytest.mark.parametrize("state", [True, False])
    def test_source_enabled(self, state):
        """Verify the communication of the source_enabled getter/setter."""
        mapping = {True: 1, False: 0}
        with expected_protocol(
            AgilentB2987,
            [(f":OUTP {mapping[state]}", None),
             (":OUTP?", mapping[state])]
        ) as inst:
            inst.source_enabled = state
            assert state == inst.source_enabled

    @pytest.mark.parametrize("low_state", ['FLO', 'COMM'])
    def test_source_low_state(self, low_state):
        """Verify the communication of the source_low_state getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":OUTP:LOW {low_state}", None),
             (":OUTP:LOW?", low_state)]
        ) as inst:
            inst.source_low_state = low_state
            assert low_state == inst.source_low_state

    @pytest.mark.parametrize("off_state", ['ZERO', 'HIZ', 'NORM'])
    def test_source_off_state(self, off_state):
        """Verify the communication of the source_off_state getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":OUTP:OFF:MODE {off_state}", None),
             (":OUTP:OFF:MODE?", off_state)]
        ) as inst:
            inst.source_off_state = off_state
            assert off_state == inst.source_off_state

    @pytest.mark.parametrize("voltage", [0, 3, -2.5, 1000, 1.5e2, -1e3])
    def test_source_voltage(self, voltage):
        """Verify the communication of the source_voltage getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":SOUR:VOLT {voltage:g}", None),
             (":SOUR:VOLT?", voltage)]
        ) as inst:
            inst.source_voltage = voltage
            assert voltage == inst.source_voltage

    @pytest.mark.parametrize("range", ['MIN', 1000])
    def test_source_voltage_range(self, range):
        """Verify the communication of the source_voltage_range getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":SOUR:VOLT:RANG {range}", None),
             (":SOUR:VOLT:RANG?", range)]
        ) as inst:
            inst.source_voltage_range = range
            assert range == inst.source_voltage_range
