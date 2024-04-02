#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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

import re
import time

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_discrete_set, strict_range, \
    truncated_range, strict_discrete_range


def sanitize_source(source):
    """Parse source string.

    :param source: can be "cX", "ch X", "chan X", "channel X", "math" or "line", where X is
    a single digit integer. The parser is case and white space insensitive.
    :return: can be "C1", "C2", "C3", "C4", "MATH" or "LINE".
    """

    match = re.match(r"^\s*(C|CH|CHAN|CHANNEL)\s*(?P<number>\d)\s*$|"
                     r"^\s*(?P<name_only>LINE|AUX)\s*$", source, re.IGNORECASE)
    if match:
        if match.group("number") is not None:
            source = match.group("number")
            # source = "C" + match.group("number")
        else:
            source = match.group("name_only")
        source = source.upper()
    else:
        raise ValueError(f"source {source} not recognized")
    return source


def _math_define_validator(value, values):
    """
    Validate the input of the math_define property
    :param value: input parameters as a 3-element tuple
    :param values: allowed space for each parameter
    """
    if not isinstance(value, tuple):
        raise ValueError('Input value {} of trigger_select should be a tuple'.format(value))
    if len(value) != 3:
        raise ValueError('Number of parameters {} different from 3'.format(len(value)))
    output = (value[0], value[1], value[2])
    for i in range(3):
        strict_discrete_set(output[i], values=values[i])
    return output


class TektronixMsoScopeChannel(Channel):
    """Implementation of a scope base class channel."""

    unit = Instrument.control(
        "CH{ch}:PRObe:UNIts?",
        "CH{ch}:PRObe:UNIts %s",
        """Control a string describing the units of measure for the
        probe attached to the specified channel. ("A" for Amperes, "V" for
        Volts).
        """,
        validator=strict_discrete_set,
        values=["A", "V"],
        get_process=lambda v: v[1:-1],
    )

    scale = Instrument.control(
        "CH{ch}:SCAle?",
        "CH{ch}:SCAle %G",
        """Control the vertical scale (units per division) in Volts.""",
    )

    label = Instrument.control(
        "CH{ch}:LABel:NAMe?",
        "CH{ch}:LABel:NAMe \"%s\"",
        """Control the label attached to the displayed waveform for
           the specified channel.
        """,
    )

    bwlimit = Instrument.control(
        "CH{ch}:BANdwidth?",
        "CH{ch}:BANdwidth %G",
        """Control the low-pass bandwidth limit filter.

        Available arguments depend upon the instrument and the attached accessories.
        """,
        validator=strict_range,
        values=[20.0000E+6, 250.0000E+6, 500.0000E+6, 1.0000E+9],
        dynamic=True,
    )

    coupling = Instrument.control(
        "CH{ch}:COUPling?",
        "CH{ch}:COUPling %s",
        """Control the input coupling setting""",
        validator=strict_discrete_set,
        values={"ac": "AC", "dc": "DC", "dcrej": "DCREJ"},
        map_values=True,
        dynamic=True,
    )

    offset = Instrument.control(
        "CH{ch}:OFFSet?",
        "CH{ch}:OFFSet %G",
        """Control the center of the screen in Volts by a a float parameter.
        The range of legal values varies depending on range and scale. If the specified
        value is outside of the legal range, the offset value is automatically set to the nearest
        legal value.
        """,
    )

    position = Instrument.control(
        "CH{ch}:POSition?",
        "CH{ch}:POSition %d",
        """Control the vertical position.""",
    )

    display = Instrument.control(
        "DISplay:GLObal:CH{ch}:STATE?",
        "DISplay:GLObal:CH{ch}:STATE %d",
        """Control the global state (display mode On or Off)""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    probe_ext_attenuation = Instrument.control(
        "CH{ch}:PROBEFunc:EXTAtten?",
        "CH{ch}:PROBEFunc:EXTAtten %s",
        """Control the attenuation value as a multiplier to the given scale factor.
        """,
        validator=strict_discrete_set,
        values={1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
    )

    trigger_level = Instrument.control(
        "TRIGger:A:LEVel:CH{ch}?",
        "TRIGger:A:LEVel:CH{ch} %g",
        """Control the trigger level for an Edge, Pulse Width,
        Runt or Rise/Fall (Transition and Slew Rate) trigger
        when triggering on an analog channel waveform.
        """,
    )

    trigger_lower_threshold = Instrument.control(
        "TRIGger:A:LOWerthreshold:CH{ch}?",
        "TRIGger:A:LOWerthreshold:CH{ch} %f",
        """Control the A lower trigger level threshold.
        """,
    )

    trigger_upper_threshold = Instrument.control(
        "TRIGger:A:UPPerthreshold:CH{ch}?",
        "TRIGger:A:UPPerthreshold:CH{ch} %f",
        """Control the A upper trigger level threshold.
        """,
    )

    @property
    def current_configuration(self):
        """Get channel configuration as a dict containing the following keys:

        - "channel": channel number (int)
        - "bandwidth_limit": bandwidth limiting enabled (bool)
        - "coupling": "ac 1M", "dc 1M", "ground" coupling (str)
        - "offset": vertical offset (float)
        - "display": currently displayed (bool)
        - "unit": "A" or "V" units (str)
        - "label": "" (str)
        - "volts_div": vertical divisions (float)
        - "trigger_level": trigger level (float)
        """

        ch_setup = {
            "channel": self.id,
            "bandwidth_limit": self.bwlimit,
            "coupling": self.coupling,
            "offset": self.offset,
            "display": self.display,
            "unit": self.unit,
            "label": self.label,
            "volts_div": self.scale,
            "trigger_level": self.trigger_level,
        }
        return ch_setup


class TektronixMsoScopeMathChannel(Channel):
    """Implementation of a math base class channel"""

    def math_add_new(self, slot: int):
        """Add a new math channel."""
        self.write(f'MATH:ADDNEW \"MATH{slot}\"')

    math_define = Instrument.control(
        "MATH:MATH{ch}:DEFine?", "MATH:MATH{ch}:DEFine \"%s%s%s\"",
        """Control the desired waveform math operation between two channels.

        Three parameters must be passed as a tuple:

        #. source1 : source channel on the left
        #. operation : operator must be "*", "/", "+", "-"
        #. source2 : source channel on the right

        """,
        validator=_math_define_validator,
        values=[["CH1", "CH2", "CH3", "CH4"], ["*", "/", "+", "-"], ["CH1", "CH2", "CH3", "CH4"]],
    )

    math_type = Instrument.control(
        "MATH:MATH{ch}:TYPe?",
        "MATH:MATH{ch}:TYPe %s",
        """Control the math type.""",
        validator=strict_discrete_set,
        values=["BASIC", "FFT", "ADVANCED"],
    )

    math_basic_function = Instrument.control(
        "MATH:MATH{ch}:FUNCtion?",
        "MATH:MATH{ch}:FUNCtion %s",
        """Control the basic math arithmetic function.
        This command does not affect the same Math equation in Advanced math
        (also accessed via the property math_define.""",
        validator=strict_discrete_set,
        values=["ADD", "SUBTRACT", "MULTIPLY", "DIVIDE"],
    )

    math_source1 = Instrument.control(
        "MATH:MATH{ch}:SOUrce1?",
        "MATH:MATH{ch}:SOUrce1 %s",
        """Control the math source1.
        This command sets the Basic Math components in the user interface,
        with two sources and a function. You would also need to set the
        math type to Basic to see the change in the user interface but this will not effect
        the programmable interface.""",
        validator=strict_discrete_set,
        values=['CH1', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6', 'CH7', 'CH8'],
    )

    math_source2 = Instrument.control(
        "MATH:MATH{ch}:SOUrce2?",
        "MATH:MATH{ch}:SOUrce2 %s",
        """Control the math source2.""",
        validator=strict_discrete_set,
        values=['CH1', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6', 'CH7', 'CH8'],
    )

    math_average_mode = Instrument.control(
        "MATH:MATH{ch}:AVG:MODE?",
        "MATH:MATH{ch}:AVG:MODE %d",
        """Control the math average mode flag.""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
    )

    math_average_sweeps = Instrument.control(
        "MATH:MATH{ch}:AVG:WEIGht?",
        "MATH:MATH{ch}:AVG:WEIGht %d",
        """Control the number of acquisitions at which the averaging
        algorithm will begin exponential averaging.""",
        validator=strict_range,
        values=[1, 1000000],
    )

    math_FFT_output_type = Instrument.control(
        "MATH:MATH{ch}:SPECTral:TYPE?",
        "MATH:MATH{ch}:SPECTral:TYPE %s",
        """Control the FFT type selected for spectral analysis.""",
        validator=strict_discrete_set,
        values=["MAGNITUDE", "PHASE", "REAL", "IMAGINARY"],
    )

    math_FFT_window_type = Instrument.control(
        "MATH:MATH{ch}:SPECTral:WINdow?",
        "MATH:MATH{ch}:SPECTral:WINdow %s",
        """Control the type of window for the FFT.""",
        validator=strict_discrete_set,
        values=["RECTANGULAR", "HAMMING", "HANNING", "BLACKMANHARRIS",
                "KAISERBESSEL", "GAUSSIAN", "FLATTOP2", "TEKEXPONENTIAL"],
    )

    math_FFT_horizontal_unit = Instrument.control(
        "MATH:MATH{ch}:SPECTral:HORZ?",
        "MATH:MATH{ch}:SPECTral:HORZ %s",
        """Control the horizontal axis unit.""",
        validator=strict_discrete_set,
        values=["LOG", "LINEAR"],
    )

    math_FFT_vertical_unit = Instrument.control(
        "MATH:MATH{ch}:SPECTral:MAG?",
        "MATH:MATH{ch}:SPECTral:MAG %s",
        """Control the vertical axis unit.""",
        validator=strict_discrete_set,
        values=["LINEAR", "DBM"],
    )

    math_FFT_view_autoscale = Instrument.control(
        "DISplay:MATHFFTView{ch}:AUTOScale?",
        "DISplay:MATHFFTView{ch}:AUTOScale %d",
        """Control the enabled state of autoscale for Math/FFT waveforms.""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
    )

    math_FFT_view_zoom_xaxis_from = Instrument.control(
        "DISplay:MATHFFTView{ch}:ZOOM:XAXIS:FROM?",
        "DISplay:MATHFFTView{ch}:ZOOM:XAXIS:FROM %f",
        """Control the left edge of the zoom x-axis.""",
    )

    math_FFT_view_zoom_xaxis_to = Instrument.control(
        "DISplay:MATHFFTView{ch}:ZOOM:XAXIS:TO?",
        "DISplay:MATHFFTView{ch}:ZOOM:XAXIS:TO %f",
        """Control the right edge of the zoom x-axis.""",
    )

    math_FFT_view_zoom_yaxis_from = Instrument.control(
        "DISplay:MATHFFTView{ch}:ZOOM:YAXIS:FROM?",
        "DISplay:MATHFFTView{ch}:ZOOM:YAXIS:FROM %f",
        """Control the bottom value of the zoom y-axis.""",
    )

    math_FFT_view_zoom_yaxis_to = Instrument.control(
        "DISplay:MATHFFTView{ch}:ZOOM:YAXIS:TO?",
        "DISplay:MATHFFTView{ch}:ZOOM:YAXIS:TO %f",
        """Control the top value of the zoom y-axis.""",
    )


class TektronixMsoScope(Instrument):
    """A base abstract class for any Tektronix MSO oscilloscope family.

    This MSO Scope Family consists of:
    4 Series MSO (MSO44, MSO46),
    5 Series MSO (MSO54, MSO56, MSO58, MSO58LP),
    6 Series MSO (MSO64),
    6B Series MSO (MSO64B, MSO66B, MSO68B),
    and the 6 Series Low Profile Digitizer (LPD64) instruments.

    Attributes:
        WRITE_INTERVAL_S: minimum time between two commands. If a command is received less than
        WRITE_INTERVAL_S after the previous one, the code blocks until at least WRITE_INTERVAL_S
        seconds have passed.
        Because the oscilloscope takes a non neglibile time to perform some operations, it might
        be needed for the user to tweak the sleep time between commands.
        The WRITE_INTERVAL_S is set to 10ms as default however its optimal value heavily depends
        on the actual commands and on the connection type, so it is impossible to give a unique
        value to fit all cases. An interval between 10ms and 500ms second proved to be good,
        depending on the commands and connection latency.
    """

    _BOOLS = {True: "ON", False: "OFF"}
    _STATE = {"ON": 1, "OFF": 0}
    _TRIGGER_SLOPES = {"negative": "FALL", "positive": "RISE", "either": "EITHER"}
    TRIGGER_TYPES = {"edge": "EDGE", "pulse": "WIDTH", "timeout": "TIMEOUT", "runt": "RUNT",
                    "window": "WINDOW", "logic": "LOGIC", "sethold": "SETHOLD",
                    "transition": "TRANSITION", "bus": "BUS"}
    _TRIGGER_COUPLING = {"dc": "DC", "lowpass": "LFREJ", "highpass": "HFREJ", "noise": "NOISEREJ"}

    ANALOG_TRIGGER_SOURCE = ['CH1', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6', 'CH7', 'CH8']
    DIGITAL_TRIGGER_SOURCE = ['CH1_D0', 'CH1_D1', 'CH1_D2', 'CH1_D3',
                              'CH1_D4', 'CH1_D5', 'CH1_D6', 'CH1_D7',
                              'CH2_D0', 'CH2_D1', 'CH2_D2', 'CH2_D3',
                              'CH2_D4', 'CH2_D5', 'CH2_D6', 'CH2_D7',
                              'CH3_D0', 'CH3_D1', 'CH3_D2', 'CH3_D3',
                              'CH3_D4', 'CH3_D5', 'CH3_D6', 'CH3_D7',
                              'CH4_D0', 'CH4_D1', 'CH4_D2', 'CH4_D3',
                              'CH4_D4', 'CH4_D5', 'CH4_D6', 'CH4_D7',
                              'CH5_D0', 'CH5_D1', 'CH5_D2', 'CH5_D3',
                              'CH5_D4', 'CH5_D5', 'CH5_D6', 'CH5_D7',
                              'CH6_D0', 'CH6_D1', 'CH6_D2', 'CH6_D3',
                              'CH6_D4', 'CH6_D5', 'CH6_D6', 'CH6_D7',
                              'CH7_D0', 'CH7_D1', 'CH7_D2', 'CH7_D3',
                              'CH7_D4', 'CH7_D5', 'CH7_D6', 'CH7_D7',
                              'CH8_D0', 'CH8_D1', 'CH8_D2', 'CH8_D3',
                              'CH8_D4', 'CH8_D5', 'CH8_D6', 'CH8_D7']
    CHANNELS_MAX = 8
    BANDWIDTH_RANGE = [1E7, 7E10]
    WRITE_INTERVAL_S = 0.02  # seconds

    def __init__(self, adapter,
                 name="Tektronix Oscilloscope",
                 analog_channels=8,
                 **kwargs):
        super().__init__(adapter, name=name, includeSCPI=True, **kwargs)
        if self.adapter.connection is not None:
            self.adapter.connection.timeout = 3000
        self._seconds_since_last_write = 0  # Timestamp of the last command
        self.default_setup()

        number_of_channels = None if analog_channels == "auto" else analog_channels

        self.update_channels(number_of_channels=number_of_channels)

    def update_channels(self, number_of_channels=None, **kwargs):
        """Create or remove channels to be correct with the actual number of channels.

        :param int number_of_channels: optional, if given, defines the desired number of channels.
        """
        if number_of_channels is None:
            number_of_channels = self.number_of_channels

        # noinspection PyAttributeOutsideInit
        if not hasattr(self, "channels"):
            self.channels = {}

        if len(self.channels) == number_of_channels:
            return

        # Remove redundant channels
        while len(self.channels) > number_of_channels:
            self.remove_child(self.channels[len(self.channels)])

        # Create new channels
        while len(self.channels) < number_of_channels:
            self.add_child(TektronixMsoScopeChannel, len(self.channels) + 1,
                           **kwargs)

    ################
    # System Setup #
    ################

    def add_new_math(self, slot: int):
        """adds the specified math channel."""
        self.add_child(TektronixMsoScopeMathChannel, slot, collection="maths", prefix="math_")
        self.maths[slot].math_add_new(slot)

    def math_delete_all(self):
        """Delete all math channels"""
        for math_channel in self.ask("MATH:LIST?").strip('\n').split(","):
            self.write(f'MATH:DELETE "{math_channel}"')

    def default_setup(self):
        """ Set up the oscilloscope for remote operation.

        The COMM_HEADER property controls the way the oscilloscope formats response to queries.
        This command does not affect the interpretation of messages sent to the oscilloscope.
        Headers can be sent in their long or short form regardless of the HEADer setting.
        By setting the COMM_HEADER to OFF, the instrument is going to reply with minimal
        information, and this makes the response message much easier to parse.
        The user should not be fiddling with the COMM_HEADER during operation, because
        if the communication header is anything other than OFF, the whole driver breaks down.
        """
        self._comm_header = "OFF"
        self._verbose = "ON"

    def ch(self, source):
        """ Get channel object from its index or its name. Or if source is "math", just return the
        scope object.

        :param source: can be 1, 2, 3, 4, 5, 6, 7, 8
         or CH1, CH2, CH3, CH4, CH5, CH6, CH7, CH8, LINE
        :return: handle to the selected source.
        """
        if isinstance(source, str):
            source = sanitize_source(source)
        if source == "MATH":
            return self
        elif source == "LINE":
            raise ValueError("LINE is not a valid channel")
        else:
            return getattr(self, f"ch_{source if isinstance(source, int) else source[-1]}")

    def autoscale(self):
        """ sets the vertical, horizontal, and trigger controls
            of the instrument to automatically acquire and display
            the selected waveform."""
        self.write("AUTOSet EXECute;*WAI")

    def reset(self):
        """ Resets the instrument. """
        self.write("*RST;*WAI")

    def write(self, command, **kwargs):
        """Write the command to the instrument through the adapter.

        Note: if the last command was sent less than WRITE_INTERVAL_S before, this method blocks for
        the remaining time so that commands are never sent with rate more than 1/WRITE_INTERVAL_S
        Hz.

        :param command: command string to be sent to the instrument
        """
        seconds_since_last_write = time.monotonic() - self._seconds_since_last_write
        if seconds_since_last_write < self.WRITE_INTERVAL_S:
            time.sleep(self.WRITE_INTERVAL_S - seconds_since_last_write)
            self._seconds_since_last_write = seconds_since_last_write
        super().write(command, **kwargs)

    _comm_header = Instrument.control(
        "HEADer?", "HEADer %s",
        """Control the way the oscilloscope formats response to queries.
        The user should not be fiddling with the COMM_HEADER during operation, because
        if the communication header is anything other than OFF, the whole driver breaks down.
        • OFF — omit headers on query responses, so that only the argument is returned.
        • ON — include headers on applicable query responses.""",
        validator=strict_discrete_set,
        values=_STATE,
    )

    _verbose = Instrument.control(
        "VERBose?", "VERBose %s",
        """Control Verbose state that controls the length of
        keywords on query responses.
        Keywords can be both headers and arguments.""",
        validator=strict_discrete_set,
        values=_STATE,
    )

    # Timebase Setup
    horizontal_mode = Instrument.control(
        "HORizontal:MODE?", "HORizontal:MODE %s",
        """Control horizontal operating mode.
        """,
        validator=strict_discrete_set,
        values=["AUTO", "MANUAL"],
    )

    horizontal_manualmode_cfg = Instrument.control(
        "HORizontal:MODe:MANual:CONFIGure?",
        "HORizontal:MODe:MANual:CONFIGure %s",
        """Control which horizontal control (scale or record length)
        will primarily change when the sample rate is changed in Manual mode.
        If the selected control (scale or record length) reaches a limit then
        the unselected control (record length or scale) may also change.
        """,
        validator=strict_discrete_set,
        values=["HORIZONTALSCALE", "RECORDLENGTH"],
    )

    horizontal_record_length = Instrument.control(
        "HORizontal:RECOrdlength?", "HORizontal:RECOrdlength %f",
        """Control horizontal record length in kilo-points per seconds.
        To change the record length the Horizontal Mode must be set to Manual.
        """,
    )

    horizontal_sample_rate = Instrument.control(
        "HORizontal:MODE:SAMPLERate?", "HORizontal:MODE:SAMPLERate %f",
        """Control the sample rate in Mega-sample per seconds.""",
    )

    horizontal_delay_mode = Instrument.control(
        "HORizontal:DELay:MODe?", "HORizontal:DELay:MODe %s",
        """Control horizontal delay mode.
        OFF sets the Horizontal Delay Mode to off.
        This causes the HORizontal:POSition command to operate like
        the HORIZONTAL POSITION knob on the front panel.
        ON sets the Horizontal Delay Mode to on.
        This causes the HORizontal:DELay:TIMe command to operate like
        the HORIZONTAL POSITION knob on the front panel.""",
        validator=strict_discrete_set,
        values=_STATE,
    )

    horizontal_minsamplerate_override = Instrument.control(
        "HORizontal:SAMPLERate:ANALYZemode:MINimum:OVERRide?",
        "HORizontal:SAMPLERate:ANALYZemode:MINimum:OVERRide %s",
        """Control the flag which allows override of the horizontal
        analyze minimum sample rate.
        OFF does not allow override of the horizontal analyze minimum sample rate.
        ON allows override of the horizontal analyze minimum sample rate.
        """,
        validator=strict_discrete_set,
        values=_STATE,
    )

    horizontal_minsamplerate_value = Instrument.control(
        "HORizontal:SAMPLERate:ANALYZemode:MINimum:VALue?",
        "HORizontal:SAMPLERate:ANALYZemode:MINimum:VALue %s",
        """Control the minimum sample rate used by Analysis Automatic horizontal mode.
        Value is in sample per seconds.
        AUTOmatic allows the instrument to set the minimum value.
        """,
        validator=strict_discrete_set,
        values={"AUTOMATIC": "AUTOMATIC", "3.125GS": 3.125E+9, "1.5625GS": 1.5625E+9,
                "1.25GS": 1.25E+9, "625M": 6.25E+8, "312.5M": 3.125E+8, "250M": 250E+6,
                "125M": 1.25E+8, "62.5M": 6.25E+7, "31.25M": 3.125E+7, "25M": 25E+6,
                "12.5M": 12.5E+6, "6.25M": 6.25E+6, "5M": 5.E+6, "3.125M": 3.125E+6,
                "2.5M": 2.5E+6, "1.25M": 1.25E+6, "1M": 1.0E+6, "625k": 625E+3,
                "500k": 500E+3, "312.5k": 312.5E+3, "250k": 250E+3, "125k": 125E+3,
                "100k": 100E+3, "62.5k": 6.250E+4, "50k": 5.00E+4, "31.25k": 3.1250E+4,
                "25k": 2.50E+4, "12.5k": 1.250E+4, "10k": 1.00E+4, "6.25k": 6.250E+3,
                "5k": 5.00E+3, "3.125k": 3.1250E+3, "2.5k": 2.50E+3, "1.25k": 1.25e+3,
                "1k": 1000, "625": 625, "500": 500, "312.5": 312.5, "250": 250,
                "125": 125, "100": 100, "62.5": 62.5, "50": 50, "31.25": 31.25,
                "25": 25, "12.5": 12.5, "10": 10, "6.25": 6.25, "5": 5, "3.125": 3.125,
                "2.5": 2.5, "1.5625": 1.5625},
        map_values=True,
        dynamic=True,
    )

    horizontal_delay_time = Instrument.control(
        "HORizontal:DELay:TIMe?", "HORizontal:DELay:TIMe %G",
        """Control horizontal delay time that is used when delay mode is on.""",
    )

    timebase_offset = Instrument.control(
        "HORizontal:POSition?", "HORizontal:POSition %G",
        """Control horizontal position as a percent of screen width.
        When Horizontal Delay Mode is turned off, this command is equivalent
        to adjusting the HORIZONTAL POSITION knob on the front panel.
        When Horizontal Delay Mode is turned on, the horizontal position is forced to 50%.""",
        validator=strict_range,
        values=[0, 100],
    )

    timebase_scale = Instrument.control(
        "HORizontal:SCAle?", "HORizontal:SCAle %G",
        """Control the horizontal scale (seconds per division) in seconds for the main
        window (float).""",
        validator=strict_range,
        values=[200e-12, 1000],
    )

    @property
    def timebase(self):
        """Get timebase setup as a dict containing the following keys:

            - "timebase_scale": horizontal scale in seconds/div (float)
            - "timebase_offset": interval in seconds between the trigger and the reference
              position (float)
        """
        tb_setup = {
            "timebase_scale": self.timebase_scale,
            "timebase_offset": self.timebase_offset,
        }
        return tb_setup

    def timebase_setup(self, scale=None, offset=None):
        """Set up timebase. Unspecified parameters are not modified. Modifying a single parameter
        might impact other parameters. Refer to oscilloscope documentation and make multiple
        consecutive calls to timebase_setup if needed.

        :param scale: interval in seconds between the trigger event and the reference position.
        :param offset: horizontal scale per division in seconds/div.
        """

        if scale is not None:
            self.timebase_scale = scale
        if offset is not None:
            self.timebase_offset = offset

    # Acquisition
    acquisition_state = Instrument.control(
        "ACQuire:STATE?", "ACQuire:STATE %s",
        """Control starts or stops acquisitions.
        """,
        validator=strict_discrete_set,
        values={"STOP": 0, "RUN": 1},
        map_values=True,
    )

    acquisition_average = Instrument.control(
        "ACQuire:NUMAVg?", "ACQuire:NUMAVg %d",
        """Control number of waveform acquisitions
        that make up an averaged waveform.
        """,
        validator=strict_range,
        values=[2, 10240],
    )

    acquisition_mode = Instrument.control(
        "ACQUIRE:MODE?", "ACQUIRE:MODE %s",
        """Control acquisition mode of the instrument.
        """,
        validator=strict_discrete_set,
        values=["SAMPLE", "PEAKDETECT", "AVERAGE", "ENVELOPE"],
    )

    acquisition_condition = Instrument.control(
        "ACQuire:STOPAfter?", "ACQuire:STOPAfter %s",
        """Control whether the instrument continually acquires
            acquisitions or acquires a single sequence.
        """,
        validator=strict_discrete_set,
        values=["RUNSTOP", "SEQUENCE"],
    )

    acquisition_num_sequence = Instrument.control(
        "ACQuire:SEQ:NUMSEQ?", "ACQuire:SEQ:NUMSEQ %d",
        """Control the number of acquisitions or measurements
        that comprise the sequence, In single sequence acquisition mode.
        """,
    )

    def run(self):
        """Starts repetitive acquisitions.

        This is the same as pressing the Run key on the front panel.
        """
        self.acquisition_state = 'RUN'

    def stop(self):
        """ Stops the acquisition. This is the same as pressing the Stop key on the front panel."""
        self.acquisition_state = 'STOP'

    def single(self):
        """Causes the instrument to acquire a single trigger of data.

        This is the same as pressing the Single key on the front panel.
        """
        self.acquisition_condition = "SEQUENCE"
        self.acquisition_state = 'RUN'

    # General Trigger settings
    def center_trigger(self):
        """Set the trigger levels to center of the trigger source waveform."""
        self.write("TRIGger:A SETLEVEL")

    trigger_type = Instrument.control(
        "TRIGGER:A:TYPE?",
        "TRIGGER:A:TYPE %s",
        """Control the type of A trigger.

        Arguments
        EDGE is a normal trigger. A trigger event occurs when a signal passes through
        a specified voltage level in a specified direction and is controlled by the
        WIDth specifies that the trigger occurs when a pulse with a specified with is found.
        TIMEOut specifies that a trigger occurs when a pulse with the specified timeout
        is found.
        RUNt specifies that a trigger occurs when a pulse with the specified parameters
        is found.
        WINdow specifies that a trigger occurs when a signal with the specified window
        parameters is found.
        LOGIc specifies that a trigger occurs when specified conditions are met and is
        controlled by the TRIGger:{A|B}:LOGIc commands.
        SETHold specifies that a trigger occurs when a signal is found that meets the
        setup and hold parameters.
        Transition specifies that a trigger occurs when a specified pulse is found that
        meets the transition trigger parameters.
        BUS specifies that a trigger occurs when a signal is found that meets the specified
        bus setup parameters.
        """,
        validator=strict_discrete_set,
        values=TRIGGER_TYPES,
        map_values=True,
    )

    trigger_mode = Instrument.control(
        "TRIGger:A:MODe?",
        "TRIGger:A:MODe %s",
        """Control the trigger sweep mode (string).

        <mode>:= {AUTO|NORMal}

        - auto : When AUTO sweep mode is selected, the oscilloscope begins to search for the
          trigger signal that meets the conditions.
          If the trigger signal is satisfied, the running state on the top left corner of
          the user interface shows Trig'd, and the interface shows stable waveform.
          Otherwise, the running state always shows Auto, and the interface shows unstable
          waveform.
        - normal : When NORMAL sweep mode is selected, the oscilloscope enters the wait trigger
          state and begins to search for trigger signals that meet the conditions.
          If the trigger signal is satisfied, the running state shows Trig'd, and the interface
          shows stable waveform.
          Otherwise, the running state shows Ready, and the interface displays the last
          triggered waveform (previous trigger) or does not display the waveform (no
          previous trigger).
          Then, the oscilloscope stops scanning, the RUN/STOP key is red light,
          and the running status shows Stop.
          Otherwise, the running state shows Ready, and the interface does not display the waveform.
        """,
        validator=strict_discrete_set,
        values={"normal": "NORMAL", "auto": "AUTO"},
        map_values=True,
    )

    trigger_holdoff_by = Instrument.control(
        "TRIGger:A:HOLDoff:BY?",
        "TRIGger:A:HOLDoff:BY %s",
        """Control the type of holdoff for the A trigger.
        Holdoff types are expressed as either user-specified time (TIMe)
        or by an internally calculated random time value (RANDom).""",
        validator=strict_discrete_set,
        values=["TIME", "RANDOM"],
    )

    trigger_holdoff_time = Instrument.control(
        "TRIGger:A:HOLDoff:TIMe?",
        "TRIGger:A:HOLDoff:TIMe %s",
        """Control the A trigger holdoff time.""",
        validator=strict_range,
        values=[0, 10],
    )

    # Edge trigger settings
    trigger_edge_source = Instrument.control(
        "TRIGger:A:EDGE:SOUrce?",
        "TRIGger:A:EDGE:SOUrce %s",
        """Control the source for the edge trigger.
        For instruments that have an Auxiliary Input
        (such as the MSO58LP), AUXiliary can be selected as trigger source.""",
        validator=strict_discrete_set,
        values=ANALOG_TRIGGER_SOURCE + DIGITAL_TRIGGER_SOURCE,
        dynamic=True,
    )

    trigger_edge_slope = Instrument.control(
        "TRIGger:A:EDGE:SLOpe?",
        "TRIGger:A:EDGE:SLOpe %s",
        """Control the slope for the edge trigger.
        """,
        validator=strict_discrete_set,
        values=_TRIGGER_SLOPES,
        map_values=True,
        dynamic=True,
    )

    trigger_edge_coupling = Instrument.control(
        "TRIGger:A:EDGE:COUPling?",
        "TRIGger:A:EDGE:COUPling %s",
        """Control the coupling for the edge trigger.
        """,
        validator=strict_discrete_set,
        values=_TRIGGER_COUPLING,
        map_values=True,
    )

    # Pulse Width Trigger Settings
    trigger_width_source = Instrument.control(
        "TRIGger:A:PULSEWidth:SOUrce?",
        "TRIGger:A:PULSEWidth:SOUrce %s",
        """Control the source waveform for a pulse width trigger.
        """,
        validator=strict_discrete_set,
        values=ANALOG_TRIGGER_SOURCE,
    )

    trigger_width_polarity = Instrument.control(
        "TRIGger:A:PULSEWidth:POLarity?",
        "TRIGger:A:PULSEWidth:POLarity %s",
        """Control the polarity for a pulse width trigger.
        """,
        validator=strict_discrete_set,
        values={"negative": "NEGATIVE", "positive": "POSITIVE"},
        map_values=True,
    )

    trigger_width_when = Instrument.control(
        "TRIGger:A:PULSEWidth:WHEn?",
        "TRIGger:A:PULSEWidth:WHEn %s",
        """Control the trigger when a pulse is detected with a width (duration)
        that is less than, greater than, equal to, or unequal to a specified value.
        {LESSthan|MOREthan|EQual|UNEQual|WIThin|OUTside}

        Arguments
        LESSthan causes a trigger when a pulse is detected with a width less than the
        time set by the TRIGger:{A|B}:PULSEWidth:LOWLimit command.

        MOREthan causes a trigger when a pulse is detected with a width greater than the
        time set by the TRIGger:{A|B}:PULSEWidth:LOWLimit command.

        EQual causes a trigger when a pulse is detected with a width equal to the time
        period specified in TRIGger:{A|B}:PULSEWidth:LOWLimit within a ±5%
        tolerance.

        UNEQual causes a trigger when a pulse is detected with a width
        greater than or less than (but not equal) the time period specified in
        TRIGger:{A|B}:PULSEWidth:LOWLimit within a ±5% tolerance.

        WIThin causes a trigger when a pulse is detected that is within a range set by
        two values.

        OUTside causes a trigger when a pulse is detected that is outside of a range set
        by two values.
        """,
        validator=strict_discrete_set,
        values=["LESSthan", "MOREthan", "EQual", "UNEQual", "WIThin", "OUTside"],
        map_values=True,
    )

    trigger_width_lowlimit = Instrument.control(
        "TRIGger:A:PULSEWidth:LOWLimit?",
        "TRIGger:A:PULSEWidth:LOWLimit %g",
        """Control the lower limit to use, in seconds, when triggering on detection
        of a pulse whose duration is inside or outside a range of two values.

        This command also specifies the single limit to use, in seconds,
        when triggering on detection of a pulse whose duration is less than,
        greater than, equal to, or not equal to this time limit.
        """,
    )

    trigger_width_highlimit = Instrument.control(
        "TRIGger:A:PULSEWidth:HIGHLimit?",
        "TRIGger:A:PULSEWidth:HIGHLimit %g",
        """Control the upper limit to use, in seconds, when triggering on
        detection of a pulse whose duration is inside or outside
        a range of two values.
        """,
    )

    # Window Trigger Settings
    trigger_window_source = Instrument.control(
        "TRIGger:A:WINdow:SOUrce?",
        "TRIGger:A:WINdow:SOUrce %s",
        """Control the source for a window trigger.
        """,
        validator=strict_discrete_set,
        values=ANALOG_TRIGGER_SOURCE,
    )

    trigger_window_crossing = Instrument.control(
        "TRIGger:A:WINdow:CROSSIng?",
        "TRIGger:A:WINdow:CROSSIng %s",
        """Control the window trigger threshold crossing of the
        selected trigger source. The threshold crossing selection is only effective when
        :TRIGger:{A|B}:WINdow:WHEn is INSIDEGreater or OUTSIDEGreater.
        """,
        validator=strict_discrete_set,
        values=["UPPER", "LOWER", "EITHER", "NONE"],
        map_values=True,
    )

    trigger_window_when = Instrument.control(
        "TRIGger:A:WINdow:WHEn?",
        "TRIGger:A:WINdow:WHEn %s",
        """Control the window trigger event.
        This command is equivalent to selecting Window Setup from the Trig menu
        and selecting from the Window Trigger When box.
        Arguments
        OUTSIDEGreater specifies a trigger event when the signal leaves the window
        defined by the threshold levels for the time specified by Width.
        INSIDEGreater specifies a trigger event when the signal enters the window
        defined by the threshold levels for the time specified by Width.
        ENTERSWindow specifies a trigger event when the signal enters the window
        defined by the threshold levels.
        EXITSWindow specifies a trigger event when the signal leaves the window defined
        by the threshold levels.
        """,
        validator=strict_discrete_set,
        values=["ENTERSW", "EXITSW", "INSIDEG", "OUTSIDEG"],
        map_values=True,
    )

    trigger_window_width = Instrument.control(
        "TRIGger:A:WINdow:WIDTH?",
        "TRIGger:A:WINdow:WIDTH %g",
        """Control the minimum width for a window violation.""",
    )

    # Download data
    def download_image(self):
        """Get a PNG image of oscilloscope screen in bytearray.
        """
        self.write('SAVE:IMAGe \"C:/Temp.png\"')
        self.write('FILESystem:READFile \"C:/Temp.png\"')
        img = self.read_bytes(-1)
        self.write('FILESystem:DELEte \"C:/Temp.png\"')
        return bytearray(img)

    # Measurement
    _measurable_parameters = ["ACCOMMONMODE", "ACRMS", "AMPlITUDE", "AREA", "BASE", "BITAMPLITUDE",
                              "BITHIGH", "BITLOW", "BURSTWIDTH", "COMMONMODE", "DATARATE", "DCD",
                              "DDJ", "DDRAOS", "DDRAOSPERTCK", "DDRAOSPERUI", "DDRAUS",
                              "DDRAUSPERTCK", "DDRAUSPERUI", "DDRHOLDDIFF", "DDRSETUPDIFF",
                              "DDRTCHABS", "DDRTCHAVERAGE", "DDRTCKAVERAGE", "DDRTCLABS",
                              "DDRTCLAVERAGE", "DDRTERRMN", "DDRTERRN", "DDRTJITCC", "DDRTJITDUTY",
                              "DDRTJITPER", "DDRTPST", "DDRTRPRE", "DDRTWPRE", "DDRVIXAC",
                              "DDRTDQSCK", "DELAY", "DJ", "DJDIRAC", "EYEHIGH", "EYELOW",
                              "FALLSLEWRATE", "FALLTIME", "FREQUENCY", "F2", "F4", "F8", "HEIGHT",
                              "HEIGHTBER", "HIGH", "HIGHTIME", "HOLD", "IMDAPOWERQUALITY",
                              "IMDAHARMONICS", "IMDAINPUTVOLTAGE", "IMDAINPUTCURRENT",
                              "IMDAINPUTPOWER", "IMDAPHASORDIAGRAM", "IMDAEFFICIENCY",
                              "IMDALINERIPPLE", "IMDASWITCHRIPPLE", "IMDADQ0", "JITTERSUMMARY",
                              "J2", "J9", "LOW", "LOWTIME", "MAXIMUM", "MEAN", "MINIMUM", "NDUTY",
                              "NOVERSHOOT", "NPERIOD", "NPJ", "NWIDTH", "PDUTY", "PERIOD", "PHASE",
                              "PHASENOISE", "PJ", "PK2PK", "POVERSHOOT", "PWIDTH", "QFACTOR",
                              "RISESLEWRATE", "RISETIME", "RJ", "RJDIRAC", "RMS", "SETUP", "SKEW",
                              "SRJ", "SSCFREQDEV", "SSCMODRATE", "TIE", "TIMEOUTSIDELEVEL",
                              "TIMETOMAX", "TIMETOMIN", "TJBER", "TNTRATIO", "TOP", "UNITINTERVAL",
                              "VDIFFXOVR", "WIDTH", "WIDTHBER"]

    measurement_add_slot = Instrument.setting(
        "MEASUrement:ADDNew MEAS%d",
        """Set the specified measurement.
        :param slot >=1
        """,
    )

    measurement_add = Instrument.setting(
        "MEASUrement:ADDMEAS %s",
        """Set a measurement.""",
        validator=strict_discrete_set,
        values=_measurable_parameters,
    )

    measurement_gating_type = Instrument.control(
        "MEASUrement:GATing?", "MEASUrement:GATing %s",
        """Control the gating type for the measurement.
        :param slot: int
        :param gating_type: str
        NONE specifies measurements are taken across the entire record.
        SCREEN turns on gating, using the left and right edges of the screen.
        CURSor limits measurements to the portion of the waveform between the vertical
        bar cursors, even if they are off screen.
        LOGic specifies that measurements are taken only when the logical state of other
        waveforms is true.
        SEARch specifies that measurements are taken only where the results of a user
        specified search are found.
        TIMe limits measurements to the portion of the waveform between the Start and
        End gate times.
        """,
        validator=strict_discrete_set,
        values=["NONE", "SCREEN", "CURSOR", "LOGIC", "SEARCH", "TIME"],
    )

    measurement_gating_starttime = Instrument.control(
        "MEASUrement:GATing:STARTtime?", "MEASUrement:GATing:STARTtime %g",
        """Control the start gate time for all measurements that use Global gating.
        """,
    )

    measurement_gating_endtime = Instrument.control(
        "MEASUrement:GATing:ENDtime?", "MEASUrement:GATing:ENDtime %g",
        """Control the end gate time for all measurements that use Global gating.
        """,
    )

    measurement_gating_active = Instrument.control(
        "MEASUrement:GATing:ACTive?", "MEASUrement:GATing:ACTive %s",
        """Control the global gating active level used for logic gating.
        """,
        validator=strict_discrete_set,
        values=["HIGH", "LOW"],
    )

    measurement_gating_hysteresis = Instrument.control(
        "MEASUrement:GATing:HYSTeresis?", "MEASUrement:GATing:HYSTeresis %g",
        """Control the global gating hysteresis value used for logic gating.
        """,
    )

    measurement_gating_logicsource = Instrument.control(
        "MEASUrement:GATing:LOGICSource?", "MEASUrement:GATing:LOGICSource %s",
        """Control the gating data source used for logic gating.

        accepted values are CH<x>, MATH<x>, REF<x>
        """,
    )

    measurement_gating_threshold = Instrument.control(
        "MEASUrement:GATing:MIDRef?", "MEASUrement:GATing:MIDRef %g",
        """Control the global gating mid ref value used for logic gating.
        """,
    )

    measurement_gating_searchsource = Instrument.control(
        "MEASUrement:GATing:SEARCHSource?", "MEASUrement:GATing:SEARCHSource %s",
        """Control the global gating search source when the gating type is search.
        """,
    )

    def measurement_clear_all(self):
        """deletes all the active instances of measurements defined in the scope application."""
        self.write("MEASUrement:DELETEALL")

    def measurement_population_config(self, slot: int, global_flag=0,
                                      limit_state=0, limit_value=1000):
        """Configure the measurement population settings.
        :param slot
        :param global_flag : int
        0 specifies that population settings can be changed independently
        for each individual measurement.
        1 applies the global population settings to all the measurements' population
        settings.
        :param limit_state : int 0 turns off the population limit.
        1 turns on the population limit.
        :param limit_value : int population limit value for the measurement.
        """
        self.write(f'MEASUrement:MEAS{slot}:POPUlation:GLOBal {global_flag}')
        self.write(f'MEASUrement:MEAS{slot}:POPUlation:LIMIT:STATE {limit_state}')
        self.write(f'MEASUrement:MEAS{slot}:POPUlation:LIMIT:VALue {limit_value}')

    def measurement_result_curracq_mean(self, slot):
        """Returns the mean value for the measurement for the
        current acquisition."""
        self.write(f'MEASUrement:MEAS{slot}:RESUlts:CURRentacq:MEAN?')
        return float(self.read().strip('\n'))

    def measurement_result_curracq_max(self, slot):
        """Returns the maximum value for the measurement for the
        current acquisition."""
        self.write(f'MEASUrement:MEAS{slot}:RESUlts:CURRentacq:MAX?')
        return float(self.read().strip('\n'))

    def measurement_result_curracq_min(self, slot):
        """Returns the minimum value for the measurement for the
        current acquisition."""
        self.write(f'MEASUrement:MEAS{slot}:RESUlts:CURRentacq:MIN?')
        return float(self.read().strip('\n'))

    def measurement_result_curracq_stddev(self, slot):
        """Returns the standard deviation for the specified
        measurement for all acquisitions accumulated
        since statistics were last reset."""
        self.write(f'MEASUrement:MEAS{slot}:RESUlts:CURRentacq:STDDev?')
        return float(self.read().strip('\n'))

    def measurement_result_curracq_population(self, slot):
        """Returns the population for the specified measurement
        for the current acquisition."""
        self.write(f'MEASUrement:MEAS{slot}:RESUlts:CURRentacq:POPUlation?')
        return int(self.read().strip('\n'))

    def measurement_result_allacqs_mean(self, slot):
        """Returns the mean value for all accumulated
        measurement acquisitions."""
        self.write(f'MEASUrement:MEAS{slot}:RESUlts:ALLAcqs:MEAN?')
        return float(self.read().strip('\n'))

    def measurement_result_allacqs_max(self, slot):
        """Returns the maximum value for all accumulated
        measurement acquisitions."""
        self.write(f'MEASUrement:MEAS{slot}:RESUlts:ALLAcqs:MAX?')
        return float(self.read().strip('\n'))

    def measurement_result_allacqs_min(self, slot):
        """Returns the minimum value for all accumulated
        measurement acquisitions."""
        self.write(f'MEASUrement:MEAS{slot}:RESUlts:ALLAcqs:MIN?')
        return float(self.read().strip('\n'))

    def measurement_result_allacqs_stddev(self, slot):
        """Returns the standard deviation for all accumulated
        measurement acquisitions."""
        self.write(f'MEASUrement:MEAS{slot}:RESUlts:ALLAcqs:STDDev?')
        return float(self.read().strip('\n'))

    def measurement_result_allacqs_population(self, slot):
        """Returns returns the population measurement value."""
        self.write(f'MEASUrement:MEAS{slot}:RESUlts:ALLAcqs:POPUlation?')
        return int(self.read().strip('\n'))

    def measurement_configure(self, slot: int, source1, source2, meas_type):
        """Configure the measurement

        :param slot: int measurement slot number
        :param source1: str channel measurement source
        :param source2: str second channel source
        :param meas_type: str measurement type"""
        slot = truncated_range(slot, [1, 1000])
        source1 = strict_discrete_set(source1, self.ANALOG_TRIGGER_SOURCE)
        source2 = strict_discrete_set(source2, self.ANALOG_TRIGGER_SOURCE)
        meas_type = strict_discrete_set(meas_type, self._measurable_parameters)
        self.write(f'MEASUrement:MEAS{slot}:SOUrce1 {source1};*WAI')
        self.write(f'MEASUrement:MEAS{slot}:SOUrce2 {source2};*WAI')
        self.write(f'MEASUrement:MEAS{slot}:TYPe {meas_type};*WAI')

    # Display
    intensity_backlight = Instrument.control(
        "DISplay:INTENSITy:BACKLight?", "DISplay:INTENSITy:BACKLight %s",
        """Control the display backlight intensity setting""",
        validator=strict_range,
        values=['LOW', 'MEDIUM', 'HIGH'],
    )

    # Analog Function Generator
    afg_output_state = Instrument.control(
        "AFG:OUTPUT:STATE?", "AFG:OUTPUT:STATE %d",
        """Control the AFG output state.""",
        validator=strict_discrete_set,
        values=_BOOLS,
    )

    afg_output_mode = Instrument.control(
        "AFG:OUTPut:MODe?", "AFG:OUTPut:MODe %s",
        """Control the AFG output mode.""",
        validator=strict_discrete_set,
        values=["OFF", "CONTINUOUS", "BURST"],
    )

    afg_output_load_impedance = Instrument.control(
        "AFG:OUTPut:LOAd:IMPEDance?", "AFG:OUTPut:LOAd:IMPEDance %s",
        """Control the AFG output load impedance.""",
        validator=strict_discrete_set,
        values=["FIFTY", "HIGHZ"],
    )

    afg_offset = Instrument.control(
        "AFG:OFFSet?", "AFG:OFFSet %g",
        """Control the AFG offset value, in volts.""",
    )

    afg_noise_state = Instrument.control(
        "AFG:NOISEADD:STATE?", "AFG:NOISEADD:STATE %d",
        """Control the AFG additive noise state.""",
        validator=strict_discrete_set,
        values=_BOOLS,
    )

    afg_noise_level = Instrument.control(
        "AFG:NOISEAdd:PERCent?", "AFG:NOISEAdd:PERCent %f",
        """Control the AFG additive noise level as a percentage. Minimum is 0.0%,
        maximum is 100.0% and increment is 1.0%.""",
        validator=lambda v, vs: strict_discrete_range(v, vs, step=1.0),
        values=[0.0, 100.0],
    )

    afg_lowlvl = Instrument.control(
        "AFG:LOWLevel?", "AFG:LOWLevel %g",
        """Control the low level value of the output waveform, in
        volts, when using the arbitrary function generator feature.""",
    )

    afg_highlvl = Instrument.control(
        "AFG:HIGHLevel?", "AFG:HIGHLevel %g",
        """Control the high level value of the output waveform, in
        volts, when using the arbitrary function generator feature.""",
    )

    afg_function = Instrument.control(
        "AFG:FUNCtion?", "AFG:FUNCtion %s",
        """Control which AFG function to execute.""",
        validator=strict_discrete_set,
        values=["SINE", "SQUARE", "PULSE", "RAMP", "NOISE", "DC", "SINC", "GAUSSIAN", "LORENTZ",
                "ERISE", "EDECAY", "HAVERSINE", "CARDIAC", "ARBITRARY"]
    )

    afg_frequency = Instrument.control(
        "AFG:FREQuency?", "AFG:FREQuency %g",
        """Control the AFG frequency, in Hz.""",
        validator=strict_range,
        values=[0.1, 50.000E6],
    )

    afg_period = Instrument.control(
        "AFG:PERIod?", "AFG:PERIod %f",
        """Control the period of the AFG waveform, in seconds.""",
        validator=strict_range,
        values=[2.0E-8, 10],
    )

    afg_burst_trigger = Instrument.setting(
        "AFG:BURSt:TRIGger",
        """Set a burst trigger on AFG output.""",
    )

    afg_burst_ccount = Instrument.control(
        "AFG:BURSt:CCOUnt?", "AFG:BURSt:CCOUnt %d",
        """Control the cycle count for AFG burst mode.""",
    )

    afg_arbitrary_source = Instrument.control(
        "AFG:ARBitrary:SOUrce?", "AFG:ARBitrary:SOUrce %s",
        """Control the source name for the Arbitrary Waveform.
        Currently supported sources are either waveform file
        (.wfm) or text file (.csv).""",
    )

    afg_amplitude = Instrument.control(
        "AFG:AMPLitude?", "AFG:AMPLitude %f",
        """Control the AFG amplitude in volts, peak to peak.
        The amplitude range varies with the load impedance
        and the output function.
        Waveform    50Ohms      HighZ
        Sine        10mv..2.5V  20mV..5V
        Square      10mv..2.5V  20mV..5V
        Pulse       10mv..2.5V  20mV..5V
        Ramp        10mv..2.5V  20mV..5V
        DC          0V +/-1.25V 0V..+/-2.5V
        """,
    )

    afg_pulsewidth = Instrument.control(
        "AFG:PULse:WIDth?", "AFG:PULse:WIDth %f",
        """Control the AFG pulse width, in seconds.
        The range is [10%*Period, 90%*Period]""",
    )

    afg_rampsymetry = Instrument.control(
        "AFG:RAMP:SYMmetry?", "AFG:RAMP:SYMmetry %f",
        """Control the AFG ramp symmetry in percent. Minimum is 0.0%,
        maximum is 100.0% and increment is 0.10%.""",
        validator=lambda v, vs: strict_discrete_range(v, vs, step=0.1),
        values=[0.0, 100.0],
    )

    afg_squareduty = Instrument.control(
        "AFG:SQUare:DUty?", "AFG:SQUare:DUty %f",
        """Control the AFG duty cycle in percent. The minimum is 10.0%,
        maximum is 90.0% and increment is 0.10%.""",
        validator=lambda v, vs: strict_discrete_range(v, vs, step=0.1),
        values=[10.0, 90.0],
    )


class TektronixMSO58(TektronixMsoScope):
    """A class representing the Tektronix MSO58 Scope.

        This scope has 8 analog input and is part of the
        :class:`~.TektronixMsoScope` family of instruments; for documentation refer to
        this base class.
    """

    def __init__(self, adapter,
                 name="Tektronix MSO58 Oscilloscope",
                 active_channels=8,
                 **kwargs):
        super().__init__(adapter, name, active_channels, **kwargs)


class TektronixMSO64(TektronixMsoScope):
    """A class representing the Tektronix MSO64 Scope.

        This scope has 4 analog input and is part of the
        :class:`~.TektronixMsoScope` family of instruments; for documentation refer to
        this base class.
    """

    def __init__(self, adapter,
                 name="Tektronix MSO64 Oscilloscope",
                 active_channels=4,
                 **kwargs):
        super().__init__(adapter, name, active_channels, **kwargs)

    ANALOG_TRIGGER_SOURCE = ['CH1', 'CH2', 'CH3', 'CH4']
    DIGITAL_TRIGGER_SOURCE = ['CH1_D0', 'CH1_D1', 'CH1_D2', 'CH1_D3',
                              'CH1_D4', 'CH1_D5', 'CH1_D6', 'CH1_D7',
                              'CH2_D0', 'CH2_D1', 'CH2_D2', 'CH2_D3',
                              'CH2_D4', 'CH2_D5', 'CH2_D6', 'CH2_D7',
                              'CH3_D0', 'CH3_D1', 'CH3_D2', 'CH3_D3',
                              'CH3_D4', 'CH3_D5', 'CH3_D6', 'CH3_D7',
                              'CH4_D0', 'CH4_D1', 'CH4_D2', 'CH4_D3',
                              'CH4_D4', 'CH4_D5', 'CH4_D6', 'CH4_D7']
