#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

from pymeasure.instruments import Instrument
from pymeasure.instruments.teledyne.teledyne_oscilloscope import TeledyneOscilloscope,\
    TeledyneOscilloscopeChannel, sanitize_source
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


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
    output = (sanitize_source(value[0]), value[1], sanitize_source(value[2]))
    for i in range(3):
        strict_discrete_set(output[i], values=values[i])
    return output


def _measure_delay_validator(value, values):
    """
    Validate the input of the measure_delay property
    :param value: input parameters as a 3-element tuple
    :param values: allowed space for each parameter
    """
    if not isinstance(value, tuple):
        raise ValueError('Input value {} of trigger_select should be a tuple'.format(value))
    if len(value) != 3:
        raise ValueError('Number of parameters {} different from 3'.format(len(value)))
    output = (value[0], sanitize_source(value[1]), sanitize_source(value[2]))
    if output[1][0] > output[2][0]:
        raise ValueError(f'First channel number {output[1]} must be <= than second one {output[2]}')
    for i in range(3):
        strict_discrete_set(output[i], values=values[i])
    return output


class LeCroyT3DSO1204Channel(TeledyneOscilloscopeChannel):
    """Implementation of a LeCroy T3DSO1204 Oscilloscope channel.

    Implementation modeled on Channel object of Keysight DSOX1102G instrument.
    """

    TRIGGER_SLOPES = {"negative": "NEG", "positive": "POS", "window": "WINDOW"}

    # Change listed values for existing commands:
    trigger_slope_values = TRIGGER_SLOPES

    bwlimit = Instrument.control(
        "BWL?", "BWL %s",
        """Control the 20 MHz internal low-pass filter (strict bool).

        This oscilloscope only has one frequency available for this filter.
        """,
        validator=strict_discrete_set,
        values=TeledyneOscilloscopeChannel._BOOLS,
        map_values=True
    )

    invert = Instrument.control(
        "INVS?", "INVS %s",
        """Control the inversion of the input signal (strict bool).""",
        validator=strict_discrete_set,
        values=TeledyneOscilloscopeChannel._BOOLS,
        map_values=True
    )

    skew_factor = Instrument.control(
        "SKEW?", "SKEW %.2ES",
        """Control the channel-to-channel skew factor for the specified channel.
        Each analog channel can be adjusted + or -100 ns for a total of 200 ns difference
        between channels. You can use the oscilloscope's skew control to remove cable-delay
        errors between channels.
        """,
        validator=strict_range,
        values=[-1e-7, 1e-7],
        preprocess_reply=lambda v: v.rstrip('S')
    )

    trigger_level2 = Instrument.control(
        "TRLV2?", "TRLV2 %.2EV",
        """Control the lower trigger level voltage for the specified source (float).
        Higher and lower trigger levels are used with runt/slope triggers.
        When setting the trigger level it must be divided by the probe attenuation. This is
        not documented in the datasheet and it is probably a bug of the scope firmware.
        An out-of-range value will be adjusted to the closest legal value.
        """
    )

    unit = Instrument.control(
        "UNIT?", "UNIT %s",
        """Control the unit of the specified trace. Measurement results, channel sensitivity, and
        trigger level will reflect the measurement units you select. ("A" for Amperes, "V" for
        Volts).
        """,
        validator=strict_discrete_set,
        values=["A", "V"]
    )


class LeCroyT3DSO1204(TeledyneOscilloscope):
    """Represents the LeCroy T3DSO1204 Oscilloscope interface for interacting with the instrument.

    Refer to the LeCroy T3DSO1204 Oscilloscope Programmer's Guide for further details about
    using the lower-level methods to interact directly with the scope.

    This implementation is based on the shared base class :class:`TeledyneOscilloscope`.

    Attributes:

        WRITE_INTERVAL_S: minimum time between two commands. If a command is received less than
        WRITE_INTERVAL_S after the previous one, the code blocks until at least WRITE_INTERVAL_S
        seconds have passed.
        Because the oscilloscope takes a non-negligible time to perform some operations, it might
        be needed for the user to tweak the sleep time between commands.
        The WRITE_INTERVAL_S is set to 10ms as default however its optimal value heavily depends
        on the actual commands and on the connection type, so it is impossible to give a unique
        value to fit all cases. An interval between 10ms and 500ms second proved to be good,
        depending on the commands and connection latency.

    .. code-block:: python

        scope = LeCroyT3DSO1204(resource)
        scope.autoscale()
        ch1_data_array, ch1_preamble = scope.download_waveform(source="C1", points=2000)
        # ...
        scope.shutdown()
    """

    _BOOLS = {True: "ON", False: "OFF"}

    WRITE_INTERVAL_S = 0.02  # seconds

    ch_1 = Instrument.ChannelCreator(LeCroyT3DSO1204Channel, 1)

    ch_2 = Instrument.ChannelCreator(LeCroyT3DSO1204Channel, 2)

    ch_3 = Instrument.ChannelCreator(LeCroyT3DSO1204Channel, 3)

    ch_4 = Instrument.ChannelCreator(LeCroyT3DSO1204Channel, 4)

    def __init__(self, adapter, name="LeCroy T3DSO1204 Oscilloscope", **kwargs):
        super().__init__(adapter, name, **kwargs)

    ##################
    # Timebase Setup #
    ##################

    timebase_hor_magnify = Instrument.control(
        "HMAG?", "HMAG %.2ES",
        """Control the zoomed (delayed) window horizontal scale (seconds/div).

        The main sweep scale determines the range for this command.
        """,
        validator=strict_range,
        values=[1e-9, 20e-3]
    )

    timebase_hor_position = Instrument.control(
        "HPOS?", "HPOS %.2ES",
        """Control the horizontal position in the zoomed (delayed) view of the main sweep.

        The main sweep range and the main sweep horizontal position determine
        the range for this command. The value for this command must keep the zoomed view window
        within the main sweep range.
        """,
    )

    @property
    def timebase(self):
        """Get timebase setup as a dict containing the following keys:

            - "timebase_scale": horizontal scale in seconds/div (float)
            - "timebase_offset": interval in seconds between the trigger and the reference
              position (float)
            - "timebase_hor_magnify": horizontal scale in the zoomed window in seconds/div (float)
            - "timebase_hor_position": horizontal position in the zoomed window in seconds
              (float)

        """
        tb_setup = {
            "timebase_scale": self.timebase_scale,
            "timebase_offset": self.timebase_offset,
            "timebase_hor_magnify": self.timebase_hor_magnify,
            "timebase_hor_position": self.timebase_hor_position
        }
        return tb_setup

    def timebase_setup(self, scale=None, offset=None, hor_magnify=None, hor_position=None):
        """Set up timebase. Unspecified parameters are not modified. Modifying a single parameter
        might impact other parameters. Refer to oscilloscope documentation and make multiple
        consecutive calls to timebase_setup if needed.

        :param scale: interval in seconds between the trigger event and the reference position.
        :param offset: horizontal scale per division in seconds/div.
        :param hor_magnify: horizontal scale in the zoomed window in seconds/div.
        :param hor_position: horizontal position in the zoomed window in seconds."""

        if scale is not None:
            self.timebase_scale = scale
        if offset is not None:
            self.timebase_offset = offset
        if hor_magnify is not None:
            self.timebase_hor_magnify = hor_magnify
        if hor_position is not None:
            self.timebase_hor_position = hor_position

    ###############
    # Acquisition #
    ###############

    acquisition_type = Instrument.control(
        "ACQW?", "ACQW %s",
        """Control the type of data acquisition.

        Can be 'normal', 'peak', 'average', 'highres'.
        """,
        validator=strict_discrete_set,
        values={"normal": "SAMPLING", "peak": "PEAK_DETECT", "average": "AVERAGE",
                "highres": "HIGH_RES"},
        map_values=True,
        get_process=lambda v: [v[0].lower(), int(v[1])] if len(v) == 2 and v[0] == "AVERAGE" else v
    )

    acquisition_average = Instrument.control(
        "AVGA?", "AVGA %d",
        """Control the averaging times of average acquisition.""",
        validator=strict_discrete_set,
        values=[4, 16, 32, 64, 128, 256, 512, 1024]
    )

    acquisition_status = Instrument.measurement(
        "SAST?", """Get the acquisition status of the scope.""",
        values={"stopped": "Stop", "triggered": "Trig'd", "ready": "Ready", "auto": "Auto",
                "armed": "Arm"},
        map_values=True
    )

    acquisition_sampling_rate = Instrument.measurement(
        "SARA?", """Get the sample rate of the scope."""
    )

    def acquisition_sample_size(self, source):
        """Get acquisition sample size for a certain channel. Used mainly for waveform acquisition.
        If the source is MATH, the SANU? MATH query does not seem to work, so I return the memory
        size instead.

        :param source: channel number of channel name.
        :return: acquisition sample size of that channel.
        """
        if isinstance(source, str):
            source = sanitize_source(source)
        if source in [1, "C1"]:
            return self.acquisition_sample_size_c1
        elif source in [2, "C2"]:
            return self.acquisition_sample_size_c2
        elif source in [3, "C3"]:
            return self.acquisition_sample_size_c3
        elif source in [4, "C4"]:
            return self.acquisition_sample_size_c4
        elif source == "MATH":
            math_define = self.math_define[1]
            match = re.match(r"'(\w+)[+\-/*](\w+)'", math_define)
            return min(self.acquisition_sample_size(match.group(1)),
                       self.acquisition_sample_size(match.group(2)))
        else:
            raise ValueError("Invalid source: must be 1, 2, 3, 4 or C1, C2, C3, C4, MATH.")

    acquisition_sample_size_c1 = Instrument.measurement(
        "SANU? C1", """Get the number of data points that the hardware
        will acquire from the input signal of channel 1.
        Note.
        Channel 2 and channel 1 share the same ADC, so the sample is the same too.
        """
    )

    acquisition_sample_size_c2 = Instrument.measurement(
        "SANU? C1", """Get the number of data points that the hardware
        will acquire from the input signal of channel 2.
        Note.
        Channel 2 and channel 1 share the same ADC, so the sample is the same too.
        """
    )

    acquisition_sample_size_c3 = Instrument.measurement(
        "SANU? C3", """Get the number of data points that the hardware
        will acquire from the input signal of channel 3.
        Note.
        Channel 3 and channel 4 share the same ADC, so the sample is the same too.
        """
    )

    acquisition_sample_size_c4 = Instrument.measurement(
        "SANU? C3", """Get the number of data points that the hardware
        will acquire from the input signal of channel 4.
        Note.
        Channel 3 and channel 4 share the same ADC, so the sample is the same too.
        """
    )

    ##################
    #    Waveform    #
    ##################

    memory_size = Instrument.control(
        "MSIZ?", "MSIZ %s",
        """Control the maximum depth of memory.

        <size>:={7K,70K,700K,7M} for non-interleaved mode. Non-interleaved means a single channel is
        active per A/D converter. Most oscilloscopes feature two channels per A/D converter.

        <size>:={14K,140K,1.4M,14M} for interleave mode. Interleave mode means multiple active
        channels per A/D converter.
        """,
        validator=strict_discrete_set,
        values={7e3: "7K", 7e4: "70K", 7e5: "700K", 7e6: "7M",
                14e3: "14K", 14e4: "140K", 14e5: "1.4M", 14e6: "14M"},
        map_values=True
    )

    @property
    def waveform_preamble(self):
        """Get preamble information for the selected waveform source as a dict with the
        following keys:

        - "type": normal, peak detect, average, high resolution (str)
        - "requested_points": number of data points requested by the user (int)
        - "sampled_points": number of data points sampled by the oscilloscope (int)
        - "transmitted_points": number of data points actually transmitted (optional) (int)
        - "memory_size": size of the oscilloscope internal memory in bytes (int)
        - "sparsing": sparse point. It defines the interval between data points. (int)
        - "first_point": address of the first data point to be sent (int)
        - "source": source of the data : "C1", "C2", "C3", "C4", "MATH".
        - "unit": Physical units of the Y-axis
        - "type":  type of data acquisition. Can be "normal", "peak", "average", "highres"
        - "average": average times of average acquisition
        - "sampling_rate": sampling rate (it is a read-only property)
        - "grid_number": number of horizontal grids (it is a read-only property)
        - "status": acquisition status of the scope. Can be "stopped", "triggered", "ready",
          "auto", "armed"
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
            "type": self.acquisition_type,
            "sampling_rate": self.acquisition_sampling_rate,
            "grid_number": self._grid_number,
            "status": self.acquisition_status,
            "memory_size": self.memory_size,
            "xdiv": self.timebase_scale,
            "xoffset": self.timebase_offset
        }
        preamble["average"] = self.acquisition_average if preamble["type"][0] == "average" else None
        strict_discrete_set(self.waveform_source, ["C1", "C2", "C3", "C4", "MATH"])
        preamble["sampled_points"] = self.acquisition_sample_size(self.waveform_source)
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
            preamble["unit"] = None
        else:
            preamble["ydiv"] = self.ch(self.waveform_source).scale
            preamble["yoffset"] = self.ch(self.waveform_source).offset
            preamble["unit"] = self.ch(self.waveform_source).unit
        return preamble

    ###############
    #    Math     #
    ###############

    math_define = Instrument.control(
        "DEF?", "DEF EQN,'%s%s%s'",
        """Control the desired waveform math operation between two channels.

        Three parameters must be passed as a tuple:

        #. source1 : source channel on the left
        #. operation : operator must be "*", "/", "+", "-"
        #. source2 : source channel on the right

        """,
        validator=_math_define_validator,
        values=[["C1", "C2", "C3", "C4"], ["*", "/", "+", "-"], ["C1", "C2", "C3", "C4"]]
    )

    math_vdiv = Instrument.control(
        "MTVD?", "MTVD %.2EV",
        """Control the vertical scale of the selected math operation.

        This command is only valid in add, subtract, multiply and divide operation.
        Note: legal values for the scale depend on the selected operation.
        """,
        validator=strict_discrete_set,
        values=[5e-4, 1e-3, 2e-3, 5e-3, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100]
    )

    math_vpos = Instrument.control(
        "MTVP?", "MTVP %d",
        """Control the vertical position of the math waveform with specified source.

        Note: the point represents the screen pixels and is related to the screen center. For
        example, if the point is 50. The math waveform will be displayed 1 grid above the vertical
        center of the screen. Namely one grid is 50.
        """,
        validator=strict_range,
        values=[-255, 255]
    )

    ###############
    #   Measure   #
    ###############

    measure_delay = Instrument.control(
        "MEAD?", "MEAD %s,%s-%s",
        """Control measurement delay.

        The MEASURE_DELY command places the instrument in the continuous measurement mode and
        starts a type of delay measurement.
        The MEASURE_DELY? query returns the measured value of delay type.
        The command accepts three arguments with the following syntax:

            measure_delay = (<type>,<sourceA>,<sourceB>)

            <type> := {PHA,FRR,FRF,FFR,FFF,LRR,LRF,LFR,LFF,SKEW}

            <sourceA>,<sourceB> := {C1,C2,C3,C4} where if sourceA=CX and sourceB=CY, then X < Y

        ========= ======================================================================
        Type      Description
        ========= ======================================================================
        PHA       The phase difference between two channels. (rising edge - rising edge)
        FRR       Delay between two channels. (first rising edge - first rising edge)
        FRF       Delay between two channels. (first rising edge - first falling edge)
        FFR       Delay between two channels. (first falling edge - first rising edge)
        FFF       Delay between two channels. (first falling edge - first falling edge)
        LRR       Delay between two channels. (first rising edge - last rising edge)
        LRF       Delay between two channels. (first rising edge - last falling edge)
        LFR       Delay between two channels. (first falling edge - last rising edge)
        LFF       Delay between two channels. (first falling edge - last falling edge)
        Skew      Delay between two channels. (edge – edge of the same type)
        ========= ======================================================================
        """,
        validator=_measure_delay_validator,
        values=[["PHA", "FRR", "FRF", "FFR", "FFF", "LRR", "LRF", "LFR", "LFF", "Skey"],
                ["C1", "C2", "C3", "C4"], ["C1", "C2", "C3", "C4"]]
    )

    ###############
    #   Display   #
    ###############

    menu = Instrument.control(
        "MENU?", "MENU %s",
        """Control the bottom menu enabled state (strict bool).""",
        validator=strict_discrete_set,
        values=TeledyneOscilloscope._BOOLS,
        map_values=True
    )

    grid_display = Instrument.control(
        "GRDS?", "GRDS %s",
        """Control the type of the grid which is used to display (FULL, HALF, OFF).""",
        validator=strict_discrete_set,
        values={"full": "FULL", "half": "HALF", "off": "OFF"},
        map_values=True
    )
