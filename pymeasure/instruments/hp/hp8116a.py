#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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
import time
import numpy as np
from enum import IntFlag
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    strict_discrete_set, strict_range, truncated_discrete_set
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Status(IntFlag):
    """ IntFlag type for the GPIB status byte which is returned by the :py:attr:`status` property.
    When the timing_error or programming_error flag is set, a more detailed error description
    can be obtained by calling :py:method:`check_errors()`.
    """
    timing_error = 1 << 0
    programming_error = 1 << 1
    syntax_error = 1 << 2
    system_failure = 1 << 3
    autovernier_in_progress = 1 << 4
    sweep_in_progress = 1 << 5
    service_request = 1 << 6
    buffer_not_empty = 1 << 7


class HP8116A(Instrument):
    """ Represents the Hewlett-Packard 8116A 50 MHz Pulse/Function Generator
    and provides a high-level interface for interacting with the instrument.
    The resolution for all floating point instrument parameters is 3 digits.
    """

    def __init__(self, resourceName, **kwargs):
        kwargs.setdefault('read_termination', '\r\n')
        kwargs.setdefault('write_termination', '\r\n')
        kwargs.setdefault('send_end', True)
        super(HP8116A, self).__init__(
            resourceName,
            'Hewlett-Packard 8116A Pulse/Function Generator',
            includeSCPI=False,
            **kwargs
        )

    OPERATING_MODES = {
        'normal': 'M1',
        'triggered': 'M2',
        'gate': 'M3',
        'external_width': 'M4',

        # Option 001 only
        'internal_sweep': 'M5',
        'external_sweep': 'M6',
        'internal_burst': 'M7',
        'external_burst': 'M8',
    }

    OPERATING_MODES_INV = {v: k for k, v in OPERATING_MODES.items()}

    CONTROL_MODES = {
        'off': 'CT0',
        'FM': 'CT1',
        'AM': 'CT2',
        'PWM': 'CT3',
        'VCO': 'CT4',
    }

    CONTROL_MODES_INV = {v: k for k, v in CONTROL_MODES.items()}

    TRIGGER_SLOPES = {
        'off': 'T0',
        'positive': 'T1',
        'negative': 'T2',
    }

    TRIGGER_SLOPES_INV = {v: k for k, v in TRIGGER_SLOPES.items()}

    SHAPES = {
        'dc': 'W0',
        'sine': 'W1',
        'triangle': 'W2',
        'square': 'W3',
        'pulse': 'W4',
    }

    SHAPES_INV = {v: k for k, v in SHAPES.items()}

    _units_freqency = {
        'milli': 'MZ',
        'no_prefix': 'HZ',
        'kilo': 'KHZ',
        'mega': 'MHZ',
    }

    _units_voltage = {
        'milli': 'MV',
        'no_prefix': 'V',
    }

    _units_time = {
        'nano': 'NS',
        'micro': 'US',
        'milli': 'MS',
        'no_prefix': 'S',
    }

    _si_prefixes = {
        'nano': 1e-9,
        'micro': 1e-6,
        'milli': 1e-3,
        'no_prefix': 1,
        'kilo': 1e3,
        'mega': 1e6,
    }

    @property
    def status(self):
        """ Returns the status byte of the 8116A as an IntFlag-type enum. """
        return Status(self.adapter.connection.read_stb())

    # Instrument communication #

    def write(self, command):
        """ Write a command to the instrument and wait until the 8116A has interpreted it. """
        self.adapter.write(command)

        # We need to read the status byte and wait until this bit is cleared
        # because some older units lock up if we don't.
        while self.status & Status.buffer_not_empty:
            time.sleep(0.001)

    def read(self):
        """ Some units of the 8116A don't use the EOI line (see service note 8116A-07A).
        Therefore reads with automatic end-of-transmission detection will timeout.
        Instead, :code:`adapter.read_bytes()` has to be used.
        """
        raise NotImplementedError('Not supported, use adapter.read_bytes() instead')

    def ask(self, command, num_bytes):
        """ Write a command to the instrument, read the response, and return the response.

        :param command: The command to send to the instrument.
        :param num_bytes: The number of bytes to read from the instrument.
        """
        self.write(command)
        return self.adapter.read_bytes(num_bytes).decode('ascii')

    def values(self, command, num_bytes, separator=',', cast=float,
               preprocess_reply=None, **kwargs):
        results = str(self.ask(command, num_bytes)).strip(' ,\r\n')
        if callable(preprocess_reply):
            results = preprocess_reply(results)
        elif callable(self.adapter.preprocess_reply):
            results = self.adapter.preprocess_reply(results)
        results = results.split(separator)
        for i, result in enumerate(results):
            try:
                if cast == bool:
                    # Need to cast to float first since results are usually
                    # strings and bool of a non-empty string is always True
                    results[i] = bool(float(result))
                else:
                    results[i] = cast(result)
            except Exception:
                pass  # Keep as string
        return results

    # Numeric parameter parsing #

    @staticmethod
    def get_value_with_unit(value, units):
        """ Convert a floating point value to a string with the appropriate unit.

        :param value: The value to convert.
        :param units: Dictionary containing a mapping of SI-prefixes to the unit strings
            the instrument uses, eg. 'milli' -> 'MZ' for millihertz.
        """
        if value < 1e-6:
            value_str = f'{value*1e9:.3g} {units["nano"]}'
        elif value < 1e-3:
            value_str = f'{value*1e6:.3g} {units["micro"]}'
        elif value < 1:
            value_str = f'{value*1e3:.3g} {units["milli"]}'
        elif value < 1e3:
            value_str = f'{value:.3g} {units["no_prefix"]}'
        elif value < 1e6:
            value_str = f'{value*1e-3:.3g} {units["kilo"]}'
        else:
            value_str = f'{value*1e-6:.3g} {units["mega"]}'

        return value_str

    @staticmethod
    def parse_value_with_unit(value_str, units):
        """ Convert a string with a value and a unit as returned by the HP8116A to a float.

        :param value_str: The string to parse.
        :param units: Dictionary containing a mapping of SI-prefixes to the unit strings
            the instrument uses, eg. 'milli' -> 'MZ' for millihertz.
        """
        value_str = value_str.strip()
        value = float(value_str[3:7].strip())
        unit = value_str[8:].strip()
        units_inverse = {v: k for k, v in units.items()}
        value *= HP8116A._si_prefixes[units_inverse[unit]]

        return value

    # Instrument controls #

    @staticmethod
    def boolean_control(identifier, state_index, docs, inverted=False):
        return Instrument.control(
            'CST', identifier + '%d', docs,
            validator=strict_discrete_set,
            values=[True, False],
            get_process=lambda x: inverted ^ bool(int(x[state_index][1])),
            set_process=lambda x: int(inverted ^ x),
            num_bytes=91,
        )

    @staticmethod
    def generate_1_2_5_sequence(min, max):
        exp_min = int(np.log10(min))
        exp_max = int(np.log10(max))

        seq_1_2_5 = np.array([1, 2, 5])
        sequence = np.array([seq_1_2_5 * (10 ** exp) for exp in range(exp_min, exp_max + 1)])
        sequence = sequence.flatten()
        sequence = sequence[(sequence >= min) & (sequence <= max)]

        return list(sequence)

    operating_mode = Instrument.control(
        'CST', '%s',
        """ A string property that controls the operating mode of the instrument.
        Possible values (without Option 001) are: 'normal', 'triggered', 'gate', 'external_width'.
        With Option 001, 'internal_sweep', 'external_sweep', 'external_width', 'external_pulse'
        are also available.
        """,
        validator=strict_discrete_set,
        values=OPERATING_MODES,
        map_values=True,
        get_process=lambda x: HP8116A.OPERATING_MODES_INV[x[0]],
        num_bytes=91,
    )

    control_mode = Instrument.control(
        'CST', '%s',
        """ A string property that controls the control mode of the instrument.
        Possible values are 'off', 'FM', 'AM', 'PWM', 'VCO'.
        """,
        validator=strict_discrete_set,
        values=CONTROL_MODES,
        map_values=True,
        get_process=lambda x: HP8116A.CONTROL_MODES_INV[x[1]],
        num_bytes=91,
    )

    trigger_slope = Instrument.control(
        'CST', '%s',
        """ A string property that controls the slope the trigger triggers on.
        Possible values are: 'off', 'positive', 'negative'.
        """,
        validator=strict_discrete_set,
        values=TRIGGER_SLOPES,
        map_values=True,
        get_process=lambda x: HP8116A.TRIGGER_SLOPES_INV[x[2]],
        num_bytes=91,
    )

    shape = Instrument.control(
        'CST', '%s',
        """ A string property that controls the shape of the output waveform.
        Possible values are: 'dc', 'sine', 'triangle', 'square', 'pulse'.
        """,
        validator=strict_discrete_set,
        values=SHAPES,
        map_values=True,
        get_process=lambda x: HP8116A.SHAPES_INV[x[3]],
        num_bytes=91,
    )

    haversine_enabled = boolean_control(
        'H', 4,
        """ A boolean property that controls whether a haversine/havertriangle signal
        is generated when in 'triggered', 'internal_burst' or 'external_burst' operating mode.
        """,
    )

    autovernier_enabled = boolean_control(
        'A', 5,
        """ A boolean property that controls whether the autovernier is enabled. """,
    )

    limit_enabled = boolean_control(
        'L', 6,
        """ A boolean property that controls whether parameter limiting is enabled. """,
    )

    complement_enabled = boolean_control(
        'C', 7,
        """ A boolean property that controls whether the complement
        of the signal is generated.
        """,
    )

    output_enabled = boolean_control(
        'D', 8,
        """ A boolean property that controls whether the output is enabled. """,
        inverted=True,  # The actual command is "Disable output"...
    )

    frequency = Instrument.control(
        'IFRQ', 'FRQ %s',
        """ A floating point value that controls the frequency of the
        output in Hz. The allowed frequency range is 1 mHz to 52.5 MHz.
        """,
        validator=strict_range,
        values=[1e-3, 52.5001e6],
        set_process=lambda x: HP8116A.get_value_with_unit(x, HP8116A._units_freqency),
        get_process=lambda x: HP8116A.parse_value_with_unit(x, HP8116A._units_freqency),
        num_bytes=14,
    )

    duty_cycle = Instrument.control(
        'IDTY', 'DTY %s %%',
        """ An integer value that controls the duty cycle of the output in percent.
        The allowed range is 10% to 90%. It is valid for all shapes except 'pulse',
        where :py:attr:`pulse_width` is used.
        """,
        validator=strict_range,
        values=[10, 90.0001],
        get_process=lambda x: int(x[6:8]),
        num_bytes=14,
    )

    pulse_width = Instrument.control(
        'IWID', 'WID %s',
        """ A floating point value that controls the pulse width.
        The allowed pulse width range is 8 ns to 999 ms.
        The pulse width may not be larger than the period.
        """,
        validator=strict_range,
        values=[8e-9, 999.001e-3],
        set_process=lambda x: HP8116A.get_value_with_unit(x, HP8116A._units_time),
        get_process=lambda x: HP8116A.parse_value_with_unit(x, HP8116A._units_time),
        num_bytes=14,
    )

    amplitude = Instrument.control(
        'IAMP', 'AMP %s',
        """ A floating point value that controls the amplitude of the
        output in V. The allowed amplitude range generally is 10 mV to 16 V,
        but it is also limited by the current offset.
        """,
        validator=strict_range,
        values=[10e-3, 16.001],
        set_process=lambda x: HP8116A.get_value_with_unit(x, HP8116A._units_voltage),
        get_process=lambda x: HP8116A.parse_value_with_unit(x, HP8116A._units_voltage),
        num_bytes=14,
    )

    offset = Instrument.control(
        'IOFS', 'OFS %s',
        """ A floating point value that controls the offset of the
        output in V. The allowed offset range generally is -7.95 V to 7.95 V,
        but it is also limited by the amplitude.
        """,
        validator=strict_range,
        values=[-7.95, 7.95001],
        set_process=lambda x: HP8116A.get_value_with_unit(x, HP8116A._units_voltage),
        get_process=lambda x: HP8116A.parse_value_with_unit(x, HP8116A._units_voltage),
        num_bytes=14,
    )

    high_level = Instrument.control(
        'IHIL', 'HIL %s',
        """ A floating point value that controls the high level of the
        output in V. The allowed high level range generally is -7.9 V to 8 V,
        but it must be at least 10 mV greater than the low level.
        """,
        validator=strict_range,
        values=[-7.9, 8.001],
        set_process=lambda x: HP8116A.get_value_with_unit(x, HP8116A._units_voltage),
        get_process=lambda x: HP8116A.parse_value_with_unit(x, HP8116A._units_voltage),
        num_bytes=14,
    )

    low_level = Instrument.control(
        'ILOL', 'LOL %s',
        """ A floating point value that controls the low level of the
        output in V. The allowed low level range generally is -8 V to 7.9 V,
        but it must be at least 10 mV less than the high level.
        """,
        validator=strict_range,
        values=[-8, 7.9001],
        set_process=lambda x: HP8116A.get_value_with_unit(x, HP8116A._units_voltage),
        get_process=lambda x: HP8116A.parse_value_with_unit(x, HP8116A._units_voltage),
        num_bytes=14,
    )

    burst_number = Instrument.control(
        'IBUR', 'BUR %s #',
        """ An integer value that controls the number of periods generated in a burst.
        The allowed range is 1 to 1999. It is only valid for units with Option 001
        in one of the burst modes.
        """,
        validator=strict_range,
        values=[1, 1999],
        get_process=lambda x: int(x[4:8]),
        num_bytes=14,
    )

    repetition_rate = Instrument.control(
        'IRPT', 'RPT %s',
        """ A floating point value that controls the repetition rate (= the time between bursts)
        in internal_burst mode. The allowed range is 20 ns to 999 ms.
        """,
        validator=strict_range,
        values=[20e-9, 999.001e-3],
        set_process=lambda x: HP8116A.get_value_with_unit(x, HP8116A._units_time),
        get_process=lambda x: HP8116A.parse_value_with_unit(x, HP8116A._units_time),
        num_bytes=14,
    )

    sweep_start = Instrument.control(
        'ISTA', 'STA %s',
        """ A floating point value that controls the start frequency in both sweep modes.
        The allowed range is 1 mHz to 52.5 MHz.
        """,
        validator=strict_range,
        values=[1e-3, 52.5001e6],
        set_process=lambda x: HP8116A.get_value_with_unit(x, HP8116A._units_freqency),
        get_process=lambda x: HP8116A.parse_value_with_unit(x, HP8116A._units_freqency),
        num_bytes=14,
    )

    sweep_stop = Instrument.control(
        'ISTP', 'STP %s',
        """ A floating point value that controls the stop frequency in both sweep modes.
        The allowed range is 1 mHz to 52.5 MHz.
        """,
        validator=strict_range,
        values=[1e-3, 52.5001e6],
        set_process=lambda x: HP8116A.get_value_with_unit(x, HP8116A._units_freqency),
        get_process=lambda x: HP8116A.parse_value_with_unit(x, HP8116A._units_freqency),
        num_bytes=14,
    )

    sweep_marker_frequency = Instrument.control(
        'IMRK', 'MRK %s',
        """ A floating point value that controls the frequency marker in both sweep modes.
        At this frequency, the marker output switches from low to high.
        The allowed range is 1 mHz to 52.5 MHz.
        """,
        validator=strict_range,
        values=[1e-3, 52.5001e6],
        set_process=lambda x: HP8116A.get_value_with_unit(x, HP8116A._units_freqency),
        get_process=lambda x: HP8116A.parse_value_with_unit(x, HP8116A._units_freqency),
        num_bytes=14,
    )

    sweep_time = Instrument.control(
        'ISWT', 'SWT %s',
        """ A floating point value that controls the sweep time per decade in both sweep modes.
        The sweep time is selectable in a 1-2-5 sequence between 10 ms and 500 s.
        """,
        validator=truncated_discrete_set,
        values=generate_1_2_5_sequence(10e-3, 500),
        set_process=lambda x: HP8116A.get_value_with_unit(x, HP8116A._units_time),
        get_process=lambda x: HP8116A.parse_value_with_unit(x, HP8116A._units_time),
        num_bytes=14,
    )

    # Functions using low-level access via instrument.adapter.connection methods #

    def GPIB_trigger(self):
        """ Initate trigger via low-level GPIB-command (aka GET - group execute trigger). """
        self.adapter.connection.assert_trigger()

    def reset(self):
        """ Initatiate a reset (like a power-on reset) of the 8116A. """
        self.adapter.connection.clear()

    def shutdown(self):
        """ Gracefully close the connection to the 8116A. """
        self.adapter.connection.clear()
        self.adapter.connection.close()
        super().shutdown()
