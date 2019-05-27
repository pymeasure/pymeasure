#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set

CHANNEL_NUMS = [1, 2, 3]


class BKPrecision9130B(Instrument):
    """ Represents the BK Precision 9130B DC Power Supply interface for interacting with the instrument. """

    voltage = Instrument.control('MEASure:SCALar:VOLTage:DC?', 'SOURce:VOLTage:LEVel:IMMediate:AMPLitude %g',
                                 """Floating point property used to control voltage of the selected channel.""")

    current = Instrument.control('MEASure:SCALar:CURRent:DC?', 'SOURce:CURRent:LEVel:IMMediate:AMPLitude %g',
                                 """Floating point property used to control current of the selected channel.""")

    source_enabled = Instrument.control('SOURce:CHANnel:OUTPut:STATe?', 'SOURce:CHANnel:OUTPut:STATe %d',
                                        """A boolean property that controls whether the source is enabled, takes """
                                        """values True or False. """,
                                        validator=strict_discrete_set, values={True: 1, False: 0}, map_values=True)

    channel = Instrument.control('INSTrument:SELect?', 'INSTrument:SELect CH%d',
                                 f"""An integer property used to control which channel is selected. Can only take""" 
                                 f"""values {CHANNEL_NUMS}.""",
                                 validator=strict_discrete_set, values=CHANNEL_NUMS)

    def __init__(self, adapter, **kwargs) -> None:
        super().__init__(adapter, "BK Precision 9130B Source", **kwargs)


