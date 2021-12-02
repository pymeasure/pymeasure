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
from .util import parse_reply


class AH2500A(Instrument):
    """ Andeen Hagerling 2500A Precision Capacitance Bridge implementation
    """
    id = "Andeen Hagerling AH2500A"  # device does not support '*IDN?'

    config = Instrument.measurement(
        "SHOW",
        """ Read out configuration """,
    )

    caploss = Instrument.measurement(
        "Q",
        """ Perform a single capacitance, loss measurement and return the
        values in units of pF and nS.""",
        get_process=parse_reply
    )

    def __init__(self, adapter, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = 3000
        if "write_termination" not in kwargs:
            kwargs["write_termination"] = "\n"
        if "read_termination" not in kwargs:
            kwargs["read_termination"] = "\n"
        super(AH2500A, self).__init__(
            adapter, "Andeen Hagerling 2x00A Precision Capacitance Bridge",
            **kwargs
        )
        self._triggered = False

    def trigger(self):
        self._triggered = True
        self.write("TRG")

    def triggered_caploss(self):
        if self._triggered:
            return parse_reply(self.read())
        else:
            raise Exception("Device was not triggered previously!")
