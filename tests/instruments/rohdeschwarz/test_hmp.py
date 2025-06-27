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
from pymeasure.instruments.rohdeschwarz.hmp import process_sequence


def test_process_sequence():
    "Test `process_sequence` function."

    # Sequence must contain multiple of 3 values.
    with pytest.raises(ValueError):
        process_sequence([1.0, 1.0, 1.0, 2.0, 2.0])

    # Dwell times must be between 0.06 and 10 s.
    with pytest.raises(ValueError):
        process_sequence([1.0, 1.0, 1.0, 2.0, 2.0, 0.05])

    with pytest.raises(ValueError):
        process_sequence([1.0, 1.0, 1.0, 2.0, 2.0, 10.1])

    # Test with a valid sequence.
    sequence = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    assert process_sequence(sequence) == "1.0,2.0,3.0,4.0,5.0,6.0"
