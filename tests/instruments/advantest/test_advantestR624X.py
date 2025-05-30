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

from pymeasure.test import expected_protocol

from pymeasure.instruments.advantest import AdvantestR6246


def test_init():
    with expected_protocol(
            AdvantestR6246,
            [],
            ):
        pass  # Verify the expected communication.


def test_set_current():
    with expected_protocol(
        AdvantestR6246,
        [("di 1,0,2.1100e-04,2.1300e-04", None),
         ("spot 1,2.3120e-03", None),
         (None, "ABCD 7.311e-4")]
    ) as inst:
        inst.ch_A.current_source(0, 0.000211, 2.13e-4)
        inst.ch_A.change_source_current = 23.12e-4
        assert inst.read_measurement() == 0.0007311


def test_event_status_setter():
    with expected_protocol(
        AdvantestR6246,
        [('*ese 255', None),
         ('*ese?', "200")]
    ) as inst:
        inst.event_status_enable = 258  # too large, gets truncated
        assert inst.event_status_enable == 200
