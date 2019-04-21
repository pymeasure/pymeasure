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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range

from time import sleep
from numpy import linspace


class SM7045D(Instrument):
    """ This is the class for the SM 70-45 D power supply.

    .. code-block:: python

        source = SM7045D("GPIB::8")

        source.ramp_to_zero(1)               # Set output to 0 before enabling
        source.enable()                      # Enables the output
        source.current = 1                   # Sets a current of 1 Amps

    """
    VOLTAGE_RANGE = [0, 70]
    CURRENT_RANGE = [0, 45]

    voltage = Instrument.control(
        "SO:VO?", "SO:VO %g",
        """ A floating point property that represents the output voltage
        setting of the power supply in Volts. This property can be set. """,
        validator=strict_range,
        values=VOLTAGE_RANGE
    )

    current = Instrument.control(
        "SO:CU?", "SO:CU %g",
        """ A floating point property that represents the output current of
        the power supply in Amps. This property can be set. """,
        validator=strict_range,
        values=CURRENT_RANGE
    )

    max_voltage = Instrument.control(
        "SO:VO:MA?", "SO:VO:MA %g",
        """ A floating point property that represents the maximum output
        voltage of the power supply in Volts. This property can be set. """,
        validator=strict_range,
        values=VOLTAGE_RANGE
    )

    max_current = Instrument.control(
        "SO:CU:MA?", "SO:VO:MA %g",
        """ A floating point property that represents the maximum output
        current of the power supply in Amps. This property can be set. """,
        validator=strict_range,
        values=CURRENT_RANGE
    )

    measure_voltage = Instrument.measurement(
        "ME:VO?",
        """ Measures the actual output voltage of the power supply in
        Volts. """,
    )

    measure_current = Instrument.measurement(
        "ME:CU?",
        """ Measures the actual output current of the power supply in
        Amps. """,
    )

    rsd = Instrument.measurement(
        "SO:FU:RSD?",
        """ Check whether remote shutdown is enabled/disabled and thus if the
        output of the power supply is disabled/enabled. """,
    )

    def __init__(self, resourceName, **kwargs):
        super(SM7045D, self).__init__(
            resourceName,
            "Delta Elektronika SM 70-45 D",
            **kwargs
        )

    def enable(self):
        """
        Disable remote shutdown, hence output will be enabled.
        """
        self.write("SO:FU:RSD 0")

    def disable(self):
        """
        Enables remote shutdown, hence input will be disabled.
        """
        self.write("SO:FU:RSD 1")

    def ramp_to_current(self, target_current, current_step=0.1):
        """
        Gradually increase/decrease current to target current.

        :param target_current: Float that sets the target current (in A)
        :param current_step: Optional float that sets the current steps
                             / ramp rate (in A/s)
        """

        curr = self.current
        n = round(abs(curr - target_current) / current_step) + 1
        for i in linspace(curr, target_current, n):
            self.current = i
            sleep(0.1)

    def ramp_to_zero(self, current_step=0.1):
        """
        Gradually decrease the current to zero.

        :param current_step: Optional float that sets the current steps
                             / ramp rate (in A/s)
        """

        self.ramp_to_current(0, current_step)

    def shutdown(self):
        """
        Set the current to 0 A and disable the output of the power source.
        """
        self.ramp_to_zero()
        self.disable()
