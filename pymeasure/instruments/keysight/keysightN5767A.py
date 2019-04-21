#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range


from pymeasure.adapters import VISAAdapter


class KeysightN5767A(Instrument):
    """ Represents the Keysight N5767A Power supply
    interface for interacting with the instrument.

    .. code-block:: python

    """
    ###############
    # Current (A) #
    ###############
    current_range = Instrument.control(
        ":CURR?", ":CURR %g",
        """ A floating point property that controls the DC current range in
        Amps, which can take values from 0 to 25 A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 25],
    )

    current = Instrument.measurement(":MEAS:CURR?",
        """ Reads a setting current in Amps. """
     )

    ###############
    # Voltage (V) #
    ###############
    voltage_range = Instrument.control(
        ":VOLT?", ":VOLT %g V",
        """ A floating point property that controls the DC voltage range in
        Volts, which can take values from 0 to 60 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 60]
    )

    voltage = Instrument.measurement("MEAS:VOLT?",
        """ Reads a DC voltage measurement in Volts. """
     )

    ##############
    #_status (0/1) #
    ##############
    _status = Instrument.measurement(":OUTP?",
        """ Read power supply current output status. """,
    )

    def enable(self):
        """ Enables the flow of current.
        """
        self.write(":OUTP 1")

    def disable(self):
        """ Disables the flow of current.
        """
        self.write(":OUTP 0")

    def is_enabled(self):
        """ Returns True if the current supply is enabled.
        """
        return bool(self._status)

    def __init__(self, adapter, **kwargs):
        super(KeysightN5767A, self).__init__(
            adapter, "Keysight N5767A power supply", **kwargs
        )
        # Set up data transfer format
        if isinstance(self.adapter, VISAAdapter):
            self.adapter.config(
                is_binary=False,
                datatype='float32',
                converter='f',
                separator=','
            )

    def check_errors(self):
        """ Read all errors from the instrument."""
        while True:
            err = self.values(":SYST:ERR?")
            if int(err[0]) != 0:
                errmsg = "Keysight N5767A: %s: %s" % (err[0],err[1])
                log.error(errmsg + '\n')
            else:
                break
