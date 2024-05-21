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

from time import perf_counter_ns

from pymeasure.test import expected_protocol
from pymeasure.instruments.temptronic.temptronic_base import ATSBase


def test_check_query_delay():
    with expected_protocol(ATSBase, [("TTIM?", "7")]) as inst:
        start = perf_counter_ns()
        assert inst.maximum_test_time == 7
        delay = perf_counter_ns() - start
        # HACK acceptable factor is needed, as in CI under windows (Py38, Py39) the `sleep` interval
        # is slightly shorter than the given argument.
        acceptable_factor = 0.95
        assert delay > 0.05 * 1e9 * acceptable_factor
