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
from pymeasure.test import expected_protocol

from pymeasure.instruments.chroma.chroma_63600 import Chroma63600


def test_init():
    with expected_protocol(
            Chroma63600,
            [],
    ):
        pass  # Verify the expected communication.


def test_ch_1_active_setter():
    with expected_protocol(
            Chroma63600,
            [(b'CHAN 1;CHANNEL:ACTIVE ON', None)],
    ) as inst:
        inst.ch_1.active = True


def test_ch_1_active_getter():
    with expected_protocol(
            Chroma63600,
            [(b'CHAN 1;CHANNEL:ACTIVE?', b'ON')],
    ) as inst:
        assert inst.ch_1.active is True


def test_ch_1_enabled_setter():
    with expected_protocol(
            Chroma63600,
            [(b'CHAN 1;LOAD ON', None)],
    ) as inst:
        inst.ch_1.enabled = True


def test_ch_1_enabled_getter():
    with expected_protocol(
            Chroma63600,
            [(b'CHAN 1;LOAD?', b'ON')],
    ) as inst:
        assert inst.ch_1.enabled is True


def test_ch_1_mode_getter():
    with expected_protocol(
            Chroma63600,
            [(b'CHAN 1;:MODE?', b'CRH')],
    ) as inst:
        assert inst.ch_1.mode == ("CR","H")


def test_ch_1_status_getter():
    with expected_protocol(
            Chroma63600,
            [(b'CHAN 1;LOAD:PROTECTION?', b'0')],
    ) as inst:
        assert inst.ch_1.status == 0


def test_ch_3_current_getter():
    with expected_protocol(
            Chroma63600,
            [(b'CHAN 3;FETCH:CURRENT?', b'0.0038438')],
    ) as inst:
        assert inst.ch_3.current == 0.0038438


def test_ch_3_frequency_getter():
    with expected_protocol(
            Chroma63600,
            [(b'CHAN 3;FETCH:FREQUENCY?', b'-0000000000')],
    ) as inst:
        assert inst.ch_3.frequency == -0.0


def test_ch_3_identify_getter():
    with expected_protocol(
            Chroma63600,
            [(b'CHAN 3;CHAN:ID?', b'CHROMA,63630-80-60,636308007635,1.92,1.92')],
    ) as inst:
        assert inst.ch_3.identify == ['CHROMA', '63630-80-60', 636308007635.0, 1.92, 1.92]


def test_ch_3_mode_setter():
    with expected_protocol(
            Chroma63600,
            [(b'CHAN 3;:MODE CRH', None)],
    ) as inst:
        inst.ch_3.mode = 'CRH'


def test_ch_3_power_getter():
    with expected_protocol(
            Chroma63600,
            [(b'CHAN 3;FETCH:POWER?', b'0.0000054')],
    ) as inst:
        assert inst.ch_3.power == 5.4e-06


def test_ch_3_resistance_setpoint_1_setter():
    with expected_protocol(
            Chroma63600,
            [(b'CHAN 3;RESISTANCE:STATIC:L1 10', None)],
    ) as inst:
        inst.ch_3.resistance_setpoint_1 = 10


def test_ch_3_resistance_setpoint_1_getter():
    with expected_protocol(
            Chroma63600,
            [(b'CHAN 3;RESISTANCE:STATIC:L1?', b'24.00')],
    ) as inst:
        assert inst.ch_3.resistance_setpoint_1 == 24.0


def test_ch_3_voltage_getter():
    with expected_protocol(
            Chroma63600,
            [(b'CHAN 3;FETCH:VOLTAGE?', b'0.0009822')],
    ) as inst:
        assert inst.ch_3.voltage == 0.0009822


def test_ch_5_mode_getter():
    with expected_protocol(
            Chroma63600,
            [(b'CHAN 5;:MODE?', b'CRH')],
    ) as inst:
        assert inst.ch_5.mode == ("CR","H")


def test_ch_5_status_getter():
    with expected_protocol(
            Chroma63600,
            [(b'CHAN 5;LOAD:PROTECTION?', b'0')],
    ) as inst:
        assert inst.ch_5.status == 0


def test_currents_getter():
    with expected_protocol(
            Chroma63600,
            [(b'MEAS:ALLC?',
              b'0.0053471,0,0.0039698,0,0.0036226,0,0.5005162,0,0.0004139,0.0004023')],
    ) as inst:
        assert inst.currents == [0.0053471, 0.0, 0.0039698, 0.0, 0.0036226, 0.0, 0.5005162,
                                 0.0, 0.0004139, 0.0004023]


def test_powers_getter():
    with expected_protocol(
            Chroma63600,
            [(b'MEAS:ALLP?',
              b'0.0000085,0,0.0000034,0,0.0000046,0,0.4900631,0,0.0000001,0.0000002')],
    ) as inst:
        assert inst.powers == [8.5e-06, 0.0, 3.4e-06, 0.0, 4.6e-06, 0.0, 0.4900631, 0.0,
                               1e-07, 2e-07]


def test_voltages_getter():
    with expected_protocol(
            Chroma63600,
            [(b'MEAS:ALLV?',
              b'0.0017520,0,0.0014331,0,0.0021199,0,0.9797283,0,0.0004860,0.0011949')],
    ) as inst:
        assert inst.voltages == [0.001752, 0.0, 0.0014331, 0.0, 0.0021199, 0.0,
                                 0.9797283, 0.0, 0.000486, 0.0011949]

