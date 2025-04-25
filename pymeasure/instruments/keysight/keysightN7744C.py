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

import logging
from pymeasure.instruments import Instrument, SCPIUnknownMixin, Channel
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class MPPMChannel(Channel):
    """A channel of the voltage source."""

    wavelength = Channel.control(
        "SENSe{ch}:POWer:WAVelength?", "SENSe{ch}:POWer:WAVelength %gNM",
        """Control the sensor wavelength of this channel.""",
    )

    power = Channel.measurement(
        "READ{ch}:POWer?",
        """Measure the current power meter value of this channel.""",
    )

    power_unit = Channel.control(
        "SENSe{ch}:POWer:UNIT?", "SENSe{ch}:POWer:UNIT %g",
        """Control the sensor wavelength of this channel.""",
        validator=strict_discrete_set,
        map_values=True,
        values={'dBm': 0, 'Watt': 1}
    )

    range = Channel.control(
        "SENSe{ch}:POWer:RANGe?", "SENSe{ch}:POWer:RANGe %g",
        """Control the range setting for the channel.""",
        validator=strict_range,
        values=[-30, 10]
    )

    auto_range = Channel.control(
        "SENSe{ch}:POWer:RANGe:AUTO?", "SENSe{ch}:POWer:RANGe:AUTO %g",
        """Control whether automatic power ranging is being used by the channel.""",
        validator=strict_discrete_set,
        map_values=True,
        values={False: 0, True: 1}
    )

    averaging_time = Channel.control(
        "SENSe{ch}:POWer:ATIMe?", "SENSe{ch}:POWer:ATIMe %g",
        """Control the averaging time of the channel.""",
    )

    auto_gain = Channel.control(
        "SENSe{ch}:POWer:GAIN:AUTO?", "SENSe{ch}:POWer:GAIN:AUTO %g",
        """Control the Auto Gain of the channel.""",
        validator=strict_discrete_set,
        map_values=True,
        values={False: 0, True: 1}
    )

    zero = Channel.control(
        "SENSe{ch}:CORRection:COLLect:ZERO?", "SENSe{ch}:CORRection:COLLect:ZERO",
        """Control the electrical offsets of the channel.""",
    )

    state = Channel.control(
        "SENSe{ch}:FUNCtion:STATe?", "SENSe{ch}:FUNCtion:STATe %s",
        """Control the logging, MinMax, or stability data acquisition function mode.""",
        validator=strict_discrete_set,
        values=['LOGGing', 'LOGG', 'STABility', 'STAB', 'MINMax', 'MINM', 'STOP', 'START']
    )

    logging_parameters = Channel.control(
        "SENSe{ch}:FUNCtion:PARameter:LOGGing?",
        "SENSe{ch}:FUNCtion:PARameter:LOGGing %g,%gS",
        """Control the number of data points and the averaging time for the logging data 
        acquisition function."""
        # get_process=lambda v: tuple(float(x) for x in v.split(','))
    )


class KeysightN7744C(SCPIUnknownMixin, Instrument):
    """
    This represents the Keysight N7744C Optical Multiport Power Meter interface.

    .. code-block:: python

        mppm = KeysightN7744C(address)

    """

    def __init__(self, adapter, name="N7744C Optical Multiport Power Meter", **kwargs):
        super().__init__(
            adapter, name, **kwargs)

    channel_1 = Instrument.ChannelCreator(MPPMChannel, 1)
    channel_2 = Instrument.ChannelCreator(MPPMChannel, 2)
    channel_3 = Instrument.ChannelCreator(MPPMChannel, 3)
    channel_4 = Instrument.ChannelCreator(MPPMChannel, 4)

    zero_all = Instrument.control(
        "SENSe:CORRection:COLLect:ZERO:ALL?",
        "SENSe:CORRection:COLLect:ZERO:ALL",
        """Control the electrical offsets for all power meter channels."""
    )

    time = Instrument.control(
        "SYSTem:TIME?", "SYSTem:TIME %g,%g,%g",
        """Control the  the instrument’s internal time."""
        # get_process=lambda v: tuple(float(x) for x in v.split(','))
    )

    error = Instrument.measurement(
        "SYSTem:ERRor?", """Get the next error from the error queue."""
    )

    wavelength_all = Instrument.setting(
        "SENSe:POWer:WAVelength:ALL %gNM",
        """Control the sensor wavelength of this channel."""
    )

    def preset(self):
        """Sets the insrument to its standard settings. The stored settings are deleted."""
        self.write('SYSTem:PRESet')

    def reboot(self):
        """Reboots the instrument."""
        self.write('SYSTem:REBoot')
