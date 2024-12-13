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
from pymeasure.instruments import Instrument, SCPIUnknownMixin
from pymeasure.instruments.validators import strict_discrete_set

class HP66312A(SCPIUnknownMixin, Instrument):
    """ Represents the HP / Agilent / Keysight 66312AA Multimeter and
    provides a high-level interface for interacting with the instrument.

    .. code-block:: python
#garbage below, reminder to make example code
        dmm = HP66312A("GPIB::1")
        dmm.function_ = "DCV"
        print(dmm.reading)  # -> Single float reading

        dmm.nplc = 0.02
        dmm.autozero_enabled = False
        dmm.trigger_count = 100
        dmm.trigger_delay = "MIN"
        print(dmm.reading)  # -> Array of 100 very fast readings

    """
    FUNCTIONS = {"DCV": "VOLT", "DCV_RATIO": "VOLT:RAT",
                 "ACV": "VOLT:AC", "DCI": "CURR", "ACI": "CURR:AC",
                 "R2W": "RES", "R4W": "FRES", "FREQ": "FREQ",
                 "PERIOD": "PER", "CONTINUITY": "CONT", "DIODE": "DIOD"}

    FUNCTIONS_WITH_RANGE = {
        "DCV": "VOLT", "ACV": "VOLT:AC", "DCI": "CURR",
        "ACI": "CURR:AC", "R2W": "RES", "R4W": "FRES",
        "FREQ": "FREQ", "PERIOD": "PER"}

    BOOL_MAPPINGS = {True: 1, False: 0}

    # Below: stop_bits: 20 comes from
    # https://pyvisa.readthedocs.io/en/latest/api/constants.html#pyvisa.constants.StopBits
    def __init__(self, adapter, name="HP 34401A", **kwargs):
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
    
    # #Measurement commands WIP
    # current = Instrument.control(
        # "MEAS:CURR?",
    # )
    
    # current_rms = Instrument.control(
        # "MEAS:CURR:ACDC?",
    # )
    
    # current_min = Instrument.control(
        # "MEAS:CURR:MIN?",
    # )

    # current_max = Instrument.control(
        # "MEAS:CURR:MAX?",
    # )    
    
    # voltage = Instrument.control(
        # "MEAS:VOLT?",
    # )

    # voltage_rms = Instrument.control(
        # "MEAS:VOLT:ACDC?",
    # )

    # voltage_min = Instrument.control(
        # "MEAS:VOLT:MIN?",
    # )
    
    # voltage_max = Instrument.control(
        # "MEAS:VOLT:MAX?",
    # )

    # Trigger related commands WIP
    def init_trigger(self):
        """Set the state of the triggering system to "wait-for-trigger".

        Measurements will begin when the specified trigger conditions
        are satisfied after this command is received."""
        self.write("INIT"),

    reading = Instrument.measurement(
        "READ?",
        """Take a measurement of the currently selected function.

        Reading this property is equivalent to calling `init_trigger()`,
        waiting for completion and fetching the reading(s).""",
    )

    trigger_source = Instrument.control(
        "TRIG:SOUR?", "TRIG:SOUR %s",
        """Control the trigger source.

        Valid values: "IMM", "BUS", "EXT"
        The multimeter will accept a software (bus) trigger,
        an immediate internal trigger (this is the default source),
        or a hardware trigger from the rear-panel
        Ext Trig (external trigger) terminal.""",
        validator=strict_discrete_set,
        values=["IMM", "BUS", "EXT"],
    )

    trigger_delay = Instrument.control(
        "TRIG:DEL?", "TRIG:DEL %s",
        """Control the trigger delay in seconds.

        Valid values (incl. floats): 0 to 3600 seconds, "MIN", "MAX".""",
    )

    trigger_auto_delay_enabled = Instrument.control(
        "TRIG:DEL:AUTO?", "TRIG:DEL:AUTO %s",
        """Control the automatic trigger delay state.

        If enabled, the delay is determined by function, range, integration time,
        and ac filter setting. Selecting a specific trigger delay value
        automatically turns off the automatic trigger delay.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    sample_count = Instrument.control(
        "SAMP:COUN?", "SAMP:COUN %s",
        """Controls the number of samples per trigger event.

        Valid values: 1 to 50000, "MIN", "MAX".""",
    )

    trigger_count = Instrument.control(
        "TRIG:COUN?", "TRIG:COUN %s",
        """Control the number of triggers accepted before returning to the "idle" state.

        Valid values: 1 to 50000, "MIN", "MAX", "INF".
        The INFinite parameter instructs the multimeter to continuously accept triggers
        (you must send a device clear to return to the "idle" state).""",
    )

    stored_reading = Instrument.measurement(
        "FETC?",
        """Measure the reading(s) currently stored in the multimeter's internal memory.

        Reading this property will NOT initialize a trigger.
        If you need that, use the `reading` property instead.""",
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
        """Control the text displayed on the multimeter's display.

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
        """The SCPI version of the multimeter.""",
    )

    self_test_result = Instrument.measurement(
        "*TST?",
        """Initiate a self-test of the multimeter and return the result.

        Be sure to set an appropriate connection timeout,
        otherwise the command will fail.""",
    )

    def write(self, command):
        """Write a command to the instrument."""
        if "{function_prefix_for_range}" in command:
            command = command.replace("{function_prefix_for_range}",
                                      self._get_function_prefix_for_range())
        elif "{function}" in command:
            command = command.replace("{function}", HP34401A.FUNCTIONS[self.function_])
        super().write(command)

    def _get_function_prefix_for_range(self):
        function_prefix = HP34401A.FUNCTIONS_WITH_RANGE[self.function_]
        if function_prefix in ["FREQ", "PER"]:
            function_prefix += ":VOLT"
        return function_prefix
