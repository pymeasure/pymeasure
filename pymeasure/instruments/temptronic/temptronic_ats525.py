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

"""
Implementation of an interface class for ThermoStream® Systems devices.
Reference Document for implementation:
ATS-515/615, ATS 525/625 & ATS 535/635 ThermoStream® Systems
Interface & Applications Manual
Revision E
September, 2019
"""

from pymeasure.instruments.temptronic.temptronic_base import ATSBase
from pymeasure.instruments.instrument import Instrument


class ATS525(ATSBase):
    """Represent the TemptronicATS525 instruments.
    """

    temperature_limit_air_low_values = [-60, 25]

    system_current = Instrument.measurement(
        "AMPS?",
        """Operating current.
        """,
    )

    def __init__(self, adapter, name="Temptronic ATS-525 Thermostream", **kwargs):
        super().__init__(adapter, name, **kwargs)
