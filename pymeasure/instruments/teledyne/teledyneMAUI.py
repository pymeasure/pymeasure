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
from pymeasure.instruments.teledyne.teledyne_oscilloscope import TeledyneOscilloscope, \
    TeledyneOscilloscopeChannel, _results_list_to_dict


class TeledyneMAUIChannel(TeledyneOscilloscopeChannel):
    """Base class for channels on a :class:`TeledyneMAUI` device."""

    # Probably for historic reasons, "20MHZ" is registered as "ON"
    BANDWIDTH_LIMITS = ["OFF", "ON", "200MHZ"]

    TRIGGER_SLOPES = {"negative": "NEG", "positive": "POS"}

    # Reset listed values for existing commands:
    bwlimit_values = BANDWIDTH_LIMITS

    def autoscale(self):
        """Perform auto-setup command for channel."""
        self.write("AUTO_SETUP FIND")

    # noinspection PyIncorrectDocstring
    def setup(self, **kwargs):
        """Setup channel. Unspecified settings are not modified.

        Modifying values such as probe attenuation will modify offset, range, etc. Refer to
        oscilloscope documentation and make multiple consecutive calls to setup() if needed.
        See property descriptions for more information.

        :param bwlimit:
        :param coupling:
        :param display:
        :param offset:
        :param probe_attenuation:
        :param scale:
        :param trigger_coupling:
        :param trigger_level:
        :param trigger_slope:
        """
        super().setup(**kwargs)

    @property
    def current_configuration(self):
        """Get channel configuration as a dict containing the following keys:

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

    This base class works out of the box. Some properties, especially the number of channels,
    might have to be adjusted to the actual device.

    The manual detailing the API is "MAUI Oscilloscopes Remote Control and Automation Manual"
    (`link`_).

    .. _link: https://cdn.teledynelecroy.com/files/manuals/
              maui-remote-control-automation_27jul22.pdf
    """

    ch_1 = Instrument.ChannelCreator(TeledyneMAUIChannel, 1)

    ch_2 = Instrument.ChannelCreator(TeledyneMAUIChannel, 2)

    ch_3 = Instrument.ChannelCreator(TeledyneMAUIChannel, 3)

    ch_4 = Instrument.ChannelCreator(TeledyneMAUIChannel, 4)

    # Change listed values for existing commands:
    bwlimit_values = TeledyneMAUIChannel.BANDWIDTH_LIMITS

    ###############
    #   Trigger   #
    ###############

    @property
    def trigger(self):
        """Get trigger setup as a dict containing the following keys:

        - "mode": trigger sweep mode [auto, normal, single, stop]
        - "trigger_type": condition that will trigger the acquisition of waveforms
          [edge,slew,glit,intv,runt,drop]
        - "source": trigger source [c1,c2,c3,c4]
        - "hold_type": hold type (refer to page 172 of programing guide)
        - "hold_value1": hold value1 (refer to page 172 of programing guide)
        - "hold_value2": hold value2 (refer to page 172 of programing guide)
        - "coupling": input coupling for the selected trigger sources
        - "level": trigger level voltage for the active trigger source
        - "slope": trigger slope of the specified trigger source

        """
        trigger_select = self.trigger_select
        ch = self.ch(trigger_select[1])
        tb_setup = {
            "mode": self.trigger_mode,
            "trigger_type": trigger_select[0],
            "source": trigger_select[1],
            "hold_type": trigger_select[2],
            "hold_value1": trigger_select[3] if len(trigger_select) >= 4 else None,
            "hold_value2": trigger_select[4] if len(trigger_select) >= 5 else None,
            "coupling": ch.trigger_coupling,
            "level": ch.trigger_level,
            "slope": ch.trigger_slope
        }
        return tb_setup

    def force_trigger(self):
        """Make one acquisition if in active trigger mode.

        No action is taken if the device is in 'Stop trigger mode'.
        """
        # Method instead of property since no reply is sent
        self.write("FRTR")

    #################
    # Download data #
    #################

    hardcopy_setup_current = Instrument.measurement(
        "HCSU?",
        """Get current hardcopy config.""",
        get_process=_results_list_to_dict,
    )

    def hardcopy_setup(self, **kwargs):
        """Specify hardcopy settings.

        Connect a printer or define how to save to file. Set any or all
        of the following parameters.

        :param device: {BMP, JPEG, PNG, TIFF}
        :param format: {PORTRAIT, LANDSCAPE}
        :param background: {Std, Print, BW}
        :param destination: {PRINTER, CLIPBOARD, EMAIL, FILE, REMOTE}
        :param area: {GRIDAREAONLY, DSOWINDOW, FULLSCREEN}
        :param directory: Any legal DOS path, for FILE mode only
        :param filename: Filename string, no extension, for FILE mode only
        :param printername: Valid printer name, for PRINTER mode only
        :param portname: {GPIB, NET}
        """
        keys = {
            "device": "DEV",
            "format": "FORMAT",
            "background": "BCKG",
            "destination": "DEST",
            "area": "AREA",
            "directory": "DIR",
            "filename": "FILE",
            "printername": "PRINTER",
            "portname": "PORT",
        }

        arg_strs = [keys[key] + "," + value for key, value in kwargs.items()]

        self.write("HCSU " + ",".join(arg_strs))

    def download_image(self, **kwargs):
        """Get a BMP image of oscilloscope screen in bytearray of specified file format.

        The hardcopy destination is set to "REMOTE" by default.

        :param \\**kwargs: Keyword arguments for :meth:`hardcopy_setup`
        """
        kwargs.setdefault("destination", "REMOTE")
        self.hardcopy_setup(**kwargs)
        return super().download_image()
