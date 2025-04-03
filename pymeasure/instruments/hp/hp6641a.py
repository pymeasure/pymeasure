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

import enum
from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class OperationStatus(enum.Flag):
    """Operation Status."""
    CAL = 1 << 0
    WTG = 1 << 5
    CV = 1 << 8
    CC = 1 << 10


class QuestionableStatus(enum.Flag):
    """Questionable Status."""
    OV = 1 << 0
    OC = 1 << 1
    OT = 1 << 4
    RI = 1 << 9
    UNR = 1 << 10


class StandardEventStatus(enum.Flag):
    """Standard Event Status."""
    OPC = 1 << 0
    QYE = 1 << 2
    DDE = 1 << 3
    EXE = 1 << 4
    CME = 1 << 5
    PON = 1 << 7


limits = {
    "HP6641A": {"Volt_lim": 8.190, "OVP_lim": 8.8, "Cur_lim": 20.475},
    "HP6673A": {"Volt_lim": 35.831, "OVP_lim": 42.0, "Cur_lim": 61.43},
    "HP6674A": {"Volt_lim": 61.425, "OVP_lim": 72.0, "Cur_lim": 35.83}}


class HP6641A(SCPIMixin, Instrument):
    """ Represents the HP / Agilent 6641A
    provides a high-level interface for interacting with the instrument.

    .. code-block:: python

        instr =  vxi11.Instrument("192.168.88.116", "gpib0,6")
        psu = hp6641a.HP6641A(instr);
        psu.clear()
        psu.remote_control_enabled = True
        psu.voltage_setpoint = 3.3
        psu.current_setpoint = 1.5
        psu.ovp_setpoint = 8.0
        psu.output_enabled = 1
        print(f'read errors: {psu.pop_err()}')
        while True:
            print(f'output voltage: {psu.voltage}')
            print(f'output current: {psu.current}')
            time.sleep(1)
    """

    BOOL_MAPPINGS = {True: 1, False: 0}
    DISP_MAPPINGS = {True: "TEXT", False: "NORM"}

    def __init__(self, adapter, name="HP6641A", **kwargs):
        super().__init__(adapter, name, **kwargs)

    voltage_setpoint = Instrument.control(
        "VOLT?", "VOLT %g",
        "Control the voltage setpoint in Volts (float).",
        dynamic=True,
        validator=strict_range,
        values=[0, limits["HP6641A"]["Volt_lim"]]
    )

    ovp_setpoint = Instrument.control(
        "VOLT:PROT?", "VOLT:PROT %g",
        "Control the Over Voltage Protection setpoint in Volts (float).",
        dynamic=True,
        validator=strict_range,
        values=[0, limits["HP6641A"]["OVP_lim"]]
    )

    current_setpoint = Instrument.control(
        "CURR?", "CURR %g",
        "Control the current setpoint in Amperes (float).",
        dynamic=True,
        validator=strict_range,
        values=[0, limits["HP6641A"]["Cur_lim"]]
    )

    voltage = Instrument.measurement(
        "MEAS:VOLT?",
        "Measure the voltage at the power supply's sense terminals"
    )

    current = Instrument.measurement(
        "MEAS:CURR?",
        "Measure the current at the power supply's sense terminals"
    )

    output_enabled = Instrument.control(
        "OUTP:STAT?", "OUTP:STAT %g",
        "Control the power supply output and Read back the programmed value",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True
    )

    disp_mode_text = Instrument.control(
        "DISP:MODE?", "DISP:MODE %s",
        "Set and Get display mode between its normal metering mode and a mode in which\
        it displays text sent by the user",
        validator=strict_discrete_set,
        values=DISP_MAPPINGS,
        map_values=True
    )

    disp_text = Instrument.control(
        "DISP:TEXT?", "DISP:TEXT \"%s\"",
        "Set and Get character strings to/from display",
    )

    scpi_version = Instrument.measurement(
        "SYST:VERS?",
        """Get SCPI version of the multimeter.""",
    )

    self_test_result = Instrument.measurement(
        "*TST?",
        """Get self-test result.

        Be sure to set an appropriate connection timeout,
        otherwise the command will fail.""",
    )

    def pop_err(self):
        """Pop an error off the error queue. Returns a tuple containing the
        code and error description. An error code 0 indicates success."""
        error_str = self.ask('SYST:ERR?').strip()
        error_code_str, error_desc_str = error_str.split(',')
        error_code = int(error_code_str)
        error_desc = error_desc_str.strip('"')
        return error_code, error_desc

    def get_status(self):
        """Read Operation, Questionable, Standard Event Status."""
        operation_status = OperationStatus(int(self.ask("STAT:OPER:COND?")))
        questionable_status = QuestionableStatus(int(self.ask("STAT:QUES:COND?")))
        standard_event_status = StandardEventStatus(int(self.ask("*ESR?")))
        return operation_status, questionable_status, standard_event_status


class HP6673A(HP6641A):
    """ Represents the HP / Agilent 6674A
    provides a high-level interface for interacting with the instrument.
    """

    set_voltage_values = [0, limits["HP6673A"]["Volt_lim"]]
    set_ovp_values = [0, limits["HP6673A"]["OVP_lim"]]
    set_current_values = [0, limits["HP6673A"]["Cur_lim"]]

    def __init__(self, adapter, name="HP6673A", **kwargs):
        super().__init__(adapter, name, **kwargs)


class HP6674A(HP6641A):
    """ Represents the HP / Agilent 6674A
    provides a high-level interface for interacting with the instrument.
    """

    voltage_setpoint_values = [0, limits["HP6674A"]["Volt_lim"]]
    ovp_setpoint_values = [0, limits["HP6674A"]["OVP_lim"]]
    current_setpoint_values = [0, limits["HP6674A"]["Cur_lim"]]

    def __init__(self, adapter, name="HP6674A", **kwargs):
        super().__init__(adapter, name, **kwargs)
