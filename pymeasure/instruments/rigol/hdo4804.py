#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import numpy as np
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class Channel():
    """ Implementation of a Rigol MS05354 Oscilloscope channel.
    Implementation modeled on Channel object of Tektronix AFG3152C instrument. """

    BOOLS = {True: 1, False: 0}

    bwlimit = Instrument.control(
        "BWLimit?", "BWLimit %s",
        """ A string parameter that sets the bandwidth of the channel. Options are:
        "20M", "250M", or "OFF". "OFF" sets the Bandwith to full (800 MHz in this case)""",
        validator=strict_discrete_set,
        values=['20M', '250M', 'OFF'],
    )

    coupling = Instrument.control(
        "COUPling?", "COUPling %s",
        """ A string parameter that determines the coupling ("ac" or "dc" or "gnd").""",
        validator=strict_discrete_set,
        values={"ac": "AC", "dc": "DC", "gnd": "GND"},
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

    offset = Instrument.control(
        "OFFSet?", "OFFSet %g",
        """ A float parameter to set value that is represented at center of screen in 
        Volts. The range of legal values varies depending on range and scale. If the specified value 
        is outside of the legal range, the offset value is automatically set to the nearest legal value. """
    )

    probe_attenuation = Instrument.control(
        "PROBe?", "PROBe %g",
        """ A float parameter that specifies the probe attenuation. The allowed values are only the standard 1,2,5,10...
         but the oscilloscope will set to the nearest legal value. May be from 0.01 to 50000.""",
        validator=strict_range,
        values=[0.01, 50000]
    )

    scale = Instrument.control(
        "SCALe?", "SCALe %g",
        """ A float parameter that specifies the vertical scale, or units per division, in Volts. If Vernier is off, 
        the V/div will snap to the next larger 1, 2, 5, 10..., otherwise the number you set will actually be the scale"""
    )

    units = Instrument.control(
        "UNITs?", "UNITs %s",
        """ A string parameter that sets the units of the corresponding analog channel. Options are:
        "VOLTage|WATT|AMPere|UNKNown""",
        validator=strict_discrete_set,
        values=['VOLT', 'VOLTage', 'WATT', 'AMP', 'AMPere', 'UNKN', 'UNKNown'],
    )

    impedance = Instrument.control(
        "IMPedance?", "IMPedance %s",
        """A string control that sets the input impedance of the channel.
        Can be OMEG or FIFTY""",
        validator=strict_discrete_set,
        values={"OMEG":"OMEG", "FIFTY":"FIFT"},
        map_values=True
    )

    vernier = Instrument.control(
        "VERNier?", "VERNier %d",
        """ A boolean parameter that toggles whether or the V/div setting is restricted to 1,2,5,10... .""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
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

    def setup(self, bwlimit=None, coupling=None, display=None, invert=None, offset=None,
              probe_attenuation=None, scale=None):
        """ Setup channel. Unspecified settings are not modified. Modifying values such as
        probe attenuation will modify offset, range, etc. Refer to oscilloscope documentation and make
        multiple consecutive calls to setup() if needed.
        :param bwlimit: A boolean, which enables 25 MHz internal low-pass filter.
        :param coupling: "ac" or "dc".
        :param display: A boolean, which enables channel display.
        :param invert: A boolean, which enables input signal inversion.
        :param offset: Numerical value represented at center of screen, must be inside the legal range.
        :param probe_attenuation: Probe attenuation values from 0.1 to 1000.
        :param scale: Units per division. """

        if probe_attenuation is not None: self.probe_attenuation = probe_attenuation
        if bwlimit is not None: self.bwlimit = bwlimit
        if coupling is not None: self.coupling = coupling
        if display is not None: self.display = display
        if invert is not None: self.invert = invert
        if offset is not None: self.offset = offset
        if scale is not None: self.scale = scale


class RigolHDO4804(Instrument):
    """ Represents the Rigol HDO4804 Oscilloscope interface for interacting
    with the instrument.
    Refer to the Rigol HDO4804 Oscilloscope Programmer's Guide for further details about
    using the lower-level methods to interact directly with the scope.
    .. code-block:: python

        scope = RigolHDO4804(resource)
        scope.autoscale()
        ch1_data_array, ch1_preamble = scope.download_data(source="channel1", points=2000)
        # ...
        scope.shutdown()
    Known issues:

    - The digitize command will be completed before the operation is. May lead to
      VI_ERROR_TMO (timeout) occuring when sending commands immediately after digitize.
      Current fix: if deemed necessary, add delay between digitize and follow-up command
      to scope.
    """

    BOOLS = {True: 1, False: 0}

    def __init__(self, adapter, **kwargs):
        super(RigolHDO4804, self).__init__(
            adapter, "Rigol HDO4804 Oscilloscope", **kwargs
        )
        # Account for setup time for timebase_mode, waveform_points_mode
        self.adapter.connection.timeout = 6000
        self.ch1 = Channel(self, 1)
        self.ch2 = Channel(self, 2)
        self.ch3 = Channel(self, 3)
        self.ch4 = Channel(self, 4)

    #################
    # Channel setup #
    #################

    def autoscale(self):
        """ Autoscale displayed channels. """
        self.write("system:autoscale")

    ##################
    # Timebase Setup #
    ##################

    timebase_mode = Instrument.control(
        ":TIMebase:MODE?", ":TIMebase:MODE %s",
        """ A string parameter that sets the current time base. Can be "main", "xy", or "roll".""",
        validator=strict_discrete_set,
        values={"main": "MAIN", "xy": "XY", "roll": "ROLL"},
        map_values=True
    )

    timebase_offset = Instrument.control(
        ":TIMebase:OFFSet?", ":TIMebase:HREFerence:MODE CENTer;:TIMebase:OFFSet %g",
        """ A float parameter that sets the time interval in seconds between the trigger 
        event and the reference position (at center of screen by default)."""
    )

    timebase_scale = Instrument.control(
        ":TIMebase:SCALe?", ":TIMebase:SCALe %g",
        """ A float parameter that sets the horizontal scale (units per division) in seconds 
        for the main window. In YT mode ,the range is 1 ns to 1000 s; in roll mode, 200 ms to 1000 s """
    )

    ###############
    # Acquisition #
    ###############

    acquisition_navg = Instrument.control(
        ":ACQuire:AVERages?", ":ACQuire:AVERages %d",
        """ An integer parameter that sets the number of averages to take if averaging is enable. Range is 2-65536.""",
        validator=strict_range,
        values=[2, 65536],
    )

    acquisition_mdepth = Instrument.control(
        ":ACQuire:MDEPth?", ":ACQuire:MDEPth %s",
        """ A string parameter that sets the memory depth of the oscilloscope. Options are:
         'AUTO', or the integer corresponding to '1k', '10k', '100k', '1M', '25M', '50M', '100M', '200M'""",
    )

    acquisition_type = Instrument.control(
        ":ACQuire:TYPE?", ":ACQuire:TYPE %s",
        """ A string parameter that sets the type of data acquisition. Can be "normal", "average", or "peak".""",
        validator=strict_discrete_set,
        values={"normal": "NORM", "average": "AVER", "peak": "PEAK"},
        map_values=True
    )

    acquisition_srate = Instrument.measurement(
        ":ACQuire:SRATe?",
        """ A string parameter that returns the sampling rate in Samples/s. There are 10 horizontal divs in the MSO500
         series. The relationship between mdepth, sample rate, and waveform length is 
         memory depth = sample rate x waveform length. Waveform length is 10 divs * timebase_scale""",
    )

    ###########
    # Trigger #
    ###########

    trigger_type = Instrument.control(
        ":TRIGger:MODE?", ":TRIGger:MODE %s",
        """ A string parameter that sets trigger type. Can be "edge", "pulse", or "slope". There are many more options
        but only these three are implemented here because many more commands would need to be implemented to set the
        other modes.
         """,
        validator=strict_discrete_set,
        values={"edge": "EDGE", "pulse": "PULSe", "slope": "SLOPe"},
        map_values=True
    )

    trigger_coupling = Instrument.control(
        ":TRIGger:COUPling?", ":TRIGger:COUPling %s",
        """ A string parameter that sets trigger coupling. Can be "ac", "dc", "lfreject", or "hfreject".
         """,
        validator=strict_discrete_set,
        values={"ac": "AC", "dc": "DC", "lfreject": "LFR", "hfreject": "HFR"},
        map_values=True
    )

    trigger_status = Instrument.measurement(
        ":TRIGger:STATus?",
        """ A string parameter that gets the trigger status. Will return any of: TD, WAIT, RUN, AUTO, STOP .
         """
    )

    trigger_mode = Instrument.control(
        ":TRIGger:SWEep?", ":TRIGger:SWEep %s",
        """ A string parameter that sets trigger mode. Can be "auto", "normal", or "single". "single" is the same as
        pressing the single button or running the self.single() method.
         """,
        validator=strict_discrete_set,
        values={"auto": "AUTO", "normal": "NORM", "single": "SING"},
        map_values=True
    )

    trigger_edge_source = Instrument.control(
        ":TRIGger:EDGE:SOURce?", ":TRIGger:EDGE:SOURce %s",
        """ String parameter that sets or queries the trigger source of the Edge trigger. The options are 
        {D0|D1|D2|D3|D4|D5|D6|D7|D8|D9|D10|D11|D12|D13|D14|D15|CHANnel1|CHANnel2|CHANnel3|CHANnel4|ACLine}
         """,
        validator=strict_discrete_set,
        values=['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'D13', 'D14', 'D15',
                'CHANnel1', 'CHANnel2', 'CHANnel3', 'CHANnel4', 'ACLine', 'CHAN1', 'CHAN2', 'CHAN3', 'CHAN4']
    )

    trigger_edge_slope = Instrument.control(
        ":TRIGger:EDGE:SLOPe?", ":TRIGger:EDGE:SLOPe %s",
        """ String parameter that sets or queries the edge trigger slope. Can be "pos", "neg", or "either"
         """,
        validator=strict_discrete_set,
        values={"pos": "POSitive", "neg": "NEGative", "either": "RFALI"},
        map_values=True
    )

    trigger_edge_level = Instrument.control(
        ":TRIGger:EDGE:LEVel?", ":TRIGger:EDGE:LEVel %g",
        """ Float parameter that sets or queries the edge trigger level."
         """
    )


    def run(self):
        """ Starts repetitive acquisitions. This is the same as pressing the Run key on the front panel."""
        self.write(":run")

    def stop(self):
        """  Stops the acquisition. This is the same as pressing the Stop key on the front panel."""
        self.write(":stop")

    def single(self):
        """ Causes the instrument to acquire a single trigger of data.
        This is the same as pressing the Single key on the front panel. """
        self.write(":single")

    ############
    # Waveform #
    ############

    waveform_source = Instrument.control(
        ":waveform:source?", ":waveform:source %s",
        """ A string parameter that selects the analog channel, function, or reference waveform 
        to be used as the source for the waveform methods. Can be:
        'CHANnel1', 'CHANnel2', 'CHANnel3', 'CHANnel4','CHAN1', 'CHAN2', 'CHAN3', 'CHAN4'.
        TODO implement Digital pin sources and the MATH sources""",
        validator=strict_discrete_set,
        values=['CHANnel1', 'CHANnel2', 'CHANnel3', 'CHANnel4', 'CHAN1', 'CHAN2', 'CHAN3', 'CHAN4'],
    )

    waveform_mode = Instrument.control(
        ":waveform:mode?", ":waveform:mode %s",
        """ A string parameter that sets the data record to be transferred with the waveform_data
         method. Can be "normal", "maximum", or "raw".""",
        validator=strict_discrete_set,
        values={"normal": "NORM", "maximum": "MAX", "raw": "RAW"},
        map_values=True
    )

    waveform_format = Instrument.control(
        ":waveform:format?", ":waveform:format %s",
        """ A string parameter that controls how the data is formatted when sent from the 
        oscilloscope. Can be "ascii", "word" or "byte". Words are transmitted in big endian by default.""",
        validator=strict_discrete_set,
        values={"ascii": "ASC", "word": "WORD", "byte": "BYTE"},
        map_values=True
    )

    waveform_points = Instrument.control(
        ":waveform:points?", ":waveform:points %d",
        """ An integer parameter that sets the number of waveform points to be transferred with
        the waveform_data method. range is 1 to value based on oscilloscope state. 

        Note that the oscilloscope may provide less than the specified nb of points. """,
    )

    waveform_start = Instrument.control(
        ":waveform:start?", ":waveform:start %d",
        """ An integer parameter that sets the starting point of the waveform record to be transferred.""",
    )

    waveform_stop = Instrument.control(
        ":waveform:stop?", ":waveform:stop %d",
        """ An integer parameter that sets the ending point of the waveform record to be transferred.""",
    )

    waveform_xincrement = Instrument.measurement(
        ":waveform:xincrement?",
        """ An attribute that returns the timestep between points based on the current waveform transfer mode. """,
    )

    waveform_xorigin = Instrument.measurement(
        ":waveform:xorigin?",
        """ An attribute that returns the start time of the currently selected waveform transfer mode. """,
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
            - "yreference": data point associated with yorigin (int)"""
        return self._waveform_preamble()

    @property
    def waveform_data(self):
        """ Get the binary block of sampled data points transmitted using the IEEE 488.2 arbitrary
        block data format."""
        # Other waveform formats raise UnicodeDecodeError
        self.waveform_format = "byte"

        data = self.binary_values(":waveform:data?", dtype=np.uint8)[11:-1].astype('float32')
        data = self.waveform_preamble['yincrement']*(data-128)

        return data

    ########
    # Mask #
    ########

    mask_enable = Instrument.control(
        "MASK:ENABle?", "MASK:ENABle %d",
        """ A boolean parameter that controls whether or not the mask is enabled.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    mask_source = Instrument.control(
        "MASK:SOURce?", "MASK:SOURce %s",
        """ An integer parameter that sets the channel source for the mask.""",
        validator=strict_discrete_set,
        values={1: 'CHAN1', 2: 'CHAN2', 3: 'CHAN3', 4: 'CHAN4'},
        map_values=True
    )

    mask_operate = Instrument.control(
        "MASK:OPERate?", "MASK:OPERate %s",
        """ A boolean control that turns the mask test condition on/off.""",
        validator=strict_discrete_set,
        values={True: 'RUN', False: 'STOP'},
        map_values=True
    )

    mask_mdisplay = Instrument.control(
        "MASK:MDISplay?", "MASK:MDISplay %d",
        """ A boolean parameter that controls whether or not the mask statistics window is displayed.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    mask_x = Instrument.control(
        "MASK:X?", "MASK:X %g",
        """ A float parameter controlling the horizontal location of the pass/fail test mask.
        Can be anywhere from 0.01 div to 2 divs. Default is 0.24 div""",
        validator=strict_range,
        values=[0.01, 2],
    )

    mask_y= Instrument.control(
        "MASK:Y?", "MASK:Y %g",
        """ A float parameter controlling the vertical location of the pass/fail test mask.
        Can be anywhere from 0.04 div to 2 divs. Default is 0.48 div.""",
        validator=strict_range,
        values=[0.04, 2]
    )

    def create_mask(self, source, x=0.24, y=0.48):
        """
        Create the mask with the desire parameters
        """
        if self.trigger_status != 'STOP':
            self.stop()
        self.mask_operate = False
        self.mask_enable = True
        self.mask_source = source
        self.mask_x = x
        self.mask_y = y
        self.write(':MASK:CREate')
        self.mask_operate = True
        self.mask_mdisplay = True

    def disable_mask(self):
        self.mask_operate = False
        self.mask_enable = False



    def reset_mask_stats(self):
        """
        Resets the number of frames that passed and failed the pass/fail test, as well as the total
        number of frames.
        """
        self.write(':MASK:RESet')

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

    def check_errors(self):
        """ Read all errors from the instrument."""
        while True:
            err = self.values(":SYST:ERR?")
            if int(err[0]) != 0:
                errmsg = "Keysight DSOX1102G: %s: %s" % (err[0], err[1])
                log.error(errmsg + "\n")
            else:
                break

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
        """ Set up timebase. Unspecified parameters are not modified. Modifying a single parameter might
        impact other parameters. Refer to oscilloscope documentation and make multiple consecutive calls
        to channel_setup if needed.
        :param mode: Timebase mode, can be "main", "window", "xy", or "roll".
        :param offset: Offset in seconds between trigger and center of screen.
        :param horizontal_range: Full-scale range in seconds.
        :param scale: Units-per-division in seconds."""

        if mode is not None: self.timebase_mode = mode
        if offset is not None: self.timebase_offset = offset
        if horizontal_range is not None: self.timebase_range = horizontal_range
        if scale is not None: self.timebase_scale = scale

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
        """ Get data from specified source of oscilloscope. Returned objects are a np.ndarray of data
        values (no temporal axis) and a dict of the waveform preamble, which can be used to build the
        corresponding time values for all data points.
        Multimeter will be stopped for proper acquisition.
        :param source: measurement source, can be "channel1", "channel2", "function", "fft", "wmemory1",
                        "wmemory2", or "ext".
        :param points: integer number of points to acquire. Note that oscilloscope may return less points than
                        specified, this is not an issue of this library. Can be 100, 250, 500, 1000,
                        2000, 5000, 10000, 20000, 50000, or 62500.
        :return data_ndarray, waveform_preamble_dict: see waveform_preamble property for dict format.
        """
        # TODO: Consider downloading from multiple sources at the same time.
        self.waveform_source = source
        self.waveform_points_mode = "normal"
        self.waveform_points = points

        preamble = self.waveform_preamble
        data_bytes = self.waveform_data
        return np.array(data_bytes), preamble

    def _waveform_preamble(self):
        """
        Reads waveform preamble and converts it to a more convenient dict of values.
        """
        vals = self.values(":waveform:preamble?")
        # Get values to dict
        vals_dict = dict(zip(["format", "type", "points", "count", "xincrement", "xorigin",
                              "xreference", "yincrement", "yorigin", "yreference"], vals))
        # Map element values
        format_map = {0: "BYTE", 1: "WORD", 2: "ASCII"}
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