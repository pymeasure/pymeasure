# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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
import time
from typing import List, Literal

import numpy as np
import pydantic

from pymeasure.instruments.instrument import BaseChannel, Instrument
from pymeasure.instruments.validators import (
    strict_discrete_set,
    strict_range,
    truncated_range,
)

# Setup logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley2600(Instrument):
    """Represents the Keithley 2600 series (channel A and B) SourceMeter"""

    id_starts_with = "Keithley"

    def __init__(self, adapter, **kwargs):
        self.ChA = Channel(self, "a")
        self.ChB = Channel(self, "b")
        super().__init__(
            adapter, "Keithley 2600 SourceMeter", includeSCPI=False, **kwargs
        )

        # Sweep command times out at the default timeout duration
        self.adapter.connection.timeout = 25000

    def _flush_errors(self):
        """Returns a list of errors where each element includes the error code
        and message.
        """
        self._wait_until_ready()
        errors = []
        while True:
            err = self.ask_no_lock("print(errorqueue.next())")
            err = err.split("\t")
            # Keithley Instruments Inc. sometimes on startup
            # if tab delimitated message is greater than one, grab first two as code, message
            # otherwise, assign code & message to returned error
            if len(err) > 1:
                err = (int(float(err[0])), err[1])
                code = err[0]
                if not code == 0:
                    message = err[1].replace('"', "")
                    error_msg = f"{str(code)},{str(message)}"
                    log.error(error_msg)
                    errors.append(error_msg)
            else:
                break

            return errors

    def clear(self):
        """Clears the instrument status byte"""
        self.write("status.reset()")

    def reset(self):
        """Resets the instrument."""
        self.write("*reset()")

    @property
    def status(self) -> str:
        """Checks the status of the system.

        Returns:
            "ok: busy" if the threading lock cannot be acquired, "ok: ON"
            if the system is on and the lock was acquired. If communication
            was not initially successfull, the system is queried again and
            the ID is checked. If the system does not return an expected response,
            status is set to warning: Cannot communicate with device".
        """
        if not self.communication_success:
            id = self.get_id(check_for_errors=False)

            if id.startswith(self.id_starts_with):
                curr_status = "ok: ON"
                self.communication_success = True
            else:
                curr_status = "warning: Cannot communicate with device"
        else:
            if self._lock.locked():
                curr_status = "ok: busy"
            else:
                curr_status = "ok: ON"

        return curr_status

    @property
    def complete(self):
        """This property allows synchronization between a controller and a device. The Operation Complete
        query places an ASCII character 1 into the device's Output Queue when all pending
        selected device operations have been finished.
        """
        ready = self.ask_no_lock("waitcomplete() print([[1]])").strip()
        if ready == "1":
            return True
        elif ready == "0":
            return False
        else:
            return None

    def get_id(self, check_errors=True):
        """Requests and returns the identification of the instrument."""
        return self.ask(
            "*IDN?",
            check_errors,
        ).strip()

    @staticmethod
    @pydantic.validate_arguments
    def calculate_step_size(
        sweep_start: float,
        sweep_end: float,
        number_of_sweep_points: pydantic.conint(ge=2),
    ) -> float:
        """Calculates the step size for a sweep given the relavant parameters.

        Args:
            sweep_start: Starting sweep value.
            sweep_end: Ending sweep value.
            number_of_sweep_points: Number of sweep steps being taken.

        Returns:
            Returns the sweep step as a float type.
        """
        return (sweep_end - sweep_start) / (number_of_sweep_points - 1)

    @staticmethod
    @pydantic.validate_arguments
    def get_sweep_list(
        sweep_start: float,
        sweep_end: float,
        number_of_sweep_points: pydantic.conint(ge=2),
    ) -> List[float]:
        """Get the list of sweep steps to be taken.

        Args:
            sweep_start: Starting sweep value.
            sweep_end: Ending sweep value.
            number_of_sweep_points: Number of sweep steps being taken.

        Returns:
            List of sweep steps (as float types)
        """
        step = Keithley2600.calculate_step_size(
            sweep_start.sweep_end, number_of_sweep_points
        )
        return list(range(sweep_start, sweep_end + step, step))


class Channel(BaseChannel):
    def __init__(self, instrument, channel):
        self.instrument = instrument
        self.channel = channel
        super().__init__()

    def ask(self, cmd):
        return float(self.instrument.ask(f"print(smu{self.channel}.{cmd})"))

    def write(self, cmd):
        self.instrument.write(f"smu{self.channel}.{cmd}")

    def values(self, cmd, **kwargs):
        """Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values(f"print(smu{self.channel}.{cmd})")

    def buffer_ascii_values(self, buffer_number, cmd=None, **kwargs) -> np.array:
        """Reads a set of ascii values from one of the channel's buffers through the adapter,
        passing on any key-word arguments.

        Args:
            buffer_number: The buffer number to read from.
            cmd: The command to append to the buffer print statement (e.g. could be ``readings`` to
                access readings, or ``sourcevalues`` to access sourcing measurements). Defaults to
                None.

        Returns:
            The data read from the buffer as a numpy array.
        """
        if cmd:
            return self.instrument.ascii_values(
                f"printbuffer(1, smu{self.channel}.nvbuffer{buffer_number}.n, smu{self.channel}.nvbuffer{buffer_number}.{cmd})",
                container=np.array,
                **kwargs,
            )
        else:
            return self.instrument.ascii_values(
                f"printbuffer(1, smu{self.channel}.nvbuffer{buffer_number}.n, smu{self.channel}.nvbuffer{buffer_number})",
                container=np.array,
                **kwargs,
            )

    def binary_values(self, cmd, header_bytes=0, dtype=np.float32):
        return self.instrument.binary_values(
            f"print(smu{self.channel}.{cmd})",
            header_bytes,
            dtype,
        )

    def check_errors(self):
        return self.instrument.check_errors()

    source_output = Instrument.control(
        "source.output",
        "source.output=%d",
        """Property controlling the channel output state (ON of OFF)
        """,
        validator=strict_discrete_set,
        values={"OFF": 0, "ON": 1},
        map_values=True,
    )

    source_mode = Instrument.control(
        "source.func",
        "source.func=%d",
        """Property controlling the channel source function (Voltage or Current)
        """,
        validator=strict_discrete_set,
        values={"voltage": 1, "current": 0},
        map_values=True,
    )

    measure_nplc = Instrument.control(
        "measure.nplc",
        "measure.nplc=%f",
        """ Property controlling the nplc value """,
        validator=truncated_range,
        values=[0.001, 25],
        map_values=True,
    )

    buffer_1_source_value_collection = Instrument.control(
        "nvbuffer1.collectsourcevalues",
        "nvbuffer1.collectsourcevalues=%d",
        """ Enables or disables the storage of source values """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    buffer_1_time_stamp_collection = Instrument.control(
        "nvbuffer1.collecttimestamps",
        "nvbuffer1.collecttimestamps=%d",
        """ Enables or disables the storage of timestamps """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    ###############
    # Current (A) #
    ###############
    current = Instrument.measurement("measure.i()", """ Reads the current in Amps """)

    source_current = Instrument.control(
        "source.leveli",
        "source.leveli=%f",
        """ Property controlling the applied source current """,
        validator=truncated_range,
        values=[-1.5, 1.5],
    )

    compliance_current = Instrument.control(
        "source.limiti",
        "source.limiti=%f",
        """ Property controlling the source compliance current """,
        validator=truncated_range,
        values=[-1.5, 1.5],
    )

    source_current_range = Instrument.control(
        "source.rangei",
        "source.rangei=%f",
        """Property controlling the source current range """,
        validator=truncated_range,
        values=[-1.5, 1.5],
    )

    current_range = Instrument.control(
        "measure.rangei",
        "measure.rangei=%f",
        """Property controlling the measurement current range """,
        validator=truncated_range,
        values=[-1.5, 1.5],
    )

    ###############
    # Voltage (V) #
    ###############
    voltage = Instrument.measurement("measure.v()", """ Reads the voltage in Volts """)

    source_voltage = Instrument.control(
        "source.levelv",
        "source.levelv=%f",
        """ Property controlling the applied source voltage """,
        validator=strict_range,
        values=[-200, 200],
        dynamic=True,
    )

    compliance_voltage = Instrument.control(
        "source.limitv",
        "source.limitv=%f",
        """ Property controlling the source compliance voltage """,
        validator=strict_range,
        values=[-200, 200],
        dynamic=True,
    )

    source_voltage_range = Instrument.control(
        "source.rangev",
        "source.rangev=%f",
        """Property controlling the source voltage range """,
        validator=truncated_range,
        values=[-200, 200],
    )

    voltage_range = Instrument.control(
        "measure.rangev",
        "measure.rangev=%f",
        """Property controlling the measurement voltage range """,
        validator=truncated_range,
        values=[-200, 200],
    )

    ####################
    # Resistance (Ohm) #
    ####################
    resistance = Instrument.measurement(
        "measure.r()", """ Reads the resistance in Ohms """
    )

    wires_mode = Instrument.control(
        "sense",
        "sense=%d",
        """Property controlling the resistance measurement mode: 4 wires or 2 wires""",
        validator=strict_discrete_set,
        values={"4": 1, "2": 0},
        map_values=True,
    )

    #######################
    # Measurement Methods #
    #######################

    def measure_voltage(self, nplc=1, voltage=21.0, auto_range=True):
        """Configures the measurement of voltage.
        :param nplc: Number of power line cycles (NPLC) from 0.001 to 25
        :param voltage: Upper limit of voltage in Volts, from -200 V to 200 V
        :param auto_range: Enables auto_range if True, else uses the set voltage
        """
        log.info(f"{self.channel} is measuring voltage.")
        self.write("measure.v()")
        self.write(f"measure.nplc={nplc:f}")
        if auto_range:
            self.write("measure.autorangev=1")
        else:
            self.voltage_range = voltage

    def measure_current(self, nplc=1, current=1.05e-4, auto_range=True):
        """Configures the measurement of current.
        :param nplc: Number of power line cycles (NPLC) from 0.001 to 25
        :param current: Upper limit of current in Amps, from -1.5 A to 1.5 A
        :param auto_range: Enables auto_range if True, else uses the set current
        """
        log.info(f"{self.channel} is measuring current.")
        self.write("measure.i()")
        self.write(f"measure.nplc={nplc:f}")
        if auto_range:
            self.write("measure.autorangei=1")
        else:
            self.current_range = current

    def auto_range_source(self):
        """Configures the source to use an automatic range."""
        if self.source_mode == "current":
            self.write("source.autorangei=1")
        else:
            self.write("source.autorangev=1")

    def apply_current(self, current_range=None, compliance_voltage=0.1):
        """Configures the instrument to apply a source current, and
        uses an auto range unless a current range is specified.
        The compliance voltage is also set.
        :param compliance_voltage: A float in the correct range for a
                                   :attr:`~.Keithley2600.compliance_voltage`
        :param current_range: A :attr:`~.Keithley2600.current_range` value or None
        """
        log.info(f"{self.channel} is sourcing current.")
        self.source_mode = "current"
        if current_range is None:
            self.auto_range_source()
        else:
            self.source_current_range = current_range
        self.compliance_voltage = compliance_voltage

    def apply_voltage(self, voltage_range=None, compliance_current=0.1):
        """Configures the instrument to apply a source voltage, and
        uses an auto range unless a voltage range is specified.
        The compliance current is also set.
        :param compliance_current: A float in the correct range for a
                                   :attr:`~.Keithley2600.compliance_current`
        :param voltage_range: A :attr:`~.Keithley2600.voltage_range` value or None
        """
        log.info(f"{self.channel} is sourcing voltage.")
        self.source_mode = "voltage"
        if voltage_range is None:
            self.auto_range_source()
        else:
            self.source_voltage_range = voltage_range
        self.compliance_current = compliance_current

    def ramp_to_voltage(self, target_voltage, steps=30, pause=0.1):
        """Ramps to a target voltage from the set voltage value over
        a certain number of linear steps, each separated by a pause duration.
        :param target_voltage: A voltage in Amps
        :param steps: An integer number of steps
        :param pause: A pause duration in seconds to wait between steps"""
        voltages = np.linspace(self.source_voltage, target_voltage, steps)
        for voltage in voltages:
            self.source_voltage = voltage
            time.sleep(pause)

    def ramp_to_current(self, target_current, steps=30, pause=0.1):
        """Ramps to a target current from the set current value over
        a certain number of linear steps, each separated by a pause duration.
        :param target_current: A current in Amps
        :param steps: An integer number of steps
        :param pause: A pause duration in seconds to wait between steps"""
        currents = np.linspace(self.source_current, target_current, steps)
        for current in currents:
            self.source_current = current
            time.sleep(pause)

    @pydantic.validate_arguments
    def clear_buffer(self, buffer_number: Literal[1, 2]):
        """Clears the specified buffer.

        Args:
            buffer_number: The buffer number to clear.
        """
        self.write(f"nvbuffer{buffer_number}.clear()")

    @pydantic.validate_arguments
    def sweep_voltage_measure_current(
        self,
        current_limit: float,
        current_measurement_range: float,
        sweep_start_v: float,
        sweep_end_v: float,
        settling_time: pydantic.confloat(ge=0),
        number_of_sweep_points: pydantic.conint(ge=2),
    ) -> np.ndarray:
        """Performs a inear voltage sweep with current measured at every step (point).

        The steps followed can be seen below:

            1. Sets the SMU to output ``sweep_start_v`` volts, allows the source to settle for ``settling_time`` seconds, and
                then makes a current measurement.
            2. Sets the SMU to output the next voltage step, allows the source to settle for ``settling_time`` seconds,
                and then makes a voltage measurement.
            3. Repeats the above sequence until the current is measured on the ``sweep_end_v`` volts step.

        The step size can be computed using the calculate_step_size static method included in the
        Keithley2600 class.

        Args:
            current_limit: The maximum current that should be sourced in amperes.
            current_measurement_range: The measurement range to use when measuring the current.
            sweep_start_v: Starting sweep voltage (in volts).
            sweep_end_v: Ending sweep voltage (in volts).
            settling_time: The settling time used before making a measurement (in seconds).
            number_of_sweep_points: The number of points to sweep for.

        Returns:
            Returns a 2D numpy array, with the first dimension being the measured voltage values,
                and the second dimension being the measured current values.
        """
        self.clear_buffer(1)
        self.buffer_1_source_value_collection = True

        self.compliance_current = current_limit
        self.current_range = current_measurement_range
        self.instrument.write(
            f"SweepVLinMeasureI(smu{self.channel}, {sweep_start_v}, {sweep_end_v}, {settling_time}, {number_of_sweep_points})"
        )
        voltage_values = self.buffer_ascii_values(1, "sourcevalues")
        measurement_values = self.buffer_ascii_values(1, "readings", delay=4)
        return np.array([voltage_values, measurement_values])

    def shutdown(self):
        """Ensures that the current or voltage is turned to zero
        and disables the output."""
        log.info(f"Shutting down channel {self.channel}.")
        if self.source_mode == "current":
            self.ramp_to_current(0.0)
        else:
            self.ramp_to_voltage(0.0)
        self.source_output = "OFF"
