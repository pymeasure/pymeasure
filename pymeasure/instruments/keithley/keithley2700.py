#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

from pymeasure.instruments import Instrument

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

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter, "Keithley 2700 MultiMeter/Switch System", **kwargs
        )

        self.check_errors()
        self.determine_valid_channels()

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
        
        ###########
        # MEASURE #
        ###########
        # Most of these are quite similar (and copied from) to keithley2000, as they both use SCPI and are very similar instruments.
        
        MODES = {
        'current': 'CURR:DC', 'current ac': 'CURR:AC',
        'voltage': 'VOLT:DC', 'voltage ac': 'VOLT:AC',
        'resistance': 'RES', 'resistance 4W': 'FRES',
        'period': 'PER', 'frequency': 'FREQ',
        'temperature': 'TEMP', 'continuity': 'CONT'
    }

    mode = Instrument.control(
        ":CONF?", ":CONF:%s",
        """ A string property that controls the configuration mode for measurements,
        which can take the values: :code:'current' (DC), :code:'current ac',
        :code:'voltage' (DC),  :code:'voltage ac', :code:'resistance' (2-wire),
        :code:'resistance 4W' (4-wire), :code:'period', :code:'frequency',
        :code:'temperature', and :code:'frequency'. """,
        validator=strict_discrete_set,
        values=MODES,
        map_values=True,
        get_process=lambda v: v.replace('"', '')
    )

    beep_state = Instrument.control(
        ":SYST:BEEP:STAT?",
        ":SYST:BEEP:STAT %g",
        """ A string property that enables or disables the system status beeper,
        which can take the values: :code:'enabled' and :code:'disabled'. """,
        validator=strict_discrete_set,
        values={'enabled': 1, 'disabled': 0},
        map_values=True
    )

    ###############
    # Current (A) #
    ###############

    current = Instrument.measurement(
        ":READ?",
        """ Reads a DC or AC current measurement in Amps, based on the
        active :attr:`~.Keithley2000.mode`. """
    )
    current_range = Instrument.control(
        ":SENS:CURR:RANG?", ":SENS:CURR:RANG:AUTO 0;:SENS:CURR:RANG %g",
        """ A floating point property that controls the DC current range in
        Amps, which can take values from 0 to 3.1 A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 3.1]
    )
    current_reference = Instrument.control(
        ":SENS:CURR:REF?", ":SENS:CURR:REF %g",
        """ A floating point property that controls the DC current reference
        value in Amps, which can take values from -3.1 to 3.1 A. """,
        validator=truncated_range,
        values=[-3.1, 3.1]
    )
    current_nplc = Instrument.control(
        ":SENS:CURR:NPLC?", ":SENS:CURR:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the DC current measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    current_digits = Instrument.control(
        ":SENS:CURR:DIG?", ":SENS:CURR:DIG %d",
        """ An integer property that controls the number of digits in the DC current
        readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int,
    )
    current_ac_range = Instrument.control(
        ":SENS:CURR:AC:RANG?", ":SENS:CURR:AC:RANG:AUTO 0;:SENS:CURR:AC:RANG %g",
        """ A floating point property that controls the AC current range in
        Amps, which can take values from 0 to 3.1 A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 3.1]
    )
    current_ac_reference = Instrument.control(
        ":SENS:CURR:AC:REF?", ":SENS:CURR:AC:REF %g",
        """ A floating point property that controls the AC current reference
        value in Amps, which can take values from -3.1 to 3.1 A. """,
        validator=truncated_range,
        values=[-3.1, 3.1]
    )
    current_ac_nplc = Instrument.control(
        ":SENS:CURR:AC:NPLC?", ":SENS:CURR:AC:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the AC current measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    current_ac_digits = Instrument.control(
        ":SENS:CURR:AC:DIG?", ":SENS:CURR:AC:DIG %d",
        """ An integer property that controls the number of digits in the AC current
        readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int
    )
    current_ac_bandwidth = Instrument.control(
        ":SENS:CURR:AC:DET:BAND?", ":SENS:CURR:AC:DET:BAND %g",
        """ A floating point property that sets the AC current detector
        bandwidth in Hz, which can take the values 3, 30, and 300 Hz. """,
        validator=truncated_discrete_set,
        values=[3, 30, 300]
    )

    ###############
    # Voltage (V) #
    ###############

    voltage = Instrument.measurement(
        ":READ?",
        """ Reads a DC or AC voltage measurement in Volts, based on the
        active :attr:`~.Keithley2000.mode`. """
    )
    voltage_range = Instrument.control(
        ":SENS:VOLT:RANG?", ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG %g",
        """ A floating point property that controls the DC voltage range in
        Volts, which can take values from 0 to 1010 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 1010]
    )
    voltage_reference = Instrument.control(
        ":SENS:VOLT:REF?", ":SENS:VOLT:REF %g",
        """ A floating point property that controls the DC voltage reference
        value in Volts, which can take values from -1010 to 1010 V. """,
        validator=truncated_range,
        values=[-1010, 1010]
    )
    voltage_nplc = Instrument.control(
        ":SENS:CURRVOLT:NPLC?", ":SENS:VOLT:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the DC voltage measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    voltage_digits = Instrument.control(
        ":SENS:VOLT:DIG?", ":SENS:VOLT:DIG %d",
        """ An integer property that controls the number of digits in the DC voltage
        readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int
    )
    voltage_ac_range = Instrument.control(
        ":SENS:VOLT:AC:RANG?", ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:AC:RANG %g",
        """ A floating point property that controls the AC voltage range in
        Volts, which can take values from 0 to 757.5 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 757.5]
    )
    voltage_ac_reference = Instrument.control(
        ":SENS:VOLT:AC:REF?", ":SENS:VOLT:AC:REF %g",
        """ A floating point property that controls the AC voltage reference
        value in Volts, which can take values from -757.5 to 757.5 Volts. """,
        validator=truncated_range,
        values=[-757.5, 757.5]
    )
    voltage_ac_nplc = Instrument.control(
        ":SENS:VOLT:AC:NPLC?", ":SENS:VOLT:AC:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the AC voltage measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    voltage_ac_digits = Instrument.control(
        ":SENS:VOLT:AC:DIG?", ":SENS:VOLT:AC:DIG %d",
        """ An integer property that controls the number of digits in the AC voltage
        readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int
    )
    voltage_ac_bandwidth = Instrument.control(
        ":SENS:VOLT:AC:DET:BAND?", ":SENS:VOLT:AC:DET:BAND %g",
        """ A floating point property that sets the AC voltage detector
        bandwidth in Hz, which can take the values  3, 30, and 300 Hz. """,
        validator=truncated_discrete_set,
        values=[3, 30, 300]
    )
    voltage_dcv_input_divider = Instrument.control(
    	":SENS:VOLT:DC:IDIV?", ":SENS:VOLT:DC:IDIV %d",
    	""" A 10MOhm voltage divider that can be connected across the voltage inputs
    	for the 100mV, 1V, and 10V ranges. Reduces the input resistance to 10MOhm. Useful
    	for stabilizing 0V reading when input is open, and for some high-voltage probes. """,
    	values={'On': 1, 'Off': 0},
        map_values=True
    )

    ####################
    # Resistance (Ohm) #
    ####################

    resistance = Instrument.measurement(
        ":READ?",
        """ Reads a resistance measurement in Ohms for both 2-wire and 4-wire
        configurations, based on the active :attr:`~.Keithley2000.mode`. """
    )
    resistance_range = Instrument.control(
        ":SENS:RES:RANG?", ":SENS:RES:RANG:AUTO 0;:SENS:RES:RANG %g",
        """ A floating point property that controls the 2-wire resistance range
        in Ohms, which can take values from 0 to 120 MOhms.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 120e6]
    )
    resistance_reference = Instrument.control(
        ":SENS:RES:REF?", ":SENS:RES:REF %g",
        """ A floating point property that controls the 2-wire resistance
        reference value in Ohms, which can take values from 0 to 120 MOhms. """,
        validator=truncated_range,
        values=[0, 120e6]
    )
    resistance_nplc = Instrument.control(
        ":SENS:RES:NPLC?", ":SENS:RES:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the 2-wire resistance measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    resistance_digits = Instrument.control(
        ":SENS:RES:DIG?", ":SENS:RES:DIG %d",
        """ An integer property that controls the number of digits in the 2-wire
        resistance readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int
    )
    resistance_4W_range = Instrument.control(
        ":SENS:FRES:RANG?", ":SENS:FRES:RANG:AUTO 0;:SENS:FRES:RANG %g",
        """ A floating point property that controls the 4-wire resistance range
        in Ohms, which can take values from 0 to 120 MOhms.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 120e6]
    )
    resistance_4W_reference = Instrument.control(
        ":SENS:FRES:REF?", ":SENS:FRES:REF %g",
        """ A floating point property that controls the 4-wire resistance
        reference value in Ohms, which can take values from 0 to 120 MOhms. """,
        validator=truncated_range,
        values=[0, 120e6]
    )
    resistance_4W_nplc = Instrument.control(
        ":SENS:FRES:NPLC?", ":SENS:FRES:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the 4-wire resistance measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    resistance_4W_digits = Instrument.control(
        ":SENS:FRES:DIG?", ":SENS:FRES:DIG %d",
        """ An integer property that controls the number of digits in the 4-wire
        resistance readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int
    )
    resistance_4w_offset_compensation = Instrument.control(
    	":SENS:FRES:OCOM?", ":SENS:FRES:OCOM %d",
    	""" Enable or disable offset compensation for 4 wire resistance measurements.
    	If on, each measurement will involve two measurement steps, one at standard current
    	level, the other with a much lower current. This reduces the effects of
    	thermoelectric voltages. See manual for further explanation""",
	values={'On': 1, 'Off': 0},
        map_values=True
    )
    
    ##################
    # Frequency (Hz) #
    ##################

    frequency = Instrument.measurement(
        ":READ?",
        """ Reads a frequency measurement in Hz, based on the
        active :attr:`~.Keithley2000.mode`. """
    )
    frequency_reference = Instrument.control(
        ":SENS:FREQ:REF?", ":SENS:FREQ:REF %g",
        """ A floating point property that controls the frequency reference
        value in Hz, which can take values from 0 to 15 MHz. """,
        validator=truncated_range,
        values=[0, 15e6]
    )
    frequency_digits = Instrument.control(
        ":SENS:FREQ:DIG?", ":SENS:FREQ:DIG %d",
        """ An integer property that controls the number of digits in the frequency
        readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int
    )
    frequency_threshold = Instrument.control(
        ":SENS:FREQ:THR:VOLT:RANG?", ":SENS:FREQ:THR:VOLT:RANG %g",
        """ A floating point property that controls the voltage signal threshold
        level in Volts for the frequency measurement, which can take values
        from 0 to 1010 V. """,
        validator=truncated_range,
        values=[0, 1010]
    )
    frequency_aperature = Instrument.control(
        ":SENS:FREQ:APER?", ":SENS:FREQ:APER %g",
        """ A floating point property that controls the frequency aperature in seconds,
        which sets the integration period and measurement speed. Takes values
        from 0.01 to 1.0 s. """,
        validator=truncated_range,
        values=[0.01, 1.0]
    )

    ##############
    # Period (s) #
    ##############

    period = Instrument.measurement(
        ":READ?",
        """ Reads a period measurement in seconds, based on the
        active :attr:`~.Keithley2000.mode`. """
    )
    period_reference = Instrument.control(
        ":SENS:PER:REF?", ":SENS:PER:REF %g",
        """ A floating point property that controls the period reference value
        in seconds, which can take values from 0 to 1 s. """,
        validator=truncated_range,
        values=[0, 1]
    )
    period_digits = Instrument.control(
        ":SENS:PER:DIG?", ":SENS:PER:DIG %d",
        """ An integer property that controls the number of digits in the period
        readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int
    )
    period_threshold = Instrument.control(
        ":SENS:PER:THR:VOLT:RANG?", ":SENS:PRE:THR:VOLT:RANG %g",
        """ A floating point property that controls the voltage signal threshold
        level in Volts for the period measurement, which can take values
        from 0 to 1010 V. """,
        validator=truncated_range,
        values=[0, 1010]
    )
    period_aperature = Instrument.control(
        ":SENS:PER:APER?", ":SENS:PER:APER %g",
        """ A floating point property that controls the period aperature in seconds,
        which sets the integration period and measurement speed. Takes values
        from 0.01 to 1.0 s. """,
        validator=truncated_range,
        values=[0.01, 1.0]
    )

    ###################
    # Temperature (C) #
    ###################

    temperature = Instrument.measurement(
        ":READ?",
        """ Reads a temperature measurement in Celsius, based on the
        active :attr:`~.Keithley2000.mode`. """
    )
    temperature_reference = Instrument.control(
        ":SENS:TEMP:REF?", ":SENS:TEMP:REF %g",
        """ A floating point property that controls the temperature reference value
        in Celsius, which can take values from -200 to 1372 C. """,
        validator=truncated_range,
        values=[-200, 1372]
    )
    temperature_nplc = Instrument.control(
        ":SENS:TEMP:NPLC?", ":SENS:TEMP:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the temperature measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    temperature_digits = Instrument.control(
        ":SENS:TEMP:DIG?", ":SENS:TEMP:DIG %d",
        """ An integer property that controls the number of digits in the temperature
        readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int
    )

    ###########
    # Trigger #
    ###########

    trigger_count = Instrument.control(
        ":TRIG:COUN?", ":TRIG:COUN %d",
        """ An integer property that controls the trigger count,
        which can take values from 1 to 9,999. """,
        validator=truncated_range,
        values=[1, 9999],
        cast=int
    )
    trigger_delay = Instrument.control(
        ":TRIG:SEQ:DEL?", ":TRIG:SEQ:DEL %g",
        """ A floating point property that controls the trigger delay
        in seconds, which can take values from 1 to 9,999,999.999 s. """,
        validator=truncated_range,
        values=[0, 999999.999]
    )

	##########
	# Buffer #
	##########
	
    buffer_points = Instrument.control(
        ":TRAC:POIN?", ":TRAC:POIN %d",
        """ An integer property that controls the number of buffer points. This
        does not represent actual points in the buffer, but the configuration
        value instead. """,
        validator=truncated_range,
        values=[2, 55000],
        cast=int
    )
    means = Instrument.measurement(
        ":CALC2:FORM MEAN;:CALC2:IMM?;",
        """ Reads the calculated means (averages) for voltage,
        current, and resistance from the buffer data  as a list. """
    )
    maximums = Instrument.measurement(
        ":CALC2:FORM MAX;:CALC2:IMM?;",
        """ Returns the calculated maximums for voltage, current, and
        resistance from the buffer data as a list. """
    )
    minimums = Instrument.measurement(
        ":CALC2:FORM MIN;:CALC2:IMM?;",
        """ Returns the calculated minimums for voltage, current, and
        resistance from the buffer data as a list. """
    )
    standard_devs = Instrument.measurement(
        ":CALC2:FORM SDEV;:CALC2:IMM?;",
        """ Returns the calculated standard deviations for voltage,
        current, and resistance from the buffer data as a list. """
    )

####
	
    def measure_voltage(self, max_voltage=1, ac=False):
        """ Configures the instrument to measure voltage,
        based on a maximum voltage to set the range, and
        a boolean flag to determine if DC or AC is required.

        :param max_voltage: A voltage in Volts to set the voltage range
        :param ac: False for DC voltage, and True for AC voltage
        """
        if ac:
            self.mode = 'voltage ac'
            self.voltage_ac_range = max_voltage
        else:
            self.mode = 'voltage'
            self.voltage_range = max_voltage

    def measure_current(self, max_current=10e-3, ac=False):
        """ Configures the instrument to measure current,
        based on a maximum current to set the range, and
        a boolean flag to determine if DC or AC is required.

        :param max_current: A current in Volts to set the current range
        :param ac: False for DC current, and True for AC current
        """
        if ac:
            self.mode = 'current ac'
            self.current_ac_range = max_current
        else:
            self.mode = 'current'
            self.current_range = max_current

    def measure_resistance(self, max_resistance=10e6, wires=2):
        """ Configures the instrument to measure voltage,
        based on a maximum voltage to set the range, and
        a boolean flag to determine if DC or AC is required.

        :param max_voltage: A voltage in Volts to set the voltage range
        :param ac: False for DC voltage, and True for AC voltage
        """
        if wires == 2:
            self.mode = 'resistance'
            self.resistance_range = max_resistance
        elif wires == 4:
            self.mode = 'resistance 4W'
            self.resistance_4W_range = max_resistance
        else:
            raise ValueError("Keithley 2000 only supports 2 or 4 wire"
                             "resistance meaurements.")

    def measure_period(self):
        """ Configures the instrument to measure the period. """
        self.mode = 'period'

    def measure_frequency(self):
        """ Configures the instrument to measure the frequency. """
        self.mode = 'frequency'

    def measure_temperature(self):
        """ Configures the instrument to measure the temperature. """
        self.mode = 'temperature'

    def measure_continuity(self):
        """ Configures the instrument to perform continuity testing. """
        self.mode = 'continuity'

    def _mode_command(self, mode=None):
        if mode is None:
            mode = self.mode
        return self.MODES[mode]

    def auto_range(self, mode=None):
        """ Sets the active mode to use auto-range,
        or can set another mode by its name.

        :param mode: A valid :attr:`~.Keithley2000.mode` name, or None for the active mode
        """
        self.write(":SENS:%s:RANG:AUTO 1" % self._mode_command(mode))

    def enable_reference(self, mode=None):
        """ Enables the reference for the active mode,
        or can set another mode by its name.

        :param mode: A valid :attr:`~.Keithley2000.mode` name, or None for the active mode
        """
        self.write(":SENS:%s:REF:STAT 1" % self._mode_command(mode))

    def disable_reference(self, mode=None):
        """ Disables the reference for the active mode,
        or can set another mode by its name.

        :param mode: A valid :attr:`~.Keithley2000.mode` name, or None for the active mode
        """
        self.write(":SENS:%s:REF:STAT 0" % self._mode_command(mode))

    def acquire_reference(self, mode=None):
        """ Sets the active value as the reference for the active mode,
        or can set another mode by its name.

        :param mode: A valid :attr:`~.Keithley2000.mode` name, or None for the active mode
        """
        self.write(":SENS:%s:REF:ACQ" % self._mode_command(mode))

    def enable_filter(self, mode=None, type='repeat', count=1):
        """ Enables the averaging filter for the active mode,
        or can set another mode by its name.

        :param mode: A valid :attr:`~.Keithley2000.mode` name, or None for the active mode
        :param type: The type of averaging filter, either 'repeat' or 'moving'.
        :param count: A number of averages, which can take take values from 1 to 100.
        :param window: The filter window in percent of range, from 0 to 10.
        """
        self.write(":SENS:%s:AVER:STAT 1")
        self.write(":SENS:%s:AVER:TCON %s")
        self.write(":SENS:%s:AVER:COUN %d")
        self.write(":SENS:%s:AVER:WIND %d")

    def disable_filter(self, mode=None):
        """ Disables the averaging filter for the active mode,
        or can set another mode by its name.

        :param mode: A valid :attr:`~.Keithley2000.mode` name, or None for the active mode
        """
        self.write(":SENS:%s:AVER:STAT 0" % self._mode_command(mode))

