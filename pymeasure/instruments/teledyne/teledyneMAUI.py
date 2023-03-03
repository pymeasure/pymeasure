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
    TeledyneOscilloscopeChannel


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


class TeledyneMAUIChannel(TeledyneOscilloscopeChannel):
    """Base class for channels on a :class:`TeledyneMAUI` device."""

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


class TeledyneMAUI(TeledyneOscilloscope):
    """A base class for the MAUI-type of Teledyne oscilloscopes.

    This class is not exactly device specific. Nonetheless, it might already work out of the box and
    therefore this class not abstract.
    """

    channels = Instrument.ChannelCreator(TeledyneMAUIChannel, (1, 2, 3, 4))

    # HMAG and the like now only apply to math functions (F1..Fn):

    @property
    def timebase_hor_magnify(self):
        raise NotImplementedError("Property is not available on this device")

    @property
    def timebase_hor_position(self):
        raise NotImplementedError("Property is not available on this device")

    # PEAK_DETECT, AVERAGE, etc. are moved to functions (F1..Fn);

    @property
    def acquisition_type(self):
        raise NotImplementedError("Property is not available on this device")

    @property
    def acquisition_average(self):
        raise NotImplementedError("Property is not available on this device")

    @property
    def acquisition_status(self):
        raise NotImplementedError("Property is not available on this device")

    @property
    def acquisition_sampling_rate(self):
        raise NotImplementedError("Property is not available on this device")

    bwlimit = Instrument.control(
        "BWL?", "BWL %s",
        """Sets the internal low-pass filter for all channels.""",
        validator=strict_discrete_set,
        values=TeledyneMAUIChannel._BANDWIDTH_LIMITS,
        get_process=_channel_results_to_dict,
    )

    @property
    def timebase(self):
        """ Read timebase setup as a dict containing the following keys:
            - "timebase_scale": horizontal scale in seconds/div (float)
            - "timebase_offset": interval in seconds between the trigger and the reference
            position (float)
        """
        tb_setup = {
            "timebase_scale": self.timebase_scale,
            "timebase_offset": self.timebase_offset,
        }
        return tb_setup

    memory_size = Instrument.control(
        "MSIZ?", "MSIZ %s",
        """A float parameter or string that selects the maximum depth of memory.
        Use for example 500, 100e6, "100K", "25MA".

        The reply will always be a float.
        """
    )

    @property
    def waveform_preamble(self):
        """ Get preamble information for the selected waveform source as a dict with the
        following keys:
        - "requested_points": number of data points requested by the user (int)
        - "sampled_points": number of data points sampled by the oscilloscope (int)
        - "transmitted_points": number of data points actually transmitted (optional) (int)
        - "memory_size": size of the oscilloscope internal memory in bytes (int)
        - "sparsing": sparse point. It defines the interval between data points. (int)
        - "first_point": address of the first data point to be sent (int)
        - "source": source of the data : "C1", "C2", "C3", "C4", "MATH".
        - "grid_number": number of horizontal grids (it is a read-only property)
        - "xdiv": horizontal scale (units per division) in seconds
        - "xoffset": time interval in seconds between the trigger event and the reference position
        - "ydiv": vertical scale (units per division) in Volts
        - "yoffset": value that is represented at center of screen in Volts
        """
        vals = self.values("WFSU?")
        preamble = {
            "sparsing": vals[vals.index("SP") + 1],
            "requested_points": vals[vals.index("NP") + 1],
            "first_point": vals[vals.index("FP") + 1],
            "transmitted_points": None,
            "source": self.waveform_source,
            "grid_number": self._grid_number,
            "memory_size": self.memory_size,
            "xdiv": self.timebase_scale,
            "xoffset": self.timebase_offset
        }
        return self._fill_yaxis_preamble(preamble)

    def _fill_yaxis_preamble(self, preamble=None):
        """ Fill waveform preamble section concerning the Y-axis.
        :param preamble: waveform preamble to be filled
        :return: filled preamble
        """
        if preamble is None:
            preamble = {}
        if self.waveform_source == "MATH":
            preamble["ydiv"] = self.math_vdiv
            preamble["yoffset"] = self.math_vpos
        else:
            preamble["ydiv"] = self.ch(self.waveform_source).scale
            preamble["yoffset"] = self.ch(self.waveform_source).offset
        return preamble
