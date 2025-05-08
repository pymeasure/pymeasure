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
ATS-545 & -645
THERMOSTREAM
Interface & Applications Manual
Revision B
November, 2015
"""

from pymeasure.instruments.temptronic.temptronic_base import ATSBase


class ATS545(ATSBase):
    """Represents the TemptronicATS545 instrument.

    Coding example

    .. code-block:: python

        ts = ATS545('ASRL3::INSTR')  # replace adapter address
        ts.configure()  # basic configuration (defaults to T-DUT)
        ts.start()  # starts flow (head position not changed)
        ts.set_temperature(25)  # sets temperature to 25 degC
        ts.wait_for_settling()  # blocks script execution and polls for settling
        ts.shutdown(head=False)  # disables thermostream, keeps head down

    """

    temperature_limit_air_low_values = [-80, 25]

    mode_values = {'manual': 10,    # 5 in ATSbase
                   'program': 0,    # 6 in ATSbase
                   'initial': 63},  # after power up, reading is 63

    def next_setpoint(self):
        """not implemented in ATS545

        set ``self.set_point_number`` instead
        """
        raise NotImplementedError

    def __init__(self, adapter, name="Temptronic ATS-545 Thermostream", **kwargs):
        super().__init__(adapter, name, **kwargs)
