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

import logging
from warnings import warn

from pymeasure.instruments import Instrument, SCPIMixin

from .buffer import KeithleyBuffer

import numpy as np
import time

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


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
        clist = [f"{value:d}"]
    elif isinstance(value, (list, tuple, np.ndarray, range)):
        clist = [f"{x:d}" for x in value]
    else:
        raise ValueError(f"Type of value ({type(value)}) not valid")

    # Pad numbers to length (if required)
    clist = [c.rjust(2, "0") for c in clist]
    clist = [c.rjust(3, "1") for c in clist]

    # Check channels against valid channels
    for c in clist:
        if int(c) not in values:
            raise ValueError(
                f"Channel number {value:g} not valid."
            )

    # Convert list of strings to clist format
    clist = "(@{:s})".format(", ".join(clist))

    return clist


def text_length_validator(value, values):
    """ Provides a validator function that a valid string for the display
    commands of the Keithley. Raises a TypeError if value is not a string.
    If the string is too long, it is truncated to the correct length.

    :param value: A value to test
    :param values: The allowed length of the text
    """

    if not isinstance(value, str):
        raise TypeError("Value is not a string.")

    return value[:values]


class Keithley2700(KeithleyBuffer, SCPIMixin, Instrument):
    """ Represents the Keithley 2700 Multimeter/Switch System and provides a
    high-level interface for interacting with the instrument.

    .. code-block:: python

        keithley = Keithley2700("GPIB::1")

    """

    CLIST_VALUES = list(range(101, 300))

    def __init__(self, adapter, name="Keithley 2700 MultiMeter/Switch System", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

        self.check_errors()
        self.determine_valid_channels()

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
        """ A parameter that opens the specified list of channels. Can only
        be set.
        """,
        validator=clist_validator,
        values=CLIST_VALUES,
        check_set_errors=True
    )

    def get_state_of_channels(self, channels):
        """ Get the open or closed state of the specified channels

        :param channels: a list of channel numbers, or single channel number
        """
        clist = clist_validator(channels, self.CLIST_VALUES)
        state = self.ask("ROUTe:MULTiple:STATe? %s" % clist)

        return state

    def open_all_channels(self):
        """ Open all channels of the Keithley 2700.
        """
        self.write(":ROUTe:OPEN:ALL")

    def determine_valid_channels(self):
        """ Determine what cards are installed into the Keithley 2700
        and from that determine what channels are valid.
        """
        self.CLIST_VALUES.clear()

        self.cards = {slot: card for slot, card in enumerate(self.options, 1)}

        for slot, card in self.cards.items():

            if card == "none":
                continue
            elif card == "7709":
                """The 7709 is a 6(rows) x 8(columns) matrix card, with two
                additional switches (49 & 50) that allow row 1 and 2 to be
                connected to the DMM backplane (input and sense respectively).
                """
                channels = range(1, 51)
            else:
                log.warning(
                    f"Card type {card} at slot {slot} is not yet implemented."
                )
                continue

            channels = [100 * slot + ch for ch in channels]

            self.CLIST_VALUES.extend(channels)

    def close_rows_to_columns(self, rows, columns, slot=None):
        """ Closes (connects) the channels between column(s) and row(s)
        of the 7709 connection matrix.
        Only one of the parameters 'rows' or 'columns' can be "all"

        :param rows: row number or list of numbers; can also be "all"
        :param columns: column number or list of numbers; can also be "all"
        :param slot: slot number (1 or 2) of the 7709 card to be used
        """

        channels = self.channels_from_rows_columns(rows, columns, slot)
        self.closed_channels = channels

    def open_rows_to_columns(self, rows, columns, slot=None):
        """ Opens (disconnects) the channels between column(s) and row(s)
        of the 7709 connection matrix.
        Only one of the parameters 'rows' or 'columns' can be "all"

        :param rows: row number or list of numbers; can also be "all"
        :param columns: column number or list of numbers; can also be "all"
        :param slot: slot number (1 or 2) of the 7709 card to be used
        """

        channels = self.channels_from_rows_columns(rows, columns, slot)
        self.open_channels = channels

    def channels_from_rows_columns(self, rows, columns, slot=None):
        """ Determine the channel numbers between column(s) and row(s) of the
        7709 connection matrix. Returns a list of channel numbers.
        Only one of the parameters 'rows' or 'columns' can be "all"

        :param rows: row number or list of numbers; can also be "all"
        :param columns: column number or list of numbers; can also be "all"
        :param slot: slot number (1 or 2) of the 7709 card to be used

        """

        if slot is not None and self.cards[slot] != "7709":
            raise ValueError("No 7709 card installed in slot %g" % slot)

        if isinstance(rows, str) and isinstance(columns, str):
            raise ValueError("Only one parameter can be 'all'")
        elif isinstance(rows, str) and rows == "all":
            rows = list(range(1, 7))
        elif isinstance(columns, str) and columns == "all":
            columns = list(range(1, 9))

        if isinstance(rows, (list, tuple, np.ndarray)) and \
                isinstance(columns, (list, tuple, np.ndarray)):

            if len(rows) != len(columns):
                raise ValueError("The length of the rows and columns do not match")

            # Flatten (were necessary) the arrays
            new_rows = []
            new_columns = []
            for row, column in zip(rows, columns):
                if isinstance(row, int) and isinstance(column, int):
                    new_rows.append(row)
                    new_columns.append(column)
                elif isinstance(row, (list, tuple, np.ndarray)) and isinstance(column, int):
                    new_columns.extend(len(row) * [column])
                    new_rows.extend(list(row))
                elif isinstance(column, (list, tuple, np.ndarray)) and isinstance(row, int):
                    new_columns.extend(list(column))
                    new_rows.extend(len(column) * [row])

            rows = new_rows
            columns = new_columns

        # Determine channel number from rows and columns number.
        rows = np.array(rows, ndmin=1)
        columns = np.array(columns, ndmin=1)

        channels = (rows - 1) * 8 + columns

        if slot is not None:
            channels += 100 * slot

        return channels

    # system, some taken from Keithley 2400
    def beep(self, frequency, duration):
        """ Sounds a system beep.

        :param frequency: A frequency in Hz between 65 Hz and 2 MHz
        :param duration: A time in seconds between 0 and 7.9 seconds
        """
        self.write(f":SYST:BEEP {frequency:g}, {duration:g}")

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
        warn("Deprecated to use `error`, use `next_error` instead.", FutureWarning)
        return self.next_error

    def reset(self):
        """ Resets the instrument and clears the queue.  """
        self.write("status:queue:clear;*RST;:stat:pres;:*CLS;")

    options = Instrument.measurement(
        "*OPT?",
        """Property that lists the installed cards in the Keithley 2700.
        Returns a dict with the integer card numbers on the position.""",
        cast=False
    )

    ###########
    # DISPLAY #
    ###########

    text_enabled = Instrument.control(
        "DISP:TEXT:STAT?", "DISP:TEXT:STAT %d",
        """ A boolean property that controls whether a text message can be
        shown on the display of the Keithley 2700.
        """,
        values={True: 1, False: 0},
        map_values=True,
    )
    display_text = Instrument.control(
        "DISP:TEXT:DATA?", "DISP:TEXT:DATA '%s'",
        """ A string property that controls the text shown on the display of
        the Keithley 2700. Text can be up to 12 ASCII characters and must be
        enabled to show.
        """,
        validator=text_length_validator,
        values=12,
        cast=str,
        separator="NO_SEPARATOR",
        get_process=lambda v: v.strip("'\""),
    )

    def display_closed_channels(self):
        """ Show the presently closed channels on the display of the Keithley
        2700.
        """

        # Get the closed channels and make a string of the list
        channels = self.closed_channels
        channel_string = " ".join([
            str(channel % 100) for channel in channels
        ])

        # Prepend "Closed: " or "C: " to the string, depending on the length
        str_length = 12
        if len(channel_string) < str_length - 8:
            channel_string = "Closed: " + channel_string
        elif len(channel_string) < str_length - 3:
            channel_string = "C: " + channel_string

        # enable displaying text-messages
        self.text_enabled = True

        # write the string to the display
        self.display_text = channel_string
