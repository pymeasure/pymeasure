#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure Developers
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


class LakeShore331(Instrument):
    """Instrument object for the Lake Shore 331 Temperature Controller"""

    temperature_A = Instrument.measurement(
        "KRDG? A",
        """ Reads the temperature of the sensor A in Kelvin """
    )
    temperature_A = Instrument.measurement(
        "KRDG? B",
        """ Reads the temperature of the sensor B in Kelvin """
    )

    def __init__(self, adapter, **kwargs):
        super(LakeShore331, self).__init__(
            adapter,
            "Lake Shore 331 Temperature Controller",
            **kwargs
        )