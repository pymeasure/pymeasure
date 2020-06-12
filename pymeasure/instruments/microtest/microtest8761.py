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


import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range


from pymeasure.adapters import VISAAdapter


class Microtest8761(Instrument):
    """ Represents the microtest 8761 cable harness tester
    interface for interacting with the instrument.

    It can also be used for microtest 8740 8751 and 8700
    
    .. code-block:: python

    """
    ##############################
    # Conduction Resistance Test #
    ##############################
    def test(self):
        """ Read conduction resistance data.
        """
        self.write(":KEY TEST")

    def info(self):
        """ Dsiplay system information.
        """
        self.write(":SYSTEM :INFO X1")

    def __init__(self, adapter, **kwargs):
        super(Microtest8761, self).__init__(
            adapter, "Microtest 8761 cable harness tester", **kwargs
        )