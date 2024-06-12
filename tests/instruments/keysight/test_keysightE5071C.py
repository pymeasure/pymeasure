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
    ) as keysighte5071c:
        assert keysighte5071c.id == ["Keysight Technologies", "E5071C", "0", "B.13.10"]
        assert keysighte5071c.manu == "Keysight Technologies"
        assert keysighte5071c.model == "E5071C"
        assert keysighte5071c.fw == "B.13.10"
        assert keysighte5071c.sn == "0"
        # options


def test_keysightE5071C_channels():
    with expected_protocol(
        KeysightE5071C,
        [
            ("SERV:CHAN:ACT?", "1\n\n"),
        ],
    ) as keysighte5071c:
        assert keysighte5071c.ch_1.get_active_channel == 1


def test_keysightE5071C_scan_points():
    with expected_protocol(
        KeysightE5071C,
        [
            ("SENS1:SWE:POIN?", "201\n\n"),
        ],
    ) as keysighte5071c:
        assert keysighte5071c.ch_1.scan_points == 201


def test_keysightE5071C_averaging():
    with expected_protocol(
        KeysightE5071C,
        [
            (":SENS1:AVER?", "0\n\n"),
        ],
    ) as keysighte5071c:
        assert keysighte5071c.ch_1.averaging_enabled is False


# def test_keysightE5071C_frequencies(keysighte5071c):


# def test_keysightE5071C_scan(keysighte5071c):


# def test_keysightE5071C_data_complex(keysighte5071c):


# def test_keysightE5071C_shutdown(keysighte5071c):


# def test_keysightE5071C_warmup_complete(keysighte5071c):


# def test_keysightE5071C_emit_beeps(keysighte5071c):


# def test_keysightE5071C_output_power(keysighte5071c):


# def test_keysightE5071C_triggering(keysighte5071c):


# def test_keysightE5071C_windows(keysighte5071c):


# def test_keysightE5071C_sweep(keysighte5071c):
