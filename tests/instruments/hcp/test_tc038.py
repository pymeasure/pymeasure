#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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
from pymeasure.instruments.hcp.tc038 import _check_errors, _data_to_temp


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


# Error code tests
@pytest.mark.parametrize("code,message", [
    ("03", "Register number does not exist."),
    ("04", "Out of setpoint range."),
    ("05", "Out of data number range."),
    ("08", "Illegal parameter is set."),
])
def test_check_errors_with_EC2(code, message):
    # response layout: chr(2) + address + "01" + "ER" + EC1 + EC2 + chr(3)
    response = "\x020101ER" + code + "07\x03"
    errors = _check_errors(response)
    assert len(errors) == 1
    assert errors[0] == message + " Wrong parameter has number 07."


@pytest.mark.parametrize("code,message", [
    ("02", "Command does not exist or is not executable."),
    ("06", "Executed monitor without specifying what to monitor."),
    ("42", "Sum does not match the expected value."),
    ("43", "Data value greater than specified received."),
    ("44", "End of data or end of text character is not received."),
])
def test_check_errors_without_EC2(code, message):
    response = "\x020101ER" + code + "\x03"
    errors = _check_errors(response)
    assert errors == [message]


def test_check_errors_OK_response():
    response = "\x020101OK\x03"
    assert _check_errors(response) == []


def test_data_to_temp_zero():
    assert _data_to_temp("\x020101OK0000\x03") == 0.0


def test_data_to_temp_multidigit_hex():
    # 0x00C8 = 200 -> 20.0 °C
    assert _data_to_temp("\x020101OK00C8\x03") == 20.0


def test_data_to_temp_large_hex():
    # 0xFFFF = 65535 -> 6553.5 °C
    assert _data_to_temp("\x020101OKFFFF\x03") == 6553.5


def test_check_set_errors_returns_empty_on_OK():
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03"),
         (b"\x0201010WWRD0120,01,00C8\x03", b"\x020101OK\x03"),
         (b"\x0201010WWRD0120,01,00C8\x03", b"\x020101OK\x03")]
    ) as inst:
        inst.setpoint = 20
        # setpoint setter (check_set_errors=True) consumed one OK; verify the
        # helper returns [] explicitly via a fresh write/read cycle.
        inst.write("WWRD0120,01,00C8")
        assert inst.check_set_errors() == []
