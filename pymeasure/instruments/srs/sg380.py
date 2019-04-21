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
from pymeasure.instruments.validators import truncated_range


class SG380(Instrument):

    MOD_TYPES_VALUES = ['AM', 'FM', 'PM', 'SWEEP', 'PULSE', 'BLANK', 'IQ']

    MOD_FUNCTIONS = ['SINE', 'RAMP', 'TRIANGLE', 'SQUARE', 'NOISE', 'EXTERNAL']

    MIN_RF = 0.0

    MAX_RF = 4E9

    # TODO: restrict modulation depth to allowed values (depending on
    # frequency)
    fm_dev = Instrument.control(
        "FDEV?", "FDEV%.6f",
        """ A floating point property that represents the modulation frequency
        deviation in Hz. This property can be set. """
    )

    rate = Instrument.control(
        "RATE?", "RATE%.6f",
        """ A floating point property that represents the modulation rate
        in Hz. This property can be set. """
    )

    def __init__(self, resourceName, **kwargs):
        super(SG380, self).__init__(
            resourceName,
            "Stanford Research Systems SG380 RF Signal Generator",
            **kwargs
        )

    @property
    def has_doubler(self):
        """Gets the modulation type"""
        return bool(self.ask("OPTN? 2"))

    @property
    def has_IQ(self):
        """Gets the modulation type"""
        return bool(self.ask("OPTN? 3"))

    @property
    def frequency(self):
        """Gets RF frequency"""
        return float(self.ask("FREQ?"))

    @frequency.setter
    def frequency(self, frequency):
        """Defines RF frequency"""
        if self.has_doubler:
            truncated_range(frequency, (SG380.MIN_RF, 2*SG380.MAX_RF))
        else:
            truncated_range(frequency, (SG380.MIN_RF, SG380.MAX_RF))
        self.write("FREQ%.6f" % frequency)

    @property
    def mod_type(self):
        """Gets the modulation type"""
        return SG380.MOD_TYPES_VALUES[int(self.ask("TYPE?"))]

    @mod_type.setter
    def mod_type(self, type_):
        """Defines the modulation type"""
        if type_ not in SG380.MOD_TYPES_VALUES:
            raise RuntimeError('Undefined modulation type')
        elif (type_ == 'IQ') and not self.has_IQ:
            raise RuntimeError('IQ option not installed')
        else:
            index = SG380.MOD_TYPES_VALUES.index(type_)
        self.write("TYPE%d" % index)

    @property
    def mod_function(self):
        """Gets the modulation function"""
        return SG380.MOD_FUNCTIONS[int(self.ask("MFNC?"))]

    @mod_function.setter
    def mod_func(self, function):
        """Defines the modulation function"""
        if function not in SG380.MOD_FUNCTIONS:
            index = 1
        else:
            index = SG380.MOD_FUNCTIONS.index(function)
        self.write("MFNC%d" % index)
