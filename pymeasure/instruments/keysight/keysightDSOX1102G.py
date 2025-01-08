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

import numpy as np

from pymeasure.instruments import Instrument, SCPIUnknownMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Channel():
    """ Implementation of a Keysight DSOX1102G Oscilloscope channel.

    Implementation modeled on Channel object of Tektronix AFG3152C instrument. """

    BOOLS = {True: 1, False: 0}

    bwlimit = Instrument.control(
        "BWLimit?", "BWLimit %d",
        """ A boolean parameter that toggles 25 MHz internal low-pass filter.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    coupling = Instrument.control(
        "COUPling?", "COUPling %s",
        """ A string parameter that determines the coupling ("ac" or "dc").""",
        validator=strict_discrete_set,
        values={"ac": "AC", "dc": "DC"},
        map_values=True
    )

    display = Instrument.control(
        "DISPlay?", "DISPlay %d",
        """ A boolean parameter that toggles the display.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    invert = Instrument.control(
        "INVert?", "INVert %d",
        """ A boolean parameter that toggles the inversion of the input signal.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    label = Instrument.control(
        "LABel?", 'LABel "%s"',
        """ A string to label the channel. Labels with more than 10 characters are truncated to 10
        characters. May contain commonly used ASCII characters. Lower case characters are converted
        to upper case.""",
        get_process=lambda v: str(v[1:-1])
    )

    offset = Instrument.control(
        "OFFSet?", "OFFSet %f",
        """ A float parameter to set value that is represented at center of screen in
        Volts. The range of legal values varies depending on range and scale. If the specified
        value is outside of the legal range, the offset value is automatically set to the nearest
        legal value.
        """
    )

    probe_attenuation = Instrument.control(
        "PROBe?", "PROBe %f",
        """ A float parameter that specifies the probe attenuation. The probe attenuation
        may be from 0.1 to 10000.""",
        validator=strict_range,
        values=[0.1, 10000]
    )

    range = Instrument.control(
        "RANGe?", "RANGe %f",
        """ A float parameter that specifies the full-scale vertical axis in Volts.
        When using 1:1 probe attenuation, legal values for the range are from 8 mV to 40V."""
    )

    scale = Instrument.control(
        "SCALe?", "SCALe %f",
        """A float parameter that specifies the vertical scale, or units per division, in Volts."""
    )

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number

    def values(self, command, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values(":channel%d:%s" % (
            self.number, command), **kwargs)

    def ask(self, command):
        self.instrument.ask(":channel%d:%s" % (self.number, command))

    def write(self, command):
        self.instrument.write(":channel%d:%s" % (self.number, command))

    def setup(self, bwlimit=None, coupling=None, display=None, invert=None, label=None, offset=None,
              probe_attenuation=None, vertical_range=None, scale=None):
        """ Setup channel. Unspecified settings are not modified. Modifying values such as
        probe attenuation will modify offset, range, etc. Refer to oscilloscope documentation and
        make multiple consecutive calls to setup() if needed.

        :param bwlimit: A boolean, which enables 25 MHz internal low-pass filter.
        :param coupling: "ac" or "dc".
        :param display: A boolean, which enables channel display.
        :param invert: A boolean, which enables input signal inversion.
        :param label: Label string with max. 10 commonly used ASCII characters.
        :param offset: Numerical value represented at center of screen, must be inside
            the legal range.
        :param probe_attenuation: Probe attenuation values from 0.1 to 1000.
        :param vertical_range: Full-scale vertical axis of the selected channel. When using 1:1
            probe attenuation, legal values for the range are  from 8mV to 40 V. If the probe
            attenuation is changed, the range value is multiplied by the probe attenuation factor.
        :param scale: Units per division. """

        if vertical_range is not None and scale is not None:
            log.warning(
                'Both "vertical_range" and "scale" are specified. Specified "scale" has priority.')

        if probe_attenuation is not None:
            self.probe_attenuation = probe_attenuation
        if bwlimit is not None:
            self.bwlimit = bwlimit
        if coupling is not None:
            self.coupling = coupling
        if display is not None:
            self.display = display
        if invert is not None:
            self.invert = invert
        if label is not None:
            self.label = label
        if offset is not None:
            self.offset = offset
        if vertical_range is not None:
            self.range = vertical_range
        if scale is not None:
            self.scale = scale

    @property
    def current_configuration(self):
        """ Read channel configuration as a dict containing the following keys:
            - "CHAN": channel number (int)
            - "OFFS": vertical offset (float)
            - "RANG": vertical range (float)
            - "COUP": "dc" or "ac" coupling (str)
            - "IMP": input impedance (str)
            - "DISP": currently displayed (bool)
            - "BWL": bandwidth limiting enabled (bool)
            - "INV": inverted (bool)
            - "UNIT": unit (str)
            - "PROB": probe attenuation (float)
            - "PROB:SKEW": skew factor (float)
            - "STYP": probe signal type (str)
        """

        # Using the instrument's ask method because Channel.ask() adds the prefix ":channelX:", and
        # to query the configuration details, we actually need to ask ":channelX?", without a
        # second ":"
        ch_setup_raw = self.instrument.ask(":channel%d?" % self.number).strip("\n")

        # ch_setup_raw hat the following format:
        # :CHAN1:RANG +40.0E+00;OFFS +0.00000E+00;COUP DC;IMP ONEM;DISP 1;BWL 0;
        # INV 0;LAB "1";UNIT VOLT;PROB +10E+00;PROB:SKEW +0.00E+00;STYP SING

        # Cut out the ":CHANx:" at beginning and split string
        ch_setup_splitted = ch_setup_raw[7:].split(";")

        # Create dict of setup parameters
        ch_setup_dict = dict(map(lambda v: v.split(" "), ch_setup_splitted))

        # Add "CHAN" key
        ch_setup_dict["CHAN"] = ch_setup_raw[5]

        # Convert values to specific type
        to_str = ["COUP", "IMP", "UNIT", "STYP"]
        to_bool = ["DISP", "BWL", "INV"]
        to_float = ["OFFS", "PROB", "PROB:SKEW", "RANG"]
        to_int = ["CHAN"]
        for key in ch_setup_dict:
            if key in to_str:
                ch_setup_dict[key] = str(ch_setup_dict[key])
            elif key in to_bool:
                ch_setup_dict[key] = (ch_setup_dict[key] == "1")
            elif key in to_float:
                ch_setup_dict[key] = float(ch_setup_dict[key])
            elif key in to_int:
                ch_setup_dict[key] = int(ch_setup_dict[key])
        return ch_setup_dict


class KeysightDSOX1102G(SCPIUnknownMixin, Instrument):
    """ Represents the Keysight DSOX1102G Oscilloscope interface for interacting
    with the instrument.

    Refer to the Keysight DSOX1102G Oscilloscope Programmer's Guide for further details about
    using the lower-level methods to interact directly with the scope.

    .. code-block:: python

        scope = KeysightDSOX1102G(resource)
        scope.autoscale()
        ch1_data_array, ch1_preamble = scope.download_data(source="channel1", points=2000)
        # ...
        scope.shutdown()

    Known issues:

    - The digitize command will be completed before the operation is. May lead to
      VI_ERROR_TMO (timeout) occurring when sending commands immediately after digitize.
      Current fix: if deemed necessary, add delay between digitize and follow-up command
      to scope.
    """

    BOOLS = {True: 1, False: 0}

    def __init__(self, adapter, name="Keysight DSOX1102G Oscilloscope", **kwargs):
        super().__init__(
            adapter, name, timeout=6000, **kwargs
        )
        # Account for setup time for timebase_mode, waveform_points_mode
        self.ch1 = Channel(self, 1)
        self.ch2 = Channel(self, 2)

    #################
    # Channel setup #
    #################

    def autoscale(self):
        """ Autoscale displayed channels. """
        self.write(":autoscale")

    ##################
    # Timebase Setup #
    ##################

    @property
    def timebase(self):
        """ Read timebase setup as a dict containing the following keys:
            - "REF": position on screen of timebase reference (str)
            - "MAIN:RANG": full-scale timebase range (float)
            - "POS": interval between trigger and reference point (float)
            - "MODE": mode (str)"""
        return self._timebase()

    timebase_mode = Instrument.control(
        ":TIMebase:MODE?", ":TIMebase:MODE %s",
        """ A string parameter that sets the current time base. Can be "main",
        "window", "xy", or "roll".""",
        validator=strict_discrete_set,
        values={"main": "MAIN", "window": "WIND", "xy": "XY", "roll": "ROLL"},
        map_values=True
    )

    timebase_offset = Instrument.control(
        ":TIMebase:POSition?", ":TIMebase:REFerence CENTer;:TIMebase:POSition %f",
        """ A float parameter that sets the time interval in seconds between the trigger
        event and the reference position (at center of screen by default)."""
    )

    timebase_range = Instrument.control(
        ":TIMebase:RANGe?", ":TIMebase:RANGe %f",
        """ A float parameter that sets the full-scale horizontal time in seconds for the
        main window."""
    )

    timebase_scale = Instrument.control(
        ":TIMebase:SCALe?", ":TIMebase:SCALe %f",
        """ A float parameter that sets the horizontal scale (units per division) in seconds
        for the main window."""
    )

    ###############
    # Acquisition #
    ###############

    acquisition_type = Instrument.control(
        ":ACQuire:TYPE?", ":ACQuire:TYPE %s",
        """ A string parameter that sets the type of data acquisition. Can be "normal", "average",
        "hresolution", or "peak".""",
        validator=strict_discrete_set,
        values={"normal": "NORM", "average": "AVER", "hresolution": "HRES", "peak": "PEAK"},
        map_values=True
    )

    acquisition_mode = Instrument.control(
        ":ACQuire:MODE?", ":ACQuire:MODE %s",
        """ A string parameter that sets the acquisition mode. Can be "realtime" or "segmented".""",
        validator=strict_discrete_set,
        values={"realtime": "RTIM", "segmented": "SEGM"},
        map_values=True
    )

    def run(self):
        """ Starts repetitive acquisitions.

        This is the same as pressing the Run key on the front panel.
        """
        self.write(":run")

    def stop(self):
        """  Stops the acquisition. This is the same as pressing the Stop key on the front panel."""
        self.write(":stop")

    def single(self):
        """ Causes the instrument to acquire a single trigger of data.
        This is the same as pressing the Single key on the front panel. """
        self.write(":single")

    _digitize = Instrument.setting(
        ":DIGitize %s",
        """ Acquire waveforms according to the settings of the :ACQuire commands and specified
        source, as a string parameter that can take the following values: "channel1", "channel2",
        "function", "math", "fft", "abus", or "ext". """,
        validator=strict_discrete_set,
        values={"channel1": "CHAN1", "channel2": "CHAN2", "function": "FUNC", "math": "MATH",
                "fft": "FFT", "abus": "ABUS", "ext": "EXT"},
        map_values=True
    )

    def digitize(self, source: str):
        """ Acquire waveforms according to the settings of the :ACQuire commands. Ensure a delay
        between the digitize operation and further commands, as timeout may be reached before
        digitize has completed.
        :param source: "channel1", "channel2", "function", "math", "fft", "abus", or "ext"."""
        self._digitize = source

    waveform_points_mode = Instrument.control(
        ":waveform:points:mode?", ":waveform:points:mode %s",
        """ A string parameter that sets the data record to be transferred with the waveform_data
         method. Can be "normal", "maximum", or "raw".""",
        validator=strict_discrete_set,
        values={"normal": "NORM", "maximum": "MAX", "raw": "RAW"},
        map_values=True
    )
    waveform_points = Instrument.control(
        ":waveform:points?", ":waveform:points %d",
        """ An integer parameter that sets the number of waveform points to be transferred with
        the waveform_data method. Can be any of the following values:
        100, 250, 500, 1000, 2 000, 5 000, 10 000, 20 000, 50 000, 62 500.

        Note that the oscilloscope may provide less than the specified nb of points. """,
        validator=strict_discrete_set,
        values=[100, 250, 500, 1000, 2000, 5000, 10000, 20000, 50000, 62500]
    )
    waveform_source = Instrument.control(
        ":waveform:source?", ":waveform:source %s",
        """ A string parameter that selects the analog channel, function, or reference waveform
        to be used as the source for the waveform methods. Can be "channel1", "channel2",
        "function", "fft", "wmemory1", "wmemory2", or "ext".""",
        validator=strict_discrete_set,
        values={"channel1": "CHAN1", "channel2": "CHAN2", "function": "FUNC", "fft": "FFT",
                "wmemory1": "WMEM1", "wmemory2": "WMEM2", "ext": "EXT"},
        map_values=True
    )
    waveform_format = Instrument.control(
        ":waveform:format?", ":waveform:format %s",
        """ A string parameter that controls how the data is formatted when sent from the
        oscilloscope. Can be "ascii", "word" or "byte". Words are transmitted in big endian by
        default.""",
        validator=strict_discrete_set,
        values={"ascii": "ASC", "word": "WORD", "byte": "BYTE"},
        map_values=True
    )

    @property
    def waveform_preamble(self):
        """ Get preamble information for the selected waveform source as a dict with the following keys:
            - "format": byte, word, or ascii (str)
            - "type": normal, peak detect, or average (str)
            - "points": nb of data points transferred (int)
            - "count": always 1 (int)
            - "xincrement": time difference between data points (float)
            - "xorigin": first data point in memory (float)
            - "xreference": data point associated with xorigin (int)
            - "yincrement": voltage difference between data points (float)
            - "yorigin": voltage at center of screen (float)
            - "yreference": data point associated with yorigin (int)"""  # noqa: E501
        return self._waveform_preamble()

    @property
    def waveform_data(self):
        """ Get the binary block of sampled data points transmitted using the IEEE 488.2 arbitrary
        block data format."""
        # Other waveform formats raise UnicodeDecodeError
        self.waveform_format = "ascii"

        data = self.values(":waveform:data?")
        # Strip header from first data element
        data[0] = float(data[0][10:])

        return data

    ################
    # System Setup #
    ################

    @property
    def system_setup(self):
        """ A string parameter that sets up the oscilloscope. Must be in IEEE 488.2 format.
        It is recommended to only set a string previously obtained from this command."""
        return self.ask(":system:setup?")

    @system_setup.setter
    def system_setup(self, setup_string):
        self.write(":system:setup " + setup_string)

    def ch(self, channel_number):
        if channel_number == 1:
            return self.ch1
        elif channel_number == 2:
            return self.ch2
        else:
            raise ValueError("Invalid channel number. Must be 1 or 2.")

    def clear_status(self):
        """ Clear device status. """
        self.write("*CLS")

    def factory_reset(self):
        """ Factory default setup, no user settings remain unchanged. """
        self.write("*RST")

    def default_setup(self):
        """ Default setup, some user settings (like preferences) remain unchanged. """
        self.write(":SYSTem:PRESet")

    def timebase_setup(self, mode=None, offset=None, horizontal_range=None, scale=None):
        """ Set up timebase. Unspecified parameters are not modified. Modifying a single parameter
        might impact other parameters. Refer to oscilloscope documentation and make multiple
        consecutive calls to channel_setup if needed.

        :param mode: Timebase mode, can be "main", "window", "xy", or "roll".
        :param offset: Offset in seconds between trigger and center of screen.
        :param horizontal_range: Full-scale range in seconds.
        :param scale: Units-per-division in seconds."""

        if mode is not None:
            self.timebase_mode = mode
        if offset is not None:
            self.timebase_offset = offset
        if horizontal_range is not None:
            self.timebase_range = horizontal_range
        if scale is not None:
            self.timebase_scale = scale

    def download_image(self, format_="png", color_palette="color"):
        """ Get image of oscilloscope screen in bytearray of specified file format.

        :param format_: "bmp", "bmp8bit", or "png"
        :param color_palette: "color" or "grayscale"
        """
        query = f":DISPlay:DATA? {format_}, {color_palette}"
        # Using binary_values query because default interface does not support binary transfer
        img = self.binary_values(query, header_bytes=10, dtype=np.uint8)
        return bytearray(img)

    def download_data(self, source, points=62500):
        """ Get data from specified source of oscilloscope. Returned objects are a np.ndarray of
        data values (no temporal axis) and a dict of the waveform preamble, which can be used to
        build the corresponding time values for all data points.

        Multimeter will be stopped for proper acquisition.

        :param source: measurement source, can be "channel1", "channel2", "function", "fft",
            "wmemory1", "wmemory2", or "ext".
        :param points: integer number of points to acquire. Note that oscilloscope may return fewer
            points than specified, this is not an issue of this library. Can be 100, 250, 500, 1000,
            2000, 5000, 10000, 20000, 50000, or 62500.

        :return data_ndarray, waveform_preamble_dict: see waveform_preamble property for dict
            format.
        """
        # TODO: Consider downloading from multiple sources at the same time.
        self.waveform_source = source
        self.waveform_points_mode = "normal"
        self.waveform_points = points

        preamble = self.waveform_preamble
        data_bytes = self.waveform_data
        return np.array(data_bytes), preamble

    def _timebase(self):
        """
        Reads setup data from timebase and converts it to a more convenient dict of values.
        """
        tb_setup_raw = self.ask(":timebase?").strip("\n")

        # tb_setup_raw hat the following format:
        # :TIM:MODE MAIN;REF CENT;MAIN:RANG +1.00E-03;POS +0.0E+00

        # Cut out the ":TIM:" at beginning and split string
        tb_setup_splitted = tb_setup_raw[5:].split(";")

        # Create dict of setup parameters
        tb_setup = dict(map(lambda v: v.split(" "), tb_setup_splitted))

        # Convert values to specific type
        to_str = ["MODE", "REF"]
        to_float = ["MAIN:RANG", "POS"]
        for key in tb_setup:
            if key in to_str:
                tb_setup[key] = str(tb_setup[key])
            elif key in to_float:
                tb_setup[key] = float(tb_setup[key])

        return tb_setup

    def _waveform_preamble(self):
        """
        Reads waveform preamble and converts it to a more convenient dict of values.
        """
        vals = self.values(":waveform:preamble?")
        # Get values to dict
        vals_dict = dict(zip(["format", "type", "points", "count", "xincrement", "xorigin",
                              "xreference", "yincrement", "yorigin", "yreference"], vals))
        # Map element values
        format_map = {0: "BYTE", 1: "WORD", 4: "ASCII"}
        type_map = {0: "NORMAL", 1: "PEAK DETECT", 2: "AVERAGE", 3: "HRES"}
        vals_dict["format"] = format_map[int(vals_dict["format"])]
        vals_dict["type"] = type_map[int(vals_dict["type"])]

        # Correct types
        to_int = ["points", "count", "xreference", "yreference"]
        to_float = ["xincrement", "xorigin", "yincrement", "yorigin"]
        for key in vals_dict:
            if key in to_int:
                vals_dict[key] = int(vals_dict[key])
            elif key in to_float:
                vals_dict[key] = float(vals_dict[key])

        return vals_dict
