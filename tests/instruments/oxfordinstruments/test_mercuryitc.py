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
from pymeasure.instruments.oxfordinstruments import MercuryiTC


def test_init():
    with expected_protocol(
            MercuryiTC,
            [],
    ):
        pass  # Verify the expected communication.


def test_HTR_MB_current_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'READ:DEV:MB0.H1:HTR:SIG:CURR', b'STAT:DEV:MB0.H1:HTR:SIG:CURR:-0.0000A')],
    ) as inst:
        assert inst.HTR_MB.current == -0.0


def test_HTR_MB_max_power_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'READ:DEV:MB0.H1:HTR:PMAX', b'STAT:DEV:MB0.H1:HTR:PMAX:12.5000')],
    ) as inst:
        assert inst.HTR_MB.max_power == 12.5


def test_HTR_MB_power_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'READ:DEV:MB0.H1:HTR:SIG:POWR', b'STAT:DEV:MB0.H1:HTR:SIG:POWR:0.0000W')],
    ) as inst:
        assert inst.HTR_MB.power == 0.0


def test_HTR_MB_resistance_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'READ:DEV:MB0.H1:HTR:RES', b'STAT:DEV:MB0.H1:HTR:RES:50')],
    ) as inst:
        assert inst.HTR_MB.resistance == 50.0


def test_HTR_MB_voltage_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'READ:DEV:MB0.H1:HTR:SIG:VOLT', b'STAT:DEV:MB0.H1:HTR:SIG:VOLT:-0.0481V')],
    ) as inst:
        assert inst.HTR_MB.voltage == -0.0481


def test_HTR_MB_voltage_limit_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'READ:DEV:MB0.H1:HTR:VLIM', b'STAT:DEV:MB0.H1:HTR:VLIM:25')],
    ) as inst:
        assert inst.HTR_MB.voltage_limit == 25.0


def test_TS_MB_control_loop_D_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'READ:DEV:MB1.T1:TEMP:LOOP:D', b'STAT:DEV:MB1.T1:TEMP:LOOP:D:0.0')],
    ) as inst:
        assert inst.TS_MB.control_loop_D == 0.0


def test_TS_MB_control_loop_I_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'READ:DEV:MB1.T1:TEMP:LOOP:I', b'STAT:DEV:MB1.T1:TEMP:LOOP:I:1.8')],
    ) as inst:
        assert inst.TS_MB.control_loop_I == 1.8


def test_TS_MB_control_loop_P_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'READ:DEV:MB1.T1:TEMP:LOOP:P', b'STAT:DEV:MB1.T1:TEMP:LOOP:P:3.5')],
    ) as inst:
        assert inst.TS_MB.control_loop_P == 3.5


def test_TS_MB_control_loop_PID_enabled_setter():
    with expected_protocol(
            MercuryiTC,
            [(b'SET:DEV:MB1.T1:TEMP:LOOP:ENAB:OFF',
              b'STAT:SET:DEV:MB1.T1:TEMP:LOOP:ENAB:OFF:VALID')],
    ) as inst:
        inst.TS_MB.control_loop_PID_enabled = False


def test_TS_MB_control_loop_PID_enabled_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'READ:DEV:MB1.T1:TEMP:LOOP:ENAB', b'STAT:DEV:MB1.T1:TEMP:LOOP:ENAB:OFF')],
    ) as inst:
        assert inst.TS_MB.control_loop_PID_enabled is False


def test_TS_MB_control_loop_temperature_setpoint_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'READ:DEV:MB1.T1:TEMP:LOOP:TSET', b'STAT:DEV:MB1.T1:TEMP:LOOP:TSET:61.0000K')],
    ) as inst:
        assert inst.TS_MB.control_loop_temperature_setpoint == 61.0


def test_TS_MB_control_loop_heater_percent_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'READ:DEV:MB1.T1:TEMP:LOOP:HSET', b'STAT:DEV:MB1.T1:TEMP:LOOP:HSET:0')],
    ) as inst:
        assert inst.TS_MB.control_loop_heater_percent == 0.0


def test_TS_MB_control_loop_ramp_enabled_setter():
    with expected_protocol(
            MercuryiTC,
            [(b'SET:DEV:MB1.T1:TEMP:LOOP:RENA:OFF',
              b'STAT:SET:DEV:MB1.T1:TEMP:LOOP:RENA:OFF:VALID')],
    ) as inst:
        inst.TS_MB.control_loop_ramp_enabled = False


def test_TS_MB_control_loop_ramp_enabled_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'READ:DEV:MB1.T1:TEMP:LOOP:RENA', b'STAT:DEV:MB1.T1:TEMP:LOOP:RENA:OFF')],
    ) as inst:
        assert inst.TS_MB.control_loop_ramp_enabled is False


def test_TS_MB_control_loop_ramp_rate_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'READ:DEV:MB1.T1:TEMP:LOOP:RSET', b'STAT:DEV:MB1.T1:TEMP:LOOP:RSET:5.0000K/m')],
    ) as inst:
        assert inst.TS_MB.control_loop_ramp_rate == 5.0


def test_TS_MB_temperature_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'READ:DEV:MB1.T1:TEMP:SIG:TEMP', b'STAT:DEV:MB1.T1:TEMP:SIG:TEMP:330.0725K')],
    ) as inst:
        assert inst.TS_MB.temperature == 330.0725


def test_TS_MB_voltage_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'READ:DEV:MB1.T1:TEMP:SIG:VOLT', b'STAT:DEV:MB1.T1:TEMP:SIG:VOLT:174.3112mV')],
    ) as inst:
        assert inst.TS_MB.voltage == 0.17431120000000003


def test_identity_getter():
    with expected_protocol(
            MercuryiTC,
            [(b'*IDN?', b'IDN:OXFORD INSTRUMENTS:MERCURY ITC:232150255:2.6.04.000')],
    ) as inst:
        assert inst.identity == 'IDN:OXFORD INSTRUMENTS:MERCURY ITC:232150255:2.6.04.000'
