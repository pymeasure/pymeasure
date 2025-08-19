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

import numpy as np

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
BOOLEANS = [True, False]
IMPEDANCE_RANGE = [3e-1, 1e6]
TRIGGER_MODES = ["IMM", "INT2", "EXT", "MAN"]
MAX_VOLTAGE = 5.0
SIN_AMPL_BORDER = 3.0
MAX_DAC_VALUE = 8191


class Keysight81160AChannel(Agilent33500Channel):
    """
    Represent the Keysight 81160A channel and provide a high-level interface for interacting with
    the instrument channels.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._waveform_volatile = None

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

    burst_state_values = BOOLEANS
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

    limit_state_enabled = Instrument.control(
        ":VOLT{ch}:LIM:STAT?",
        ":VOLT{ch}:LIM:STAT %s",
        """Control whether the state limit is enabled (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    limit_high = Instrument.control(
        ":VOLT{ch}:LIM:HIGH?",
        ":VOLT{ch}:LIM:HIGH %f",
        """Control the high-level voltage limit in Volts (float).""",
        validator=strict_range,
        values=LIMIT_HIGH_RANGE,
        dynamic=True,
    )

    limit_low = Instrument.control(
        ":VOLT{ch}:LIM:LOW?",
        ":VOLT{ch}:LIM:LOW %f",
        """Control the low-level voltage limit in Volts (float).""",
        validator=strict_range,
        values=LIMIT_LOW_RANGE,
        dynamic=True,
    )

    free_memory_slots = Instrument.measurement(
        ":DATA{ch}:NVOL:FREE?",
        """Get the number of free non-volatile memory slots to store user waveforms (int).""",
    )

    coupling_enabled = Instrument.control(
        ":TRAC:CHAN{ch}?",
        ":TRAC:CHAN{ch} %s",
        """Control whether the channel coupling is enabled (bool). 'True' to copy values from this
        channel to another one.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    waveforms = Instrument.measurement(
        ":DATA{ch}:NVOL:CAT?",
        """Get the available user waveforms in memory (list[str]).""",
        preprocess_reply=lambda v: v.replace('"', "").replace("\n", ""),
    )

    trigger_mode = Instrument.control(
        ":ARM:SOUR{ch}?",
        ":ARM:SOUR{ch} %s",
        """Control the triggering mode (string, strictly 'IMM', 'INT2', 'EXT' or 'MAN').""",
        validator=strict_discrete_set,
        values=TRIGGER_MODES,
        dynamic=True,
    )

    trigger_count = Instrument.control(
        ":TRIG{ch}:COUN?",
        ":TRIG{ch}:COUN %d",
        """Control the number of cycles to be output when a burst is triggered (int). Enable burst
        state if number > 1.

        Short form of burst_ncycles and burst_state = True""",
        validator=strict_range,
        values=TRIGGER_COUNT,
        dynamic=True,
    )

    def _preprocess_waveform(self, data):
        """
        Convert a waveform data to int values (from -'MAX_DAC_VALUE' to 'MAX_DAC_VALUE').

        :param data: waveform voltage data (array-like).
        :return: waveform voltage data as int values (array-like).
        """
        data_normed = data / data.max()
        data_int = np.round(data_normed * MAX_DAC_VALUE).astype(int)

        return data_int

    @property
    def waveform_volatile(self):
        """
        Get volatile waveform data.

        Warning: This property may not reflect the current device volatile waveform. It only returns
        the waveform previously set via this driver. If the device has been power-cycled, modified
        externally, or if no waveform was set, the returned value may be invalid or None.

        :return: waveform data (array-like) or None if not set.
        """
        return self._waveform_volatile

    @waveform_volatile.setter
    def waveform_volatile(self, waveform):
        """
        Set volatile waveform data for arbitrary waveform generation.

        :param waveform: The waveform data to be set (array-like).
        """
        self._waveform_volatile = np.array(waveform, dtype=np.float64)
        waveform_int = self._preprocess_waveform(self._waveform_volatile)
        self.write_binary_values(
            command=f":DATA{self.id}:DAC VOLATILE,",
            values=waveform_int,
            datatype="h",
            is_big_endian=True,
        )

    def save_waveform(self, waveform, name):
        """
        Save a waveform to the generator's nonvolatile memory.

        :param waveform: The waveform data.
        :param name: The name that will be used to identify the waveform in memory,
            up to 12 characters. The first character must be a letter (A-Z), but the remaining
            characters can be numbers (0-9) or the underscore character ('_').
            Blank spaces are not allowed.
        """
        self.waveform_volatile = waveform
        self.write(f":DATA{self.id}:COPY {name}, VOLATILE")

    def delete_waveform(self, name):
        """
        Delete a waveform from the generator's nonvolatile memory.

        :param name: The name of the user-defined waveform to be deleted.
        """
        self.write(f":DATA{self.id}:DEL {name.upper()}")

    def apply_dc(self, voltage):
        """
        Apply a DC voltage.

        :param voltage: Voltage to be applied (float).
        """
        self.write(f":APPL{self.id}:DC DEF, DEF, {voltage}")

    def apply_noise(self, amplitude, offset):
        """
        Apply noise to the output.

        :param amplitude: The amplitude of the noise (float).
        :param offset: The offset voltage (float).
        """
        self._check_voltages(amplitude, offset)
        self.write(f":APPL{self.id}:NOIS DEF, {amplitude}, {offset}")

    def apply_pulse(self, frequency, amplitude, offset):
        """
        Apply a pulse waveform.

        :param frequency: Frequency of the pulse (float).
        :param amplitude: Amplitude of the pulse (float).
        :param offset: Offset voltage (float).
        """
        self._check_voltages(amplitude, offset)
        self.write(f":APPL{self.id}:PULS {frequency}, {amplitude}, {offset}")

    def apply_sin(self, frequency, amplitude, offset):
        """
        Apply a sine waveform.

        :param frequency: Frequency of the sine wave (float).
        :param amplitude: Amplitude of the sine wave (float).
        :param offset: Offset voltage (float).
        """
        self._check_voltages(amplitude, offset)
        self._check_sin_params(frequency, amplitude)
        self.write(f":APPL{self.id}:SIN {frequency}, {amplitude}, {offset}")

    def apply_square(self, frequency, amplitude, offset):
        """
        Apply a square waveform.

        :param frequency: Frequency of the square wave (float).
        :param amplitude: Amplitude of the square wave (float).
        :param offset: Offset voltage (float).
        """
        self._check_voltages(amplitude, offset)
        self.write(f":APPL{self.id}:SQU {frequency}, {amplitude}, {offset}")

    def apply_user_waveform(self, frequency, amplitude, offset):
        """
        Apply a user-defined waveform.

        :param frequency: Frequency of the user waveform (float).
        :param amplitude: Amplitude of the user waveform (float).
        :param offset: Offset voltage (float).
        """
        self._check_voltages(amplitude, offset)
        self.write(f":APPL{self.id}:USER {frequency}, {amplitude}, {offset}")

    def _check_voltages(self, amplitude, offset):
        if abs(amplitude) + abs(offset) > MAX_VOLTAGE:
            raise ValueError(f"Amplitude + offset exceed maximal voltage of {MAX_VOLTAGE} V.")

    def _check_sin_params(self, frequency, amplitude):
        if frequency > FREQUENCY_RANGE[-1] and amplitude > SIN_AMPL_BORDER:
            raise ValueError(
                f"Frequency of higher than {FREQUENCY_RANGE[-1]} Hz is only supported for sin with"
                + f" amplitude below {SIN_AMPL_BORDER} V."
            )


class Keysight81160A(Agilent33500):
    """
    Represent the Keysight 81160A and provide a high-level interface for interacting with
    the instrument.

    .. code-block:: python

        generator = Keysight81160A("GPIB::1")        # Replace with your device address
        generator.reset()                            # Reset the generator to default settings

        generator.shape = "SIN"                      # Set default channel output shape to sine
        generator.channels[1].shape = "SIN"          # Set channel 1 output signal shape to sine
        generator.frequency = 1e3                    # Set default channel output frequency to 1 kHz
        generator.channels[1].frequency = 1e3        # Set channel 1 output frequency to 1 kHz
        generator.channels[2].amplitude = 5          # Set channel 2 output amplitude to 5 Vpp
        generator.channels[2].offset = 0.5           # Set channel 2 output offset to 0.5 V
        generator.channels[2].output = True          # Enable channel 2 output

        # Output a square wave at 1 kHz with 5 Vpp and 0.5 V offset
        generator.channels[2].apply_square(1e3, 5, 0)

        ch1 = generator.channels[1]                  # Short form for channel 1
        waveform = [-2.0, -1.5, 0.0, 1.5, 2.0]       # Define a user-defined waveform in Volts
        ch1.waveform_volatile = waveform             # Set user-defined waveform to volatile memory
        print(f"{ch1.free_memory_slots} slots free") # Get number of slots in non-volatile memory
        ch1.save_waveform(waveform, "test")          # Save the waveform to non-volatile memory
        ch1.shape = "USER"                           # Set channel 1 shape to user-defined
        ch1.trigger_mode = "MAN"                     # Set trigger mode to manual
        ch1.trigger_count = 2                        # Set number of cycles to be generated to 2
        ch1.output = True                            # Enable channel 1 output
        generator.trigger()                          # Trigger the generator to output the waveform
        ch1.delete_waveform("test")                  # Delete the waveform from non-volatile memory

    """

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
