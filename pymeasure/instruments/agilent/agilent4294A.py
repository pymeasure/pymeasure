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

from pymeasure.instruments import Instrument


class Agilent4294A(Instrument):
    """ Represents the Agilent 4294A Precision Impedance Analyzer """

    start_frequency = Instrument.control(
        "STAR?", "STAR %e HZ",
        """ A property that represents the start frequency in Hz. This property can be set.
        """
    )
    stop_frequency = Instrument.control(
        "STOP?", "STOP %e HZ",
        """ A property that represents the stop frequency in Hz. This property can be set.
        """
    )

    def __init__(self, adapter, name="Agilent 4294A Precision Impedance Analyzer", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        print(self.adapter.connection)
        print(type(self.adapter.connection))
        self.adapter.connection.timeout = 5000

        self._query = self.adapter.connection.query
        self._write = self.adapter.connection.write

    def save_graphics(self, filename=""):
        # Adapted from
        # https://www.keysight.com/se/en/lib/software-detail/programming-examples/4294a-data-transfer-program-excel-vba-1645196.html
        self._write("STOD MEMO")
        self._write("PRIC VARI")

        local_filename = filename + ".tiff"

        REMOTE_FILE = "agt4294a.tiff"  # Filename of the in-memory file on the device
        print("got here")
        result = self._write(f'SAVDTIF "{REMOTE_FILE}"')
        print(result)
        print("got here 2")

        # vErr = self.ask("OUTPERRO?").split(",")
        vErr = self._query("OUTPERRO?")
        print(vErr)
        print("got here 3")
        print(vErr)
        if not int(vErr[0]) == 0:
            self._write(f'PURG "{REMOTE_FILE}"')
            self._write(f'SAVDTIF "{REMOTE_FILE}"')
            vErr = self._query("OUTPERRO?").split(",")
            print(vErr)

        self._write(f'ROPEN "{REMOTE_FILE}"')
        lngFileSize = int(self.query(f'FSIZE? "{REMOTE_FILE}"'))
        print(lngFileSize)
        MAX_BUFF_SIZE = 16384
        iBufCnt = lngFileSize // MAX_BUFF_SIZE
        if lngFileSize % MAX_BUFF_SIZE > 0:
            iBufCnt += 1

        with open(local_filename, 'wb') as file:
            for _ in range(iBufCnt):
                data = self.query_binary_values("READ?", datatype='B', container=bytes)
                file.write(data)
            
        self._write(f'PURG "{REMOTE_FILE}"')

        return local_filename
