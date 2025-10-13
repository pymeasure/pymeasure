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

from pymeasure.instruments.keithley import Keithley2400


INIT_COMMS = (":FORM:ELEM VOLT, CURR, RES, TIME, STAT", None)


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
        [INIT_COMMS, ("OUTP?", 1)],
    ) as inst:
        assert inst.source_enabled is True


def test_source_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, ("OUTP 0", None)],
    ) as inst:
        inst.source_enabled = False


def test_enable_source():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, ("OUTP 1", None)],
    ) as inst:
        inst.enable_source()


def test_disable_source():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, ("OUTP 0", None)],
    ) as inst:
        inst.disable_source()


def test_source_mode_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:FUNC?", "CURR")],
    ) as inst:
        assert inst.source_mode == "current"


def test_source_mode_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:FUNC VOLT", None)],
    ) as inst:
        inst.source_mode = "voltage"


def test_auto_output_off_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:CLE:AUTO?", 0)],
    ) as inst:
        assert inst.auto_output_off is False


def test_auto_output_off_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:CLE:AUTO 1", None)],
    ) as inst:
        inst.auto_output_off = True


def test_source_delay_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:DEL?", 0.1)],
    ) as inst:
        assert inst.source_delay == 0.1


def test_source_delay_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:DEL 0.1", None)],
    ) as inst:
        inst.source_delay = 0.1


def test_source_delay_auto_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:DEL:AUTO?", 1)],
    ) as inst:
        assert inst.source_delay_auto is True


def test_source_delay_auto_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:DEL:AUTO 0", None)],
    ) as inst:
        inst.source_delay_auto = False


def test_auto_zero_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SYST:AZER:STAT?", "ONCE")],
    ) as inst:
        assert inst.auto_zero == "once"


def test_auto_zero_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SYST:AZER:STAT 0", None)],
    ) as inst:
        inst.auto_zero = False


def test_output_off_state_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":OUTP:SMOD?", "HIMP")],
    ) as inst:
        assert inst.output_off_state == "disconnect"


def test_output_off_state_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":OUTP:SMOD ZERO", None)],
    ) as inst:
        inst.output_off_state = "zero"


###########
# MEASURE #
###########


def test_measure_all():
    with expected_protocol(
        Keithley2400,
        [
            INIT_COMMS,
            (":SENS:RES:MODE MAN", None),
            (":SENS:FUNC:ALL", None),
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
        [INIT_COMMS, (":MEAS:CURR?", 0.5)],
    ) as inst:
        assert inst.current == 0.5


def test_current_range_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:CURR:RANG?", 0.5)],
    ) as inst:
        assert inst.current_range == 0.5


def test_current_range_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:CURR:RANG 0.5", None)],
    ) as inst:
        inst.current_range = 0.5


def test_current_range_auto_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:CURR:RANG:AUTO?", 1)],
    ) as inst:
        assert inst.current_range_auto_enabled is True


def test_current_range_auto_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:CURR:RANG:AUTO 0", None)],
    ) as inst:
        inst.current_range_auto_enabled = False


def test_current_nplc_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:CURR:NPLC?", 1)],
    ) as inst:
        assert inst.current_nplc == 1


def test_current_nplc_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:CURR:NPLC 0.1", None)],
    ) as inst:
        inst.current_nplc = 0.1


def test_compliance_current_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:CURR:PROT?", 0.5)],
    ) as inst:
        assert inst.compliance_current == 0.5


def test_compliance_current_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:CURR:PROT 0.5", None)],
    ) as inst:
        inst.compliance_current = 0.5


def test_source_current_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:CURR?", 0.5)],
    ) as inst:
        assert inst.source_current == 0.5


def test_source_current_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:CURR 0.5", None)],
    ) as inst:
        inst.source_current = 0.5


def test_source_current_range_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:CURR:RANG?", 0.5)],
    ) as inst:
        assert inst.source_current_range == 0.5


def test_source_current_range_setter():  # TODO: This gives more than one value
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:CURR:RANG 0.5", None)],
    ) as inst:
        inst.source_current_range = 0.5


def test_source_current_range_auto_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:CURR:RANG:AUTO?", 1)],
    ) as inst:
        assert inst.source_current_range_auto_enabled is True


def test_source_current_range_auto_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:CURR:RANG:AUTO 0", None)],
    ) as inst:
        inst.source_current_range_auto_enabled = False


###############
# Voltage (V) #
###############


def test_voltage():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":MEAS:VOLT?", 0.5)],
    ) as inst:
        assert inst.voltage == 0.5


def test_voltage_range_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:VOLT:RANG?", 0.5)],
    ) as inst:
        assert inst.voltage_range == 0.5


def test_voltage_range_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:VOLT:RANG 0.5", None)],
    ) as inst:
        inst.voltage_range = 0.5


def test_voltage_range_auto_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:VOLT:RANG:AUTO?", 1)],
    ) as inst:
        assert inst.voltage_range_auto_enabled is True


def test_voltage_range_auto_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:VOLT:RANG:AUTO 0", None)],
    ) as inst:
        inst.voltage_range_auto_enabled = False


def test_voltage_nplc_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:VOLT:NPLC?", 1)],
    ) as inst:
        assert inst.voltage_nplc == 1


def test_voltage_nplc_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:VOLT:NPLC 0.1", None)],
    ) as inst:
        inst.voltage_nplc = 0.1


def test_compliance_voltage_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:VOLT:PROT?", 0.5)],
    ) as inst:
        assert inst.compliance_voltage == 0.5


def test_compliance_voltage_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:VOLT:PROT 0.5", None)],
    ) as inst:
        inst.compliance_voltage = 0.5


def test_source_voltage_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:VOLT?", 0.5)],
    ) as inst:
        assert inst.source_voltage == 0.5


def test_source_voltage_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:VOLT 0.5", None)],
    ) as inst:
        inst.source_voltage = 0.5


def test_source_voltage_range_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:VOLT:RANG?", 0.5)],
    ) as inst:
        assert inst.source_voltage_range == 0.5


def test_source_voltage_range_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:VOLT:RANG 0.5", None)],
    ) as inst:
        inst.source_voltage_range = 0.5


def test_source_voltage_range_auto_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:VOLT:RANG:AUTO?", 1)],
    ) as inst:
        assert inst.source_voltage_range_auto_enabled is True


def test_source_voltage_range_auto_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SOUR:VOLT:RANG:AUTO 0", None)],
    ) as inst:
        inst.source_voltage_range_auto_enabled = False


####################
# Resistance (Ohm) #
####################


def test_resistance():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":MEAS:RES?", 0.5)],
    ) as inst:
        assert inst.resistance == 0.5


def test_resistance_range_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:RES:RANG?", 0.5)],
    ) as inst:
        assert inst.resistance_range == 0.5


def test_resistance_range_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:RES:RANG 0.5", None)],
    ) as inst:
        inst.resistance_range = 0.5


def test_resistance_range_auto_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:RES:RANG:AUTO?", 1)],
    ) as inst:
        assert inst.resistance_range_auto_enabled is True


def test_resistance_range_auto_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:RES:RANG:AUTO 0", None)],
    ) as inst:
        inst.resistance_range_auto_enabled = False


def test_resistance_nplc_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:RES:NPLC?", 1)],
    ) as inst:
        assert inst.resistance_nplc == 1


def test_resistance_nplc_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SENS:RES:NPLC 0.1", None)],
    ) as inst:
        inst.resistance_nplc = 0.1


##########
# BUFFER #
##########


# TODO


###########
# TRIGGER #
###########


# TODO


##########
# FILTER #
##########


# TODO


######
# UI #
######


def test_display_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":DISP:ENAB?", 1)],
    ) as inst:
        assert inst.display_enabled is True


def test_display_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":DISP:ENAB 0", None)],
    ) as inst:
        inst.display_enabled = False


########
# MISC #
########


def test_four_wire_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SYST:RSEN?", 0)],
    ) as inst:
        assert inst.four_wire_enabled is False


def test_four_wire_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SYST:RSEN 1", None)],
    ) as inst:
        inst.four_wire_enabled = True


def test_line_frequency_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SYST:LFR?", 50)],
    ) as inst:
        assert inst.line_frequency == 50


def test_line_frequency_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SYST:LFR 60", None)],
    ) as inst:
        inst.line_frequency = 60


def test_auto_line_frequency_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SYST:LFR:AUTO?", 1)],
    ) as inst:
        assert inst.line_frequency_auto is True


def test_auto_line_frequency_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":SYST:LFR:AUTO 0", None)],
    ) as inst:
        inst.line_frequency_auto = False


def test_front_terminals_enabled_getter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ROUT:TERM?", "FRON")],
    ) as inst:
        assert inst.front_terminals_enabled is True


def test_front_terminals_enabled_setter():
    with expected_protocol(
        Keithley2400,
        [INIT_COMMS, (":ROUT:TERM REAR", None)],
    ) as inst:
        inst.front_terminals_enabled = False
