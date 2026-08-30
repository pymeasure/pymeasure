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

from pymeasure.instruments.ami.ami430 import AMI430
from pymeasure.test import expected_protocol

# AMI430.__init__ reads (and discards) two welcome/connect message lines
# before any other communication; their content is irrelevant here.
INIT = [(None, b"welcome1"), (None, b"welcome2")]


def test_has_persistent_switch_enabled_true():
    with expected_protocol(
            AMI430,
            INIT + [(b"PSwitch?", b"1")],
    ) as instr:
        assert instr.has_persistent_switch_enabled() is True


def test_has_persistent_switch_enabled_false():
    with expected_protocol(
            AMI430,
            INIT + [(b"PSwitch?", b"0")],
    ) as instr:
        assert instr.has_persistent_switch_enabled() is False


def test_enable_persistent_switch():
    with expected_protocol(
            AMI430,
            INIT + [(b"PSwitch 1", None)],
    ) as instr:
        instr.enable_persistent_switch()


def test_disable_persistent_switch():
    with expected_protocol(
            AMI430,
            INIT + [(b"PSwitch 0", None)],
    ) as instr:
        instr.disable_persistent_switch()
