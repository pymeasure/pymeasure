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
from pymeasure.instruments.keysight.keysightE3631A import KeysightE3631A


def test_voltage_setpoint():
    """Verify the voltage setpoint setter and getter."""
    with expected_protocol(
        KeysightE3631A,
        [("INST:NSEL 1;:VOLT 1.5", None),
         ("INST:NSEL 1;:VOLT?", "1.5")],
    ) as inst:
        inst.ch_1.voltage_setpoint = 1.5
        assert inst.ch_1.voltage_setpoint == 1.5


def test_current_limit():
    """Verify the current limit setter and getter."""
    with expected_protocol(
        KeysightE3631A,
        [("INST:NSEL 3;:CURR 0.5", None),
         ("INST:NSEL 3;:CURR?", "0.5")],
    ) as inst:
        inst.ch_3.current_limit = 0.5
        assert inst.ch_3.current_limit == 0.5


def test_current_limit_validator():
    """Verify the current limit validator."""
    with expected_protocol(
        KeysightE3631A,
        [],
    ) as inst:
        with pytest.raises(ValueError, match="not in range"):
            inst.ch_1.current_limit = 7


def test_output_enabled():
    """Verify the output enable setter and getter."""
    with expected_protocol(
        KeysightE3631A,
        [("OUTPut 1", None),
         ("OUTPut?", "0")],
    ) as inst:
        inst.output_enabled = True
        assert inst.output_enabled is False


def test_tracking_enabled():
    """Verify the tracking mode setter and getter."""
    with expected_protocol(
        KeysightE3631A,
        [(":OUTP:TRAC 1", None),
         (":OUTP:TRAC?", "0")],
    ) as inst:
        inst.tracking_enabled = True
        assert inst.tracking_enabled is False


@pytest.mark.parametrize("channel", [1, 2, 3])
def test_channel_output_enabled(channel):
    """Verify the per-channel output enable setter and getter."""
    with expected_protocol(
        KeysightE3631A,
        [(f"OUTPut 1, (@{channel})", None),
         (f"INST:NSEL {channel};:OUTPut?", "0")],
    ) as inst:
        getattr(inst, f"ch_{channel}").output_enabled = True
        assert getattr(inst, f"ch_{channel}").output_enabled is False


@pytest.mark.parametrize("channel", [1, 2, 3])
def test_channel_voltage_measurement(channel):
    """Verify the per-channel voltage measurement."""
    with expected_protocol(
        KeysightE3631A,
        [(f"INST:NSEL {channel};:MEAS:VOLT?", "1.23")],
    ) as inst:
        assert getattr(inst, f"ch_{channel}").voltage == 1.23


@pytest.mark.parametrize("channel", [1, 2, 3])
def test_channel_current_measurement(channel):
    """Verify the per-channel current measurement."""
    with expected_protocol(
        KeysightE3631A,
        [(f"INST:NSEL {channel};:MEAS:CURR?", "0.456")],
    ) as inst:
        assert getattr(inst, f"ch_{channel}").current == 0.456


def test_ch_2_voltage_setpoint():
    """Verify the ch_2 voltage setpoint setter and getter (default range)."""
    with expected_protocol(
        KeysightE3631A,
        [("INST:NSEL 2;:VOLT 5", None),
         ("INST:NSEL 2;:VOLT?", "5")],
    ) as inst:
        inst.ch_2.voltage_setpoint = 5
        assert inst.ch_2.voltage_setpoint == 5


def test_ch_2_current_limit():
    """Verify the ch_2 current limit setter and getter (default range)."""
    with expected_protocol(
        KeysightE3631A,
        [("INST:NSEL 2;:CURR 0.5", None),
         ("INST:NSEL 2;:CURR?", "0.5")],
    ) as inst:
        inst.ch_2.current_limit = 0.5
        assert inst.ch_2.current_limit == 0.5


def test_ch_1_voltage_validator_range():
    """Verify the ch_1 voltage setpoint range is [0, 6]."""
    with expected_protocol(
        KeysightE3631A,
        [("INST:NSEL 1;:VOLT 6", None)],
    ) as inst:
        # upper bound of ch_1 is 6, not the default 25
        with pytest.raises(ValueError, match="not in range"):
            inst.ch_1.voltage_setpoint = 7
        # 6 is the valid maximum
        inst.ch_1.voltage_setpoint = 6


def test_ch_1_current_validator_range():
    """Verify the ch_1 current limit range is [0, 5]."""
    with expected_protocol(
        KeysightE3631A,
        [("INST:NSEL 1;:CURR 5", None)],
    ) as inst:
        # upper bound of ch_1 is 5, not the default 1
        with pytest.raises(ValueError, match="not in range"):
            inst.ch_1.current_limit = 6
        # 5 is the valid maximum
        inst.ch_1.current_limit = 5


def test_ch_3_voltage_negative_range():
    """Verify the ch_3 voltage setpoint supports the negative range [0, -25]."""
    with expected_protocol(
        KeysightE3631A,
        [("INST:NSEL 3;:VOLT -25", None),
         ("INST:NSEL 3;:VOLT 0", None)],
    ) as inst:
        # negative values are valid on ch_3 (range is [0, -25] i.e. [-25, 0])
        inst.ch_3.voltage_setpoint = -25
        inst.ch_3.voltage_setpoint = 0


def test_ch_3_voltage_validator_rejects_positive():
    """Verify positive out-of-range voltages are rejected on ch_3."""
    with expected_protocol(
        KeysightE3631A,
        [],
    ) as inst:
        with pytest.raises(ValueError, match="not in range"):
            inst.ch_3.voltage_setpoint = 1
