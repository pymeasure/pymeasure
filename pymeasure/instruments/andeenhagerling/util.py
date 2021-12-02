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

mcl = re.compile("[FHZ0-9.=\s]*C=\s*(-?[0-9.]+)\s*PF L=\s*(-?[0-9.]+)\s*NS")

def parse_reply(string):
    """
    parse reply string from Andeen Hagerling capacitance bridges.

    :param string: reply string from the instrument. This commonly could be
      2500A: "C=123.123456 PF L=0.12345 NS"
      2700A: "F= 1000.00 HZ C= 4.20188     PF L=-0.0260      NS V= 15.0     V"
    """
    m = mcl.match(string)
    if m is not None:
        cap, loss = map(float, m.groups())
        return cap, loss
    # if an invalid string is returned ('EXCESS NOISE')
    return math.nan, math.nan
