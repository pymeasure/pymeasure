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

import math
import re
import logging

from pymeasure.instruments import Instrument

log = logging.getLogger(__name__)


class AH2500A(Instrument):
    """ Andeen Hagerling 2500A Precision Capacitance Bridge implementation
    """
    # regular expression to extract measurement values
    mcl = re.compile(r"[FHZ0-9.=\s]*C=\s*(-?[0-9.]+)\s*PF L=\s*(-?[0-9.]+)\s*NS")

    @classmethod
    def _parse_reply(cls, string):
        """
        parse reply string from Andeen Hagerling capacitance bridges.

        :param string: reply string from the instrument. This commonly is:
          2500A:
            "C=123.123456 PF L=0.12345 NS"
          2700A:
            "F= 1000.00 HZ C= 4.20188     PF L=-0.0260      NS V= 15.0     V"
        """
        m = cls.mcl.match(string)
        if m is not None:
            cap, loss = map(float, m.groups())
            return cap, loss
        # if an invalid string is returned ('EXCESS NOISE')
        log.warning("Excess noise, check your experiment setup")
        return math.nan, math.nan

    config = Instrument.measurement(
        "SHOW",
        """ Read out configuration """,
    )

    caploss = Instrument.measurement(
        "Q",
        """ Perform a single capacitance, loss measurement and return the
        values in units of pF and nS.""",
        get_process=_parse_reply,
    )

    def __init__(self, adapter, name=None, timeout=3000,
                 write_termination="\n", read_termination="\n",
                 **kwargs):
        kwargs.setdefault("write_termination", write_termination)
        kwargs.setdefault("read_termination", read_termination)
        kwargs.setdefault("timeout", timeout)
        kwargs.setdefault("includeSCPI", False)
        super(AH2500A, self).__init__(
            adapter,
            name or "Andeen Hagerling 2500A Precision Capacitance Bridge",
            **kwargs
        )
        self._triggered = False

    def trigger(self):
        """
        Triggers a new measurement without blocking and waiting for the return
        value.
        """
        self.write("TRG")
        self._triggered = True

    def triggered_caploss(self):
        """
        reads the measurement value after the device was triggered by the
        trigger function.
        """
        if not self._triggered:
            log.warning(
                "Device not triggered, trigger manually for better timing")
            self.trigger()
        self._triggered = False
        return parse_reply(self.read())
