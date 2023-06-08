#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

from numpy import arange

from pymeasure.instruments.validators import strict_discrete_set, strict_range
from pymeasure.instruments import Instrument, Channel

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

try:
    from enum import StrEnum
except ImportError:
    class StrEnum(str, Enum):
        """Until StrEnum is broadly available / pymeasure relies on python <=
        3.10.x."""

        def __str__(self):
            return self.value


class AcquisitionState(StrEnum):
    """Enumeration to represent the different acquisition states"""

    #: Starts the acquisition or indicates that it is running
    Run = "RUN"

    #: Stops the acquisition or indicates the stop of an acquisition
    Stop = "STOP"

    #: Indicates a completed acquisition
    Complete = "COMP"

    #: Immediate interrupt of current acquisition or indicates a finished but interrupted
    # acquisition
    Break = "BRE"


class Coupling(StrEnum):
    """Enumeration to represent the different coupling modes"""

    #: DC coupling passes the input signal unchanged.
    DC = "DCL"

    #: Removes the DC offset voltage from the input signal.
    AC = "ACL"

    #: Connection to a virtual ground. All channel data is set to o V.
    GND = "GND"


class Bandwidth(StrEnum):
    """Enumeration to represent the different bandwidth limitation possibilities"""

    #: Use full bandwidth.
    Full = "FULL"

    #: Limit to 20 MHz. Higher frequencies are removed to reduce noise.
    B20_MHz = "B20"


class RTB200XAnalogChannel(Channel):
    """
    One RTB2000 series oscilloscope channel
    """

    state = Channel.control(
        "CHANnel{ch}:STATe?", "CHANnel{ch}:STATe %s",
        """
        Control the channel signal. 
        Switch it either on or off.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", False: "OFF"},
        cast=str
    )

    scale = Channel.control(
        "CHANnel{ch}:SCALe?", "CHANnel{ch}:SCALe %g",
        """
        Control the vertical scale for this channel.
        """,
        validator=strict_range,
        values=[1e-3, 10]
    )

    range = Channel.control(
        "CHANnel{ch}:RANGe?", "CHANnel{ch}:RANGe %g",
        """
        Control the voltage range across the all vertical divisions of the diagram. Use the command
        alternatively instead :attr:`scale`
        """,
        validator=strict_range,
        values=[8e-3, 80]
    )

    position = Channel.control(
        "CHANnel{ch}:POSition?", "CHANnel{ch}:POSition %g",
        """
        Control the vertical position of the waveform in divisions.
        """,
        validator=strict_range,
        values=[-5, 5]
    )

    offset = Channel.control(
        "CHANnel{ch}:OFFSet?", "CHANnel{ch}:OFFSet %g",
        """
        Control the offset voltage, which is subtracted to correct an offset-affected signal.
        """
    )

    coupling = Channel.control(
        "CHANnel{ch}:COUPling?", "CHANnel{ch}:COUPling %s",
        """
        Control the connection of the indicated channel signal - coupling and termination.
        """,
        validator=strict_discrete_set,
        values=[e for e in Coupling]
    )

    bandwidth = Channel.control(
        "CHANnel{ch}:BANDwidth?", "CHANnel{ch}:BANDwidth %s",
        """
        Control the bandwidth limit for the indicated channel.
        """,
        validator=strict_discrete_set,
        values=[e for e in Bandwidth]
    )

    polarity_inversion_active = Channel.control(
        "CHANnel{ch}:POLarity?", "CHANnel{ch}:POLarity %s",
        """
        Control the inversion of the signal amplitude.

        To invert means to reflect the voltage values of all signal components against the ground
        level. Inversion affects only the display of the signal but not the trigger.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: "INV", False: "NORM"},
        cast=str
    )

    skew = Channel.control(
        "CHANnel{ch}:SKEW?", "CHANnel{ch}:SKEW %g",
        """
        Control a delay for the selected channel.
        
        Deskew compensates delay differences between channels caused by the different
        length of cables, probes, and other sources. Correct deskew values are important for
        accurate triggering.
        """
    )


class RTB200X(Instrument):
    """
    Represents a Rohde & Schwarz RTB2000 series oscilloscope.

    All physical values that can be set can either be as a string of a value
    and a unit (e.g. "1.2 GHz") or as a float value in the base units (Hz,
    dBm, etc.).
    """

    def __init__(self, adapter, name="Rohde&Schwarz RTB200X", **kwargs):
        super().__init__(
            adapter, name, includeSCPI=True, **kwargs
        )

    def autoscale(self):
        """
        Performs an autoset process for analog channels: analyzes the enabled analog channel
        signals, and adjusts the horizontal, vertical, and trigger settings to display stable
        waveforms
        """
        self.write("AUToscale")

    acquisition_state = Instrument.control(
        "ACQuire:STATe?", "ACQuire:STATe %s",
        """
        Control the acquisition state of the instrument
        """,
        validator=strict_discrete_set,
        values=[e for e in AcquisitionState]
    )

    def activate_analog_channels(self):
        """
        Switches all analog channels on
        """
        self.write("CHANNEL1:AON")

    def deactivate_analog_channels(self):
        """
        Switches all analog channels off.
        """
        self.write("CHANNEL1:AOFF")


class RTB2004(RTB200X):
    analog = Instrument.ChannelCreator(
        RTB200XAnalogChannel,
        (1, 2, 3, 4),
        prefix="ch")


class RTB2002(RTB200X):
    analog = Instrument.ChannelCreator(
        RTB200XAnalogChannel,
        (1, 2),
        prefix="ch")
