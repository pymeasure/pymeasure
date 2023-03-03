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

import re

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from pymeasure.instruments.lecroy.lecroyT3DSO1204 import (
    LeCroyT3DSO1204,
    ScopeChannel as LeCroyT3DSO1204ScopeChannel,
)


def _channel_results_to_dict(results):
    """Turn a per-channel result list into a more convenient dict.

    E.g. turn ['C1', 'OFF', 'C2', 'OFF', 'C3', 'OFF', 'C4', 'OFF'] into
    {'C1': 'OFF', 'C2': 'OFF', 'C3': 'OFF', 'C4': 'OFF'}
    """
    keys = results[::2]
    values = results[1::2]
    return dict(zip(keys, values))


def _remove_unit(value):
    """Remove a unit from the returned string and cast to float."""
    if value.endswith(" V"):
        value = value[:-2]

    return float(value)


class ScopeChannel(LeCroyT3DSO1204ScopeChannel):
    """Extended Channel object for the HDO6xxx."""

    # For some reason "20MHZ" is registered as "ON"
    _BANDWIDTH_LIMITS = ["OFF", "ON", "200MHZ"]

    _TRIGGER_SLOPES = {"negative": "NEG", "positive": "POS"}

    @property
    def trigger_level2(self):
        raise NotImplementedError("Property is not available on this device")

    @property
    def skew_factor(self):
        raise NotImplementedError("Property is not available on this device")

    @property
    def unit(self):
        raise NotImplementedError("Property is not available on this device")

    @property
    def invert(self):
        # There is checkbox on the oscilloscope labeled "Invert", but
        # I cannot find a Visa command to match
        raise NotImplementedError("Property is not available on this device")

    bwlimit = Instrument.control(
        "BWL?", "BWL %s",
        """
        Sets bandwidth limit for this channel.
        
        The current bandwidths can only be read back for all channels at once!
        """,
        validator=strict_discrete_set,
        values=_BANDWIDTH_LIMITS,
        get_process=_channel_results_to_dict,
    )

    trigger_level = Instrument.control(
        "TRLV?", "TRLV %.2EV",
        """ A float parameter that sets the trigger level voltage for the active trigger source.
            When there are two trigger levels to set, this command is used to set the higher
            trigger level voltage for the specified source. :attr:`trigger_level2` is used to set
            the lower trigger level voltage.
            When setting the trigger level it must be divided by the probe attenuation. This is
            not documented in the datasheet and it is probably a bug of the scope firmware.
            An out-of-range value will be adjusted to the closest legal value.
        """,
        get_process=_remove_unit,
    )

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

        bwlimits = self.bwlimit  # Result only exists for all channels

        ch_setup = {
            "channel": self.id,
            "attenuation": self.probe_attenuation,
            "bandwidth_limit": bwlimits[f"C{self.id}"],
            "coupling": self.coupling,
            "offset": self.offset,
            "display": self.display,
            "volts_div": self.scale,
            "trigger_coupling": self.trigger_coupling,
            "trigger_level": self.trigger_level,
            "trigger_slope": self.trigger_slope
        }
        return ch_setup


class TeledyneHDO6xxx(LeCroyT3DSO1204):
    """Reference to the Teledyne-Lecroy HDo6xxx class of oscilloscopes.

    Most functionality is inherited from :class:`LeCroyT3DSO1204`.

    It is unclear which manual details the exact API of the oscilloscope, but
    this file seems very close: "WavePro Remote Control Manual" (`link`_).
    The file is from 2002, but it still seems to apply to this model.

    .. _: https://cdn.teledynelecroy.com/files/manuals/wp_rcm_revc.pdf
    """

    channels = Instrument.ChannelCreator(ScopeChannel, (1, 2, 3, 4))

    bwlimit = Instrument.control(
        "BWL?", "BWL %s",
        """Sets the internal low-pass filter for all channels.""",
        validator=strict_discrete_set,
        values=ScopeChannel._BANDWIDTH_LIMITS,
        get_process=_channel_results_to_dict,
    )
