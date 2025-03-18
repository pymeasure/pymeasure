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

from pymeasure.instruments import Instrument
from pymeasure.instruments.agilent import Agilent33500
from pymeasure.instruments.agilent.agilent33500 import Agilent33500Channel
from pymeasure.instruments.validators import strict_discrete_set, strict_range

WF_SHAPES = ["SIN", "SQU", "RAMP", "PULS", "NOIS", "DC", "USER"]
FREQUENCY_SIN_RANGE = [1e-6, 500e6]
FREQUENCY_RANGE = [1e-6, 330e6]
AMPLITUDE_RANGE = [0.05, 5]
OFFSET_RANGE = [-4.995, 4.995]
VOLTAGE_HIGH_RANGE = [-4.95, 5.0]
VOLTAGE_LOW_RANGE = [-5, 4.95]
SQUARE_DUTYCYCLE_RANGE = [0.0001515, 99.9998485]
PULSE_PERIOD_RANGE = [2e-9, 1e6]
PULSE_WIDTH_RANGE = [1.5e-9, 1e6]
PULSE_DUTYCYCLE_RANGE = [1.5e-1, 99.99]
PULSE_TRANSITION_RANGE = [1e-9, 1e3]
BURST_PERIOD = [3.03e-9, 1e6]
BURST_NCYCLES = [2, 2.147483647e9]
TRIGGER_COUNT = [1, 2.147483647e9]
LIMIT_HIGH_RANGE = [-9.99, 10]
LIMIT_LOW_RANGE = [-10, 9.99]
STATES = ["ON", "OFF"]
IMPEDANCE_RANGE = [3e-1, 1e6]
TRIGGER_MODES = ["IMM", "INT2", "EXT", "MAN"]


class Keysight81160AChannel(Agilent33500Channel):
    shape_values = WF_SHAPES
    shape_get_command = ":FUNC{ch}?"
    shape_set_command = ":FUNC{ch} %s"

    frequency_values = FREQUENCY_SIN_RANGE
    frequency_get_command = ":FREQ{ch}?"
    frequency_set_command = ":FREQ{ch} %f"

    amplitude_values = AMPLITUDE_RANGE
    amplitude_get_command = ":VOLT{ch}?"
    amplitude_set_command = ":VOLT{ch} %f"

    amplitude_unit_get_command = ":VOLT{ch}:UNIT?"
    amplitude_unit_set_command = ":VOLT{ch}:UNIT %s"

    offset_values = OFFSET_RANGE
    offset_get_command = ":VOLT{ch}:OFFS?"
    offset_set_command = ":VOLT{ch}:OFFS %f"

    voltage_high_values = VOLTAGE_HIGH_RANGE
    voltage_high_get_command = ":VOLT{ch}:HIGH?"
    voltage_high_set_command = ":VOLT{ch}:HIGH %f"

    voltage_low_values = VOLTAGE_LOW_RANGE
    voltage_low_get_command = ":VOLT{ch}:LOW?"
    voltage_low_set_command = ":VOLT{ch}:LOW %f"

    square_dutycycle_values = SQUARE_DUTYCYCLE_RANGE
    square_dutycycle_set_command = ":FUNC{ch}:SQU:DCYC %f"
    square_dutycycle_get_command = ":FUNC{ch}:SQU:DCYC?"

    ramp_symmetry_set_command = ":FUNC{ch}:RAMP:SYMM %f"
    ramp_symmetry_get_command = ":FUNC{ch}:RAMP:SYMM?"

    pulse_period_values = PULSE_PERIOD_RANGE
    pulse_period_set_command = ":PULS:PER{ch} %e"
    pulse_period_get_command = ":PULS:PER{ch}?"

    pulse_hold_set_command = ":PULS:HOLD{ch} %s"
    pulse_hold_get_command = ":PULS:HOLD{ch}?"

    pulse_width_values = PULSE_WIDTH_RANGE
    pulse_width_set_command = ":PULS:WIDT{ch} %e"
    pulse_width_get_command = ":PULS:WIDT{ch}?"

    pulse_dutycycle_values = PULSE_DUTYCYCLE_RANGE
    pulse_dutycycle_set_command = ":PULS:DCYC{ch} %f"
    pulse_dutycycle_get_command = ":PULS:DCYC{ch}?"

    pulse_transition_values = PULSE_TRANSITION_RANGE
    pulse_transition_set_command = ":FUNC{ch}:PULS:TRAN %e"
    pulse_transition_get_command = ":FUNC{ch}:PULS:TRAN?"

    output_load_values = IMPEDANCE_RANGE
    output_load_set_command = ":OUTP{ch}:LOAD %e"
    output_load_get_command = ":OUTP{ch}:LOAD?"

    burst_state_values = STATES
    burst_state_set_command = ":BURS{ch}:STAT %s"
    burst_state_get_command = ":BURS{ch}:STAT?"

    burst_mode_set_command = ":BURS{ch}:MODE %s"
    burst_mode_get_command = ":BURS{ch}:MODE?"

    burst_period_values = BURST_PERIOD
    burst_period_set_command = ":BURS{ch}:INT:PER %e"
    burst_period_get_command = ":BURS{ch}:INT:PER?"

    burst_ncycles_values = BURST_NCYCLES
    burst_ncycles_set_command = ":BURS{ch}:NCYC %d"
    burst_ncycles_get_command = ":BURS{ch}:NCYC?"

    limit_state = Instrument.control(
        ":VOLT{ch}:LIM:STAT?",
        ":VOLT{ch}:LIM:STAT %s",
        """ Control the limit state (string).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0},
        dynamic=True,
    )

    limit_high = Instrument.control(
        ":VOLT{ch}:LIM:HIGH?",
        ":VOLT{ch}:LIM:HIGH %f",
        """ Control the high-level voltage limit (float).""",
        validator=strict_range,
        values=LIMIT_HIGH_RANGE,
        dynamic=True,
    )

    limit_low = Instrument.control(
        ":VOLT{ch}:LIM:LOW?",
        ":VOLT{ch}:LIM:LOW %f",
        """ Control the low-level voltage limit (float).""",
        validator=strict_range,
        values=LIMIT_LOW_RANGE,
        dynamic=True,
    )

    memory_free = Instrument.measurement(
        ":DATA{ch}:NVOL:FREE?",
        """ Get the number of free non-volatile memory slots to store user waveforms (int).""",
        dynamic=True,
    )

    coupling = Instrument.control(
        ":TRAC:CHAN{ch}?",
        ":TRAC:CHAN{ch} %s",
        """ Control the channel coupling (string). ``:TRAC:CHAN1 ON`` to copy values from
        channel 1 to channel 2.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0},
        dynamic=True,
    )

    waveforms = Instrument.measurement(
        ":DATA{ch}:NVOL:CAT?",
        """ Get the available user waveforms in memory (list[str]).""",
        preprocess_reply=lambda v: v.replace('"', "").replace("\n", ""),
        dynamic=True,
    )

    volatile_waveform = Instrument.setting(
        ":DATA{ch}:DAC VOLATILE, %s",
        """ Set the volatile waveform data (str).""",
        dynamic=True,
    )

    trigger_mode = Instrument.control(
        ":ARM:SOUR{ch}?",
        ":ARM:SOUR{ch} %s",
        """ Control the triggering mode (string).""",
        validator=strict_discrete_set,
        values=TRIGGER_MODES,
        dynamic=True,
    )

    trigger_count = Instrument.control(
        ":TRIG{ch}:COUN?",
        ":TRIG{ch}:COUN %d",
        """ Control the number of cycles to be output when a burst is triggered (int). Enable burst state if number > 1.
        
        Short form of burst_ncycles and burst_state = True""",
        validator=strict_range,
        values=TRIGGER_COUNT,
        dynamic=True,
    )

    def save_waveform(self, waveform, name):
        """
        Save a waveform to the generator's nonvolatile memory.

        :param waveform: The waveform data.
        :param name: The name of the waveform.
        """
        self.volatile_waveform = waveform
        self.write(f":DATA{self.id}:COPY {name}, VOLATILE")

    def delete_waveform(self, name):
        """
        Delete a waveform from the generator's nonvolatile memory.

        :param name: The name of the waveform.
        """
        self.write(f":DATA{self.id}:DEL {name.upper()}")


class Keysight81160A(Agilent33500):
    ch_1 = Instrument.ChannelCreator(Keysight81160AChannel, 1)
    ch_2 = Instrument.ChannelCreator(Keysight81160AChannel, 2)

    shape_values = WF_SHAPES
    frequency_values = FREQUENCY_SIN_RANGE
    amplitude_values = AMPLITUDE_RANGE
    offset_values = OFFSET_RANGE
    voltage_high_values = VOLTAGE_HIGH_RANGE
    voltage_low_values = VOLTAGE_LOW_RANGE
    square_dutycycle_values = SQUARE_DUTYCYCLE_RANGE
    pulse_period_values = PULSE_PERIOD_RANGE
    pulse_period_get_command = ":PULS:PER?"
    pulse_period_set_command = ":PULS:PER %e"
    pulse_width_values = PULSE_WIDTH_RANGE
    pulse_dutycycle_values = PULSE_DUTYCYCLE_RANGE
    pulse_transition_values = PULSE_TRANSITION_RANGE
    pulse_transition_set_command = ":FUNC:PULS:TRAN %e"
    burst_period_values = BURST_PERIOD
    burst_ncycles_values = BURST_NCYCLES
    arb_file_get_command = ":FUNC:USER?"
