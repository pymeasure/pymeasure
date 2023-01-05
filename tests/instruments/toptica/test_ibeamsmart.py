#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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


from pymeasure.instruments.toptica import IBeamSmart

# Note: This communication does not contain the first two device responses, as they are
# ignored due to `adapter.flush_read_buffer()`.
# The device communication depends on previous commands and whether the device power cycled.
# TODO verify the right talk usual communication
init_comm = [("echo off", None), ("prom off", None), ("talk usual", ""), (None, "[OK]")]


def test_init():
    with expected_protocol(IBeamSmart,
                           init_comm,
                           ):
        pass  # verify init


def test_version():
    with expected_protocol(
            IBeamSmart,
            init_comm + [("ver", ""), (None, "iBPs-001A01-05"), (None, "[OK]")],
    ) as inst:
        assert inst.version == "iBPs-001A01-05"


def test_power():
    with expected_protocol(
            IBeamSmart,
            init_comm + [("sh pow", ""), (None, "PIC  = 000001 uW  "), (None, "[OK]")],
    ) as inst:
        assert inst.power == 1


def test_disable_laser():
    with expected_protocol(
            IBeamSmart,
            init_comm + [("la off", ""), (None, "[OK]")],
    ) as inst:
        inst.laser_enabled = False


def test_setting_failed():
    with expected_protocol(
            IBeamSmart,
            init_comm + [("la off", ""), (None, "abc"), (None, "[OK]")],
    ) as inst:
        with pytest.raises(ValueError):
            inst.laser_enabled = False
