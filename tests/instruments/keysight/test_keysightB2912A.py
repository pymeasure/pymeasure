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
from pymeasure.test import expected_protocol
from pymeasure.instruments.keysight.keysightB2912A import KeysightB2912A


# ──────────────────────── source functions ────────────────────────


def test_source_output_enabled():
    with expected_protocol(
        KeysightB2912A,
        [
            (":outp1 1.0", None),
            (":outp1?", "1.0"),
        ],
    ) as inst:
        inst.ch1.source_output_enabled = True
        assert inst.ch1.source_output_enabled is True


def test_source_output_enabled_ch2():
    with expected_protocol(
        KeysightB2912A,
        [
            (":outp2 0.0", None),
            (":outp2?", "0.0"),
        ],
    ) as inst:
        inst.ch2.source_output_enabled = False
        assert inst.ch2.source_output_enabled is False


def test_source_output_mode():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sour1:func:mode CURR", None),
            (":sour1:func:mode?", "CURR"),
        ],
    ) as inst:
        inst.ch1.source_output_mode = "CURR"
        assert inst.ch1.source_output_mode == "CURR"


def test_source_output_mode_invalid():
    with expected_protocol(KeysightB2912A, []) as inst:
        with pytest.raises(ValueError):
            inst.ch1.source_output_mode = "INVALID"


def test_source_output_shape():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sour2:func:shap PULS", None),
            (":sour2:func:shap?", "PULS"),
        ],
    ) as inst:
        inst.ch2.source_output_shape = "PULS"
        assert inst.ch2.source_output_shape == "PULS"


def test_source_current():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sour1:curr 0.001", None),
            (":sour1:curr?", "0.001"),
        ],
    ) as inst:
        inst.ch1.source_current = 1e-3
        assert inst.ch1.source_current == 1e-3


def test_source_current_out_of_range():
    with expected_protocol(KeysightB2912A, []) as inst:
        with pytest.raises(ValueError):
            inst.ch1.source_current = 5


def test_source_current_triggered():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sour1:curr:trig 0.002", None),
            (":sour1:curr:trig?", "0.002"),
        ],
    ) as inst:
        inst.ch1.source_current_triggered = 2e-3
        assert inst.ch1.source_current_triggered == 2e-3


def test_source_voltage():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sour2:volt 1.5", None),
            (":sour2:volt?", "1.5"),
        ],
    ) as inst:
        inst.ch2.source_voltage = 1.5
        assert inst.ch2.source_voltage == 1.5


def test_source_voltage_out_of_range():
    with expected_protocol(KeysightB2912A, []) as inst:
        with pytest.raises(ValueError):
            inst.ch1.source_voltage = 300


def test_source_voltage_triggered():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sour1:volt:trig 1.11", None),
            (":sour1:volt:trig?", "1.11"),
        ],
    ) as inst:
        inst.ch1.source_voltage_triggered = 1.11
        assert inst.ch1.source_voltage_triggered == 1.11


# ───────────────────── output protection ──────────────────────


def test_output_protection_enabled():
    with expected_protocol(
        KeysightB2912A,
        [
            (":outp1:prot 1.0", None),
            (":outp1:prot?", "1.0"),
        ],
    ) as inst:
        inst.ch1.output_protection_enabled = True
        assert inst.ch1.output_protection_enabled is True


def test_compliance_current():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sens1:curr:prot 1e-06", None),
            (":sens1:curr:prot?", "1e-06"),
        ],
    ) as inst:
        inst.ch1.compliance_current = 1e-6
        assert inst.ch1.compliance_current == 1e-6


def test_compliance_voltage():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sens2:volt:prot 4", None),
            (":sens2:volt:prot?", "4"),
        ],
    ) as inst:
        inst.ch2.compliance_voltage = 4
        assert inst.ch2.compliance_voltage == 4


# ───────────────────── pulse configuration ────────────────────


def test_pulse_delay():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sour1:pulse:del 0.001", None),
            (":sour1:pulse:del?", "0.001"),
        ],
    ) as inst:
        inst.ch1.pulse_delay = 1e-3
        assert inst.ch1.pulse_delay == 1e-3


def test_pulse_width():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sour2:pulse:widt 0.5", None),
            (":sour2:pulse:widt?", "0.5"),
        ],
    ) as inst:
        inst.ch2.pulse_width = 0.5
        assert inst.ch2.pulse_width == 0.5


# ──────────────────── measurement functions ───────────────────


def test_current_measurement_range_auto():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sens1:curr:range:auto 0.0", None),
            (":sens1:curr:range:auto?", "0.0"),
        ],
    ) as inst:
        inst.ch1.current_measurement_range_auto = False
        assert inst.ch1.current_measurement_range_auto is False


def test_current_measurement_range():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sens1:curr:range 0.1", None),
            (":sens1:curr:rang?", "0.1"),
        ],
    ) as inst:
        inst.ch1.current_measurement_range = 0.1
        assert inst.ch1.current_measurement_range == 0.1


def test_current_measurement_speed():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sens1:curr:aper 0.0001", None),
            (":sens1:curr:aper?", "0.0001"),
        ],
    ) as inst:
        inst.ch1.current_measurement_speed = 1e-4
        assert inst.ch1.current_measurement_speed == 1e-4


def test_current_measurement_speed_nplc():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sens1:curr:nplc 1", None),
            (":sens1:curr:nplc?", "1"),
        ],
    ) as inst:
        inst.ch1.current_measurement_speed_nplc = 1
        assert inst.ch1.current_measurement_speed_nplc == 1


def test_current_measurement_speed_nplc_out_of_range():
    with expected_protocol(KeysightB2912A, []) as inst:
        with pytest.raises(ValueError):
            inst.ch1.current_measurement_speed_nplc = 200


def test_measured_current():
    with expected_protocol(
        KeysightB2912A,
        [(":meas:curr? (@1)", "1.234e-3")],
    ) as inst:
        assert inst.ch1.measured_current == pytest.approx(1.234e-3)


def test_voltage_measurement_range_auto():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sens2:volt:range:auto 1.0", None),
            (":sens2:volt:range:auto?", "1.0"),
        ],
    ) as inst:
        inst.ch2.voltage_measurement_range_auto = True
        assert inst.ch2.voltage_measurement_range_auto is True


def test_voltage_measurement_range():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sens1:volt:range 0.2", None),
            (":sens1:volt:rang?", "0.2"),
        ],
    ) as inst:
        inst.ch1.voltage_measurement_range = 0.2
        assert inst.ch1.voltage_measurement_range == 0.2


def test_voltage_measurement_speed():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sens2:volt:aper 0.0001", None),
            (":sens2:volt:aper?", "0.0001"),
        ],
    ) as inst:
        inst.ch2.voltage_measurement_speed = 1e-4
        assert inst.ch2.voltage_measurement_speed == 1e-4


def test_voltage_measurement_speed_nplc():
    with expected_protocol(
        KeysightB2912A,
        [
            (":sens1:volt:nplc 10", None),
            (":sens1:volt:nplc?", "10"),
        ],
    ) as inst:
        inst.ch1.voltage_measurement_speed_nplc = 10
        assert inst.ch1.voltage_measurement_speed_nplc == 10


def test_measured_voltage():
    with expected_protocol(
        KeysightB2912A,
        [(":meas:volt? (@2)", "0.456")],
    ) as inst:
        assert inst.ch2.measured_voltage == pytest.approx(0.456)


# below tests captured from hardware B2912A via a
# pymeasure.generator.Generator

def test_measured_current_array():
    block = (
        b"#232\xbd\xce<\x8f\xd6\x06\xeaM\xbd\xd80s\x11\x9f!\xd7"
        b"\xbd\xd9\x03\x8eC\xadH\xd0\xbd\xd9\x03\x8eC\xadH\xd0\n"
    )
    with expected_protocol(
        KeysightB2912A,
        [
            (":form?", "ASC"),
            (":form REAL,64", None),
            (":fetc:arr:curr? (@1)", block),
            (":form ASC", None),
        ],
    ) as inst:
        values = inst.ch1.measured_current_array
        assert values.dtype.kind == "f"
        assert values.dtype.itemsize == 8
        assert values == pytest.approx([-5.5e-11, -8.8e-11, -9.1e-11, -9.1e-11])


def test_measured_voltage_array():
    block = (
        b"#232?\xb9\x99\x9bG\x18\xc3E?\xb9\x99\x99\x99\x99\x99\x99"
        b"?\xb9\x99\x99\x99\x99\x99\x99?\xb9\x99\x97\xec\x1ao\xed\n"
    )
    with expected_protocol(
        KeysightB2912A,
        [
            (":form?", "ASC"),
            (":form REAL,64", None),
            (":fetc:arr:volt? (@2)", block),
            (":form ASC", None),
        ],
    ) as inst:
        values = inst.ch2.measured_voltage_array
        assert values.dtype.kind == "f"
        assert values.dtype.itemsize == 8
        assert values == pytest.approx([0.1000001, 0.1, 0.1, 0.0999999])


# ──────────────── trigger configuration ───────────────────────


def test_trigger_source():
    with expected_protocol(
        KeysightB2912A,
        [(":trig1:sour TIM", None)],
    ) as inst:
        inst.ch1.trigger_source = "TIM"


def test_trigger_source_invalid():
    with expected_protocol(KeysightB2912A, []) as inst:
        with pytest.raises(ValueError):
            inst.ch1.trigger_source = "INVALID"


def test_source_trigger_delay():
    with expected_protocol(
        KeysightB2912A,
        [
            (":trig1:tran:del 0.5", None),
            (":trig1:tran:del?", "0.5"),
        ],
    ) as inst:
        inst.ch1.source_trigger_delay = 0.5
        assert inst.ch1.source_trigger_delay == 0.5


def test_measurement_trigger_delay():
    with expected_protocol(
        KeysightB2912A,
        [
            (":trig2:acq:del 0.1", None),
            (":trig2:acq:del?", "0.1"),
        ],
    ) as inst:
        inst.ch2.measurement_trigger_delay = 0.1
        assert inst.ch2.measurement_trigger_delay == 0.1


def test_source_trigger_timer_period():
    with expected_protocol(
        KeysightB2912A,
        [(":trig1:tran:tim 0.01", None)],
    ) as inst:
        inst.ch1.source_trigger_timer_period = 0.01


def test_source_trigger_timer_period_string():
    with expected_protocol(
        KeysightB2912A,
        [(":trig1:tran:tim MIN", None)],
    ) as inst:
        inst.ch1.source_trigger_timer_period = "MIN"


def test_measurement_trigger_timer_period():
    with expected_protocol(
        KeysightB2912A,
        [(":trig2:acq:tim 1", None)],
    ) as inst:
        inst.ch2.measurement_trigger_timer_period = 1


def test_source_trigger_count():
    with expected_protocol(
        KeysightB2912A,
        [(":trig1:tran:coun 100", None)],
    ) as inst:
        inst.ch1.source_trigger_count = 100


def test_source_trigger_count_infinite():
    with expected_protocol(
        KeysightB2912A,
        [(":trig1:tran:coun 2147483647", None)],
    ) as inst:
        inst.ch1.source_trigger_count = 2147483647


def test_measurement_trigger_count():
    with expected_protocol(
        KeysightB2912A,
        [(":trig2:acq:coun 50", None)],
    ) as inst:
        inst.ch2.measurement_trigger_count = 50


def test_source_trigger_count_out_of_range():
    with expected_protocol(KeysightB2912A, []) as inst:
        with pytest.raises(ValueError):
            inst.ch1.source_trigger_count = 200000


# ───────────────────── channel methods ────────────────────────


def test_initiate():
    with expected_protocol(
        KeysightB2912A,
        [(":INIT (@1)", None)],
    ) as inst:
        inst.ch1.initiate()


def test_abort():
    with expected_protocol(
        KeysightB2912A,
        [(":ABOR:ALL (@2)", None)],
    ) as inst:
        inst.ch2.abort()


# ──────────────────── channel idle property ───────────────────
# ch1: acquire_idle=bit1 (2), transition_idle=bit4 (16) → both set = 18
# ch2: acquire_idle=bit7 (128), transition_idle=bit10 (1024) → both set = 1152


def test_ch1_idle_true():
    with expected_protocol(KeysightB2912A, [("STAT:OPER:COND?", "18")]) as inst:
        assert inst.ch1.idle is True


def test_ch1_idle_false():
    with expected_protocol(KeysightB2912A, [("STAT:OPER:COND?", "0")]) as inst:
        assert inst.ch1.idle is False


def test_ch1_idle_partial():
    # acquire_idle bit set but transition_idle not → False
    with expected_protocol(KeysightB2912A, [("STAT:OPER:COND?", "2")]) as inst:
        assert inst.ch1.idle is False


def test_ch2_idle_true():
    with expected_protocol(KeysightB2912A, [("STAT:OPER:COND?", "1152")]) as inst:
        assert inst.ch2.idle is True


def test_ch2_idle_false():
    with expected_protocol(KeysightB2912A, [("STAT:OPER:COND?", "0")]) as inst:
        assert inst.ch2.idle is False


# ───────────────── instrument-level idle property ─────────────


def test_inst_idle_true():
    # ch1 idle, then ch2 idle → both queried
    with expected_protocol(
        KeysightB2912A,
        [("STAT:OPER:COND?", "18"), ("STAT:OPER:COND?", "1152")],
    ) as inst:
        assert inst.idle is True


def test_inst_idle_false_ch1():
    # ch1 not idle → short-circuit, ch2 never queried
    with expected_protocol(KeysightB2912A, [("STAT:OPER:COND?", "0")]) as inst:
        assert inst.idle is False


def test_inst_idle_false_ch2():
    # ch1 idle, ch2 not → both queried
    with expected_protocol(
        KeysightB2912A,
        [("STAT:OPER:COND?", "18"), ("STAT:OPER:COND?", "0")],
    ) as inst:
        assert inst.idle is False


# ──────────────────── wait_for_idle ───────────────────────────


def test_ch_wait_for_idle_returns():
    # ch1 already idle → returns immediately after one poll
    with expected_protocol(KeysightB2912A, [("STAT:OPER:COND?", "18")]) as inst:
        inst.ch1.wait_for_idle()


def test_ch_wait_for_idle_timeout():
    # ch1 not idle and timeout=0 → raises ValueError after first poll
    with expected_protocol(KeysightB2912A, [("STAT:OPER:COND?", "0")]) as inst:
        with pytest.raises(ValueError):
            inst.ch1.wait_for_idle(timeout=0)


def test_inst_wait_for_idle_returns():
    # both channels idle → returns after two polls
    with expected_protocol(
        KeysightB2912A,
        [("STAT:OPER:COND?", "18"), ("STAT:OPER:COND?", "1152")],
    ) as inst:
        inst.wait_for_idle()


def test_inst_wait_for_idle_timeout():
    # ch1 not idle, timeout=0 → raises ValueError after first poll
    with expected_protocol(KeysightB2912A, [("STAT:OPER:COND?", "0")]) as inst:
        with pytest.raises(ValueError):
            inst.wait_for_idle(timeout=0)
