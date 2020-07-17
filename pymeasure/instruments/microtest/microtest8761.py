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


from pymeasure.adapters import VISAAdapter

from pymeasure.instruments import Instrument
import logging
import re
import time
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Microtest8761(Instrument):
    """ Represents the microtest 8761 cable harness tester,
    interface for interacting with the instrument.

    It can also be used for microtest 8740 8751 and 8700
    """

    def __init__(self, adapter=VISAAdapter, **kwargs):
        super().__init__(adapter, "microtest 8761", **kwargs)

    def test(self, timeout=2000):
        """ Read Conductance data.
            timeout unit: ms
        """
        self.adapter.write(":KEY TEST")
        self.adapter.connection.timeout = timeout
        data = self.adapter.connection.read_raw()
        self.adapter.connection.read_raw()

        return data

        # self.data = self.query_binary_values(":KEY TEST")

    def dataFormat(self, data):
        """Convert binary string to list.
            returm list of name, resistance and unit.
        """
        # replace useless characters.
        data = data.replace(b'\xea', b' ohm ')
        data = data.replace(b'X ', b'')
        data = data.replace(b'>', b'')
        data = data.replace(b'\00', b'').decode('ascii').strip()

        # split string to list by \s
        datalist = re.split(r'[\s]+', data)

        namelist = []
        resistance = []
        unit = []
        for i in range(len(datalist)):
            if(datalist[i] == 'COND'):
                namelist.append(datalist[i+1])
                resistance.append(float(datalist[i+2]))
                unit.append(datalist[i+3])

        return namelist, resistance, unit
