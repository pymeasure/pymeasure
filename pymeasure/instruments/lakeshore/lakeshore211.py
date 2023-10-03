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
from pymeasure.instruments.validators import strict_discrete_set
from pyvisa.constants import Parity
from enum import IntEnum

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class LakeShore211(Instrument):
    """ Represents the Lake Shore 211 Temperature Monitor and provides
    a high-level interface for interacting with the instrument.

    Untested properties and methods will be noted in their docstrings.

    .. code-block:: python

        controller = LakeShore211("GPIB::1")

        print(controller.temperature_celsius)     # Print the sensor temperature in celsius

    """

    class AnalogMode(IntEnum):
        VOLTAGE = 0
        CURRENT = 1

    class AnalogRange(IntEnum):
        RANGE_20K = 0
        RANGE_100K = 1
        RANGE_200K = 2
        RANGE_325K = 3
        RANGE_475K = 4
        RANGE_1000K = 5

    class RelayNumber(IntEnum):
        RELAY_ONE = 1
        RELAY_TWO = 2

    class RelayMode(IntEnum):
        OFF = 0
        ON = 1
        ALARMS = 2

    alarm_keys = ['on', 'high_value', 'low_value', 'deadband', 'latch']

    def __init__(self, adapter, name="Lake Shore 211 Temperature Monitor", **kwargs):
        super().__init__(
            adapter,
            name,
            asrl={'data_bits': 7, 'parity': Parity.odd},
            **kwargs
        )

    analog_configuration = Instrument.control(
        "ANALOG?", "ANALOG %d,%d",
        """
        Control the analog mode and analog range.
        Values need to be supplied as a tuple of (analog mode, analog range)
        Analog mode can be 0 or 1

        +--------+--------+
        | setting| mode   |
        +--------+--------+
        | 0      | voltage|
        +--------+--------+
        | 1      | current|
        +--------+--------+

        Analog range can be 0 through 5

        +--------+----------+
        | setting| range    |
        +--------+----------+
        | 0      | 0 – 20 K |
        +--------+----------+
        | 1      | 0 – 100 K|
        +--------+----------+
        | 2      | 0 – 200 K|
        +--------+----------+
        | 3      | 0 – 325 K|
        +--------+----------+
        | 4      | 0 – 475 K|
        +--------+----------+
        | 5      |0 – 1000 K|
        +--------+----------+
        """,
        # Validate and return tuple v
        validator=lambda v, vs: (
            strict_discrete_set(v[0], vs[0]), strict_discrete_set(v[1], vs[1])),
        values=[list(AnalogMode), list(AnalogRange)],
        # These are the vs values in the validator lambda
        get_process=lambda x: (LakeShore211.AnalogMode(x[0]), LakeShore211.AnalogRange(x[1])),
        cast=int
    )

    analog_out = Instrument.measurement(
        "AOUT?",
        """Measure the percentage of output of the analog output.
        """
    )

    display_units = Instrument.control(
        "DISPFLD?", "DISPFLD %d",
        """
        Control the input data to display. Valid entries:

        +-------------+--------------+
        | setting     | units        |
        +-------------+--------------+
        | 'kelvin'    | Kelvin       |
        +-------------+--------------+
        | 'celsius'   | Celsius      |
        +-------------+--------------+
        | 'sensor'    | Sensor Units |
        +-------------+--------------+
        | 'fahrenheit'| Fahrenheit   |
        +-------------+--------------+
        """,
        values={'kelvin': 0, 'celsius': 1, 'sensor': 2, 'fahrenheit': 3},
        map_values=True
    )

    temperature_celsius = Instrument.measurement(
        "CRDG?",
        """Measure the temperature of the sensor in celsius
        """
    )

    temperature_fahrenheit = Instrument.measurement(
        "FRDG?",
        """Measure the temperature of the sensor in fahrenheit
        """
    )

    temperature_sensor = Instrument.measurement(
        "SRDG?",
        """Measure the temperature of the sensor in sensor units
        """
    )

    temperature_kelvin = Instrument.measurement(
        "KRDG?",
        """Measure the temperature of the sensor in kelvin
        """
    )

    def get_relay_mode(self, relay):
        """
        Get the status of a relay

        Property is UNTESTED

        :param RelayNumber relay: Specify which relay to query
        :return: Current RelayMode of queried relay
        """
        relay = strict_discrete_set(relay, list(self.RelayNumber))
        return int(self.ask("RELAY? %d" % relay))

    def configure_relay(self, relay, mode):
        """
        Configure the relay mode of a relay

        Property is UNTESTED

        :param RelayNumber relay: Specify which relay to configure
        :param RelayMode mode: Specify which mode to assign
        """
        relay = strict_discrete_set(relay, list(self.RelayNumber))
        mode = strict_discrete_set(mode, list(self.RelayMode))
        self.write('RELAY %d %d' % (relay, mode))

    def get_alarm_status(self):
        """
        Query the current alarm status

        :return: Dictionary of current status [on, high_value, low_value, deadband, latch]
        """

        status = self.values('ALARM?')
        return dict(zip(self.alarm_keys,
                        [int(status[0]), float(status[1]), float(status[2]), float(status[3]),
                         int(status[4])]))

    def configure_alarm(self, on=True, high_value=270.0, low_value=0.0, deadband=0, latch=False):
        """Configures the alarm parameters for the input.

        :param on:  Boolean setting of alarm, default True
        :param high_value: High value the temperature is checked against to activate the alarm
        :param low_value: Low value the temperature is checked against to activate the alarm
        :param deadband: Value that the temperature must change outside of an alarm condition
        :param latch: Specifies if the alarm should latch or not
        """

        command_string = "ALARM %d,%g,%g,%g,%d" % (on, high_value, low_value, deadband, latch)
        self.write(command_string)

    def reset_alarm(self):
        """Resets the alarm of the Lakeshore 211
        """
        self.write('ALMRST')
