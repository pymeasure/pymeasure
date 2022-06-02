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

from pytest import raises

from pymeasure.test import expected_protocol
from pymeasure.instruments import Instrument


class BasicTestInstrument(Instrument):
    simple = Instrument.control(
        "VOLT?", "VOLT %s V",
        """Simple property replying with plain floats""",
    )


class InstrumentWithPreprocess(BasicTestInstrument):
    def values(self, command, **kwargs):
        return super().values(command, preprocess_reply=lambda v: v+"2345", **kwargs)

    # For now preprocess_reply at init level is nonfunctional because this
    # lives in the adapter, should be fixed with #567
    def __broken__init__(self, adapter, **kwargs):
        super().__init__(adapter, preprocess_reply=lambda v: v+"2345", **kwargs)


def test_simple_protocol():
    """Test a property without parsing or channel prefixes."""
    with expected_protocol(BasicTestInstrument,
                           [('VOLT?', 3.14),
                            ('VOLT 4.5 V', None),
                            ]) as instr:
        assert instr.simple == 3.14
        instr.simple = 4.5


def test_not_all_communication_used():
    """Test whether unused communication raises an error."""
    with raises(AssertionError, match="Unprocessed protocol definitions remain"):
        with expected_protocol(BasicTestInstrument,
                               [('VOLT?', 3.14),
                                ('VOLT 4.5 V', None),
                                ]) as instr:
            assert instr.simple == 3.14


def test_non_empty_write_buffer():
    with raises(AssertionError, match="Non-empty write buffer"):
        with expected_protocol(BasicTestInstrument,
                               [('VOLT?', 3.14),
                                ]) as instr:
            instr.adapter.write_bytes(b"VOLT")
            instr.adapter._index = 1


def test_non_empty_read_buffer():
    with raises(AssertionError, match="Non-empty read buffer"):
        with expected_protocol(BasicTestInstrument,
                               [('VOLT?', 3.14),
                                ]) as instr:
            instr.write("VOLT?")


def test_preprocess():
    with expected_protocol(InstrumentWithPreprocess,
                           [("VOLT?", "3.1")]) as instr:
        assert instr.simple == 3.12345

# After completing expected_protocol tests, add tests elsewhere:
# TODO: Add protocol tests for a simple instrument
# TODO: Add protocol tests for an instrument with multiple channels
# TODO: Add protocol tests for a frame-based instrument (recommend: TC038, TC038D)
# TODO: (Later) Add protocol tests for an instrument with a custom Adapter, refactor that (probably)
# TODO: (Later) Search for any custom Adapters and refactor those
