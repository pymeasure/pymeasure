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

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_discrete_range, strict_discrete_set


def step_validator(step):
    """Creates a strict_discrete_range with the specified step"""
    return lambda x, y: strict_discrete_range(x, y, step)


class MainChannel(Channel):
    WAVEFORMS = {
        "SINE": 0,
        "SQUARE": 1,
        "PULSE": 2,
        "TRIANGLE": 3,
        "SAWTOOTH_RISE": 4,
        "SAWTOOTH_FALL": 5,
        "DC": 6,
        "PULSE_LORENTZ": 7,
        "MULTITONE": 8,
        "RANDOM_NOISE": 9,
        "ELECTROCARDIOGRAM": 10,
        "PULSE_TRAPEZ": 11,
        "PULSE_SINC": 12,
        "PULSE_NARROW": 13,
        "GAUSSIAN_NOISE": 14,
        "AMP_MOD": 15,
        "FREQ_MOD": 16,
        "ARB1": 17,
        "ARB2": 18,
        "ARB3": 19,
    }

    SWEEPMODES = {"LINEAR": 0, "LOG": 1}

    waveform = Instrument.setting(
        "{ch}w%i",
        """Set the waveform of the channel.

        The waveform must be one of the following:

        - SINE
        - SQUARE
        - PULSE
        - TRIANGLE
        - SAWTOOTH_RISE
        - SAWTOOTH_FALL
        - DC
        - PULSE_LORENTZ
        - MULTITONE
        - RANDOM_NOISE
        - ELECTROCARDIOGRAM
        - PULSE_TRAPEZ
        - PULSE_SINC
        - PULSE_NARROW
        - GAUSSIAN_NOISE
        - AMP_MOD
        - FREQ_MOD
        - ARB1
        - ARB2
        - ARB3
        """,
        validator=strict_discrete_set,
        map_values=True,
        values=WAVEFORMS,
    )

    frequency = Instrument.control(
        "{ch}\ncf",
        "{ch}f%.9i",
        "Control the frequency (Hz) of the channel.",
        validator=step_validator(1),
        values=(0, 100000000),
        set_process=lambda x: x * 100,
        get_process=lambda x: float(x.strip("cf")) / 100,
    )

    amplitude = Instrument.setting(
        "{ch}a%.1f",
        "Set the amplitude (V) of the channel.",
        validator=step_validator(0.1),
        values=(0.1, 20),
    )

    offset = Instrument.setting(
        "{ch}o%.1f",
        "Set the offset (V) of the channel",
        validator=step_validator(0.1),
        values=(-10, 10),
    )

    duty_cycle = Instrument.control(
        "{ch}\ncd",
        "{ch}d%i",
        "Control the duty cycle (percentage) of the channel",
        validator=step_validator(1),
        values=(1, 99),
        get_process=lambda x: float(x.strip("cd")),
    )

    sweep_time = Instrument.control(
        "{ch}\nct",
        "{ch}t%.2i",
        """Control the sweep time (s)""",
        validator=step_validator(1),
        values=(0, 99),
        get_process=lambda x: float(x.strip("ct")),
    )

    sweep_beginning_frequency = Instrument.setting(
        "{ch}b%.9i",
        """Set the sweep beginning frequency (Hz)""",
        validator=step_validator(1),
        values=(0, 100000000),
        set_process=lambda x: x * 100,
    )

    sweep_end_frequency = Instrument.setting(
        "{ch}e%.9i",
        """Set the sweep beginning frequency (Hz)""",
        validator=step_validator(1),
        values=(0, 100000000),
        set_process=lambda x: x * 100,
    )

    sweep_mode = Instrument.setting(
        "{ch}m%i",
        "Set the sweepmode (LINEAR or LOG).",
        validator=strict_discrete_set,
        map_values=True,
        values=SWEEPMODES,
    )

    def start_sweep(self):
        self.write("{ch}r1")

    def pause_sweep(self):
        self.write("{ch}r0")


class SubsidiaryChannel(Channel):
    WAVEFORMS = {
        "SINE": 0,
        "SQUARE": 1,
        "TRIANGLE": 2,
        "SAWTOOTH_RISE": 3,
        "SAWTOOTH_FALL": 4,
        "DC": 5,
        "PULSE_LORENTZ": 6,
        "MULTITONE": 7,
        "RANDOM_NOISE": 8,
        "ELECTROCARDIOGRAM": 9,
        "PULSE_TRAPEZ": 10,
        "PULSE_SINC": 11,
        "PULSE_NARROW": 12,
        "GAUSSIAN_NOISE": 13,
        "AMP_MOD": 14,
        "FREQ_MOD": 15,
        "ARB1": 16,
        "ARB2": 17,
        "ARB3": 18,
    }

    waveform = Instrument.setting(
        "{ch}w%i",
        """Set the waveform of the channel.

        The waveform must be one of the following:

        - SINE
        - SQUARE
        - TRIANGLE
        - SAWTOOTH_RISE
        - SAWTOOTH_FALL
        - DC
        - PULSE_LORENTZ
        - MULTITONE
        - RANDOM_NOISE
        - ELECTROCARDIOGRAM
        - PULSE_TRAPEZ
        - PULSE_SINC
        - PULSE_NARROW
        - GAUSSIAN_NOISE
        - AMP_MOD
        - FREQ_MOD
        - ARB1
        - ARB2
        - ARB3
        """,
        validator=strict_discrete_set,
        map_values=True,
        values=WAVEFORMS,
    )

    frequency = Instrument.control(
        "{ch}\ncf",
        "{ch}f%.9i",
        "Control the frequency (Hz) of the channel.",
        validator=step_validator(1),
        values=(0, 100000000),
        set_process=lambda x: x * 100,
        get_process=lambda x: float(x.strip("cf")) / 100,
    )

    amplitude = Instrument.setting(
        "{ch}a%.1f",
        "Set the amplitude (V) of the channel.",
        validator=step_validator(0.1),
        values=(0.1, 20),
    )

    offset = Instrument.setting(
        "{ch}o%.1f",
        "Set the offset (V) of the channel",
        validator=step_validator(0.1),
        values=(-10, 10),
    )

    duty_cycle = Instrument.control(
        "{ch}\ncd",
        "{ch}d%i",
        "Control the duty cycle (percentage) of the channel",
        validator=step_validator(1),
        values=(1, 99),
        get_process=lambda x: float(x.strip("cd")),
    )

    phase = Instrument.setting(
        "{ch}p%i",
        """Set the phase (deg) of the waveform""",
        validator=step_validator(1),
        values=(0, 360),
    )


class FY3200S(Instrument):
    """Class to control the Feeltech FY3200S arbitrary waveform generator"""

    def __init__(self, adapter, name: str = "FY3200s AWG", **kwargs):
        """Initialize the instrument with a SerialAdapter
        :param adapter: Adapter or string for the connection.
        :type adapter: SerialAdapter
        :param name: Instrument name
        :type name: str
        """
        super().__init__(adapter, name, includeSCPI=False, write_termination="\n", **kwargs)

    main_channel = Instrument.ChannelCreator(MainChannel, "b")
    subsidiary_channel = Instrument.ChannelCreator(SubsidiaryChannel, "d")

    frequency = Instrument.measurement(
        "ce",
        "Measure the exterior frequency (Hz).",
        get_process=lambda x: float(x.strip("ce")) / 100,
    )

    count = Instrument.measurement(
        "cc", "Measure the current value of the counter.", get_process=lambda x: int(x.strip("cc"))
    )

    def save(self, pos: int):
        """
        Save the current settings to a specified position.

        :param pos: The position to save the settings (must be an integer between 0 and 9).
        :type pos: int
        :raises ValueError: If the position is not in the range 0-9.
        """
        if pos not in range(10):
            raise ValueError("Save position must be an integer between 0 and 9")
        else:
            self.write("bs%i" % pos)

    def load(self, pos: int):
        """
        Load the settings from a specified position.

        :param pos: The position to load the settings from (must be an integer between 0 and 9).
        :type pos: int
        :raises ValueError: If the position is not in the range 0-9.
        """
        if pos not in range(10):
            raise ValueError("Load position must be an integer between 0 and 9")
        else:
            self.write("bl%i" % pos)

    @property
    def id(self):
        """Get the identification of the instrument."""
        return self.ask("a")
