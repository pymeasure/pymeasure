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
from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import (
    strict_discrete_set,
)

log = logging.getLogger(__name__)  # https://docs.python.org/3/howto/logging.html#library-config
log.addHandler(logging.NullHandler())

_FREQS_HZ = [
    100,
    120,
    400,
    1_000,
    4_000,
    10_000,
    40_000,
    50_000,
    75_000,
    100_000,
]  # Allowed frequencies in Hz
_RESIS_OHM = ["AUTO", 10, 100, 1_000, 10_000, 100_000]  # Allowed resistance ranges in Ohm
_LEVELS_MVRMS = [300, 600]  # Allowed levels in mVrms
_EQUIV = ["SER", "PAL"]  # Allowed equivalent circuit types
_IMPA = ["R", "L", "C", "Z", "AUTO"]  # Allowed main measurement parameters
_IMPB = ["X", "Q", "D", "THETA", "ESR"]  # Allowed secondary measurement parameters


def mixed_validator(value, values):
    """Validator that accepts both strings and numbers in the same list."""
    if isinstance(value, str):
        if value.upper() not in [v for v in values if isinstance(v, str)]:
            raise ValueError
    elif isinstance(value, (int, float)):
        if value not in [v for v in values if isinstance(v, (int, float))]:
            raise ValueError
    else:
        raise ValueError
    return value


class LCR500(SCPIMixin, Instrument):
    def __init__(self, adapter, name="Voltcraft LCR-500", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self.adapter.connection.write_termination = "\n"
        self.adapter.connection.read_termination = "\n"

    def _parse_fetch(self, value):
        """Parse the fetch response into a tuple of floats.
        The response is expected to be in the format: 'primary,secondary,range'
        """
        parts = value.split(",")
        if len(parts) != 3:
            raise ValueError("Invalid fetch response: %s" % value)
        return float(parts[0]), float(parts[1]), int(parts[2])

    go_to_local = Instrument.setting(
        "*GTL", """Switch the device to local mode and disable key lock."""
    )

    # -- Frequency Subsystem --
    frequency = Instrument.control(
        "FREQ?",
        "FREQ %d",
        """Control the measurement frequency in Hz (int).
        Can be one of: 100, 120, 400, 1k, 4k, 10k, 40k, 50k, 75k, 100k.
        """,
        validator=strict_discrete_set,
        values=_FREQS_HZ,
    )

    # -- Function Subsystem --
    main_parameter = Instrument.control(
        "FUNC:IMPA?",
        "FUNC:IMPA %s",
        """Control the main measurement parameter (str).
        Can be one of: 
            'R': Resistance, 
            'L': Inductance, 
            'C': Capacitance, 
            'Z': Impedance, 
            'AUTO': Automatic.
        """,
        validator=strict_discrete_set,
        values=_IMPA,
    )

    secondary_parameter = Instrument.control(
        "FUNC:IMPB?",
        "FUNC:IMPB %s",
        """Control the secondary measurement parameter (str).
        Can be one of:
            'X': Reactance, 
            'Q': Quality factor, 
            'D': Dissipation factor, 
            'THETA': Phase angle, 
            'ESR': Equivalent series resistance.
        """,
        validator=strict_discrete_set,
        values=_IMPB,
    )

    measurement_range = Instrument.control(
        "FUNC:RANG?",
        "FUNC:RANG %s",
        """Control the measurement range (str or int).
        Can be one of: 'AUTO', 10, 100, 1k, 10k, 100k.
        """,
        validator=mixed_validator,
        values=_RESIS_OHM,
    )

    level = Instrument.control(
        "FUNC:LEV?",
        "FUNC:LEV %d",
        """Control the measurement signal level in mVrms (int).
        Can be one of: 300, 600.
        """,
        validator=strict_discrete_set,
        values=_LEVELS_MVRMS,
    )
    equivalent_circuit = Instrument.control(
        "FUNC:EQUI?",
        "FUNC:EQUI %s",
        """Control the equivalent circuit type (str).
        Can be one of: 'SER', 'PAL'.
        """,
        validator=strict_discrete_set,
        values=_EQUIV,
    )

    # -- Fetch Subsystem --
    fetch = Instrument.measurement(
        "FETC?",
        """Perform a measurement and return the result as tuple of
        (primary_value, secondary_value, range_used).""",
        parser=_parse_fetch,
    )
