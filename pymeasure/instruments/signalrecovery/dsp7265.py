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
from time import sleep, time

import numpy as np

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_discrete_set, truncated_range, \
    modular_range_bidirectional, strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DSP7265(Instrument):
    """This is the class for the DSP 7265 lockin amplifier"""

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
                  'adc2', 'adc3', 'dac1', 'dac2', 'noise', 'ratio', 'log ratio',
                  'event', 'frequency part 1', 'frequency part 2',
                  # Dual modes
                  'x2', 'y2', 'magnitude2', 'phase2', 'sensitivity2']

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Signal Recovery DSP 7265",
            includeSCPI=False,
            # Remove extra unicode character
            preprocess_reply=lambda r: r.replace('\x00', ''),
            **kwargs
        )

    voltage = Instrument.control(
        "OA.", "OA. %g",
        """ A floating point property that represents the voltage
        in Volts. This property can be set. """,
        validator=truncated_range,
        values=[0, 5]
    )
    frequency = Instrument.control(
        "OF.", "OF. %g",
        """ A floating point property that represents the lock-in
        frequency in Hz. This property can be set. """,
        validator=truncated_range,
        values=[0, 2.5e5]
    )
    dac1 = Instrument.control(
        "DAC. 1", "DAC. 1 %g",
        """ A floating point property that represents the output
        value on DAC1 in Volts. This property can be set. """,
        validator=truncated_range,
        values=[-12, 12]
    )
    dac2 = Instrument.control(
        "DAC. 2", "DAC. 2 %g",
        """ A floating point property that represents the output
        value on DAC2 in Volts. This property can be set. """,
        validator=truncated_range,
        values=[-12, 12]
    )
    dac3 = Instrument.control(
        "DAC. 3", "DAC. 3 %g",
        """ A floating point property that represents the output
        value on DAC3 in Volts. This property can be set. """,
        validator=truncated_range,
        values=[-12, 12]
    )
    dac4 = Instrument.control(
        "DAC. 4", "DAC. 4 %g",
        """ A floating point property that represents the output
        value on DAC4 in Volts. This property can be set. """,
        validator=truncated_range,
        values=[-12, 12]
    )
    harmonic = Instrument.control(
        "REFN", "REFN %d",
        """ An integer property that represents the reference
        harmonic mode control, taking values from 1 to 65535.
        This property can be set. """,
        validator=truncated_discrete_set,
        values=list(range(65535))
    )
    reference_phase = Instrument.control(
        "REFP.", "REFP. %g",
        """ A floating point property that represents the reference
        harmonic phase in degrees. This property can be set. """,
        validator=modular_range_bidirectional,
        values=[0, 360]
    )
    x = Instrument.measurement("X.",
                               """ Reads the X value in Volts """
                               )
    y = Instrument.measurement("Y.",
                               """ Reads the Y value in Volts """
                               )
    xy = Instrument.measurement("XY.",
                                """ Reads both the X and Y values in Volts """
                                )
    mag = Instrument.measurement("MAG.",
                                 """ Reads the magnitude in Volts """
                                 )
    phase = Instrument.measurement("PHA.",
                                   """ Reads the phase in degrees """
                                   )
    adc1 = Instrument.measurement("ADC. 1",
                                  """ Reads the input value of ADC1 in Volts """
                                  )
    adc2 = Instrument.measurement("ADC. 2",
                                  """ Reads the input value of ADC2 in Volts """
                                  )
    id = Instrument.measurement("ID",
                                """ Reads the instrument identification """
                                )
    ratio = Instrument.measurement("RT.",
                                   """ Reads the ratio output, defined as X/ADC1 """
                                   )
    log_ratio = Instrument.measurement("LR.",
                                       """ Reads the log ratio output, defined as log(X/ADC1) """
                                       )
    reference = Instrument.control(
        "IE", "IE %d",
        """Controls the oscillator reference. Can be "internal",
        "external rear" or "external front" """,
        validator=strict_discrete_set,
        values=REFERENCES,
        map_values=True
    )

    @property
    def sensitivity(self):
        """ A floating point property that controls the sensitivity
        range in Volts (for voltage mode) or Amps (for current modes).
        When in Volts it takes discrete values from 2 nV to 1 V. When in
        Amps it takes discrete values from 2 fA to 1 µA (for normal current
        mode) or up to 10 nA (for low noise current mode).
        This property can be set. """
        return self.values("SEN.")[0]

    @sensitivity.setter
    def sensitivity(self, value):
        # get the voltage/current mode:
        imode = self.IMODES.index(self.imode)

        # Scale the sensitivities to the correct range for voltage/current mode
        sensitivities = [s * self.SEN_MULTIPLIER[imode] for s in self.SENSITIVITIES]
        if imode == 2:
            sensitivities[0:7] = [np.nan] * 7

        # Check and map the value
        value = truncated_discrete_set(value, sensitivities)
        print(value)
        value = sensitivities.index(value)

        # Set sensitivity
        self.write("SEN %d" % value)

    imode = Instrument.control(
        "IMODE", "IMODE %d",
        """ Property that controls the voltage/current mode. can be
        'voltage mode', 'current mode', or 'low noise current mode' """,
        validator=strict_discrete_set,
        values=IMODES,
        map_values=True
    )
    slope = Instrument.control(
        "SLOPE", "SLOPE %d",
        """ A integer property that controls the filter slope in
        dB/octave, which can take the values 6, 12, 18, or 24 dB/octave.
        This property can be set. """,
        validator=truncated_discrete_set,
        values=[6, 12, 18, 24],
        map_values=True
    )
    time_constant = Instrument.control(
        "TC", "TC %d",
        """ A floating point property that controls the time constant
        in seconds, which takes values from 10 microseconds to 50,000
        seconds. This property can be set. """,
        validator=truncated_discrete_set,
        values=TIME_CONSTANTS,
        map_values=True
    )

    def set_voltage_mode(self):
        self.write("IMODE 0")

    def setDifferentialMode(self, lineFiltering=True):
        """Sets lockin to differential mode, measuring A-B"""
        self.write("VMODE 3")
        self.write("LF %d 0" % 3 if lineFiltering else 0)

    def setChannelAMode(self):
        self.write("VMODE 1")

    @property
    def adc3(self):
        # 50,000 for 1V signal over 1 s
        integral = self.values("ADC 3")[0]
        return integral / (50000.0 * self.adc3_time)

    @property
    def adc3_time(self):
        # Returns time in seconds
        return self.values("ADC3TIME")[0] / 1000.0

    @adc3_time.setter
    def adc3_time(self, value):
        # Takes time in seconds
        self.write("ADC3TIME %g" % int(1000 * value))
        sleep(value * 1.2)

    @property
    def auto_gain(self):
        return (int(self.values("AUTOMATIC")) == 1)

    @auto_gain.setter
    def auto_gain(self, value):
        if value:
            self.write("AUTOMATIC 1")
        else:
            self.write("AUTOMATIC 0")

    def auto_sensitivity(self):
        self.write("AS")

    def auto_phase(self):
        self.write("AQN")

    @property
    def gain(self):
        return self.values("ACGAIN")

    @gain.setter
    def gain(self, value):
        self.write("ACGAIN %d" % int(value / 10.0))

    curve_buffer_bits = Instrument.control(
        "CBD", "CBD %d",
        """ An integer property that controls which data outputs are stored
        in the curve buffer. Valid values are values between 1 and 65,535 (or
        2,097,151 in dual reference mode). """,
        values=[1, 2097151],
        validator=truncated_range,
        cast=int,
    )

    curve_buffer_length = Instrument.control(
        "LEN", "LEN %d",
        """ An integer property that controls the length of the curve buffer.
        Valid values are values between 1 and 32,768, but the actual maximum
        amount of points is determined by the amount of curves that are stored,
        as set via the curve_buffer_bits property (32,768 / n) """,
        values=[1, 32768],
        validator=truncated_range,
        cast=int,
    )

    curve_buffer_interval = Instrument.control(
        "STR", "STR %d",
        """ An integer property that controls Sets the time interval between
        successive points being acquired in the curve buffer. The time interval
        is specified in ms with a resolution of 5 ms; input values are rounded
        up to a multiple of 5. Valid values are values between 0 and 1,000,000,000
        (corresponding to 12 days).
        The interval may be set to 0, which sets the rate of data storage to the
        curve buffer to 1.25 ms/point (800 Hz). However this only allows storage
        of the X and Y channel outputs. There is no need to issue a CBD 3 command
        to set this up since it happens automatically when acquisition starts.
        """,
        values=[1, 1000000000],
        validator=truncated_range,
        cast=int,
    )

    curve_buffer_status = Instrument.measurement(
        "M",
        """ A property that represents the status of the curve buffer acquisition
        with four values:
        the first value represents the status with 5 possibilities (0: no activity,
        1: acquisition via TD command running, 2: acquisition bya TDC command running,
        5: acquisition via TD command halted, 6: acquisition bia TDC command halted);
        the second value is the number of sweeps that is acquired;
        the third value is the decimal representation of the status byte (the same
        response as the ST command;
        the fourth value is the number of points acquired in the curve buffer.
        """,
        cast=int,
    )

    def init_curve_buffer(self):
        """ Initializes the curve storage memory and status variables. All record
        of previously taken curves is removed.
        """
        self.write("NC")

    def set_buffer(self, points, quantities=None, interval=10.0e-3):
        """ Method that prepares the curve buffer for a measurement.

        :param int points:
            Number of points to be recorded in the curve buffer

        :param list quantities:
            List containing the quantities (strings) that are to be
            recorded in the curve buffer, can be any of:
            'x', 'y', 'magnitude', 'phase', 'sensitivity', 'adc1',
            'adc2', 'adc3', 'dac1', 'dac2', 'noise', 'ratio', 'log ratio',
            'event', 'frequency' (or 'frequency part 1' and 'frequency part 2');
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
            bits += 2**self.CURVE_BITS.index(q)

        self.curve_buffer_bits = bits
        self.curve_buffer_length = points

        self.curve_buffer_interval = int(interval * 1000)
        self.init_curve_buffer()

    def start_buffer(self):
        """ Initiates data acquisition. Acquisition starts at the current position
        in the curve buffer and continues at the rate set by the STR command until
        the buffer is full.
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

    def get_buffer(self, quantity=None, convert_to_float=True, wait_for_buffer=True):
        """ Method that retrieves the buffer after it has been filled. The data
        retrieved from the lock-in is in a fixed-point format, which requires
        translation before it can be interpreted as meaningful data. When
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
            Bool that determines whether to convert the fixed-point buffer-data to
            meaningful floating point values via the `buffer_to_float` method. If True,
            this method tries to convert all the available data to meaningful values;
            if this is not possible, an exception will be raised. If False, this
            conversion is not performed and the raw buffer-data is returned.

        :param bool wait_for_buffer:
            Bool that determines whether to wait for the data acquisition to finished
            if this method is called before the acquisition is finished. If True, the
            method waits until the buffer is filled before continuing; if False, the
            method raises an exception if the acquisition is not finished when the
            method is called.
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

    def buffer_to_float(self, buffer_data, sensitivity=None, sensitivity2=None, raise_error=True):
        """Method that converts fixed-point buffer data to floating point data.

        The provided data is converted as much as possible, but there are some requirements to the
        data if all provided columns are to be converted; if a key in the provided data cannot be
        converted it will be omitted in the returned data or an exception will be raised,
        depending on the value of raise_error.

        The requirements for converting the data are as follows:

        - Converting X, Y, magnitude and noise requires sensitivity data, which can either be part
          of the provided data or can be provided via the sensitivity argument
        - The same holds for X2, Y2 and magnitude2 with sensitivity2.
        - Converting the frequency requires both 'frequency part 1' and 'frequency part 2'.

        :param dict buffer_data:
            The data to be converted. Must be in the format as returned by the
            `get_buffer` method: a dict of numpy arrays.

        :param sensitivity:
            If provided, the sensitivity used to convert X, Y, magnitude and noise.
            Can be provided as a float or as an array that matches the length of elements in
            `buffer_data`. If both a sensitivity is provided and present in the buffer_data, the
            provided value is used for the conversion, but the sensitivity in the buffer_data is
            stored in the returned dict.

        :param sensitivity2:
            Same as the first sensitivity argument, but for X2, Y2, magnitude2 and noise2.

        :param bool raise_error:
            Determines whether an exception is raised in case not all keys provided in buffer_data
            can be converted. If False, the columns that cannot be converted are omitted in the
            returned dict.

        :return: Floating-point buffer data
        :rtype: dict
        """
        data = {}

        def maybe_raise(message):
            if raise_error:
                raise ValueError(message)

        def convert_if_present(keys, multiply_by=1):
            """Copy any available entries from buffer_data to data, scale with multiply_by.
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
                maybe_raise("X, Y, magnitude and noise cannot be converted as no "
                            "sensitivity is provided, neither as argument nor as "
                            "part of the buffer_data. ")
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
        convert_if_present(["adc1", "adc2", "dac1", "dac2", "ratio", "log ratio"], 1 / 1000)

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
                            "sensitivity2 is provided, neither as argument nor as "
                            "part of the buffer_data. ")
            else:
                convert_if_present(["x2", "y2", "magnitude2"], sensitivity2 / 10000)

        return data

    def shutdown(self):
        log.info("Shutting down %s." % self.name)
        self.voltage = 0.
        self.isShutdown = True
