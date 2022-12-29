#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set


class HP34401A(Instrument):
    """ Represents the HP 34401A instrument.
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

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter,
            "HP 34401A",
            asrl={'baud_rate': 9600, 'data_bits': 7, 'parity': 2},
            **kwargs
        )

    function_ = Instrument.control(
        "FUNC?", "FUNC \"%s\"",
        """ A string property that controls the measurement function,
        which can take the values: DCV, DCV_RATIO, ACV, DCI, ACI,
        R2W, R4W, FREQ, PERIOD, CONTINUITY, DIODE. """,
        validator=strict_discrete_set,
        values=FUNCTIONS,
        map_values=True,
        get_process=lambda v: v.strip('"'))

    @property
    def range_(self):
        """ A float property that sets the range for the currently active function.
        For frequency and period measurements, ranging applies to
        the signal's input voltage, not its frequency"""
        command = f"{self._get_function_range_prefix()}:RANG?"
        return float(self.ask(command))

    @range_.setter
    def range_(self, value):
        command = f"{self._get_function_range_prefix()}:RANG {value}"
        self.write(command)

    @property
    def auto_range_enabled(self):
        """ A boolean property that controls the autorange state
        for the currently active function. """
        command = f"{self._get_function_range_prefix()}:RANG:AUTO?"
        return self.ask(command).strip() == "1"

    @auto_range_enabled.setter
    def auto_range_enabled(self, value):
        command = f"{self._get_function_range_prefix()}:RANG:AUTO {HP34401A.BOOL_MAPPINGS[value]}"
        self.write(command)

    @property
    def resolution(self):
        """ A property that controls the measurement resolution.
        Not valid for frequency, period, or ratio.
        Specify the resolution in the same units as the
        measurement function, not in number of digits.
        MIN selects the smallest value accepted, which gives the most resolution.
        MAX selects the largest value accepted which gives the least resolution. """
        command = f"{HP34401A.FUNCTIONS[self.function_]}:RES?"
        return float(self.ask(command))

    @resolution.setter
    def resolution(self, value):
        command = f"{HP34401A.FUNCTIONS[self.function_]}:RES {value}"
        self.write(command)

    @property
    def nplc(self):
        """ A float / string property that controls the integration time in
        number of power line cycles for the currently active function
        (the default is 10 PLC).
        Valid values: 0.02, 0.2, 1, 10, 100
        The strings "MIN" for 0.02 and "MAX" = 100 are also valid.
        This command is valid only for dc volts, ratio, dc current,
        2-wire ohms, and 4-wire ohms.
        """
        command = f"{HP34401A.FUNCTIONS[self.function_]}:NPLC?"
        return float(self.ask(command))

    @nplc.setter
    def nplc(self, value):
        command = f"{HP34401A.FUNCTIONS[self.function_]}:NPLC {value}"
        self.write(command)

    @property
    def gate_time(self):
        """ Select the gate time (or aperture time)
        for frequency or period measurements (the default is 0.1 seconds).
        Valid values: 0.01, 0.1, 1.
        Specifically:  10 ms (4.5 digits), 100 ms (default; 5.5 digits),
        or 1 second (6.5 digits). MIN = 0.01 seconds. MAX = 1 second. """
        command = f"{HP34401A.FUNCTIONS[self.function_]}:APER?"
        return float(self.ask(command))

    @gate_time.setter
    def gate_time(self, value):
        command = f"{HP34401A.FUNCTIONS[self.function_]}:APER {value}"
        self.write(command)

    detector_bandwidth = Instrument.control(
        "DET:BAND?", "DET:BAND %s",
        """ A float / string property that controls the lowest frequency
        expected in the input signal in Hertz.
        Valid values: 3, 20, 200, MIN, MAX
        """)

    autozero_enabled = Instrument.control(
        "ZERO:AUTO?", "ZERO:AUTO %s",
        """ A boolean property that controls the autozero state. """,
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True)

    def trigger_single_autozero(self):
        """ Triggers an autozero measurement.
        Consequent autozero measurements are disabled. """
        self.write("ZERO:AUTO ONCE")

    auto_input_impedance_enabled = Instrument.control(
        "INP:IMP:AUTO?", "INP:IMP:AUTO %s",
        """ A boolean property to enable or disable the automatic
        input resistance mode for dc voltage measurements.
        With AUTO OFF (default), the input resistance is fixed
        at 10 MΩ for all ranges. With AUTO ON, the input resistance is set to
        >10 GOhms for the 100 mV, 1 V, and 10 V ranges. """,
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True)

    terminals_used = Instrument.measurement(
        "ROUT:TERM?",
        """ Query the multimeter to determine if the front or rear input terminals
            are selected. Returns "FRONT" or "REAR". """,
        values={"FRONT": "FRON", "REAR": "REAR"},
        map_values=True)

    # Trigger related commands
    def init_trigger(self):
        """ This command changes the state of the triggering system
        from the "idle" state to the "wait-for-trigger" state.
        Measurements will begin when the specified trigger conditions
        are satisfied after this command is received """
        self.write("INIT")

    reading = Instrument.measurement(
        "READ?",
        """ The reading(s) of the currently selected function.
        Reading this property is equivalent to calling `init_trigger()`,
        waiting for completion and fetching the reading(s). """)

    trigger_source = Instrument.control(
        "TRIG:SOUR?", "TRIG:SOUR %s",
        """ A string property that controls the trigger source.
        Valid values: IMM, BUS, EXT
        The multimeter will accept a software (bus) trigger,
        an immediate internal trigger (this is the default source),
        or a hardware trigger from the rear-panel Ext Trig (external trigger) terminal. """)

    trigger_delay = Instrument.control(
        "TRIG:DEL?", "TRIG:DEL %s",
        """ A float / string property that controls the trigger delay in seconds.
        Valid values: 0 to 3600 seconds, "MIN" or "MAX". """)

    trigger_auto_delay_enabled = Instrument.control(
        "TRIG:DEL:AUTO?", "TRIG:DEL:AUTO %s",
        """ A boolean property that controls the automatic trigger delay state.
        If enabled, the delay is determined by function, range, integration time,
        and ac filter setting. Selecting a specific trigger delay value
        automatically turns off the automatic trigger delay. """,
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True)

    sample_count = Instrument.control(
        "SAMP:COUN?", "SAMP:COUN %s",
        """ A integer property that controls the number of samples to be taken
        for each trigger event. Valid values: 1 to 50000, "MIN" or "MAX". """)

    trigger_count = Instrument.control(
        "TRIG:COUN?", "TRIG:COUN %s",
        """ A integer property that controls the number of triggers the multimeter
        will accept before returning to the "idle" state.
        Valid values: 1 to 50000, "MIN", "MAX" or "INF".
        The INFinite parameter instructs the multimeter to continuously accept triggers
        (you must send a device clear to return to the "idle" state). """)

    stored_reading = Instrument.measurement(
        "FETCh?",
        """ This property returns the reading(s) currently stored in the
        multimeter's internal memory. Reading this property will NOT initialize a trigger.
        If you need that, use the `reading` property instead. """)

    # Display related commands
    display_enabled = Instrument.control(
        "DISP?", "DISP %s",
        """ A boolean property that controls the display state. """,
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True)

    displayed_text = Instrument.control(
        "DISP:TEXT?", "DISP:TEXT \"%s\"",
        """ A string property that controls the text that is displayed on the
        multimeter's display. The text can be up to 12 characters long;
        any additional characters are truncated my the multimeter. """,
        get_process=lambda x: x.strip('"'))

    # System related commands
    def beep(self):
        """ This command causes the multimeter to beep once. """
        self.write("SYST:BEEP")

    beeper_enabled = Instrument.control(
        "SYST:BEEP:STAT?", "SYST:BEEP:STAT %s",
        """ A boolean property that controls if the beeper is enabled. """,
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True)

    scpi_version = Instrument.measurement(
        "SYST:VERS?",
        """ Query the SCPI version of the multimeter. """)

    stored_readings_count = Instrument.measurement(
        "DATA:POIN?",
        """ Query the number of readings currently stored
        in the multimeter's internal memory. """)

    self_test_result = Instrument.measurement(
        "*TST?",
        """ A boolean property that, if read,
        initiates a self-test of the multimeter and returns the result. """)

    def _get_function_range_prefix(self):
        function_prefix = HP34401A.FUNCTIONS_WITH_RANGE[self.function_]
        if function_prefix in ["FREQ", "PER"]:
            function_prefix += ":VOLT"
        return function_prefix
