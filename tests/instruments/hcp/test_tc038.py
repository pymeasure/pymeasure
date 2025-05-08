#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

import pytest

from pymeasure.test import expected_protocol


from pymeasure.instruments.hcp import TC038


def test_setpoint():
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03"),
         (b"\x0201010WRDD0120,01\x03", b"\x020101OK00C8\x03")]
    ) as inst:
        assert inst.setpoint == 20


def test_setpoint_setter():
    # Communication from manual.
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03"),
         (b"\x0201010WWRD0120,01,00C8\x03", b"\x020101OK\x03")]
    ) as inst:
        inst.setpoint = 20


def test_setpoint_error():
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03"),
         (b"\x0201010WWRD0120,01,00C8\x03", b"\x020101ER0401\x03")]
    ) as inst:
        with pytest.raises(ConnectionError, match="Out of setpoint range"):
            inst.setpoint = 20


def test_temperature():
    # Communication from manual.
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03"),
         (b"\x0201010WRDD0002,01\x03", b"\x020101OK00C8\x03")]
    ) as inst:
        assert 20 == inst.temperature


def test_monitored():
    # Communication from manual.
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03"),
         (b"\x0201010WRM\x03", b"\x020101OK00C8\x03")]
    ) as inst:
        assert 20 == inst.monitored_value


def test_monitored_error():
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03"),
         (b"\x0201010WRM\x03", b"\x020101ER0600\x03")]
    ) as inst:
        with pytest.raises(ConnectionError, match="monitor"):
            inst.monitored_value


def test_set_monitored():
    # Communication from manual.
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03")]
    ):
        pass  # Instantiation calls set_monitored_quantity()


def test_set_monitored_wrong_input():
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03")]
    ) as inst:
        with pytest.raises(KeyError):
            inst.set_monitored_quantity("temper")


def test_information():
    # Communication from manual.
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03"),
         (b"\x0201010INF6\x03",
          b"\x020101OKUT150333 V01.R001111222233334444\x03")]
    ) as inst:
        value = inst.information
        assert value == "UT150333 V01.R001111222233334444"
