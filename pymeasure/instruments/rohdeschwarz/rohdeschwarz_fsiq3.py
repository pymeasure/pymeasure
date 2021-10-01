#
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

from pymeasure.instruments.rf_signal_generator import RFSignalGenerator
class HPD4000A(RFSignalGenerator):
    """ Class representing "HP D4000A/Agilent E4433A RF signal generator """

    # Define instrument limits according to datasheet
    power_values = (-136.0, 13.0)
    frequency_values = (250e3, 4e9)

    name = "HP D4000A Signal Generator"
    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            self.name,
            **kwargs
        )

    @property
    def id(self):
        """ Requests and returns the identification of the instrument. """
        return_value = self.ask("*IDN?").strip().split(",")
        # Swap second and third entry since they are not following SCPI order.
        # The second entry should be model
        return_value[1], return_value[2] = return_value[2], return_value[1]
        return ",".join(return_value)

