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
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

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
    def haversine(self):
        """ With triggered, gate or E.BUR operating mode selected and shape
        set to sine or triangle, this setting shifts the start phase of the
        waveform is -90°. As a result, haversine and havertriangle signals
        can be generated.
        """
        raise NotImplementedError
    
    @haversine.setter
    def haversine(self, haversine):
        haversine_set = int(haversine)
        haversine_cmd = "Z" + str(int(strict_discrete_set(haversine_set, [0, 1])))
        self.write(haversine_cmd)

    ## Instrument communication ##

    def write(self, command):
        """ Write a command to the instrument.
        If the command is a query (interrogate or CST for instrument state),
        wait for the 8116A to respond before returning.
        """
        self.adapter.write(command)

        if command.strip().lower()[0] in ('i', 'c'):
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
    
    def values(self, command, num_bytes, separator=',', cast=float, preprocess_reply=None, **kwargs):
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

    ## Numeric parameter parsing ##

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
    
    ## Controls and settings ##

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
    
    ## Functions using low-level access via instrument.adapter.connection methods ##

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


