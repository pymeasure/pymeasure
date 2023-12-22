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
import re
import warnings
from functools import cached_property
from io import BytesIO
from time import sleep
from time import time as now

import numpy as np
from pyvisa import VisaIOError

from pymeasure.adapters import PrologixAdapter
from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import truncated_range, discreteTruncate, strict_discrete_set


class HP8753E(Instrument):
    """Represents the HP8753E Vector Network Analyzer
    and provides a high-level interface for taking scans of the
    scattering parameters.

    Keyword arguements:
    adapter -- <placeholder for description of pymeasure.adapter>
    name -- <str> describing the instrument
    """

    def __init__(self, adapter=None, name="Hewlett Packard 8753E Vector Network Analyzer", **kwargs):
        super().__init__(adapter, name, includeSCPI=False, **kwargs)

    SCAN_POINT_VALUES = [3, 11, 21, 26, 51, 101, 201, 401, 801, 1601]
    SCATTERING_PARAMETERS = ["S11", "S12", "S21", "S22"]
    S11, S12, S21, S22 = SCATTERING_PARAMETERS

    start_frequency = Instrument.control(
        "STAR?",
        "STAR %e Hz",
        """Control the start frequency in Hz. (float truncated from 30_000.0
        to 6_000_000_000.0).
        """,
        validator=truncated_range,
        cast=float,
        values=[30E3, 6E9],
    )
    stop_frequency = Instrument.control(
        "STOP?",
        "STOP %e Hz",
        """Control the stop frequency in Hz. (float truncated from 30_000.0
        to 6_000_000_000.0).
        """,
        validator=truncated_range,
        cast=float,
        values=[30E3, 6E9],
    )
    sweep_time = Instrument.control(
        "SWET?",
        "SWET%.2e",
        """Control the sweep time in seconds. (float truncated from 0.0 to 999.0)
        """,
        validator=truncated_range,
        cast=float,
        values=[30E3, 6E9]
    )
    averages = Instrument.control(
        "AVERFACT?",
        "AVERFACT%d",
        """ An integer representing the number of averages to take. Note that
        averaging must be enabled for this to take effect. This property can be set.
        """,
        cast=lambda x: int(float(x)),  # need float() to convert scientific notation in strings
        validator=discreteTruncate,
        values=[0, 999],
    )
    averaging_enabled = Instrument.control(
        "AVERO?",
        "AVERO%d",
        """ A bool that indicates whether or not averaging is enabled. This property
        can be set.""",
        cast=bool,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    correction_enabled = Instrument.control(
        "CORR?",
        "CORR%d",
        """ A bool that indicates whether or not correction is enabled. This property
        can be set.""",
        cast=bool,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    power = Instrument.control(
        "POWE?",
        "POWE%.2e",
        """ A float that can be set from -70 to +10dBm to control output power from
        the VNA ports. This property can be set.""",
        cast=float,
        validator=truncated_range,
        values=[-70, 10],
    )

    id = Instrument.measurement(
        '*IDN?',
        """Gets the identification of the instrument""",
        cast=str
    )

    sn = Instrument.measurement(
        'OUTPSERN',
        """Get the serial number of the HP8753E""",
    )

    options = Instrument.measurement(
        'OUTPOPTS',
        """Get the installed options for the HP8753E""",
    )

    @property
    def manu(self):
        """Get the manufacturer of the instrument."""
        try:
            return self._manu
        except AttributeError:
            self._manu, self._model, _, self._fw = self.id
            return self._manu

    @property
    def model(self):
        """Get the model of the instrument."""
        try:
            return self._model
        except AttributeError:
            self._manu, self._model, _, self._fw = self.id
            return self._model

    @property
    def fw(self):
        """Get the firmware of the instrument."""
        try:
            return self._fw
        except AttributeError:
            self._manu, self._model, _, self._fw = self.id
            return self._fw

    def set_fixed_frequency(self, frequency):
        """Set the sweep to be a fixed frequency in Hz. (float truncated from 30_000.0 to 6_000_000_000.0)"""
        self.start_frequency = frequency
        self.stop_frequency = frequency
        self.scan_points = 3

    @property
    def parameter(self):
        for parameter in HP8753E.SCATTERING_PARAMETERS:
            if int(self.ask(f"{parameter}?")) == 1:
                return parameter
        return None

    @parameter.setter
    def parameter(self, value):
        if value in HP8753E.SCATTERING_PARAMETERS:
            self.write("%s" % value)
        else:
            raise Exception("Invalid scattering parameter requested" " for Hewlett Packard 8753E")

    @property
    def scan_points(self):
        """Gets the number of scan points"""
        search = re.search(r"\d\.\d+E[+-]\d{2}$", self.ask("POIN?"), re.MULTILINE)
        if search:
            return int(float(search.group()))
        else:
            raise Exception("Improper message returned for the" " number of points")

    @scan_points.setter
    def scan_points(self, points):
        """Sets the number of scan points, truncating to an allowed
        value if not properly provided
        """
        points = discreteTruncate(points, HP8753E.SCAN_POINT_VALUES)
        if points:
            self.write("POIN%d" % points)
        else:
            raise RangeException("Maximum scan points (1601) for" " Hewlett Packard 8753E exceeded")

    @property
    def IFBW(self):
        """Gets the IF Bandwidth"""
        search = re.search(r"\d\.\d+E[+-]\d{2}$", self.ask("IFBW?"), re.MULTILINE)
        if search:
            return int(float(search.group()))
        else:
            raise Exception("Improper message returned for the" " IF Bandwidth")

    @IFBW.setter
    def IFBW(self, bandwidth):
        """Sets the resolution bandwidth (IF bandwidth)"""
        allowedBandwidth = [10, 30, 100, 300, 1000, 3000, 3700, 6000]
        bandwidth = discreteTruncate(bandwidth, allowedBandwidth)
        if bandwidth:
            self.write("IFBW%d" % bandwidth)
        else:
            raise RangeException(
                "Maximum IF bandwidth (6000) for Hewlett Packard " "8753E exceeded"
            )

    def reset(self):
        self.write("*RST")
        sleep(0.25)

    def scan(self, averages=None, blocking=None, timeout=None, delay=None):
        """Initiates a scan with the number of averages specified and
        blocks until the operation is complete.
        """
        if averages is not None or blocking is not None or timeout is not None or delay is not None:
            warnings.warn(
                "averages, blocking, timeout, and delay arguments are no longer used by scan()",
                FutureWarning,
            )

        self.scan_single()

        # All queries will block until the scan is done, so use NOOP? to check.
        # These queries will time out after several seconds though,
        # so query repeatedly until the scan finishes.
        status = "1\r\n"
        while True:
            try:
                status = self.ask("NOOP?")
                break
            except VisaIOError as e:
                if e.abbreviation != "VI_ERROR_TMO":
                    raise e
            finally:
                if self.adapter.connection.bytes_in_buffer > 0:
                    self.adapter.flush_read_buffer()

        self.adapter.flush_read_buffer()
        sleep(0.1)

    def scan_single(self):
        """Initiates a single scan"""

        # sometimes the averaging enabled question trips up the 8753E
        for i in range(5):
            try:
                averaging_enabled = self.averaging_enabled
                break
            except VisaIOError as e:
                sleep(0.2)
                if e.abbreviation != "VI_ERROR_TMO":
                    raise e
                if i == 4:
                    raise e
        if averaging_enabled:
            self.write(f"NUMG{self.averages}")
        else:
            self.write("SING")

    def scan_continuous(self):
        """Initiates a continuous scan"""
        self.write("CONT")
        self.adapter.flush_read_buffer()

    @property
    def frequencies(self):
        """Returns a list of frequencies from the last scan"""
        return np.linspace(self.start_frequency, self.stop_frequency, num=self.scan_points)

    @property
    def data_complex(self):
        """Returns the complex power from the last scan"""
        # TODO: Implement binary transfer instead of ASCII

        # get number of points
        points = self.scan_points

        # TODO get data format
        self.write("FORM4")

        self.adapter.flush_read_buffer()

        if isinstance(self.adapter, PrologixAdapter):
            temp_data = []

            # set adapter to auto
            auto_state = self.adapter.auto
            self.adapter.auto = 1
            start = now()
            self.write("OUTPDATA")

            # if form4 is the data transfer method
            while len(temp_data) < (points):
                if self.adapter.connection.bytes_in_buffer >= 50:
                    temp_data.append(self.read_bytes(50).decode("utf-8").strip("\n").split(","))
                else:
                    # try not to overwhelm the prologix adapter
                    sleep(0.0001)

                # break the loop if the sweep gets interrupted
                time_elapsed = now() - start
                if time_elapsed > points * 0.006:
                    if self.adapter.connection.bytes_in_buffer > 0:
                        self.adapter.flush_read_buffer()
                        sleep(0.05)
                    raise Exception(f"Failed to read data. Data transfer method timed out")

            # process string data into complex numbers
            preformat_data = [float(point[0]) + float(point[1]) * 1j for point in temp_data]
            data = np.array(preformat_data)

            # return adapter to previous auto state for prologix adapter
            self.adapter.auto = auto_state

            # data_complex = data[:, 0] + 1j * data[:, 1]
            return data
        else:
            raise NotImplementedError("Function data_complex only written for PrologixAdapter")

    def check_errors(self):
        pass

    def shutdown(self):
        pass


