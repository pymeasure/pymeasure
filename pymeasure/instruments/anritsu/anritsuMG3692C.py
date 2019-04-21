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

from pymeasure.instruments import Instrument, discreteTruncate, RangeException


class AnritsuMG3692C(Instrument):
    """ Represents the Anritsu MG3692C Signal Generator
    """
    power = Instrument.control(
        ":POWER?;", ":POWER %g dBm;",
        """ A floating point property that represents the output power
        in dBm. This property can be set. """
    )
    frequency = Instrument.control(
        ":FREQUENCY?;", ":FREQUENCY %e Hz;",
        """ A floating point property that represents the output frequency
        in Hz. This property can be set. """
    )

    def __init__(self, resourceName, **kwargs):
        super(AnritsuMG3692C, self).__init__(
            resourceName,
            "Anritsu MG3692C Signal Generator",
            **kwargs
        )

    @property
    def output(self):
        """ A boolean property that represents the signal output state.
        This property can be set to control the output.
        """
        return int(self.ask(":OUTPUT?")) == 1

    @output.setter
    def output(self, value):
        if value:
            self.write(":OUTPUT ON;")
        else:
            self.write(":OUTPUT OFF;")

    def enable(self):
        """ Enables the signal output.
        """
        self.output = True

    def disable(self):
        """ Disables the signal output.
        """
        self.output = False

    def shutdown(self):
        """ Shuts down the instrument, putting it in a safe state.
        """
        # TODO: Implement modulation
        self.modulation = False
        self.disable()
