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
#

import logging

from enum import Enum

from pymeasure.instruments.validators import strict_discrete_set, strict_range
from pymeasure.instruments import Instrument, Channel

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

try:
    from enum import StrEnum
except ImportError:
    class StrEnum(str, Enum):
        """Until StrEnum is broadly available / pymeasure relies on python <=
        3.10.x."""

        def __str__(self):
            return self.value


class AcquisitionState(StrEnum):
    """Enumeration to represent the different acquisition states"""

    #: Starts the acquisition or indicates that it is running
    Run = "RUN"

    #: Stops the acquisition or indicates the stop of an acquisition
    Stop = "STOP"

    #: Indicates a completed acquisition
    Complete = "COMP"

    #: Immediate interrupt of current acquisition or indicates a finished but interrupted
    # acquisition
    Break = "BRE"


class Coupling(StrEnum):
    """Enumeration to represent the different coupling modes"""

    #: DC coupling passes the input signal unchanged.
    DC = "DCL"

    #: Removes the DC offset voltage from the input signal.
    AC = "ACL"

    #: Connection to a virtual ground. All channel data is set to o V.
    GND = "GND"


class Bandwidth(StrEnum):
    """Enumeration to represent the different bandwidth limitation possibilities"""

    #: Use full bandwidth.
    Full = "FULL"

    #: Limit to 20 MHz. Higher frequencies are removed to reduce noise.
    B20_MHz = "B20"


class WaveformColor(StrEnum):
    """Enumeration to represent the different waveform colors"""

    #: Temperature colors. Blue corresponds to rare occurrences of the samples, while white
    # indicates frequent ones.
    Temperature = "TEMP"

    #: Rainbow colors. Blue corresponds to rare occurrences of the
    # samples, while red indicates frequent ones.
    Rainbow = "RAIN"

    #: Fire colors. Yellow corresponds to rare occurrences of the samples,
    # while red indicates frequent ones.
    Fire = "FIRE"

    #: Default monochrome color.
    Default = "DEF"


class ThresholdHysteresis(StrEnum):
    """Enumeration to represent the different threshold hysteresis settings """

    Small = "SMAL"
    Medium = "MED"
    Large = "LARG"


class DecimationMode(StrEnum):
    """Enumeration to represent the decimation modes per channel"""

    #: Input data is acquired with a sample rate which is aligned to the time base (horizontal
    # scale) and the record length.
    Sample = "SAMP"

    #: Peak Detect: the minimum and the maximum of n samples in a sample interval are recorded as
    # waveform points.
    PeakDetect = "PDET"

    #: High resolution: The average of n sample points is recorded as waveform point.
    HighResolution = "HRES"


class AcquisitionMode(StrEnum):
    """Enumeration to represent the acquisition modes"""

    #: The acquisitions are displayed as they are done.
    Refresh = "REF"

    #: The acquisitions are averaged.
    Average = "AVER"

    #: The envelope of a repetitive signal is shown, representing the borders in which the signal
    # occurs.
    Envelope = "ENV"


class ArithmeticMethod(StrEnum):
    """Enumeration to represent the acquisition modes"""

    #: The data of the current acquisition is recorded according to the decimation settings.
    Off = "OFF"

    #: Detects the minimum and maximum values in an sample interval over a number of acquisitions.
    Envelope = "ENV"

    #: Calculates the average from the data of the current acquisition and a number of
    # acquisitions before. The number of used acquisitions is set with
    # :attr:`RTB200X.acquisition_average_count`
    Average = "AVER"


class InterpolationMode(StrEnum):
    """Enumeration to represent the interpolation modes"""

    #: Linear interpolation between two adjacent sample points.
    Linear = "LIN"

    #: Interpolation by means of a sin(x)/x curve.
    SinX = "SINX"

    #: Sample & hold causes a histogram-like interpolation.
    SampleHold = "SMHD"


class RTB200XAnalogChannel(Channel):
    """
    One RTB2000 series oscilloscope channel
    """

    # vertical settings
    state = Channel.control(
        "CHANnel{ch}:STATe?", "CHANnel{ch}:STATe %s",
        """
        Control the channel signal.
        Switch it either on or off.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", False: "OFF"},
        cast=str,
        check_set_errors=True,
    )

    vertical_scale = Channel.control(
        "CHANnel{ch}:SCALe?", "CHANnel{ch}:SCALe %g",
        """
        Control the vertical scale for this channel.
        """,
        validator=strict_range,
        values=[1e-3, 10],
        check_set_errors=True,
    )

    vertical_range = Channel.control(
        "CHANnel{ch}:RANGe?", "CHANnel{ch}:RANGe %g",
        """
        Control the voltage range across the all vertical divisions of the diagram. Use the command
        alternatively instead :attr:`scale`
        """,
        validator=strict_range,
        values=[8e-3, 80],
        check_set_errors=True,
    )

    vertical_position = Channel.control(
        "CHANnel{ch}:POSition?", "CHANnel{ch}:POSition %g",
        """
        Control the vertical position of the waveform in divisions.
        """,
        validator=strict_range,
        values=[-5, 5],
        check_set_errors=True,
    )

    vertical_offset = Channel.control(
        "CHANnel{ch}:OFFSet?", "CHANnel{ch}:OFFSet %g",
        """
        Control the offset voltage, which is subtracted to correct an offset-affected signal.
        """,
        check_set_errors=True,
    )

    coupling = Channel.control(
        "CHANnel{ch}:COUPling?", "CHANnel{ch}:COUPling %s",
        """
        Control the connection of the indicated channel signal - coupling and termination.
        """,
        validator=strict_discrete_set,
        values=[e for e in Coupling],
        check_set_errors=True,
    )

    bandwidth = Channel.control(
        "CHANnel{ch}:BANDwidth?", "CHANnel{ch}:BANDwidth %s",
        """
        Control the bandwidth limit for the indicated channel.
        """,
        validator=strict_discrete_set,
        values=[e for e in Bandwidth],
        check_set_errors=True,
    )

    polarity_inversion_active = Channel.control(
        "CHANnel{ch}:POLarity?", "CHANnel{ch}:POLarity %s",
        """
        Control the inversion of the signal amplitude.

        To invert means to reflect the voltage values of all signal components against the ground
        level. Inversion affects only the display of the signal but not the trigger.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: "INV", False: "NORM"},
        cast=str,
        check_set_errors=True,
    )

    skew = Channel.control(
        "CHANnel{ch}:SKEW?", "CHANnel{ch}:SKEW %g",
        """
        Control a delay for the selected channel.

        Deskew compensates delay differences between channels caused by the different
        length of cables, probes, and other sources. Correct deskew values are important for
        accurate triggering.
        """,
        check_set_errors=True,
    )

    zero_offset = Channel.control(
        "CHANnel{ch}:ZOFFset?", "CHANnel{ch}:ZOFFset %g",
        """
        Control the zero offset.

        Differences in DUT and oscilloscope ground levels may cause larger zero errors affecting
        the waveform. If the DUT is ground-referenced, the "Zero Offset" corrects the zero
        error and sets the probe to the zero level.
        You can assess the zero error by measuring the mean value of a signal that should
        return zero.
        """,
        check_set_errors=True,
    )

    waveform_color = Channel.control(
        "CHANnel{ch}:WCOLor?", "CHANnel{ch}:WCOLor %s",
        """
        Control the color scale for the waveform color. Each scale comprises a set of colors,
        where each color represents a certain frequency of occurrence.
        """,
        check_set_errors=True,
        validator=strict_discrete_set,
        values=[e for e in WaveformColor]
    )

    threshold = Channel.control(
        "CHANnel{ch}:THReshold?", "CHANnel{ch}:THReshold %g",
        """
        Control the Threshold value for digitization of analog signals.

        If the signal value is higher than the threshold, the signal state is high (1 or true for
        the Boolean logic). Otherwise, the signal state is considered low (0 or false) if the
        signal value is below the threshold.

        Often used values are:
        - TTL: 1.4 V
        - ECL: -1.3 V
        - CMOS: 2.5 V
        Default unit: V
        """,
        check_set_errors=True
    )

    def find_threshold(self):
        """
        The instrument analyzes the channel and sets the threshold for digitization.
        """
        self.write("CHANnel%s:THReshold:FINDlevel" % self.id)

    threshold_hysteresis = Channel.control(
        "CHANnel{ch}:THReshold:HYSTeresis?", "CHANnel{ch}:THReshold:HYSTeresis %s",
        """
        Control the size of the hysteresis to avoid the change of signal states due to noise.
        """,
        check_set_errors=True,
        validator=strict_discrete_set,
        values=[e for e in ThresholdHysteresis]
    )

    label = Channel.control(
        "CHANnel{ch}:LABel?", "CHANnel{ch}:LABel %s",
        """
        Set a name for the selected channel.

        Maximum 8 characters more will be cut.
        """,
        check_set_errors=True,
        get_process=lambda v: v[1:-1],
        set_process=lambda v: "\"" + v + "\""
    )

    label_active = Channel.control(
        "CHANnel{ch}:LABel:STATe?", "CHANnel{ch}:LABel:STATe %s",
        """
        Control if the channel label will be shown or not
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", False: "OFF"},
        cast=str,
        check_set_errors=True,
    )

    # passive probes
    probe_unit = Channel.control(
        "PROBe{ch}:SETup:ATTenuation:UNIT?", "PROBe{ch}:SETup:ATTenuation:UNIT %s",
        """
        Control the unit that the probe can measure.

        Either 'V' or 'A',
        """,
        validator=strict_discrete_set,
        values=['V', 'A'],
        check_set_errors=True
    )

    probe_attenuation = Channel.control(
        "PROBe{ch}:SETup:ATTenuation:MANual?", "PROBe{ch}:SETup:ATTenuation:MANual %g",
        """
        Control the attenuation of the probe.

        Range: 0.0001 to 10e6
        """,
        validator=strict_range,
        values=[1e-4, 10e6],
        check_set_errors=True
    )

    probe_gain = Channel.control(
        "PROBe{ch}:SETup:GAIN:MANual?", "PROBe{ch}:SETup:GAIN:MANual %g",
        """
        Control the gain of the probe or signal chain.

        Range: 0.0001 to 10e6
        """,
        validator=strict_range,
        values=[1e-4, 10e3],
        check_set_errors=True
    )

    decimation_mode = Channel.control(
        "CHANnel{ch}:TYPE?", "CHANnel{ch}:TYPE %s",
        """
        Control the method to reduce the data stream of the ADC to a stream of waveform points
        with lower sample rate.
        """,
        check_set_errors=True,
        validator=strict_discrete_set,
        values=[e for e in DecimationMode]
    )

    arithmetics = Channel.control(
        "CHANnel{ch}:ARIThmetics?", "CHANnel{ch}:ARIThmetics %s",
        """
        Control the method to build the resulting waveform from several consecutive acquisitions
        of the signal.
        """,
        check_set_errors=True,
        validator=strict_discrete_set,
        values=[e for e in ArithmeticMethod]
    )


class RTB200X(Instrument):
    """
    Represents a Rohde & Schwarz RTB2000 series oscilloscope.

    All physical values that can be set can either be as a string of a value
    and a unit (e.g. "1.2 GHz") or as a float value in the base units (Hz,
    dBm, etc.).
    """

    def __init__(self, adapter, name="Rohde&Schwarz RTB200X", **kwargs):
        super().__init__(
            adapter, name, includeSCPI=True, **kwargs
        )

    def autoscale(self):
        """
        Performs an autoset process for analog channels: analyzes the enabled analog channel
        signals, and adjusts the horizontal, vertical, and trigger settings to display stable
        waveforms
        """
        self.write("AUToscale")

    acquisition_state = Instrument.control(
        "ACQuire:STATe?", "ACQuire:STATe %s",
        """
        Control the acquisition state of the instrument
        """,
        validator=strict_discrete_set,
        values=[e for e in AcquisitionState],
        check_set_errors=True,
    )

    def activate_analog_channels(self):
        """
        Switches all analog channels on
        """
        self.write("CHANNEL1:AON")

    def deactivate_analog_channels(self):
        """
        Switches all analog channels off.
        """
        self.write("CHANNEL1:AOFF")

    # horizontal settings
    horizontal_scale = Instrument.control(
        "TIMebase:SCALe?", "TIMebase:SCALe %g",
        """
        Control the horizontal scale for all channel and math waveforms.
        """,
        validator=strict_range,
        values=[1e-9, 50],
        check_set_errors=True,
    )

    horizontal_position = Instrument.control(
        "TIMebase:POSition?", "TIMebase:POSition %g",
        """
        Control the trigger position, the time distance from the trigger point to the reference
        point (trigger offset). The trigger point is the zero point of the diagram. Changing the
        horizontal position, you can move the trigger, even outside the screen.
        """,
        check_set_errors=True,
    )

    timebase_reference = Instrument.control(
        "TIMebase:REFerence?", "TIMebase:REFerence %g",
        """
        Control the time reference point in the diagram. The reference point is the rescaling
        center of the time scale on the screen. If you modify the time scale, the reference point
        remains fixed on the screen, and the scale is stretched or compressed to both sides of
        the reference point.
        The reference point defines which part of the waveform is shown. By default, the reference
        point is displayed in the center of the window, and you can move it to the left or
        right.
        """,
        validator=strict_discrete_set,
        values=[8.33, 50, 91.67],
        check_set_errors=True,
    )

    acquisition_time = Instrument.control(
        "TIMebase:ACQTime?", "TIMebase:ACQTime %g",
        """
        Control the time of one acquisition, that is the time across the 12 divisions of the diagram
        """,
        validator=strict_range,
        values=[250e-12, 500],
        check_set_errors=True,
    )

    horizontal_divisions = Instrument.measurement(
        "TIMebase:DIVisions?",
        """
        Get the number of horizontal divisions on the screen.
        """
    )

    # TIMebase:RATime not implemented

    # acquisition settings
    acquisition_points_automatic = Instrument.control(
        "ACQuire:POINts:AUTomatic?", "ACQuire:POINts:AUTomatic %s",
        """
        Control the automatic record length. The instrument sets a value that fits to the
        selected timebase. If you set a specific value with :attr:`acquisition_points`, the
        automatic assignment of a record length is turned off.

        .. code-block:: python
            instr.acquisition_points_automatic = True
            instr.horizontal_scale = 1e-9
            print(instr.acquisition_points_automatic)
            # 10000
            instr.horizontal_scale = 5e-3
            print(instr.acquisition_points_automatic)
            # 20000000
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", False: "OFF"},
        cast=str,
        check_set_errors=True,
    )

    acquisition_points = Instrument.control(
        "ACQuire:POINts:VALue?", "ACQuire:POINts:VALue %g",
        """
        Control the record length value, the number of recorded waveform points in a segment.
        The command turns :attr:`acquisition_points_automatic` false.
        If :attr:`acquisition_points_automatic` is true, the query acquisition_points returns
        the automatically set record length.
        Each predefined record length corresponds to a maximum number of history segments,
        which are stored in the instrument's memory. If option R&S RTB-K15 is installed,
        you can display the history segments.

        If the entered value differs from the predefined values, the instrument sets the closest
        value.

        Available record length values are:
        - 10 kSa (13107 history segments)
        - 20 kSa (13107 history segments)
        - 50 kSa (3276 history segments)
        - 100 kSa (2621 history segments)
        - 200 kSa (1456 history segments)
        - 500 kSa (319 history segments)
        - 1 MSa (319 history segments)
        - 2 MSa (159 history segments)
        - 5 MSa (40 history segments)
        - 10 MSa (32 history segments)
        - 20 MSa (16 history segments)
        """,
        validator=strict_discrete_set,
        values=[10e3, 20e3, 50e3, 100e3, 200e3, 500e3, 1e6, 2e6, 5e6, 10e6, 20e6],
        check_set_errors=True,
    )

    acquisition_mode = Instrument.control(
        "ACQuire:TYPE?", "ACQuire:TYPE %s",
        """
        Control the type of the aquisition mode.
        """,
        validator=strict_discrete_set,
        values=[e for e in AcquisitionMode],
        check_set_errors=True,
    )

    acquisition_count = Instrument.control(
        "ACQuire:NSINgle:COUNt?", "ACQuire:NSINgle:COUNt %g",
        """
        Control the number of waveforms acquired with :attr:`acquisition_state`
        """,
        check_set_errors=True,
    )

    acquisition_average_count = Instrument.control(
        "ACQuire:AVERage:COUNt?", "ACQuire:AVERage:COUNt %g",
        """
        Control the number of waveforms used to calculate the average waveform. The higher the
        number, the better the noise is reduced.
        """,
        validator=strict_range,
        values=[2, 100000],
        check_set_errors=True,
    )

    def reset_averaging(self):
        """
        Delete the waveform and restarts the average calculation.
        """
        self.write("ACQuire:AVERage:RESet")

    average_complete = Instrument.measurement(
        "ACQuire:AVERage:COMPlete?",
        """
        Get the state of averaging.
        """,
        map_values=True,
        values={True: "1", False: "0"},
        cast=str,
    )

    roll_automatic_enabled = Instrument.control(
        "TIMebase:ROLL:AUTomatic?", "TIMebase:ROLL:AUTomatic %s",
        """
        Control the automatic roll mode. The instrument switches to roll mode if the timebase
        is equal or slower than the roll mode limit defined with TODO TIMebase:ROLL:MTIMe.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", False: "OFF"},
        cast=str,
        check_set_errors=True,
    )

    roll_minimum_time = Instrument.control(
        "TIMebase:ROLL:MTIMe?", "TIMebase:ROLL:MTIMe %g",
        """
        Control the value at which the roll mode gets automatically activated,
        if :attr:`roll_automatic_enabled` is active.
        Default unit: s/div
        """,
        check_set_errors=True,
    )

    interpolation_mode = Instrument.control(
        "ACQuire:INTerpolate?", "ACQuire:INTerpolate %s",
        """
        Control the interpolation mode.
        """,
        validator=strict_discrete_set,
        values=[e for e in InterpolationMode],
        check_set_errors=True,
    )

    adc_sample_rate = Instrument.measurement(
        "ACQuire:POINts:ARATe?",
        """
        Get the sample rate of the ADC, that is the number of points that are sampled by
        the ADC in one second.
        Default unit: Hz
        """
    )

    sample_rate = Instrument.measurement(
        "ACQuire:SRATe?",
        """
        Get the sample rate, that is the number of recorded waveform samples per second.
        Default unit: Sa/s
        """
    )


class RTB2004(RTB200X):
    def __init__(self, adapter, name="Rohde & Schwarz RTB2004", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs,
        )

    analog = Instrument.ChannelCreator(
        RTB200XAnalogChannel,
        (1, 2, 3, 4),
        prefix="ch")


class RTB2002(RTB200X):

    def __init__(self, adapter, name="Rohde & Schwarz RTB2002", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs,
        )

    analog = Instrument.ChannelCreator(
        RTB200XAnalogChannel,
        (1, 2),
        prefix="ch")
