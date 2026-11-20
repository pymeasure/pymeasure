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

from pymeasure.instruments.lakeshore import lakeshore625
from pymeasure.instruments.lakeshore.lakeshore625 import (
    LakeShore625,
    MagnetFaultError,
    decode_errors,
    heater_interlocked_range,
)
from pymeasure.test import expected_protocol

HEATER_OFF = (b"PSH?", b"0")
HEATER_ON = (b"PSH?", b"1")
HEATER_WARMING = (b"PSH?", b"2")
HEATER_COOLING = (b"PSH?", b"3")
NO_ERRORS = (b"ERST?", b"000,000,000")
HEATER_PARAMETERS = (b"PSHS?", b"1,+050,+010")


class FakeClock:
    """Replace the driver's clock; every ``sleep`` advances time instantly and is recorded."""

    def __init__(self):
        self.t = 0.0
        self.sleeps = []

    def perf_counter(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


def test_options_not_supported():
    """The Model 625 has no *OPT? command, so nothing may be sent."""
    with expected_protocol(LakeShore625, []) as inst, pytest.raises(NotImplementedError):
        inst.options  # noqa: B018


@pytest.fixture
def clock(monkeypatch):
    c = FakeClock()
    monkeypatch.setattr(lakeshore625.time, "perf_counter", c.perf_counter)
    monkeypatch.setattr(lakeshore625.time, "sleep", c.sleep)
    return c


def ramp_start(field=b"0", setf=b"SETF 1"):
    """Pairs before a ramp: error pre-check, heater state, start field, live PSH?, setpoint."""
    return [NO_ERRORS, HEATER_ON, (b"RDGF?", field), HEATER_ON, (setf, None)]


def ramp_polls(polls, errors=None):
    """Pairs of the ramp loop; ``polls`` are (OPST? reply, RDGF? reply), each followed by ERST?."""
    pairs = []
    for i, (status, field) in enumerate(polls):
        error = errors[i] if errors else b"000,000,000"
        pairs += [(b"OPST?", status), (b"RDGF?", field), (b"ERST?", error)]
    return pairs


def test_validator_locked():
    with pytest.raises(ValueError, match="interlock"):
        heater_interlocked_range(1.0, None)


def test_validator_unlocked_in_range():
    assert heater_interlocked_range(1.5, [-6, 6]) == 1.5


def test_validator_unlocked_out_of_range():
    with pytest.raises(ValueError):
        heater_interlocked_range(7.0, [-6, 6])


# field_setpoint and the live heater interlock -----------------------------------------------


def test_field_setpoint_getter():
    """Reading the setpoint does not query the heater."""
    with expected_protocol(
        LakeShore625,
        [(b"SETF?", b"0.25")],
    ) as inst:
        assert inst.field_setpoint == 0.25


def test_field_setpoint_setter_queries_heater_first():
    """Heater switched on elsewhere since init: the live PSH? query unlocks the write."""
    with expected_protocol(
        LakeShore625,
        [HEATER_ON, (b"SETF 1.5", None)],
    ) as inst:
        inst.field_setpoint = 1.5


def test_field_setpoint_setter_heater_switched_off_on_front_panel():
    with (
        expected_protocol(
            LakeShore625,
            [HEATER_OFF],  # no SETF written
        ) as inst,
        pytest.raises(ValueError, match="interlock"),
    ):
        inst.field_setpoint = 1.0


def test_field_setpoint_setter_heater_on_still_range_checked():
    with (
        expected_protocol(
            LakeShore625,
            [HEATER_ON],
        ) as inst,
        pytest.raises(ValueError),
    ):
        inst.field_setpoint = 6.5


@pytest.mark.parametrize("heater_state", [HEATER_WARMING, HEATER_COOLING])
def test_field_setpoint_setter_locked_while_heater_switching(heater_state):
    with (
        expected_protocol(
            LakeShore625,
            [heater_state],
        ) as inst,
        pytest.raises(ValueError, match="interlock"),
    ):
        inst.field_setpoint = 1.0


def test_field_setpoint_setter_every_write_queries_heater():
    with expected_protocol(
        LakeShore625,
        [HEATER_ON, (b"SETF 1", None), HEATER_ON, (b"SETF 2", None), HEATER_OFF],
    ) as inst:
        inst.field_setpoint = 1
        inst.field_setpoint = 2
        with pytest.raises(ValueError, match="interlock"):
            inst.field_setpoint = 3


def test_field_setpoint_interlock_is_per_instance():
    with (
        expected_protocol(
            LakeShore625,
            [HEATER_ON, (b"SETF 1", None)],
        ) as inst_on,
        expected_protocol(
            LakeShore625,
            [HEATER_OFF],
        ) as inst_off,
    ):
        inst_on.field_setpoint = 1
        with pytest.raises(ValueError, match="interlock"):
            inst_off.field_setpoint = 1.0


# persistent_heater ------------------------------------------------------------------------


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"PSH?", b"0")], "off"),
        ([(b"PSH?", b"1")], "on"),
        ([(b"PSH?", b"2")], "warming"),
        ([(b"PSH?", b"3")], "cooling"),
    ),
)
def test_persistent_heater_getter(comm_pairs, value):
    with expected_protocol(
        LakeShore625,
        comm_pairs,
    ) as inst:
        assert inst.persistent_heater == value


def test_persistent_heater_setter_on_unlocks_setpoint():
    with expected_protocol(
        LakeShore625,
        [(b"PSH 1", None), HEATER_ON, (b"SETF -2", None)],
    ) as inst:
        inst.persistent_heater = "on"
        inst.field_setpoint = -2


def test_persistent_heater_setter_off_relocks_without_query():
    """The private control is locked by the last known heater state, without a fresh PSH?."""
    with expected_protocol(
        LakeShore625,
        [HEATER_ON, (b"SETF 1", None), (b"PSH 0", None)],
    ) as inst:
        assert inst.persistent_heater == "on"  # unlocks the private control
        inst._field_setpoint = 1
        inst.persistent_heater = "off"
        with pytest.raises(ValueError, match="interlock"):
            inst._field_setpoint = 1.0


def test_persistent_heater_setter_on_keeps_private_control_locked():
    """Writing "on" starts warming the switch; only a PSH? read reporting "on" unlocks."""
    with expected_protocol(
        LakeShore625,
        [(b"PSH 1", None)],
    ) as inst:
        inst.persistent_heater = "on"
        with pytest.raises(ValueError, match="interlock"):
            inst._field_setpoint = 1.0


def test_persistent_heater_setter_rejects_warming():
    with (
        expected_protocol(LakeShore625, []) as inst,
        pytest.raises(ValueError),
    ):
        inst.persistent_heater = "warming"


def test_heater_parameters_getter():
    with expected_protocol(
        LakeShore625,
        [HEATER_PARAMETERS],
    ) as inst:
        assert inst.heater_parameters == [1.0, 50.0, 10.0]


# decode_errors ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "reply, messages",
    (
        ("000,032,000", ["magnet quench detected"]),
        ("004,001,002", ["output over current", "calibration error", "PSH short circuit"]),
    ),
)
def test_decode_errors(reply, messages):
    assert decode_errors(reply)[3] == messages


# wait_for_heater --------------------------------------------------------------------------


def test_wait_for_heater_until_on_and_stable(clock):
    with expected_protocol(
        LakeShore625,
        [
            HEATER_PARAMETERS,
            HEATER_WARMING,  # OPST? only asked once PSH? is "on"
            HEATER_ON,
            (b"OPST?", b"002"),  # on, switch not yet stable
            HEATER_ON,
            (b"OPST?", b"006"),
        ],
    ) as inst:
        inst.wait_for_heater("on")
    assert clock.sleeps == [1.0, 1.0]


def test_wait_for_heater_timeout(clock):
    with (
        expected_protocol(
            LakeShore625,
            [HEATER_WARMING, HEATER_WARMING],
        ) as inst,
        pytest.raises(TimeoutError),
    ):
        inst.wait_for_heater("on", timeout_s=0.5, poll_s=1.0)


# set_field_blocking -----------------------------------------------------------------------


def test_set_field_blocking_refuses_when_heater_off(clock):
    with (
        expected_protocol(
            LakeShore625,
            [NO_ERRORS, HEATER_OFF, (b"RDGF?", b"0"), HEATER_OFF],
        ) as inst,
        pytest.raises(ValueError, match="interlock"),
    ):
        inst.set_field_blocking(1.0)


def test_set_field_blocking_waits_for_warming_heater(clock):
    with expected_protocol(
        LakeShore625,
        [
            NO_ERRORS,
            HEATER_WARMING,
            HEATER_PARAMETERS,
            HEATER_ON,
            (b"OPST?", b"006"),
            (b"RDGF?", b"0"),
            HEATER_ON,
            (b"SETF 1", None),
        ]
        + ramp_polls([(b"006", b"1.0")]),
    ) as inst:
        inst.set_field_blocking(1)


def test_set_field_blocking_finishes_on_mask_and_field(clock):
    with expected_protocol(
        LakeShore625,
        ramp_start() + ramp_polls([(b"002", b"0.5"), (b"006", b"1.0")]),
    ) as inst:
        inst.set_field_blocking(1)


def test_set_field_blocking_needs_psh_stable_bit(clock):
    """Ramp done (2) at the target is not enough while the switch is not stable (4)."""
    with expected_protocol(
        LakeShore625,
        ramp_start() + ramp_polls([(b"002", b"1.0"), (b"006", b"1.0")]),
    ) as inst:
        inst.set_field_blocking(1)


def test_set_field_blocking_ignores_stale_done_at_start(clock):
    """Status still says "done" right after the write, but the field is not at the target."""
    with expected_protocol(
        LakeShore625,
        ramp_start() + ramp_polls([(b"006", b"0.0"), (b"002", b"0.5"), (b"006", b"1.0")]),
    ) as inst:
        inst.set_field_blocking(1)


def test_set_field_blocking_extra_status_bits_do_not_block(clock):
    """E.g. compliance bit (1) set as well: 7 & 6 == 6."""
    with expected_protocol(
        LakeShore625,
        ramp_start(b"0.999") + ramp_polls([(b"007", b"1.0")]),
    ) as inst:
        inst.set_field_blocking(1)


def test_set_field_blocking_adaptive_poll_interval(clock):
    """Every OPST? also sleeps 0.5 s (query_delay), so the clock moves 0.5 s per status read."""
    with expected_protocol(
        LakeShore625,
        ramp_start()
        + ramp_polls([(b"002", b"0.1"), (b"002", b"0.2"), (b"002", b"0.6"), (b"006", b"1.0")]),
    ) as inst:
        inst.set_field_blocking(1, min_poll=0.6, max_poll=10.0)
    query_delays, loop_sleeps = clock.sleeps[0::2], clock.sleeps[1::2]
    assert query_delays == [0.5] * 4
    # t=0.5: 0.1 T in 0.5 s -> 0.2 T/s, 0.9 T left -> 0.5*0.9/0.2 = 2.25 s
    # t=3.25: 0.1 T in 2.75 s -> 0.8 T left needs 22 s -> half = 11 s, clamped to 10 s
    # t=13.75: 0.4 T in 10.5 s -> 0.4 T left -> 0.5*0.4/(0.4/10.5) = 5.25 s
    assert loop_sleeps == pytest.approx([2.25, 10.0, 5.25])


def test_set_field_blocking_unknown_rate_uses_min_poll(clock):
    with expected_protocol(
        LakeShore625,
        ramp_start() + ramp_polls([(b"002", b"0.0"), (b"006", b"1.0")]),
    ) as inst:
        inst.set_field_blocking(1, min_poll=0.6, max_poll=10.0, stall_s=100)
    assert clock.sleeps[1] == 0.6


def test_set_field_blocking_stall_stops_ramp(clock):
    """Field stuck at 0.3 T; polls at 0.5, 1.5, 2.5 s -> stalled for 2.0 s > 1.2 s."""
    with (
        expected_protocol(
            LakeShore625,
            ramp_start() + ramp_polls([(b"002", b"0.3")] * 3) + [(b"STOP", None)],
        ) as inst,
        pytest.raises(TimeoutError, match="stalled"),
    ):
        inst.set_field_blocking(1, stall_s=1.2, min_poll=0.5, max_poll=0.5)


def test_set_field_blocking_timeout_stops_ramp(clock):
    """Polls at t=0.5 s (below timeout) and t=1.5 s (> 0.9 s) -> ramp stopped."""
    with (
        expected_protocol(
            LakeShore625,
            ramp_start() + ramp_polls([(b"002", b"0.1"), (b"002", b"0.2")]) + [(b"STOP", None)],
        ) as inst,
        pytest.raises(TimeoutError, match="timed out"),
    ):
        inst.set_field_blocking(1, timeout_s=0.9, min_poll=0.5, max_poll=0.5)


# faults -----------------------------------------------------------------------------------


def test_set_field_blocking_fault_before_ramp_refuses(clock):
    with (
        expected_protocol(
            LakeShore625,
            [(b"ERST?", b"000,032,000")],  # no SETF written
        ) as inst,
        pytest.raises(MagnetFaultError, match="quench"),
    ):
        inst.set_field_blocking(1)


def test_set_field_blocking_quench_during_ramp_raises_without_stop(clock):
    with (
        expected_protocol(
            LakeShore625,
            ramp_start()
            + ramp_polls(
                [(b"002", b"0.4"), (b"000", b"0.2")], errors=[b"000,000,000", b"000,096,000"]
            ),  # quench + crowbar
        ) as inst,
        pytest.raises(MagnetFaultError, match="quench"),
    ):
        inst.set_field_blocking(1)


def test_set_field_blocking_non_fatal_error_only_logged(clock, caplog):
    with expected_protocol(
        LakeShore625,
        [(b"ERST?", b"000,001,000"), HEATER_ON, (b"RDGF?", b"0"), HEATER_ON, (b"SETF 1", None)]
        + ramp_polls([(b"006", b"1.0")], errors=[b"000,001,000"]),
    ) as inst:
        inst.set_field_blocking(1)
    assert "calibration error" in caplog.text
