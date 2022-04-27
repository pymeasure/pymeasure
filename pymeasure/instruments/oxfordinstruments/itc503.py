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
import numpy
from enum import IntFlag

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, \
    truncated_range, strict_range

from .adapters import OxfordInstrumentsAdapter


# Setup logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def pointer_validator(value, values):
    """ Provides a validator function that ensures the passed value is
    a tuple or a list with a length of 2 and passes every item through
    the strict_range validator.

    :param value: A value to test
    :param values: A range of values (passed to strict_range)
    :raises: TypeError if the value is not a tuple or a list
    :raises: IndexError if the value is not of length 2
    """

    if not isinstance(value, (list, tuple)):
        raise TypeError('{:g} is not a list or tuple'.format(value))
    if not len(value) == 2:
        raise IndexError('{:g} is not of length 2'.format(value))
    return tuple(strict_range(v, values) for v in value)


class ITC503(Instrument):
    """Represents the Oxford Intelligent Temperature Controller 503.

    .. code-block:: python

        itc = ITC503("GPIB::24")        # Default channel for the ITC503

        itc.control_mode = "RU"         # Set the control mode to remote
        itc.heater_gas_mode = "AUTO"    # Turn on auto heater and flow
        itc.auto_pid = True             # Turn on auto-pid

        print(itc.temperature_setpoint) # Print the current set-point
        itc.temperature_setpoint = 300  # Change the set-point to 300 K
        itc.wait_for_temperature()      # Wait for the temperature to stabilize
        print(itc.temperature_1)        # Print the temperature at sensor 1

    """

    def __init__(self,
                 adapter,
                 name="Oxford ITC503",
                 clear_buffer=True,
                 min_temperature=0,
                 max_temperature=1677.7,
                 **kwargs):

        if isinstance(adapter, (int, str)):
            kwargs.setdefault('read_termination', '\r')
            kwargs.setdefault('send_end', True)
            adapter = OxfordInstrumentsAdapter(
                adapter,
                asrl={
                    'baud_rate': 9600,
                    'data_bits': 8,
                    'parity': 0,
                    'stop_bits': 20,
                },
                preprocess_reply=lambda v: v[1:],
                **kwargs,
            )

        super().__init__(
            adapter=adapter,
            name=name,
            includeSCPI=False,
        )

        # Clear the buffer in order to prevent communication problems
        if clear_buffer:
            self.adapter.connection.clear()

        self.temperature_setpoint_values = [min_temperature, max_temperature]

    class FLOW_CONTROL_STATUS(IntFlag):
        """ IntFlag class for decoding the flow control status. Contains the following
        flags:

        === ======================  ==============================================
        bit flag                    meaning
        === ======================  ==============================================
        4   HEATER_ERROR_SIGN       Sign of heater-error; True means negative
        3   TEMPERATURE_ERROR_SIGN  Sign of temperature-error; True means negative
        2   SLOW_VALVE_ACTION       Slow valve action occurring
        1   COOLDOWN_TERMINATION    Cooldown-termination occurring
        0   FAST_COOLDOWN           Fast-cooldown occurring
        === ======================  ==============================================

        """
        HEATER_ERROR_SIGN = 16
        TEMPERATURE_ERROR_SIGN = 8
        SLOW_VALVE_ACTION = 4
        COOLDOWN_TERMINATION = 2
        FAST_COOLDOWN = 1

    version = Instrument.measurement(
        "V",
        """ A string property that returns the version of the IPS. """,
        preprocess_reply=lambda v: v,
    )

    control_mode = Instrument.control(
        "X", "C%d",
        """ A string property that sets the ITC in `local` or `remote` and `locked`
        or `unlocked`, locking the LOC/REM button. Allowed values are:

        =====   =================
        value   state
        =====   =================
        LL      local & locked
        RL      remote & locked
        LU      local & unlocked
        RU      remote & unlocked
        =====   =================
        """,
        preprocess_reply=lambda v: v[5:6],
        cast=int,
        validator=strict_discrete_set,
        values={"LL": 0, "RL": 1, "LU": 2, "RU": 3},
        map_values=True,
    )

    heater_gas_mode = Instrument.control(
        "X", "A%d",
        """ A string property that sets the heater and gas flow control to
        `auto` or `manual`. Allowed values are:

        ======   =======================
        value    state
        ======   =======================
        MANUAL   heater & gas manual
        AM       heater auto, gas manual
        MA       heater manual, gas auto
        AUTO     heater & gas auto
        ======   =======================
        """,
        preprocess_reply=lambda v: v[3:4],
        cast=int,
        validator=strict_discrete_set,
        values={"MANUAL": 0, "AM": 1, "MA": 2, "AUTO": 3},
        map_values=True,
    )

    heater = Instrument.control(
        "R5", "O%f",
        """ A floating point property that represents the heater output power
        as a percentage of the maximum voltage. Can be set if the heater is in
        manual mode. Valid values are in range 0 [off] to 99.9 [%]. """,
        validator=truncated_range,
        values=[0, 99.9]
    )

    heater_voltage = Instrument.measurement(
        "R6",
        """ A floating point property that represents the heater output power
        in volts. For controlling the heater, use the :class:`ITC503.heater`
        property. """,
    )

    gasflow = Instrument.control(
        "R7", "G%f",
        """ A floating point property that controls gas flow when in manual
        mode. The value is expressed as a percentage of the maximum gas flow.
        Valid values are in range 0 [off] to 99.9 [%]. """,
        validator=truncated_range,
        values=[0, 99.9]
    )

    proportional_band = Instrument.control(
        "R8", "P%f",
        """ A floating point property that controls the proportional band
        for the PID controller in Kelvin. Can be set if the PID controller
        is in manual mode. Valid values are 0 [K] to 1677.7 [K]. """,
        validator=truncated_range,
        values=[0, 1677.7]
    )

    integral_action_time = Instrument.control(
        "R9", "I%f",
        """ A floating point property that controls the integral action time
        for the PID controller in minutes. Can be set if the PID controller
        is in manual mode. Valid values are 0 [min.] to 140 [min.]. """,
        validator=truncated_range,
        values=[0, 140]
    )

    derivative_action_time = Instrument.control(
        "R10", "D%f",
        """ A floating point property that controls the derivative action time
        for the PID controller in minutes. Can be set if the PID controller
        is in manual mode. Valid values are 0 [min.] to 273 [min.]. """,
        validator=truncated_range,
        values=[0, 273]
    )

    auto_pid = Instrument.control(
        "X", "L%d",
        """ A boolean property that sets the Auto-PID mode on (True) or off (False).
        """,
        preprocess_reply=lambda v: v[12:13],
        cast=int,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    sweep_status = Instrument.control(
        "X", "S%d",
        """ An integer property that sets the sweep status. Values are:

        =========   =========================================
        value       meaning
        =========   =========================================
        0           Sweep not running
        1           Start sweep / sweeping to first set-point
        2P - 1      Sweeping to set-point P
        2P          Holding at set-point P
        =========   =========================================
        """,
        preprocess_reply=lambda v: v[7:9],
        cast=int,
        validator=strict_range,
        values=[0, 32]
    )

    temperature_setpoint = Instrument.control(
        "R0", "T%f",
        """ A floating point property that controls the temperature set-point of
        the ITC in kelvin. """,
        validator=truncated_range,
        values=[0, 1677.7],  # Kelvin, 0 - 1677.7K is the maximum range of the instrument
        dynamic=True,
    )

    temperature_1 = Instrument.measurement(
        "R1",
        """ Reads the temperature of the sensor 1 in Kelvin. """,
    )

    temperature_2 = Instrument.measurement(
        "R2",
        """ Reads the temperature of the sensor 2 in Kelvin. """,
    )

    temperature_3 = Instrument.measurement(
        "R3",
        """ Reads the temperature of the sensor 3 in Kelvin. """,
    )

    temperature_error = Instrument.measurement(
        "R4",
        """ Reads the difference between the set-point and the measured
        temperature in Kelvin. Positive when set-point is larger than
        measured. """,
    )

    front_panel_display = Instrument.setting(
        "F%d",
        """ A string property that controls what value is displayed on
        the front panel of the ITC. Valid values are:
        'temperature setpoint', 'temperature 1', 'temperature 2',
        'temperature 3', 'temperature error', 'heater', 'heater voltage',
        'gasflow', 'proportional band', 'integral action time',
        'derivative action time', 'channel 1 freq/4', 'channel 2 freq/4',
        'channel 3 freq/4'.
        """,
        validator=strict_discrete_set,
        map=True,
        values={
            "temperature setpoint": 0,
            "temperature 1": 1,
            "temperature 2": 2,
            "temperature 3": 3,
            "temperature error": 4,
            "heater": 5,
            "heater voltage": 6,
            "gasflow": 7,
            "proportional band": 8,
            "integral action time": 9,
            "derivative action time": 10,
            "channel 1 freq/4": 11,
            "channel 2 freq/4": 12,
            "channel 3 freq/4": 13,
        },
    )

    x_pointer = Instrument.setting(
        "x%d",
        """ An integer property to set pointers into tables for loading and
        examining values in the table. The significance and valid values for
        the pointer depends on what property is to be read or set. """,
        validator=strict_range,
        values=[0, 128]
    )

    y_pointer = Instrument.setting(
        "y%d",
        """ An integer property to set pointers into tables for loading and
        examining values in the table. The significance and valid values for
        the pointer depends on what property is to be read or set. """,
        validator=strict_range,
        values=[0, 128]
    )

    pointer = Instrument.setting(
        "$x%d\r$y%d",
        """ A tuple property to set pointers into tables for loading and
        examining values in the table, of format (x, y). The significance
        and valid values for the pointer depends on what property is to be
        read or set. The value for x and y can be in the range 0 to 128. """,
        validator=pointer_validator,
        values=[0, 128]
    )

    sweep_table = Instrument.control(
        "r", "s%f",
        """ A property that controls values in the sweep table. Relies on
        :class:`ITC503.x_pointer` and :class:`ITC503.y_pointer` (or
        :class:`ITC503.pointer`) to point at the location in the table that is
        to be set or read.

        The x-pointer selects the step of the sweep (1 to 16); the y-pointer
        selects the parameter:

        =========   =======================
        y-pointer   parameter
        =========   =======================
        1           set-point temperature
        2           sweep-time to set-point
        3           hold-time at set-point
        =========   =======================
        """,
    )

    auto_pid_table = Instrument.control(
        "q", "p%f",
        """ A property that controls values in the auto-pid table. Relies on
        :class:`ITC503.x_pointer` and :class:`ITC503.y_pointer` (or
        :class:`ITC503.pointer`) to point at the location in the table that
        is to be set or read.

        The x-pointer selects the table entry (1 to 16); the y-pointer
        selects the parameter:

        =========   =======================
        y-pointer   parameter
        =========   =======================
        1           upper temperature limit
        2           proportional band
        3           integral action time
        4           derivative action time
        =========   =======================
        """,
    )

    target_voltage_table = Instrument.control(
        "t", "v%f",
        """ A property that controls values in the target heater voltage table.
        Relies on the :class:`ITC503.x_pointer` to select the entry in the table
        that is to be set or read (1 to 64).
        """,
    )

    gasflow_configuration_parameter = Instrument.control(
        "d", "c%f",
        """ A property that controls the gas flow configuration parameters.
        Relies on the :class:`ITC503.x_pointer` to select which parameter
        is set or read:

        =========   =====================================
        x-pointer   parameter
        =========   =====================================
        1           valve gearing
        2           target table & features configuration
        3           gas flow scaling
        4           temperature error sensitivity
        5           heater voltage error sensitivity
        6           minimum gas valve in auto
        =========   =====================================
        """,
    )

    gasflow_control_status = Instrument.measurement(
        "m",
        """ A property that reads the gas-flow control status. Returns
        the status in the form of a :class:`ITC503.FLOW_CONTROL_STATUS`
        IntFlag. """,
        cast=int,
        get_process=lambda v: ITC503.FLOW_CONTROL_STATUS(v),
    )

    target_voltage = Instrument.measurement(
        "n",
        """ A float property that reads the current heater target voltage
        with which the actual heater voltage is being compared. Only valid
        if gas-flow in auto mode. """,
    )

    valve_scaling = Instrument.measurement(
        "o",
        """ A float property that reads the valve scaling parameter. Only
        valid if gas-flow in auto mode. """,
    )

    def wait_for_temperature(self,
                             error=0.01,
                             timeout=3600,
                             check_interval=0.5,
                             stability_interval=10,
                             thermalize_interval=300,
                             should_stop=lambda: False,
                             ):
        """
        Wait for the ITC to reach the set-point temperature.

        :param error: The maximum error in Kelvin under which the temperature
                      is considered at set-point
        :param timeout: The maximum time the waiting is allowed to take. If
                        timeout is exceeded, a TimeoutError is raised. If
                        timeout is None, no timeout will be used.
        :param check_interval: The time between temperature queries to the ITC.
        :param stability_interval: The time over which the temperature_error is
                                   to be below error to be considered stable.
        :param thermalize_interval: The time to wait after stabilizing for the
                                    system to thermalize.
        :param should_stop: Optional function (returning a bool) to allow the
                            waiting to be stopped before its end.
        """

        number_of_intervals = int(stability_interval / check_interval)
        stable_intervals = 0
        attempt = 0

        t0 = time()
        while True:
            temp_error = self.temperature_error
            if abs(temp_error) < error:
                stable_intervals += 1
            else:
                stable_intervals = 0
                attempt += 1

            if stable_intervals >= number_of_intervals:
                break

            if timeout is not None and (time() - t0) > timeout:
                raise TimeoutError(
                    "Timeout expired while waiting for the Oxford ITC305 to "
                    "reach the set-point temperature"
                )

            if should_stop():
                return

            sleep(check_interval)

        if attempt == 0:
            return

        t1 = time() + thermalize_interval
        while time() < t1:
            sleep(check_interval)
            if should_stop():
                return

        return

    def program_sweep(self, temperatures, sweep_time, hold_time, steps=None):
        """
        Program a temperature sweep in the controller. Stops any running sweep.
        After programming the sweep, it can be started using
        OxfordITC503.sweep_status = 1.

        :param temperatures: An array containing the temperatures for the sweep
        :param sweep_time: The time (or an array of times) to sweep to a
                           set-point in minutes (between 0 and 1339.9).
        :param hold_time: The time (or an array of times) to hold at a
                          set-point in minutes (between 0 and 1339.9).
        :param steps: The number of steps in the sweep, if given, the
                      temperatures, sweep_time and hold_time will be
                      interpolated into (approximately) equal segments
        """
        # Check if in remote control
        if not self.control_mode.startswith("R"):
            raise AttributeError(
                "Oxford ITC503 not in remote control mode"
            )

        # Stop sweep if running to be able to write the program
        self.sweep_status = 0

        # Convert input np.ndarrays
        temperatures = numpy.array(temperatures, ndmin=1)
        sweep_time = numpy.array(sweep_time, ndmin=1)
        hold_time = numpy.array(hold_time, ndmin=1)

        # Make steps array
        if steps is None:
            steps = temperatures.size
        steps = numpy.linspace(1, steps, steps)

        # Create interpolated arrays
        interpolator = numpy.round(
            numpy.linspace(1, steps.size, temperatures.size))
        temperatures = numpy.interp(steps, interpolator, temperatures)

        interpolator = numpy.round(
            numpy.linspace(1, steps.size, sweep_time.size))
        sweep_time = numpy.interp(steps, interpolator, sweep_time)

        interpolator = numpy.round(
            numpy.linspace(1, steps.size, hold_time.size))
        hold_time = numpy.interp(steps, interpolator, hold_time)

        # Pad with zeros to wipe unused steps (total 16) of the sweep program
        padding = 16 - temperatures.size
        temperatures = numpy.pad(temperatures, (0, padding), 'constant',
                                 constant_values=temperatures[-1])
        sweep_time = numpy.pad(sweep_time, (0, padding), 'constant')
        hold_time = numpy.pad(hold_time, (0, padding), 'constant')

        # Setting the arrays to the controller
        for line, (setpoint, sweep, hold) in \
                enumerate(zip(temperatures, sweep_time, hold_time), 1):
            self.pointer = (line, 1)
            self.sweep_table = setpoint

            self.pointer = (line, 2)
            self.sweep_table = sweep

            self.pointer = (line, 3)
            self.sweep_table = hold

    def wipe_sweep_table(self):
        """ Wipe the currently programmed sweep table. """
        self.write("w")
