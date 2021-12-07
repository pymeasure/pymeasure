#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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
from .ah2500a import AH2500A


class AH2700A(AH2500A):
    """ Andeen Hagerling 2700A Precision Capacitance Bridge implementation
    """
    id = Instrument.measurement(
        "*IDN?", """ Reads the instrument identification """
    )

    config = Instrument.measurement(
        "SHOW ALL",
        """ Read out configuration """,
    )

    def __init__(self, adapter, timeout=5000, **kwargs):
        super(AH2700A, self).__init__(
            adapter,
            name="Andeen Hagerling 2700A Precision Capacitance Bridge",
            timeout=timeout,
            includeSCPI=True,
            **kwargs)

    def trigger(self):
        """
        Triggers a new measurement without blocking and waiting for the return
        value.
        """
        self.write("*TRG")
        self._triggered = True
