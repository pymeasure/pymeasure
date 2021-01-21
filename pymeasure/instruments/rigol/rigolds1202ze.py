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
import os
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class RigolDS1202ZE_Channel():
    """ Modification of the pymeasure Keysight DSOX1102G Oscilloscope class.
    Made to implement within the RigolDS1202ZE scope class """

    BOOLS = {True: 1, False: 0}

    bwlimit = Instrument.control(
        "BWLimit?", "BWLimit %d",
        """ A boolean parameter that toggles 20 MHz internal low-pass filter.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    coupling = Instrument.control(
        "COUPling?", "COUPling %s",
        """ A string parameter that determines the coupling ("ac" or "dc").""",
        validator=strict_discrete_set,
        values={"ac": "AC", "dc": "DC", "gnd": "GND"},
        map_values=True
    )

    # display = Instrument.control(
    #     "DISPlay?", "DISPlay %d",
    #     """ A boolean parameter that toggles the display.""",
    #     validator=strict_discrete_set,
    #     values=BOOLS,
    #     map_values=True
    # )

    invert = Instrument.control(
        "INVert?", "INVert %d",
        """ A boolean parameter that toggles the inversion of the input signal.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    # label = Instrument.control(
    #     "LABel?", 'LABel "%s"',
    #     """ A string to label the channel. Labels with more than 10 characters are truncated to 10
    #     characters. May contain commonly used ASCII characters. Lower case characters are converted
    #     to upper case.""",
    #     get_process=lambda v: str(v[1:-1])
    # )

    offset = Instrument.control(
        "OFFSet?", "OFFSet %f",
        """ A float parameter to set value that is represented at center of screen in 
        Volts. The range of legal values varies depending on range and scale. If the specified value 
        is outside of the legal range, the offset value is automatically set to the nearest legal value. """
    )

    probe_attenuation = Instrument.control(
        "PROBe?", "PROBe %f",
        """ A float parameter that specifies the probe attenuation. The probe attenuation
        may be from 0.1 to 10000.""",
        validator=strict_discrete_set,
        values=[0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
    )

    range = Instrument.control(
        "RANGe?", "RANGe %f",
        """ A float parameter that specifies the full-scale vertical axis in Volts.
        When using 1:1 probe attenuation, legal values for the range are from 8 mV to 40V."""
    )

    scale = Instrument.control(
        "SCALe?", "SCALe %f",
        """ A float parameter that specifies the vertical scale, or units per division, in Volts."""
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
        probe attenuation will modify offset, range, etc. Refer to oscilloscope documentation and make
        multiple consecutive calls to setup() if needed.
        :param bwlimit: A boolean, which enables 25 MHz internal low-pass filter.
        :param coupling: "ac" or "dc".
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
        if bwlimit is not None: self.bwlimit = bwlimit
        if coupling is not None: self.coupling = coupling
        if display is not None: self.display = display
        if invert is not None: self.invert = invert
        if label is not None: self.label = label
        if offset is not None: self.offset = offset
        if vertical_range is not None: self.range = vertical_range
        if scale is not None: self.scale = scale

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

        # Using the instrument's ask method because Channel.ask() adds the prefix ":channelX:", and to query the
        # configuration details, we actually need to ask ":channelX?", without a second ":"
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


class RigolDS1202ZE(Instrument):
    """ modification of the pymeasure Keysight DSOX1102G Oscilloscope class for the Rigol DS1202Z-E
    Refer to the Rigol DS1202Z-E Oscilloscope Programmer's Guide for further details about
    using the lower-level methods to interact directly with the scope.
    .. code-block:: python

        scope = KeysightDSOX1102G(resource)
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
        super(RigolDS1202ZE, self).__init__(
            adapter, "Rigol DS1202Z-E Oscilloscope", **kwargs
        )
        # Account for setup time for timebase_mode, waveform_points_mode
        self.adapter.connection.timeout = 6000
        self.ch1 = RigolDS1202ZE_Channel(self, 1)
        self.ch2 = RigolDS1202ZE_Channel(self, 2)

    #################
    # Channel setup #
    #################

    def autoscale(self):
        """ Autoscale displayed channels. """
        self.write(":autoscale")

    ##################
    # Timebase Setup #
    ##################

    # @property
    # def timebase(self):
    #     """ Read timebase setup as a dict containing the following keys:
    #         - "REF": position on screen of timebase reference (str)
    #         - "MAIN:RANG": full-scale timebase range (float)
    #         - "POS": interval between trigger and reference point (float)
    #         - "MODE": mode (str)"""
    #     return self._timebase()

    timebase_mode = Instrument.control(
        ":TIMebase:MODE?", ":TIMebase:MODE %s",
        """ A string parameter that sets the current time base. Can be "main", 
        "window", "xy", or "roll" corresponding to YT, XY, ROLL.""",
        validator=strict_discrete_set,
        values={"main": "MAIN", "window": "WIND", "xy": "XY", "roll": "ROLL"},
        map_values=True
    )

    timebase_offset = Instrument.control(
        ":TIMebase:MAIN:OFFSet?", ":TIMebase:MAIN:OFFSet %f",
        """ A float parameter that sets the time interval in seconds between the trigger 
        event and the reference position (at center of screen by default)."""
    )

    # timebase_range = Instrument.control(
    #     ":TIMebase:RANGe?", ":TIMebase:RANGe %f",
    #     """ A float parameter that sets the full-scale horizontal time in seconds for the
    #     main window."""
    # )

    timebase_scale = Instrument.control(
        ":TIMebase:MAIN:SCALe?", ":TIMebase:MAIN:SCALe %f",
        """ A float parameter that sets the horizontal scale (units per division) in seconds 
        for the main window."""
    )

    ###############
    # Acquisition #
    ###############

    acquisition_averages = Instrument.control(
        ":ACQuire:AVERages?", ":ACQuire:AVERages %i",
        """ An integer parameter that sets the number of averages. Can be 2^n where n is integer from 1 to 10.""",
        validator=strict_discrete_set,
        values=[2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    )

    acquisition_type = Instrument.control(
        ":ACQuire:TYPE?", ":ACQuire:TYPE %s",
        """ A string parameter that sets the type of data acquisition. Can be "normal", "average",
        "hresolution", or "peak".""",
        validator=strict_discrete_set,
        values={"normal": "NORM", "average": "AVER", "hresolution": "HRES", "peak": "PEAK"},
        map_values=True
    )

    # need to add if statement checking if 1 or 2 channels are enabled bec if so the values if two channels are
    # enabled is half that of only 1 being enabled
    acquisition_memory_depth = Instrument.control(
        ":ACQuire:MDEPth?", ":ACQuire:MDEPth %s", ":ACQuire:MDEPth %i"
        """ An integer parameter that sets the number of waveform points to be transferred with
        the waveform_data method. Can be any of the following values if 1 channel is enabled
        "AUTO", 12000, 120000, 1200000, 12000000, 24000000
        or if two channels are enbled can take values :"AUTO", 6000, 60000, 600000, 6000000,12000000
        Note that the oscilloscope may provide less than the specified nb of points. 
        
        Memory Depth = Sample Rate x Waveform Length
        Wherein, the Waveform Length is the product of the horizontal timebase (set by
        the :TIMebase[:MAIN]:SCALe command) times the number of grids in the horizontal
        direction on the screen (12 for DS1000Z-E).
        When AUTO is selected, the oscilloscope will select the memory depth automatically
        according to the current sample rate""",
        validator=strict_discrete_set,
        values=["AUTO", 12000, 120000, 1200000, 12000000, 24000000]
    )

    acquisition_sample_rate = Instrument.control(
        ":ACQuire:SRate?",
        """Query the current sample rate. The default unit is Sa/s. Sample rate is the sample 
        frequency of the oscilloscope, namely the waveform points sampled per second.
        The following equation describes the relationship among memory depth, sample rate, and waveform length:
        
        Memory Depth = Sample Rate x Waveform Length
        
        Wherein, the Memory Depth can be set using the :ACQuire:MDEPth command, and
        the Waveform Length is the product of the horizontal timebase (set by
        the :TIMebase[:MAIN]:SCALe command) times the number of the horizontal scales
        (12 for DS1000Z-E)..""", docs=None
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

    def force_trigger(self):
        """Generate a trigger signal forcefully. This command is only applicable to the normal and
        single trigger modes (see the :TRIGger:SWEep command) and is equivalent to pressing
        the FORCE key in the trigger control area on the front panel."""
        self.write(":TFORCE")

    # _digitize = Instrument.setting(
    #     ":DIGitize %s",
    #     """ Acquire waveforms according to the settings of the :ACQuire commands and specified source,
    #      as a string parameter that can take the following values: "channel1", "channel2", "function",
    #      "math", "fft", "abus", or "ext". """,
    #     validator=strict_discrete_set,
    #     values={"channel1": "CHAN1", "channel2": "CHAN2", "function": "FUNC", "math": "MATH",
    #             "fft": "FFT", "abus": "ABUS", "ext": "EXT"},
    #     map_values=True
    # )

    # def digitize(self, source: str):
    #     """ Acquire waveforms according to the settings of the :ACQuire commands. Ensure a delay
    #     between the digitize operation and further commands, as timeout may be reached before
    #     digitize has completed.
    #     :param source: "channel1", "channel2", "function", "math", "fft", "abus", or "ext"."""
    #     self._digitize = source

    waveform_points_mode = Instrument.control(
        ":waveform:mode?", ":waveform:mode %s",
        """ A string parameter that sets the data record to be transferred with the waveform_data
         method. Can be "normal", "maximum", or "raw".""",
        validator=strict_discrete_set,
        values={"normal": "NORM", "maximum": "MAX", "raw": "RAW"},
        map_values=True
    )
    waveform_source = Instrument.control(
        ":waveform:source?", ":waveform:source %s",
        """ A string parameter that selects the analog channel, function, or reference waveform 
        to be used as the source for the waveform methods. Can be "channel1", "channel2", "math""",
        validator=strict_discrete_set,
        values={"channel1": "CHAN1", "channel2": "CHAN2", "math": "MATH"},
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

    @property
    def waveform_preamble(self):
        """ Get preamble information for the selected waveform source as a dict with the following keys:
            - "format": byte, word, or ascii (str)
            - "type":  0 (NORMal), 1 (MAXimum) or 2 (RAW) (str)
            - "points": an integer between 1 and 24000000(int)
            - "count": the number of averages in the average sample mode and 1 in other modes (int)
            - "xincrement": the time difference between two neighboring points in the X direction (float)
            - "xorigin": first data point in memory (float)
            - "xreference": data point associated with xorigin (int)
            - "yincrement": voltage difference between data points (float)
            - "yorigin":  the vertical offset relative to the "Vertical Reference Position" in the Y
                            direction. ie voltage at center of screen (float)
            - "yreference": data point associated with yorigin (int)"""
        return self._waveform_preamble()

    #@property
    def waveform_data(self, source, points=1000, filename=None):
        #TODO: need to figure out how to read data in byte format, currently it is only in ascii format which allows
        # for less elements to be gathered from the scopes buffer.. see the Tip below for further explanation

        """ Get the binary block of sampled data points transmitted using the IEEE 488.2 arbitrary
        block data format.

        Tip:(taken directly from Rigol DS1202ZE programming manual)
            When reading the waveform data in the internal memory, the maximum number
            of waveform points can be read each time the :WAV:DATA? command is sent is
            related to the return format of the waveform data currently selected, as shown
            in the table below.

            Return Format of the Waveform Data | Maximum Number of Waveform Points can be Read Each Time
            (note can not necessarily read the entire buffer on one read depending on the waveform format)
            BYTE                               | BYTE 250000
            WORD                               | WORD 125000
            ASCii                              | ASCii 15625

            Before reading the waveform data in the internal memory, you need to judge
            whether the waveform data can all be read at one time according to the memory
            depth of the oscilloscope and the maximum number of waveform points that can
            be read each time (refer to the table above).

            1) When the memory depth of the oscilloscope is lower than or equal to the
            maximum number of waveform points that can be read each time, the
            waveform data in the internal memory can all be read at one time by
            specifying the start point and stop point.

            2) When the memory depth of the oscilloscope is greater than the maximum
            number of waveform points that can be read each time, the waveform data
            in the internal memory need to be read in several batches by specifying the
            start point and stop point. Each time, only the waveform data in one area of
            the internal memory is read (the waveform data of two neighbouring areas
            are continuous); then, you need to combine the waveform data that are
            read separately in sequence."""

        # Other waveform formats raise UnicodeDecodeError

        self.run()
        self.write(":STOP")
        self.waveform_source = source
        self.waveform_format = "ascii"
        self.waveform_points_mode = "normal"
        self.acquisition_memory_depth = points

        preamble = self.waveform_preamble


        max_num_pts = 15625
        num_blocks = preamble['points'] // max_num_pts
        last_block_pts = preamble['points'] % max_num_pts

        datas = []
        for i in range(num_blocks + 1):
            if i < num_blocks:
                self.write(':wav:star %i' % (1 + i * 250000))
                self.write(':wav:stop %i' % (250000 * (i + 1)))
            else:
                if last_block_pts:
                    self.write(':wav:star %i' % (1 + num_blocks * 250000))
                    self.write(':wav:stop %i' % (num_blocks * 250000 + last_block_pts))
                else:
                    break
            #first value is a string in ascii format
            data = self.values(':wav:data?')[1:]
            datas.append(data)

        datas = np.concatenate(datas)
        #reads in ascii format dont need to account for offsets on scope???? that is why below line
        #voltage_array = (datas - preamble['yorigin'] - preamble['yreference']) * preamble['yincrement']
        voltage_array = datas

        time_array = np.arange(0, preamble['points'] * preamble['xincrement'], preamble['xincrement'])
        # info['xorigin'] + info['xreference']

        if filename:
            try:
                os.remove(filename)
            except OSError:
                pass
            np.savetxt(filename, np.c_[time_array, voltage_array], '%.12e', ',')

        #when using the ascii mode the first value give when you query data? is an a valid waveform point but is a
        #string for some reason.. therefore to output arrays of equal size i just take off the fist point
        # of both voltage and time array
        return time_array[1:], voltage_array

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
                errmsg = "Rigol DS1202ZE: %s: %s" % (err[0], err[1])
                log.error(errmsg + "\n")
            else:
                break

    def clear_status(self):
        """ Clear device status. """
        self.write(":CLEAR")

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

    # def get_data(self, source, points=62500):
    #     """ Get data from specified source of oscilloscope. Returned objects are a np.ndarray of data
    #     values (no temporal axis) and a dict of the waveform preamble, which can be used to build the
    #     corresponding time values for all data points.
    #     Multimeter will be stopped for proper acquisition.
    #     :param source: measurement source, can be "channel1", "channel2", "function", "fft", "wmemory1",
    #                     "wmemory2", or "ext".
    #     :param points: integer number of points to acquire. Note that oscilloscope may return less points than
    #                     specified, this is not an issue of this library. Can be 100, 250, 500, 1000,
    #                     2000, 5000, 10000, 20000, 50000, or 62500.
    #     :return data_ndarray, waveform_preamble_dict: see waveform_preamble property for dict format.
    #     """
    #     # TODO: Consider downloading from multiple sources at the same time.
    #     self.waveform_source = source
    #     self.waveform_points_mode = "normal"
    #     self.waveform_points = points
    #
    #     data_bytes = self.values(':wav:data?')
    #     return data_bytes

    # def _timebase(self):
    #     """
    #     Reads setup data from timebase and converts it to a more convenient dict of values.
    #     """
    #     tb_setup_raw = self.ask(":timebase?").strip("\n")
    #
    #     # tb_setup_raw hat the following format:
    #     # :TIM:MODE MAIN;REF CENT;MAIN:RANG +1.00E-03;POS +0.0E+00
    #
    #     # Cut out the ":TIM:" at beginning and split string
    #     tb_setup_splitted = tb_setup_raw[5:].split(";")
    #
    #     # Create dict of setup parameters
    #     tb_setup = dict(map(lambda v: v.split(" "), tb_setup_splitted))
    #
    #     # Convert values to specific type
    #     to_str = ["MODE", "REF"]
    #     to_float = ["MAIN:RANG", "POS"]
    #     for key in tb_setup:
    #         if key in to_str:
    #             tb_setup[key] = str(tb_setup[key])
    #         elif key in to_float:
    #             tb_setup[key] = float(tb_setup[key])
    #
    #     return tb_setup

    def _waveform_preamble(self):
        """
        Reads waveform preamble and converts it to a more convenient dict of values.
        """
        vals = self.values(":waveform:preamble?")
        # Get values to dict
        vals_dict = dict(zip(["format", "type", "points", "count", "xincrement", "xorigin",
                              "xreference", "yincrement", "yorigin", "yreference"], vals))
        # Map element values
        format_map = {0: "BYTE", 1: "WORD", 2: "ASC"}
        type_map = {0: "NORMal", 1: "MAXimum", 2: "RAW"}
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


#from jdsypymeasure.pymeasure.instruments.rigol.rigolds1202ze import RigolDS1202ZE ;
from jdsypymeasure.pymeasure.adapters.visa import VISAAdapter ;
scope_adapter = VISAAdapter("RigolDS1202ZE") ;
scope = RigolDS1202ZE(adapter=scope_adapter) ;
time, voltage = scope.waveform_data("channel2", points=12000)
time2, voltage2 = scope.waveform_data("channel2", points=12000)
import matplotlib.pyplot as plt

plt.plot(time,voltage)
plt.show()

