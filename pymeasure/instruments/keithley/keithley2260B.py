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
from pymeasure.instruments.validators import strict_discrete_set

import logging
from warnings import warn

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley2260B(SCPIMixin, Instrument):
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
        """Control whether the source is enabled, takes values True or False. (bool)""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    current_limit = Instrument.control(
        ":SOUR:CURR?",
        ":SOUR:CURR %g",
        """Control the source current in amps. This is not checked against the allowed range.
        Depending on whether the instrument is in constant current or constant voltage mode,
        this might differ from the actual current achieved. (float)""",
    )

    voltage_setpoint = Instrument.control(
        ":SOUR:VOLT?",
        ":SOUR:VOLT %g",
        """Control the source voltage in volts. This is not checked against the allowed range.
        Depending on whether the instrument is in constant current or constant voltage mode,
        this might differ from the actual voltage achieved. (float)""",
    )

    power = Instrument.measurement(
        ":MEAS:POW?",
        """Get the power (in Watt) the dc power supply is putting out.
        """,
    )

    voltage = Instrument.measurement(
        ":MEAS:VOLT?",
        """Get the voltage (in Volt) the dc power supply is putting out.
        """,
    )

    current = Instrument.measurement(
        ":MEAS:CURR?",
        """Get the current (in Ampere) the dc power supply is putting out.
        """,
    )

    applied = Instrument.control(
        ":APPly?",
        ":APPly %g,%g",
        """Control voltage (volts) and current (amps) simultaneously.
        Values need to be supplied as tuple of (voltage, current). Depending on
        whether the instrument is in constant current or constant voltage mode,
        the values achieved by the instrument will differ from the ones set.
        """,
    )

    @property
    def error(self):
        """Get the next error of the instrument (list of code and message)."""
        warn("Deprecated to use `error`, use `next_error` instead.", FutureWarning)
        return self.next_error

    @property
    def enabled(self):
        """Control whether the output is enabled, see :attr:`output_enabled`."""
        log.warning('Deprecated property name "enabled", use the identical "output_enabled", '
                    'instead.', FutureWarning)
        return self.output_enabled

    @enabled.setter
    def enabled(self, value):
        log.warning('Deprecated property name "enabled", use the identical "output_enabled", '
                    'instead.', FutureWarning)
        self.output_enabled = value

    def shutdown(self):
        """ Disable output, call parent function"""
        self.output_enabled = False
        super().shutdown()
