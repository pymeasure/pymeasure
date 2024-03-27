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

import pytest

from pymeasure.test import expected_protocol
from pymeasure.adapters import ProtocolAdapter
from pymeasure.instruments.generic_types import SCPIMixin, SCPIUnknownMixin
from pymeasure.instruments import Instrument


class Test_SCPIMixin:
    class SCPIInstrument(SCPIMixin, Instrument):
        pass

    def test_init(self):
        inst = self.SCPIInstrument(ProtocolAdapter(), "test")
        assert inst.SCPI is False  # should not be set by the new init

    @pytest.mark.parametrize("method, write, reply", (
        ("id", "*IDN?", "xyz, abc"),
        ("complete", "*OPC?", "1"),
        ("status", "*STB?", "189"),
        ("options", "*OPT?", "a9"),
    ))
    def test_SCPI_properties(self, method, write, reply):
        with expected_protocol(
                self.SCPIInstrument,
                [(write, reply)],
                name="test") as inst:
            assert getattr(inst, method) == reply

    def test_next_error(self):
        with expected_protocol(
                self.SCPIInstrument,
                [("SYST:ERR?", '-100,"Command error"')],
                name="test") as inst:
            assert inst.next_error == [-100, '"Command error"']

    @pytest.mark.parametrize("method, write", (("clear", "*CLS"),
                                               ("reset", "*RST"),
                                               ))
    def test_SCPI_write_commands(self, method, write):
        with expected_protocol(
                self.SCPIInstrument,
                [(write, None)],
                name="test") as inst:
            getattr(inst, method)()

    def test_check_errors(self):
        with expected_protocol(
                self.SCPIInstrument,
                [("SYST:ERR?", '-100,"Command error"'),
                 ("SYST:ERR?", '-222,"Data out of range"'),
                 ("SYST:ERR?", '0,"No error"'),
                 ],
                name="test") as inst:
            assert inst.check_errors() == [[-100, '"Command error"'],
                                           [-222, '"Data out of range"']]


def test_SCPIunknownMixin():
    class SCPIunknownInstrument(SCPIUnknownMixin, Instrument):
        pass

    with pytest.warns(FutureWarning):
        inst = SCPIunknownInstrument(ProtocolAdapter(), "test")
    assert inst.SCPI is False
