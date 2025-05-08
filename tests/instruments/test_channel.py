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

from unittest import mock

import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments import Channel, Instrument
from pymeasure.instruments.validators import truncated_range


class GenericChannel(Channel):
    #  Use truncated_range as this easily lets us test for the range boundaries
    fake_ctrl = Channel.control(
        "C{ch}:control?", "C{ch}:control %d", "Control docs",
        validator=truncated_range,
        values=(1, 10),
        dynamic=True,
    )
    fake_setting = Channel.setting(
        "C{ch}:setting %d", "Set docs",
        validator=truncated_range,
        values=(1, 10),
        dynamic=True,
    )
    fake_measurement = Channel.measurement(
        "C{ch}:measurement?", "Measure docs",
        values={'X': 1, 'Y': 2, 'Z': 3},
        map_values=True,
        dynamic=True,
    )
    special_control = Channel.control(
        "SOUR{ch}:special?", "OUTP{ch}:special %s",
        """Control with different channel specifiers for get and set.""",
        cast=str,
    )
    check_errors_control = Channel.control(
        "C{ch}:xy?", "C{ch}:xy %d",
        """Control something, with error check on get and set.""",
        check_set_errors=True,
        check_get_errors=True,
    )


class ChannelWithPlaceholder(Channel):
    """A test channel with a different placeholder"""

    placeholder = "fn"

    test = Channel.control("{fn}test?", "test{fn} %i", """Control test.""")


class ChannelInstrument(Instrument):
    def __init__(self, adapter, name="ChannelInstrument", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self.errors = []
        self.add_child(GenericChannel, "A")
        self.add_child(GenericChannel, "B")

    def check_errors(self):
        err = self.values("SYST:ERR?")
        if err:
            self.errors.append(err)
        return err


class TestChannelCommunication:
    @pytest.fixture()
    def ch(self):
        a = mock.MagicMock(return_value="5")
        return Channel(a, "A")

    def test_write(self, ch):
        ch.write("abc")
        assert ch.parent.method_calls == [mock.call.write('abc')]

    def test_read(self, ch):
        ch.read()
        assert ch.parent.method_calls == [mock.call.read()]

    def test_write_bytes(self, ch):
        ch.write_bytes(b"abc")
        assert ch.parent.method_calls == [mock.call.write_bytes(b"abc")]

    def test_read_bytes(self, ch):
        ch.read_bytes(5)
        assert ch.parent.method_calls == [mock.call.read_bytes(5)]

    def test_write_binary_values(self, ch):
        ch.write_binary_values("abc", [5, 6, 7])
        assert ch.parent.method_calls == [mock.call.write_binary_values("abc", [5, 6, 7])]

    def test_read_binary_values(self, ch):
        ch.read_binary_values()
        assert ch.parent.method_calls == [mock.call.read_binary_values()]

    def test_check_errors(self, ch):
        ch.check_errors()
        assert ch.parent.method_calls == [mock.call.check_errors()]

    def test_check_get_errors(self, ch):
        ch.check_get_errors()
        assert ch.parent.method_calls == [mock.call.check_get_errors()]

    def test_check_set_errors(self, ch):
        ch.check_set_errors()
        assert ch.parent.method_calls == [mock.call.check_set_errors()]


def test_channel_with_different_prefix():
    c = ChannelWithPlaceholder(None, "A")
    assert c.insert_id("id:{fn}") == "id:A"


def test_channel_write():
    with expected_protocol(ChannelInstrument, [("ChA:volt?", None)]) as inst:
        inst.ch_A.write("Ch{ch}:volt?")


def test_channel_write_name_twice():
    """Verify, that any (i.e. more than one) occurrence of '{ch}' is changed."""
    with expected_protocol(ChannelInstrument, [("ChA:volt:ChA?", None)]) as inst:
        inst.ch_A.write("Ch{ch}:volt:Ch{ch}?")


def test_channel_write_without_ch():
    """Verify, that it is possible to send a command without '{ch}'."""
    with expected_protocol(ChannelInstrument, [("Test", None)]) as inst:
        inst.ch_A.write("Test")


def test_channel_control():
    with expected_protocol(
            ChannelInstrument,
            [("CA:control 7", None), ("CA:control?", "1.45")]
    ) as inst:
        inst.ch_A.fake_ctrl = 7
        assert inst.ch_A.fake_ctrl == 1.45


def test_channel_setting():
    with expected_protocol(
            ChannelInstrument,
            [("CA:setting 3", None)]
    ) as inst:
        inst.ch_A.fake_setting = 3


def test_channel_measurement():
    with expected_protocol(
            ChannelInstrument,
            [("CA:measurement?", "2")]
    ) as inst:
        assert inst.ch_A.fake_measurement == "Y"


def test_channel_dynamic_property():
    with expected_protocol(ChannelInstrument, [("CA:control 100", None)]) as inst:
        inst.ch_A.fake_ctrl_values = (1, 200)
        # original values is (1, 10), therefore 100 should not be allowed.
        inst.ch_A.fake_ctrl = 100


def test_channel_special_control():
    """Test different Prefixes for getter and setter."""
    with expected_protocol(ChannelInstrument,
                           [("SOURA:special?", "super"),
                            ("OUTPB:special test", None)],
                           ) as inst:
        assert inst.ch_A.special_control == "super"
        inst.ch_B.special_control = "test"


def test_channel_check_set_errors():
    with expected_protocol(ChannelInstrument,
                           [("CA:xy 5", None),
                            ("SYST:ERR?", "Some, error")],
                           ) as inst:
        inst.ch_A.check_errors_control = 5
        assert inst.errors == [["Some", " error"]]


def test_channel_check_get_errors():
    with expected_protocol(ChannelInstrument,
                           [("CA:xy?", "5"),
                            ("SYST:ERR?", "Some, error")],
                           ) as inst:
        assert inst.ch_A.check_errors_control == 5
        assert inst.errors == [["Some", " error"]]
