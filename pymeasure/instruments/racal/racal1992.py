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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from pymeasure.instruments.validators import strict_range
from pymeasure.instruments.validators import strict_discrete_range


class Racal1992(Instrument):
    """ Represents the Racal-Dana 1992 Universal counter

    .. code-block:: python

        from pymeasure.instruments.racal import Racal1992
        counter = Racal1992("GPIB0::10")

    """

    resolution = Instrument.control(
            None,
            "SRS %d",
            """ An integer from 3 to 9 that specifies the number
            of significant digits. """,
            validator=strict_discrete_range,
            values=range(3,10),
            map_values=True
    )

    def __init__(self, adapter, **kwargs):
        kwargs.setdefault('write_termination', '\r\n')

        super().__init__(
            adapter,
            "Racal-Dana 1992",
            **kwargs
        )

    def read_value_raw(self):
        v = self.read_bytes(21)
        return v

    @property
    def resolution(self):
        """Number of significant digits. 

        This must be an integer from 3 to 9.

        """

        self.write("RRS")
        return self.read_value_raw(self)

    @resolution.setter
    def resolution(self, value):
        strict_discrete_range(value, range(3,10), 1)
        self.write(f"SRS {value}")

