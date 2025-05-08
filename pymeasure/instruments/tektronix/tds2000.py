#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from pymeasure.instruments import Instrument, SCPIUnknownMixin


class TDS2000(SCPIUnknownMixin, Instrument):
    """ Represents the Tektronix TDS 2000 Oscilloscope
    and provides a high-level for interacting with the instrument
    """

    class Measurement:

        SOURCE_VALUES = ['CH1', 'CH2', 'MATH']

        TYPE_VALUES = [
            'FREQ', 'MEAN', 'PERI', 'PHA', 'PK2', 'CRM',
            'MINI', 'MAXI', 'RIS', 'FALL', 'PWI', 'NWI'
        ]

        UNIT_VALUES = ['V', 's', 'Hz']

        def __init__(self, parent, preamble="MEASU:IMM:"):
            self.parent = parent
            self.preamble = preamble

        @property
        def value(self):
            return self.parent.values("%sVAL?" % self.preamble)

        @property
        def source(self):
            return self.parent.ask("%sSOU?" % self.preamble).strip()

        @source.setter
        def source(self, value):
            if value in TDS2000.Measurement.SOURCE_VALUES:
                self.parent.write(f"{self.preamble}SOU {value}")
            else:
                raise ValueError("Invalid source ('{}') provided to {}".format(
                                 self.parent, value))

        @property
        def type(self):
            return self.parent.ask("%sTYP?" % self.preamble).strip()

        @type.setter
        def type(self, value):
            if value in TDS2000.Measurement.TYPE_VALUES:
                self.parent.write(f"{self.preamble}TYP {value}")
            else:
                raise ValueError("Invalid type ('{}') provided to {}".format(
                                 self.parent, value))

        @property
        def unit(self):
            return self.parent.ask("%sUNI?" % self.preamble).strip()

        @unit.setter
        def unit(self, value):
            if value in TDS2000.Measurement.UNIT_VALUES:
                self.parent.write(f"{self.preamble}UNI {value}")
            else:
                raise ValueError("Invalid unit ('{}') provided to {}".format(
                                 self.parent, value))

    def __init__(self, adapter, name="Tektronix TDS 2000 Oscilloscope", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        self.measurement = TDS2000.Measurement(self)
