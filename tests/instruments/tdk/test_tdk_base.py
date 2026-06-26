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
from pymeasure.instruments.tdk.tdk_base import TDK_Lambda_Base


def test_init():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK")],
    ):
        pass  # Verify the expected communication.


def test_identity():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"IDN?", b'LAMBDA,GENX-Y'),
             (b"REV?", b"REV:1U:4.3")]
    ) as instr:
        assert instr.id == ["LAMBDA", "GENX-Y"]
        assert instr.version == "REV:1U:4.3"


def test_multidrop_capability():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"MDAV?", b'1')]
    ) as instr:
        assert instr.multidrop_capability is True


def test_remote():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"RMT?", b"REM"),
             (b"RMT LOC", b"OK"),
             (b"RMT?", b"LOC"), ]
    ) as instr:
        assert instr.remote == "REM"
        instr.remote = 'LOC'
        assert instr.remote == "LOC"


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Measurement properties
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_serial():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"SN?", b"12345")]
    ) as instr:
        assert instr.serial == "12345"


def test_last_test_date():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"DATE?", b"2024/01/01")]
    ) as instr:
        assert instr.last_test_date == "2024/01/01"


def test_master_slave_setting():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"MS?", b"1")]
    ) as instr:
        assert instr.master_slave_setting == 1.0


def test_repeat():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"MV?", b"12.5"),
             (b"\\", b"12.5")]
    ) as instr:
        _ = instr.voltage
        assert instr.repeat == 12.5


def test_voltage_measurement():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"MV?", b"12.5")]
    ) as instr:
        assert instr.voltage == 12.5


def test_current_measurement():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"MC?", b"3.25")]
    ) as instr:
        assert instr.current == 3.25


def test_mode():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"MODE?", b"CV")]
    ) as instr:
        assert instr.mode == "CV"


def test_display():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"DVC?", b"12.5,12,3.25,3,44,0")]
    ) as instr:
        assert instr.display == [12.5, 12.0, 3.25, 3.0, 44.0, 0.0]


def test_status():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"STT?", b"12.5,12,3.25,3,0,0")]
    ) as instr:
        assert instr.status == [12.5, 12.0, 3.25, 3.0, 0.0, 0.0]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Setpoint control properties
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_voltage_setpoint_get_set():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"PV 10", b"OK"),
             (b"PV?", b"10")]
    ) as instr:
        instr.voltage_setpoint = 10
        assert instr.voltage_setpoint == 10


def test_current_setpoint_get_set():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"PC 5", b"OK"),
             (b"PC?", b"5")]
    ) as instr:
        instr.current_setpoint = 5
        assert instr.current_setpoint == 5


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Protection / configuration control properties
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_over_voltage():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"OVP 20", b"OK"),
             (b"OVP?", b"20")]
    ) as instr:
        instr.over_voltage = 20
        assert instr.over_voltage == 20


def test_under_voltage():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"UVL 10", b"OK"),
             (b"UVL?", b"10")]
    ) as instr:
        instr.under_voltage = 10
        assert instr.under_voltage == 10


def test_pass_filter():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"FILTER?", b"18"),
             (b"FILTER 23", b"OK")]
    ) as instr:
        assert instr.pass_filter == 18
        instr.pass_filter = 23


def test_output_enabled():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"OUT?", b"ON"),
             (b"OUT OFF", b"OK")]
    ) as instr:
        assert instr.output_enabled is True
        instr.output_enabled = False


def test_foldback_enabled():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"FLD?", b"OFF"),
             (b"FLD ON", b"OK")]
    ) as instr:
        assert instr.foldback_enabled is False
        instr.foldback_enabled = True


def test_foldback_delay():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"FBD?", b"5"),
             (b"FBD 10", b"OK")]
    ) as instr:
        val = instr.foldback_delay
        assert val == 5
        assert isinstance(val, int)
        instr.foldback_delay = 10


def test_auto_restart_enabled():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"AST?", b"OFF"),
             (b"AST ON", b"OK")]
    ) as instr:
        assert instr.auto_restart_enabled is False
        instr.auto_restart_enabled = True


def test_address_set():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"ADR 7", b"OK")]
    ) as instr:
        instr.address = 7


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# check_set_errors behavior
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_check_set_errors_ok(monkeypatch):
    """A non-querying command returning 'OK' produces an empty error list."""
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"RMT LOC", b"OK")]
    ) as instr:
        # No exception is raised and no errors are populated.
        instr.remote = "LOC"


def test_check_set_errors_non_ok(caplog):
    """A non-querying command returning a non-'OK' response populates the
    error list (logged, not raised)."""
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"RMT LOC", b"ERR123")]
    ) as instr:
        instr.remote = "LOC"
        # The received error is logged via the common_base error handling.
        assert "Received error: ERR123" in caplog.text


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Methods (clear, reset, foldback_reset, save, recall, set_max_over_voltage)
# call self.check_errors(), which is not implemented in the TDK hierarchy.
# Use a monkeypatched stub to verify the correct command is sent.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def _stub_check_errors(self):
    """Stub for the unimplemented ``check_errors`` method.

    The TDK methods (``clear``, ``reset``, ...) issue a non-querying command
    that receives an ``OK`` reply, then call ``check_errors``. As
    ``check_errors`` is not implemented in the TDK hierarchy, this stub
    consumes the reply so the protocol buffer is drained.
    """
    self.read()
    return []


def test_clear(monkeypatch):
    monkeypatch.setattr(TDK_Lambda_Base, "check_errors", _stub_check_errors)
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"CLS", b"OK")]
    ) as instr:
        instr.clear()


def test_reset(monkeypatch):
    monkeypatch.setattr(TDK_Lambda_Base, "check_errors", _stub_check_errors)
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"RST", b"OK")]
    ) as instr:
        instr.reset()


def test_foldback_reset(monkeypatch):
    monkeypatch.setattr(TDK_Lambda_Base, "check_errors", _stub_check_errors)
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"FDBRST", b"OK")]
    ) as instr:
        instr.foldback_reset()


def test_save(monkeypatch):
    monkeypatch.setattr(TDK_Lambda_Base, "check_errors", _stub_check_errors)
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"SAV", b"OK")]
    ) as instr:
        instr.save()


def test_recall(monkeypatch):
    monkeypatch.setattr(TDK_Lambda_Base, "check_errors", _stub_check_errors)
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"RCL", b"OK")]
    ) as instr:
        instr.recall()


def test_set_max_over_voltage(monkeypatch):
    monkeypatch.setattr(TDK_Lambda_Base, "check_errors", _stub_check_errors)
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"OVM", b"OK")]
    ) as instr:
        instr.set_max_over_voltage()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ramp_to_current and shutdown
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_ramp_to_current():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"PC?", b"5"),
             (b"PC 5", b"OK"),
             (b"PC 3.75", b"OK"),
             (b"PC 2.5", b"OK"),
             (b"PC 1.25", b"OK"),
             (b"PC 0", b"OK")]
    ) as instr:
        instr.ramp_to_current(0, steps=5, pause=0)


def test_shutdown():
    # ramp_to_current uses 20 steps by default: np.linspace(5, 0, 20) rounded.
    ramp_currents = [
        5.0, 4.74, 4.47, 4.21, 3.95, 3.68, 3.42, 3.16, 2.89, 2.63,
        2.37, 2.11, 1.84, 1.58, 1.32, 1.05, 0.79, 0.53, 0.26, 0.0,
    ]
    proto = [(b"ADR 6", b"OK"), (b"PC?", b"5")]
    for c in ramp_currents:
        proto.append((f"PC {c:g}".encode(), b"OK"))
    proto.append((b"OUT OFF", b"OK"))
    with expected_protocol(
            TDK_Lambda_Base,
            proto,
    ) as instr:
        instr.shutdown()
        assert instr.isShutdown is True
