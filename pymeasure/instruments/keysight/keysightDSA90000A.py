#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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
from time import sleep, time

class Channel():
    """ Implementation of a Keysight DSA 90000A Oscilloscope channel. Note, that is
    90000 (four zeroes, not to be confused with 9000, three zeroes) followed by an A.
    There is command overlap between other models, but the limits change

    Implementation modeled on Channel object of Tektronix AFG3152C instrument. Majority of
     driver re-used from  DSOX1102G. Maybe this is a deep statement about a base oscilloscope class.
     """

    BOOLS = {True: 1, False: 0}

    bwlimit = Instrument.control(
        "ISIM:BANDwidth?", "ISIM:BANDwidth %g",
        """ A float parameter that sets a custom bandwidth (cutoff frequency). Must be enable
        or disabled by setting the enable_bwlimit parameter.
        Can be anywhere from 1e3 to sample rate/2. Currently implemented as [1e9,50e9].""",
        validator=strict_range,
        values=[1e3,50e9],
    )

    enable_bwlimit = Instrument.control(
        "ISIM:BWLimit?", "ISIM:BWLimit %d",
        """ A boolean parameter that enables or disables the bw cutoff specified by 
        bwlimit.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    bwlimit_type = Instrument.control(
        "ISIM:BWLimit:TYPE?", "ISIM:BWLimit:TYPE %s",
        """ A string parameter that specifies the type of filter that implements the 
        bandwidth limit specified in bwlimit and enabled by enable_bwlimit. Options are:
        'WALL': Specifies a Brick-Wall response filter. Sharp roll-off
        'BESSEL4': Specifies a 4-th order Bessel filter. More gradual roll off.
        'BANDPASS': This option is for use with the Phase Noise analysis application [not
        implemented in this driver]. Included for completeness.""",
        validator=strict_discrete_set,
        values=['WALL', 'BESSEL4', 'BANDPASS']
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
        Volts. The range of legal values varies depending on range and scale. If the specified value 
        is outside of the legal range, the offset value is automatically set to the nearest legal value. """
    )

    probe_attenuation = Instrument.control(
        "PROBe?", "PROBe %f,RAT",
        """ A float parameter that specifies the probe attenuation as a ratio. The probe attenuation
        may be from 0.1 to 10000.""",
        validator=strict_range,
        values=[0.1, 10000]
    )

    range = Instrument.control(
        "RANGe?", "RANGe %f",
        """ A float parameter that specifies the full-scale vertical axis in Volts. 
        When using 1:1 probe attenuation, legal values for the 91204A range from 8 mV to 800 mV."""
    )

    scale = Instrument.control(
        "SCALe?", "SCALe %f",
        """ A float parameter that specifies the vertical scale, or units per division, in Volts. 
        Limits are [1e-3,1] for the 91204A range"""
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

    def setup(self, display=None, invert=None, label=None, offset=None,
              probe_attenuation=None, vertical_range=None, scale=None):
        """ Setup channel. Unspecified settings are not modified. Modifying values such as
        probe attenuation will modify offset, range, etc. Refer to oscilloscope documentation and make
        multiple consecutive calls to setup() if needed.

        :param display: A boolean, which enables channel display.
        :param invert: A boolean, which enables input signal inversion.
        :param label: Label string with max. 10 characters, may contain commonly used ASCII characters.
        :param offset: Numerical value represented at center of screen, must be inside the legal range.
        :param probe_attenuation: Probe attenuation values from 0.1 to 1000.
        :param vertical_range: Full-scale vertical axis of the selected channel. When using 1:1 probe
                                attenuation, legal values for the range are  from 8mV to 40 V. If the
                                probe attenuation is changed, the range value is multiplied by the
                                probe attenuation factor.
        :param scale: Units per division. """

        if vertical_range is not None and scale is not None:
            log.warning('Both "vertical_range" and "scale" are specified. Specified "scale" has priority.')

        if probe_attenuation is not None: self.probe_attenuation = probe_attenuation
        if display is not None: self.display = display
        if invert is not None: self.invert = invert
        if label is not None: self.label = label
        if offset is not None: self.offset = offset
        if vertical_range is not None: self.range = vertical_range
        if scale is not None: self.scale = scale


class KeysightDSA90000A(Instrument):
    """ Represents the Keysight DSA90000A Oscilloscope interface for interacting
    with the instrument.

    Refer to the Keysight DSA90000A Oscilloscope Programmer's Guide for further details about
    using the lower-level methods to interact directly with the scope.

    .. code-block:: python
    
        scope = KeysightDSA90000A(resource)
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
        super(KeysightDSA90000A, self).__init__(
            adapter, "Keysight DSA90000A Oscilloscope", **kwargs
        )
        # Account for setup time for timebase_mode, waveform_points_mode
        self.adapter.connection.timeout = 6000
        self.ch1 = Channel(self, 1)
        self.ch2 = Channel(self, 2)
        self.ch3 = Channel(self, 3)
        self.ch4 = Channel(self, 4)
        self.system_headers = False

    system_headers = Instrument.control(
        ":SYSTem:HEADer?", ":SYSTem:HEADer %d",
        """ A boolean parameter controlling whether or not the oscope returns headers with queries""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    #################
    # Channel setup #
    #################

    def autoscale(self):
        """ Autoscale displayed channels. """
        self.write(":autoscale")

    ##################
    # Timebase Setup #
    ##################


    timebase_offset = Instrument.control(
        ":TIMebase:POSition?", ":TIMebase:REFerence CENTer;:TIMebase:POSition %.4E",
        """ A float parameter that sets the time interval in seconds between the trigger 
        event and the reference position (at center of screen by default)."""
    )

    timebase_range = Instrument.control(
        ":TIMebase:RANGe?", ":TIMebase:RANGe %.4E",
        """ A float parameter that sets the full-scale horizontal time in seconds for the 
        main window."""
    )

    timebase_scale = Instrument.control(
        ":TIMebase:SCALe?", ":TIMebase:SCALe %.4E",
        """ A float parameter that sets the horizontal scale (units per division) in seconds 
        for the main window."""
    )

    ###########
    # Trigger #
    ###########

    trigger_holdoff = Instrument.control(
        ":TRIGger:HOLDoff?", ":TRIGger:HOLDoff %.4E",
        """ A float control that sets the time before the oscilloscope should wait
        after receiving a trigger to enable the trigger again. Range is [1e-9,10] s.""",
        validator=strict_range,
        values=[1e-9,10]
    )

    trigger_holdoff_mode = Instrument.control(
        ":TRIGger:HOLDoff:MODE?", ":TRIGger:HOLDoff:MODE %s",
        """ A string control that sets the holdoff mode to FIXED (rearm delay specified by trigger_holdoff)
         or RANDOM (not implemented yet in this driver).""",
        validator=strict_discrete_set,
        values=['fixed', 'random']
    )

    trigger_hysteresis = Instrument.control(
        ":TRIGger:HYSTeresis?", ":TRIGger:HYSTeresis %s",
        """ A string control that sets the noise rejection type on the trigger. For the 90000 (four zeros) series,
        your options are norm (normal) and hsen (lowers hysteresis of trigger circuitry, use for wfs > 4 GHz)""",
        validator=strict_discrete_set,
        values=['norm', 'hsen']
    )

    trigger_mode = Instrument.control(
        ":TRIGger:MODE?", ":TRIGger:MODE %s",
        """ A string control that sets the trigger mode. Consult the manual for advanced options. 
        EDGE is the most common option""",
        validator=strict_discrete_set,
        values=['EDGE', 'COMM', 'DELAY', 'GLIT', 'PATT', 'PWID', 'RUNT', 'SBUS1', 'SBUS2', 'SBUS3', 'SBUS4',
                'SEQ', 'SHOL', 'STAT', 'TIM', 'TRAN', 'TV', 'WIND', 'ADV']
    )

    trigger_sweep = Instrument.control(
        ":TRIGger:SWEep?", ":TRIGger:SWEep %s",
        """ A string control that sets the oscilloscope sweep mode. 'sing' is a legacy option. 
        If the scope is set to single() and this is 'auto' the scope will force a trigger every 200 us.
        Use 'trig' if your waveform may occur >200 us after single() is called (in general, probably just use 'trig')
        Factory default is 'auto'""",
        validator=strict_discrete_set,
        values=['sing', 'auto', 'trig']
    )

    trigger_edge_slope = Instrument.control(
        ":TRIGger:EDGE:SLOPe?", ":TRIGger:EDGE:SLOPe %s",
        """ A string control that sets the slope of the edge trigger to:
        'pos', 'neg', or 'eith' (either)""",
        validator=strict_discrete_set,
        values=['pos', 'neg', 'eith']
    )

    def trigger_level(self,channel, level):
        """
        Function to set the trigger level on the specified channel  (channel 0 is aux).
        NOTE: This does not change the trigger source.
        :param channel: Integer corresponding to a given channel (0 is aux)
        :param level: level of trigger in V
        :return:
        """
        if channel == 0:
            source = 'AUX'
        elif channel in [1,2,3,4]:
            source = 'CHAN%d' % channel
        else:
            raise ValueError(f'{channel} not a valid trigger source')
        self.write(':TRIGger:LEVel %s, %f' % (source, level))

    def trigger_edge_source(self,channel):
        """
        Function to set the edge trigger source
        :param channel: Integer corresponding to a given channel (0 is aux)
        :return:
        """
        if channel == 0:
            source = 'AUX'
        elif channel in [1,2,3,4]:
            source = 'CHAN%d' % channel
        else:
            raise ValueError(f'{channel} not a valid trigger source')
        self.write(':TRIGger:EDGE:SOURce %s' % (source))

    def set_edge_trigger(self, source, level, slope):
        """
        Convenience function to set the scope trigger to edge, source to channel source at the specified level
        """
        self.trigger_mode = 'EDGE'
        self.trigger_level(source, level)
        self.trigger_edge_slope = slope
        self.trigger_edge_source(source)

    ###############
    # Acquisition #
    ###############

    enable_averaging = Instrument.control(
        ":ACQuire:AVER?", ":ACQuire:AVER %d",
        """ A boolean parameter controlling where averaging is turned off or on.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    average_n = Instrument.control(
        ":ACQuire:COUNt?", ":ACQuire:COUNt %d",
        """ A integer parameter controlling the number of averages provided averaging is turned on.""",
        validator=strict_range,
        values=[2,65534],
    )

    acquisition_mode = Instrument.control(
        ":ACQuire:MODE?", ":ACQuire:MODE %s",
        """ A string parameter that sets the acquisition mode. Can be "realtime", "segmented", 'hresolution.""",
        validator=strict_discrete_set,
        values={"realtime": "RTIM", "segmented": "SEGM", "hresolution": "HRES"},
        map_values=True
    )

    acquisition_bandwidth = Instrument.control(
        ":ACQuire:BANDwidth?", "ACQuire:BANDwidth %s",
        """A mixed parameter that sets the acquisition bandwith. Can be 'AUTO', 'MAX',
        or a very specific set of real numbers according to you model. For the 91204A it is:
        12e9, 10e9, 8e9, 6e9, 4e9, 3e9, 2.5e9, 2e9, 1e9"""
    )

    acquisition_srate = Instrument.control(
        ":ACQuire:SRATe?", "ACQuire:SRATe %s",
        """A mixed parameter that sets the acquisition sample rate. Can be 'AUTO', 'MAX',
        or a very specific set of real numbers according to you model."""
    )

    state = Instrument.measurement(
        ":ASTate?",
        """Returns the acquisition state of the oscilloscope. 
         ARM : the trigger is armed and the oscilloscope has acquired all of the pre-trigger data
         TRIG : The trigger condition has occurred and the oscilloscope is acquiring post trigger data
         ATRIG : The trigger condition has not been met, but the oscillscope has auto triggered and is acquiring
         post trigger data
         ADONE : The acquisition is done and the data has been processed and is ready to be unloaded"""
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

    @property
    def pder(self):
        return int(self.ask(':PDER?'))

    def wait_for_acquisition(self, tdelta=.1, n_it=1000 ):
        breaker = 0
        while self.pder == 0 and breaker < n_it:
            sleep(tdelta)
            breaker = breaker + 1

    def wait_for_op(self, timeout=10, should_stop=lambda : False):
        self.write("*OPC?")

        t0 = time()
        while True:
            try:
                ready = bool(self.read())
            except VisaIOError:
                ready = False

            if ready:
                return

            if timeout != 0 and time() - t0 > timeout:
                raise TimeoutError(
                    "Timeout expired while waiting for the Agilent 33220A" +
                    " to finish the triggering."
                )

            if should_stop():
                return


    _digitize = Instrument.setting(
        ":DIGitize %s",
        """ Acquire waveforms according to the settings of the :ACQuire commands and specified source,
         as a string parameter that can take the following values: "channel1", "channel2", "channel3", "channel4"
          "function", "math", "fft", "abus", or "ext", "current". """,
        validator=strict_discrete_set,
        values={"channel1": "CHAN1", "channel2": "CHAN2","channel3": "CHAN3",
                "channel4": "CHAN4", "function": "FUNC", "math": "MATH",
                "fft": "FFT", "abus": "ABUS", "ext": "EXT", "current": ''},
        map_values=True
    )

    def digitize(self, source: str):
        """ Acquire waveforms according to the settings of the :ACQuire commands. Ensure a delay
        between the digitize operation and further commands, as timeout may be reached before
        digitize has completed.
        :param source: "channel1", "channel2", "function", "math", "fft", "abus", "ext", or "current."""
        self._digitize = source

    waveform_points_mode = Instrument.measurement(
        ":waveform:type?",
        """ A string measurement that returns the type of waveform data. The type cannot be set here.
        It is set by other parameters on the scope""",
    )

    waveform_source = Instrument.control(
        ":waveform:source?", ":waveform:source %s",
        """ A string parameter that selects the analog channel, function, or reference waveform 
        to be used as the source for the waveform methods. Can be "channel1", "channel2", "function", 
        "fft", "wmemory1", "wmemory2", or "ext".""",
        validator=strict_discrete_set,
        values={"channel1": "CHAN1", "channel2": "CHAN2", "channel3": "CHAN3",
                "channel4": "CHAN4", "function": "FUNC", "fft": "FFT",
                "wmemory1": "WMEM1", "wmemory2": "WMEM2", "ext": "EXT"},
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

    waveform_byteorder = Instrument.control(
        ":waveform:byteorder?", ":waveform:byteorder %s",
        """ A string parameter that endianess of the transmitted data. options are 'big' or 'little'""",
        validator=strict_discrete_set,
        values={"little": "LSBF", "big": "MSBF"},
        map_values=True
    )

    waveform_streaming = Instrument.control(
        ":waveform:streaming?", ":SYSTem:streaming %d",
        """ A boolean parameter controlling whether or not the oscope streams data when queried for data""",
        validator=strict_discrete_set,
        values=BOOLS,
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
            - "yreference": data point associated with yorigin (int)"""
        return self._waveform_preamble()

    def get_waveform_subpart(self, start, size, format='word', byteorder='little'):
        """
        Function to grab only a subpart of the waveform acquired. Start is the integer of the starting point in the
        record, size is the integer length of the record you want to get back. You will likely need to calculate
        this from the xincrement as acquired from waveform_preamble. You can specify the format as "word" [default]
        or "ascii". The default byteorder is little.
        """

        self.waveform_format = format
        self.waveform_byteorder = byteorder
        if not isinstance(start, int):
            raise TypeError(f"start is of type {type(start)} not int")
        if not isinstance(size, int):
            raise TypeError(f"size is of type {type(size)} not int")
        data = self.values(f"waveform:data? {start},{size}")

        return data

    @property
    def waveform_data_ascii(self):
        """ Get the ascii block of sampled data points transmitted using the IEEE 488.2 arbitrary
        block data format."""
        # Other waveform formats raise UnicodeDecodeError
        self.waveform_format = "ascii"

        data = self.values(":waveform:data?")
        # Strip header from first data element

        return data

    @property
    def waveform_data_word(self):
        """ Get the block of sampled data points transmitted using the IEEE 488.2 arbitrary
        block data format."""
        # Other waveform formats raise UnicodeDecodeError
        self.waveform_format = "word"
        self.waveform_byteorder = 'little'
        self.waveform_streaming = False

        data = self.adapter.connection.query_binary_values(":waveform:data?", datatype = 'h')
        # Strip header from first data element
        #data[0] = float(data[0][10:])

        return data

    def get_waveform_data_word_subpart(self,start,points):
        """ Get the block of sampled data points transmitted using the IEEE 488.2 arbitrary
        block data format."""
        # Other waveform formats raise UnicodeDecodeError
        self.waveform_format = "word"
        self.waveform_byteorder = 'little'
        self.waveform_streaming = False

        data = self.adapter.connection.query_binary_values(f":waveform:data? {start}, {points}", datatype = 'h')
        # Strip header from first data element
        #data[0] = float(data[0][10:])

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

    def timebase_setup(self, offset=None, horizontal_range=None, scale=None):
        """ Set up timebase. Unspecified parameters are not modified. Modifying a single parameter might
        impact other parameters. Refer to oscilloscope documentation and make multiple consecutive calls
        to channel_setup if needed.

        :param mode: Timebase mode, can be "main", "window", "xy", or "roll".
        :param offset: Offset in seconds between trigger and center of screen.
        :param horizontal_range: Full-scale range in seconds.
        :param scale: Units-per-division in seconds."""

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
        vals = vals[:9]
        # Get values to dict
        vals_dict = dict(zip(["format", "type", "points", "count", "xincrement", "xorigin",
                              "xreference", "yincrement", "yorigin", "yreference"], vals))
        # Map element values
        format_map = {0: "ASCII", 1: "BYTE", 2: "WORD", 3: "LONG", 4: "LONGLONG", 5: 'FLOAT'}
        type_map = {1: "RAW", 2: "AVER", 3: "VHIS", 4: "HHIS", 6: 'INT', 9: 'DIGITAL', 10: 'PDET'}
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
