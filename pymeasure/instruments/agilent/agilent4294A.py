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

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_range, strict_discrete_set
import pandas as pd
import numpy as np
import os

# Set of valid arguments for the MEAS? command
MEASUREMENT_TYPES = [
    "IMPH",
    "IRIM",
    "LSR",
    "LSQ",
    "CSR",
    "CSQ",
    "CSD",
    "AMPH",
    "ARIM",
    "LPG",
    "LPQ",
    "CPG",
    "CPQ",
    "CPD",
    "COMP",
    "IMLS",
    "IMCS",
    "IMLP",
    "IMCP",
    "IMRS",
    "IMQ",
    "IMD",
    "LPR",
    "CPR",
]


class Agilent4294A(SCPIMixin, Instrument):
    """ Represents the Agilent 4294A Precision Impedance Analyzer """

    def __init__(self, adapter, name="Agilent 4294A Precision Impedance Analyzer",
                 read_termination="\n",
                 write_termination="\n",
                 timeout=5000,
                 **kwargs):

        super().__init__(
            adapter,
            name,
            read_termination=read_termination,
            write_termination=write_termination,
            timeout=timeout,
            **kwargs
        )

    start_frequency = Instrument.control(
        "STAR?", "STAR %d HZ", "Control the start frequency in Hz",
        validator=strict_range, values=[40, 140E6]
    )

    stop_frequency = Instrument.control(
        "STOP?", "STOP %d HZ", "Control the stop frequency in Hz",
        validator=strict_range, values=[40, 140E6]
    )

    num_points = Instrument.control(
        "POIN?", "POIN %d", "Control the number of points measured at each sweep",
        validator=strict_discrete_set, values=range(2, 802),
        cast=int,
    )

    measurement_type = Instrument.control(
        "MEAS?", "MEAS %d", "Control the measurement type. See MEASUREMENT_TYPES",
        validator=strict_discrete_set, values=MEASUREMENT_TYPES,
    )

    active_trace = Instrument.control(
        "TRAC?", "TRAC %s", "Control the active trace",
        validator=strict_discrete_set, values=["A", "B"]
    )

    title = Instrument.control(
        "TITL?", 'TITL "%s"', "Control the title of the active trace"
    )

    def save_graphics(self, path=""):
        """ Save graphics on the screen to a file on the local computer.
        Adapted from:
        https://www.keysight.com/se/en/lib/software-detail/programming-examples/4294a-data-transfer-program-excel-vba-1645196.html
        """

        self.write("STOD MEMO")  # store to internal memory
        self.write("PRIC VARI")  # save a color image

        root, ext = os.path.splitext(path)
        if ext != ".tiff":
            ext = ".tiff"
        if not root:
            root = "graphics"

        path = root + ext

        REMOTE_FILE = "agt4294a.tiff"  # Filename of the in-memory file on the device
        self.write(f'SAVDTIF "{REMOTE_FILE}"')

        vErr = self.ask("OUTPERRO?").split(",")
        if not int(vErr[0]) == 0:
            self.write(f'PURG "{REMOTE_FILE}"')
            self.write(f'SAVDTIF "{REMOTE_FILE}"')
            vErr = self.ask("OUTPERRO?").split(",")

        self.write(f'ROPEN "{REMOTE_FILE}"')
        lngFileSize = int(self.ask(f'FSIZE? "{REMOTE_FILE}"'))
        MAX_BUFF_SIZE = 16384
        iBufCnt = lngFileSize // MAX_BUFF_SIZE
        if lngFileSize % MAX_BUFF_SIZE > 0:
            iBufCnt += 1

        with open(path, 'wb') as file:
            for _ in range(iBufCnt):
                data = self.adapter.connection.query_binary_values("READ?", datatype='B',
                                                                   container=bytes)
                file.write(data)
        self.write(f'PURG "{REMOTE_FILE}"')

        return path

    def get_data(self, path=None):
        """
        Get the measurement data from the instrument after completion.

        :param path: Path for optional data export to CSV.
        :returns: Pandas Dataframe
        """
        prev_active_trace = self.active_trace

        num_points = self.num_points
        freqs = np.array(self.ask("OUTPSWPRM?").split(","), dtype=float)
        self.active_trace = "A"
        adata = np.array(self.ask("OUTPDTRC?").split(","), dtype=float).reshape(num_points, 2)

        self.active_trace = "B"
        bdata = np.array(self.ask("OUTPDTRC?").split(","), dtype=float).reshape(num_points, 2)

        # restore the previous state
        self.active_trace = prev_active_trace

        df = pd.DataFrame(
            np.hstack((freqs.reshape(-1, 1), adata, bdata)),
            columns=["Frequency", "A Real", "A Imag", "B Real", "B Imag"]
        )

        if path is not None:
            _, ext = os.path.splitext(path)
            if ext != ".csv":
                path = path + ".csv"
            df.to_csv(path, index=False)

        return df
