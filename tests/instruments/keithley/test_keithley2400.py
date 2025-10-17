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

import math

from pymeasure.test import expected_protocol

from pymeasure.instruments.keithley.keithley2400 import (
    Keithley2400,
    SourceMode,
    AutoZeroState,
    OutputOffState,
    TriggerSource,
    ArmSource,
    TriggerOutputEvent,
    ArmOutputEvent,
)


INIT_COMMS = (":FORMAT:ELEMENTS VOLTAGE, CURRENT, RESISTANCE, TIME, STATUS", None)


def test_id():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, ("*IDN?", "KEITHLEY INSTRUMENTS INC., MODEL nnnn, xxxxxxx, yyyyy/zzzzz /a/d")],
    ) as inst:
        assert inst.id == "KEITHLEY INSTRUMENTS INC., MODEL nnnn, xxxxxxx, yyyyy/zzzzz /a/d"


def test_next_error():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, ("SYST:ERR?", '-113, "Undefined header"')],
    ) as inst:
        assert inst.next_error == [-113, ' "Undefined header"']


##########
# SOURCE #
##########


def test_source_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, ("OUTPUT?", 1)],
    ) as inst:
        assert inst.source_enabled is True


def test_source_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, ("OUTPUT 0", None)],
    ) as inst:
        inst.source_enabled = False


def test_enable_source():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, ("OUTPUT 1", None)],
    ) as inst:
        inst.enable_source()


def test_disable_source():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, ("OUTPUT 0", None)],
    ) as inst:
        inst.disable_source()


def test_source_mode_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:FUNCTION?", "current")],
    ) as inst:
        assert inst.source_mode == SourceMode.CURRENT


def test_source_mode_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:FUNCTION voltage", None)],
    ) as inst:
        inst.source_mode = SourceMode.VOLTAGE


def test_auto_output_off_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:CLEAR:AUTO?", 0)],
    ) as inst:
        assert inst.auto_output_off is False


def test_auto_output_off_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:CLEAR:AUTO 1", None)],
    ) as inst:
        inst.auto_output_off = True


def test_source_delay_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:DELAY?", 0.1)],
    ) as inst:
        assert inst.source_delay == 0.1


def test_source_delay_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:DELAY 0.1", None)],
    ) as inst:
        inst.source_delay = 0.1


def test_source_delay_auto_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:DELAY:AUTO?", 1)],
    ) as inst:
        assert inst.source_delay_auto_enabled is True


def test_source_delay_auto_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:DELAY:AUTO 0", None)],
    ) as inst:
        inst.source_delay_auto_enabled = False


def test_auto_zero_state_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SYSTEM:AZERO:STATUS?", "ONCE")],
    ) as inst:
        assert inst.auto_zero_state == AutoZeroState.ONCE


def test_auto_zero_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SYSTEM:AZERO:STATUS OFF", None)],
    ) as inst:
        inst.auto_zero_state = AutoZeroState.OFF


def test_output_off_state_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":OUTPUT:SMODE?", "HIMP")],
    ) as inst:
        assert inst.output_off_state == OutputOffState.DISCONNECTED


def test_output_off_state_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":OUTPUT:SMODE ZERO", None)],
    ) as inst:
        inst.output_off_state = OutputOffState.ZERO


###########
# MEASURE #
###########


def test_filter_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:AVERAGE?", 0)],
    ) as inst:
        assert inst.filter_enabled is False


def test_filter_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:AVERAGE 1", None)],
    ) as inst:
        inst.filter_enabled = True


def test_repeat_filter_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:AVERAGE:TCONTROL?", "MOVING")],
    ) as inst:
        assert inst.repeat_filter_enabled is False


def test_repeat_filter_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:AVERAGE:TCONTROL REPEAT", None)],
    ) as inst:
        inst.repeat_filter_enabled = True


def test_filter_count_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:AVERAGE:COUNT?", 10)],
    ) as inst:
        assert inst.filter_count == 10


def test_filter_count_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:AVERAGE:COUNT 15", None)],
    ) as inst:
        inst.filter_count = 15


def test_measure_all():
    with expected_protocol(
        Keithley2400,
        [
            INIT_COMMS,
            (":SENSE:RESISTANCE:MODE MANUAL", None),
            (":SENSE:FUNCTION:ALL", None),
            (":READ?", "0.1,0.2,9.91e37,1234,5678\n"),
        ],
    ) as inst:
        result = inst.measure_all()
        assert result["voltage"] == 0.1
        assert result["current"] == 0.2
        assert math.isnan(result["resistance"])
        assert result["time"] == 1234
        assert result["status"] == 5678


###############
# Current (A) #
###############


def test_current():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":MEASURE:CURRENT?", b"0.1,0.2,9.91e37,1234,5678\n")],
    ) as inst:
        assert inst.current == 0.2


def test_current_range_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:CURRENT:RANGE?", 0.5)],
    ) as inst:
        assert inst.current_range == 0.5


def test_current_range_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:CURRENT:RANGE 0.5", None)],
    ) as inst:
        inst.current_range = 0.5


def test_current_range_auto_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:CURRENT:RANGE:AUTO?", 1)],
    ) as inst:
        assert inst.current_range_auto_enabled is True


def test_current_range_auto_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:CURRENT:RANGE:AUTO 0", None)],
    ) as inst:
        inst.current_range_auto_enabled = False


def test_current_nplc_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:CURRENT:NPLCYCLES?", 1)],
    ) as inst:
        assert inst.current_nplc == 1


def test_current_nplc_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:CURRENT:NPLCYCLES 0.1", None)],
    ) as inst:
        inst.current_nplc = 0.1


def test_compliance_current_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:CURRENT:PROTECTION?", 0.5)],
    ) as inst:
        assert inst.compliance_current == 0.5


def test_compliance_current_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:CURRENT:PROTECTION 0.5", None)],
    ) as inst:
        inst.compliance_current = 0.5


def test_source_current_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:CURRENT?", 0.5)],
    ) as inst:
        assert inst.source_current == 0.5


def test_source_current_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:CURRENT 0.5", None)],
    ) as inst:
        inst.source_current = 0.5


def test_source_current_range_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:CURRENT:RANGE?", 0.5)],
    ) as inst:
        assert inst.source_current_range == 0.5


def test_source_current_range_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:CURRENT:RANGE 0.5", None)],
    ) as inst:
        inst.source_current_range = 0.5


def test_source_current_range_auto_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:CURRENT:RANGE:AUTO?", 1)],
    ) as inst:
        assert inst.source_current_range_auto_enabled is True


def test_source_current_range_auto_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:CURRENT:RANGE:AUTO 0", None)],
    ) as inst:
        inst.source_current_range_auto_enabled = False


###############
# Voltage (V) #
###############


def test_voltage():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":MEASURE:VOLTAGE?", b"0.1,0.2,9.91e37,1234,5678\n")],
    ) as inst:
        assert inst.voltage == 0.1


def test_voltage_range_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:VOLTAGE:RANGE?", 0.5)],
    ) as inst:
        assert inst.voltage_range == 0.5


def test_voltage_range_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:VOLTAGE:RANGE 0.5", None)],
    ) as inst:
        inst.voltage_range = 0.5


def test_voltage_range_auto_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:VOLTAGE:RANGE:AUTO?", 1)],
    ) as inst:
        assert inst.voltage_range_auto_enabled is True


def test_voltage_range_auto_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:VOLTAGE:RANGE:AUTO 0", None)],
    ) as inst:
        inst.voltage_range_auto_enabled = False


def test_voltage_nplc_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:VOLTAGE:NPLCYCLES?", 1)],
    ) as inst:
        assert inst.voltage_nplc == 1


def test_voltage_nplc_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:VOLTAGE:NPLCYCLES 0.1", None)],
    ) as inst:
        inst.voltage_nplc = 0.1


def test_compliance_voltage_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:VOLTAGE:PROTECTION?", 0.5)],
    ) as inst:
        assert inst.compliance_voltage == 0.5


def test_compliance_voltage_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:VOLTAGE:PROTECTION 0.5", None)],
    ) as inst:
        inst.compliance_voltage = 0.5


def test_source_voltage_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:VOLTAGE?", 0.5)],
    ) as inst:
        assert inst.source_voltage == 0.5


def test_source_voltage_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:VOLTAGE 0.5", None)],
    ) as inst:
        inst.source_voltage = 0.5


def test_source_voltage_range_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:VOLTAGE:RANGE?", 0.5)],
    ) as inst:
        assert inst.source_voltage_range == 0.5


def test_source_voltage_range_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:VOLTAGE:RANGE 0.5", None)],
    ) as inst:
        inst.source_voltage_range = 0.5


def test_source_voltage_range_auto_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:VOLTAGE:RANGE:AUTO?", 1)],
    ) as inst:
        assert inst.source_voltage_range_auto_enabled is True


def test_source_voltage_range_auto_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOURCE:VOLTAGE:RANGE:AUTO 0", None)],
    ) as inst:
        inst.source_voltage_range_auto_enabled = False


####################
# Resistance (Ohm) #
####################


def test_resistance():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":MEASURE:RESISTANCE?", "0.1,0.2,0.5,1234,5678\n")],
    ) as inst:
        assert inst.resistance == 0.5


def test_resistance_range_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:RESISTANCE:RANGE?", 0.5)],
    ) as inst:
        assert inst.resistance_range == 0.5


def test_resistance_range_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:RESISTANCE:RANGE 0.5", None)],
    ) as inst:
        inst.resistance_range = 0.5


def test_resistance_range_auto_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:RESISTANCE:RANGE:AUTO?", 1)],
    ) as inst:
        assert inst.resistance_range_auto_enabled is True


def test_resistance_range_auto_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:RESISTANCE:RANGE:AUTO 0", None)],
    ) as inst:
        inst.resistance_range_auto_enabled = False


def test_resistance_nplc_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:RESISTANCE:NPLCYCLES?", 1)],
    ) as inst:
        assert inst.resistance_nplc == 1


def test_resistance_nplc_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENSE:RESISTANCE:NPLCYCLES 0.1", None)],
    ) as inst:
        inst.resistance_nplc = 0.1


###########
# TRIGGER #
###########


def test_trigger():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, ("*TRG", None)],
    ) as inst:
        inst.trigger()


def test_reset_trigger():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ABORT", None)],
    ) as inst:
        inst.reset_trigger()


def test_clear_trigger():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":TRIGGER:CLEAR", None)],
    ) as inst:
        inst.clear_trigger()


def test_trigger_count_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":TRIGGER:COUNT?", 10)],
    ) as inst:
        assert inst.trigger_count == 10


def test_trigger_count_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ARM:COUNT?", 7), (":TRIGGER:COUNT 10", None)],
    ) as inst:
        inst.trigger_count = 10


def test_arm_count_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ARM:COUNT?", 10)],
    ) as inst:
        assert inst.arm_count == 10


def test_arm_count_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":TRIGGER:COUNT?", 7), (":ARM:COUNT 10", None)],
    ) as inst:
        inst.arm_count = 10


def test_trigger_delay_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":TRIGGER:DELAY?", 10)],
    ) as inst:
        assert inst.trigger_delay == 10


def test_trigger_delay_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":TRIGGER:DELAY 10", None)],
    ) as inst:
        inst.trigger_delay = 10


def test_arm_timer_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ARM:TIMER?", 10)],
    ) as inst:
        assert inst.arm_timer == 10


def test_arm_timer_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ARM:TIMER 10", None)],
    ) as inst:
        inst.arm_timer = 10


def test_trigger_source_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":TRIGGER:SOURCE?", "IMMEDIATE")],
    ) as inst:
        assert inst.trigger_source == TriggerSource.IMMEDIATE


def test_trigger_source_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":TRIGGER:SOURCE TLINK", None)],
    ) as inst:
        inst.trigger_source = TriggerSource.TRIGGER_LINK


def test_arm_source_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ARM:SOURCE?", "IMMEDIATE")],
    ) as inst:
        assert inst.arm_source == ArmSource.IMMEDIATE


def test_arm_source_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ARM:SOURCE TLINK", None)],
    ) as inst:
        inst.arm_source = ArmSource.TRIGGER_LINK


def test_trigger_output_event_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":TRIGGER:OUTPUT?", "SENSE")],
    ) as inst:
        assert inst.trigger_output_event == TriggerOutputEvent.SENSE


def test_trigger_output_event_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":TRIGGER:OUTPUT NONE", None)],
    ) as inst:
        inst.trigger_output_event = TriggerOutputEvent.NONE


def test_arm_output_event_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ARM:OUTPUT?", "TENTER")],
    ) as inst:
        assert inst.arm_output_event == ArmOutputEvent.ENTER


def test_arm_output_event_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ARM:OUTPUT NONE", None)],
    ) as inst:
        inst.arm_output_event = ArmOutputEvent.NONE


def test_disable_output_triggers():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ARM:OUTPUT NONE", None), (":TRIGGER:OUTPUT NONE", None)],
    ) as inst:
        inst.disable_output_triggers()


def test_trigger_input_line_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":TRIGGER:ILINE?", 0)],
    ) as inst:
        assert inst.trigger_input_line == 0


def test_trigger_input_line_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":TRIGGER:ILINE 1", None)],
    ) as inst:
        inst.trigger_input_line = 1


def test_arm_input_line_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ARM:ILINE?", 0)],
    ) as inst:
        assert inst.arm_input_line == 0


def test_arm_input_line_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ARM:ILINE 1", None)],
    ) as inst:
        inst.arm_input_line = 1


def test_trigger_output_line_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":TRIGGER:OLINE?", 0)],
    ) as inst:
        assert inst.trigger_output_line == 0


def test_trigger_output_line_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":TRIGGER:OLINE 1", None)],
    ) as inst:
        inst.trigger_output_line = 1


def test_arm_output_line_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ARM:OLINE?", 0)],
    ) as inst:
        assert inst.arm_output_line == 0


def test_arm_output_line_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ARM:OLINE 1", None)],
    ) as inst:
        inst.arm_output_line = 1


def test_trigger_on_bus():
    with expected_protocol(
        Keithley2400,
        [
            INIT_COMMS,
            (":TRIGGER:COUNT?", 1),
            (":ARM:COUNT 1", None),
            (":ARM:SOURCE BUS", None),
            (":TRIGGER:SOURCE IMMEDIATE", None),
        ],
    ) as inst:
        inst.trigger_on_bus()


def test_trigger_on_external():
    with expected_protocol(
        Keithley2400,
        [
            INIT_COMMS,
            (":ARM:SOURCE TLINK", None),
            (":TRIGGER:SOURCE TLINK", None),
            (":ARM:ILINE 1", None),
            (":TRIGGER:ILINE 1", None),
        ],
    ) as inst:
        inst.trigger_on_external()


######
# UI #
######


def test_display_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":DISPLAY:ENABLE?", 1)],
    ) as inst:
        assert inst.display_enabled is True


def test_display_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":DISPLAY:ENABLE 0", None)],
    ) as inst:
        inst.display_enabled = False


########
# MISC #
########


def test_four_wire_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SYSTEM:RSENSE?", 0)],
    ) as inst:
        assert inst.four_wire_enabled is False


def test_four_wire_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SYSTEM:RSENSE 1", None)],
    ) as inst:
        inst.four_wire_enabled = True


def test_line_frequency_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SYSTEM:LFREQUENCY?", 50)],
    ) as inst:
        assert inst.line_frequency == 50


def test_line_frequency_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SYSTEM:LFREQUENCY 60", None)],
    ) as inst:
        inst.line_frequency = 60


def test_line_frequency_auto_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SYSTEM:LFREQUENCY:AUTO?", 1)],
    ) as inst:
        assert inst.line_frequency_auto_enabled is True


def test_line_frequency_auto_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SYSTEM:LFREQUENCY:AUTO 0", None)],
    ) as inst:
        inst.line_frequency_auto_enabled = False


def test_front_terminals_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ROUTE:TERMINALS?", "FRONT")],
    ) as inst:
        assert inst.front_terminals_enabled is True


def test_front_terminals_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ROUTE:TERMINALS REAR", None)],
    ) as inst:
        inst.front_terminals_enabled = False
