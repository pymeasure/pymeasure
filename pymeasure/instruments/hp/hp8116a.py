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
import time
import numpy as np
from enum import Enum, IntFlag
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    strict_discrete_set, strict_range, truncated_discrete_set
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# for Python>3.9, these two methods can be static methods in the class
def _generate_1_2_5_sequence(min, max):
    """ Generate a list of a 1-2-5 sequence between min and max. """
    exp_min = int(np.log10(min))
    exp_max = int(np.log10(max))

    seq_1_2_5 = np.array([1, 2, 5])
    sequence = np.array([seq_1_2_5 * (10 ** exp) for exp in range(exp_min - 1, exp_max + 1)])
    sequence = sequence.flatten()
    sequence = sequence[(sequence >= min) & (sequence <= max)]

    return list(sequence)


def _boolean_control(identifier, state_index, docs, inverted=False, **kwargs):
    return Instrument.control(
        'CST', identifier + '%d', docs,
        validator=strict_discrete_set,
        values=[True, False],
        get_process=lambda x: inverted ^ bool(int(x[state_index][1])),
        set_process=lambda x: int(inverted ^ x),
        **kwargs
    )


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

    def __init__(self, adapter, name="Hewlett-Packard 8116A", **kwargs):
        kwargs.setdefault('read_termination', '\r\n')
        kwargs.setdefault('write_termination', '\r\n')
        kwargs.setdefault('send_end', True)
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            **kwargs
        )
        self.has_option_001 = self._check_has_option_001()

    class Digit(Enum):
        """ Enum of the digits used with the autovernier
        (see :py:meth:`HP8116A.start_autovernier()`).
        """
        MOST_SIGNIFICANT = 'M'
        SECOND_SIGNIFICANT = 'S'
        LEAST_SIGNIFICANT = 'L'

    class Direction(Enum):
        """ Enum of the directions used with the autovernier
        (see :py:meth:`HP8116A.start_autovernier()`).
        """
        UP = 'U'
        DOWN = 'D'

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

    _units_frequency = {
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

    @staticmethod
    def _get_value_with_unit(value, units):
        """ Convert a floating point value to a string with 3 digits resolution
        and the appropriate unit.

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
    def _parse_value_with_unit(value_str, units):
        """ Convert a string with a value and a unit as returned by the HP8116A to a float.

        :param value_str: The string to parse.
        :param units: Dictionary containing a mapping of SI-prefixes to the unit strings
            the instrument uses, eg. 'milli' -> 'MZ' for millihertz.
        """

        # Example value_str: 'FRQ 1.00KHZ'
        # Digits and unit are always positioned the same for all parameters
        value_str = value_str.strip()
        value = float(value_str[3:8].strip())
        unit = value_str[8:].strip()
        units_inverse = {v: k for k, v in units.items()}
        value *= HP8116A._si_prefixes[units_inverse[unit]]

        return value

    # Instrument communication #

    def write(self, command):
        """ Write a command to the instrument and wait until the 8116A has interpreted it. """
        super().write(command)

        # We need to read the status byte and wait until the buffer_not_empty bit
        # is cleared because some older units lock up if we don't.
        self._wait_for_commands_processed()

    def ask(self, command, num_bytes=None):
        """ Write a command to the instrument, read the response, and return the response as ASCII text.

        :param command: The command to send to the instrument.
        :param num_bytes: The number of bytes to read from the instrument. If not specified,
                          the number of bytes is automatically determined by the command.
        """  # noqa: E501
        self.write(command)

        if num_bytes is None:
            if command == 'CST':
                # We usually only need the first 29 bytes of the state response since they contain
                # the current boolean parameters. The other parameters all have corresponding
                # 'interrogate' commands.
                num_bytes = 29
            elif command[0] == 'I':
                num_bytes = 14

        # The first character is always a space or a leftover character from the previous command,
        # when the number of bytes read was too large or too small.
        bytes = self.read_bytes(num_bytes)[1:]
        return bytes.decode('ascii').strip(' ,\r\n')

    operating_mode = Instrument.control(
        'CST', '%s',
        """Control the operating mode of the instrument.
        Possible values (without Option 001) are: 'normal', 'triggered', 'gate', 'external_width'.
        With Option 001, 'internal_sweep', 'external_sweep', 'external_width', 'external_pulse'
        are also available.
        """,
        validator=strict_discrete_set,
        values=OPERATING_MODES,
        map_values=True,
        get_process=lambda x: HP8116A.OPERATING_MODES_INV[x[0]]
    )

    control_mode = Instrument.control(
        'CST', '%s',
        """Control the control mode of the instrument.
        Possible values are 'off', 'FM', 'AM', 'PWM', 'VCO'.
        """,
        validator=strict_discrete_set,
        values=CONTROL_MODES,
        map_values=True,
        get_process=lambda x: HP8116A.CONTROL_MODES_INV[x[1]]
    )

    trigger_slope = Instrument.control(
        'CST', '%s',
        """Control the slope the trigger triggers on.
        Possible values are: 'off', 'positive', 'negative'.
        """,
        validator=strict_discrete_set,
        values=TRIGGER_SLOPES,
        map_values=True,
        get_process=lambda x: HP8116A.TRIGGER_SLOPES_INV[x[2]]
    )

    shape = Instrument.control(
        'CST', '%s',
        """Control the shape of the output waveform.
        Possible values are: 'dc', 'sine', 'triangle', 'square', 'pulse'.
        """,
        validator=strict_discrete_set,
        values=SHAPES,
        map_values=True,
        get_process=lambda x: HP8116A.SHAPES_INV[x[3]]
    )

    haversine_enabled = _boolean_control(
        'H', 4,
        """Control whether a haversine/havertriangle signal
        is generated when in 'triggered', 'internal_burst' or 'external_burst' operating mode.
        """,
    )

    autovernier_enabled = _boolean_control(
        'A', 5,
        """Control whether the autovernier is enabled (bool).""",
        check_set_errors=True
    )

    limit_enabled = _boolean_control(
        'L', 6,
        """Control whether parameter limiting is enabled (bool).""",
    )

    complement_enabled = _boolean_control(
        'C', 7,
        """Control whether the complement of the signal is generated (bool).""",
    )

    output_enabled = _boolean_control(
        'D', 8,
        """Control whether the output is enabled (bool).""",
        inverted=True,  # The actual command is "Disable output"...
    )

    frequency = Instrument.control(
        'IFRQ', 'FRQ %s',
        """Control the frequency of the output in Hz (strict float from 1e-3 to 52.5e6).
        """,
        validator=strict_range,
        values=[1e-3, 52.5001e6],
        set_process=lambda x: HP8116A._get_value_with_unit(x, HP8116A._units_frequency),
        get_process=lambda x: HP8116A._parse_value_with_unit(x, HP8116A._units_frequency)
    )

    duty_cycle = Instrument.control(
        'IDTY', 'DTY %s %%',
        """Control the duty cycle of the output in percent (float).
        The allowed range generally is 10 % to 90 %, but it also depends on the current frequency.
        It is valid for all shapes except 'pulse', where :py:attr:`pulse_width` is used instead.
        """,
        validator=strict_range,
        values=[10, 90.0001],
        cast=int,
        # get_process=lambda x: int(x[6:8])
    )

    pulse_width = Instrument.control(
        'IWID', 'WID %s',
        """Control the pulse width in s (strict float from 8e-9 to 999e-3).
        The pulse width may not be larger than the period.
        """,
        validator=strict_range,
        values=[8e-9, 999.001e-3],
        set_process=lambda x: HP8116A._get_value_with_unit(x, HP8116A._units_time),
        get_process=lambda x: HP8116A._parse_value_with_unit(x, HP8116A._units_time)
    )

    amplitude = Instrument.control(
        'IAMP', 'AMP %s',
        """Control the amplitude of the output in V (strict float from 10e-3 to 16).
        The allowed amplitude range is also limited by the current offset.
        """,
        validator=strict_range,
        values=[10e-3, 16.001],
        set_process=lambda x: HP8116A._get_value_with_unit(x, HP8116A._units_voltage),
        get_process=lambda x: HP8116A._parse_value_with_unit(x, HP8116A._units_voltage)
    )

    offset = Instrument.control(
        'IOFS', 'OFS %s',
        """Control the offset of the output in V (strit float from -7.95 to 7.95).
        The allowed offset range is also limited by the amplitude.
        """,
        validator=strict_range,
        values=[-7.95, 7.95001],
        set_process=lambda x: HP8116A._get_value_with_unit(x, HP8116A._units_voltage),
        get_process=lambda x: HP8116A._parse_value_with_unit(x, HP8116A._units_voltage)
    )

    high_level = Instrument.control(
        'IHIL', 'HIL %s',
        """Control the high level of the output in V (strict float from -7.9 to 8).
        The allowed high level range must be at least 10 mV greater than the low level.
        """,
        validator=strict_range,
        values=[-7.9, 8.001],
        set_process=lambda x: HP8116A._get_value_with_unit(x, HP8116A._units_voltage),
        get_process=lambda x: HP8116A._parse_value_with_unit(x, HP8116A._units_voltage)
    )

    low_level = Instrument.control(
        'ILOL', 'LOL %s',
        """Control the low level of the output in V (strict float from -8 to 7.9).
        The allowed low level range must be at least 10 mV less than the high level.
        """,
        validator=strict_range,
        values=[-8, 7.9001],
        set_process=lambda x: HP8116A._get_value_with_unit(x, HP8116A._units_voltage),
        get_process=lambda x: HP8116A._parse_value_with_unit(x, HP8116A._units_voltage)
    )

    burst_number = Instrument.control(
        'IBUR', 'BUR %s #',
        """Control the number of periods generated in a burst (strict int from 1 to 1999).
        It is only valid for units with Option 001 in one of the burst modes.
        """,
        validator=strict_range,
        values=[1, 1999],
        get_process=lambda x: int(x[4:8])
    )

    repetition_rate = Instrument.control(
        'IRPT', 'RPT %s',
        """Control the repetition rate in s (i.e. the time between bursts)
        in 'internal_burst' mode (strict float from 20e-9 to 999e-3).
        """,
        validator=strict_range,
        values=[20e-9, 999.001e-3],
        set_process=lambda x: HP8116A._get_value_with_unit(x, HP8116A._units_time),
        get_process=lambda x: HP8116A._parse_value_with_unit(x, HP8116A._units_time)
    )

    sweep_start = Instrument.control(
        'ISTA', 'STA %s',
        """Control the start frequency in both sweep modes in Hz
        (strict float from 1e-3 to 52.5e6).
        """,
        validator=strict_range,
        values=[1e-3, 52.5001e6],
        set_process=lambda x: HP8116A._get_value_with_unit(x, HP8116A._units_frequency),
        get_process=lambda x: HP8116A._parse_value_with_unit(x, HP8116A._units_frequency)
    )

    sweep_stop = Instrument.control(
        'ISTP', 'STP %s',
        """Control the stop frequency in both sweep modes in Hz (strict float from 1e-3 to 52.5e6).
        """,
        validator=strict_range,
        values=[1e-3, 52.5001e6],
        set_process=lambda x: HP8116A._get_value_with_unit(x, HP8116A._units_frequency),
        get_process=lambda x: HP8116A._parse_value_with_unit(x, HP8116A._units_frequency)
    )

    sweep_marker_frequency = Instrument.control(
        'IMRK', 'MRK %s',
        """Control the frequency marker in both sweep modes in Hz
        (strict float from 1e-3 to 52.5e6).
        At this frequency, the marker output switches from low to high.
        """,
        validator=strict_range,
        values=[1e-3, 52.5001e6],
        set_process=lambda x: HP8116A._get_value_with_unit(x, HP8116A._units_frequency),
        get_process=lambda x: HP8116A._parse_value_with_unit(x, HP8116A._units_frequency)
    )

    sweep_time = Instrument.control(
        'ISWT', 'SWT %s',
        """Control the sweep time per decade in both sweep modes in s (float).
        The sweep time is selectable in a 1-2-5 sequence between 10 ms and 500 s.
        """,
        validator=truncated_discrete_set,
        values=_generate_1_2_5_sequence(10e-3, 500),
        set_process=lambda x: HP8116A._get_value_with_unit(x, HP8116A._units_time),
        get_process=lambda x: HP8116A._parse_value_with_unit(x, HP8116A._units_time)
    )

    @property
    def status(self):
        """Get the status byte of the 8116A as a :class:`Status` IntFlag-type enum."""
        return Status(self.adapter.connection.read_stb())

    @property
    def complete(self):
        """Get whether the measurement is complete (bool)."""
        return not (self.status & Status.buffer_not_empty)

    @property
    def options(self):
        """Get the device options installed. The only possible option is 001."""
        if self.has_option_001:
            return ['001']
        else:
            return []

    def start_autovernier(self, control, digit, direction, start_value=None):
        """ Start the autovernier on the specified control.

        :param control: The control to change, pass as :code:`HP8116A.some_control`. Allowed
                        controls are frequency, amplitude, offset, duty_cycle, and pulse_width
        :param digit: The digit to change, type: :py:class:`HP8116A.Digit`.
        :param direction: The direction in which to change the control,
                          type: :py:class:`HP8116A.Direction`.
        :param start_value: An optional value to start the autovernier at. If not specified,
                            the current value of the control is used.
        """
        if not self.autovernier_enabled:
            raise RuntimeError('Autovernier has to be enabled first.')

        if control not in (HP8116A.frequency, HP8116A.amplitude, HP8116A.offset,
                           HP8116A.duty_cycle, HP8116A.pulse_width):
            raise ValueError('Control must be one of frequency, amplitude, offset, ' +
                             'duty_cycle, or pulse_width.')

        start_value = control.fget(self) if start_value is None else start_value
        # The control always has to be set to select it for the autovernier.
        control.fset(self, start_value)

        self.write(digit.value + direction.value)

    def GPIB_trigger(self):
        """ Initiate trigger via low-level GPIB-command (aka GET - group execute trigger). """
        self.adapter.connection.assert_trigger()

    def reset(self):
        """ Initatiate a reset (like a power-on reset) of the 8116A. """
        self.adapter.connection.clear()
        self._wait_for_commands_processed()

    def shutdown(self):
        """ Gracefully close the connection to the 8116A. """
        self.adapter.connection.clear()
        self.adapter.close()
        super().shutdown()

    def check_errors(self):
        """ Check for errors in the 8116A.

        :return: list of error entries or empty list if no error occurred.
        """
        errors_response = self.ask('IERR', 100).split('\r\n')[0].strip(' ,\r\n')
        errors = errors_response.split('ERROR')[:-1]
        errors = [e.strip() + " ERROR" for e in errors]

        if errors[0] == 'NO ERROR':
            return []
        else:
            for error in errors:
                log.error(f'{self.name}: {error}')
            return errors

    def _wait_for_commands_processed(self, timeout=1):
        """ Wait until the commands have been processed by the 8116A. """
        start = time.time()
        while not self.complete:
            time.sleep(0.001)
            if time.time() - start > timeout:
                raise RuntimeError('Timeout waiting for commands to be processed.')

    def _check_has_option_001(self):
        """ Return True if the 8116A has option 001 and False otherwise.

        This is done by checking the length of the response to the CST (current status) command
        which includes sweep parameters and burst parameters only if the 8116A has option 001.
        """

        # The longest possible state string is 163 characters long including termination characters
        state_string = self.ask('CST', 163).split('\r\n')[0].strip(' ,\r\n')

        if len(state_string) == 159:
            return True
        elif len(state_string) == 87:
            return False
        else:
            log.warning('Could not determine if 8116A has option 001. Assuming it has.')
            return True
