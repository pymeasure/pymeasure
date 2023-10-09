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
from pymeasure.instruments import Instrument, Channel

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

Attenuator_70dB_4_Section = {
    0: (False, False, False, False),
    10: (True, False, False, False),
    20: (False, False, False, True),
    30: (True, False, False, True),
    40: (False, True, False, True),
    50: (True, True, False, True),
    60: (False, True, True, True),
    70: (True, True, True, True),
}
""" Mapping of logical values for use with 0 - 70 dB attenuators with 4 switching sections """


class SwitchDriverChannel(Channel):
    enabled = Instrument.setting(
        "%s{ch}",
        """
        Set this channel to the polarity 'A' for True and 'B' for False.
        """,
        map_values=True,
        values={True: "A", False: "B"}
    )


class HP11713A(Instrument):
    """
    Represents the HP 11713A Switch and Attenuator Driver and provides a high-level
    interface for interacting with the instrument.

    Usually an attenuator is hooked to either X or Y or X and Y. To ease the control
    of the attenuator driver you have the possibility to set an attenuator type via
    the attribute 'ATTENUATOR_X' or 'ATTENUATOR_Y'. The hp11713a keeps different default attenuator
    mappings. After setting the attenuator type you are able to use the methods 'attenuation_x'
    and/or 'attenuation_y' to set the switch driver to the correct value for the specified
    attenuation. The attenuation values are rounded.

    .. code-block:: python

        from pymeasure.instruments.hp import HP11713A
        from pymeasure.instruments.hp.hp11713a import Attenuator_110dB

        sd = HP11713A("GPIB::1")

        sd.ATTENUATOR_Y = Attenuator_110dB
        sd.attenuation_y(10)
        sd.ch_0.enabled = True

    """

    ATTENUATOR_X = {}
    ATTENUATOR_Y = {}

    channels = Instrument.MultiChannelCreator(SwitchDriverChannel, list(range(0, 9)))

    def __init__(self, adapter, name="Hewlett-Packard HP11713A",
                 **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            send_end=True,
            **kwargs,
        )

    def attenuation_x(self, attenuation):
        """ Set switches according to the attenuation in dB for X

        The set attenuation will be rounded to the next available step.
        An attenuation mapping has to be set in before e.g.

        .. code-block:: python

            from pymeasure.instruments.hp.hp11713a import HP11713A, Attenuator_110dB

            instr.ATTENUATOR_X = Attenuator_110dB
            instr.attenuation_x(10)
        """
        rounding = 0
        if list(self.ATTENUATOR_X.keys())[1] == 10:
            rounding = -1

        self.ch_1.enabled, self.ch_2.enabled, self.ch_3.enabled, self.ch_4.enabled = \
            self.ATTENUATOR_X[int(round(attenuation, rounding))]

    def attenuation_y(self, attenuation):
        """ Set switches according to the attenuation in dB for Y

        The set attenuation will be rounded to the next available step.
        An attenuation mapping has to be set in before e.g.

        .. code-block:: python

            from pymeasure.instruments.hp.hp11713a import HP11713A, Attenuator_110dB

            instr.ATTENUATOR_Y = Attenuator_110dB
            instr.attenuation_y(10)
        """
        rounding = 0
        if list(self.ATTENUATOR_Y.keys())[1] == 10:
            rounding = -1

        self.ch_5.enabled, self.ch_6.enabled, self.ch_7.enabled, self.ch_8.enabled = \
            self.ATTENUATOR_Y[int(round(attenuation, rounding))]

    def deactivate_all(self):
        """
        Deactivate all switches to polarity 'B'.
        """
        self.write("B1234567890")
