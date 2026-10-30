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
import logging
from enum import Enum
from pymeasure.instruments import Instrument, Channel
from pymeasure.adapters import SerialAdapter


from pymeasure.instruments.validators import (
    strict_discrete_set,
    truncated_range,
    strict_range,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class CustomEnum(Enum):
    """Provides additional methods to IntEnum:
    * Conversion to string automatically replaces '_' with ' ' in names
      and converts to title case
    * get classmethod to get enum reference with name or integer
    .. automethod:: __str__
    """

    def __str__(self):
        """Gives title case string of enum value."""
        return str(self.value).replace("_", " ")
        # str() conversion just because of pylint bug

    @classmethod
    def get(cls, input_value):
        """Gives Enum member by specifying name or value.
        Args:
            input_value (str|int): Enum name or value
        Returns:
            _type_: enum member
        """

        if isinstance(input_value, int):
            return cls(input_value)
        else:
            return cls[input_value.upper()]


class AWGChannel(Channel):
    """Implementation of a AWG channel."""

    waveform_type = Instrument.control(
        "R<ch>W",
        "W<ch>W%s",
        """ Waveform Type based on the enum.""",
        validator=strict_discrete_set,
        values="FeelTechFY6800.WaveformType",
    )

    def insert_id(self, command):
        return command.replace("<ch>", "F" if self.id == 2 else "M")


class FeelTechFY6800(Instrument):
    class WaveformType(CustomEnum):
        """Parameter format in a data file"""

        SINE = "00"
        RECTANGULAR = "01"
        TRIANGLE = "02"
        RISE_SAWTOOTH = "03"
        FALL_SAWTOOTH = "04"
        STEP_TRIANGLE = "05"
        POSITIVE_STEP = "06"
        INVERSE_STEP = "07"
        POSITIVE_EXPONENT = "08"
        INVERSE_EXPONENT = "09"
        POSITIVE_FALLING_EXPONENT = "10"
        INVERSE_FALLING_EXPONENT = "11"
        POSITIVE_LOG = "12"
        INVERSE_LOG = "13"
        POSITIVE_FALLING_LOG = "14"
        INVERSE_FALLING_LOG = "15"
        POSITIVE_HALF_WAVE = "16"
        NEGATIVE_HALF_WAVE = "17"
        POSITIVE_HALF_WAVE_RECT = "18"
        NEGATIVE_HALF_WAVE_RECT = "19"
        LORENZ_PULSE = "20"
        MULTITONE = "21"
        NOISE = "22"
        ECG = "23"
        TRAPEZOIDAL_PULSE = "24"
        SINC_PULSE = "25"
        NARROW_PULSE = "26"
        GAUS_WHITE_NOISE = "27"
        AM = "28"
        FM = "29"
        LINEAR_FM = "30"

    def __init__(self, adapter=SerialAdapter, name="FeelTech FY6800", includeSCPI=True, **kwargs):
        super().__init__(adapter, name, includeSCPI, **kwargs)

    channels = Instrument.ChannelCreator(AWGChannel, (1, 2))
