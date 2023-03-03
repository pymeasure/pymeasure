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
from pymeasure.instruments.teledyne.teledyne_oscilloscope import TeledyneOscilloscope, \
    TeledyneOscilloscopeChannel, _results_list_to_dict


class TeledyneMAUIChannel(TeledyneOscilloscopeChannel):
    """Base class for channels on a :class:`TeledyneMAUI` device."""

    # For some reason "20MHZ" is registered as "ON"
    BANDWIDTH_LIMITS = ["OFF", "ON", "200MHZ"]

    TRIGGER_SLOPES = {"negative": "NEG", "positive": "POS"}

    # Reset listed values for existing commands:
    bwlimit_values = BANDWIDTH_LIMITS

    def autoscale(self):
        """Perform auto-setup command for channel."""
        self.write("AUTO_SETUP FIND")

    @property
    def current_configuration(self):
        """ Read channel configuration as a dict containing the following keys:
            - "channel": channel number (int)
            - "attenuation": probe attenuation (float)
            - "bandwidth_limit": bandwidth limiting, parsed for this channel (str)
            - "coupling": "ac 1M", "dc 1M", "ground" coupling (str)
            - "offset": vertical offset (float)
            - "display": currently displayed (bool)
            - "volts_div": vertical divisions (float)
            - "trigger_coupling": trigger coupling can be "dc" "ac" "highpass" "lowpass" (str)
            - "trigger_level": trigger level (float)
            - "trigger_slope": trigger slope can be "negative" "positive" "window" (str)
        """
        ch_setup = {
            "channel": self.id,
            "attenuation": self.probe_attenuation,
            "bandwidth_limit": self.bwlimit[f"C{self.id}"],
            "coupling": self.coupling,
            "offset": self.offset,
            "display": self.display,
            "volts_div": self.scale,
            "trigger_coupling": self.trigger_coupling,
            "trigger_level": self.trigger_level,
            "trigger_slope": self.trigger_slope
        }
        return ch_setup


class TeledyneMAUI(TeledyneOscilloscope):
    """A base class for the MAUI-type of Teledyne oscilloscopes.

    This class is not exactly device specific. Nonetheless, it might already work out of the box and
    therefore this class not abstract.
    """

    channels = Instrument.ChannelCreator(TeledyneMAUIChannel, (1, 2, 3, 4))

    # Change listed values for existing commands:
    bwlimit_values = TeledyneMAUIChannel.BANDWIDTH_LIMITS
