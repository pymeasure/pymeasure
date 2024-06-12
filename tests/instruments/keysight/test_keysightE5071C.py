#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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

from pymeasure.instruments.keysight import KeysightE5071C
from pymeasure.test import expected_protocol

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def test_keysightE5071C_id():
    """
    Verify *IDN? communication to check:
    keysightE5071C.id
    keysightE5071C.manu
    keysightE5071C.model
    keysightE5071C.fw
    keysightE5071C.sn
    """
    with expected_protocol(
        KeysightE5071C,
        [
            ("*IDN?", "Keysight Technologies,E5071C,0,B.13.10\n\n"),
            ("*IDN?", "Keysight Technologies,E5071C,0,B.13.10\n\n"),
        ],
    ) as inst:
        assert inst.id == ["Keysight Technologies", "E5071C", "0", "B.13.10"]
        assert inst.manu == "Keysight Technologies"
        assert inst.model == "E5071C"
        assert inst.fw == "B.13.10"
        assert inst.sn == "0"
