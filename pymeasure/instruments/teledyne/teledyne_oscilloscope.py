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

from abc import ABCMeta
import re
import sys
import time
from decimal import Decimal
import numpy as np

from pymeasure.instruments import Instrument, Channel, SCPIUnknownMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range, \
    strict_discrete_range


def sanitize_source(source):
    """Parse source string.

    :param source: can be "cX", "ch X", "chan X", "channel X", "math" or "line", where X is
    a single digit integer. The parser is case and white space insensitive.
    :return: can be "C1", "C2", "C3", "C4", "MATH" or "LINE.
    """

    match = re.match(r"^\s*(C|CH|CHAN|CHANNEL)\s*(?P<number>\d)\s*$|"
                     r"^\s*(?P<name_only>MATH|LINE)\s*$", source, re.IGNORECASE)
    if match:
        if match.group("number") is not None:
            source = "C" + match.group("number")
        else:
            source = match.group("name_only")
        source = source.upper()
    else:
        raise ValueError(f"source {source} not recognized")
    return source


def _trigger_select_num_pars(value):
    """Find the expected number of parameters for the trigger_select property.

    :param value: input parameters as a tuple
    """
    value = tuple(map(lambda v: v.upper() if isinstance(v, str) else v, value))
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


def _trigger_select_validator(value, values, num_pars_finder=_trigger_select_num_pars):
    """Validate the input of the trigger_select property.

    :param value: input parameters as a tuple
    :param values: allowed space for each parameter
    :param num_pars_finder: function to find the number of expected parameters
    """
    if not isinstance(value, tuple):
        raise ValueError('Input value {} of trigger_select should be a tuple'.format(value))
    if len(value) < 3 or len(value) > 5:
        raise ValueError('Number of parameters {} can only be 3, 4, 5'.format(len(value)))
    value = tuple(map(lambda v: v.upper() if isinstance(v, str) else v, value))
    value = list(value)
    value[1] = sanitize_source(value[1])
    value = tuple(value)
    if value[0] not in values.keys():
        raise ValueError('Value {} not in the discrete set {}'.format(value[0], values.keys()))
    num_expected_pars = num_pars_finder(value)
    if len(value) != num_expected_pars:
        raise ValueError('Number of parameters {} != {}'.format(len(value), num_expected_pars))
    for i, element in enumerate(value[1:], start=1):
        if i < 3:
            strict_discrete_set(element, values=values[value[0]][i - 1])
        else:
            strict_range(element, values=values[value[0]][i - 1])
    return value


def _trigger_select_get_process(value):
    """Process the output of the trigger_select property.

    The format of the input list is

        <trig_type>, SR, <source>, HT, <hold_type>[, HV, <hold_value1>S][, HV2, <hold_value2>S]

    The format of the output list is

        <trig_type>, <source>, <hold_type>[, <hold_value1>][, <hold_value2>]

    :param value: output parameters as a list
    """
    output = []
    if len(value) > 0:
        output.append(value[0].lower())
    if "SR" in value:
        output.append(value[value.index("SR") + 1].lower())
    if "HT" in value:
        output.append(value[value.index("HT") + 1].lower())
    if "HV" in value:
        output.append(float(value[value.index("HV") + 1][:-1]))
    if "HV2" in value:
        output.append(float(value[value.index("HV2") + 1][:-1]))
    return output


def _results_list_to_dict(results):
    """Turn a list into a dict, using the uneven indices as keys.

    E.g. turn ['C1', 'OFF', 'C2', 'OFF'] into {'C1': 'OFF', 'C2': 'OFF'}
    """
    keys = results[::2]
    values = results[1::2]
    return dict(zip(keys, values))


def _remove_unit(value):
    """Remove a unit from the returned string and cast to float."""
    if isinstance(value, float):
        return value

    if value.endswith(" V"):
        value = value[:-2]

    return float(value)


def _intensity_validator(value, values):
    """Validate the input of the intensity property (grid intensity and trace intensity).

    :param value: input parameters as a 2-element tuple
    :param values: allowed space for each parameter
    """
    if not isinstance(value, tuple):
        raise ValueError('Input value {} of trigger_select should be a tuple'.format(value))
    if len(value) != 2:
        raise ValueError('Number of parameters {} different from 2'.format(len(value)))
    for i in range(2):
        strict_discrete_range(value=value[i], values=values[i], step=1)
    return value


class _ChunkResizer:
    """The only purpose of this class is to resize the chunk size of the instrument adapter.

    This is necessary when reading a big chunk of data from the oscilloscope like image dumps and
    waveforms.

    .. Note::
        Only if the new chunk size is bigger than the current chunk size, it is resized.

    """

    def __init__(self, adapter, chunk_size):
        """Just initialize the object attributes.

        :param adapter: Adapter of the instrument. This is usually accessed through the
                        Instrument::adapter attribute.
        :param chunk_size: new chunk size (int).
        """
        self.adapter = adapter
        self.old_chunk_size = None
        self.new_chunk_size = int(chunk_size) if chunk_size else 0

    def __enter__(self):
        """Only resize the chunk size if the adapter support this feature."""
        if (self.adapter.connection is not None
                and hasattr(self.adapter.connection, "chunk_size")):
            if self.new_chunk_size > self.adapter.connection.chunk_size:
                self.old_chunk_size = self.adapter.connection.chunk_size
                self.adapter.connection.chunk_size = self.new_chunk_size

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.old_chunk_size is not None:
            self.adapter.connection.chunk_size = self.old_chunk_size


class TeledyneOscilloscopeChannel(Channel, metaclass=ABCMeta):
    """A base abstract class for channel on a :class:`TeledyneOscilloscope` device."""

    _BOOLS = {True: "ON", False: "OFF"}

    BANDWIDTH_LIMITS = ["OFF", "ON"]

    TRIGGER_SLOPES = {"negative": "NEG", "positive": "POS"}

    # Capture and split a reply like "RMS,281E-6" and "RMS,281E-6,OK"
    # The third response item ("state"), is not present in all oscilloscopes
    # For compatibility it is captured if it can, but ignored otherwise
    _re_pava_response = re.compile(r"^\s*"
                                   r"(?P<parameter>\w+),\s*"
                                   r"(?P<value>[^,]*)\s*"
                                   r"(?:,(?P<state>\w+)\s*)?$")

    bwlimit = Instrument.control(
        "BWL?", "BWL %s",
        """Control the internal low-pass filter for this channel.

        The current bandwidths can only be read back for all channels at once!
        """,
        validator=strict_discrete_set,
        values=BANDWIDTH_LIMITS,
        get_process=_results_list_to_dict,
        dynamic=True,
    )

    coupling = Instrument.control(
        "CPL?", "CPL %s",
        """Control the coupling with a string parameter ("ac 1M", "dc 1M", "ground").""",
        validator=strict_discrete_set,
        values={"ac 1M": "A1M", "dc 1M": "D1M", "ground": "GND"},
        map_values=True
    )

    display = Instrument.control(
        "TRA?", "TRA %s",
        """Control the display enabled state. (strict bool)""",
        validator=strict_discrete_set,
        values=_BOOLS,
        map_values=True
    )

    offset = Instrument.control(
        "OFST?", "OFST %.2EV",
        """Control the center of the screen in Volts by a a float parameter.
        The range of legal values varies depending on range and scale. If the specified
        value is outside of the legal range, the offset value is automatically set to the nearest
        legal value.
        """
    )

    probe_attenuation = Instrument.control(
        "ATTN?", "ATTN %g",
        """Control the probe attenuation. The probe attenuation may be from 0.1 to 10000.""",
        validator=strict_discrete_set,
        values={0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000}
    )

    scale = Instrument.control(
        "VDIV?", "VDIV %.2EV",
        """Control the vertical scale (units per division) in Volts."""
    )

    trigger_coupling = Instrument.control(
        "TRCP?", "TRCP %s",
        """Control the input coupling for the selected trigger sources (string).

        - ac: AC coupling block DC component in the trigger path, removing dc offset
          voltage from the trigger waveform. Use AC coupling to get a stable edge trigger when
          your waveform has a large dc offset.
        - dc: DC coupling allows dc and ac signals into the trigger path.
        - lowpass: HFREJ coupling places a lowpass filter in the trigger path.
        - highpass: LFREJ coupling places a highpass filter in the trigger path.

        """,
        validator=strict_discrete_set,
        values={"ac": "AC", "dc": "DC", "lowpass": "HFREJ", "highpass": "LFREJ"},
        map_values=True
    )

    trigger_level = Instrument.control(
        "TRLV?", "TRLV %.2EV",
        """Control the trigger level voltage for the active trigger source (float).

        When there are two trigger levels to set, this command is used to set the higher
        trigger level voltage for the specified source. :attr:`trigger_level2` is used to set
        the lower trigger level voltage.

        When setting the trigger level it must be divided by the probe attenuation. This is
        not documented in the datasheet and it is probably a bug of the scope firmware.
        An out-of-range value will be adjusted to the closest legal value.
        """,
        get_process=_remove_unit,
    )

    trigger_slope = Instrument.control(
        "TRSL?", "TRSL %s",
        """Control the trigger slope of the specified trigger source (string).

        <trig_slope>:={NEG,POS,WINDOW} for edge trigger
        <trig_slope>:={NEG,POS} for other trigger

        +------------+--------------------------------------------------+
        | parameter  | trigger slope                                    |
        +------------+--------------------------------------------------+
        | negative   | Negative slope for edge trigger or other trigger |
        +------------+--------------------------------------------------+
        | positive   | Positive slope for edge trigger or other trigger |
        +------------+--------------------------------------------------+
        | window     | Window slope for edge trigger                    |
        +------------+--------------------------------------------------+

        """,
        validator=strict_discrete_set,
        values=TRIGGER_SLOPES,
        map_values=True,
        dynamic=True,
    )

    _measurable_parameters = ["PKPK", "MAX", "MIN", "AMPL", "TOP", "BASE", "CMEAN", "MEAN", "RMS",
                              "CRMS", "OVSN", "FPRE", "OVSP", "RPRE", "PER", "FREQ", "PWID",
                              "NWID", "RISE", "FALL", "WID", "DUTY", "NDUTY", "ALL"]

    display_parameter = Instrument.setting(
        "PACU %s",
        """Set the waveform processing of this channel with the specified algorithm and the result
        is displayed on the front panel.

        The command accepts the following parameters:

        =========   ===================================
        Parameter   Description
        =========   ===================================
        PKPK        vertical peak-to-peak
        MAX         maximum vertical value
        MIN         minimum vertical value
        AMPL        vertical amplitude
        TOP         waveform top value
        BASE        waveform base value
        CMEAN       average value in the first cycle
        MEAN        average value
        RMS         RMS value
        CRMS        RMS value in the first cycle
        OVSN        overshoot of a falling edge
        FPRE        preshoot of a falling edge
        OVSP        overshoot of a rising edge
        RPRE        preshoot of a rising edge
        PER         period
        FREQ        frequency
        PWID        positive pulse width
        NWID        negative pulse width
        RISE        rise-time
        FALL        fall-time
        WID         Burst width
        DUTY        positive duty cycle
        NDUTY       negative duty cycle
        ALL         All measurement
        =========   ===================================
        """,
        validator=strict_discrete_set,
        values=_measurable_parameters
    )

    def measure_parameter(self, parameter: str):
        """Process a waveform with the selected algorithm and returns the specified measurement.

        :param parameter: same as the display_parameter property
        """
        parameter = strict_discrete_set(value=parameter, values=self._measurable_parameters)
        output = self.ask("PAVA? %s" % parameter)
        match = self._re_pava_response.match(output)
        if match:
            if match.group('parameter') != parameter:
                raise ValueError(f"Parameter {match.group('parameter')} different from {parameter}")
            if match.group('state') and match.group('state') == 'IV':
                raise ValueError(f"Parameter state for {parameter} is invalid")
            return float(match.group('value'))
        else:
            raise ValueError(f"Cannot extract value from output {output}")

    def insert_id(self, command):
        # only in case of the BWL and PACU commands the syntax is different. Why? SIGLENT Why?
        if command[0:4] == "BWL ":
            return "BWL C%d,%s" % (self.id, command[4:])
        elif command[0:5] == "PACU ":
            return "PACU %s,C%d" % (command[5:], self.id)
        else:
            return "C%d:%s" % (self.id, command)

    # noinspection PyIncorrectDocstring
    def setup(self, **kwargs):
        """Setup channel. Unspecified settings are not modified.

        Modifying values such as probe attenuation will modify offset, range, etc. Refer to
        oscilloscope documentation and make multiple consecutive calls to setup() if needed.
        See property descriptions for more information.

        :param bwlimit:
        :param coupling:
        :param display:
        :param invert:
        :param offset:
        :param skew_factor:
        :param probe_attenuation:
        :param scale:
        :param unit:
        :param trigger_coupling:
        :param trigger_level:
        :param trigger_level2:
        :param trigger_slope:
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def current_configuration(self):
        """Get channel configuration as a dict containing the following keys:

        - "channel": channel number (int)
        - "attenuation": probe attenuation (float)
        - "bandwidth_limit": bandwidth limiting enabled (bool)
        - "coupling": "ac 1M", "dc 1M", "ground" coupling (str)
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

        ch_setup = {
            "channel": self.id,
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
        return ch_setup


class TeledyneOscilloscope(SCPIUnknownMixin, Instrument, metaclass=ABCMeta):
    """A base abstract class for any Teledyne Lecroy oscilloscope.

    All Teledyne oscilloscopes have a very similar interface, hence this base class to combine
    them. Note that specific models will likely have conflicts in their interface.

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

    _BOOLS = TeledyneOscilloscopeChannel._BOOLS

    WRITE_INTERVAL_S = 0.02  # seconds

    ch_1 = Instrument.ChannelCreator(TeledyneOscilloscopeChannel, 1)

    ch_2 = Instrument.ChannelCreator(TeledyneOscilloscopeChannel, 2)

    ch_3 = Instrument.ChannelCreator(TeledyneOscilloscopeChannel, 3)

    ch_4 = Instrument.ChannelCreator(TeledyneOscilloscopeChannel, 4)

    def __init__(self, adapter, name="Teledyne Oscilloscope", **kwargs):
        super().__init__(adapter, name=name, **kwargs)
        if self.adapter.connection is not None:
            self.adapter.connection.timeout = 3000
        self._grid_number = 14  # Number of grids in the horizontal direction
        self._seconds_since_last_write = 0  # Timestamp of the last command
        self._header_size = 16  # bytes
        self._footer_size = 2  # bytes
        self.waveform_source = "C1"
        self.default_setup()

    ################
    # System Setup #
    ################

    def default_setup(self):
        """ Set up the oscilloscope for remote operation.

        The COMM_HEADER command controls the
        way the oscilloscope formats response to queries. This command does not affect the
        interpretation of messages sent to the oscilloscope. Headers can be sent in their long or
        short form regardless of the CHDR setting.
        By setting the COMM_HEADER to OFF, the instrument is going to reply with minimal
        information, and this makes the response message much easier to parse.
        The user should not be fiddling with the COMM_HEADER during operation, because
        if the communication header is anything other than OFF, the whole driver breaks down.
        """
        self._comm_header = "OFF"

    def ch(self, source):
        """ Get channel object from its index or its name. Or if source is "math", just return the
        scope object.

        :param source: can be 1, 2, 3, 4 or C1, C2, C3, C4, MATH
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
        """ Autoscale displayed channels."""
        self.write("ASET")

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
        "CHDR?", "CHDR %s",
        """Control the way the oscilloscope formats response to queries.
        The user should not be fiddling with the COMM_HEADER during operation, because
        if the communication header is anything other than OFF, the whole driver breaks down.
        • SHORT — response starts with the short form of the header word.
        • LONG — response starts with the long form of the header word.
        • OFF — header is omitted from the response and units in numbers are suppressed.""",
        validator=strict_discrete_set,
        values=["OFF", "SHORT", "LONG"],
    )

    ###########
    # General #
    ###########

    bwlimit = Instrument.control(
        "BWL?", "BWL %s",
        """Set the internal low-pass filter for all channels.""",
        validator=strict_discrete_set,
        values=TeledyneOscilloscopeChannel.BANDWIDTH_LIMITS,
        get_process=_results_list_to_dict,
        dynamic=True,
    )

    ##################
    # Timebase Setup #
    ##################

    timebase_offset = Instrument.control(
        "TRDL?", "TRDL %.2ES",
        """Control the time interval in seconds between the trigger event and the reference
        position (at center of screen by default)."""
    )

    timebase_scale = Instrument.control(
        "TDIV?", "TDIV %.2ES",
        """Control the horizontal scale (units per division) in seconds for the main
        window (float).""",
        validator=strict_range,
        values=[1e-9, 100]
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

    ###############
    # Acquisition #
    ###############

    def run(self):
        """Starts repetitive acquisitions.

        This is the same as pressing the Run key on the front panel.
        """
        self.trigger_mode = "normal"

    def stop(self):
        """ Stops the acquisition. This is the same as pressing the Stop key on the front panel."""
        self.write("STOP")

    def single(self):
        """Causes the instrument to acquire a single trigger of data.

        This is the same as pressing the Single key on the front panel.
        """
        self.write("ARM")

    ##################
    #    Waveform    #
    ##################

    waveform_points = Instrument.control(
        "WFSU?", "WFSU NP,%d",
        """Control the number of waveform points to be transferred with
        the digitize method (int). NP = 0 sends all data points.

        Note that the oscilloscope may provide less than the specified nb of points.
        """,
        validator=strict_range,
        get_process=lambda vals: vals[vals.index("NP") + 1],
        values=[0, sys.maxsize]
    )

    waveform_sparsing = Instrument.control(
        "WFSU?", "WFSU SP,%d",
        """Control the interval between data points (integer). For example:

               SP = 0 sends all data points.
               SP = 4 sends 1 point every 4 data points.
        """,
        validator=strict_range,
        get_process=lambda vals: vals[vals.index("SP") + 1],
        values=[0, sys.maxsize]
    )

    waveform_first_point = Instrument.control(
        "WFSU?", "WFSU FP,%d",
        """Control the address of the first data point to be sent (int).
        For waveforms acquired in sequence mode, this refers to the relative address in the
        given segment. The first data point starts at zero and is strictly positive.""",
        validator=strict_range,
        get_process=lambda vals: vals[vals.index("FP") + 1],
        values=[0, sys.maxsize]
    )

    ##################
    #    Waveform    #
    ##################

    memory_size = Instrument.control(
        "MSIZ?", "MSIZ %s",
        """Control the maximum depth of memory (float or string).
        Assign for example 500, 100e6, "100K", "25MA".

        The reply will always be a float.
        """
    )

    @property
    def waveform_preamble(self):
        """Get preamble information for the selected waveform source as a dict with the
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
        """Fill waveform preamble section concerning the Y-axis.
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

    def _digitize(self, src, num_bytes=None):
        """Acquire waveforms according to the settings of the acquire commands.
        Note.
        If the requested number of bytes is not specified, the default chunk size is used,
        but in such a case it cannot be quaranteed that the message is received in its entirety.

        :param src: source of data: "C1", "C2", "C3", "C4", "MATH".
        :param: num_bytes: number of bytes expected from the scope (including the header and
        footer).
        :return: bytearray with raw data.
        """
        with _ChunkResizer(self.adapter, num_bytes):
            binary_values = self.binary_values(f"{src}:WF? DAT2", dtype=np.uint8)
        if num_bytes is not None and len(binary_values) != num_bytes:
            raise BufferError(f"read bytes ({len(binary_values)}) != requested bytes ({num_bytes})")
        return binary_values

    def _header_footer_sanity_checks(self, message):
        """Check that the header follows the predefined format.
        The format of the header is DAT2,#9XXXXXXX where XXXXXXX is the number of acquired
        points, and it is zero padded.
        Then check that the footer is present. The footer is a double line-carriage \n\n
        :param message: raw bytes received from the scope """
        message_header = bytes(message[0:self._header_size]).decode("ascii")
        # Sanity check on header and footer
        if message_header[0:7] != "DAT2,#9":
            raise ValueError(f"Waveform data in invalid : header is {message_header}")
        message_footer = bytes(message[-self._footer_size:]).decode("ascii")
        if message_footer != "\n\n":
            raise ValueError(f"Waveform data in invalid : footer is {message_footer}")

    def _npoints_sanity_checks(self, message):
        """Check that the number of transmitted points is consistent with the message length.
        :param message: raw bytes received from the scope """
        message_header = bytes(message[0:self._header_size]).decode("ascii")
        transmitted_points = int(message_header[-9:])
        received_points = len(message) - self._header_size - self._footer_size
        if transmitted_points != received_points:
            raise ValueError(f"Number of transmitted points ({transmitted_points}) != "
                             f"number of received points ({received_points})")

    def _acquire_data(self, requested_points=0, sparsing=1):
        """Acquire raw data points from the scope. The header, footer and number of points are
        sanity-checked, but they are not processed otherwise. For a description of the input
        arguments refer to the download_waveform method.
        If the number of expected points is big enough, the transmission is split in smaller
        chunks of 20k points and read one chunk at a time. I do not know the reason why,
        but if the chunk size is big enough the transmission does not complete successfully.
        :return: raw data points as numpy array and waveform preamble
        """
        # Setup waveform acquisition parameters
        self.waveform_sparsing = sparsing
        self.waveform_points = requested_points
        self.waveform_first_point = 0

        # Calculate how many points are to be expected
        sample_points = self.acquisition_sample_size(self.waveform_source)
        if requested_points > 0:
            expected_points = min(requested_points, int(sample_points / sparsing))
        else:
            expected_points = int(sample_points / sparsing)

        # If the number of points is big enough, split the data in small chunks and read it one
        # chunk at a time. For less than a certain amount of points we do not bother splitting them.
        chunk_bytes = 20000
        chunk_points = chunk_bytes - self._header_size - self._footer_size
        iterations = -(expected_points // -chunk_points)
        i = 0
        data = []
        while i < iterations:
            # number of points already read
            read_points = i * chunk_points
            # number of points still to read
            remaining_points = expected_points - read_points
            # number of points requested in a single chunk
            requested_points = chunk_points if remaining_points > chunk_points else remaining_points
            self.waveform_points = requested_points
            # number of bytes requested in a single chunk
            requested_bytes = requested_points + self._header_size + self._footer_size
            # read the next chunk starting from this points
            first_point = read_points * sparsing
            self.waveform_first_point = first_point
            # read chunk of points
            values = self._digitize(src=self.waveform_source, num_bytes=requested_bytes)
            # perform many sanity checks on the received data
            self._header_footer_sanity_checks(values)
            self._npoints_sanity_checks(values)
            # append the points without the header and footer
            data.append(values[self._header_size:-self._footer_size])
            i += 1
        data = np.concatenate(data)
        preamble = self.waveform_preamble
        return data, preamble

    #################
    # Download data #
    #################

    def download_image(self):
        """Get a BMP image of oscilloscope screen in bytearray of specified file format.
        """
        # Using binary_values query because default interface does not support binary transfer
        with _ChunkResizer(self.adapter, 20 * 1024 * 1024):
            img = self.binary_values("SCDP", dtype=np.uint8)
        return bytearray(img)

    def _process_data(self, ydata, preamble):
        """Apply scale and offset to the data points acquired from the scope.
        - Y axis : the scale is ydiv / 25 and the offset -yoffset. the
        offset is not applied for the MATH source.
        - X axis : the scale is sparsing / sampling_rate and the offset is -xdiv * 7. The
        7 = 14 / 2 factor comes from the fact that there are 14 vertical grid lines and the data
        starts from the left half of the screen.

        :return: tuple of (numpy array of Y points, numpy array of X points, waveform preamble) """

        def _scale_data(y):
            if preamble["source"] == "MATH":
                value = int.from_bytes([y], byteorder='big', signed=False) * preamble["ydiv"] / 25.
                value -= preamble["ydiv"] * (preamble["yoffset"] + 255) / 50.
            else:
                value = int.from_bytes([y], byteorder='big', signed=True) * preamble["ydiv"] / 25.
                value -= preamble["yoffset"]
            return value

        def _scale_time(x):
            return float(Decimal(-preamble["xdiv"] * self._grid_number / 2.) +
                         Decimal(float(x * preamble["sparsing"])) /
                         Decimal(preamble["sampling_rate"]))

        data_points = np.vectorize(_scale_data)(ydata)
        time_points = np.vectorize(_scale_time)(np.arange(len(data_points)))
        return data_points, time_points, preamble

    def download_waveform(self, source, requested_points=None, sparsing=None):
        """Get data points from the specified source of the oscilloscope.

        The returned objects are two np.ndarray of data and time points and a dict with the
        waveform preamble, that contains metadata about the waveform.

        :param source: measurement source. It can be "C1", "C2", "C3", "C4", "MATH".
        :param requested_points: number of points to acquire. If None the number of points
               requested in the previous call will be assumed, i.e. the value of the number of
               points stored in the oscilloscope memory. If 0 the maximum number of points will
               be returned.
        :param sparsing: interval between data points. For example if sparsing = 4, only one
               point every 4 points is read. If 0 or None the sparsing of the previous call is
               assumed, i.e. the value of the sparsing stored in the oscilloscope memory.
        :return: data_ndarray, time_ndarray, waveform_preamble_dict: see waveform_preamble
                 property for dict format.
        """
        # Sanitize the input arguments
        if not sparsing:
            sparsing = self.waveform_sparsing
        if requested_points is None:
            requested_points = self.waveform_points
        self.waveform_source = sanitize_source(source)
        # Acquire the Y data and the preable
        ydata, preamble = self._acquire_data(requested_points, sparsing)
        # Update the preamble with info about actually acquired data
        preamble["transmitted_points"] = len(ydata)
        preamble["requested_points"] = requested_points
        preamble["sparsing"] = sparsing
        preamble["first_point"] = 0
        # Scale the Y-data and create the X-data
        return self._process_data(ydata, preamble)

    ###############
    #   Trigger   #
    ###############

    trigger_mode = Instrument.control(
        "TRMD?", "TRMD %s",
        """Control the trigger sweep mode (string).

        <mode>:= {AUTO,NORM,SINGLE,STOP}

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
        - single : When SINGLE sweep mode is selected, the backlight of SINGLE key lights up,
          the oscilloscope enters the waiting trigger state and begins to search for the
          trigger signal that meets the conditions.
          If the trigger signal is satisfied, the running state shows Trig'd, and the interface
          shows stable waveform.
          Then, the oscilloscope stops scanning, the RUN/STOP key is red light,
          and the running status shows Stop.
          Otherwise, the running state shows Ready, and the interface does not display the waveform.
        - stopped : STOP is a part of the option of this command, but not a trigger mode of the
          oscilloscope.
        """,
        validator=strict_discrete_set,
        values={"stopped": "STOP", "normal": "NORM", "single": "SINGLE", "auto": "AUTO"},
        map_values=True
    )

    _trigger_select_vals = {
        "EDGE": [["C1", "C2", "C3", "C4", "LINE"], ["TI", "OFF"], [80e-9, 1.5]],
        "DROP": [["C1", "C2", "C3", "C4"], ["TI"], [2e-9, 4.2]],
        "GLIT": [["C1", "C2", "C3", "C4"], ["PS", "PL", "P2", "P1"], [2e-9, 4.2], [2e-9, 4.2]],
        "RUNT": [["C1", "C2", "C3", "C4"], ["PS", "PL", "P2", "P1"], [2e-9, 4.2]],
        "SLEW": [["C1", "C2", "C3", "C4"], ["IS", "IL", "I2", "I1"], [2e-9, 4.2]],
        "INTV": [["C1", "C2", "C3", "C4"], ["IS", "IL", "I2", "I1"], [2e-9, 4.2]]
    }

    _trigger_select_short_command = "TRSE %s,SR,%s,HT,%s"
    _trigger_select_normal_command = "TRSE %s,SR,%s,HT,%s,HV,%.2E"
    _trigger_select_extended_command = "TRSE %s,SR,%s,HT,%s,HV,%.2E,HV2,%.2E"

    _trigger_select = Instrument.control(
        "TRSE?", _trigger_select_normal_command,
        """Control the trigger, see :meth:`~trigger_select()` documentation.""",
        get_process=_trigger_select_get_process,
        validator=_trigger_select_validator,
        values=_trigger_select_vals,
        dynamic=True
    )

    def center_trigger(self):
        """Set the trigger levels to center of the trigger source waveform."""
        self.write("SET50")

    @property
    def trigger_select(self):
        """Control the condition that will trigger the acquisition of waveforms (string).

        Depending on the trigger type, additional parameters must be specified. These additional
        parameters are grouped in pairs. The first in the pair names the variable to be modified,
        while the second gives the new value to be assigned. Pairs may be given in any order and
        restricted to those variables to be changed.

        There are five parameters that can be specified. Parameters 1. 2. 3. are always mandatory.
        Parameters 4. 5. are required only for certain combinations of the previous parameters.

        1. <trig_type>:={edge, slew, glit, intv, runt, drop}
        2. <source>:={c1, c2, c3, c4, line}
        3. <hold_type>:=

           * {ti, off} for edge trigger.
           * {ti} for drop trigger.
           * {ps, pl, p2, p1} for glit/runt trigger.
           * {is, il, i2, i1} for slew/intv trigger.

        4. <hold_value1>:= a time value with unit.
        5. <hold_value2>:= a time value with unit.

        Note:

        - "line" can only be selected when the trigger type is "edge".
        - All time arguments should be given in multiples of seconds. Use the scientific notation
          if necessary.
        - The range of hold_values varies from trigger types. [80nS, 1.5S] for "edge" trigger,
          and [2nS, 4.2S] for others.
        - The trigger_select command is switched automatically between the short, normal and
          extended version depending on the number of expected parameters.
        """
        return self._trigger_select

    # noinspection PyAttributeOutsideInit
    @trigger_select.setter
    def trigger_select(self, value):
        num_expected_pars = _trigger_select_num_pars(value)
        if num_expected_pars == 3:
            self._trigger_select_set_command = self._trigger_select_short_command
        elif num_expected_pars == 4:
            self._trigger_select_set_command = self._trigger_select_normal_command
        elif num_expected_pars == 5:
            self._trigger_select_set_command = self._trigger_select_extended_command
        self._trigger_select = value

    def trigger_setup(self, mode=None, source=None, trigger_type=None, hold_type=None,
                      hold_value1=None, hold_value2=None, coupling=None, level=None, level2=None,
                      slope=None):
        """Set up trigger.

        Unspecified parameters are not modified. Modifying a single parameter
        might impact other parameters. Refer to oscilloscope documentation and make multiple
        consecutive calls to trigger_setup and channel_setup if needed.

        :param mode: trigger sweep mode [auto, normal, single, stop]
        :param source: trigger source [c1, c2, c3, c4, line]
        :param trigger_type: condition that will trigger the acquisition of waveforms
               [edge,slew,glit,intv,runt,drop]
        :param hold_type: hold type (refer to page 172 of programing guide)
        :param hold_value1: hold value1 (refer to page 172 of programing guide)
        :param hold_value2: hold value2 (refer to page 172 of programing guide)
        :param coupling: input coupling for the selected trigger sources
        :param level: trigger level voltage for the active trigger source
        :param level2: trigger lower level voltage for the active trigger source (only slew/runt
               trigger)
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
            source = sanitize_source(source)
            strict_discrete_set(source, ["C1", "C2", "C3", "C4", "LINE"])
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
        """Get trigger setup as a dict containing the following keys:

        - "mode": trigger sweep mode [auto, normal, single, stop]
        - "trigger_type": condition that will trigger the acquisition of waveforms [edge,
          slew,glit,intv,runt,drop]
        - "source": trigger source [c1,c2,c3,c4]
        - "hold_type": hold type (refer to page 172 of programing guide)
        - "hold_value1": hold value1 (refer to page 172 of programing guide)
        - "hold_value2": hold value2 (refer to page 172 of programing guide)
        - "coupling": input coupling for the selected trigger sources
        - "level": trigger level voltage for the active trigger source
        - "level2": trigger lower level voltage for the active trigger source (only slew/runt
          trigger)
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
        return tb_setup

    ###############
    #    Math     #
    ###############

    ###############
    #   Measure   #
    ###############

    def display_parameter(self, parameter, channel):
        """Same as the display_parameter method in the Channel subclass."""
        self.ch(channel).display_parameter = parameter

    def measure_parameter(self, parameter, channel):
        """
        Same as the measure_parameter method in the Channel subclass
        """
        # noinspection PyArgumentList
        return self.ch(channel).measure_parameter(parameter)

    ###############
    #   Display   #
    ###############

    intensity = Instrument.control(
        "INTS?", "INTS GRID,%d,TRACE,%d",
        """Set the intensity level of the grid or the trace in percent """,
        validator=_intensity_validator,
        values=[[0, 100], [0, 100]],
        get_process=lambda v: {v[0]: v[1], v[2]: v[3]}
    )
