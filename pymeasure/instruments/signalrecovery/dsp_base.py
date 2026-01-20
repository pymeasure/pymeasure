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

# =============================================================================
# Libraries / modules
# =============================================================================

import logging
from time import sleep, time
import numpy as np
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import modular_range_bidirectional
from pymeasure.instruments.validators import strict_discrete_set
from pymeasure.instruments.validators import strict_range

# =============================================================================
# Logging
# =============================================================================

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# =============================================================================
# Instrument file
# =============================================================================


class DSPBase(Instrument):
    """This is the base class for the Signal Recovery DSP 72XX lock-in
    amplifiers.

    Do not directly instantiate an object with this class. Use one of the
    DSP 72XX series instrument classes that inherit from this parent
    class. Floating point command mode (i.e., the inclusion of the ``.``
    character in commands) is included for usability.

    Untested commands are noted in docstrings.
    """

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Constants
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    SENSITIVITIES = [
        np.nan, 2.0e-9, 5.0e-9, 10.0e-9, 20.0e-9, 50.0e-9, 100.0e-9,
        200.0e-9, 500.0e-9, 1.0e-6, 2.0e-6, 5.0e-6, 10.0e-6,
        20.0e-6, 50.0e-6, 100.0e-6, 200.0e-6, 500.0e-6, 1.0e-3,
        2.0e-3, 5.0e-3, 10.0e-3, 20.0e-3, 50.0e-3, 100.0e-3,
        200.0e-3, 500.0e-3, 1.0
    ]
    SEN_MULTIPLIER = [1, 1e-6, 1e-8]

    TIME_CONSTANTS = [
        10.0e-6, 20.0e-6, 40.0e-6, 80.0e-6, 160.0e-6, 320.0e-6,
        640.0e-6, 5.0e-3, 10.0e-3, 20.0e-3, 50.0e-3, 100.0e-3,
        200.0e-3, 500.0e-3, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0,
        100.0, 200.0, 500.0, 1.0e3, 2.0e3, 5.0e3, 10.0e3,
        20.0e3, 50.0e3
    ]
    REFERENCES = ['internal', 'external rear', 'external front']
    IMODES = ['voltage mode', 'current mode', 'low noise current mode']

    CURVE_BITS = ['x', 'y', 'magnitude', 'phase', 'sensitivity', 'adc1',
                  'adc2', 'dac1', 'dac2', 'noise', 'ratio', 'log ratio',
                  'event', 'frequency part 1', 'frequency part 2',
                  # Dual modes
                  'x2', 'y2', 'magnitude2', 'phase2', 'sensitivity2']

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Initializer and important communication methods
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self, adapter, name="Signal Recovery DSP 72XX Base", **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            **kwargs
        )

    def read(self, **kwargs):
        """Read the response and remove extra unicode character from instrument readings."""
        return super().read(**kwargs).replace('\x00', '')

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Properties
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    id = Instrument.measurement(
        "ID",
        """Measure the model number of the instrument.

        Returned value is an integer.""",
        cast=int
    )

    imode = Instrument.control(
        "IMODE", "IMODE %d",
        """Control the lock-in amplifier to detect a voltage or current
        signal.

        Valid values are ``voltage mode, ``current mode``, or ``low noise current mode``.
        """,
        validator=strict_discrete_set,
        values=IMODES,
        map_values=True
    )

    slope = Instrument.control(
        "SLOPE", "SLOPE %d",
        """Control the low-pass filter roll-off.

        Valid values are the integers 6, 12, 18, or 24, which represents the
        slope of the low-pass filter in dB/octave.
        """,
        validator=strict_discrete_set,
        values=[6, 12, 18, 24],
        map_values=True
    )

    time_constant = Instrument.control(
        "TC", "TC %d",
        """Control the filter time constant.

        Valid values are a strict set of time constants from 10 us to 50,000 s.
        Returned values are floating point numbers in seconds.
        """,
        validator=strict_discrete_set,
        values=TIME_CONSTANTS,
        map_values=True
    )

    shield = Instrument.control(
        "FLOAT", "FLOAT %d",
        """Control the input connector shield state.

        Valid values are 0 to have shields grounded or 1 to have the shields
        floating (i.e., connected to ground via a 1 kOhm resistor).
        """,
        validator=strict_discrete_set,
        values=[0, 1]
    )

    fet = Instrument.control(
        "FET", "FET %d",
        """Control the voltage preamplifier transistor type.

        Valid values are 0 for bipolar or 1 for FET.
        """,
        validator=strict_discrete_set,
        values=[0, 1]
    )

    coupling = Instrument.control(
        "CP", "CP %d",
        """Control the input coupling mode.

        Valid values are 0 for AC coupling mode or 1 for DC coupling mode.
        """,
        validator=strict_discrete_set,
        values=[0, 1]
    )

    voltage = Instrument.control(
        "OA.", "OA. %g",
        """Control the oscillator amplitude.

        Valid values are floating point numbers between 0 to 5 V.
        """,
        validator=strict_range,
        values=[0, 5]
    )

    frequency = Instrument.control(
        "OF.", "OF. %g",
        """Control the oscillator frequency.

        Valid values are floating point numbers representing the frequency in Hz.
        """,
        validator=strict_range,
        values=[0, 2.5e5],
        dynamic=True
    )

    reference = Instrument.control(
        "IE", "IE %d",
        """Control the oscillator reference input mode.

        Valid values are ``internal``, ``external rear`` or ``external front``.
        """,
        validator=strict_discrete_set,
        values=REFERENCES,
        map_values=True
    )

    harmonic = Instrument.control(
        "REFN", "REFN %d",
        """Control the reference harmonic mode.

        Valid values are integers.
        """,
        validator=strict_range,
        values=[1, 65535],
        dynamic=True
    )

    reference_phase = Instrument.control(
        "REFP.", "REFP. %g",
        """Control the reference absolute phase angle.

        Valid values are floating point numbers between 0 - 360 degrees.
         """,
        validator=modular_range_bidirectional,
        values=[0, 360]
    )

    dac1 = Instrument.control(
        "DAC. 1", "DAC. 1 %g",
        """Control the voltage of the DAC1 output on the rear panel.

        Valid values are floating point numbers between -12 to 12 V.
        """,
        validator=strict_range,
        values=[-12, 12]
    )

    dac2 = Instrument.control(
        "DAC. 2", "DAC. 2 %g",
        """Control the voltage of the DAC2 output on the rear panel.

        Valid values are floating point numbers between -12 to 12 V.
        """,
        validator=strict_range,
        values=[-12, 12]
    )

    @property
    def gain(self):
        """Control the AC gain of signal channel amplifier."""
        return self.values("ACGAIN")

    @gain.setter
    def gain(self, value):
        value = strict_discrete_set(int(value / 10), list(range(0, 10)))
        self.write("ACGAIN %d" % value)

    @property
    def sensitivity(self):
        """Control the signal's measurement sensitivity range.

        When in voltage measurement mode, valid values are discrete values from
        2 nV to 1 V. When in current measurement mode, valid values are
        discrete values from 2 fA to 1 µA (for normal current mode) or up to
        10 nA (for low noise current mode).
        """
        return self.values("SEN.")[0]

    @sensitivity.setter
    def sensitivity(self, value):
        # get the voltage/current mode:
        imode = self.IMODES.index(self.imode)

        # Scale the sensitivities to the correct range for voltage/current mode
        sensitivities = [s * self.SEN_MULTIPLIER[imode]
                         for s in self.SENSITIVITIES]
        if imode == 2:
            sensitivities[0:7] = [np.nan] * 7

        # Check and map the value
        value = strict_discrete_set(value, sensitivities)
        value = sensitivities.index(value)

        # Set sensitivity
        self.write("SEN %d" % value)

    @property
    def auto_gain(self):
        """Control lock-in amplifier for automatic AC gain."""
        return int(self.values("AUTOMATIC")) == 1

    @auto_gain.setter
    def auto_gain(self, value):
        if value:
            self.write("AUTOMATIC 1")
        else:
            self.write("AUTOMATIC 0")

    x = Instrument.measurement(
        "X.",
        """Measure the output signal's X channel.

        Returned value is a floating point number in volts.
        """
    )

    y = Instrument.measurement(
        "Y.",
        """Measure the output signal's Y channel.

        Returned value is a floating point number in volts.
        """
    )

    xy = Instrument.measurement(
        "XY.",
        """Measure both the X and Y channels.

        Returned values are floating point numbers in volts.
        """
    )

    mag = Instrument.measurement(
        "MAG.",
        """Measure the magnitude of the signal.

        Returned value is a floating point number in volts.
        """
    )

    phase = Instrument.measurement(
        "PHA.",
        """Measure the signal's absolute phase angle.

        Returned value is a floating point number in degrees.
        """
    )

    adc1 = Instrument.measurement(
        "ADC. 1",
        """Measure the voltage of the ADC1 input on the rear panel.

        Returned value is a floating point number in volts.
        """
    )

    adc2 = Instrument.measurement(
        "ADC. 2",
        """Measure the voltage of the ADC2 input on the rear panel.

        Returned value is a floating point number in volts.
        """
    )

    ratio = Instrument.measurement(
        "RT.",
        """Measure the ratio between the X channel and ADC1.

        Returned value is a unitless floating point number equivalent to the
        mathematical expression X/ADC1.
        """
    )

    log_ratio = Instrument.measurement(
        "LR.",
        """
        Measure the log (base 10) of the ratio between the X channel and ADC1.

        Returned value is a unitless floating point number equivalent to the
        mathematical expression log(X/ADC1).
        """
    )

    curve_buffer_bits = Instrument.control(
        "CBD", "CBD %d",
        """Control which data outputs are stored in the curve buffer.

        Valid values are values are integers between 1 and 65,535 (or 2,097,151
        in dual reference mode).
        """,
        values=[1, 2097151],
        validator=strict_range,
        cast=int,
        dynamic=True
    )

    curve_buffer_length = Instrument.control(
        "LEN", "LEN %d",
        """Control the length of the curve buffer.

        Valid values are integers between 1 and 32,768, but the actual maximum
        amount of points is determined by the amount of curves that are stored,
        as set via the curve_buffer_bits property (32,768 / n).
        """,
        values=[1, 32768],
        validator=strict_range,
        cast=int
    )

    curve_buffer_interval = Instrument.control(
        "STR", "STR %d",
        """Control the time interval between the collection of successive
        points in the curve buffer.

        Valid values to the time interval are integers in ms with a
        resolution of 5 ms; input values are rounded up to a multiple of 5.
        Valid values are values between 0 and 1,000,000,000 (corresponding to
        12 days). The interval may be set to 0, which sets the rate of data
        storage to the curve buffer to 1.25 ms/point (800 Hz). However this
        only allows storage of the X and Y channel outputs. There is no need to
        issue a CBD 3 command to set this up since it happens automatically
        when acquisition starts.
        """,
        values=[1, 1000000000],
        validator=strict_range,
        cast=int
    )

    curve_buffer_status = Instrument.measurement(
        "M",
        """Measure the status of the curve buffer acquisition.

        Command returns four values:
        **First value - Curve Acquisition Status:** Number with 5 possibilities:
        0: no activity
        1: acquisition via TD command running
        2: acquisition by a TDC command running
        5: acquisition via TD command halted
        6: acquisition bia TDC command halted
        **Second value - Number of Sweeps Acquired**: Number of sweeps already
        acquired.
        **Third value - Status Byte:** Decimal representation of the status byte
        (the same response as the ST command
        **Fourth value - Number of Points Acquired:** Number of points acquired
        in the curve buffer.
        """,
        cast=int,
    )

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Methods
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def set_voltage_mode(self):
        """Sets lock-in amplifier to measure a voltage signal."""
        self.write("IMODE 0")

    def setDifferentialMode(self, lineFiltering=True):
        """Sets lock-in amplifier to differential mode, measuring A-B."""
        self.write("VMODE 3")
        self.write("LF %d 0" % (3 if lineFiltering else 0))

    def setChannelAMode(self):
        """Sets lock-in amplifier to measure a voltage signal only from the A
        input connector.
        """
        self.write("VMODE 1")

    def auto_sensitivity(self):
        """Adjusts the full-scale sensitivity so signal's magnitude lies
        between 30 - 90 % of full-scale.
        """
        self.write("AS")

    def auto_phase(self):
        """Adjusts the reference absolute phase to maximize the X channel
        output and minimize the Y channel output signals.
        """
        self.write("AQN")

    def init_curve_buffer(self):
        """Initializes the curve storage memory and status variables. All
        record of previously taken curves is removed.
        """
        self.write("NC")

    def set_buffer(self, points, quantities=None, interval=10.0e-3):
        """Prepares the curve buffer for a measurement.

        :param int points:
            Number of points to be recorded in the curve buffer

        :param list quantities:
            List containing the quantities (strings) that are to be
            recorded in the curve buffer, can be any of:
            'x', 'y', 'magnitude', 'phase', 'sensitivity', 'adc1', 'adc2',
            'adc3', 'dac1', 'dac2',
            'noise', 'ratio', 'log ratio', 'event', 'frequency'
            (or 'frequency part 1' and 'frequency part 2');
            for both dual modes, additional options are:
            'x2', 'y2', 'magnitude2', 'phase2', 'sensitivity2'.
            Default is 'x' and 'y'.

        :param float interval:
            The interval between two subsequent points stored in the
            curve buffer in s. Default is 10 ms.
        """

        if quantities is None:
            quantities = ["x", "y"]

        if "frequency" in quantities:
            quantities.remove("frequency")
            quantities.extend([
                "frequency part 1",
                "frequency part 2"
            ])

        # remove all possible duplicates
        quantities = list({q.lower() for q in quantities})

        bits = 0
        for q in quantities:
            bits += 2 ** self.CURVE_BITS.index(q)

        self.curve_buffer_bits = bits
        self.curve_buffer_length = points

        self.curve_buffer_interval = int(interval * 1000)
        self.init_curve_buffer()

    def start_buffer(self):
        """Initiates data acquisition. Acquisition starts at the current
        position in the curve buffer and continues at the rate set by the STR
        command until the buffer is full.
        """
        self.write("TD")

    def wait_for_buffer(self, timeout=None, delay=0.1):
        """ Method that waits until the curve buffer is filled
        """
        start = time()
        while self.curve_buffer_status[0] == 1:
            sleep(delay)
            if timeout is not None and time() < start + timeout:
                break

    def get_buffer(self, quantity=None,
                   convert_to_float=True, wait_for_buffer=True):
        """Retrieves the buffer after it has been filled. The data retrieved
        from the lock-in is in a fixed-point format, which requires translation
        before it can be interpreted as meaningful data. When
        `convert_to_float` is True the conversion is performed (if possible)
        before returning the data.

        :param str quantity:
            If provided, names the quantity that is to be retrieved from the
            curve buffer; can be any of:
            'x', 'y', 'magnitude', 'phase', 'sensitivity', 'adc1', 'adc2',
            'adc3', 'dac1', 'dac2', 'noise', 'ratio', 'log ratio', 'event',
            'frequency part 1' and 'frequency part 2';
            for both dual modes, additional options are:
            'x2', 'y2', 'magnitude2', 'phase2', 'sensitivity2'.
            If no quantity is provided, all available data is retrieved.

        :param bool convert_to_float:
            Bool that determines whether to convert the fixed-point buffer-data
            to meaningful floating point values via the `buffer_to_float`
            method. If True, this method tries to convert all the available
            data to meaningful values; if this is not possible, an exception
            will be raised. If False, this conversion is not performed and the
            raw buffer-data is returned.

        :param bool wait_for_buffer:
            Bool that determines whether to wait for the data acquisition to
            finished if this method is called before the acquisition is
            finished. If True, the method waits until the buffer is filled
            before continuing; if False, the method raises an exception if the
            acquisition is not finished when the method is called.
        """

        # Check if buffer is finished
        if self.curve_buffer_status[0] != 0:
            if wait_for_buffer:
                self.wait_for_buffer()
            else:
                raise RuntimeError("Buffer acquisition is not yet finished.")

        # Check which quantities are recorded in the buffer
        bits = format(self.curve_buffer_bits, '021b')[::-1]
        quantity_enums = [e for e, b in enumerate(bits) if b == "1"]

        # Check if the provided quantity (if any) is indeed recorded
        if quantity is not None:
            if self.CURVE_BITS.index(quantity) in quantity_enums:
                quantity_enums = [self.CURVE_BITS.index(quantity)]
            else:
                raise KeyError("The selected quantity '%s' is not recorded;"
                               "quantity should be one of: %s" % (
                                   quantity, ", ".join(
                                       [self.CURVE_BITS[q] for q in quantity_enums]
                                   )))

        # Retrieve the data
        data = {}
        for enum in quantity_enums:
            self.write("DC %d" % enum)
            q_data = []

            while True:
                stb = format(self.adapter.connection.read_stb(), '08b')[::-1]

                if bool(int(stb[2])):
                    raise ValueError("Status byte reports command parameter error.")

                if bool(int(stb[0])):
                    break

                if bool(int(stb[7])):
                    q_data.append(int(self.read().strip()))

            data[self.CURVE_BITS[enum]] = np.array(q_data)

        if convert_to_float:
            data = self.buffer_to_float(data)

        if quantity is not None:
            data = data[quantity]

        return data

    def buffer_to_float(self, buffer_data, sensitivity=None,
                        sensitivity2=None, raise_error=True):
        """Converts fixed-point buffer data to floating point data.

        The provided data is converted as much as possible, but there are some
        requirements to the data if all provided columns are to be converted;
        if a key in the provided data cannot be converted it will be omitted in
        the returned data or an exception will be raised, depending on the
        value of raise_error.

        The requirements for converting the data are as follows:

        - Converting X, Y, magnitude and noise requires sensitivity data, which
          can either be part of the provided data or can be provided via the
          sensitivity argument
        - The same holds for X2, Y2 and magnitude2 with sensitivity2.
        - Converting the frequency requires both 'frequency part 1' and
          'frequency part 2'.

        :param dict buffer_data:
            The data to be converted. Must be in the format as returned by the
            `get_buffer` method: a dict of numpy arrays.

        :param sensitivity:
            If provided, the sensitivity used to convert X, Y, magnitude and
            noise. Can be provided as a float or as an array that matches the
            length of elements in `buffer_data`. If both a sensitivity is
            provided and present in the buffer_data, the provided value is used
            for the conversion, but the sensitivity in the buffer_data is
            stored in the returned dict.

        :param sensitivity2:
            Same as the first sensitivity argument, but for X2, Y2, magnitude2
            and noise2.

        :param bool raise_error:
            Determines whether an exception is raised in case not all keys
            provided in buffer_data can be converted. If False, the columns
            that cannot be converted are omitted in the returned dict.

        :return: Floating-point buffer data
        :rtype: dict
        """

        data = {}

        def maybe_raise(message):
            if raise_error:
                raise ValueError(message)

        def convert_if_present(keys, multiply_by=1):
            """Copy any available entries from buffer_data to data, scale with
            multiply_by.
            """
            for key in keys:
                if key in buffer_data:
                    data[key] = buffer_data[key] * multiply_by

        # Sensitivity (for both single and dual modes)
        for key in ["sensitivity", "sensitivity2"]:
            if key in buffer_data:
                data[key] = np.array([
                    self.SENSITIVITIES[v % 32] * self.SEN_MULTIPLIER[v // 32]
                    for v in buffer_data[key]
                ])
        # Try to set sensitivity values from arg or data
        sensitivity = sensitivity or data.get('sensitivity', None)
        sensitivity2 = sensitivity2 or data.get('sensitivity2', None)

        if any(["x" in buffer_data,
                "y" in buffer_data,
                "magnitude" in buffer_data,
                "noise" in buffer_data, ]):
            if sensitivity is None:
                maybe_raise("X, Y, magnitude and noise cannot be converted as "
                            "no sensitivity is provided, neither as argument "
                            "nor as part of the buffer_data. ")
            else:
                convert_if_present(["x", "y", "magnitude", "noise"], sensitivity / 10000)

        # phase data (for both single and dual modes)
        convert_if_present(["phase", "phase2"], 1 / 100)

        # frequency data from frequency part 1 and 2
        if "frequency part 1" in buffer_data or "frequency part 2" in buffer_data:
            if "frequency part 1" in buffer_data and "frequency part 2" in buffer_data:
                data["frequency"] = np.array([
                    int(format(v2, "016b") + format(v1, "016b"), 2) / 1000 for
                    v1, v2 in zip(buffer_data["frequency part 1"], buffer_data["frequency part 2"])
                ])
            else:
                maybe_raise("Can calculate the frequency only when both"
                            "frequency part 1 and 2 are provided.")

        # conversion for, adc1, adc2, dac1, dac2, ratio, and log ratio
        convert_if_present(["adc1", "adc2", "dac1",
                            "dac2", "ratio", "log ratio"], 1 / 1000)

        # adc3 (integrating converter); requires a call to adc3_time
        if "adc3" in buffer_data:
            data["adc3"] = buffer_data["adc3"] / (50000 * self.adc3_time)

        # event does not require a conversion
        convert_if_present(["event"])

        # X, Y, and magnitude data for both dual modes
        if any(["x2" in buffer_data,
                "y2" in buffer_data,
                "magnitude2" in buffer_data, ]):
            if sensitivity2 is None:
                maybe_raise("X2, Y2 and magnitude2 cannot be converted as no "
                            "sensitivity2 is provided, neither as argument nor "
                            "as part of the buffer_data. ")
            else:
                convert_if_present(["x2", "y2", "magnitude2"], sensitivity2 / 10000)

        return data

    def shutdown(self):
        """Safely shutdown the lock-in amplifier.

        Sets oscillator amplitude to 0 V and AC gain to 0 dB.
        """
        log.info("Shutting down %s." % self.name)
        self.voltage = 0.
        self.gain = 0.
        super().shutdown()
