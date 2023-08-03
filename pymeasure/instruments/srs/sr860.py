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

from pymeasure.instruments.validators import strict_discrete_set, \
    truncated_discrete_set, truncated_range
from pymeasure.instruments import Instrument


class SR860(Instrument):

    SENSITIVITIES = [
        1e-9, 2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9,
        500e-9, 1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6,
        200e-6, 500e-6, 1e-3, 2e-3, 5e-3, 10e-3, 20e-3,
        50e-3, 100e-3, 200e-3, 500e-3, 1
    ]
    TIME_CONSTANTS = [
        1e-6, 3e-6, 10e-6, 30e-6, 100e-6, 300e-6, 1e-3, 3e-3, 10e-3,
        30e-3, 100e-3, 300e-3, 1, 3, 10, 30, 100, 300, 1e3,
        3e3, 10e3, 30e3
    ]
    ON_OFF_VALUES = ['0', '1']
    SCREEN_LAYOUT_VALUES = ['0', '1', '2', '3', '4', '5']
    EXPANSION_VALUES = ['0', '1', '2,']
    CHANNEL_VALUES = ['OCH1', 'OCH2']
    OUTPUT_VALUES = ['XY', 'RTH']
    INPUT_TIMEBASE = ['AUTO', 'IN']
    INPUT_DCMODE = ['COM', 'DIF', 'common', 'difference']
    INPUT_REFERENCESOURCE = ['INT', 'EXT', 'DUAL', 'CHOP']
    INPUT_REFERENCETRIGGERMODE = ['SIN', 'POS', 'NEG', 'POSTTL', 'NEGTTL']
    INPUT_REFERENCEEXTERNALINPUT = ['50OHMS', '1MEG']
    INPUT_SIGNAL_INPUT = ['VOLT', 'CURR', 'voltage', 'current']
    INPUT_VOLTAGE_MODE = ['A', 'A-B']
    INPUT_COUPLING = ['AC', 'DC']
    INPUT_SHIELDS = ['Float', 'Ground']
    INPUT_RANGE = ['1V', '300M', '100M', '30M', '10M']
    INPUT_GAIN = ['1MEG', '100MEG']
    INPUT_FILTER = ['Off', 'On']
    LIST_PARAMETER = ['i=', '0=Xoutput', '1=Youtput', '2=Routput', 'Thetaoutput', '4=Aux IN1',
                      '5=Aux IN2', '6=Aux IN3', '7=Aux IN4', '8=Xnoise', '9=Ynoise',
                      '10=AUXOut1', '11=AuxOut2', '12=Phase', '13=Sine Out amplitude',
                      '14=DCLevel', '15I=nt.referenceFreq', '16=Ext.referenceFreq']
    LIST_HORIZONTAL_TIME_DIV = ['0=0.5s', '1=1s', '2=2s', '3=5s', '4=10s', '5=30s', '6=1min',
                                '7=2min', '8=5min', '9=10min', '10=30min', '11=1hour', '12=2hour',
                                '13=6hour', '14=12hour', '15=1day', '16=2days']

    x = Instrument.measurement("OUTP? 0",
                               """ Reads the X value in Volts """
                               )
    y = Instrument.measurement("OUTP? 1",
                               """ Reads the Y value in Volts """
                               )
    magnitude = Instrument.measurement("OUTP? 2",
                                       """ Reads the magnitude in Volts. """
                                       )
    theta = Instrument.measurement("OUTP? 3",
                                   """ Reads the theta value in degrees. """
                                   )
    phase = Instrument.control(
        "PHAS?", "PHAS %0.7f",
        """ A floating point property that represents the lock-in phase
        in degrees. This property can be set. """,
        validator=truncated_range,
        values=[-360, 360]
    )
    frequency = Instrument.control(
        "FREQ?", "FREQ %0.6e",
        """ A floating point property that represents the lock-in frequency
        in Hz. This property can be set. """,
        validator=truncated_range,
        values=[0.001, 500000]
    )
    internalfrequency = Instrument.control(
        "FREQINT?", "FREQINT %0.6e",
        """A floating property that represents the internal lock-in frequency in Hz
        This property can be set.""",
        validator=truncated_range,
        values=[0.001, 500000]
    )
    harmonic = Instrument.control(
        "HARM?", "Harm %d",
        """An integer property that controls the harmonic that is measured.
        Allowed values are 1 to 99. Can be set.""",
        validator=strict_discrete_set,
        values=range(1, 99)
    )
    harmonicdual = Instrument.control(
        "HARMDUAL?", "HARMDUAL %d",
        """An integer property that controls the harmonic in dual reference mode that is measured.
        Allowed values are 1 to 99. Can be set.""",
        validator=strict_discrete_set,
        values=range(1, 99)
    )
    sine_voltage = Instrument.control(
        "SLVL?", "SLVL %0.9e",
        """A floating point property that represents the reference sine-wave
        voltage in Volts. This property can be set.""",
        validator=truncated_range,
        values=[1e-9, 2]
    )

    timebase = Instrument.control(
        "TBMODE?", "TBMODE %d",
        """Sets the external 10 MHZ timebase to auto(i=0) or internal(i=1).""",
        validator=strict_discrete_set,
        values=[0, 1],
        map_values=True
    )
    dcmode = Instrument.control(
        "REFM?", "REFM %d",
        """A string property that represents the sine out dc mode.
        This property can be set. Allowed values are:{}""".format(INPUT_DCMODE),
        validator=strict_discrete_set,
        values=INPUT_DCMODE,
        map_values=True
    )
    reference_source = Instrument.control(
        "RSRC?", "RSRC %d",
        """A string property that represents the reference source.
        This property can be set. Allowed values are:{}""".format(INPUT_REFERENCESOURCE),
        validator=strict_discrete_set,
        values=INPUT_REFERENCESOURCE,
        map_values=True
    )
    reference_triggermode = Instrument.control(
        "RTRG?", "RTRG %d",
        """A string property that represents the external reference trigger mode.
        This property can be set. Allowed values are:{}""".format(INPUT_REFERENCETRIGGERMODE),
        validator=strict_discrete_set,
        values=INPUT_REFERENCETRIGGERMODE,
        map_values=True
    )
    reference_externalinput = Instrument.control(
        "REFZ?", "REFZ&d",
        """A string property that represents the external reference input.
        This property can be set. Allowed values are:{}""".format(INPUT_REFERENCEEXTERNALINPUT),
        validator=strict_discrete_set,
        values=INPUT_REFERENCEEXTERNALINPUT,
        map_values=True
    )
    input_signal = Instrument.control(
        "IVMD?", "IVMD %d",
        """A string property that represents the signal input.
        This property can be set. Allowed values are:{}""".format(INPUT_SIGNAL_INPUT),
        validator=strict_discrete_set,
        values=INPUT_SIGNAL_INPUT,
        map_values=True
    )
    input_voltage_mode = Instrument.control(
        "ISRC?", "ISRC %d",
        """A string property that represents the voltage input mode.
        This property can be set. Allowed values are:{}""".format(INPUT_VOLTAGE_MODE),
        validator=strict_discrete_set,
        values=INPUT_VOLTAGE_MODE,
        map_values=True
    )
    input_coupling = Instrument.control(
        "ICPL?", "ICPL %d",
        """A string property that represents the input coupling.
        This property can be set. Allowed values are:{}""".format(INPUT_COUPLING),
        validator=strict_discrete_set,
        values=INPUT_COUPLING,
        map_values=True
    )
    input_shields = Instrument.control(
        "IGND?", "IGND %d",
        """A string property that represents the input shield grounding.
        This property can be set. Allowed values are:{}""".format(INPUT_SHIELDS),
        validator=strict_discrete_set,
        values=INPUT_SHIELDS,
        map_values=True
    )
    input_range = Instrument.control(
        "IRNG?", "IRNG %d",
        """A string property that represents the input range.
        This property can be set. Allowed values are:{}""".format(INPUT_RANGE),
        validator=strict_discrete_set,
        values=INPUT_RANGE,
        map_values=True
    )
    input_current_gain = Instrument.control(
        "ICUR?", "ICUR %d",
        """A string property that represents the current input gain.
        This property can be set. Allowed values are:{}""".format(INPUT_GAIN),
        validator=strict_discrete_set,
        values=INPUT_GAIN,
        map_values=True
    )
    sensitvity = Instrument.control(
        "SCAL?", "SCAL %d",
        """ A floating point property that controls the sensitivity in Volts,
        which can take discrete values from 2 nV to 1 V. Values are truncated
        to the next highest level if they are not exact. """,
        validator=truncated_discrete_set,
        values=SENSITIVITIES,
        map_values=True
    )
    time_constant = Instrument.control(
        "OFLT?", "OFLT %d",
        """ A floating point property that controls the time constant
        in seconds, which can take discrete values from 10 microseconds
        to 30,000 seconds. Values are truncated to the next highest
        level if they are not exact. """,
        validator=truncated_discrete_set,
        values=TIME_CONSTANTS,
        map_values=True
    )
    filter_slope = Instrument.control(
        "OFSL?", "OFSL %d",
        """A integer property that sets the filter slope to 6 dB/oct(i=0), 12 DB/oct(i=1),
        18 dB/oct(i=2), 24 dB/oct(i=3).""",
        validator=strict_discrete_set,
        values=range(0, 3)
    )
    filer_synchronous = Instrument.control(
        "SYNC?", "SYNC %d",
        """A string property that represents the synchronous filter.
        This property can be set. Allowed values are:{}""".format(INPUT_FILTER),
        validator=strict_discrete_set,
        values=INPUT_FILTER,
        map_values=True
    )
    filter_advanced = Instrument.control(
        "ADVFILT?", "ADVFIL %d",
        """A string property that represents the advanced filter.
        This property can be set. Allowed values are:{}""".format(INPUT_FILTER),
        validator=strict_discrete_set,
        values=INPUT_FILTER,
        map_values=True
    )
    frequencypreset1 = Instrument.control(
        "PSTF? 0", "PSTF 0, %0.6e",
        """A floating point property that represents the preset frequency for the F1 preset button.
        This property can be set.""",
        validator=truncated_range,
        values=[0.001, 500000]
    )
    frequencypreset2 = Instrument.control(
        "PSTF? 1", "PSTF 1, %0.6e",
        """A floating point property that represents the preset frequency for the F2 preset button.
        This property can be set.""",
        validator=truncated_range,
        values=[0.001, 500000]
    )
    frequencypreset3 = Instrument.control(
        "PSTF? 2", "PSTF2, %0.6e",
        """A floating point property that represents the preset frequency for the F3 preset button.
        This property can be set.""",
        validator=truncated_range,
        values=[0.001, 500000]
    )
    frequencypreset4 = Instrument.control(
        "PSTF? 3", "PSTF3, %0.6e",
        """A floating point property that represents the preset frequency for the F4 preset button.
        This property can be set.""",
        validator=truncated_range,
        values=[0.001, 500000]
    )
    sine_amplitudepreset1 = Instrument.control(
        "PSTA? 0", "PSTA0, %0.9e",
        """Floating point property representing the preset sine out amplitude, for the A1 preset button.
        This property can be set.""",  # noqa: E501
        validator=truncated_range,
        values=[1e-9, 2]
    )
    sine_amplitudepreset2 = Instrument.control(
        "PSTA? 1", "PSTA1, %0.9e",
        """Floating point property representing the preset sine out amplitude, for the A2 preset button.
        This property can be set.""",  # noqa: E501
        validator=truncated_range,
        values=[1e-9, 2]
    )
    sine_amplitudepreset3 = Instrument.control(
        "PSTA? 2", "PSTA2, %0.9e",
        """Floating point property representing the preset sine out amplitude, for the A3 preset button.
        This property can be set.""",  # noqa: E501
        validator=truncated_range,
        values=[1e-9, 2]
    )
    sine_amplitudepreset4 = Instrument.control(
        "PSTA? 3", "PSTA 3, %0.9e",
        """Floating point property representing the preset sine out amplitude, for the A3 preset button.
        This property can be set.""",  # noqa: E501
        validator=truncated_range,
        values=[1e-9, 2]
    )
    sine_dclevelpreset1 = Instrument.control(
        "PSTL? 0", "PSTL 0, %0.3e",
        """A floating point property that represents the preset sine out dc level for the L1 button.
        This property can be set.""",
        validator=truncated_range,
        values=[-5, 5]
    )
    sine_dclevelpreset2 = Instrument.control(
        "PSTL? 1", "PSTL 1, %0.3e",
        """A floating point property that represents the preset sine out dc level for the L2 button.
        This property can be set.""",
        validator=truncated_range,
        values=[-5, 5]
    )
    sine_dclevelpreset3 = Instrument.control(
        "PSTL? 2", "PSTL 2, %0.3e",
        """A floating point property that represents the preset sine out dc level for the L3 button.
        This property can be set.""",
        validator=truncated_range,
        values=[-5, 5]
    )
    sine_dclevelpreset4 = Instrument.control(
        "PSTL? 3", "PSTL3, %0.3e",
        """A floating point property that represents the preset sine out dc level for the L4 button.
        This property can be set.""",
        validator=truncated_range,
        values=[-5, 5]
    )

    aux_out_1 = Instrument.control(
        "AUXV? 0", "AUXV 1, %f",
        """ A floating point property that controls the output of Aux output 1 in
        Volts, taking values between -10.5 V and +10.5 V.
        This property can be set.""",
        validator=truncated_range,
        values=[-10.5, 10.5]
    )
    # For consistency with other lock-in instrument classes
    dac1 = aux_out_1

    aux_out_2 = Instrument.control(
        "AUXV? 1", "AUXV 2, %f",
        """ A floating point property that controls the output of Aux output 2 in
        Volts, taking values between -10.5 V and +10.5 V.
        This property can be set.""",
        validator=truncated_range,
        values=[-10.5, 10.5]
    )
    # For consistency with other lock-in instrument classes
    dac2 = aux_out_2

    aux_out_3 = Instrument.control(
        "AUXV? 2", "AUXV 3, %f",
        """ A floating point property that controls the output of Aux output 3 in
        Volts, taking values between -10.5 V and +10.5 V.
        This property can be set.""",
        validator=truncated_range,
        values=[-10.5, 10.5]
    )
    # For consistency with other lock-in instrument classes
    dac3 = aux_out_3

    aux_out_4 = Instrument.control(
        "AUXV? 3", "AUXV 4, %f",
        """ A floating point property that controls the output of Aux output 4 in
        Volts, taking values between -10.5 V and +10.5 V.
        This property can be set.""",
        validator=truncated_range,
        values=[-10.5, 10.5]
    )
    # For consistency with other lock-in instrument classes
    dac4 = aux_out_4

    aux_in_1 = Instrument.measurement(
        "OAUX? 0",
        """ Reads the Aux input 1 value in Volts with 1/3 mV resolution. """
    )
    # For consistency with other lock-in instrument classes
    adc1 = aux_in_1

    aux_in_2 = Instrument.measurement(
        "OAUX? 1",
        """ Reads the Aux input 2 value in Volts with 1/3 mV resolution. """
    )
    # For consistency with other lock-in instrument classes
    adc2 = aux_in_2

    aux_in_3 = Instrument.measurement(
        "OAUX? 2",
        """ Reads the Aux input 3 value in Volts with 1/3 mV resolution. """
    )
    # For consistency with other lock-in instrument classes
    adc3 = aux_in_3

    aux_in_4 = Instrument.measurement(
        "OAUX? 3",
        """ Reads the Aux input 4 value in Volts with 1/3 mV resolution. """
    )
    # For consistency with other lock-in instrument classes
    adc4 = aux_in_4

    def snap(self, val1="X", val2="Y", val3=None):
        """retrieve 2 or 3 parameters at once
        parameters can be chosen by index, or enumeration as follows:

        +--------+-------------+------------------------+
        | index  | enumeration | parameter              |
        +========+=============+========================+
        | 0      | X           | X output               |
        +--------+-------------+------------------------+
        | 1      | Y           | Y output               |
        +--------+-------------+------------------------+
        | 2      | R           | R output               |
        +--------+-------------+------------------------+
        | 3      | THeta       | θ output               |
        +--------+-------------+------------------------+
        | 4      | IN1         | Aux In1                |
        +--------+-------------+------------------------+
        | 5      | IN2         | Aux In2                |
        +--------+-------------+------------------------+
        | 6      | IN3         | Aux In3                |
        +--------+-------------+------------------------+
        | 7      | IN4         | Aux In4                |
        +--------+-------------+------------------------+
        | 8      | XNOise      | Xnoise                 |
        +--------+-------------+------------------------+
        | 9      | YNOise      | Ynoise                 |
        +--------+-------------+------------------------+
        | 10     | OUT1        | Aux Out1               |
        +--------+-------------+------------------------+
        | 11     | OUT2        | Aux Out2               |
        +--------+-------------+------------------------+
        | 12     | PHAse       | Reference Phase        |
        +--------+-------------+------------------------+
        | 13     | SAMp        | Sine Out Amplitude     |
        +--------+-------------+------------------------+
        | 14     | LEVel       | DC Level               |
        +--------+-------------+------------------------+
        | 15     | FInt        | Int. Ref. Frequency    |
        +--------+-------------+------------------------+
        | 16     | FExt        | Ext. Ref. Frequency    |
        +--------+-------------+------------------------+

        :param val1: parameter enumeration/index
        :param val2: parameter enumeration/index
        :param val3: parameter enumeration/index (optional)

        Defaults:
            val1 = "X"
            val2 = "Y"
            val3 = None
        """
        if val3 is None:
            return self.values(
                command=f"SNAP? {val1}, {val2}",
                separator=",",
                cast=float,
            )
        else:
            return self.values(
                command=f"SNAP? {val1}, {val2}, {val3}",
                separator=",",
                cast=float,
            )

    gettimebase = Instrument.measurement(
        "TBSTAT?",
        """Returns the current 10 MHz timebase source."""
    )
    extfreqency = Instrument.measurement(
        "FREQEXT?",
        """Returns the external frequency in Hz."""
    )
    detectedfrequency = Instrument.measurement(
        "FREQDET?",
        """Returns the actual detected frequency in HZ."""
    )
    get_signal_strength_indicator = Instrument.measurement(
        "ILVL?",
        """Returns the signal strength indicator."""
    )
    get_noise_bandwidth = Instrument.measurement(
        "ENBW?",
        """Returns the equivalent noise bandwidth, in hertz."""
    )
    # Display Commands
    front_panel = Instrument.control(
        "DBLK?", "DBLK %i",
        """Turns the front panel blanking on(i=0) or off(i=1).""",
        validator=strict_discrete_set,
        values=ON_OFF_VALUES,
        map_values=True
    )
    screen_layout = Instrument.control(
        "DLAY?", "DLAY %i",
        """A integer property that Sets the screen layout to trend(i=0), full strip chart
        history(i=1), half strip chart history(i=2), full FFT(i=3), half FFT(i=4) or big
        numerical(i=5).""",
        validator=strict_discrete_set,
        values=SCREEN_LAYOUT_VALUES,
        map_values=True
    )

    def screenshot(self):
        """Take screenshot on device
        The DCAP command saves a screenshot to a USB memory stick.
        This command is the same as pressing the [Screen Shot] key.
        A USB memory stick must be present in the front panel USB port.
        """
        self.write("DCAP")

    parameter_DAT1 = Instrument.control(
        "CDSP? 0", "CDSP 0, %i",
        """A integer property that assigns a parameter to data channel 1(green).
        This parameters can be set. Allowed values are:{}""".format(LIST_PARAMETER),
        validator=strict_discrete_set,
        values=range(0, 16)
    )
    parameter_DAT2 = Instrument.control(
        "CDSP? 1", "CDSP 1, %i",
        """A integer property that assigns a parameter to data channel 2(blue).
        This parameters can be set. Allowed values are:{}""".format(LIST_PARAMETER),
        validator=strict_discrete_set,
        values=range(0, 16)
    )
    parameter_DAT3 = Instrument.control(
        "CDSP? 2", "CDSP 2, %i",
        """A integer property that assigns a parameter to data channel 3(yellow).
        This parameters can be set. Allowed values are:{}""".format(LIST_PARAMETER),
        validator=strict_discrete_set,
        values=range(0, 16)
    )
    parameter_DAT4 = Instrument.control(
        "CDSP? 3", "CDSP 3, %i",
        """A integer property that assigns a parameter to data channel 3(orange).
        This parameters can be set. Allowed values are:{}""".format(LIST_PARAMETER),
        validator=strict_discrete_set,
        values=range(0, 16)
    )
    strip_chart_dat1 = Instrument.control(
        "CGRF? 0", "CGRF 0, %i",
        """A integer property that turns the strip chart graph of data channel 1 off(i=0) or on(i=1).
        """,  # noqa: E501
        validator=strict_discrete_set,
        values=ON_OFF_VALUES,
        map_values=True
    )
    strip_chart_dat2 = Instrument.control(
        "CGRF? 1", "CGRF 1, %i",
        """A integer property that turns the strip chart graph of data channel 2 off(i=0) or on(i=1).
        """,  # noqa: E501
        validator=strict_discrete_set,
        values=ON_OFF_VALUES,
        map_values=True
    )
    strip_chart_dat3 = Instrument.control(
        "CGRF? 2", "CGRF 2, %i",
        """A integer property that turns the strip chart graph of data channel 1 off(i=0) or on(i=1).
        """,  # noqa: E501
        validator=strict_discrete_set,
        values=ON_OFF_VALUES,
        map_values=True
    )
    strip_chart_dat4 = Instrument.control(
        "CGRF? 3", "CGRF 3, %i",
        """A integer property that turns the strip chart graph of data channel 4 off(i=0) or on(i=1).
        """,  # noqa: E501
        validator=strict_discrete_set,
        values=ON_OFF_VALUES,
        map_values=True
    )
    # Strip Chart commands
    horizontal_time_div = Instrument.control(
        "GSPD?", "GSDP %i",
        """A integer property for the horizontal time/div according to the following table:{}
        """.format(LIST_HORIZONTAL_TIME_DIV),
        validator=strict_discrete_set,
        values=range(0, 16)
    )

    def __init__(self, adapter, name="Stanford Research Systems SR860 Lock-in amplifier",
                 **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
