#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
from pymeasure.instruments.validators import strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

Attenuator_11dB = {
    0: (False, False, False, False),
    1: (True, False, False, False),
    2: (False, True, False, False),
    3: (True, True, False, False),
    4: (False, False, False, True),
    5: (True, False, False, True),
    6: (False, True, False, True),
    7: (True, True, False, True),
    8: (False, False, True, True),
    9: (True, False, True, True),
    10: (False, True, True, True),
    11: (True, True, True, True),
}
""" Mapping of logical values for use with 0 - 11 dB attenuators """

Attenuator_110dB = {
    0: (False, False, False, False),
    10: (True, False, False, False),
    20: (False, True, False, False),
    30: (True, True, False, False),
    40: (False, False, False, True),
    50: (True, False, False, True),
    60: (False, True, False, True),
    70: (True, True, False, True),
    80: (False, False, True, True),
    90: (True, False, True, True),
    100: (False, True, True, True),
    110: (True, True, True, True),
}
""" Mapping of logical values for use with 0 - 110 dB attenuators """

Attenuator_70dB_3_Section = {
    0: (False, False, False, False),
    10: (True, False, False, False),
    20: (False, True, False, False),
    30: (True, True, False, False),
    40: (False, False, True, False),
    50: (True, False, True, False),
    60: (False, True, True, False),
    70: (True, True, True, False),
}
""" Mapping of logical values for use with 0 - 70 dB attenuators with 3 switching sections """


class HP11713A(Instrument):
    """
    A switch driver
    """

    ATTENUATOR_X = {}
    ATTENUATOR_Y = {}

    def __init__(self, adapter, name="Hewlett-Packard HP11713A", deactivate_string="B1234567890",
                 **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            send_end=True,
            **kwargs,
        )
        self.deactivate_string = deactivate_string

    def x(self, one, two, three, four):
        """ Set switches according to the booleans """
        cmd_str = ""
        cmd_str += "A" if any([one, two, three, four]) else ""
        cmd_str += "1" if one else ""
        cmd_str += "2" if two else ""
        cmd_str += "3" if three else ""
        cmd_str += "4" if four else ""
        cmd_str += "B" if not all([one, two, three, four]) else ""
        cmd_str += "1" if not one else ""
        cmd_str += "2" if not two else ""
        cmd_str += "3" if not three else ""
        cmd_str += "4" if not four else ""
        self.write(cmd_str)

    def y(self, five, six, seven, eight):
        """ Set switches according to the booleans """
        cmd_str = ""
        cmd_str += "A" if any([five, six, seven, eight]) else ""
        cmd_str += "5" if five else ""
        cmd_str += "6" if six else ""
        cmd_str += "7" if seven else ""
        cmd_str += "8" if eight else ""
        cmd_str += "B" if not all([five, six, seven, eight]) else ""
        cmd_str += "5" if not five else ""
        cmd_str += "6" if not six else ""
        cmd_str += "7" if not seven else ""
        cmd_str += "8" if not eight else ""
        self.write(cmd_str)

    def attenuation_x(self, attenuation):
        """ Set switches according to the attenuation in dB for X

        A attenuation mapping has to be set in before e.g.

        .. code-block:: python
            from pymeasure.instruments.hp.hp11713a import HP11713A, Attenuator_110dB

            instr.ATTENUATOR_X = Attenuator_110dB
        """
        i, j, k, m = self.ATTENUATOR_X[attenuation]
        self.x(i, j, k, m)

    def attenuation_y(self, attenuation):
        """ Set switches according to the attenuation in dB for Y

        A attenuation mapping has to be set in before e.g.

        .. code-block:: python
            from pymeasure.instruments.hp.hp11713a import HP11713A, Attenuator_110dB

            instr.ATTENUATOR_X = Attenuator_110dB
        """
        i, j, k, m = self.ATTENUATOR_Y[attenuation]
        self.y(i, j, k, m)

    s9 = Instrument.setting(
        "%s",
        """Turn on S9 A/B
        
        The switch is always alternating between A 24V and B 24V.
        """,
        validator=strict_discrete_set,
        values={True: "A9", False: "B9"},
        map_values=True
    )

    s0 = Instrument.setting(
        "%s",
        """Turn on S0 A/B
        
        The switch is always alternating between A 24V and B 24V.
        """,
        validator=strict_discrete_set,
        values={True: "A0", False: "B0"},
        map_values=True
    )

    def deactivate_all(self):
        """
        Deactivate all switches to 'B' per default or any other deactivation string given per
        constructor.
        """
        self.write(self.deactivate_string)
