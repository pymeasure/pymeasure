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
from pymeasure.test import expected_protocol
from pymeasure.instruments.agilent.agilent33500 import Agilent33500


# TODO: Tests with a range in floats, seems to be flaky. Need to
#       figure out the reason for protocol returning 6 after decimal point

@pytest.mark.parametrize(
    "shape", ["SIN", "SQU", "TRI", "RAMP", "PULS", "PRBS", "NOIS", "ARB", "DC"]
)
def test_shape(shape):
    """
    Test Agilent 33500 shape function
    """
    with expected_protocol(
        Agilent33500,
        [
            ("SOUR1:FUNC?", shape),
            ("SOUR2:FUNC?", shape),
            ("FUNC?", shape),
            (f"SOUR1:FUNC {shape}", None),
            (f"SOUR2:FUNC {shape}", None),
            (f"FUNC {shape}", None),
        ],
    ) as inst:
        assert shape == inst.ch[1].shape
        assert shape == inst.ch[2].shape
        assert shape == inst.shape
        inst.ch[1].shape = shape
        inst.ch[2].shape = shape
        inst.shape = shape


@pytest.mark.parametrize("frequency", [1e-6, 1.2e8])
def test_frequency(frequency):
    """
    Test Agilent 33500 frequency function
    """
    with expected_protocol(
        Agilent33500,
        [
            ("SOUR1:FREQ?", frequency),
            ("SOUR2:FREQ?", frequency),
            ("FREQ?", frequency),
            (f"SOUR1:FREQ {'{:.6f}'.format(frequency)}", None),
            (f"SOUR2:FREQ {'{:.6f}'.format(frequency)}", None),
            (f"FREQ {'{:.6f}'.format(frequency)}", None),
        ],
    ) as inst:
        assert frequency == inst.ch[1].frequency
        assert frequency == inst.ch[2].frequency
        assert frequency == inst.frequency
        inst.ch[1].frequency = frequency
        inst.ch[2].frequency = frequency
        inst.frequency = frequency


@pytest.mark.parametrize("amplitude", [10e-3, 10])
def test_amplitude(amplitude):
    """
    Test Agilent 33500 amplitude function
    """
    with expected_protocol(
        Agilent33500,
        [
            ("SOUR1:VOLT?", amplitude),
            ("SOUR2:VOLT?", amplitude),
            ("VOLT?", amplitude),
            (f"SOUR1:VOLT {'{:.6f}'.format(amplitude)}", None),
            (f"SOUR2:VOLT {'{:.6f}'.format(amplitude)}", None),
            (f"VOLT {'{:.6f}'.format(amplitude)}", None),
        ],
    ) as inst:
        assert amplitude == inst.ch[1].amplitude
        assert amplitude == inst.ch[2].amplitude
        assert amplitude == inst.amplitude
        inst.ch[1].amplitude = amplitude
        inst.ch[2].amplitude = amplitude
        inst.amplitude = amplitude


@pytest.mark.parametrize("amplitude_unit", ["VPP", "VRMS", "DBM"])
def test_amplitude_unit(amplitude_unit):
    """
    Test Agilent 33500 amplitude unit function
    """
    with expected_protocol(
        Agilent33500,
        [
            ("SOUR1:VOLT:UNIT?", amplitude_unit),
            ("SOUR2:VOLT:UNIT?", amplitude_unit),
            ("VOLT:UNIT?", amplitude_unit),
            (f"SOUR1:VOLT:UNIT {amplitude_unit}", None),
            (f"SOUR2:VOLT:UNIT {amplitude_unit}", None),
            (f"VOLT:UNIT {amplitude_unit}", None),
        ],
    ) as inst:
        assert amplitude_unit == inst.ch[1].amplitude_unit
        assert amplitude_unit == inst.ch[2].amplitude_unit
        assert amplitude_unit == inst.amplitude_unit
        inst.ch[1].amplitude_unit = amplitude_unit
        inst.ch[2].amplitude_unit = amplitude_unit
        inst.amplitude_unit = amplitude_unit


@pytest.mark.parametrize("state", [0, 1])
def test_output(state):
    """
    Test Agilent 33500 output function
    """
    with expected_protocol(
        Agilent33500,
        [
            ("OUTP1?", state),
            ("OUTP2?", state),
            ("OUTP?", state),
            (f"OUTP1 {state}", None),
            (f"OUTP2 {state}", None),
            (f"OUTP {state}", None),
        ],
    ) as inst:
        assert state == inst.ch[1].output
        assert state == inst.ch[2].output
        assert state == inst.output
        inst.ch[1].output = state
        inst.ch[2].output = state
        inst.output = state


@pytest.mark.parametrize("offset", [-4.995, 4.995])
def test_offset(offset):
    """
    Test Agilent 33500 offset function
    """
    with expected_protocol(
        Agilent33500,
        [
            ("SOUR1:VOLT:OFFS?", offset),
            ("SOUR2:VOLT:OFFS?", offset),
            ("VOLT:OFFS?", offset),
            (f"SOUR1:VOLT:OFFS {'{:.6f}'.format(offset)}", None),
            (f"SOUR2:VOLT:OFFS {'{:.6f}'.format(offset)}", None),
            (f"VOLT:OFFS {'{:.6f}'.format(offset)}", None),
        ],
    ) as inst:
        assert offset == inst.ch[1].offset
        assert offset == inst.ch[2].offset
        assert offset == inst.offset
        inst.ch[1].offset = offset
        inst.ch[2].offset = offset
        inst.offset = offset


@pytest.mark.parametrize("voltage_high", [-4.995, 4.995])
def test_voltage_high(voltage_high):
    """
    Test Agilent 33500 voltage_high function
    """
    with expected_protocol(
        Agilent33500,
        [
            ("SOUR1:VOLT:HIGH?", voltage_high),
            ("SOUR2:VOLT:HIGH?", voltage_high),
            ("VOLT:HIGH?", voltage_high),
            (f"SOUR1:VOLT:HIGH {'{:.6f}'.format(voltage_high)}", None),
            (f"SOUR2:VOLT:HIGH {'{:.6f}'.format(voltage_high)}", None),
            (f"VOLT:HIGH {'{:.6f}'.format(voltage_high)}", None),
        ],
    ) as inst:
        assert voltage_high == inst.ch[1].voltage_high
        assert voltage_high == inst.ch[2].voltage_high
        assert voltage_high == inst.voltage_high
        inst.ch[1].voltage_high = voltage_high
        inst.ch[2].voltage_high = voltage_high
        inst.voltage_high = voltage_high


@pytest.mark.parametrize("voltage_low", [-4.995, 4.995])
def test_voltage_low(voltage_low):
    """
    Test Agilent 33500 voltage_low function
    """
    with expected_protocol(
        Agilent33500,
        [
            ("SOUR1:VOLT:LOW?", voltage_low),
            ("SOUR2:VOLT:LOW?", voltage_low),
            ("VOLT:LOW?", voltage_low),
            (f"SOUR1:VOLT:LOW {'{:.6f}'.format(voltage_low)}", None),
            (f"SOUR2:VOLT:LOW {'{:.6f}'.format(voltage_low)}", None),
            (f"VOLT:LOW {'{:.6f}'.format(voltage_low)}", None),
        ],
    ) as inst:
        assert voltage_low == inst.ch[1].voltage_low
        assert voltage_low == inst.ch[2].voltage_low
        assert voltage_low == inst.voltage_low
        inst.ch[1].voltage_low = voltage_low
        inst.ch[2].voltage_low = voltage_low
        inst.voltage_low = voltage_low


@pytest.mark.parametrize("phase", [-360, 360])
def test_phase(phase):
    """
    Test Agilent 33500 phase function
    """
    with expected_protocol(
        Agilent33500,
        [
            ("SOUR1:PHAS?", phase),
            ("SOUR2:PHAS?", phase),
            ("PHAS?", phase),
            (f"SOUR1:PHAS {'{:.6f}'.format(phase)}", None),
            (f"SOUR2:PHAS {'{:.6f}'.format(phase)}", None),
            (f"PHAS {'{:.6f}'.format(phase)}", None),
        ],
    ) as inst:
        assert phase == inst.ch[1].phase
        assert phase == inst.ch[2].phase
        assert phase == inst.phase
        inst.ch[1].phase = phase
        inst.ch[2].phase = phase
        inst.phase = phase


@pytest.mark.parametrize("square_dutycycle", [0.01, 99.98])
def test_square_dutycycle(square_dutycycle):
    """
    Test Agilent 33500 square_dutycycle function
    """
    with expected_protocol(
        Agilent33500,
        [
            ("SOUR1:FUNC:SQU:DCYC?", square_dutycycle),
            ("SOUR2:FUNC:SQU:DCYC?", square_dutycycle),
            ("FUNC:SQU:DCYC?", square_dutycycle),
            (f"SOUR1:FUNC:SQU:DCYC {'{:.6f}'.format(square_dutycycle)}", None),
            (f"SOUR2:FUNC:SQU:DCYC {'{:.6f}'.format(square_dutycycle)}", None),
            (f"FUNC:SQU:DCYC {'{:.6f}'.format(square_dutycycle)}", None),
        ],
    ) as inst:
        assert square_dutycycle == inst.ch[1].square_dutycycle
        assert square_dutycycle == inst.ch[2].square_dutycycle
        assert square_dutycycle == inst.square_dutycycle
        inst.ch[1].square_dutycycle = square_dutycycle
        inst.ch[2].square_dutycycle = square_dutycycle
        inst.square_dutycycle = square_dutycycle


@pytest.mark.parametrize("ramp_symmetry", [0.01, 99.98])
def test_ramp_symmetry(ramp_symmetry):
    """
    Test Agilent 33500 ramp_symmetry function
    """
    with expected_protocol(
        Agilent33500,
        [
            ("SOUR1:FUNC:RAMP:SYMM?", ramp_symmetry),
            ("SOUR2:FUNC:RAMP:SYMM?", ramp_symmetry),
            ("FUNC:RAMP:SYMM?", ramp_symmetry),
            (f"SOUR1:FUNC:RAMP:SYMM {'{:.6f}'.format(ramp_symmetry)}", None),
            (f"SOUR2:FUNC:RAMP:SYMM {'{:.6f}'.format(ramp_symmetry)}", None),
            (f"FUNC:RAMP:SYMM {'{:.6f}'.format(ramp_symmetry)}", None),
        ],
    ) as inst:
        assert ramp_symmetry == inst.ch[1].ramp_symmetry
        assert ramp_symmetry == inst.ch[2].ramp_symmetry
        assert ramp_symmetry == inst.ramp_symmetry
        inst.ch[1].ramp_symmetry = ramp_symmetry
        inst.ch[2].ramp_symmetry = ramp_symmetry
        inst.ramp_symmetry = ramp_symmetry
