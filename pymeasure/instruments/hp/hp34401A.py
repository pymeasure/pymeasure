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

from warnings import warn
from pymeasure.instruments import Instrument, SCPIUnknownMixin
from pymeasure.instruments.validators import strict_discrete_set


deprecated_text = """

.. deprecated:: 0.12 Use the :code:`function_` and :code:`reading` properties instead.
"""


def _deprecation_warning(property_name):
    def func(x):
        warn(f'Deprecated property name "{property_name}", use the "function_" '
             'and "reading" properties instead.', FutureWarning)
        return x
    return func


class HP34401A(SCPIUnknownMixin, Instrument):
    """ Represents the HP / Agilent / Keysight 34401A Multimeter and
    provides a high-level interface for interacting with the instrument.

    .. code-block:: python

        dmm = HP34401A("GPIB::1")
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

    # Log a deprecated warning for the old function property
    voltage_ac = Instrument.measurement("MEAS:VOLT:AC? DEF,DEF",
                                        "AC voltage, in Volts" + deprecated_text,
                                        get_process=_deprecation_warning('voltage_ac'))

    current_dc = Instrument.measurement("MEAS:CURR:DC? DEF,DEF",
                                        "DC current, in Amps" + deprecated_text,
                                        get_process=_deprecation_warning('current_dc'))

    current_ac = Instrument.measurement("MEAS:CURR:AC? DEF,DEF",
                                        "AC current, in Amps" + deprecated_text,
                                        get_process=_deprecation_warning('current_ac'))

    resistance = Instrument.measurement("MEAS:RES? DEF,DEF",
                                        "Resistance, in Ohms" + deprecated_text,
                                        get_process=_deprecation_warning('resistance'))

    resistance_4w = Instrument.measurement(
        "MEAS:FRES? DEF,DEF",
        "Four-wires (remote sensing) resistance, in Ohms" + deprecated_text,
        get_process=_deprecation_warning('resistance_4w'))

    function_ = Instrument.control(
        "FUNC?", "FUNC \"%s\"",
        """Control the measurement function.

        Allowed values: "DCV", "DCV_RATIO", "ACV", "DCI", "ACI",
        "R2W", "R4W", "FREQ", "PERIOD", "CONTINUITY", "DIODE".""",
        validator=strict_discrete_set,
        values=FUNCTIONS,
        map_values=True,
        get_process=lambda v: v.strip('"'),
    )

    range_ = Instrument.control(
        "{function_prefix_for_range}:RANG?", "{function_prefix_for_range}:RANG %s",
        """Control the range for the currently active function.

        For frequency and period measurements, ranging applies to
        the signal's input voltage, not its frequency""",
    )

    autorange = Instrument.control(
        "{function_prefix_for_range}:RANG:AUTO?",
        "{function_prefix_for_range}:RANG:AUTO %d",
        """Control the autorange state for the currently active function.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    resolution = Instrument.control(
        "{function}:RES?", "{function}:RES %g",
        """Control the resolution of the measurements.

        Not valid for frequency, period, or ratio.
        Specify the resolution in the same units as the
        measurement function, not in number of digits.
        Results in a "Settings Conflict" error if autorange is enabled.
        MIN selects the smallest value accepted, which gives the most resolution.
        MAX selects the largest value accepted which gives the least resolution.""",
    )

    nplc = Instrument.control(
        "{function}:NPLC?", "{function}:NPLC %s",
        """Control the integration time in number of power line cycles (NPLC).

        Valid values: 0.02, 0.2, 1, 10, 100, "MIN", "MAX".
        This command is valid only for dc volts, ratio, dc current,
        2-wire ohms, and 4-wire ohms.""",
        validator=strict_discrete_set,
        values=[0.02, 0.2, 1, 10, 100, "MIN", "MAX"],
    )

    gate_time = Instrument.control(
        "{function}:APER?", "{function}:APER %s",
        """Control the gate time (or aperture time) for frequency or period measurements.

        Valid values: 0.01, 0.1, 1, "MIN", "MAX".
        Specifically:  10 ms (4.5 digits), 100 ms (default; 5.5 digits),
        or 1 second (6.5 digits).""",
        validator=strict_discrete_set,
        values=[0.01, 0.1, 1, "MIN", "MAX"],
    )

    detector_bandwidth = Instrument.control(
        "DET:BAND?", "DET:BAND %s",
        """Control the lowest frequency expected in the input signal in Hertz.

        Valid values: 3, 20, 200, "MIN", "MAX".""",
        validator=strict_discrete_set,
        values=[3, 20, 200, "MIN", "MAX"],
    )

    autozero_enabled = Instrument.control(
        "ZERO:AUTO?", "ZERO:AUTO %s",
        """Control the autozero state.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    def trigger_single_autozero(self):
        """Trigger an autozero measurement.

        Consequent autozero measurements are disabled."""
        self.write("ZERO:AUTO ONCE")

    auto_input_impedance_enabled = Instrument.control(
        "INP:IMP:AUTO?", "INP:IMP:AUTO %s",
        """Control if automatic input resistance mode is enabled.

        Only valid for dc voltage measurements.
        When disabled (default), the input resistance is fixed
        at 10 MOhms for all ranges. With AUTO ON, the input resistance is set to
        >10 GOhms for the 100 mV, 1 V, and 10 V ranges.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    terminals_used = Instrument.measurement(
        "ROUT:TERM?",
        """Query the multimeter to determine if the front or rear input terminals
        are selected.

        Returns "FRONT" or "REAR".""",
        values={"FRONT": "FRON", "REAR": "REAR"},
        map_values=True,
    )

    # Trigger related commands
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

    remote_lock_enabled = Instrument.control(
        "SYST: ", "SYST:%s",
        """Control whether the beeper is enabled.""",
        validator=strict_discrete_set,
        values={True: "RWL", False: "LOC"},
        map_values=True,
    )

    def beep(self):
        """This command causes the multimeter to beep once."""
        self.write("SYST:BEEP")

    beeper_enabled = Instrument.control(
        "SYST:BEEP:STAT?", "SYST:BEEP:STAT %s",
        """Control whether the beeper is enabled.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    scpi_version = Instrument.measurement(
        "SYST:VERS?",
        """The SCPI version of the multimeter.""",
    )

    stored_readings_count = Instrument.measurement(
        "DATA:POIN?",
        """The number of readings currently stored in the internal memory.""",
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
