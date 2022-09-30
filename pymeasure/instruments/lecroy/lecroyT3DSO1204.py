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

import logging
import re
import sys

import numpy as np

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# noinspection DuplicatedCode
class Channel:
    """ Implementation of a LeCroy T3DSO1204 Oscilloscope channel.

    Implementation modeled on Channel object of Keysight DSOX1102G instrument. """

    _BOOLS = {True: "ON", False: "OFF"}

    bwlimit = Instrument.control(
        "BWL?", "BWL %s",
        """ A string parameter that toggles 20 MHz internal low-pass filter ("ON", "OFF").""",
        validator=strict_discrete_set,
        values=_BOOLS,
        map_values=True
    )

    coupling = Instrument.control(
        "CPL?", "CPL %s",
        """ A string parameter that determines the coupling ("AC 1M", "DC 1M", "GND").""",
        validator=strict_discrete_set,
        values={"AC 1M": "A1M", "DC 1M": "D1M", "GND": "GND"},
        map_values=True
    )

    display = Instrument.control(
        "TRA?", "TRA %s",
        """ A string parameter that toggles the display ("ON", "OFF").""",
        validator=strict_discrete_set,
        values=_BOOLS,
        map_values=True
    )

    invert = Instrument.control(
        "INVS?", "INVS %s",
        """ A string parameter that toggles the inversion of the input signal ("ON", "OFF").""",
        validator=strict_discrete_set,
        values=_BOOLS,
        map_values=True
    )

    offset = Instrument.control(
        "OFST?", "OFST %eV",
        """ A float parameter to set value that is represented at center of screen in
        Volts. The range of legal values varies depending on range and scale. If the specified
        value is outside of the legal range, the offset value is automatically set to the nearest
        legal value.
        """
    )

    skew_factor = Instrument.control(
        "SKEW?", "SKEW %eS",
        """ Channel-tochannel skew factor for the specified channel. Each analog channel can be adjusted + or -100 ns 
        for a total of 200 ns difference between channels. You can use the oscilloscope's skew control to remove 
        cable-delay errors between channels.
        """,
        validator=strict_range,
        values=[-100, 100]
    )

    probe_attenuation = Instrument.control(
        "ATTN?", "ATTN %s",
        """ A string parameter that specifies the probe attenuation. The probe attenuation
        may be from 0.1 to 10000.""",
        validator=strict_discrete_set,
        values={"0.1", "0.2", "0.5", "1", "2", "5", "10", "20", "50", "100", "200", "500", "1000", "2000", "5000",
                "10000"}
    )

    scale = Instrument.control(
        "VDIV?", "VDIV %e",
        """ A float parameter that specifies the vertical scale, or units per division, in Volts."""
    )

    unit = Instrument.control(
        "UNIT?", "UNIT %s",
        """ Unit of the specified trace. Measurement results, channel sensitivity, and trigger level will reflect the 
        measurement units you select. ("A" for Amperes, "V" for Volts).""",
        validator=strict_discrete_set,
        values={"A", "V"}
    )

    trigger_coupling = Instrument.control(
        "TRCP?", "TRCP %s",
        """ A string parameter that specifies the input coupling for the selected trigger sources.
        • ac    — AC coupling block DC component in the trigger path, removing dc offset voltage from the trigger 
                  waveform. Use AC coupling to get a stable edge trigger when your waveform has a large dc offset.
        • dc    — DC coupling allows dc and ac signals into the trigger path.
        • lowpass  — HFREJ coupling places a lowpass filter in the trigger path.
        • highpass — LFREJ coupling places a highpass filter in the trigger path.
        """,
        validator=strict_discrete_set,
        values={"ac": "AC", "dc": "DC", "lowpass": "HFREJ", "highpass": "LFREJ"},
        map_values=True
    )

    trigger_level = Instrument.control(
        "TRLV?", "TRLV %eV",
        """ A float parameter that sets the trigger level voltage for the active trigger source. 
            When there are two trigger levels to set, this command is used to set the higher trigger 
            level voltage for the specified source. TRLV2 is used to set the lower trigger level voltage.
            The trigger level is -4.5*DIV to 4.5*DIV.
            An out-of-range value will be adjusted to the closest legal value.
        """
        # TODO dynamic range
    )

    trigger_level2 = Instrument.control(
        "TRLV2?", "TRLV2 %eV",
        """ A float parameter that sets the lower trigger level voltage for the specified source.
        Higher and lower trigger levels are used with runt/slope triggers.
        The trigger level is -4.5*DIV to 4.5*DIV.
        An out-of-range value will be adjusted to the closest legal value.
        """
        # TODO dynamic range
    )

    trigger_slope = Instrument.control(
        "TRSL?", "TRSL %s",
        """ A string parameter that sets the trigger slope of the specified trigger source.
        <trig_slope>:={NEG,POS,WINDOW} for edge trigger.
        <trig_slope>:={NEG,POS} for other trigger
        """,
        validator=strict_discrete_set,
        values={"negative": "NEG", "positive": "POS", "window": "WINDOW"},
        map_values=True
    )

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number

    def values(self, command, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values("C%d:%s" % (self.number, command), **kwargs)

    def ask(self, command):
        return self.instrument.ask("C%d:%s" % (self.number, command))

    def write(self, command):
        # only in case of the BWL command the syntax is different. Why? SIGLENT Why?
        if command == "BWL OFF":
            self.instrument.write("BWL C%d,OFF" % self.number)
        elif command == "BWL ON":
            self.instrument.write("BWL C%d,ON" % self.number)
        self.instrument.write("C%d:%s" % (self.number, command))

    def setup(self, bwlimit=None, coupling=None, display=None, invert=None, offset=None, skew_factor=None,
              probe_attenuation=None, scale=None, unit=None, trigger_coupling=None, trigger_level=None,
              trigger_level2=None, trigger_slope=None):
        """ Setup channel. Unspecified settings are not modified. Modifying values such as
        probe attenuation will modify offset, range, etc. Refer to oscilloscope documentation and
        make multiple consecutive calls to setup() if needed.

        :param bwlimit: A boolean, which enables 20 MHz internal low-pass filter.
        :param coupling: "AC 1M", "DC 1M", "GND".
        :param display: A boolean, which enables channel display.
        :param invert: A boolean, which enables input signal inversion.
        :param offset: Numerical value represented at center of screen, must be inside
            the legal range.
        :param skew_factor: Channel-tochannel skew factor from -100ns to 100ns.
        :param probe_attenuation: Probe attenuation values from 0.1 to 1000.
        :param scale: Units per division.
        :param unit: Unit of the specified trace: "A" for Amperes, "V" for Volts
        :param trigger_coupling: input coupling for the selected trigger sources
        :param trigger_level: trigger level voltage for the active trigger source
        :param trigger_level2: trigger lower level voltage for the active trigger source (only SLEW/RUNT trigger)
        :param trigger_slope: trigger slope of the specified trigger source
        """

        if bwlimit is not None:
            self.bwlimit = bwlimit
        if coupling is not None:
            self.coupling = coupling
        if display is not None:
            self.display = display
        if invert is not None:
            self.invert = invert
        if offset is not None:
            self.offset = offset
        if skew_factor is not None:
            self.skew_factor = skew_factor
        if probe_attenuation is not None:
            self.probe_attenuation = probe_attenuation
        if scale is not None:
            self.scale = scale
        if unit is not None:
            self.unit = unit
        if trigger_coupling is not None:
            self.trigger_coupling = trigger_coupling
        if trigger_level is not None:
            self.trigger_level = trigger_level
        if trigger_level2 is not None:
            self.trigger_level2 = trigger_level2
        if trigger_slope is not None:
            self.trigger_slope = trigger_slope

    @property
    def current_configuration(self):
        """ Read channel configuration as a dict containing the following keys:
            - "channel": channel number (int)
            - "attenuation": probe attenuation (float)
            - "bandwidth_limit": bandwidth limiting enabled (bool)
            - "coupling": "AC 1M", "DC 1M", "GND" coupling (str)
            - "offset": vertical offset (float)
            - "skew_factor": channel-tochannel skew factor (float)
            - "display": currently displayed (bool)
            - "unit": "A" or "V" units (str)
            - "volts_div": vertical divisions (float)
            - "inverted": inverted (bool)
            - "trigger_coupling": trigger coupling can be "dc" "ac" "highpass" "lowpass" (str)
            - "trigger_level": trigger level (float)
            - "trigger_level2": trigger lower level for SLEW or RUNT trigger (float)
            - "trigger_slope": trigger slope can be "negative" "positive" "window" (str)
        """

        ch_setup_raw = {
            "channel": self.number,
            "attenuation": self.probe_attenuation,
            "bandwidth_limit": self.bwlimit,
            "coupling": self.coupling,
            "offset": self.offset,
            "skew_factor": self.skew_factor,
            "display": self.display,
            "unit": self.unit,
            "volts_div": self.scale,
            "inverted": self.invert,
            "trigger_coupling": self.trigger_coupling,
            "trigger_level": self.trigger_level,
            "trigger_level2": self.trigger_level2,
            "trigger_slope": self.trigger_slope
        }

        # Convert values to specific type
        to_str = ["coupling", "unit", "trigger_coupling", "trigger_slope"]
        to_bool = ["bandwidth_limit", "display", "inverted"]
        to_float = ["attenuation", "offset", "skew_factor", "volts_div", "trigger_level", "trigger_level2"]
        to_int = ["channel"]
        ch_setup = self.instrument.sanitize_dictionary(ch_setup_raw, to_bool=to_bool, to_float=to_float,
                                                       to_int=to_int, to_str=to_str)
        return ch_setup


class LeCroyT3DSO1204(Instrument):
    """ Represents the LeCroy T3DSO1204 Oscilloscope interface for interacting with the instrument.

    Refer to the LeCroy T3DSO1204 Oscilloscope Programmer's Guide for further details about
    using the lower-level methods to interact directly with the scope.

    .. code-block:: python

        scope = LeCroyT3DSO1204(resource)
        scope.autoscale()
        ch1_data_array, ch1_preamble = scope.download_data(source="C1", points=2000)
        # ...
        scope.shutdown()
    """

    BOOLS = {True: "ON", False: "OFF"}

    def __init__(self, adapter, **kwargs):
        super().__init__(adapter, "LeCroy T3DSO1204 Oscilloscope", **kwargs)
        self.adapter.connection.timeout = 7000
        self.ch1 = Channel(self, 1)
        self.ch2 = Channel(self, 2)
        self.ch3 = Channel(self, 3)
        self.ch4 = Channel(self, 4)
        self.waveform_source = "C1"
        self.default_setup()

    _match_float = re.compile(r'-? *[0-9]+\.?[0-9]*(?:[Ee] *-? *[0-9]+)?')
    _match_int = re.compile(r'^[-+]?[0-9]+')

    def sanitize_dictionary(self, raw_dictionary, to_bool=None, to_float=None, to_int=None, to_str=None):
        sane_dictionary = {}
        for key, val in raw_dictionary.items():
            if val is None:
                sane_dictionary[key] = val
            elif to_str is not None and key in to_str:
                sane_dictionary[key] = str(val)
            elif to_bool is not None and key in to_bool:
                sane_dictionary[key] = (val in [True, "ON"])
            elif to_float is not None and key in to_float:
                x = val if isinstance(val, (float, int)) else re.findall(self._match_float, str(val))[0]
                sane_dictionary[key] = float(x)
            elif to_int is not None and key in to_int:
                x = val if isinstance(val, (float, int)) else re.findall(self._match_int, str(val))[0]
                sane_dictionary[key] = int(x)
            else:
                sane_dictionary[key] = val
        return sane_dictionary

    ################
    # System Setup #
    ################

    def default_setup(self):
        """ Setup the oscilloscope for remote operation. """
        self.write("CHDR OFF")

    def ch(self, channel_number):
        if channel_number == 1 or channel_number == "C1":
            return self.ch1
        elif channel_number == 2 or channel_number == "C2":
            return self.ch2
        elif channel_number == 3 or channel_number == "C3":
            return self.ch3
        elif channel_number == 4 or channel_number == "C4":
            return self.ch4
        else:
            raise ValueError("Invalid channel number. Must be 1, 2, 3, 4.")

    def autoscale(self):
        """ Autoscale displayed channels. """
        self.write("ASET")

    ##################
    # Timebase Setup #
    ##################

    timebase_offset = Instrument.control(
        "TRIG_DELAY?", "TRDL %eS",
        """ A float parameter that sets the time interval in seconds between the trigger
        event and the reference position (at center of screen by default)."""
    )

    timebase_scale = Instrument.control(
        "TDIV?", "TDIV %eS",
        """ A float parameter that sets the horizontal scale (units per division) in seconds (S), milliseconds (MS), 
        microseconds (US) or nanoseconds (NS) for the main window.""",
        validator=strict_range,
        values=[1e-9, 100]
    )

    timebase_hor_magnify = Instrument.control(
        "HMAG?", "HMAG %eS",
        """ A string parameter that sets the zoomed (delayed) window horizontal scale (seconds/div). The main sweep 
        scale determines the range for this command. """,
        validator=strict_range,
        values=[1e-9, 20e-3]
    )

    timebase_hor_position = Instrument.control(
        "HPOS?", "HPOS %eS",
        """ A string parameter that sets the horizontal position in the zoomed (delayed) view of the main sweep. The 
        main sweep range and the main sweep horizontal position determine the range for this command. The value for 
        this command must keep the zoomed view window within the main sweep range.""",
    )

    @property
    def timebase(self):
        """ Read timebase setup as a dict containing the following keys:
            - "seconds_div": horizontal scale in seconds/div (float)
            - "delay": interval in seconds between the trigger event and the reference position (float)
            - "hor_magnify": horizontal scale in the zoomed window in seconds/div (float)
            - "hor_position": horizontal position in the zoomed window in seconds (float)"""
        tb_setup = {
            "seconds_div": self.timebase_scale,
            "delay": self.timebase_offset,
            "hor_magnify": self.timebase_hor_magnify,
            "hor_position": self.timebase_hor_position
        }
        return {k: float(v) for k, v in tb_setup.items()}

    def timebase_setup(self, offset=None, scale=None, hor_magnify=None, hor_position=None):
        """ Set up timebase. Unspecified parameters are not modified. Modifying a single parameter
        might impact other parameters. Refer to oscilloscope documentation and make multiple
        consecutive calls to timebase_setup if needed.

        :param offset: horizontal scale per division in seconds/div.
        :param scale: interval in seconds between the trigger event and the reference position.
        :param hor_magnify: horizontal scale in the zoomed window in seconds/div.
        :param hor_position: horizontal position in the zoomed window in seconds."""

        if offset is not None:
            self.timebase_offset = offset
        if scale is not None:
            self.timebase_scale = scale
        if hor_magnify is not None:
            self.timebase_hor_magnify = hor_magnify
        if hor_position is not None:
            self.timebase_hor_position = hor_position

    ###############
    # Acquisition #
    ###############

    acquisition_type = Instrument.control(
        "ACQW?", "ACQW %s",
        """ A string parameter that sets the type of data acquisition. Can be "normal", "peak",
         "average", "highres".""",
        validator=strict_discrete_set,
        values={"normal": "SAMPLING", "peak": "PEAK_DETECT", "average": "AVERAGE", "highres": "HIGH_RES"},
        map_values=True
    )

    acquisition_average = Instrument.control(
        "AVGA?", "AVGA %d",
        """ A integer parameter that selects the average times of average acquisition.""",
        validator=strict_discrete_set,
        values=[4, 16, 32, 64, 128, 256]
    )

    acquisition_status = Instrument.measurement(
        "SAST?", """A string parameter that defines the acquisition status of the scope.""",
        validator=strict_discrete_set,
        values={"stopped": "Stop", "triggered": "Trig'd", "ready": "Ready", "auto": "Auto", "armed": "Arm"},
        map_values=True
    )

    acquisition_sampling_rate = Instrument.measurement(
        "SARA?", """A The SAST? sample rate of the scope."""
    )

    def run(self):
        """ Starts repetitive acquisitions.

        This is the same as pressing the Run key on the front panel.
        """
        self.trigger_mode = "normal"
        self.write("ARM")

    def stop(self):
        """  Stops the acquisition. This is the same as pressing the Stop key on the front panel."""
        self.write("STOP")

    def single(self):
        """ Causes the instrument to acquire a single trigger of data.
        This is the same as pressing the Single key on the front panel. """
        self.trigger_mode = "single"
        self.write("ARM")

    ##################
    #    Waveform    #
    ##################

    waveform_points = Instrument.control(
        "WFSU?", "WFSU NP,%d",
        """ An integer parameter that sets the number of waveform points to be transferred with
        the digitize method. NP = 0 sends all data points.

        Note that the oscilloscope may provide less than the specified nb of points. """,
        validator=strict_range,
        values=[0, sys.maxsize]
    )

    waveform_sparsing = Instrument.control(
        "WFSU?", "WFSU SP,%d",
        """ An integer parameter that defines the interval between data points. For example:
            SP = 0 sends all data points.
            SP = 4 sends every 4 data points.""",
        validator=strict_range,
        values=[0, sys.maxsize]
    )

    waveform_first_point = Instrument.control(
        "WFSU?", "WFSU FP,%d",
        """ An integer parameter that specifies the address of the first data point to be sent. For waveforms 
        acquired in sequence mode, this refers to the relative address in the given segment.
        For example:
        FP = 0 corresponds to the first data point.
        FP = 1 corresponds to the second data point.""",
        validator=strict_range,
        values=[0, sys.maxsize]
    )

    @property
    def waveform_preamble(self):
        """ Get preamble information for the selected waveform source as a dict with the following keys:
            - "type": normal, peak detect, average, high resolution (str)
            - "points": nb of data points transferred (int)
            - "sparsing": Sparse point. It defines the interval between data points. (int)
            - "first_point"  address of the first data point to be sent (int)
            """
        vals = self.values("WFSU?")
        vals_dict = {
            "sparsing": vals[vals.index("SP") + 1],
            "points": vals[vals.index("NP") + 1],
            "first_point": vals[vals.index("FP") + 1],
            "source": self.waveform_source,
            "type": self.acquisition_type,
            "average": self.acquisition_average,
            "sampling_rate": self.acquisition_sampling_rate,
            "status": self.acquisition_status,
            "xdiv": self.timebase_scale,
            "xoffset": self.timebase_offset,
        }
        if self.waveform_source in ["C1", "C2", "C3", "C4"]:
            vals_dict["ydiv"] = self.ch(self.waveform_source).scale
            vals_dict["yoffset"] = self.ch(self.waveform_source).offset
        else:
            raise NotImplementedError(f"Acquiring from source {self.waveform_source} is not implemented")
        # Correct types
        to_int = ["points", "sparsing", "first_point", "average"]
        to_float = ["xdiv", "xoffset", "ydiv", "yoffset", "sampling_rate"]
        to_str = ["type", "status", "source"]
        return self.sanitize_dictionary(vals_dict, to_float=to_float, to_int=to_int, to_str=to_str)

    def digitize(self, source: str):
        """ Acquire waveforms according to the settings of the acquire commands
        :param source: a string parameter that can take the following values: "C1", "C2", "C3", "C4".
        :return: bytearray with raw data
        """
        strict_discrete_set(source, ["C1", "C2", "C3", "C4"])
        values = self.binary_values(f"{source}:WF? DAT2", dtype=np.uint8)
        if len(values) < 18:
            raise ValueError(f"Waveform data is too short: len({len(values)}) < header(16) + footer(2)")
        header = bytes(values[0:16]).decode("ascii")
        footer = bytes(values[-2:]).decode("ascii")
        values = values[16:-2]
        if header[0:7] != "DAT2,#9":
            raise ValueError(f"Waveform data in invalid : header is {header}")
        if footer != "\n\n":
            raise ValueError(f"Waveform data in invalid : footer is {footer}")
        npoints = int(header[-9:])
        if len(values) != npoints:
            raise ValueError(f"Waveform data in invalid : received {len(values)} points instead of {npoints}")
        return values

    #################
    # Download data #
    #################

    def download_image(self):
        """ Get a BMP image of oscilloscope screen in bytearray of specified file format.
        """
        # Using binary_values query because default interface does not support binary transfer
        chunk_size = self.adapter.connection.chunk_size
        self.adapter.connection.chunk_size = 20 * 1024 * 1024
        img = self.binary_values("SCDP", dtype=np.uint8)
        self.adapter.connection.chunk_size = chunk_size
        return bytearray(img)

    def download_data(self, source, points=None, sparsing=None, first_point=None):
        """ Get data from specified source of oscilloscope. Returned objects are a np.ndarray of
        data values (no temporal axis) and a dict of the waveform preamble, which can be used to
        build the corresponding time values for all data points.

        :param source: measurement source, can be "C1", "C2", "C3", "C4".
        :param points: integer number of points to acquire. Note that oscilloscope may return fewer
            points than specified, this is not an issue of this library. If 0 all available points
            will be returned
        :param sparsing: it defines the interval between data points.
        :param first_point: it specifies the address of the first data point to be sent.

        :return data_ndarray, waveform_preamble_dict: see waveform_preamble property for dict format.
        """
        self.waveform_source = source
        if points is not None:
            self.waveform_points = points
        if sparsing is not None:
            self.waveform_sparsing = sparsing
        if first_point is not None:
            self.waveform_first_point = first_point

        preamble = self.waveform_preamble
        data_bytes = self.digitize(source)
        return np.array(data_bytes), preamble

    ###############
    #   Trigger   #
    ###############

    trigger_50 = Instrument.setting(
        "SET50",
        """ The SET50 command automatically sets the trigger levels to center of the trigger source waveform. """
    )

    trigger_mode = Instrument.control(
        "TRMD?", "TRMD %s",
        """ A string parameter that selects the trigger sweep mode.
        <mode>:= {AUTO,NORM,SINGLE,STOP}
        • AUTO — When AUTO sweep mode is selected, the oscilloscope begins to search for the trigger signal that 
        meets the conditions.
        If the trigger signal is satisfied, the running state on the top left corner of the user interface shows 
        Trig'd, and the interface shows stable waveform.
        Otherwise, the running state always shows Auto, and the interface shows unstable waveform.
        • NORM — When NORMAL sweep mode is selected, the oscilloscope enters the wait trigger state and begins to 
        search for trigger signals that meet the conditions.
        If the trigger signal is satisfied, the running state shows Trig'd, and the interface shows stable waveform.
        Otherwise, the running state shows Ready, and the interface displays the last triggered waveform (previous 
        trigger) or does not display the waveform (no previous trigger).
        • SINGLE — When SINGLE sweep mode is selected, the backlight of SINGLE key lights up, the oscilloscope enters
        the waiting trigger state and begins to search for the trigger signal that meets the conditions.
        If the trigger signal is satisfied, the running state shows Trig'd, and the interface shows stable waveform. 
        Then, the oscilloscope stops scanning, the RUN/STOP key is red light, and the running status shows Stop.
        Otherwise, the running state shows Ready, and the interface does not display the waveform.
        • STOP — STOP is a part of the option of this command, but not a trigger mode of the oscilloscope.
        """,
        validator=strict_discrete_set,
        values={"stopped": "STOP", "normal": "NORM", "single": "SINGLE", "auto": "AUTO"},
        map_values=True
    )

    @staticmethod
    def _trigger_select_num_pars(value):
        """
        find the expected number of parameter for the trigger_select property
        :param value: input parameters as a tuple
        """
        num_expected_pars = 0
        if 3 <= len(value) <= 5:
            if value[0] == "EDGE":
                num_expected_pars = 3 if value[2] == "OFF" else 4
            elif value[0] in ["SLEW", "INTV"]:
                num_expected_pars = 4 if value[2] in ["IS", "IL"] else 5
            elif value[0] in ["GLIT", "RUNT"]:
                num_expected_pars = 4 if value[2] in ["PS", "PL"] else 5
            elif value[0] == "DROP":
                num_expected_pars = 4
        else:
            raise ValueError('Number of parameters {} can only be 3, 4, 5'.format(len(value)))
        return num_expected_pars

    @staticmethod
    def _trigger_select_validator(value, values, num_pars_finder=_trigger_select_num_pars):
        """
        Validate the input of the trigger_select property
        :param value: input parameters as a tuple
        :param values: allowed space for each parameter
        :param num_pars_finder: function to find the number of expected parameters
        """
        if len(value) < 3 or len(value) > 5:
            raise ValueError('Number of parameters {} can only be 3, 4, 5'.format(len(value)))
        if value[0] not in values.keys():
            raise ValueError('Value of {} is not in the discrete set {}'.format(value[0], values.keys()))
        num_expected_pars = num_pars_finder(value)
        if len(value) != num_expected_pars:
            raise ValueError('Number of parameters {} is not the expected {}'.format(len(value), num_expected_pars))
        for i, element in enumerate(value[1:], start=1):
            if i < 3:
                strict_discrete_set(element, values=values[value[0]][i - 1])
            else:
                strict_range(element, values=values[value[0]][i - 1])
        return value

    @staticmethod
    def _trigger_select_get_process(value):
        """
        Process the output of the trigger_select property.
        The format of the input list is
            <trig_type>, SR, <source>, HT, <hold_type>[, HV, <hold_value1>S][, HV2, <hold_value2>S]
        The format of the output list is
            <trig_type>, <source>, <hold_type>[, <hold_value1>][, <hold_value2>]
        :param value: output parameters as a list
        """
        output = []
        if len(value) > 0:
            output.append(value[0])
        if "SR" in value:
            output.append(value[value.index("SR") + 1])
        if "HT" in value:
            output.append(value[value.index("HT") + 1])
        if "HV" in value:
            output.append(float(value[value.index("HV") + 1][:-1]))
        if "HV2" in value:
            output.append(float(value[value.index("HV2") + 1][:-1]))
        return output

    _trigger_select_values = {
        "EDGE": [["C1", "C2", "C3", "C4", "LINE"], ["TI", "OFF"], [80e-9, 1.5]],
        "DROP": [["C1", "C2", "C3", "C4"], ["TI"], [2e-9, 4.2]],
        "GLIT": [["C1", "C2", "C3", "C4"], ["PS", "PL", "P2", "P1"], [2e-9, 4.2], [2e-9, 4.2]],
        "RUNT": [["C1", "C2", "C3", "C4"], ["PS", "PL", "P2", "P1"], [2e-9, 4.2]],
        "SLEW": [["C1", "C2", "C3", "C4"], ["IS", "IL", "I2", "I1"], [2e-9, 4.2]],
        "INTV": [["C1", "C2", "C3", "C4"], ["IS", "IL", "I2", "I1"], [2e-9, 4.2]]
    }

    _trigger_select_short_command = "TRSE %s,SR,%s,HT,%s"
    _trigger_select_normal_command = "TRSE %s,SR,%s,HT,%s,HV,%e"
    _trigger_select_extended_command = "TRSE %s,SR,%s,HT,%s,HV,%e,HV2,%e"

    _trigger_select = Instrument.control(
        "TRSE?", _trigger_select_normal_command,
        """ A string parameter that selects the condition that will trigger the acquisition of waveforms.
        Depending on the trigger type, additional parameters must be specified. These additional parameters are 
        grouped in pairs. The first in the pair names the variable to be modified, while the second gives the new 
        value to be assigned. Pairs may be given in any order and restricted to those variables to be changed.
        <trig_type>:={EDGE,SLEW,GLIT,INTV,RUNT,DROP}
        <source>:={C1,C2,C3,C4,LINE}
        <hold_type>:={TI,OFF} for EDGE trigger.
        <hold_type>:={TI} for DROP trigger.
        <hold_type>:={PS,PL,P2,P1}for GLIT/RUNT trigger.
        <hold_type>:={IS,IL,I2,I1} for SLEW/INTV trigger.
        <hold_value1>:= a time value with unit.
        <hold_value2>:= a time value with unit.
        
        Note:
        • LINE can only be selected when the trigger type is Edge.
        • If there is no unit(S/mS/uS/nS) added, it defaults to be S.
        • The range of hold_values varies from trigger types. [80nS, 1.5S] for Edge trigger, and [2nS, 4.2S] for others.
        """,
        get_process=_trigger_select_get_process,
        validator=_trigger_select_validator,
        values=_trigger_select_values,
        dynamic=True
    )

    @property
    def trigger_select(self):
        """ Refer to the self._trigger_select documentation. """
        return self._trigger_select

    # noinspection PyAttributeOutsideInit
    @trigger_select.setter
    def trigger_select(self, value):
        """ Refer to the self._trigger_select documentation.
            The trigger_select command is switched automatically between the short, normal and extended version
            depending on the number of expected parameters.
        """
        num_expected_pars = self._trigger_select_num_pars(value)
        if num_expected_pars == 3:
            self._trigger_select_set_command = self._trigger_select_short_command
        elif num_expected_pars == 4:
            self._trigger_select_set_command = self._trigger_select_normal_command
        elif num_expected_pars == 5:
            self._trigger_select_set_command = self._trigger_select_extended_command
        self._trigger_select = value

    def trigger_setup(self, mode=None, source=None, trigger_type=None, hold_type=None, hold_value1=None,
                      hold_value2=None, coupling=None, level=None, level2=None, slope=None):
        """
        Set up trigger. Unspecified parameters are not modified. Modifying a single parameter
        might impact other parameters. Refer to oscilloscope documentation and make multiple
        consecutive calls to trigger_setup and channel_setup if needed.

        :param mode: trigger sweep mode [auto, normal, single, stop]
        :param source: trigger source [C1,C2,C3,C4]
        :param trigger_type: condition that will trigger the acquisition of waveforms [EDGE,SLEW,GLIT,INTV,RUNT,DROP]
        :param hold_type: hold type (refer to page 172 of programing guide)
        :param hold_value1: hold value1 (refer to page 172 of programing guide)
        :param hold_value2: hold value2 (refer to page 172 of programing guide)
        :param coupling: input coupling for the selected trigger sources
        :param level: trigger level voltage for the active trigger source
        :param level2: trigger lower level voltage for the active trigger source (only SLEW/RUNT trigger)
        :param slope: trigger slope of the specified trigger source
        """
        if mode is not None:
            self.trigger_mode = mode
        if all(i is not None for i in [source, trigger_type, hold_type]):
            args = [trigger_type, source, hold_type]
            if hold_value1 is not None:
                args.append(hold_value1)
            if hold_value2 is not None:
                args.append(hold_value2)
            self.trigger_select = tuple(args)
        elif any(i is not None for i in [source, trigger_type, hold_type]):
            raise ValueError("Need to specify all of source, trigger_type and hold_type arguments")
        if source is not None:
            if source not in ["C1", "C2", "C3", "C4"]:
                raise ValueError(f"Trigger source {source} not recognized")
            ch = self.ch(source)
            if coupling is not None:
                ch.trigger_coupling = coupling
            if level is not None:
                ch.trigger_level = level
            if level2 is not None:
                ch.trigger_level2 = level2
            if slope is not None:
                ch.trigger_slope = slope

    @property
    def trigger(self):
        """ Read trigger setup as a dict containing the following keys:
            - "mode": trigger sweep mode [auto, normal, single, stop]
            - "trigger_type": condition that will trigger the acquisition of waveforms [EDGE,SLEW,GLIT,INTV,RUNT,DROP]
            - "source": trigger source [C1,C2,C3,C4]
            - "hold_type": hold type (refer to page 172 of programing guide)
            - "hold_value1": hold value1 (refer to page 172 of programing guide)
            - "hold_value2": hold value2 (refer to page 172 of programing guide)
            - "coupling": input coupling for the selected trigger sources
            - "level": trigger level voltage for the active trigger source
            - "level2": trigger lower level voltage for the active trigger source (only SLEW/RUNT trigger)
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
            "level2": ch.trigger_level2,
            "slope": ch.trigger_slope
        }
        to_str = ["mode", "trigger_type", "source", "hold_type", "coupling", "slope"]
        to_float = ["hold_value1", "hold_value2", "level", "level2"]
        return self.sanitize_dictionary(tb_setup, to_str=to_str, to_float=to_float)
