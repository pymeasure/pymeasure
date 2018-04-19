#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument, discreteTruncate, RangeException

import numpy as np
import re
from io import BytesIO


class Agilent4156(Instrument):
    """ Represents the Agilent 4155/4156 Semiconductor Parameter Analyzer
    and provides a high-level interface for taking I-V measurements.
    """

    SMU_CHANNELS = ["SMU1", "SMU2", "SMU3", "SMU4"]
    VSU_CHANNELS = ["VSU1", "VSU2"]
    VMU_CHANNELS = ["VMU1", "VMU2"]

    CHANNELS = SMU_CHANNELS + VSU_CHANNELS + VMU_CHANNELS

    def __init__(self, resourceName, **kwargs):
        super(Agilent4156, self).__init__(
            resourceName,
            "Agilent 4155/4156 Semiconductor Parameter Analyzer",
            **kwargs
        )

    analyzer_mode = Instrument.control(
        ":PAGE:CHAN:MODE?", ":PAGE:CHAN:MODE %s",
        """ A string property that controls the analyzer's operating mode,
        which can take the values 'sweep' or 'sampling'.""",
        validator=strict_discrete_set,
        values=['SWE', 'SAMP'],
        check_set_errors=True,
        check_get_errors=True
    )

    @staticmethod
    def send_to_channel(channel):
        """ Creates the command string corresponding to the channel """
        try:
            any(channel.upper() in x for x in CHANNELS)
        except:
            raise KeyError('Invalid channel name.')
        else:
            return ':PAGE:CHAN:' + channel.upper() + ':'

    @staticmethod
    def check_current_voltage_name(name):
        """ Checks if current and voltage names specified for channel
        conforms to the accepted naming scheme. Returns auto-corrected name
        starting with 'a' if name is unsuitable."""
        if (len(name) > 6) or not name[0].isalpha():
            name = 'a' + name[:5]
        return name

    @staticmethod
    def channel_in_group(ch, chlist):
        """ Checks that the specified channel belongs to a list of
        channels defined by chlist """
        if ch not in chlist:
            return False
        else:
            return True

    def save_in_display_list(self, name):
        """ Save the voltage or current in the instrument display list """
        self.write(':PAGE:DISP:MODE LIST')
        self.write(':PAGE:DISP:LIST ' + name)

    def save_in_variable_list(self, name):
        """ Save the voltage or current in the instrument variable list """
        self.write(':PAGE:DISP:MODE LIST')
        self.write(':PAGE:DISP:DVAR ' + name)

    def channel_mode(ch):
        return Instrument.control(
            send_to_channel(ch) + "MODE?", send_to_channel(ch) + ":MODE %s",
            """ A string property that controls the channel mode,
            which can take the values 'V', 'I' or 'COMM'.
            VPULSE AND IPULSE are not yet supported""",
            validator=strict_discrete_set,
            values=["V", "I", "COMM"],
            check_set_errors=True,
            check_get_errors=True
        )

    def channel_function(ch):
        if channel_in_group(ch, VMU_CHANNELS):
            raise ValueError("Cannot set channel function for VMU.")
        else:
            return Instrument.control(
            send_to_channel(ch) + "FUNC?", send_to_channel(ch) + ":FUNC %s",
            """ A string property that controls the channel function,
            which can take the values 'VAR1', 'VAR2', 'VARD' or 'CONS'.""",
            validator=strict_discrete_set,
            values=["VAR1", "VAR2", "VARD", "CONS"],
            check_set_errors=True,
            check_get_errors=True
        )

    @property
    def voltage_name(self, ch):
        """ Gets the voltage name of the analyzer channel """
        return self.ask(send_to_channel(ch) + "VNAM?")

    @voltage_name.setter
    def voltage_name(self, ch, name):
        """ Sets the voltage name of the analyzer channel.
        Checks to see that the name is acceptable by instrument """
        name = check_current_voltage_name(name)
        self.write(send_to_channel(ch) + "VNAM %s" % name)

    @property
    def current_name(self, ch):
        """ Gets the current name of the analyzer channel """
        if channel_in_group(ch, SMU_CHANNELS) is True:
            return self.ask(send_to_channel(ch) + "INAM?")
        else:
            return None

    @current_name.setter
    def current_name(self, ch, name):
        """ Sets the current name of the analyzer channel.
        Checks to see that the name is acceptable by instrument """
        if channel_in_group(ch, SMU_CHANNELS) is True:
            name = check_current_voltage_name(name)
            self.write(send_to_channel(ch) + "INAM %s" % name)
        else:
            raise ValueError("Cannot set current name for non-SMU units")





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
        """ Turns on averaging of a specific number between 0 and 999
        """
        if int(averages) > 999 or int(averages) < 0:
            raise RangeException("Averaging must be in the range 0 to 999")
        else:
            self.write("AVERO1")
            self.write("AVERFACT%d" % int(averages))

    def disable_averaging(self):
        """ Disables averaging """
        self.write("AVERO0")

    def is_averaging(self):
        """ Returns True if averaging is enabled """
        return self.ask("AVERO?") == '1\n'

    def restart_averaging(self, averages):
        if int(averages) > 999 or int(averages) < 0:
            raise RangeException("Averaging must be in the range 0 to 999")
        else:
            self.write("NUMG%d" % averages)

    def scan(self, averages=1, blocking=True, timeout=25, delay=0.1):
        """ Initiates a scan with the number of averages specified and
        blocks until the operation is complete if blocking is True
        """
        if averages == 1:
            self.disableAveraging()
            self.setSingleSweep()
        else:
            self.setAveraging(averages)
            self.write("*CLS;SRE 4;ESNB 1;")
            self.restartAveraging(averages)
            if blocking:
                self.adapter.wait_for_srq(timeout, delay)

    def is_scan_complete():
        pass  # TODO: Implement method for determining if the scan is completed

    def scan_single(self):
        """ Initiates a single scan """
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
    def data(self):
        """ Returns the real and imaginary data from the last scan
        """
        # TODO: Implement binary transfer instead of ASCII
        data = np.loadtxt(
            BytesIO(self.ask("FORM4;OUTPDATA")),
            delimiter=',',
            dtype=np.float32
        )
        return data[:, 0], data[:, 1]

    def log_magnitude(self, real, imaginary):
        """ Returns the magnitude in dB from a real and imaginary
        number or numpy arrays
        """
        return 20*np.log10(self.magnitude(real, imaginary))

    def magnitude(self, real, imaginary):
        """ Returns the magnitude from a real and imaginary
        number or numpy arrays
        """
        return np.sqrt(real**2 + imaginary**2)

    def phase(self, real, imaginary):
        """ Returns the phase in degrees from a real and imaginary
        number or numpy arrays
        """
        return np.arctan2(imaginary, real)*180/np.pi
