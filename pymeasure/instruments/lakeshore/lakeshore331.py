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

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep, time

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set


class LakeShore331(Instrument):
    """ Represents the Lake Shore 331 Temperature Controller and provides
    a high-level interface for interacting with the instrument.

    .. code-block:: python

        controller = LakeShore331("GPIB::1")

        print(controller.setpoint_1)        # Print the current setpoint for loop 1
        controller.setpoint_1 = 50          # Change the setpoint to 50 K
        controller.heater_range = 'low'     # Change the heater range to Low
        controller.wait_for_temperature()   # Wait for the temperature to stabilize
        print(controller.temperature_A)     # Print the temperature at sensor A

    """

    temperature_A = Instrument.measurement(
        "KRDG? A",
        """ Reads the temperature of the sensor A in Kelvin. """
    )
    temperature_B = Instrument.measurement(
        "KRDG? B",
        """ Reads the temperature of the sensor B in Kelvin. """
    )
    setpoint_1 = Instrument.control(
        "SETP? 1", "SETP 1, %g",
        """ A floating point property that controls the setpoint temperature
        in Kelvin for Loop 1. """
    )
    setpoint_2 = Instrument.control(
        "SETP? 2", "SETP 2, %g",
        """ A floating point property that controls the setpoint temperature
        in Kelvin for Loop 2. """
    )
    heater_range = Instrument.control(
        "RANGE?", "RANGE %d",
        """ A string property that controls the heater range, which
        can take the values: off, low, medium, and high. These values
        correlate to 0, 0.5, 5 and 50 W respectively. """,
        validator=strict_discrete_set,
        values={'off':0, 'low':1, 'medium':2, 'high':3},
        map_values=True
    )

    def __init__(self, adapter, **kwargs):
        super(LakeShore331, self).__init__(
            adapter,
            "Lake Shore 331 Temperature Controller",
            **kwargs
        )

    def disable_heater(self):
        """ Turns the :attr:`~.heater_range` to :code:`off` to disable the heater. """
        self.heater_range = 'off'

    def wait_for_temperature(self, accuracy=0.1, 
            interval=0.1, sensor='A', setpoint=1, timeout=360,
            should_stop=lambda: False):
        """ Blocks the program, waiting for the temperature to reach the setpoint
        within the accuracy (%), checking this each interval time in seconds.

        :param accuracy: An acceptable percentage deviation between the 
                         setpoint and temperature
        :param interval: A time in seconds that controls the refresh rate
        :param sensor: The desired sensor to read, either A or B
        :param setpoint: The desired setpoint loop to read, either 1 or 2
        :param timeout: A timeout in seconds after which an exception is raised
        :param should_stop: A function that returns True if waiting should stop, by
                            default this always returns False
        """
        temperature_name = 'temperature_%s' % sensor
        setpoint_name = 'setpoint_%d' % setpoint
        # Only get the setpoint once, assuming it does not change
        setpoint_value = getattr(self, setpoint_name)
        def percent_difference(temperature):
            return abs(100*(temperature - setpoint_value)/setpoint_value)
        t = time()
        while percent_difference(getattr(self, temperature_name)) > accuracy:
            sleep(interval)
            if (time()-t) > timeout:
                raise Exception((
                    "Timeout occurred after waiting %g seconds for "
                    "the LakeShore 331 temperature to reach %g K."
                ) % (timeout, setpoint))
            if should_stop():
                return

