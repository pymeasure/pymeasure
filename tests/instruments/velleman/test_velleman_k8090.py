#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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


"""
Test the instrument class for the Velleman F8090.

This is not an integration test! This is software-only.
"""

from pymeasure.test import expected_protocol
from pymeasure.instruments.velleman import VellemanK8090


def test_version():
    with expected_protocol(
        VellemanK8090,
        [
            (
                bytearray.fromhex("04 71 00 00 00 8B 0F"),
                bytearray.fromhex("04 71 FF 0A 01 81 0F"),
            )
        ],
    ) as inst:
        assert inst.version == (10, 1)


def test_status():
    with expected_protocol(
        VellemanK8090,
        [
            (
                bytearray.fromhex("04 18 00 00 00 E4 0F"),
                bytearray.fromhex("04 51 01 15 80 15 0F"),
            )
        ],
    ) as inst:
        last_on, curr_on, time_on = inst.status

        assert last_on == [True, False, False, False, False, False, False, False]
        assert curr_on == [True, False, True, False, True, False, False, False]
        assert time_on == [False, False, False, False, False, False, False, True]


def test_switch_on():
    with expected_protocol(
        VellemanK8090,
        [
            (
                bytearray.fromhex("04 11 05 00 00 E6 0F"),
                None,  # The real device does send a reply
            )
        ],
    ) as inst:
        inst.switch_on = [1, 3]
        # inst.switch_on([1, 3])


def test_switch_off():
    with expected_protocol(
        VellemanK8090,
        [
            (
                bytearray.fromhex("04 12 05 00 00 E5 0F"),
                None,
            )
        ],
    ) as inst:
        inst.switch_off = [1, 3]
