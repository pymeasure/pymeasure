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

from pymeasure.instruments.keysight.keysightEDU36311A import KeysightEDU36311A, OperatingMode
from pymeasure.test import expected_protocol


def test_init():
    with expected_protocol(KeysightEDU36311A, []):
        pass


def test_id():
    with expected_protocol(
        KeysightEDU36311A,
        [("*IDN?", "Keysight Technologies,EDU36311A,CN00000001,K-01.08.03-01.00-01.08-02.00")],
    ) as inst:
        assert inst.id == (
            "Keysight Technologies,EDU36311A,CN00000001,K-01.08.03-01.00-01.08-02.00"
        )


def test_options_not_implemented():
    with expected_protocol(KeysightEDU36311A, []) as inst, pytest.raises(NotImplementedError):
        _ = inst.options


@pytest.mark.parametrize("ch, value", [(1, 6.18), (2, 30.9), (3, 0)])
def test_voltage_setpoint(ch, value):
    with expected_protocol(
        KeysightEDU36311A,
        [(f"VOLT {value:g}, (@{ch})", None), (f"VOLT? (@{ch})", f"{value:+.8E}")],
    ) as inst:
        inst.channels[ch].voltage_setpoint = value
        assert inst.channels[ch].voltage_setpoint == value


@pytest.mark.parametrize("ch, value", [(1, 6.2), (2, 31), (3, -0.1)])
def test_voltage_setpoint_out_of_range(ch, value):
    with expected_protocol(KeysightEDU36311A, []) as inst, pytest.raises(ValueError):
        inst.channels[ch].voltage_setpoint = value


@pytest.mark.parametrize("ch, value", [(1, 5.15), (1, 0.002), (2, 1.03), (3, 0.001)])
def test_current_limit(ch, value):
    with expected_protocol(
        KeysightEDU36311A,
        [(f"CURR {value:g}, (@{ch})", None), (f"CURR? (@{ch})", f"{value:+.8E}")],
    ) as inst:
        inst.channels[ch].current_limit = value
        assert inst.channels[ch].current_limit == value


@pytest.mark.parametrize("ch, value", [(1, 5.2), (1, 0.001), (2, 1.04), (3, 0)])
def test_current_limit_out_of_range(ch, value):
    with expected_protocol(KeysightEDU36311A, []) as inst, pytest.raises(ValueError):
        inst.channels[ch].current_limit = value


def test_voltage():
    with expected_protocol(
        KeysightEDU36311A,
        [("MEAS:VOLT? (@2)", "+4.54750100E-04")],
    ) as inst:
        assert inst.ch_2.voltage == pytest.approx(4.547501e-4)


def test_current():
    with expected_protocol(
        KeysightEDU36311A,
        [("MEAS:CURR? (@1)", "+2.37718200E-04")],
    ) as inst:
        assert inst.ch_1.current == pytest.approx(2.377182e-4)


def test_output_enabled():
    with expected_protocol(
        KeysightEDU36311A,
        [("OUTP 1, (@3)", None), ("OUTP? (@3)", "0")],
    ) as inst:
        inst.ch_3.output_enabled = True
        assert inst.ch_3.output_enabled is False


@pytest.mark.parametrize(
    "reply, mode",
    [
        ("+0", OperatingMode.OFF),
        ("+1", OperatingMode.CONSTANT_CURRENT),
        ("+2", OperatingMode.CONSTANT_VOLTAGE),
        ("+3", OperatingMode.HARDWARE_FAILURE),
    ],
)
def test_operating_mode(reply, mode):
    with expected_protocol(
        KeysightEDU36311A,
        [("STAT:QUES:INST:ISUM2:COND?", reply)],
    ) as inst:
        assert inst.ch_2.operating_mode == mode


def test_output_on_delay():
    with expected_protocol(
        KeysightEDU36311A,
        [("OUTP:DEL:RISE 0.5, (@1)", None), ("OUTP:DEL:RISE? (@1)", "+5.00000000E-01")],
    ) as inst:
        inst.ch_1.output_on_delay = 0.5
        assert inst.ch_1.output_on_delay == 0.5


def test_output_off_delay():
    with expected_protocol(
        KeysightEDU36311A,
        [("OUTP:DEL:FALL 3600, (@2)", None), ("OUTP:DEL:FALL? (@2)", "+3.60000000E+03")],
    ) as inst:
        inst.ch_2.output_off_delay = 3600
        assert inst.ch_2.output_off_delay == 3600


@pytest.mark.parametrize(
    "prop, command",
    [
        ("output_on_delay", "OUTP:DEL:RISE"),
        ("output_off_delay", "OUTP:DEL:FALL"),
        ("over_current_protection_delay", "CURR:PROT:DEL"),
        ("trigger_delay", "TRIG:DEL"),
    ],
)
def test_delay_millisecond_resolution(prop, command):
    with expected_protocol(KeysightEDU36311A, [(f"{command} 3599.999, (@1)", None)]) as inst:
        setattr(inst.ch_1, prop, 3599.999)


@pytest.mark.parametrize("value", [-0.001, 3601])
def test_output_delay_out_of_range(value):
    with expected_protocol(KeysightEDU36311A, []) as inst, pytest.raises(ValueError):
        inst.ch_1.output_on_delay = value


@pytest.mark.parametrize("ch, value", [(1, 0.5), (1, 6.6), (2, 1.5), (3, 33)])
def test_over_voltage_protection_level(ch, value):
    with expected_protocol(
        KeysightEDU36311A,
        [(f"VOLT:PROT {value:g}, (@{ch})", None), (f"VOLT:PROT? (@{ch})", f"{value:+.8E}")],
    ) as inst:
        inst.channels[ch].over_voltage_protection_level = value
        assert inst.channels[ch].over_voltage_protection_level == value


@pytest.mark.parametrize("ch, value", [(1, 0.4), (1, 6.7), (2, 1.4), (3, 33.1)])
def test_over_voltage_protection_level_out_of_range(ch, value):
    with expected_protocol(KeysightEDU36311A, []) as inst, pytest.raises(ValueError):
        inst.channels[ch].over_voltage_protection_level = value


@pytest.mark.parametrize("reply, tripped", [("0", False), ("1", True)])
def test_over_voltage_protection_tripped(reply, tripped):
    with expected_protocol(
        KeysightEDU36311A,
        [("VOLT:PROT:TRIP? (@1)", reply)],
    ) as inst:
        assert inst.ch_1.over_voltage_protection_tripped is tripped


def test_over_current_protection_enabled():
    with expected_protocol(
        KeysightEDU36311A,
        [("CURR:PROT:STAT 1, (@1)", None), ("CURR:PROT:STAT? (@1)", "1")],
    ) as inst:
        inst.ch_1.over_current_protection_enabled = True
        assert inst.ch_1.over_current_protection_enabled is True


def test_over_current_protection_delay():
    with expected_protocol(
        KeysightEDU36311A,
        [("CURR:PROT:DEL 0.2, (@1)", None), ("CURR:PROT:DEL? (@1)", "+2.00000000E-01")],
    ) as inst:
        inst.ch_1.over_current_protection_delay = 0.2
        assert inst.ch_1.over_current_protection_delay == 0.2


@pytest.mark.parametrize("value", ["SCH", "CCTR"])
def test_over_current_protection_delay_start(value):
    with expected_protocol(
        KeysightEDU36311A,
        [(f"CURR:PROT:DEL:STAR {value}, (@3)", None), ("CURR:PROT:DEL:STAR? (@3)", value)],
    ) as inst:
        inst.ch_3.over_current_protection_delay_start = value
        assert inst.ch_3.over_current_protection_delay_start == value


@pytest.mark.parametrize("reply, tripped", [("0", False), ("1", True)])
def test_over_current_protection_tripped(reply, tripped):
    with expected_protocol(
        KeysightEDU36311A,
        [("CURR:PROT:TRIP? (@2)", reply)],
    ) as inst:
        assert inst.ch_2.over_current_protection_tripped is tripped


def test_clear_protection():
    with expected_protocol(
        KeysightEDU36311A,
        [("OUTP:PROT:CLE (@1)", None), ("VOLT:PROT:CLE (@2)", None), ("CURR:PROT:CLE (@3)", None)],
    ) as inst:
        inst.ch_1.clear_protection()
        inst.ch_2.clear_over_voltage_protection()
        inst.ch_3.clear_over_current_protection()


def test_triggered_voltage():
    with expected_protocol(
        KeysightEDU36311A,
        [("VOLT:TRIG 2, (@1)", None), ("VOLT:TRIG? (@1)", "+2.00000000E+00")],
    ) as inst:
        inst.ch_1.triggered_voltage = 2
        assert inst.ch_1.triggered_voltage == 2


def test_triggered_voltage_out_of_range():
    with expected_protocol(KeysightEDU36311A, []) as inst, pytest.raises(ValueError):
        inst.ch_1.triggered_voltage = 7


def test_triggered_current():
    with expected_protocol(
        KeysightEDU36311A,
        [("CURR:TRIG 1, (@1)", None), ("CURR:TRIG? (@1)", "+1.00000000E+00")],
    ) as inst:
        inst.ch_1.triggered_current = 1
        assert inst.ch_1.triggered_current == 1


@pytest.mark.parametrize("ch, value", [(1, 0.001), (1, 5.2), (2, 2)])
def test_triggered_current_out_of_range(ch, value):
    with expected_protocol(KeysightEDU36311A, []) as inst, pytest.raises(ValueError):
        inst.channels[ch].triggered_current = value


def test_voltage_mode():
    with expected_protocol(
        KeysightEDU36311A,
        [("VOLT:MODE STEP, (@2)", None), ("VOLT:MODE? (@2)", "STEP")],
    ) as inst:
        inst.ch_2.voltage_mode = "STEP"
        assert inst.ch_2.voltage_mode == "STEP"


def test_current_mode():
    with expected_protocol(
        KeysightEDU36311A,
        [("CURR:MODE FIX, (@3)", None), ("CURR:MODE? (@3)", "FIX")],
    ) as inst:
        inst.ch_3.current_mode = "FIX"
        assert inst.ch_3.current_mode == "FIX"


def test_trigger_source():
    with expected_protocol(
        KeysightEDU36311A,
        [("TRIG:SOUR IMM, (@1)", None), ("TRIG:SOUR? (@1)", "IMM")],
    ) as inst:
        inst.ch_1.trigger_source = "IMM"
        assert inst.ch_1.trigger_source == "IMM"


@pytest.mark.parametrize(
    "prop, value",
    [
        ("trigger_source", "EXT"),
        ("voltage_mode", "LIST"),
        ("current_mode", "LIST"),
        ("over_current_protection_delay_start", "NONE"),
    ],
)
def test_channel_discrete_setting_invalid(prop, value):
    with expected_protocol(KeysightEDU36311A, []) as inst, pytest.raises(ValueError):
        setattr(inst.ch_1, prop, value)


def test_display_view_invalid():
    with expected_protocol(KeysightEDU36311A, []) as inst, pytest.raises(ValueError):
        inst.display_view = "METER2"


def test_trigger_delay():
    with expected_protocol(
        KeysightEDU36311A,
        [("TRIG:DEL 0.1, (@1)", None), ("TRIG:DEL? (@1)", "+1.00000000E-01")],
    ) as inst:
        inst.ch_1.trigger_delay = 0.1
        assert inst.ch_1.trigger_delay == 0.1


def test_trigger_continuous_enabled():
    with expected_protocol(
        KeysightEDU36311A,
        [("INIT:CONT 0, (@2)", None), ("INIT:CONT? (@2)", "0")],
    ) as inst:
        inst.ch_2.trigger_continuous_enabled = False
        assert inst.ch_2.trigger_continuous_enabled is False


def test_initiate_trigger_abort():
    with expected_protocol(
        KeysightEDU36311A,
        [("INIT (@1)", None), ("*TRG", None), ("ABOR (@1)", None)],
    ) as inst:
        inst.ch_1.initiate()
        inst.trigger()
        inst.ch_1.abort()


def test_tracking_enabled():
    with expected_protocol(
        KeysightEDU36311A,
        [("OUTP:TRAC 1", None), ("OUTP:TRAC?", "1")],
    ) as inst:
        inst.tracking_enabled = True
        assert inst.tracking_enabled is True


def test_display_enabled():
    with expected_protocol(
        KeysightEDU36311A,
        [("DISP 0", None), ("DISP?", "0")],
    ) as inst:
        inst.display_enabled = False
        assert inst.display_enabled is False


def test_display_view():
    with expected_protocol(
        KeysightEDU36311A,
        [("DISP:VIEW METER1", None), ("DISP:VIEW?", "METER1")],
    ) as inst:
        inst.display_view = "METER1"
        assert inst.display_view == "METER1"


def test_beeper_enabled():
    with expected_protocol(
        KeysightEDU36311A,
        [("SYST:BEEP:STAT 1", None), ("SYST:BEEP:STAT?", "1")],
    ) as inst:
        inst.beeper_enabled = True
        assert inst.beeper_enabled is True


def test_beep():
    with expected_protocol(KeysightEDU36311A, [("SYST:BEEP", None)]) as inst:
        inst.beep()


def test_save_recall_state():
    with expected_protocol(
        KeysightEDU36311A,
        [("*SAV 0", None), ("*RCL 9", None)],
    ) as inst:
        inst.save_state(0)
        inst.recall_state(9)


@pytest.mark.parametrize("method", ["save_state", "recall_state"])
@pytest.mark.parametrize("location", [-1, 10, 1.4])
def test_state_invalid_location(method, location):
    with expected_protocol(KeysightEDU36311A, []) as inst, pytest.raises(ValueError):
        getattr(inst, method)(location)
