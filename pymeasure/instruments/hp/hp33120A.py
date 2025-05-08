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

from pymeasure.instruments import Instrument, SCPIUnknownMixin
from pymeasure.instruments.validators import strict_discrete_set

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class HP33120A(SCPIUnknownMixin, Instrument):
    """ Represents the Hewlett Packard 33120A Arbitrary Waveform
    Generator and provides a high-level interface for interacting
    with the instrument.
    """

    def __init__(self, adapter, name="Hewlett Packard 33120A Function Generator", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        self.amplitude_units = 'Vpp'

    SHAPES = {
        'sinusoid': 'SIN', 'square': 'SQU', 'triangle': 'TRI',
        'ramp': 'RAMP', 'noise': 'NOIS', 'dc': 'DC', 'user': 'USER'
    }
    shape = Instrument.control(
        "SOUR:FUNC:SHAP?", "SOUR:FUNC:SHAP %s",
        """Control the shape of the wave,
        which can take the values: sinusoid, square, triangle, ramp,
        noise, dc, and user. (str)""",
        validator=strict_discrete_set,
        values=SHAPES,
        map_values=True
    )

    frequency = Instrument.control(
        "SOUR:FREQ?", "SOUR:FREQ %g",
        """Control the frequency of the
        output in Hz. The allowed range depends on the waveform shape
        and can be queried with :attr:`~.max_frequency` and
        :attr:`~.min_frequency`. (float)"""
    )

    max_frequency = Instrument.measurement(
        "SOUR:FREQ? MAX",
        """ Get the maximum :attr:`~.HP33120A.frequency` in Hz for the given shape """
    )

    min_frequency = Instrument.measurement(
        "SOUR:FREQ? MIN",
        """ Get the minimum :attr:`~.HP33120A.frequency` in Hz for the given shape """
    )

    amplitude = Instrument.control(
        "SOUR:VOLT?", "SOUR:VOLT %g",
        """ Control the voltage amplitude of the
        output signal. The default units are in  peak-to-peak Volts, but can be
        controlled by :attr:`~.amplitude_units`. The allowed range depends
        on the waveform shape and can be queried with :attr:`~.max_amplitude`
        and :attr:`~.min_amplitude`. (float)"""
    )

    max_amplitude = Instrument.measurement(
        "SOUR:VOLT? MAX",
        """ Get the maximum :attr:`~.amplitude` in Volts for the given shape """
    )

    min_amplitude = Instrument.measurement(
        "SOUR:VOLT? MIN",
        """ Get the minimum :attr:`~.amplitude` in Volts for the given shape """
    )

    offset = Instrument.control(
        "SOUR:VOLT:OFFS?", "SOUR:VOLT:OFFS %g",
        """ Control the amplitude voltage offset
        in Volts. The allowed range depends on the waveform shape and can be
        queried with :attr:`~.max_offset` and :attr:`~.min_offset`. """
    )

    max_offset = Instrument.measurement(
        "SOUR:VOLT:OFFS? MAX",
        """ Get the maximum :attr:`~.offset` in Volts for the given shape """
    )

    min_offset = Instrument.measurement(
        "SOUR:VOLT:OFFS? MIN",
        """ Get the minimum :attr:`~.offset` in Volts for the given shape """
    )

    AMPLITUDE_UNITS = {'Vpp': 'VPP', 'Vrms': 'VRMS', 'dBm': 'DBM', 'default': 'DEF'}
    amplitude_units = Instrument.control(
        "SOUR:VOLT:UNIT?", "SOUR:VOLT:UNIT %s",
        """ Control the units of the amplitude,
        which can take the values Vpp, Vrms, dBm, and default. (str)
        """,
        validator=strict_discrete_set,
        values=AMPLITUDE_UNITS,
        map_values=True
    )

    burst_enabled = Instrument.control(
        "BM:STATE?", "BM:STATE %d",
        """Control state of burst modulation""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    burst_source = Instrument.control(
        "BM:SOURCE?", "BM:SOURCE %s",
        """Control internal or external gate source for burst modulation""",
        validator=strict_discrete_set,
        values=['INT', 'EXT'],
    )

    burst_count = Instrument.control(
        "BM:NCYC?", "BM:NCYC %d",
        """Control the number of cycles per burst (1 to 50,000 cycles)""",
    )

    min_burst_count = Instrument.measurement(
        "BM:NCYC? MIN",
        """Get the minimum :attr:`~.HP33120A.burst_count`"""
    )

    max_burst_count = Instrument.measurement(
        "BM:NCYC? MAX",
        """Get the maximum :attr:`~.HP33120A.burst_count`"""
    )

    burst_rate = Instrument.control(
        "BM:INT:RATE?", "BM:INT:RATE %g",
        """Control the burst rate in Hz fo an internal burst source"""
    )

    min_burst_rate = Instrument.measurement(
        "BM:INT:RATE? MIN",
        """Get the minimum :attr:`~.HP33120A.burst_rate`"""
    )

    max_burst_rate = Instrument.measurement(
        "BM:INT:RATE? MAX",
        """Get the maximum :attr:`~.HP33120A.burst_rate`"""
    )

    burst_phase = Instrument.control(
        "BM:PHAS?", "BM:PHAS %g",
        """Control the starting phase angle of a burst (-360 to +360 degrees)"""
    )

    min_burst_phase = Instrument.measurement(
        "BM:PHAS? MIN",
        """Get the minimum :attr:`~.HP33120A.burst_phase`"""
    )

    max_burst_phase = Instrument.measurement(
        "BM:PHAS? MAX",
        """Get the maximum :attr:`~.HP33120A.burst_phase`"""
    )

    def beep(self):
        """ Causes a system beep. """
        self.write("SYST:BEEP")
