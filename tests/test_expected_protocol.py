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

from pymeasure.test import expected_protocol
from pymeasure.instruments import Instrument


class BasicTestInstrument(Instrument):
    simple = Instrument.control(
        "VOLT?", "VOLT %s V",
        """Simple property replying with plain floats""",
    )


def test_simple_protocol():
    """Test a property without parsing or channel prefixes."""
    with expected_protocol(BasicTestInstrument,
                           [('VOLT?', 3.14),
                            ('VOLT 4.5 V',),
                            ]) as instr:
        assert instr.simple == 3.14
        instr.simple = 4.5


# After completing expected_protocol tests, add tests elsewhere:
# TODO: Add protocol tests for a simple instrument
# TODO: Add protocol tests for an instrument with multiple channels
# TODO: Add protocol tests for a frame-based instrument (recommend: TC038, TC038D)
# TODO: (Later) Add protocol tests for an instrument with a custom Adapter, refactor that (probably)
# TODO: (Later) Search for any custom Adapters and refactor those
