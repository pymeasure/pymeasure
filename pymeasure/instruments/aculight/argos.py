#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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

# Standard packages
from typing import NamedTuple

# third party packages
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range

# local packages


def state_to_float(line: str) -> float:
    """Extract the float of the value line '   name = value'."""
    return float(line.split("=")[-1])


def generate_state_extraction_method(index):
    """Generate a method, which returns one of the states according to the index."""
    def extract_state(values):
        return state_to_float(values[index])
    return extract_state


class State(NamedTuple):
    crystal_temperature_setpoint: float
    crystal_temperature: float
    etalon_angle: float
    seed_voltage: float


class Argos(Instrument):
    """Communication model for the Aculight Argos 2400 OPO system.

    Note that the device can only return all values at once, which takes around 100 ms.
    If you need more than one value, read the :attr:`state` property instead of individual
    properties.
    Reading any property reads all properties and returns the corresponding value.

    Note also, that the block temperature cannot be set remotely, only via the front panel.

    Cable type: RS232 null modem female DB9 connectors: The pins 2 and 3 have to be crossed between
    both sides. Pin2 is RX and Pin3 is Tx, Pin 5 is ground.

    :param adapter: resource name
    :param query_delay: Delay between write and read in seconds.
    """

    def __init__(self, adapter, name="Argos 2400 OPO system", query_delay=0.01, **kwargs):
        super().__init__(
            adapter,
            name,
            baud_rate=4800,
            write_termination="\n",
            read_termination="\n\rOPO>",
            includeSCPI=False,
            **kwargs)
        """
        8 data bits, no parity, 1 stop bit, no flow control
        """
        self.query_delay = query_delay
        # read starts with space and ends with "\n\rOPO>"

    def wait_for(self, query_delay=None):
        """Wait for some time. Used by 'ask' to wait before reading.

        :param query_delay: Delay between writing and reading in seconds. None is default delay.
        """
        super().wait_for(self.query_delay if query_delay is None else query_delay)

    def check_set_errors(self):
        """Read after setting."""
        got = self.read()
        if "setting changed" not in got:
            raise ConnectionError(f"Change setting failed: {got}")
        return []

    @property
    def state(self) -> State:
        """Get the current state of the system as a namped tuple

        :return tuple: with 'setpoint', 'temperature', 'etalon', and 'seed'.
        """
        got = self.ask("state")
        # got is in form (note the spaces at the begin):
        #   Crystal Temp Set = 55.000\n\r
        #   Etalon Angle Set = -0.020\n\r
        #   Seed Source Set  = 0.000\n\r
        #   Crystal Temp = 54.900\n\r
        #   OPO>
        tempSet, etalon, seed, temp = got.split("\n\r")
        state = State(crystal_temperature=state_to_float(temp),
                      crystal_temperature_setpoint=state_to_float(tempSet),
                      etalon_angle=state_to_float(etalon),
                      seed_voltage=state_to_float(seed))
        return state

    version = Instrument.measurement("ver", "Get the firmware version.", cast=str)  # type: ignore

    temperature_setpoint = Instrument.control(
        "state",
        "temp %.3f",
        "Control the crystal temperature setpoint in °C.",
        separator="\n\r",
        cast=str,  # type: ignore
        get_process=generate_state_extraction_method(0),
        validator=strict_range,
        values=[30, 100],
        check_set_errors=True,
    )

    etalon = Instrument.control(
        "state",
        "etalon %.3f",
        "Control the etalon angle in degrees.",
        separator="\n\r",
        cast=str,  # type: ignore
        get_process=generate_state_extraction_method(1),
        validator=strict_range,
        values=[-12, 12],
        check_set_errors=True,
    )

    seed_voltage = Instrument.control(
        "state",
        "seed %.3f",
        "Control the seed source tuning voltage.",
        separator="\n\r",
        cast=str,  # type: ignore
        get_process=generate_state_extraction_method(2),
        validator=strict_range,
        values=[0, 5],
        check_set_errors=True,
    )

    temperature = Instrument.measurement(
        "state",
        "Get the current crystal temperature in °C.",
        separator="\n\r",
        cast=str,  # type: ignore
        get_process=generate_state_extraction_method(3),
    )
