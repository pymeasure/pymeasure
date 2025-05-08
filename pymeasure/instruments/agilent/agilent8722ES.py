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
from pymeasure.instruments.validators import discreteTruncate
from pymeasure.errors import RangeException
from pyvisa import VisaIOError

import numpy as np
import re
from io import BytesIO
import warnings


class Agilent8722ES(SCPIUnknownMixin, Instrument):
    """ Represents the Agilent8722ES Vector Network Analyzer
    and provides a high-level interface for taking scans of the
    scattering parameters.
    """

    SCAN_POINT_VALUES = [3, 11, 21, 26, 51, 101, 201, 401, 801, 1601]
    SCATTERING_PARAMETERS = ("S11", "S12", "S21", "S22")
    S11, S12, S21, S22 = SCATTERING_PARAMETERS

    start_frequency = Instrument.control(
        "STAR?", "STAR %e Hz",
        """ A floating point property that represents the start frequency
        in Hz. This property can be set.
        """
    )
    stop_frequency = Instrument.control(
        "STOP?", "STOP %e Hz",
        """ A floating point property that represents the stop frequency
        in Hz. This property can be set.
        """
    )
    sweep_time = Instrument.control(
        "SWET?", "SWET%.2e",
        """ A floating point property that represents the sweep time
        in seconds. This property can be set.
        """
    )
    averages = Instrument.control(
        "AVERFACT?", "AVERFACT%d",
        """ An integer representing the number of averages to take. Note that
        averaging must be enabled for this to take effect. This property can be set.
        """,
        cast=lambda x: int(float(x))  # need float() to convert scientific notation in strings
    )
    averaging_enabled = Instrument.control(
        "AVERO?", "AVERO%d",
        """ A bool that indicates whether or not averaging is enabled. This property
        can be set.""",
        cast=bool
    )

    def __init__(self, adapter, name="Agilent 8722ES Vector Network Analyzer", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    def set_fixed_frequency(self, frequency):
        """ Sets the scan to be of only one frequency in Hz """
        self.start_frequency = frequency
        self.stop_frequency = frequency
        self.scan_points = 3

    @property
    def parameter(self):
        for parameter in Agilent8722ES.SCATTERING_PARAMETERS:
            if int(self.values("%s?" % parameter)) == 1:
                return parameter
        return None

    @parameter.setter
    def parameter(self, value):
        if value in Agilent8722ES.SCATTERING_PARAMETERS:
            self.write("%s" % value)
        else:
            raise Exception("Invalid scattering parameter requested"
                            " for Agilent 8722ES")

    @property
    def scan_points(self):
        """ Gets the number of scan points
        """
        search = re.search(r"\d\.\d+E[+-]\d{2}$", self.ask("POIN?"),
                           re.MULTILINE)
        if search:
            return int(float(search.group()))
        else:
            raise Exception("Improper message returned for the"
                            " number of points")

    @scan_points.setter
    def scan_points(self, points):
        """ Sets the number of scan points, truncating to an allowed
        value if not properly provided
        """
        points = discreteTruncate(points, Agilent8722ES.SCAN_POINT_VALUES)
        if points:
            self.write("POIN%d" % points)
        else:
            raise RangeException("Maximum scan points (1601) for"
                                 " Agilent 8722ES exceeded")

    def set_IF_bandwidth(self, bandwidth):
        """ Sets the resolution bandwidth (IF bandwidth) """
        allowedBandwidth = [10, 30, 100, 300, 1000, 3000, 3700, 6000]
        bandwidth = discreteTruncate(bandwidth, allowedBandwidth)
        if bandwidth:
            self.write("IFBW%d" % bandwidth)
        else:
            raise RangeException("Maximum IF bandwidth (6000) for Agilent "
                                 "8722ES exceeded")

    def set_averaging(self, averages):
        """Sets the number of averages and enables/disables averaging. Should be
        between 1 and 999"""
        averages = int(averages)
        if not 1 <= averages <= 999:
            assert RangeException("Set", averages, "must be in the range 1 to 999")
        self.averages = averages
        self.averaging_enabled = (averages > 1)

    def disable_averaging(self):
        """Disables averaging"""
        warnings.warn(
            "Don't use disable_averaging(), use averaging_enabled = False instead", FutureWarning)
        self.averaging_enabled = False

    def enable_averaging(self):
        """Enables averaging"""
        warnings.warn(
            "Don't use enable_averaging(), use averaging_enabled = True instead", FutureWarning)
        self.averaging_enabled = True

    def is_averaging(self):
        """ Returns True if averaging is enabled """
        warnings.warn("Don't use is_averaging(), use averaging_enabled instead", FutureWarning)
        return self.averaging_enabled

    def restart_averaging(self, averages):
        warnings.warn("Don't use restart_averaging(), use scan_single() instead", FutureWarning)
        self.scan_single()

    def scan(self, averages=None, blocking=None, timeout=None, delay=None):
        """ Initiates a scan with the number of averages specified and
        blocks until the operation is complete.
        """
        if averages is not None or blocking is not None or timeout is not None or delay is not None:
            warnings.warn(
                "averages, blocking, timeout, and delay arguments are no longer used by scan()",
                FutureWarning
            )
        self.write("*CLS")
        self.scan_single()
        # All queries will block until the scan is done, so use NOOP? to check.
        # These queries will time out after several seconds though,
        # so query repeatedly until the scan finishes.
        while True:
            try:
                self.ask("NOOP?")
            except VisaIOError as e:
                if e.abbreviation != "VI_ERROR_TMO":
                    raise e
            else:
                break

    def scan_single(self):
        """ Initiates a single scan """
        if self.averaging_enabled:
            self.write("NUMG%d" % self.averages)
        else:
            self.write("SING")

    def scan_continuous(self):
        """ Initiates a continuous scan """
        self.write("CONT")

    @property
    def frequencies(self):
        """ Returns a list of frequencies from the last scan
        """
        return np.linspace(
            self.start_frequency,
            self.stop_frequency,
            num=self.scan_points
        )

    @property
    def data_complex(self):
        """ Returns the complex power from the last scan
        """
        # TODO: Implement binary transfer instead of ASCII
        data = np.loadtxt(
            BytesIO(self.ask("FORM4;OUTPDATA").encode()),
            delimiter=',',
            dtype=np.float32
        )
        data_complex = data[:, 0] + 1j * data[:, 1]
        return data_complex

    @property
    def data_log_magnitude(self):
        """ Returns the absolute magnitude values in dB from the last scan
        """
        return 20 * np.log10(self.data_magnitude)

    @property
    def data_magnitude(self):
        """ Returns the absolute magnitude values from the last scan
        """
        return np.abs(self.data_complex)

    @property
    def data_phase(self):
        """ Returns the phase in degrees from the last scan
        """
        return np.degrees(np.angle(self.data_complex))

    @property
    def data(self):
        """ Returns the real and imaginary data from the last scan
        """
        warnings.warn("Don't use this function, use data_complex instead", FutureWarning)
        data_complex = self.data_complex
        return data_complex.real, data_complex.complex

    def log_magnitude(self, real, imaginary):
        """ Returns the magnitude in dB from a real and imaginary
        number or numpy arrays
        """
        warnings.warn("Don't use log_magnitude(), use data_log_magnitude instead", FutureWarning)
        return 20 * np.log10(self.magnitude(real, imaginary))

    def magnitude(self, real, imaginary):
        """ Returns the magnitude from a real and imaginary
        number or numpy arrays
        """
        warnings.warn("Don't use magnitude(), use data_magnitude", FutureWarning)
        return np.sqrt(real**2 + imaginary**2)

    def phase(self, real, imaginary):
        """ Returns the phase in degrees from a real and imaginary
        number or numpy arrays
        """
        warnings.warn("Don't use phase(), use data_phase instead", FutureWarning)
        return np.arctan2(imaginary, real) * 180 / np.pi
