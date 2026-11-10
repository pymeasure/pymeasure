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

import pytest

from pymeasure.instruments.agilent import Agilent33622A
from pymeasure.instruments.agilent.agilent33622A import Agilent33622AChannel
from pymeasure.test import expected_protocol

# None is the instrument's default channel
TARGETS = {1: "SOUR1:", 2: "SOUR2:", None: ""}

# property, command, format, (min, max), (below min, above max)
LIMITS = [
    ("amplitude", "VOLT", "%f", (1e-3, 20), (0.9e-3, 20.001)),
    ("offset", "VOLT:OFFS", "%f", (-10, 10), (-10.001, 10.001)),
    ("voltage_high", "VOLT:HIGH", "%f", (-9.999, 10), (-10, 10.001)),
    ("voltage_low", "VOLT:LOW", "%f", (-10, 9.999), (-10.001, 10)),
    ("square_dutycycle", "FUNC:SQU:DCYC", "%f", (0.01, 99.98), (0.009, 99.981)),
    ("pulse_period", "FUNC:PULS:PER", "%e", (10e-9, 1e6), (9.9e-9, 1.001e6)),
    ("pulse_width", "FUNC:PULS:WIDT", "%e", (5e-9, 1e6), (4.9e-9, 1.001e6)),
    ("pulse_transition", "FUNC:PULS:TRAN:BOTH", "%e", (2.9e-9, 1e-6), (2.8e-9, 1.001e-6)),
    ("burst_ncycles", "BURS:NCYC", "%d", (1, 100_000_000), (0, 100_000_001)),
    ("arb_srate", "FUNC:ARB:SRAT", "%f", (1e-6, 1e9), (0.9e-6, 1.001e9)),
]


def get_target(inst, target):
    return inst if target is None else inst.channels[target]


def test_init():
    with expected_protocol(Agilent33622A, []) as inst:
        assert inst.name == "Agilent 33622A"
        assert isinstance(inst.ch_1, Agilent33622AChannel)
        assert isinstance(inst.ch_2, Agilent33622AChannel)


@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("bound", (0, 1))
@pytest.mark.parametrize("prop, command, fmt, limits, outside", LIMITS)
def test_setter_limits(prop, command, fmt, limits, outside, bound, target):
    value = limits[bound]
    with expected_protocol(
        Agilent33622A,
        [(f"{TARGETS[target]}{command} {fmt % value}", None)],
    ) as inst:
        setattr(get_target(inst, target), prop, value)


@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("bound", (0, 1))
@pytest.mark.parametrize("prop, command, fmt, limits, outside", LIMITS)
def test_setter_out_of_range(prop, command, fmt, limits, outside, bound, target):
    with expected_protocol(Agilent33622A, []) as inst, pytest.raises(ValueError):
        setattr(get_target(inst, target), prop, outside[bound])


@pytest.mark.parametrize("target", TARGETS)
def test_arb_srate_getter(target):
    with expected_protocol(
        Agilent33622A,
        [(f"{TARGETS[target]}FUNC:ARB:SRAT?", "+1.000000000000000E+09")],
    ) as inst:
        assert get_target(inst, target).arb_srate == 1e9
