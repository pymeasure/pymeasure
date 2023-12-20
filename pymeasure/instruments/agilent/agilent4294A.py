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
from pymeasure.instruments.validators import strict_range


class Agilent4294A(Instrument):
    """ Represents the Agilent 4294A Precision Impedance Analyzer """

    start_frequency = Instrument.control(
        "STAR?", "STAR %e HZ", "Set the start frequency in Hz",
        validator=strict_range, values=[40, 140E6]
    )
    stop_frequency = Instrument.control(
        "STOP?", "STOP %e HZ", "Set the stop frequency in Hz",
        validator=strict_range, values=[40, 140E6]
    )
    title = Instrument.control(
        "TITL?", 'TITL "%s"', "Set the title of the plot"
    )

    def __init__(self, adapter, name="Agilent 4294A Precision Impedance Analyzer", **kwargs):
        kwargs["read_termination"] = "\n"
        kwargs["write_termination"] = "\n"
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        self.adapter.connection.timeout = 5000

    def save_graphics(self, filename=""):
        """ Save graphics on the screen to a file on the local computer.
        Adapted from:
        https://www.keysight.com/se/en/lib/software-detail/programming-examples/4294a-data-transfer-program-excel-vba-1645196.html
        """

        self.write("STOD MEMO")  # store to internal memory
        self.write("PRIC VARI")  # save a color image
        local_filename = filename + ".tiff"

        REMOTE_FILE = "agt4294a.tiff"  # Filename of the in-memory file on the device
        self.write(f'SAVDTIF "{REMOTE_FILE}"')

        vErr = self.ask("OUTPERRO?").split(",")
        print(vErr)
        if not int(vErr[0]) == 0:
            self.write(f'PURG "{REMOTE_FILE}"')
            self.write(f'SAVDTIF "{REMOTE_FILE}"')
            vErr = self.ask("OUTPERRO?").split(",")
            print(vErr)

        self.write(f'ROPEN "{REMOTE_FILE}"')
        lngFileSize = int(self.ask(f'FSIZE? "{REMOTE_FILE}"'))
        print(lngFileSize)
        MAX_BUFF_SIZE = 16384
        iBufCnt = lngFileSize // MAX_BUFF_SIZE
        if lngFileSize % MAX_BUFF_SIZE > 0:
            iBufCnt += 1

        with open(local_filename, 'wb') as file:
            for _ in range(iBufCnt):
                data = self.adapter.connection.query_binary_values("READ?", datatype='B',
                                                                   container=bytes)
                file.write(data)
        self.write(f'PURG "{REMOTE_FILE}"')

        return local_filename
