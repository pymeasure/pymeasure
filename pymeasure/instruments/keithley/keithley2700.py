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

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

from .buffer import KeithleyBuffer

import numpy as np
import time
from io import BytesIO
import re


def clist_validator(value, values):
    """ Provides a validator function that returns a valid clist string
    for channel commands of the Keithley 2700. Otherwise it raises a
    ValueError.

    :param value: A value to test
    :param values: A range of values (range, list, etc.)
    :raises: ValueError if the value is out of the range
    """
    # Convert value to list of strings
    if isinstance(value, str):
        clist = [value.strip(" @(),")]
    elif isinstance(value, (int, float)):
        clist = ["{:d}".format(value)]
    elif isinstance(value, (list, tuple, np.ndarray, range)):
        clist = ["{:d}".format(x) for x in value
                 if x in values]
    else:
        raise ValueError("Type of value ({}) not valid".format(type(value)))

    # Pad numbers to length (if required)
    clist = [c.rjust(3, "1") for c in clist]

    # Check channels against valid channels
    for c in clist:
        if int(c) not in values:
            raise ValueError(
                "Channel number {:g} not valid.".format(value)
            )

    # Convert list of strings to clist format
    clist = "(@{:s})".format(", ".join(clist))

    return clist


class Keithley2700(Instrument, KeithleyBuffer):
    """ Represents the Keithely 2700 Multimeter/Switch System and provides a
    high-level interface for interacting with the instrument.

    .. code-block:: python

        keithley = Keithley2700("GPIB::1")

    """

    CLIST_VALUES = list(range(101, 300))

    # Routing commands
    closed_channels = Instrument.control(
        "ROUTe:MULTiple:CLOSe?", "ROUTe:MULTiple:CLOSe %s",
        """ Parameter that controls the opened and closed channels.
        All mentioned channels are closed, other channels will be opened.
        """,
        validator=clist_validator,
        values=CLIST_VALUES,
        check_get_errors=True,
        check_set_errors=True,
        separator=None,
        get_process=lambda v: [
            int(vv) for vv in (v.strip(" ()@,").split(",")) if not vv == ""
        ],
    )

    open_channels = Instrument.setting(
        "ROUTe:MULTiple:OPEN %s",
        """dd""",
        validator=clist_validator,
        values=CLIST_VALUES,
        check_set_errors=True
    )

    def get_state_of_channels(self, channels):
        clist = clist_validator(channels, self.CLIST_VALUES)
        state = self.ask("ROUTe:MULTiple:STATe? %s" % clist)
        print(state)

    def open_all_channels(self):
        self.write(":ROUTe:OPEN:ALL")

    def __init__(self, adapter, **kwargs):
        super(Keithley2700, self).__init__(
            adapter, "Keithley 2700 MultiMeter/Switch System", **kwargs
        )

        self.check_errors()
        self.determine_valid_channels()

    def determine_valid_channels(self):
        self.CLIST_VALUES.clear()

        for position, card in enumerate(self.options, 1):

            if card == "none":
                continue
            elif card == "7709":
                """The 7709 is a 6(rows) x 8(columns) matrix card that, with two
                additional switches (49 & 50) that allow row 1 and 2 to be
                connected to the DMM backplane (input and sense respectively).
                """
                channels = range(1, 51)
            else:
                continue

            channels = [100 * position + ch for ch in channels]

            self.CLIST_VALUES.extend(channels)

    # system, some taken from Keithley 2400
    def beep(self, frequency, duration):
        """ Sounds a system beep.

        :param frequency: A frequency in Hz between 65 Hz and 2 MHz
        :param duration: A time in seconds between 0 and 7.9 seconds
        """
        self.write(":SYST:BEEP %g, %g" % (frequency, duration))

    def triad(self, base_frequency, duration):
        """ Sounds a musical triad using the system beep.

        :param base_frequency: A frequency in Hz between 65 Hz and 1.3 MHz
        :param duration: A time in seconds between 0 and 7.9 seconds
        """
        self.beep(base_frequency, duration)
        time.sleep(duration)
        self.beep(base_frequency * 5.0 / 4.0, duration)
        time.sleep(duration)
        self.beep(base_frequency * 6.0 / 4.0, duration)

    @property
    def error(self):
        """ Returns a tuple of an error code and message from a
        single error. """
        err = self.values(":system:error?")
        if len(err) < 2:
            err = self.read()  # Try reading again
        code = err[0]
        message = err[1].replace('"', '')
        return (code, message)

    def check_errors(self):
        """ Logs any system errors reported by the instrument.
        """
        code, message = self.error
        while code != 0:
            t = time.time()
            log.info("Keithley 2700 reported error: %d, %s" % (code, message))
            print(code, message)
            code, message = self.error
            if (time.time() - t) > 10:
                log.warning("Timed out for Keithley 2700 error retrieval.")

    def reset(self):
        """ Resets the instrument and clears the queue.  """
        self.write("status:queue:clear;*RST;:stat:pres;:*CLS;")

    options = Instrument.measurement(
        "*OPT?",
        """Property that lists the installed cards in the Keithley 2700.
        Returns a dict with the integer card numbers on the position.""",
        cast=False
    )


# if __name__ == '__main__':
