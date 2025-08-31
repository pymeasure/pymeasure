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

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.channel import Channel
from pymeasure.instruments.validators import strict_range, strict_discrete_set


def float_to_nr3(input: float):
    """ Convert float to IEEE 488.2 NR3 format
        :param input: floating point number
    """
    return "{:.5E}".format(input)


class OscilloscopeChannel(Channel):
    """ Implementation of a Hewlett Packard HP54616B channel.

    Implementation modeled on Channel object of Keysight DSOX1102G Oscilloscope channel
    which was originally modelled on Tektronix AFG3152C instrument. """

    def __init__(self, instrument, number):
        super().__init__(instrument, number)
        self.instrument = instrument
        self.number = number

    ######################
    # Channel Properties #
    ######################

    bwlimit_enabled = Instrument.control(
        get_command=":CHAN{ch}:BW?",
        set_command=":CHAN{ch}:BW %s",
        docs="""Control whether the channel bandwidth limit is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True
    )

    coupling = Instrument.control(
        get_command=":CHAN{ch}:COUP?",
        set_command=":CHAN{ch}:COUP %s",
        docs="""Control channel coupling to "ac", "dc", or "gnd".""",
        validator=strict_discrete_set,
        values={"ac": "AC", "dc": "DC", "gnd": "GND"},
        map_values=True
    )

    input_impedance = Instrument.control(
        get_command=":CHAN{ch}:INP?",
        set_command=":CHAN{ch}:INP %s",
        docs="""Control input impedance to either "50" or "1M" Ohm""",
        validator=strict_discrete_set,
        values={"50": "FIFT", "1M": "ONEM"},
        map_values=True
    )

    invert_enabled = Instrument.control(
        get_command=":CHAN{ch}:INV?",
        set_command=":CHAN{ch}:INV %s",
        docs="""Control whether the input signal is inverted (bool).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True
    )

    offset = Instrument.control(
        get_command=":CHAN{ch}:OFFS?",
        set_command=":CHAN{ch}:OFFS %s",
        docs="""Control the offset in volts.""",
        set_process=float_to_nr3
    )

    probe_auto_mode_enabled = Instrument.control(
        get_command=":CHAN{ch}:PMOD?",
        set_command=":CHAN{ch}:PMOD %s",
        docs="""Control whether the probe mode is auto (True) or manual (False).""",
        validator=strict_discrete_set,
        values={True: "AUT", False: "MAN"},
        map_values=True
    )

    probe_attenuation = Instrument.control(
        get_command=":CHAN{ch}:PROB?",
        set_command=":CHAN{ch}:PROB %s",
        docs="""Control the probe attenuation. Acceptable values are "x1", "x10" and "x100".""",
        validator=strict_discrete_set,
        values={"x1": "X1", "x10": "X10", "x100": "X100"},
        map_values=True
    )

    protect_enabled = Instrument.control(
        get_command=":CHAN{ch}:PROT?",
        set_command=":CHAN{ch}:PROT %s",
        docs="""Control whether the input protection is enabled in 50Ω mode (bool). If enabled,
            the 50Ω load will disconnect if greater than 5 Vrms is detected.""",
        validator=strict_discrete_set,
        values={False: "OFF", True: "ON"},
        map_values=True
    )

    vertical_range = Instrument.control(
        get_command=":CHAN{ch}:RANG?",
        set_command=":CHAN{ch}:RANG %s",
        docs="""Control the the voltage range (float).""",
        set_process=float_to_nr3
    )

    setup_summary = Instrument.control(
        get_command=":CHAN{ch}:SET?",
        set_command=None,
        docs="""Get the channel setup.""",
    )

    vernier_enabled = Instrument.control(
        get_command=":CHAN{ch}:VERN?",
        set_command=":CHAN{ch}:VERN %s",
        docs="""Control whether the vernier option is enabled (bool).""",
        validator=strict_discrete_set,
        values={False: "OFF", True: "ON"},
        map_values=True
    )

    @property
    def current_configuration(self):
        """ Read channel configuration as a dict containing the following keys:
            - "CHAN": channel number (int)
            - "RANGE": vertical range (float)
            - "OFFSET": vertical offset (float)
            - "COUP": "dc" or "ac" coupling (str)
            - "BWLIMIT": bandwidth limiting enabled (bool)
            - "INVERT": inverted (bool)
            - "VERNIER": vernier "on" or "off" (bool)
            - "PROBE": probe attenuation (str)
            - "PMODE": prove mode "auto" or "manual" (str)
            - "INPUT": input impedance FIFT or ONEM (str)
            - "PROTECT": protect channel "on" or "off" (bool)
        """

        ch_setup_raw = self.setup_summary

        # ch_setup_raw has the following format:
        # CHAN1:RANGE +1.60000000E-001;OFFSET -1.31250000E-002;COUP DC;BWLIMIT OFF;
        # INVERT OFF;VERNIER OFF;PROBE X1;PMODE AUT;INPUT ONEM;PROTECT ON

        # Cut out the "CHANx:" at beginning and split string
        ch_setup_splitted = ch_setup_raw[6:].split(";")

        # Create dict of setup parameters
        ch_setup_dict = dict(map(lambda v: v.split(" "), ch_setup_splitted))

        # Add "CHAN" key
        ch_setup_dict["CHAN"] = ch_setup_raw[4]

        # Convert values to specific type
        to_str = ["COUP", "PROBE", "PMODE", "INPUT"]
        to_bool = ["BWLIMIT", "INVERT", "VERNIER", "PROTECT"]
        to_float = ["RANGE", "OFFSET"]
        to_int = ["CHAN"]
        for key in ch_setup_dict:
            if key in to_str:
                ch_setup_dict[key] = str(ch_setup_dict[key])
            elif key in to_bool:
                if (ch_setup_dict[key] == "ON"):
                    ch_setup_dict[key] = True
                elif (ch_setup_dict[key] == "OFF"):
                    ch_setup_dict[key] = False
                else:
                    raise Exception("Boolean should be either \"ON\" or \"OFF\". "
                                    "Setup value is neither.")
            elif key in to_float:
                ch_setup_dict[key] = float(ch_setup_dict[key])
            elif key in to_int:
                ch_setup_dict[key] = int(ch_setup_dict[key])
        return ch_setup_dict

    def setup(self, bwlimit_enabled=None, coupling=None, input_impedance=None,
              invert_enabled=None, offset=None, probe_auto_mode_enabled=None,
              probe_attenuation=None, vertical_range=None, vernier_enabled=None):
        """ Setup channel. Unspecified settings are not modified. Modifying values such as
        probe attenuation will modify offset, range, etc. Refer to oscilloscope documentation.

        :param bwlimit_enabled: A boolean, which enables 25 MHz internal low-pass filter.
        :param coupling: "ac" or "dc".
        :param input_impedance: A boolean, changes input impedance.
        :param invert_enabled: A boolean, which enables input signal inversion.
        :param offset: Numerical value represented at center of screen.
        :param probe_auto_mode_enabled: Sets the probe mode to "auto" or "manual".
        :param probe_attenuation: Sets the probe attenuation to "x1", "x10", "x100".
        :param vertical_range: Full-scale vertical axis of the selected channel.
        :param vernier_enabled: Control the enable vernier option. """

        if bwlimit_enabled is not None:
            self.bwlimit_enabled = bwlimit_enabled
        if coupling is not None:
            self.coupling = coupling
        if input_impedance is not None:
            self.input_impedance = input_impedance
        if invert_enabled is not None:
            self.invert_enabled = invert_enabled
        if offset is not None:
            self.offset = offset
        if probe_auto_mode_enabled is not None:
            self.probe_auto_mode_enabled = probe_auto_mode_enabled
        if probe_attenuation is not None:
            self.probe_attenuation = probe_attenuation
        if vertical_range is not None:
            self.vertical_range = vertical_range
        if vernier_enabled is not None:
            self.vernier_enabled = vernier_enabled


class HP54616B(SCPIMixin, Instrument):
    """ Represents the Hewlett Packard HP54616B Oscilloscope
    and provides a high-level for interacting with the instrument.
    """

    channel_1 = Instrument.ChannelCreator(OscilloscopeChannel, 1)
    channel_2 = Instrument.ChannelCreator(OscilloscopeChannel, 2)

    def __init__(self, adapter, name="Hewlett Packard HP 54616B Oscilloscope", **kwargs):
        super().__init__(adapter, name, timeout=6000, **kwargs)

    ###############
    # Root Level #
    ###############

    dither = Instrument.control(
        get_command=":DITH?",
        set_command=":DITH %s",
        docs="""Control whether the dither option is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
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

    def run(self):
        """Run oscilloscope."""
        self.write(":RUN")

    def stop(self):
        """Stop oscilloscope."""
        self.write(":STOP")

    def get_waveform_data(self, **kwargs):
        """Command to read waveform data after digitization."""
        self.write(":WAV:DATA?")
        read_data = self.read(**kwargs)
        return read_data

    def get_display_pixel(self, x, y, **kwargs):
        """Get pixel displayed at (x,y) coordinate location.
        :param int x: x-coordinate
        :param int y: y-coordinate
        """
        message = f":DISP:PIX? {x},{y}"
        self.write(message)
        read_data = self.read(**kwargs)
        return read_data

    def set_display_pixel(self, x, y, intensity, **kwargs):
        """Set pixel displayed at (x,y) coordinate location.
        :param int x: x-coordinate
        :param int y: y-coordinate
        :param int intensity: 0 to clear pixel, 1 for half-bright, 2 for full-bright,
            other value to clear pixel
        """
        message = f":DISP:PIX {x},{y},{intensity}"
        if not (0 <= x <= 511):
            raise Exception(f"x pixel value is {x} which is outside expected range [0,511]")
        if not (0 <= y <= 303):
            raise Exception(f"y pixel value is {y} which is outside expected range [0,303]")
        self.write(message, **kwargs)

    def erase_pixel_memory(self, pmem_index, **kwargs):
        message = f":ERAS PMEM{pmem_index}"
        self.write(message, **kwargs)

    ###############
    # Acquire #
    ###############

    # The :ACQUIRE:COMPLETE command specifies the completion criteria for an acquisition.
    # The parameter determines what percentage of the time buckets need to be "full"
    # before an acquisition is considered complete.
    # If you are in the NORMAL mode the instrument only needs one data bit per time bucket
    # for that time bucket to be considered full.
    # In order for the time bucket to be considered full in the AVERAGE or ENVELOPE modes
    # a specified number of data points (COUNT) must be acquired.
    # The range for the COMPLETE command is 0 to 100 and indicates the percentage of time buckets
    # that must be "full" before the acquisition is considered complete.
    # If the complete value is set to 100%, all time buckets must contain
    # data for the acquisition to be considered complete.
    # If the complete value is set to 0 then one acquisition cycle will take place.
    # The COMPLETE query returns the completion criteria for the currently selected mode.
    acquire_complete = Instrument.control(
        get_command=":ACQ:COMP?",
        set_command=":ACQ:COMP %d",
        docs="""Control the percentage of time buckets to be full before acquisition
            is considered complete. Set integer in range [1,100]. """,
        validator=strict_range,
        values=[0, 100],
        map_values=False,
    )

    acquire_count = Instrument.control(
        get_command=":ACQ:COUN?",
        set_command=":ACQ:COUN %d",
        docs="""Control number of averaged values when acquire type is average.""",
        validator=strict_range,
        values=[1, 256],
        map_values=False,
    )

    acquire_points = Instrument.control(
        get_command=":ACQ:POIN?",
        set_command=None,
        docs="""Get number of time buckets. Time buckets groups a set of high-speed samples
            into a bucket, which represents a fixed time window on the time axis.""",
        validator=strict_range,
        values=[1, 4000],
        map_values=False,
    )

    acquire_setup = Instrument.control(
        get_command=":ACQ:SET?",
        set_command=None,
        docs="""Get acquire setup.""",
    )

    acquire_type = Instrument.control(
        get_command=":ACQ:TYPE?",
        set_command=":ACQ:TYPE %s",
        docs="""Control acquire type which are NORMal, AVERage and PEAK.""",
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
        docs="""Control math channel setup. Options are "off", "plus", "subtract".""",
        validator=strict_discrete_set,
        values={"off": "OFF", "plus": "PLUS", "subtract": "SUBT"},
        map_values=True
    )

    channel2_skew = Instrument.control(
        get_command=":CHAN2:SKEW?",
        set_command=":CHAN2:SKEW %s",
        docs="""Control channel 2 skew.""",
        set_process=float_to_nr3
    )

    ###############
    # Display #
    ###############

    display_column = Instrument.control(
        get_command=":DISP:COL?",
        set_command=":DISP:COL %u",
        docs="""Control display column.""",
        validator=strict_range,
        values=[0, 63],
        map_values=False,
    )

    display_connect = Instrument.control(
        get_command=":DISP:CONN?",
        set_command=":DISP:CONN %s",
        docs="""Control display connect.""",
        validator=strict_range,
        values={"on": "ON", "off": "OFF"},
        map_values=True,
    )

    display_grid = Instrument.control(
        get_command=":DISP:GRID?",
        set_command=":DISP:GRID %s",
        docs="""Control display grid.""",
        validator=strict_discrete_set,
        values={"on": "ON", "off": "OFF", "simple": "SIMP", "tv": "TV"},
        map_values=True,
    )

    display_invert_enabled = Instrument.control(
        get_command=":DISP:INV?",
        set_command=":DISP:INV %s",
        docs="""Control whether to invert display (bool).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    display_line = Instrument.control(
        get_command=None,
        set_command=":DISP:LINE %s",
        docs="""Set display line.""",
    )

    display_palette = Instrument.control(
        get_command=":DISP:PAL?",
        set_command=":DISP:PAL %u",
        docs="""Control palette of display.""",
        validator=strict_range,
        values=[0, 6],
        map_values=False,
    )

    # Only 1 value can be set at a time so a string
    # will have to be passed in format <x>, <y>, <intensity>
    display_pixel = Instrument.control(
        get_command=None,
        set_command=":DISP:PIX %s",
        docs="""Control pixel on display.""",
    )

    display_row = Instrument.control(
        get_command=":DISP:ROW?",
        set_command=":DISP:ROW %u",
        docs="""Control row of display.""",
        validator=strict_range,
        values=[1, 20],
        map_values=False,
    )

    display_setup = Instrument.control(
        get_command=":DISP:SET?",
        set_command=None,
        docs="""Get display setup.""",
    )

    display_source = Instrument.control(
        get_command=":DISP:SOUR?",
        set_command=":DISP:SOUR %s",
        docs="""Control display source.""",
        validator=strict_discrete_set,
        values={"pmemory1": "PMEM1", "pmemory2": "PMEM2"},
        map_values=True,
    )

    ###############
    # Waveform #
    ###############

    waveform_byteorder = Instrument.control(
        get_command=":WAV:BYT?",
        set_command=":WAV:BYT %s",
        docs="""Control waveform byteorder. Options are "lsbfirst" and "msbfirst".""",
        validator=strict_discrete_set,
        values={"lsbfirst": "LSBF", "msbfirst": "MSBF"},
        map_values=True,
    )

    waveform_format = Instrument.control(
        get_command=":WAV:FORM?",
        set_command=":WAV:FORM %s",
        docs="""Control waveform format. Options are "ascii", "word" and "byte".""",
        validator=strict_discrete_set,
        values={"ascii": "ASC", "word": "WORD", "byte": "BYTE"},
        map_values=True,
    )

    waveform_points = Instrument.control(
        get_command=":WAV:POIN?",
        set_command=":WAV:POIN %s",
        docs="""Control number of waveform points.
            Options are 100, 200, 250, 400, 500, 800, 1000, 2000, 4000, 5000.""",
        validator=strict_discrete_set,
        values={
            100: 100,
            200: 200,
            250: 250,
            400: 400,
            500: 500,
            800: 800,
            1000: 1000,
            2000: 2000,
            4000: 4000,
            5000: 5000
        },
        map_values=True,
    )

    waveform_preamble = Instrument.control(
        get_command=":WAV:PRE?",
        set_command=None,
        docs="""Get waveform preamble.""",
    )

    waveform_source = Instrument.control(
        get_command=":WAV:SOUR?",
        set_command=":WAV:SOUR CHAN%s",
        docs="""Control waveform source channel. Options are 1 and 2.""",
        validator=strict_range,
        values=[1, 2],
        map_values=False,
    )

    waveform_type = Instrument.control(
        get_command=":WAV:TYPE?",
        set_command=None,
        docs="""Get waveform type. Options are {NORMal | PEAK | AVERage}.""",
    )

    waveform_x_increment = Instrument.control(
        get_command=":WAV:XINC?",
        set_command=None,
        docs="""Get waveform x increment.""",
    )

    waveform_x_origin = Instrument.control(
        get_command=":WAV:XOR?",
        set_command=None,
        docs="""Get waveform x origin.""",
    )

    waveform_x_reference = Instrument.control(
        get_command=":WAV:XREF?",
        set_command=None,
        docs="""Get waveform x reference.""",
    )

    waveform_y_increment = Instrument.control(
        get_command=":WAV:YINC?",
        set_command=None,
        docs="""Get waveform y increment.""",
    )

    waveform_y_origin = Instrument.control(
        get_command=":WAV:YOR?",
        set_command=None,
        docs="""Get waveform y origin.""",
    )

    waveform_y_reference = Instrument.control(
        get_command=":WAV:YREF?",
        set_command=None,
        docs="""Get waveform y reference.""",
    )

    ###############
    # Timebase #
    ###############

    timebase_delay = Instrument.control(
        get_command=":TIM:DEL?",
        set_command=":TIM:DEL %s",
        docs="""Control timebase delay in seconds (float).""",
        set_process=float_to_nr3
    )

    timebase_mode = Instrument.control(
        get_command=":TIM:MODE?",
        set_command=":TIM:MODE %s",
        docs="""Control timebase mode. Options are "normal", "delayed", "xy" and "roll".""",
        validator=strict_discrete_set,
        values={"normal": "NORM", "delayed": "DEL", "xy": "XY", "roll": "ROLL"},
        map_values=True,
    )

    timebase_range = Instrument.control(
        get_command=":TIM:RANG?",
        set_command=":TIM:RANG %s",
        docs="""Control timebase range in seconds (float).""",
        set_process=float_to_nr3
    )

    timebase_reference = Instrument.control(
        get_command=":TIM:REF?",
        set_command=":TIM:REF %s",
        docs="""Control timebase reference. Options are {left | center | right}.""",
        validator=strict_discrete_set,
        values={"left": "LEFT", "center": "CENT", "right": "RIGH"},
        map_values=True,
    )

    timebase_setup = Instrument.control(
        get_command=":TIM:SET?",
        set_command=None,
        docs="""Get timebase setup.""",
    )

    timebase_vernier_enabled = Instrument.control(
        get_command=":TIM:VERN?",
        set_command=":TIM:VERN %s",
        docs="""Control whether timebase vernier is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    ###############
    # Measure #
    ###############

    measure_all = Instrument.control(
        get_command=":MEAS:ALL?",
        set_command=None,
        docs="""Measure all results.""",
    )

    measure_define_delay = Instrument.control(
        get_command=":MEAS:DEF? DEL",
        set_command=":MEAS:DEF DEL %s",
        docs="""Set edge numbers to use for delay measurement in the format <edge1>,<edge2>.""",
    )

    measure_delay = Instrument.control(
        get_command=":MEAS:DEL?",
        set_command=":MEAS:DEL",
        docs="""Measure edge to edge delay in seconds (float).""",
    )

    measure_dutycycle = Instrument.control(
        get_command=":MEAS:DUTY?",
        set_command=":MEAS:DUTY",
        docs="""Measure dutycycle. Returns ratio of positive pulse with to period (float).""",
    )

    measure_falltime = Instrument.control(
        get_command=":MEAS:FALL?",
        set_command=":MEAS:FALL",
        docs="""Measure 90-10 fall time in seconds (float).""",
    )

    measure_frequency = Instrument.control(
        get_command=":MEAS:FREQ?",
        set_command=":MEAS:FREQ",
        docs="""Measure frequency in Hertz (float).""",
    )

    measure_lower = Instrument.control(
        get_command=":MEAS:LOW?",
        set_command=":MEAS:LOW %s",
        docs="""Set lower voltage threshold (float).""",
    )

    measure_nwidth = Instrument.control(
        get_command=":MEAS:NWID?",
        set_command=":MEAS:NWID",
        docs="""Measure negative pulse width in seconds (float).""",
    )

    measure_overshoot = Instrument.control(
        get_command=":MEAS:OVER?",
        set_command=":MEAS:OVER",
        docs="""Measure overshoot percentage (float).""",
    )

    measure_preshoot = Instrument.control(
        get_command=":MEAS:PRES?",
        set_command=":MEAS:PRES",
        docs="""Measure preshoot percentage (float).""",
    )

    measure_period = Instrument.control(
        get_command=":MEAS:PER?",
        set_command=":MEAS:PER",
        docs="""Measure period in seconds (float).""",
    )

    measure_phase = Instrument.control(
        get_command=":MEAS:PHAS?",
        set_command=":MEAS:PHAS",
        docs="""Measure phase angle in degrees (float).""",
    )

    measure_pstart = Instrument.control(
        get_command=":MEAS:PSTA?",
        set_command=":MEAS:PSTA",
        docs="""Measure relative position of time marker 1 in degrees (float).""",
    )

    measure_pstop = Instrument.control(
        get_command=":MEAS:PSTO?",
        set_command=":MEAS:PSTO",
        docs="""Measure relative position of time marker 2 in degrees (float).""",
    )

    measure_pwidth = Instrument.control(
        get_command=":MEAS:PWID?",
        set_command=":MEAS:PWID",
        docs="""Measure positive pulse width in seconds (float).""",
    )

    measure_risetime = Instrument.control(
        get_command=":MEAS:RISE?",
        set_command=":MEAS:RISE",
        docs="""Measure rise time in seconds (float).""",
    )

    measure_scratch = Instrument.control(
        get_command=None,
        set_command=":MEAS:SCR",
        docs="""Set the display to clear the measurement results.""",
    )

    measure_show_enabled = Instrument.control(
        get_command=":MEAS:SHOW?",
        set_command=":MEAS:SHOW %s",
        docs="""Control whether to show measurements.""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    measure_source = Instrument.control(
        get_command=":MEAS:SOUR?",
        set_command=":MEAS:SOUR %u",
        docs="""Control source channel for measurements. Options are 1 and 2.""",
        validator=strict_range,
        values=[1, 2],
        map_values=False,
    )

    measure_thresholds = Instrument.control(
        get_command=":MEAS:THR?",
        set_command=":MEAS:THR %s",
        docs="""Control measurement threshold to 10-90% time (t1090), 20-80% time (t2080)
            and "voltage" between thresholds""",
        validator=strict_discrete_set,
        values={"t1090": "T1090", "t2080": "T2080", "voltage": "VOLT"},
        map_values=True,
    )

    measure_tstart = Instrument.control(
        get_command=":MEAS:TSTA?",
        set_command=":MEAS:TSTA %s",
        docs="""Set time of start marker in seconds (float).""",
    )

    measure_tstop = Instrument.control(
        get_command=":MEAS:TSTO?",
        set_command=":MEAS:TSTO %s",
        docs="""Set time of stop marker in seconds (float).""",
    )

    measure_upper = Instrument.control(
        get_command=":MEAS:UPP?",
        set_command=":MEAS:UPP %s",
        docs="""Set upper voltage threshold (float).""",
    )

    measure_vamplitude = Instrument.control(
        get_command=":MEAS:VAMP?",
        set_command=":MEAS:VAMP",
        docs="""Measure amplitude of selected waveform in volts (float).""",
    )

    measure_vaverage = Instrument.control(
        get_command=":MEAS:VAV?",
        set_command=":MEAS:VAV",
        docs="""Measure average voltage (float).""",
    )

    measure_vbase = Instrument.control(
        get_command=":MEAS:VBAS?",
        set_command=":MEAS:VBAS",
        docs="""Measure voltage at base of selected waveform (float).""",
    )

    measure_vtop = Instrument.control(
        get_command=":MEAS:VTOP?",
        set_command=":MEAS:VTOP",
        docs="""Measure voltage at top of the waveform (float).""",
    )

    measure_vdelta = Instrument.control(
        get_command=":MEAS:VDELta?",
        set_command=None,
        docs="""Measure voltage difference between marker 1 and 2 (float).""",
    )

    measure_vmax = Instrument.control(
        get_command=":MEAS:VMAX?",
        set_command=":MEAS:VMAX",
        docs="""Measure maximum voltage of selected waveform (float).""",
    )

    measure_vmin = Instrument.control(
        get_command=":MEAS:VMIN?",
        set_command=":MEAS:VMIN",
        docs="""Measure minimum voltage of selected waveform (float).""",
    )

    measure_vpp = Instrument.control(
        get_command=":MEAS:VPP?",
        set_command=":MEAS:VPP",
        docs="""Measure peak-to-peak voltage of selected waveform (float).""",
    )

    measure_vpstart = Instrument.control(
        get_command=":MEAS:VPSTA?",
        set_command=":MEAS:VPSTA %s",
        docs="""Set relative position of voltage marker 1 in percent (float).""",
    )

    measure_vpstop = Instrument.control(
        get_command=":MEAS:VPSTO?",
        set_command=":MEAS:VPSTO %s",
        docs="""Set relative position of voltage marker 2 in percent (float).""",
    )

    measure_vstart = Instrument.control(
        get_command=":MEAS:VSTA?",
        set_command=":MEAS:VSTA %s",
        docs="""Set voltage value of voltage marker 1 (float).""",
    )

    measure_vstart = Instrument.control(
        get_command=":MEAS:VSTO?",
        set_command=":MEAS:VSTO %s",
        docs="""Set voltage value of voltage marker 2 (float).""",
    )

    measure_vrms = Instrument.control(
        get_command=":MEAS:VRMS?",
        set_command=":MEAS:VRMS",
        docs="""Measure RMS voltage (float).""",
    )

    measure_vtime = Instrument.control(
        get_command=":MEAS:VTIM %s",
        set_command=None,
        docs="""Measure time from trigger in seconds (float).""",
    )
