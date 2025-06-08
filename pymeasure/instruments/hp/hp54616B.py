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

from pymeasure.instruments import Instrument, SCPIUnknownMixin
from pymeasure.errors import RangeException
from pymeasure.instruments.validators import strict_range, strict_discrete_set

class Channel():
    """ Implementation of a Keysight DSOX1102G Oscilloscope channel.

    Implementation modeled on Channel object of Tektronix AFG3152C instrument. """

    BOOLS = {True: 1, False: 0}

    ###############
    # Channel #
    ###############

    bwlimit = Instrument.control(
        get_command=":BW?",
        set_command=":BW %s",
        docs="""Channel bandwidth limit""",
        validator=strict_discrete_set,
        values={"on":"ON", "off":"OFF"},
        map_values=True
    )

    coupling = Instrument.control(
        get_command=":COUP?",
        set_command=":COUP %s",
        docs="""Channel coupling""",
        validator=strict_discrete_set,
        values={"ac":"AC", "dc": "DC", "gnd": "GND"},
        map_values=True
    )

    input = Instrument.control(
        get_command=":INP?",
        set_command=":INP %s",
        docs=""" Sets input impedance to either 50 or 1M Ohm.""",
        validator=strict_discrete_set,
        values={"50":"FIFT","1M":"ONEM"},
        map_values=True
    )

    invert = Instrument.control(
        get_command=":INV?",
        set_command=":INV %s",
        docs=""" A boolean parameter that toggles the inversion of the input signal.""",
        validator=strict_discrete_set,
        values={"on":"ON","off":"OFF"},
        map_values=True
    )

    # TODO: Add validator for the NR3 format
    offset = Instrument.control(
        get_command=":OFFS?",
        set_command=":OFFS %s",
        docs="""Offset in volts.""",
    )

    pmode = Instrument.control(
        get_command=":PMOD?",
        set_command=":PMOD %s",
        docs="""Probe mode.""",
        validator=strict_discrete_set,
        values={"auto":"AUT","manual":"MAN"},
        map_values=True
    )

    probe = Instrument.control(
        get_command=":PROB?",
        set_command=":PROB %s",
        docs="""Probe attenuation.""",
        validator=strict_discrete_set,
        values={"x1":"X1","x10":"X10","x100":"X100"},
        map_values=True
    )

    protect = Instrument.control(
        get_command=":PROT?",
        set_command=":PROT %s",
        docs="""Protect.""",
        validator=strict_discrete_set,
        values={"off":"OFF","on":"ON"},
        map_values=True
    )

    # TODO: Add validator for the NR3 format
    range = Instrument.control(
        get_command=":RANG?",
        set_command=":RANG %s",
        docs="""Protect.""",
    )

    setup_summary = Instrument.control(
        get_command=":SET?",
        set_command=None,
        docs="""Channel setup""",
    )

    protect = Instrument.control(
        get_command=":VERN?",
        set_command=":VERN %s",
        docs="""Enable vernier.""",
        validator=strict_discrete_set,
        values={"off":"OFF","on":"ON"},
        map_values=True
    )

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number

    def values(self, command, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values(":CHAN%u:%s" % (
            self.number, command), **kwargs)

    def ask(self, command):
        self.instrument.ask(":CHANl%u:%s" % (self.number, command))

    def write(self, command):
        self.instrument.write(":CHAN%u:%s" % (self.number, command))

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
        ch_setup_raw = self.instrument.ask(":CHAN%d?" % self.number).strip("\n")

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

class HP54616B(SCPIUnknownMixin, Instrument):
    """ Represents the Hewlett Packard HP54616B Oscilloscope
    and provides a high-level for interacting with the instrument
    """

    def __init__(self, adapter, name="Hewlett Packard HP 54616B Oscilloscope", **kwargs):
        super().__init__(adapter,name,timeout=6000,**kwargs)
                # Account for setup time for timebase_mode, waveform_points_mode
        self.ch1 = Channel(self, 1)
        self.ch2 = Channel(self, 2)

    source_mode = Instrument.control(
        get_command=":SOUR:FUNC?",
        set_command=":SOUR:FUNC %s",
        docs=""" Control (string) the source mode, which can
        take the values 'current' or 'voltage'. The convenience methods
        :meth:`~.Keithley2400.apply_current` and :meth:`~.Keithley2400.apply_voltage`
        can also be used. """,
        validator=strict_discrete_set,
        values={"current": "CURR", "voltage": "VOLT"},
        map_values=True,
    )

    source_enabled = Instrument.control(
        "OUTPut?",
        "OUTPut %d",
        """Control whether the source is enabled, takes
        values True or False. The convenience methods :meth:`~.Keithley2400.enable_source` and
        :meth:`~.Keithley2400.disable_source` can also be used.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    ###############
    # Root Level #
    ###############

    dither = Instrument.control(
        get_command=":DITH?",
        set_command=":DITH %s",
        docs="""Apply dither.""",
        validator=strict_discrete_set,
        values={"on":"ON", "off":"OFF"},
        map_values=True,
    )

    ###############
    # Methods #
    ###############

    def autoscale(self):
        """The AUTOSCALE feature performs a very useful function on unknown
            waveforms by setting up the vertical channel, time base, and trigger level of
            the instrument.
        """
        self.write(":AUT")

    def digitize(self, channel):
        """The DIGitize command is a macro that captures data satisfying the
            specifications set up by the ACQuire subsystem. When the digitize process is
            complete, the acquisition is stopped. The captured data can then be
            measured by the instrument or transferred to the controller for further
            analysis.
        :param int channel: Number of bytes to read. A value of -1 indicates to
            read from the whole read buffer.
        """
        self.write(":DIG CHAN%u" % channel)

    def blank(self, channel):
        self.write(":BLAN %u" % channel)

    def stop(self):
        self.write(":STOP")

    ###############
    # Acquire #
    ###############

    acquire_complete = Instrument.control(
        get_command=":ACQ:COMP?",
        set_command=":ACQ:COMP %d",
        docs="""Complete acquire.""",
        validator=strict_range,
        values=[0, 100],
        map_values=False,
    )

    acquire_count = Instrument.control(
        get_command=":ACQ:COUN?",
        set_command=":ACQ:COUNT %d",
        docs="""Acquire average count""",
        validator=strict_range,
        values=[1, 256],
        map_values=False,
    )

    acquire_points = Instrument.control(
        get_command=":ACQ:POIN?",
        set_command=None,
        docs="""Acquire points""",
        validator=strict_range,
        values=[1, 4000],
        map_values=False,
    )

    acquire_setup = Instrument.control(
        get_command=":ACQ:SET?",
        set_command=None,
        docs="""Acquire setup""",
    )

    acquire_type = Instrument.control(
        get_command=":ACQ:TYPE?",
        set_command=":ACQ:TYPE %s",
        docs="""Acquire type""",
        validator=strict_discrete_set,
        values={"normal": "NORM", "average": "AVER", "peak": "PEAK"},
        map_values=True,
    )  

    ###############
    # Channel #
    ###############

    math = Instrument.control(
        get_command=":CHAN:MATH?",
        set_command=":CHAN:MATH %s",
        docs=""" Math channel setup. Options are off, plus, subtract.""",
        validator=strict_discrete_set,
        values={"off":"off","plus":"PLUS","subtract":"SUBT"},
        map_values=True
    ) 

    # TODO: Add validator for the NR3 format
    channel2_skew = Instrument.control(
        get_command=":CHAN2:SKEW?",
        set_command=":CHAN2:SKEW %s",
        docs=""" Channel 2 skew.""",
    ) 

    ###############
    # Display #
    ###############

    display_column = Instrument.control(
        get_command=":DISP:COL?",
        set_command=":DISP:COL %u",
        docs="""Acquire points""",
        validator=strict_range,
        values=[0, 63],
        map_values=False,
    )

    display_connect = Instrument.control(
        get_command=":DISP:CONN?",
        set_command=":DISP:CONN %s",
        docs="""Acquire points""",
        validator=strict_range,
        values={"on":"ON","off":"OFF"},
        map_values=True,
    )

    # TODO test the transmission of binary block data
    display_data = Instrument.control(
        get_command=":DISP:DATA?",
        set_command=":DISP:DATA %s",
        docs="""Display data provided in binary block data""",
    )

    display_grid = Instrument.control(
        get_command=":DISP:GRID?",
        set_command=":DISP:GRID %s",
        docs="""Display grid.""",
        validator=strict_discrete_set,
        values={"on":"ON","off":"OFF","simple":"SIMP","tv":"TV"},
        map_values=True,
    )

    display_inverse = Instrument.control(
        get_command=":DISP:INV?",
        set_command=":DISP:INV %s",
        docs="""Inverse display.""",
        validator=strict_discrete_set,
        values={"on":"ON","off":"OFF"},
        map_values=True,
    )

    display_line = Instrument.control(
        get_command=None,
        set_command=":DISP:LINE %s",
        docs="""Display line""",
    )

    display_palette = Instrument.control(
        get_command=":DISP:PAL?",
        set_command=":DISP:PAL %u",
        docs="""Display palette.""",
        validator=strict_range,
        values=[0,6],
        map_values=False,
    )

    # Only 1 values can be set at a time so a string will have to be passed
    display_pixel = Instrument.control(
        get_command=":DISP:PIX? %s",
        set_command=":DISP:PIX %s",
        docs="""Display pixel""",
    )

    display_row = Instrument.control(
        get_command=":DISP:ROW?",
        set_command=":DISP:ROW %u",
        docs="""Display row.""",
        validator=strict_range,
        values=[1,20],
        map_values=False,
    )

    display_setup = Instrument.control(
        get_command=":DISP:SET?",
        set_command=None,
        docs="""Display setup.""",
    )

    display_source = Instrument.control(
        get_command=":DISP:SOUR?",
        set_command=":DISP:SOUR %s",
        docs="""Display source.""",
        validator=strict_discrete_set,
        values={"pmemory1":"PMEM1","pmemory2":"PMEM2"},
        map_values=True,
    )

    ###############
    # Waveform #
    ###############

    waveform_byteorder = Instrument.control(
        get_command=":WAV:BYT?",
        set_command=":WAV:BYT %s",
        docs="""Waveform byteorder.""",
        validator=strict_discrete_set,
        values={"lsbfirst":"LSBF","msbfirst":"MSBF"},
        map_values=True,
    )

    waveform_data = Instrument.control(
        get_command=":WAV:DATA?",
        set_command=":WAV:DATA %s",
        docs="""Waveform data.""",
    )

    waveform_format = Instrument.control(
        get_command=":WAV:FORM?",
        set_command=":WAV:FORM %s",
        docs="""Waveform format.""",
        validator=strict_discrete_set,
        values={"ascii":"ASC","word":"WORD","byte":"BYTE"},
        map_values=True,
    )

    waveform_points = Instrument.control(
        get_command=":WAV:POIN?",
        set_command=":WAV:POIN %s",
        docs="""Waveform points.""",
        validator=strict_discrete_set,
        values={100:100,200:200,250:250,400:400,500:500,800:800,1000:1000,2000:2000,4000:4000,5000:5000},
        map_values=True,
    )

    waveform_preamble = Instrument.control(
        get_command=":WAV:PRE?",
        set_command=None,
        docs="""Waveform preamble.""",
    )

    waveform_source = Instrument.control(
        get_command=":WAV:SOUR?",
        set_command=":WAV:SOUR %s",
        docs="""Waveform source.""",
        validator=strict_range,
        values=[1,2],
        map_values=False,
    )

    waveform_type = Instrument.control(
        get_command=":WAV:TYPE?",
        set_command=None,
        docs="""Waveform type.""",
    )

    waveform_x_increment = Instrument.control(
        get_command=":WAV:XINC?",
        set_command=None,
        docs="""Waveform x increment.""",
    )

    waveform_x_origin = Instrument.control(
        get_command=":WAV:XOR?",
        set_command=None,
        docs="""Waveform x origin.""",
    )

    waveform_x_reference = Instrument.control(
        get_command=":WAV:XREF?",
        set_command=None,
        docs="""Waveform x reference.""",
    )

    waveform_y_increment = Instrument.control(
        get_command=":WAV:YINC?",
        set_command=None,
        docs="""Waveform y increment.""",
    )

    waveform_y_origin = Instrument.control(
        get_command=":WAV:YOR?",
        set_command=None,
        docs="""Waveform y origin.""",
    )

    waveform_y_reference = Instrument.control(
        get_command=":WAV:YREF?",
        set_command=None,
        docs="""Waveform y reference.""",
    )

    ###############
    # Timebase #
    ###############

    # TODO: Add validator for the NR3 format
    timebase_delay = Instrument.control(
        get_command=":TIM:DEL?",
        set_command=":TIM:DEL %s",
        docs="""Timebase delay""",
    )

    timebase_mode = Instrument.control(
        get_command=":TIM:MODE?",
        set_command=":TIM:MODE %s",
        docs="""Timebase mode.""",
        validator=strict_discrete_set,
        values={"normal":"NORM","delayed":"DEL","xy":"XY","roll":"ROLL"},
        map_values=True,
    )

    # TODO: Add validator for the NR3 format
    timebase_range = Instrument.control(
        get_command=":TIM:RANG?",
        set_command=":TIM:RANG %s",
        docs="""Timebase range.""",
    )

    timebase_reference = Instrument.control(
        get_command=":TIM:REF?",
        set_command=":TIM:REF %s",
        docs="""Timebase reference.""",
        validator=strict_discrete_set,
        values={"left":"LEFT","center":"CENT","right":"RIGH"},
        map_values=True,
    )

    timebase_setup = Instrument.control(
        get_command=":TIM:SET?",
        set_command=None,
        docs="""Timebase setup.""",
    )

    timebase_vernier = Instrument.control(
        get_command=":TIM:VERN?",
        set_command=":TIM:VERN %s",
        docs="""Timebase vernier.""",
        validator=strict_discrete_set,
        values={"on":"ON","off":"OFF"},
        map_values=True,
    )
