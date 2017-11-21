#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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

from pymeasure.instruments import Instrument, discreteTruncate
from pymeasure.instruments.validators import strict_discrete_set, \
    truncated_discrete_set, strict_range

from enum import Enum
import numpy as np
import time
import re


class SR830(Instrument):

    class OutputInterface(Enum):
        RS232=0
        GPIB=1

    REF_SOURCES = ['external', 'internal']
    REF_TRIGGERS = ['sine_zero', 'ttl_rising', 'ttl_falling']

    IN_MODES = ['a', 'a-b', 'i_1mohm', 'i_100mohm']
    IN_GROUNDS = ['float', 'ground']
    IN_COUPLINGS = ['ac', 'dc']
    IN_LINE_FILTS = ['off', '1x', '2x', 'both']

    SAMPLE_FREQUENCIES = [
        62.5e-3, 125e-3, 250e-3, 500e-3, 1, 2, 4, 8, 16,
        32, 64, 128, 256, 512
    ]
    SENSITIVITIES = [
        2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9,
        500e-9, 1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6,
        200e-6, 500e-6, 1e-3, 2e-3, 5e-3, 10e-3, 20e-3,
        50e-3, 100e-3, 200e-3, 500e-3, 1
    ]
    TIME_CONSTANTS = [
        10e-6, 30e-6, 100e-6, 300e-6, 1e-3, 3e-3, 10e-3,
        30e-3, 100e-3, 300e-3, 1, 3, 10, 100, 300, 1e3,
        3e3, 10e3, 30e3
    ]
    FILTER_SLOPES = [6, 12, 18, 24]
    EXPANSION_VALUES = [1, 10, 100]
    RESERVE_VALUES = ['high', 'normal', 'low']
    CHANNELS = ['X', 'Y', 'R']
    SNAP_VALUES = [None, 'X', 'Y', 'R', 'THETA', 'AUX1', 'AUX2', 'AUX3', 'AUX4',
                   'FREQ', 'CH1', 'CH2'] # starts at 1

    ref_source = Instrument.control(
        "FMOD?", "FMOD%d",
        """
        Reference source configuration. Can be set. Possible values:

        * ``"external"``: the internal PLL phase locks to the REF IN input
          signal, using this for lock-in measurement and for both the TTL OUT
          (on the back) and SINE OUT. See also :attr:`ref_trigger` and
          :attr:`~.sine_voltage` (for the SINE OUT).
        * ``"internal"``: uses the internal oscillator, which can be configured
          with the :attr:`~.frequency`, :attr:`~.phase` and :attr:`~.sine_voltage`
          attributes.

        """,
        validator=strict_discrete_set,
        values=REF_SOURCES,
        map_values=True,
        set_process=lambda s: s.lower()
    )

    ref_trigger = Instrument.control(
        "RSLP?", "RSLP%i",
        """
        Reference trigger used to lock into the REF IN input signal.
        Possible values:

        * ``"sine_zero"``: sine zero crossings. Cannot be used below 1Hz.
        * ``"ttl_rising"``: TTL rising edge
        * ``"ttl_falling"``: TTL falling edge
        """,
        validator=strict_discrete_set,
        values=REF_TRIGGERS,
        map_values=True,
        set_process=lambda s: s.lower()
    )

    sine_voltage = Instrument.control(
        "SLVL?", "SLVL%0.3f",
        """
        Reference SINE OUT voltage (in volts RMS, floating-point). This property
        can be set, is rounded to 0.002 V and has range 0.004 <= v <= 5.000.
        """,
        validator=strict_range,
        values=[0.004, 5.000]
    )

    frequency = Instrument.control(
        "FREQ?", "FREQ%0.5e",
        """
        Lock-in frequency (in Hertz, floating-point). This
        property can be set only if :attr:`~.ref_source` is ``"internal"``.
        The value is rounded to 5 digits or 0.0001 Hz, whichever is greater. The
        range is limited to ``0.001 <= n*f <= 102000`` (where ``n`` is the
        value of :attr:`~.harmonic`) (if harmonic > 1, this range constraint is
        not verified by PyMeasure).
        """,
        validator=strict_range,
        values=[0.001, 102000]
    )

    harmonic = Instrument.control(
        "HARM?", "HARM%d",
        """
        Detection harmonic (integer). The detected lock-in frequency will be
        harmonic * :attr:`~.frequency`. This property can be set. Its valid range
        is 1 to 19999, but only if harmonic * :attr:`~.frequency` <= 102000 Hz
        (the latter is not verified in PyMeasure).
        """,
        validator=strict_range,
        values=[1, 19999]
    )

    phase = Instrument.control(
        "PHAS?", "PHAS%0.2f",
        """
        The lock-in phase (degrees, floating-point). This property
        can be set only if :attr:`~.ref_source` is ``"internal"``
        (TBD - not documented but it is true of frequency). The value is rounded
        to 0.01 degrees. Its valid set range is -360.00 <= x <= 729.99, which
        is wrapped into the range -180.00 <= x <= +180.00. Its valid read range
        -180.00 <= x <= +180.00. """,
        validator=strict_range,
        values=[-360.00, 729.99]
    )

    input_mode = Instrument.control(
        "ISRC?", "ISRC%d",
        """
        The input mode. This property can be set. Possible values:

        * ``"a"``: Input signal is from the A connector only.
        * ``"a-b"``: Input signal is differential (A - B).
        * ``"i_1mohm"``: Current input with 1 MΩ gain.
        * ``"i_100mohm"``: Current input with 100 MΩ gain.

        Sensitivities between 20nA and 1μA will automatically sselect the 1 MΩ
        range.
        """,
        validator=strict_discrete_set,
        values=IN_MODES,
        map_values=True,
        set_process=lambda s: s.lower()
    )

    input_ground = Instrument.control(
        "IGND?", "IGND%d",
        """
        The input shield cable grounding. This property can be set.
        Possible values: ``"float"`` or ``"ground"``. See the manual.
        """,
        validator=strict_discrete_set,
        values=IN_GROUNDS,
        map_values=True,
        set_process=lambda s: s.lower()
    )

    input_coupling = Instrument.control(
        "ICPL?", "ICPL%d",
        """
        The input coupling. This property can be set. Possible values:
        ``"ac"`` or ``"dc"``. When using ``"ac"`` coupling, be aware of the
        cutoff frequency and its effect on measurements at low frequency
        (see the manual).
        """,
        validator=strict_discrete_set,
        values=IN_COUPLINGS,
        map_values=True,
        set_process=lambda s: s.lower()
    )

    input_line_filt = Instrument.control(
        "ILIN?", "ILIN%d",
        """
        Status of the input line filter. This configures two notch filters to
        reject line frequency noise (e.g. 60 Hz in North America). This
        property can be set. Possible values:

        * ``"off"``
        * ``"1x"``: Reject line frequency, e.g. 60 Hz.
        * ``"2x"``: Reject the first harmonic, e.g. 120 Hz.
        * ``"both"``: Reject both line frequency and its first harmonic.

        Be aware of the effect on measurements near these frequencies due to
        these filters.
        """,
        validator=strict_discrete_set,
        values=IN_LINE_FILTS,
        map_values=True,
        set_process=lambda s: s.lower()
    )

    channel1 = Instrument.control(
        "DDEF?1;", "DDEF1,%d,0",
        """
        Channel 1 displayed measurement. Possible values: ``"X"``, ``"R"``,
        ``"X Noise"``, ``"Aux In 1"``, ``"Aux In 2"``. The ratio is always set
        to none. This property can be set.
        """,
        validator=strict_discrete_set,
        values=['X', 'R', 'X Noise', 'Aux In 1', 'Aux In 2'],
        map_values=True,
        get_process=lambda s: s[0] # ignore the ratio
    )

    channel2 = Instrument.control(
        "DDEF?2;", "DDEF2,%d,0",
        """
        Channel 1 displayed measurement. Possible values: ``"Y"``, ``"Theta"``,
        ``"Y Noise"``, ``"Aux In 3"``, ``"Aux In 4"``. The ratio is always set
        to none. This property can be set.
        """,
        validator=strict_discrete_set,
        values=['Y', 'Theta', 'Y Noise', 'Aux In 3', 'Aux In 4'],
        map_values=True,
        get_process=lambda s: s[0] # ignore the ratio
    )

    channel1_out = Instrument.control(
        "FPOP?1;", "FPOP1,%d",
        """
        Channel 1 front panel analog output (not display). Possible values:

        * ``"display"``: channel1 display
        * ``"x"``: force the output to be X
        """,
        validator=strict_discrete_set,
        values=['display', 'x'],
        map_values=True,
        set_procss=lambda s: s.lower()
    )

    channel2_out = Instrument.control(
        "FPOP?2;", "FPOP2,%d",
        """
        Channel 2 front panel analog output (not display). Possible values:

        * ``"display"``: channel2 display
        * ``"x"``: force the output to be Y
        """,
        validator=strict_discrete_set,
        values=['display', 'y'],
        map_values=True,
        set_procss=lambda s: s.lower()
    )

    channel1_value = Instrument.measurement("OUTR?1",
        """ Reads the current channel 1 display,
            in the same units as the display. """)

    channel2_value = Instrument.measurement("OUTR?2",
        """ Reads the current channel 2 display,
            in the same units as the display. """)

    x = Instrument.measurement("OUTP?1",
        """ Reads the X measurement in volts. """
    )

    y = Instrument.measurement("OUTP?2",
        """ Reads the Y measurement in volts. """
    )

    magnitude = Instrument.measurement("OUTP?3",
        """ Reads the magnitude measurement in volts. """
    )

    theta = Instrument.measurement("OUTP?4",
        """ Reads the theta (phase) measurement in degrees. """
    )

    sensitivity = Instrument.control(
        "SENS?", "SENS%d",
        """
        Sensitivity (in volts, floating-point), which can take discrete
        values from 2 nV to 1 V. When :attr:`input_mode` is a current mode,
        unit is in μA. Values are rounded to the next highest level if they
        are not exact.
        """,
        validator=truncated_discrete_set,
        values=SENSITIVITIES,
        map_values=True
    )

    time_constant = Instrument.control(
        "OFLT?", "OFLT%d",
        """
        Low-pass filter time constant (in seconds, floating-point), which can
        take discrete values from 10 μs to 30 ks. Values are rounded to the
        next highest level if they are not exact.
        """,
        validator=truncated_discrete_set,
        values=TIME_CONSTANTS,
        map_values=True
    )

    filter_slope = Instrument.control(
        "OFSL?", "OFSL%d",
        """
        Low-pass filter slope. Possible values are 6, 12, 18 or 24 dB/octave,
        as an integer. Values are rounded to the next highest value if they
        are not exact.
        """,
        validator=truncated_discrete_set,
        values=FILTER_SLOPES,
        map_values=True
    )

    reserve = Instrument.control(
        "RMOD?", "RMOD%d",
        """
        The dynamic reserve mode. Possible values are:

        * ``"high"``: High Reserve
        * ``"normal"``: Normal
        * ``"low"``: Low noise

        In version 0.5 and prior, the values "High reserve", "Normal" and
        "Low noise" were used. These values are deprecated but available
        when setting this property.
        """,
        validator=strict_discrete_set,
        values=RESERVE_VALUES,
        map_values=True,
        set_process=lambda s: s.lower().split(' ')[0]
    )

    sync_filter = Instrument.control(
        "SYNC?", "SYNC%d",
        """
        Synchronous filter (boolean). If True, and the detection frequency
        (:attr:`~.harmonic` * :attr:`~.frequency`) is less than 200 Hz, then
        the synchronous filter is turned on.
        """,
        set_process=lambda x: 1 if x else 0
    )

    lia_status_byte = Instrument.measurement(
        "LIAS?",
        """
        Get the full LIA status byte as an integer value. The bits, and the
        associated single-bit getter, are as follows:
        
        * 0: :meth:`~.is_input_overload`
        * 1: :meth:`~.is_filter_overload`
        * 2: :meth:`~.is_output_overload`
        * 3: :meth:`~.is_freq_range_changed`
        * 4: :meth:`~.is_freq_range_changed`
        * 5: :meth:`~.is_time_constant_changed`
        * 6: :meth:`~.is_data_storage_triggered`
        * 7: Unused

        This method is faster than the individual calls, as it obtains the
        entire status byte in one command to the instrument.

        Only bits enabled by :meth:`enable_lia_status` will be set by the
        instrument when the associated event occurs.
        """)


    def __init__(self, resourceName, outx=OutputInterface.GPIB, **kwargs):
        """
        :param resourceName: resource name string or instance of a PyMeasure
            adapter object referring to this instrument's connection
        :param outx: Output interface. One of OutputInterface.RS232 or
            OutputInterface.GPIB. Required for the instrument to send responses
            to the correct interface.
        """
        super(SR830, self).__init__(
            resourceName,
            "Stanford Research Systems SR830 Lock-in amplifier",
            **kwargs
        )

        # for adapters that support terminations - per the SR830 docs
        try:
            if self.adapter.write_term is None:
                self.adapter.write_term = '\r'
        except AttributeError:
            pass

        try:
            if self.adapter.read_term is None:
                self.adapter.read_term = b'\r'
        except AttributeError:
            pass

        try:
            self.write("OUTX%d" % outx.value)
        except AttributeError: # outx is an int maybe?
            self.write("OUTX%d" % outx)


    def measure_multiple(self, measurements=('R', 'THETA')):
        """
        Get between 1 and 6 measurements. All measurements are taken at a single
        instant, unlike using properties like :attr:`.r` and :attr:`.theta`,
        which retrieve each measurement in sequence.

        Possible measurement types are 'X', 'Y', 'R', 'THETA', 'AUX1', 'AUX2',
        'AUX3', 'AUX4', 'FREQ', 'CH1' (channel 1 display value) and 'CH2'
        (channel 2 display value).

        Implements the SR830's SNAP command.

        :param measurements: A list of measurements to get. Must be between 2
            and 6 values, inclusively.
        :return: A dictionary of the requested measurements. For example, for
            a call ``get_measurements(['R', 'THETA'])``, the return value will
            look like ``{'R': 0.01004, 'THETA': 30.445}``.
        """
        if len(measurements) < 2 or len(measurements) > 6:
            raise ValueError("Must request between 2 and 6 measurements")
        try:
            meas_args_s = ','.join(
                str(self.SNAP_VALUES.index(meas.upper())) for meas in measurements)
        except ValueError as e:
            raise ValueError("Invalid measurement string") from e
        except AttributeError as e:
            raise ValueError("Invalid measurement: must be list of strings") from e
        values = self.values("SNAP?{}".format(meas_args_s))
        value_dict = {}
        for name, value in zip(measurements, values):
            value_dict[name.upper()] = value
        return value_dict


    def auto_gain(self):
        self.write("AGAN")


    def auto_reserve(self):
        self.write("ARSV")


    def auto_phase(self):
        self.write("APHS")


    def auto_offset(self, channel):
        """ Offsets the channel (X, Y, or R) to zero """
        if channel not in self.CHANNELS:
            raise ValueError('SR830 channel is invalid')
        channel = self.CHANNELS.index(channel) + 1
        self.write("AOFF %d" % channel)


    def get_scaling(self, channel):
        """ Returns the offset percent and the expansion term
        that are used to scale the channel in question
        """
        if channel not in self.CHANNELS:
            raise ValueError('SR830 channel is invalid')
        channel = self.CHANNELS.index(channel) + 1
        offset, expand = self.ask("OEXP? %d" % channel).split(',')
        return float(offset), self.EXPANSION_VALUES[int(expand)]


    def set_scaling(self, channel, precent, expand=0):
        """ Sets the offset of a channel (X=1, Y=2, R=3) to a
        certain percent (-105% to 105%) of the signal, with
        an optional expansion term (0, 10=1, 100=2)
        """
        if channel not in self.CHANNELS:
            raise ValueError('SR830 channel is invalid')
        channel = self.CHANNELS.index(channel) + 1
        expand = discreteTruncate(expand, self.EXPANSION_VALUES)
        self.write("OEXP %i,%.2f,%i" % (channel, precent, expand))


    def output_conversion(self, channel):
        """ Returns a function that can be used to determine
        the signal from the channel output (X, Y, or R), given the currently
        configured offset/expand and sensitivity.
        """
        offset, expand = self.get_scaling(channel)
        sensitivity = self.sensitivity
        return lambda x: (x/(10.*expand) + offset) * sensitivity


    @property
    def sample_frequency(self):
        """ Gets the data storage sample frequency in Hz """
        index = int(self.ask("SRAT?"))
        if index is 14:
            return None  # Trigger
        else:
            return SR830.SAMPLE_FREQUENCIES[index]


    @sample_frequency.setter
    def sample_frequency(self, frequency):
        """Sets the data storage sample frequency in Hz (``None`` is Trigger)"""
        assert type(frequency) in [float, int, type(None)]
        if frequency is None:
            index = 14  # Trigger
        else:
            frequency = discreteTruncate(frequency, SR830.SAMPLE_FREQUENCIES)
            index = SR830.SAMPLE_FREQUENCIES.index(frequency)
        self.write("SRAT%f" % index)


    def acquire_on_trigger(self, enable=True):
        self.write("TSTR%d" % enable)


    def enable_lia_status(self, input_=None, filter_=None, output=None,
        unlock=None, range_=None, time_constant=None, storage_triggered=None):
        """
        Set whether or not to report various lock-in status conditions. For all
        parameters, a ``None`` value will be left unchanged, while ``True`` will
        enable and ``False`` will disable reporting.

        :param input_: :meth:`~.is_input_overload`
        :param filter_: :meth:`~.is_filter_overload`
        :param output: :meth:`~.is_output_overload`
        :param unlock: :meth:`~.is_ref_unlocked`
        :param range_: :meth:`~.is_freq_range_changed`
        :param time_constant: :meth:`~.is_time_constant_changed`
        :param storage_triggered: :meth:`~.is_data_storage_triggered`
        """
        cmd = "LIAE %d,%d"
        values = (input_, filter_, output, unlock,
                  range_, time_constant, storage_triggered)
        for i, v in enumerate(values):
            if v is not None:
                self.write(cmd % (i, 1 if v else 0))


    def is_input_overload(self):
        """
        Return True if an input or amplifier overload has been detected.
        The detection status is cleared on the instrument.
        """
        try:
            return int(self.ask("LIAS?0")) is 1
        except ValueError:
            return False


    def is_filter_overload(self):
        """
        Return True if a filter overload has been detected.
        The detection status is cleared on the instrument.
        """
        try:
            return int(self.ask("LIAS?1")) is 1
        except ValueError:
            return False


    def is_output_overload(self):
        """
        Return True if an output measurement overload has been detected.
        The detection status is cleared on the instrument.
        """
        try:
            return int(self.ask("LIAS?2")) is 1
        except ValueError:
            return False


    def is_ref_unlocked(self):
        """
        Return True if the PLL failed to lock to the reference since last check.
        The detection status is cleared on the instrument.
        """
        try:
            return int(self.ask("LIAS?3")) is 1
        except ValueError:
            return False


    def is_freq_range_changed(self):
        """
        Return True if a frequency range transition has occurred since last
        check (above or below approximately 200 Hz). Sync filtering and time
        constants > 30s are disabled in the upper range.
        The detection status is cleared on the instrument.
        """
        try:
            return int(self.ask("LIAS?4")) is 1
        except ValueError:
            return False


    def is_time_constant_changed(self):
        """
        Return True if the time constant was automatically changed
        (e.g. due to frequency, dynamic reserve, etc. changes) since the
        last check.
        The detection status is cleared on the instrument.
        """
        try:
            return int(self.ask("LIAS?5")) is 1
        except ValueError:
            return False


    def is_data_storage_triggered(self):
        """
        Return True if data storage was triggered since last check.
        The detection status is cleared on the instrument.
        """
        try:
            return int(self.ask("LIAS?6")) is 1
        except ValueError:
            return False


    def is_out_of_range(self):
        """
        .. deprecated:: 0.6
           Use :meth:`~.is_output_overload()`
        """
        try:
            return self.is_output_overload()
        except ValueError:
            return False


    def quick_range(self):
        """
        While the magnitude is out of range, increase
        the sensitivity by one setting
        """
        while self.is_output_overload():
            self.write("SENS%d" % (int(self.ask("SENS?"))+1))
            time.sleep(5.0*self.time_constant)
            self.write("*CLS")
        # Set the range as low as possible
        self.sensitivity(1.15*abs(self.R))


    @property
    def buffer_count(self):
        query = self.ask("SPTS?")
        if query.count("\n") > 1:
            return int(re.match(r"\d+\n$", query, re.MULTILINE).group(0))
        else:
            return int(query)


    def fill_buffer(self, count, has_aborted=lambda: False, delay=0.001):
        ch1 = np.empty(count, np.float32)
        ch2 = np.empty(count, np.float32)
        currentCount = self.buffer_count
        index = 0
        while currentCount < count:
            if currentCount > index:
                ch1[index:currentCount] = self.buffer_data(1, index, currentCount)
                ch2[index:currentCount] = self.buffer_data(2, index, currentCount)
                index = currentCount
                time.sleep(delay)
            currentCount = self.buffer_count
            if has_aborted():
                self.pause_buffer()
                return ch1, ch2
        self.pauseBuffer()
        ch1[index:count+1] = self.buffer_data(1, index, count)
        ch2[index:count+1] = self.buffer_data(2, index, count)
        return ch1, ch2


    def buffer_measure(self, count, stopRequest=None, delay=1e-3):
        self.write("FAST0;STRD")
        ch1 = np.empty(count, np.float64)
        ch2 = np.empty(count, np.float64)
        currentCount = self.buffer_count
        index = 0
        while currentCount < count:
            if currentCount > index:
                ch1[index:currentCount] = self.buffer_data(1, index, currentCount)
                ch2[index:currentCount] = self.buffer_data(2, index, currentCount)
                index = currentCount
                time.sleep(delay)
            currentCount = self.buffer_count
            if stopRequest is not None and stopRequest.isSet():
                self.pauseBuffer()
                return (0, 0, 0, 0)
        self.pauseBuffer()
        ch1[index:count] = self.buffer_data(1, index, count)
        ch2[index:count] = self.buffer_data(2, index, count)
        return (ch1.mean(), ch1.std(), ch2.mean(), ch2.std())


    def pause_buffer(self):
        self.write("PAUS")


    def start_buffer(self, fast=False):
        if fast:
            self.write("FAST2;STRD")
        else:
            self.write("FAST0;STRD")


    def wait_for_buffer(self, count, has_aborted=lambda: False,
                        timeout=60, timestep=0.01):
        """ Wait for the buffer to fill a certain count
        """
        i = 0
        while not self.buffer_count >= count and i < (timeout / timestep):
            time.sleep(timestep)
            i += 1
            if has_aborted():
                return False
        self.pauseBuffer()


    def get_buffer(self, channel=1, start=0, end=None):
        """ Acquires the 32 bit floating point data through binary transfer
        """
        if end is None:
            end = self.buffer_count
        return self.binary_values("TRCB?%d,%d,%d" % (
                        channel, start, end-start))


    def reset_buffer(self):
        self.write("REST")


    def trigger(self):
        self.write("TRIG")

SR830.aquireOnTrigger = SR830.acquire_on_trigger # for backwards compatibility
