#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

from time import sleep, time
import numpy

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, \
    truncated_range, strict_range


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

    control_mode = Instrument.control(
        "X", "$C%d",
        """ A string property that sets the ITC in LOCAL or REMOTE and LOCKES,
        or UNLOCKES, the LOC/REM button. Allowed values are:
        LL: LOCAL & LOCKED
        RL: REMOTE & LOCKED
        LU: LOCAL & UNLOCKED
        RU: REMOTE & UNLOCKED. """,
        get_process=lambda v: int(v[5:6]),
        validator=strict_discrete_set,
        values={"LL": 0, "RL": 1, "LU": 2, "RU": 3},
        map_values=True,
    )

    heater_gas_mode = Instrument.control(
        "X", "$A%d",
        """ A string property that sets the heater and gas flow control to
        AUTO or MANUAL. Allowed values are:
        MANUAL: HEATER MANUAL, GAS MANUAL
        AM: HEATER AUTO, GAS MANUAL
        MA: HEATER MANUAL, GAS AUTO
        AUTO: HEATER AUTO, GAS AUTO. """,
        get_process=lambda v: int(v[3:4]),
        validator=strict_discrete_set,
        values={"MANUAL": 0, "AM": 1, "MA": 2, "AUTO": 3},
        map_values=True,
    )

    auto_pid = Instrument.control(
        "X", "$L%d",
        """ A boolean property that sets the Auto-PID mode on (True) or off (False).
        """,
        get_process=lambda v: int(v[12:13]),
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    sweep_status = Instrument.control(
        "X", "$S%d",
        """ An integer property that sets the sweep status. Values are:
        0: Sweep not running
        1: Start sweep / sweeping to first set-point
        2P - 1: Sweeping to set-point P
        2P: Holding at set-point P. """,
        get_process=lambda v: int(v[7:9]),
        validator=strict_range,
        values=[0, 32]
    )

    temperature_setpoint = Instrument.control(
        "R0", "$T%f",
        """ A floating point property that controls the temperature set-point of
        the ITC in kelvin. """,
        get_process=lambda v: float(v[1:]),
        validator=truncated_range,
        values=[0, 301]
    )

    temperature_1 = Instrument.measurement(
        "R1",
        """ Reads the temperature of the sensor 1 in Kelvin. """,
        get_process=lambda v: float(v[1:]),
    )

    temperature_2 = Instrument.measurement(
        "R2",
        """ Reads the temperature of the sensor 2 in Kelvin. """,
        get_process=lambda v: float(v[1:]),
    )

    temperature_2 = Instrument.measurement(
        "R3",
        """ Reads the temperature of the sensor 3 in Kelvin. """,
        get_process=lambda v: float(v[1:]),
    )

    temperature_error = Instrument.measurement(
        "R4",
        """ Reads the difference between the set-point and the measured
        temperature in Kelvin. Positive when set-point is larger than
        measured. """,
        get_process=lambda v: float(v[1:]),
    )

    xpointer = Instrument.setting(
        "$x%d",
        """ An integer property to set pointers into tables for loading and
        examining values in the table. For programming the sweep table values
        from 1 to 16 are allowed, corresponding to the maximum number of steps.
        """,
        validator=strict_range,
        values=[0, 128]
    )

    ypointer = Instrument.setting(
        "$y%d",
        """ An integer property to set pointers into tables for loading and
        examining values in the table. For programming the sweep table the
        allowed values are:
        1: Setpoint temperature,
        2: Sweep-time to set-point,
        3: Hold-time at set-point. """,
        validator=strict_range,
        values=[0, 128]
    )

    sweep_table = Instrument.control(
        "r", "$s%f",
        """ A property that sets values in the sweep table. Relies on the
        xpointer and ypointer to point at the location in the table that
        is to be set. """,
        get_process=lambda v: float(v[1:]),
    )

    def __init__(self, resourceName, clear_buffer=True, **kwargs):
        super(ITC503, self).__init__(
            resourceName,
            "Oxford ITC503",
            includeSCPI=False,
            send_end=True,
            read_termination="\r",
            **kwargs
        )

        # Clear the buffer in order to prevent communication problems
        if clear_buffer:
            self.adapter.connection.clear()

    def wait_for_temperature(self, error=0.01, timeout=3600,
                             check_interval=0.5, stability_interval=10,
                             thermalize_interval=300,
                             should_stop=lambda: False):
        """
        Wait for the ITC to reach the set-point temperature.

        :param error: The maximum error in Kelvin under which the temperature
                      is considered at set-point
        :param timeout: The maximum time the waiting is allowed to take. If
                        timeout is exceeded, a TimeoutError is raised. If
                        timeout is set to zero, no timeout will be used.
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

            if abs(self.temperature_error) < error:
                stable_intervals += 1
            else:
                stable_intervals = 0
                attempt += 1

            if stable_intervals >= number_of_intervals:
                break

            if timeout >= 0 and (time() - t0) > timeout:
                raise TimeoutError(
                    "Timeout expired while waiting for the Oxford ITC305 to \
                    reach the set-point temperature"
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
            self.xpointer = line

            self.ypointer = 1
            self.sweep_table = setpoint

            self.ypointer = 2
            self.sweep_table = sweep

            self.ypointer = 3
            self.sweep_table = hold
