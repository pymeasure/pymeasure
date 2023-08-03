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


def test_disable_emission():
    with expected_protocol(
            IBeamSmart,
            init_comm + [("la off", ""), (None, "[OK]")],
    ) as inst:
        inst.emission = False


def test_setting_failed():
    with expected_protocol(
            IBeamSmart,
            init_comm + [("la off", ""), (None, "abc"), (None, "[OK]")],
    ) as inst:
        with pytest.raises(ValueError):
            inst.laser_enabled = False


def test_enable_channel():
    with expected_protocol(
            IBeamSmart,
            init_comm + [("en 3", ""), (None, "[OK]"),
                         ("sta ch 3", ""), (None, "ON"), (None, "[OK]"),
                         ("di 2", ""), (None, "[OK]"),
                         ("sta ch 2", ""), (None, "OFF"), (None, "[OK]"),
                         ]
    ) as inst:
        inst.ch_3.enabled = True
        assert inst.ch_3.enabled is True
        inst.ch_2.enabled = False
        assert inst.ch_2.enabled is False


def test_channel1_enabled_getter():
    with expected_protocol(
            IBeamSmart,
            init_comm + [("sta ch 1", ""), (None, "ON"), (None, "[OK]")],
    ) as inst:
        with pytest.warns(FutureWarning):
            assert inst.channel1_enabled is True


def test_channel1_enabled_setter():
    with expected_protocol(
            IBeamSmart,
            init_comm + [("en 1", ""), (None, "[OK]")],
    ) as inst:
        with pytest.warns(FutureWarning):
            inst.channel1_enabled = True


def test_channel_power():
    with expected_protocol(
            IBeamSmart,
            init_comm + [("ch 2 pow 100.000000 mic", ""), (None, "[OK]")]
    ) as inst:
        inst.ch_2.power = 100


def test_shutdown():
    with expected_protocol(
            IBeamSmart,
            init_comm + [("di 0", ""), (None, "[OK]"), ("la off", ""), (None, "[OK]")]
    ) as inst:
        inst.shutdown()
        assert inst.isShutdown is True
