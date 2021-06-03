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

"""
Implementation of an interface class for ThermoStream® Systems devices.

Reference Document for implementation:

ATS-515/615, ATS 525/625 & ATS 535/635 ThermoStream® Systems
Interface & Applications Manual
Revision E
September, 2019

"""

from pymeasure.instruments.temptronic.temptronic_base import Base
from pymeasure.instruments.instrument import Instrument
from pymeasure.instruments.validators import truncated_range


class ATS615(Base):
    """Represent the TemptronicATS615 instruments.
    """

    temperature_limit_air_low = Instrument.control(
        "LLIM?", "LLIM %g",
        """lower air temperature limit.

        Set or get the lower air temperature limit.
        LLIM nnn -- where nnn is -45 to +25 °C
        NOTE: LLIM limits the minimum air temperature in both air and
        DUT control modes. Additionally, an “out of range” error generates
        if a setpoint is less than this value.

        """,
        validator=truncated_range,
        values=[-45, 25]
        )
