#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
import numpy as np
from time import sleep, time

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class LakeShoreTemperatureInputChannel(Channel):
    """ Temperature input channel on a lakeshore temperature monitor.
    """

    kelvin = Instrument.measurement('KRDG? {ch}', """Read the temperature in kelvin from a channel.""")
    celcius = Instrument.measurement('CRDG? {ch}', """Read the temperature in celcius from a channel.""")
    sensor = Instrument.measurement('SRDG? {ch}', """Read the temperature in sensor units from a channel.""")

    def wait_for_temperature(self, target, unit='kelvin', accuracy=0.1,
                             interval=1, timeout=360,
                             should_stop=lambda: False):
        """ Blocks the program, waiting for the temperature to reach the setpoint
        within the accuracy (%), checking this each interval time in seconds.

        :param target: Target temperature in kelvin, celcius, or sensor units.
        :param accuracy: An acceptable percentage deviation between the
                         target and temperature

        :param timeout: A timeout in seconds after which an exception is raised
        :param should_stop: A function that returns True if waiting should stop, by
                            default this always returns False
        """
        def percent_difference(temperature):
            return np.abs(100 * (temperature - target) / target)
        t = time()
        target_acquired = False
        while not target_acquired:
            reading = getattr(self, unit)
            reading = np.array([reading]) if self.id != '0' else np.array(reading)
            diff = percent_difference(reading)
            target_acquired = True if np.all(diff < accuracy) else False
            sleep(interval)
            if (time() - t) > timeout:
                raise Exception((
                            "Timeout occurred after waiting %g seconds for "
                            "the LakeShore 331 temperature to reach %g %s."
                        ) % (timeout, target, unit))
            if should_stop():
                return


class LakeShoreHeaterOutputChannel(Channel):
    """ Heater output channel on a lakeshore temperature controller.
    """

    output = Instrument.measurement('HTR? {ch}', """Query the heater output in percent of the max.""")
    mout = Instrument.control('MOUT? {ch}', 'MOUT {ch},%f', """Manual heater output in percent.""")
    range = Instrument.control('RANGE? {ch}', 'RANGE {ch},%i',
                               """String property controlling heater range, which can take the
                               values: off, low, medium, and high.""",
                               validator=strict_discrete_set,
                               values={'off': 0, 'low': 1, 'medium': 2, 'high': 3},
                               map_values=True)
    setpoint = Instrument.control(
        'SETP? {ch}', 'SETP {ch},%f', """A floating point property that control the setpoint temperature
        in the preferred units of the control loop sensor."""
    )
