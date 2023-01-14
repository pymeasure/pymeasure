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
import logging
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    truncated_discrete_set,
    strict_discrete_set,
    truncated_range,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PanasonicVP7722A(Instrument):
    """Panasonic VP-7722A Audio Analyzer."""

    def __init__(self, adapter, name="Panasonic VP-7722A Audio Analyzer", **kwargs):
        self.analysis_mode = None
        super().__init__(
            adapter, name, **kwargs)

    frequency = Instrument.control(
        "TM1",
        "FR %.2fHZ",
        """Control the oscillator frequency setting in Hz (``TM1/FR``)

        .. note::

            When measuring with frequencies below 100 Hz, enable SLOW response.
        """,
        validator=truncated_range,
        values=[10.0, 110000.0],
        cast=float,
    )

    oscillator_output_amplitude_in_dbv = Instrument.setting(
        "AP %.2f DB",
        "Set the output amplitude of the oscillator in dBV (``AP``)",
        validator=truncated_range,
        values=[-85.9, 14.0],
        cast=float,
    )

    oscillator_output_amplitude_in_dbm = Instrument.setting(
        "AP %.2f DM",
        "Set the output amplitude of the oscillator in dBm (``AP``)",
        validator=truncated_range,
        values=[-83.7, 16.2],
        cast=float,
    )

    def oscillator_output_off(self):
        """Set oscillator to off and disconnect the oscillator signal (``APOFF``)"""
        self.write("APOFF")

    oscillator_imd = Instrument.setting(
        "MX%d",
        """Set oscillator IMD test signal mixing ratio (``MX``)

        When the data code is 0, the IMD test signal mode is turned off
        and the oscillator provides the ordinary sine wave signals.

        .. note::

            Before setting the IMD test signal mode, set the frequency
            and the output amplitude of the oscillator to meet the
            conditions of the IMD measuring signals. If these
            conditions are not met, the program code will be invalid.

        """,
        validator=truncated_range,
        values=[0, 8],
        cast=int,
    )

    def measure_level(self):
        """Set to level measurement mode (``MM1``)"""
        self.write("MM1")

    def measure_ratio_right_left(self):
        """Set to ratio (R/L) measurement mode (``MM2``)"""
        self.write("MM2")

    def measure_signal_noise(self):
        """Set to S/N measurement mode (``MM3``)

        .. note::

            1.  When using the S/N measurement function with GP-IB, pay
                attention to the response time of the device under
                measurement and to the S/N delay time setting condition.
                If the measured data is requested without waiting for
                the S/N delay time to lapse, incorrect values may be
                obtained.

            2.  When measuring S/N ratios under the GP-IB control, it is
                recommended to measure and calculate signal and noise
                separately by the level measurement function, or to
                measure by the relative level measurement mode

        """
        self.write("MM3")

    def measure_distortion(self):
        "Set to total distortion measurement mode (``MM4``)"
        self.write("MM4")

    def measure_thd1(self):
        "Set to THD1 measurement mode (``MM5``)"
        self.write("MM5")

    def measure_average(self):
        "Set to average measurement mode (``MMS1``)"
        self.write("MMS1")

    def measure_ratio_left_right(self):
        "Set to ratio (L/R) measurement mode (``MMS2``)"
        self.write("MMS2")

    def measure_sinad(self):
        "Set to SINAD measurement mode (``MMS3``)"
        self.write("MMS3")

    def measure_imd(self):
        "Set to IMD measurement mode (``MMS4``)"
        self.write("MMS4")

    def measure_thd2(self):
        "Set to THD2 measurement mode (``MMS5``)"
        self.write("MMS5")

    measure_harmonic_analysis = Instrument.setting(
        "HA%d",
        "Set harmonic analysis mode to 2fo, 3fo, 4fo, 5fo or a combination. (``HA``)",
        validator=truncated_discrete_set,
        values=[2, 3, 23, 4, 24, 34, 234, 5, 25, 35, 235, 45, 245, 345, 2345],
        get_process=lambda v: int(v)
    )

    measure_relative = Instrument.setting(
        "RR%d",
        """Set relative level measurement selection. (``RR0/RR1``)

        In level measurement or average measurement, the
        relative levels can be measured. Relative values are obtained
        with the level measured upon the output of these codes as the
        reference value.

        .. note::

            1.  Be sure to send out the relative level value measurement
                code (``RR1``) after completing the level measurement. If
                it (``RR1``) is input without a level reading, it is ignored.
                It (``RR1``) is invalid when sent out simultaneously with
                a level measuring code (``MM1``), (``MMS1``).

            2.  The relative level measurement mode is automatically
                cleared when (``AU``) or (``IN``) is sent. Pay attention
                to this.

        """,
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    filter_high_pass_400hz = Instrument.setting(
        "HP%d",
        "Set 400Hz HPF (``HP0/HP1``)",
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    filter_low_pass_30khz = Instrument.setting(
        "LP%d",
        "Set 30kHz LPF (``LP0/LP1``)",
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    filter_low_pass_80khz = Instrument.setting(
        "LP%d",
        "Set 80kHz LPF (``LP0/LP2``)",
        validator=strict_discrete_set,
        values={False: 0, True: 2},
        map_values=True
    )

    filter_psophometric = Instrument.setting(
        "PS%d",
        "Set psophometric filter (``PS0/PS1``)",
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    filter_option = Instrument.setting(
        "PS%d",
        "Set option filter (``PS0/PS2``)",
        validator=strict_discrete_set,
        values={False: 0, True: 2},
        map_values=True
    )

    def filter_notch_auto(self):
        "Set the notch filter to auto tuning (``MD0``)"
        self.write("MD0.0")

    filter_notch = Instrument.setting(
        "MD0.%.2fHZ",
        "Set the notch filter to a manual value in Hz (``MD0``)",
        validator=truncated_range,
        values=[10.0, 110000.0],
        cast=float,
    )

    response_speed_fast = Instrument.setting(
        "RS%d",
        """Set response speed (``RS1/RS2``)

        The indication response characteristics may be set for a
        selected detection method and either for FAST or SLOW.

        .. note::

            When measuring with frequencies below 100 Hz, enable SLOW response.
        """,
        validator=strict_discrete_set,
        values={False: 2, True: 1},
        map_values=True
    )

    def response_rms(self):
        "Set indication response characteristics to RMS value response  (``DE1``)"
        self.write("DE1")

    def response_average(self):
        "Set indication response characteristics to Average value response  (``DE2``)"
        self.write("DE2")

    def channel_left(self):
        "Set selection to left channel  (``IN1``)"
        self.write("IN1")

    def channel_right(self):
        "Set selection to right channel  (``IN2``)"
        self.write("IN2")

    def channel_both(self):
        """Set selection to left and right channel (``IN3``)

        .. note::

            Measurements in left and right may not give correct data, except for
            for ratio and average measurements unless sufficient time
            is given before making data requests.

            For 2-signal measurement under GP-IB control use (``IN1``) or (``IN2``)
            (L or R single channel measurement) for each signal.

        """
        self.write("IN3")

    def display_db(self):
        "Set unit display to dB (``LOG``)"
        self.write("LOG")

    def display_volts(self):
        "Set unit display to V, % (``LIN``)"
        self.write("LIN")

    def display_auto(self):
        """Set unit display to automatic range (``AU``)

        This code is for selecting functions such as the automatic
        range. It clears the fixed state of manually set ranges, etc.
        """
        self.write("AU")

    def input_range_auto(self):
        "Set the input range to automatic ranging (default) (``MD1``)"
        self.write("MD1.0")

    input_range = Instrument.setting(
        "MD1.%d",
        """Set the input range to a manual setting (``MD1``)

        The setting codes are between 1 and 24, covering a range between
        -17.5 and 40 dB at 2.5 dB increments.

        (b) Measurement range setting
        The GP-IB program code related to setting the measurement range
        is the same as for the level measurement.

        (c) Denominator signal measurement range setting
        Data Denominator (input) Header Data Denornina for (input)

        ==========  ==========================
        Range code  Input range setting
        ==========  ==========================
         1          100 V, 40 dB
         2          75 v, 37.5dB
         3          56.2 V, 35 dB
         4          42.2 V, 32.5dB
         5          31.6 V, 30 dB
         6          23.7 V, 27.SdB
         7          17.8 V, 25 dB
         8          13.3 V, 22.5dB
         9          10 V, 20 dB
         10         7.5 V, 17.5dB
         11         5.62 V, 15 dB
         12         4.22 V, 12.5dB
         13         3.16 v, 10 dB
         14         2.37 V, 7.5dB
         15         1.78 V, 5 dB
         16         1.33 V, 2.5dB
         17         1 V, 0 dB
         18         750 mV, -2.5dB
         19         562 mV, -5 dB
         20         422 mV, -7.5dB
         21         316 mV, -10 dB
         22         237 mV, -12.5dB
         23         178 mV, -15 dB
         24         133 mV, -17.5dB
        ==========  ==========================

        """,
        validator=truncated_range,
        values=[1, 24],
        cast=int,
    )

    def measure_range_auto(self):
        "Set the measuring range setting to automatic ranging (default) (``MD2``)"
        self.write("MD2.0")

    measure_range_level = Instrument.setting(
        "MD2.%d",
        """Set the internal measuring range when in level measurement (``MD2``).

        ==========  ==========================
        Range code  Measuring range setting
        ==========  ==========================
         1          100 V, 40 dB
         2          31.6 V, 30 dB
         3          3.16 V, 10 dB
         4          316 mV, -10 dB
         5          31.6mV, -30 dB
         6          3.16mV, -50 dB
         7          .316mV, -70 dB
        ==========  ==========================

        """,
        validator=truncated_range,
        values=[1, 7],
        cast=int,
    )

    measure_range_distortion = Instrument.setting(
        "MD2.%d",
        """Set the internal measuring range when measuring distortion (``MD2``).

        ==========  ==========================
        Range code  Measuring range setting
        ==========  ==========================
         1          100 %, 0 dB
         2          10 %, -20 dB
         3          1 %, -40 dB
         4          0.1%, -60 dB
         5          0.01%, -80 dB
         6          0.001%, -100dB
        ==========  ==========================

        """,
        validator=truncated_range,
        values=[1, 6],
        cast=int,
    )

    measure_relative_level_ratio = Instrument.setting(
        "MD3.%.2f",
        "Set relative level ratio measurement voltage in Volts (10µV - 100 V) (``MD3``)",
        validator=truncated_range,
        values=[0.00001, 100.0],
        cast=float,
    )

    measure_signal_noise_delay_time = Instrument.setting(
        "MD4.%.2f",
        "Set S/N delay time setting (``MD4``)",
        validator=truncated_range,
        values=[1.5, 99.9],
        cast=float,
    )

    measure_number_of_averages = Instrument.setting(
        "MD5.%d",
        """Set the number of averaging times (``MD5``)

        The instrument, with its average measurement function, can pick off the
        signal component by arithmetic averaging process synchronized with the
        reference signal, and measure its level.

        The number of averages can be selected from 16, 32, 64, 128, and 256 times.
        """,
        validator=truncated_discrete_set,
        values={16: 0, 32: 1, 64: 2, 128: 3, 256: 4},
        map_values=True
    )

    measure_all_hold = Instrument.setting(
        "MD6.",
        """Set all current conditions to hold such as the measurement
        range that has been automatically set (``MD6``).

        When this code is received in any measurement modes, the
        internal range, the notch filter frequency, etc. effective
        that time are locked. For example, when this code is received
        in the DISTN mode, the input range, measurement range, and the
        notch filter frequency effective at that time are locked.

        This function holds all current conditions such as the measurement
        range that has been automatically set.
        In the distortion measurement, for example, the fundamental-rejection
        filter frequency, input range, and measurement range are fixed to the
        current condition all at the same time.
        """,
    )

    trigger_measurement = Instrument.measurement(
        " ",
        """Measure the pseudo-triggered output that was set by any of the (``MD1-6``) functions. 
        
        The analyzer can utilize pseudo-trigger (a space ' ') as a measurement trigger
        signal. The GP-IB controller can get the measured data at the time when the
        pseudo-trigger is sent to the analyzer. The pseudo-trigger function enables 
        the controller to read the latest measured data, since the measurement is 
        started when the controller sends the Pseudo-trigger signal independently of 
        the measurement cycle of the analyzer. An example program utilizing Pseudo-trigger
        function is shown below.

        .. code-block:: python

            analyzer = PanasonicVP7722A("GPIB::15")
            analyzer.measure_level()
            analyzer.filter_high_pass_400hz = False
            analyzer.filter_low_pass_30khz = True
            analyzer.measure_range_level = 1    # Set measurement range setting to 100 V, 40 dB
            for i in range(10):
                print(analyzer.trigger_measurement())   # Write the pseudo-trigger and print result

        """,
        lambda v: float(v.strip()),
    )

    config_recall = Instrument.setting(
        "RC%02d",
        "Set memory location to recall configuration (``RC``)",
        validator=truncated_range,
        values=[0, 99],
        cast=int,
    )

    config_store = Instrument.setting(
        "ST%02d",
        "Set memory location where to store current configuration (``ST``)",
        validator=truncated_range,
        values=[0, 99],
        cast=int,
    )

    config = Instrument.measurement(
        "TM0",
        """Measure the machine config in it's current state. (``TM0``)

        In this mode, the state of the analyzer at the time when the call
        is made will be provided.

        .. admonition:: For example,

            Oscillator frequency: 1 kHz, output amplitude:
            -10.0 dBV, sine wave signal, level measurement,
            400 Hz HPF ON, LPF OFF, PSOPHO OFF, FAST response,
            rms value response, L channel, V display,
            automatic measurement mode

            FR1.000KZ AP-10.0DB MX0 HH1 HP1 LP0 PS0 RS 1 DE1 IN1 RR0 LIN AU
        """,
    )

    input_level = Instrument.measurement(
        "TM2",
        """Measure input level (``TM2``).

        It is valid for (``MM4``), (``MM5``), (``MMS5``), (``HA``) (for distortion),
        (``MM2``), (``MMS2``) (for ratio) and (``MMS3``) (for SINAD).
        If this mode is specified in measurement modes other than the above
        error data is provided. '1-"

        .. note::

            There are two basic output formats, one for dB unit (``LOG``), and the other
            for V or % unit (``LIN``).

        """,
        lambda v: float(v.strip()),
    )

    frequency_and_input_level = Instrument.measurement(
        "TM3",
        """Measure frequency data and input level measured data (``TM3``)

        The outputs provided at the same time are; (1) frequency data of
        talk mode 1, and (2) measured input level data of the talk mode 2.

        returns a tuple with (Frequency data, Measured input level data)

        When this mode is set for measurement modes other than (``MM4``), (``MM5``),
        (``MMS5``), (``HA``) (for distortion) (``MM2``), (``MMS2``) (for ratio), and (``MMS3``) (for
        only the frequency data output is provided.

        .. note::

            There are two basic output formats, one for dB unit (``LOG``), and the other
            for V or % unit (``LIN``).

        """,
        lambda v: tuple(map(float, v.strip().split(','))),
    )

    measure_data = Instrument.measurement(
        "TM4",
        """Measure measured data (``TM4``)

        In this mode, only the measurement results are provided.

        .. note::

            There are two basic output formats, one for dB unit (``LOG``), and the other
            for V or % unit (``LIN``).

        """,
        lambda v: float(v.strip()),
    )

    frequency_and_measure_data = Instrument.measurement(
        "TM5",
        """Measure frequency data and measured data (``TM5``)

        The outputs provided at the same time are; (1) frequency data of
        the talk mode 1, (2) and measured data of the talk mode 4.

        return a tuple with (Frequency data, Measured data)

        .. note::

            There are two basic output formats, one for dB unit (``LOG``), and the other
            for V or % unit (``LIN``).

        """,
        lambda v: tuple(map(float, v.strip().split(','))),
    )

    input_level_and_measure_data = Instrument.measurement(
        "TM6",
        """Measure input level measured data and measured data (``TM6``)

        The outputs provided at the same time are; (1) measured input level
        data of the talk mode 2, (2) and measured data of talk mode 4.

        returns a tuple (Measured input level data, Measured data)

        When this mode is set for measurement modes other than (``MM4``), (``MM5``),
        (``MMS5``), (``HA``) (for distortion), (``MM2``), (``MMS2``) (for ratio),
        and (``MMS3``) (for SINAD), only the measured data output is provided.

        .. note::

            There are two basic output formats, one for dB unit (``LOG``), and the other
            for V or % unit (``LIN``).

        """,
        lambda v: tuple(map(float, v.strip().split(','))),
    )

    frequency_and_input_level_and_measure_data = Instrument.measurement(
        "TM7",
        """Measure all data, i.e., frequency data, input level measured data,
        and measured data (``TM7``).

        returns a tuple with (Frequency data, Measured input level data, Measured data)

        The outputs provided at the same time are; (1) frequency data of
        the talk mode 1, (2) measured input level data of talk mode 2,
        and (3) measured data of talk mode 4.

        When this mode is set for measurement modes other than MM4, MM5,
        (``MMS5``), (``HA``) (for distortion), (``MM2``), ``(MMS2``) (for ratio),
        and (``MMS3``) (for SINAD), frequency data and measured data are provided.

        .. note::

            There are two basic output formats, one for dB unit (``LOG``), and the other
            for V or % unit (``LIN``).

        """,
        lambda v: tuple(map(float, v.strip().split(','))),
    )
