#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from pymeasure.instruments.validators import strict_range

log = logging.getLogger(__name__)


class AH2500A(Instrument):
    """ Andeen Hagerling 2500A Precision Capacitance Bridge implementation
    """
    # regular expression to extract measurement values
    _reclv = re.compile(
        r"[FHZ0-9.=\s]*C=\s*(-?[0-9.]+)\s*PF L=\s*(-?[0-9.]+)\s*NS V=\s*(-?[0-9.]+)\s*V")
    _renumeric = re.compile(r'[-+]?(\d*\.?\d+)')

    def __init__(self, adapter, name=None, timeout=3000,
                 write_termination="\n", read_termination="\n",
                 **kwargs):
        kwargs.setdefault("includeSCPI", False)
        super().__init__(
            adapter,
            name or "Andeen Hagerling 2500A Precision Capacitance Bridge",
            write_termination=write_termination,
            read_termination=read_termination,
            timeout=timeout,
            **kwargs
        )
        self._triggered = False

    config = Instrument.measurement(
        "SHOW",
        """ Read out configuration """,
    )

    caplossvolt = Instrument.measurement(
        "Q",
        """ Perform a single capacitance, loss measurement and return the
        values in units of pF and nS. The used measurement voltage is returned
        as third value.""",
        # lambda function is needed here since AH2500A is otherwise undefined
        get_process=lambda v: AH2500A._parse_reply(v),
    )

    vhighest = Instrument.control(
        "SH V", "V %.4f",
        """maximum RMS value of the used measurement voltage. Values of up to
        15 V are allowed. The device will select the best suiting range below
        the given value.""",
        validator=strict_range,
        values=[0, 15],
        # typical replies: "VOLTAGE    HIGHEST= 15.0    V" or
        # "VOLTAGE HIGHEST 1.00    V"
        get_process=lambda v: float(AH2500A._renumeric.search(v).group(0)),
    )

    @classmethod
    def _parse_reply(cls, string):
        """
        parse reply string from Andeen Hagerling capacitance bridges.

        :param string: reply string from the instrument. This commonly is:
          2500A:
            "C= 1.234567    PF L= 0.000014    NS V= 0.750   V"
          2700A:
            "F= 1000.00 HZ C= 4.20188     PF L=-0.0260      NS V= 15.0     V"
        :returns: tuple with C, L, V values
        """
        m = cls._reclv.match(string)
        if m is not None:
            values = tuple(map(float, m.groups()))
            return values
        # if an invalid string is returned ('EXCESS NOISE')
        if string.strip() == "EXCESS NOISE":
            log.warning("Excess noise, check your experiment setup")
            return (math.nan, math.nan, math.nan)
        else:  # some unknown return string (e.g. misconfigured units)
            raise Exception(f'Returned string "{string}" could not be parsed')

    def trigger(self):
        """
        Triggers a new measurement without blocking and waiting for the return
        value.
        """
        self.write("TRG")
        self._triggered = True

    def triggered_caplossvolt(self):
        """
        reads the measurement value after the device was triggered by the
        trigger function.
        """
        if not self._triggered:
            log.warning(
                "Device not triggered, trigger manually for better timing")
            self.trigger()
        self._triggered = False
        return AH2500A._parse_reply(self.read())
