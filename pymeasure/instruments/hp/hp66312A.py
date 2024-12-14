#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
#work in progress by TEM01STAR
from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set

class HP66312A(SCPIMixin, Instrument):
    """ Represents the HP / Agilent / Keysight 66312AA Dynamic Measurement DC Source and
    provides a high-level interface for interacting with the instrument.

    .. code-block:: python
    
        source = HP66312A("GPIB::1")
        source.voltage_setpoint = 5
        source.current_limit = 0.2
        source.output_enabled = 1
        print(source.current) #-> Measure current draw of load


    """

    BOOL_MAPPINGS = {True: 1, False: 0}

    # Below: stop_bits: 20 comes from
    # https://pyvisa.readthedocs.io/en/latest/api/constants.html#pyvisa.constants.StopBits
    def __init__(self, adapter, name="HP 66312A", **kwargs):
        super().__init__(
            adapter,
            name,
            asrl={'baud_rate': 9600, 'data_bits': 8, 'parity': 0, 'stop_bits': 20},
            **kwargs
        )

    #Source commands
    output_enabled = Instrument.control(
        "OUTP?", "OUTP %s",
        """Enable[Disable] source output""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )
    
    voltage_setpoint = Instrument.control(
        "VOLT?","VOLT %s",
        """Output voltage setpoint""",
    )
    
    voltage_trigger_level = Instrument.control(
        "VOLT:TRIG?", "VOLT:TRIG %s",
        """Sets the pending triggered voltage level""",
    )
    
    voltage_protection = Instrument.control(
        "VOLT:PROT?", "VOLT:PROT %s",
        """Accepts floats or LEV MAX""",
    )

    
    current_limit = Instrument.control(
        "CURR?", "CURR %s",
        """Output current limit setpoint""",
    )
    
    current_trigger_level = Instrument.control(
        "CURR:TRIG?", "CURR:TRIG %s",
        """Sets the pending triggered current limit""",
    )
    
    current_protection_enabled = Instrument.control(
        "CURR:PROT:STAT?", "CURR:PROT:STAT %s",
        """Disables output if overcurrent is tripped. Off on reset""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )
    
    # #Measurement commands
    current = Instrument.measurement(
        "MEAS:CURR?",
        """Measures and returns the DC output current.""",
    )
    
    current_rms = Instrument.measurement(
        "MEAS:CURR:ACDC?",
        """Measures and returns the AC+DC RMS output current.""",
    )
    
    current_min = Instrument.measurement(
        "MEAS:CURR:MIN?",
        """Returns the minimum DC output current from a sample.""",
    )

    current_max = Instrument.measurement(
        "MEAS:CURR:MAX?",
        """Returns the maximum DC output current from a sample.""",
    )    
    
    voltage = Instrument.measurement(
        "MEAS:VOLT?",
        """Measures and returns the dc output voltage.""",
    )

    voltage_rms = Instrument.measurement(
        "MEAS:VOLT:ACDC?",
        """Measures and returns the ac+dc RMs output voltage.""",
    )

    voltage_min = Instrument.measurement(
        "MEAS:VOLT:MIN?",
        """Returns the low voltage level from a sample.""",
    )
    
    voltage_max = Instrument.measurement(
        "MEAS:VOLT:MAX?",
        """Returns the high voltage level from a sample.""",
    )

    # Output Trigger related commands
    def init_single_output_trigger(self):
        """Set the state of the triggering system to "wait-for-trigger".

        The source will change the output levels to voltage_trigger_level and current_trigger_level when it recieves a trigger command.
        It will return to Idle after a single trigger"""
        self.write("INIT:NAME TRAN"),
        
    def enable_cont_output_trigger(self):
        """Set the state of the triggering system to "wait-for-trigger".

        The source will change the output levels to voltage_trigger_level and current_trigger_level when it recieves a trigger command.
        It will return to Idle after a single trigger"""
        self.write("INIT:CONT:NAME TRAN, ON"),

    trigger_output = Instrument.setting(
        "*TRG",
        """Send a single trigger to the instrument""",
    )
   
    # Display related commands
    display_enabled = Instrument.control(
        "DISP?", "DISP %s",
        """Control the display state.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    display_mode = Instrument.control(
        "DISP:MODE?", "DISP:MODE \"%s\"",
        """Swap the display between normal and text display modes""",
        validator=strict_discrete_set,
        values=["NORM", "TEXT"], 
    )

    displayed_text = Instrument.control(
        "DISP:TEXT?", "DISP:TEXT \"%s\"",
        """Control the text displayed on the source's display.

        The text can be up to 12 characters long;
        any additional characters are truncated my the multimeter.""",
        get_process=lambda x: x.strip('"'),
    )

    # System related commands
    remote_control_enabled = Instrument.control(
        "SYST: ", "SYST:%s",
        """Control whether remote control is enabled.""",
        validator=strict_discrete_set,
        values={True: "REM", False: "LOC"},
        map_values=True,
    )
    
    error = Instrument.measurement(
    "SYST:ERR?",
    """Read the next error in the buffer (FIFO)""",
    )

    remote_lock_enabled = Instrument.control(
        "SYST: ", "SYST:%s",
        """Control whether the beeper is enabled.""",
        validator=strict_discrete_set,
        values={True: "RWL", False: "LOC"},
        map_values=True,
    )

    scpi_version = Instrument.measurement(
        "SYST:VERS?",
        """The SCPI version of the source.""",
    )

    self_test_result = Instrument.measurement(
        "*TST?",
        """Initiate a self-test of the source and return the result.

        Be sure to set an appropriate connection timeout,
        otherwise the command will fail.""",
    )

    def write(self, command):
        """Write a command to the instrument."""
        super().write(command)
