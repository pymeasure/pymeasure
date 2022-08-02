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

import pytest
from pytest import raises

from pymeasure.test import expected_protocol
from pymeasure.instruments import Instrument


class BasicTestInstrument(Instrument):
    def __init__(self, adapter, **kwargs):
        super().__init__(adapter, "Basic Test Instrument")
        self.kwargs = kwargs

    simple = Instrument.control(
        "VOLT?", "VOLT %s V",
        """Simple property replying with plain floats""",
    )
    with_error_checks = Instrument.control(
        "VOLT?", "VOLT %s V",
        """Property with error checks after both setting and getting""",
        check_set_errors=True,
        check_get_errors=True,
    )


def test_simple_protocol():
    """Test a property without parsing or channel prefixes."""
    with expected_protocol(
        BasicTestInstrument,
        [('VOLT?', 3.14),
         ('VOLT 4.5 V', None)]
    ) as instr:
        assert instr.simple == 3.14
        instr.simple = 4.5


def test_kwargs():
    """Test whether the kwargs are handed over correctly."""
    with expected_protocol(
        BasicTestInstrument,
        [],
        test=5,
        xyz="abc"
    ) as instr:
        assert instr.kwargs == {'test': 5, 'xyz': "abc"}


def test_error_checks():
    """Test protocol for getting and setting with error checks."""
    with expected_protocol(
        BasicTestInstrument,
        [('VOLT?', 3.14),
         ('SYST:ERR?', '0, 0'),
         ('VOLT 4.5 V', None),
         ('SYST:ERR?', '0, 0'),
         ]
    ) as instr:
        assert instr.with_error_checks == 3.14
        instr.with_error_checks = 4.5


def test_not_all_communication_used():
    """Test whether unused communication raises an error."""
    with raises(AssertionError, match="Unprocessed protocol definitions remain"):
        with expected_protocol(
            BasicTestInstrument,
            [('VOLT?', 3.14),
             ('VOLT 4.5 V', None),
             ]
        ) as instr:
            assert instr.simple == 3.14


def test_non_empty_write_buffer():
    with raises(AssertionError, match="Non-empty write buffer remains"):
        with expected_protocol(
            BasicTestInstrument,
            [('VOLT?', 3.14)]
        ) as instr:
            instr.adapter.write_bytes(b"VOLT")
            instr.adapter._index = 1


def test_non_empty_read_buffer():
    with raises(AssertionError, match="Non-empty read buffer remains"):
        with expected_protocol(
            BasicTestInstrument,
            [('VOLT?', 3.14)]
        ) as instr:
            instr.write("VOLT?")


def test_preprocess_reply_on_values():
    class InstrumentWithPreprocessValues(BasicTestInstrument):
        """Workaround to get preprocess_reply working with protocol tests."""
        def values(self, command, **kwargs):
            return super().values(command, preprocess_reply=lambda v: v + "2345", **kwargs)

    with expected_protocol(
        InstrumentWithPreprocessValues,
        [("VOLT?", "3.1")]
    ) as instr:
        assert instr.simple == 3.12345


@pytest.mark.xfail
def test_preprocess_reply_on_init():
    # TODO: For now preprocess_reply at init level is nonfunctional because this
    #  lives in the real adapter, should be fixed with #567
    class InstrumentWithPreprocess(BasicTestInstrument):
        def __init__(self, adapter, **kwargs):
            super().__init__(adapter, preprocess_reply=lambda v: v + "2345", **kwargs)

    with expected_protocol(
        InstrumentWithPreprocess,
        [("VOLT?", "3.1")]
    ) as instr:
        assert instr.simple == 3.12345
