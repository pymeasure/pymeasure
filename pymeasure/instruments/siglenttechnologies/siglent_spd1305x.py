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
from pymeasure.instruments.siglenttechnologies.siglent_spdbase import SPDBase, SPDChannel


class SPD1305X(SPDBase):
    """Represent the Siglent SPD1305X Power Supply.
    """

    def __init__(self, adapter, **kwargs):

        super().__init__(
            adapter,
            name="Siglent Technologies SPD1305X Power Supply",
            **kwargs
        )
        voltage_limits = [0, 30]
        current_limits = [0, 5]

        self.ch = {}
        self.ch[1] = SPDChannel(self, 1)

        self.ch[1].voltage_setpoint_values = voltage_limits
        self.ch[1].current_limit_values = current_limits

    def shutdown(self):
        """ Ensures that the voltage is turned to zero
        and disables the output. """
        self.ch[1].voltage_setpoint = 0
        self.ch[1].enable_output(False)
