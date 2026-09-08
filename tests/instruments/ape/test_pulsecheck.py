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
import struct

import pytest

from pymeasure.instruments.ape import PulseCheck
from pymeasure.instruments.ape import pulsecheck as pulsecheck_module
from pymeasure.test import expected_protocol


def test_connection_settings_can_be_overridden():
    """The defaults must not clash with connection settings passed by the user."""
    with expected_protocol(
        PulseCheck,
        [("GTA", b"\x07")],
        write_termination="\r",
        asrl={"baud_rate": 9600},
    ) as inst:
        assert inst.tau_register == 7


def test_gain_get():
    with expected_protocol(
        PulseCheck,
        [("GG", struct.pack(">H", 250))],
    ) as inst:
        assert inst.gain == 250


def test_gain_set():
    with expected_protocol(
        PulseCheck,
        [("GN500", None)],
    ) as inst:
        inst.gain = 500


def test_averages():
    with expected_protocol(
        PulseCheck,
        [("GAV", b"\x04"), ("A8", None)],
    ) as inst:
        assert inst.averages == 4
        inst.averages = 8


def test_filter():
    with expected_protocol(
        PulseCheck,
        [("GF", b"\x02"), ("F3", None)],
    ) as inst:
        assert inst.filter == "medium"
        inst.filter = "high"


def test_math_enabled():
    with expected_protocol(
        PulseCheck,
        [("GM", b"\x01"), ("M0", None)],
    ) as inst:
        assert inst.math_enabled is True
        inst.math_enabled = False


def test_measurement_running():
    with expected_protocol(
        PulseCheck,
        [("GRS", b"\x01"), ("RS0", None)],
    ) as inst:
        assert inst.measurement_running is True
        inst.measurement_running = False


def test_scan_range():
    with expected_protocol(
        PulseCheck,
        [("GSR", b"\x03"), ("SR2", None)],
    ) as inst:
        assert inst.scan_range == pytest.approx(15e-12)
        inst.scan_range = 5e-12


def test_resolution():
    with expected_protocol(
        PulseCheck,
        [("GRE", b"\x05")],
    ) as inst:
        assert inst.resolution == 32


def test_alpha():
    with expected_protocol(
        PulseCheck,
        [("GPM", struct.pack(">H", 1000))],
    ) as inst:
        assert inst.alpha == 1000


def test_tau_register():
    with expected_protocol(
        PulseCheck,
        [("GTA", b"\x07")],
    ) as inst:
        assert inst.tau_register == 7


def test_sensitivity():
    with expected_protocol(
        PulseCheck,
        [("GSY", b"\x05"), ("SY6", None)],
    ) as inst:
        assert inst.sensitivity == 100
        inst.sensitivity = 300


@pytest.mark.parametrize("code, mode", [(0, "freerun"), (1, "trigger"),
                                        (2, "fringe"), (4, "slow")])
def test_trigger_mode_get(code, mode):
    with expected_protocol(
        PulseCheck,
        [("GTF", bytes([code]))],
    ) as inst:
        assert inst.trigger_mode == mode


@pytest.mark.parametrize("mode, index", [("freerun", 0), ("trigger", 1),
                                         ("fringe", 2), ("slow", 3)])
def test_trigger_mode_set(mode, index):
    with expected_protocol(
        PulseCheck,
        [(f"TF{index}", None)],
    ) as inst:
        inst.trigger_mode = mode


def test_trigger_mode_get_unknown_code():
    """An undocumented code has to be readable, since `settings` reads the mode as well."""
    with expected_protocol(
        PulseCheck,
        [("GTF", b"\x03")],
    ) as inst:
        assert inst.trigger_mode == "unknown (3)"


def test_raw_acf():
    with expected_protocol(
        PulseCheck,
        [("GRE", b"\x02"), ("GAC", struct.pack(">4H", 64, 128, 192, 256))],
    ) as inst:
        assert inst.raw_acf() == [1, 2, 3, 4]


def test_acf():
    with expected_protocol(
        PulseCheck,
        [
            ("GRE", b"\x02"),
            ("GAC", struct.pack(">4H", 64, 128, 192, 256)),
            ("GSR", b"\x02"),
        ],
    ) as inst:
        delay, acf = inst.acf
        assert list(acf) == [1, 2, 3, 4]
        assert delay[0] == pytest.approx(-2.5e-12)
        assert delay[-1] == pytest.approx(2.5e-12)


def test_set_alpha_reaches_target_immediately(monkeypatch):
    monkeypatch.setattr(pulsecheck_module.time, "sleep", lambda seconds: None)
    with expected_protocol(
        PulseCheck,
        [
            ("GPM", struct.pack(">H", 90)),
            ("TU10", None),
            ("GPM", struct.pack(">H", 100)),
        ],
    ) as inst:
        inst.set_alpha(100)


def test_set_alpha_retries_after_getting_stuck(monkeypatch):
    """Verify that a stuck first attempt is retried and can still succeed."""
    monkeypatch.setattr(pulsecheck_module.time, "sleep", lambda seconds: None)
    with expected_protocol(
        PulseCheck,
        [
            ("GPM", struct.pack(">H", 90)),  # tune(): current position
            ("TU10", None),
            ("GPM", struct.pack(">H", 90)),  # current, after the initial 1 s wait
            ("GPM", struct.pack(">H", 90)),  # stuck-check 1/2: unchanged
            ("GPM", struct.pack(">H", 90)),  # stuck-check 2/2: unchanged -> retry
            ("GPM", struct.pack(">H", 100)),  # 2nd attempt: tune(): already there
            ("TU0", None),
            ("GPM", struct.pack(">H", 100)),  # current == target -> done
        ],
    ) as inst:
        inst.set_alpha(100)


def test_set_alpha_raises_timeout_error_when_stuck(monkeypatch):
    """Verify that a persistently stuck position raises instead of recursing forever."""
    monkeypatch.setattr(pulsecheck_module.time, "sleep", lambda seconds: None)
    with expected_protocol(
        PulseCheck,
        [
            ("GPM", struct.pack(">H", 90)),  # tune(): current position
            ("TU10", None),
            ("GPM", struct.pack(">H", 90)),  # current, after the initial 1 s wait
            ("GPM", struct.pack(">H", 90)),  # stuck-check 1/2: unchanged
            ("GPM", struct.pack(">H", 90)),  # stuck-check 2/2: unchanged -> give up
        ],
    ) as inst, pytest.raises(TimeoutError):
        inst.set_alpha(100, retries=0)


def test_set_alpha_rejects_negative_retries():
    with expected_protocol(PulseCheck, []) as inst, pytest.raises(ValueError, match="retries"):
        inst.set_alpha(100, retries=-1)


def test_set_alpha_raises_timeout_error_when_deadline_passes(monkeypatch):
    """Verify that a position which keeps moving without arriving does not loop forever."""
    monkeypatch.setattr(pulsecheck_module.time, "sleep", lambda seconds: None)
    clock = iter([0, 10, 100])  # deadline = 60; tripped right after the settling wait
    monkeypatch.setattr(pulsecheck_module.time, "monotonic", lambda: next(clock))
    with expected_protocol(
        PulseCheck,
        [
            ("GPM", struct.pack(">H", 90)),  # tune(): current position
            ("TU10", None),
            ("GPM", struct.pack(">H", 90)),  # current, after the initial 1 s wait
        ],
    ) as inst, pytest.raises(TimeoutError, match="timed out"):
        inst.set_alpha(100)


def test_set_alpha_raises_when_target_reached_after_timeout(monkeypatch):
    """Reaching the target after the deadline must report a timeout, not success."""
    monkeypatch.setattr(pulsecheck_module.time, "sleep", lambda seconds: None)
    clock = iter([0, 10, 20, 100])  # deadline = 60; only the success check at 100 is past it
    monkeypatch.setattr(pulsecheck_module.time, "monotonic", lambda: next(clock))
    with expected_protocol(
        PulseCheck,
        [
            ("GPM", struct.pack(">H", 90)),  # tune(): current position
            ("TU10", None),
            ("GPM", struct.pack(">H", 100)),  # settled on the target, but past the deadline
        ],
    ) as inst, pytest.raises(TimeoutError, match="timed out"):
        inst.set_alpha(100)


def test_tune():
    with expected_protocol(
        PulseCheck,
        [("TU-5", None)],
    ) as inst:
        inst.tune(-5)


def test_settings():
    with expected_protocol(
        PulseCheck,
        [
            ("GSY", b"\x01"),
            ("GG", struct.pack(">H", 250)),
            ("GSR", b"\x00"),
            ("GF", b"\x01"),
            ("GAV", b"\x02"),
            ("GRE", b"\x02"),
            ("GPM", struct.pack(">H", 1000)),
            ("GM", b"\x01"),
            ("GTF", b"\x00"),
        ],
    ) as inst:
        assert inst.settings == {
            "sensitivity": 1,
            "gain": 250,
            "scan_range": 0,
            "filter": "low",
            "averages": 2,
            "resolution": 4,
            "alpha": 1000,
            "math_enabled": True,
            "trigger_mode": "freerun",
        }
