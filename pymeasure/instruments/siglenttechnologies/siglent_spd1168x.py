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


class SPD1168X(SPDBase):
    """Represent the Siglent SPD1168X Power Supply.
    """

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter,
            name="Siglent Technologies SPD1168X Power Supply",
            **kwargs
        )
        self.CH1 = SPDChannel(self, 1)

    def shutdown(self):
        """ Ensures that the voltage is turned to zero
        and disables the output. """
        self.CH1.set_voltage(0.0)
        self.CH1.disable()


if __name__ == "__main__":
    psu = SPD1168X("TCPIP0::10.20.2.245::5025::SOCKET")
    print(psu.id)
    print(psu.selected_channel)
    psu.CH1.set_current = 1
    psu.CH1.output = False

    print(psu.CH1.set_voltage)
    print(psu.CH1.set_current)
    print(psu.CH1.voltage)
    print(psu.error)
