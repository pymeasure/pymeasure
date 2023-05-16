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
from pymeasure.instruments.validators import strict_discrete_set

import time
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley2260B(Instrument):
    """ Represents the Keithley 2260B Power Supply (minimal implementation)
    and provides a high-level interface for interacting with the instrument.

    For a connection through tcpip, the device only accepts
    connections at port 2268, which cannot be configured otherwise.
    example connection string: 'TCPIP::xxx.xxx.xxx.xxx::2268::SOCKET'
    the read termination for this interface is \n

    .. code-block:: python

        source = Keithley2260B("GPIB::1")
        source.voltage = 1
        print(source.voltage)
        print(source.current)
        print(source.power)
        print(source.applied)
    """

    def __init__(self, adapter, name="Keithley 2260B DC Power Supply",
                 read_termination="\n", **kwargs):
        super().__init__(
            adapter,
            name,
            read_termination=read_termination,
            **kwargs
        )

    output_enabled = Instrument.control(
        "OUTPut?",
        "OUTPut %d",
        """A boolean property that controls whether the source is enabled, takes
        values True or False.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    current_limit = Instrument.control(
        ":SOUR:CURR?",
        ":SOUR:CURR %g",
        """A floating point property that controls the source current
        in amps. This is not checked against the allowed range. Depending on
        whether the instrument is in constant current or constant voltage mode,
        this might differ from the actual current achieved.""",
    )

    voltage_setpoint = Instrument.control(
        ":SOUR:VOLT?",
        ":SOUR:VOLT %g",
        """A floating point property that controls the source voltage
        in volts. This is not checked against the allowed range. Depending on
        whether the instrument is in constant current or constant voltage mode,
        this might differ from the actual voltage achieved.""",
    )

    power = Instrument.measurement(
        ":MEAS:POW?",
        """Reads the power (in Watt) the dc power supply is putting out.
        """,
    )

    voltage = Instrument.measurement(
        ":MEAS:VOLT?",
        """Reads the voltage (in Volt) the dc power supply is putting out.
        """,
    )

    current = Instrument.measurement(
        ":MEAS:CURR?",
        """Reads the current (in Ampere) the dc power supply is putting out.
        """,
    )

    applied = Instrument.control(
        ":APPly?",
        ":APPly %g,%g",
        """Simultaneous control of voltage (volts) and current (amps).
        Values need to be supplied as tuple of (voltage, current). Depending on
        whether the instrument is in constant current or constant voltage mode,
        the values achieved by the instrument will differ from the ones set.
        """,
    )

    @property
    def enabled(self):
        log.warning('Deprecated property name "enabled", use the identical "output_enabled", '
                    'instead.', FutureWarning)
        return self.output_enabled

    @enabled.setter
    def enabled(self, value):
        log.warning('Deprecated property name "enabled", use the identical "output_enabled", '
                    'instead.', FutureWarning)
        self.output_enabled = value

    @property
    def error(self):
        """ Returns a tuple of an error code and message from a
        single error. """
        err = self.values(":system:error?")
        if len(err) < 2:
            err = self.read()  # Try reading again
        code = err[0]
        message = err[1].replace('"', "")
        return (code, message)

    def check_errors(self):
        """ Logs any system errors reported by the instrument.
        """
        code, message = self.error
        while code != 0:
            t = time.time()
            log.info("Keithley 2260B reported error: %d, %s" % (code, message))
            code, message = self.error
            if (time.time() - t) > 10:
                log.warning("Timed out for Keithley 2260B error retrieval.")

    def shutdown(self):
        """ Disable output, call parent function"""
        self.output_enabled = False
        super().shutdown()
