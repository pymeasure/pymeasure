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

# Call signature:
# $ pytest test_keysight35670A_with_device.py --device-address "GPIB0::14::INSTR"

import warnings

import pytest

from pymeasure.instruments.keysight import Keysight35670A


def _system_error_code(reply):
    """Extract the integer code from a SYSTem:ERRor? reply."""
    token = str(reply).split(",", 1)[0].strip()
    try:
        return int(token)
    except ValueError:
        try:
            return int(float(token))
        except ValueError:
            return None


def _drain_system_error_queue(analyzer, max_reads=32):
    """Drain and return non-zero system-error replies and the last observed reply."""
    errors = []
    last_reply = ""
    for _ in range(max_reads):
        reply = str(analyzer.system_error())
        last_reply = reply
        if _system_error_code(reply) == 0:
            break
        errors.append(reply)
    return errors, last_reply


def _assert_no_system_error(analyzer, context, max_reads=32):
    """Fail with context when SYSTem:ERRor? reports non-zero entries."""
    errors, last_reply = _drain_system_error_queue(analyzer, max_reads=max_reads)
    if errors:
        pytest.fail(
            f"{context}: instrument error queue not empty after {max_reads} reads; "
            f"errors={errors}; last_reply={last_reply!r}"
        )


def _close_adapter(adapter, context):
    """Close adapter best-effort and always clear adapter.connection when present."""
    if adapter is None:
        return
    try:
        adapter.close()
    except Exception as exc:
        warnings.warn(
            f"Ignored error during {context} adapter cleanup: {exc!r}",
            RuntimeWarning,
            stacklevel=2,
        )
    finally:
        if hasattr(adapter, "connection"):
            adapter.connection = None


def _has_ay6_option(options_reply):
    """Return True if options indicate 4-channel capability."""
    tokens = {
        token.strip().strip('"')
        for token in str(options_reply).upper().split(",")
        if token.strip()
    }
    return "AY6" in tokens or "A6J" in tokens


@pytest.fixture(scope="module")
def analyzer(connected_device_address):
    """Create one instrument instance per module with safe teardown and queue drain."""
    instr = Keysight35670A(connected_device_address, timeout=20000)
    adapter = getattr(instr, "adapter", None)
    try:
        try:
            instr.source_output_enabled = False
        except Exception as exc:
            warnings.warn(
                f"Ignored error during safe-state setup cleanup: {exc!r}",
                RuntimeWarning,
                stacklevel=2,
            )
        _assert_no_system_error(instr, "setup", max_reads=32)
        yield instr
    finally:
        teardown_notes = []
        try:
            instr.source_output_enabled = False
        except Exception as exc:
            teardown_notes.append(f"failed to force source_output_enabled=False: {exc!r}")
        try:
            errors, last_reply = _drain_system_error_queue(instr, max_reads=32)
            if errors:
                teardown_notes.append(
                    "teardown: error queue not empty; "
                    f"errors={errors}; last_reply={last_reply!r}"
                )
        except Exception as exc:
            teardown_notes.append(f"teardown drain failed: {exc!r}")

        _close_adapter(adapter, "analyzer teardown")

        if teardown_notes:
            pytest.fail("; ".join(teardown_notes))


@pytest.fixture(autouse=True)
def ensure_safe_state(analyzer, request):
    """Force output OFF and fail clearly when any post-test instrument error remains."""
    analyzer.source_output_enabled = False
    _assert_no_system_error(analyzer, "ensure_safe_state", max_reads=32)
    yield
    notes = []
    try:
        analyzer.source_output_enabled = False
    except Exception as exc:
        notes.append(f"could not force source_output_enabled=False: {exc!r}")
    if notes:
        pytest.fail("; ".join(notes))
    _assert_no_system_error(
        analyzer,
        f"ensure_safe_state after {request.node.name}",
        max_reads=32,
    )


def test_hardware_identity_and_options(analyzer):
    """Use only *IDN? and *OPT? reads, which are safe and non-destructive."""
    idn = analyzer.id
    options = analyzer.options()
    assert "35670A" in idn.upper()
    analyzer.check_id()
    assert isinstance(options, str)
    print(f"*IDN? -> {idn}")
    print(f"*OPT? -> {options}")


def test_hardware_system_readonly_queries(analyzer):
    """Use query-only system/status accessors that do not change instrument state."""
    assert isinstance(analyzer.system_version, str)
    assert isinstance(analyzer.power_source, str)
    assert isinstance(analyzer.status_byte, int)
    assert isinstance(analyzer.operation_condition, int)
    assert isinstance(analyzer.questionable_condition, int)
    assert isinstance(analyzer.device_condition, int)
    system_error_reply = analyzer.system_error()
    assert isinstance(system_error_reply, str)
    print(f"SYSTem:ERRor? -> {system_error_reply}")


def test_hardware_source_safe_roundtrip_restores_state(analyzer):
    """Set only safe source fields with output OFF and restore state in finally."""
    original_function = analyzer.source_function
    original_frequency = analyzer.source_frequency
    original_offset = analyzer.source_voltage_offset

    try:
        analyzer.source_output_enabled = False
        analyzer.source_function = "sine"
        analyzer.source_frequency = 1000.0
        assert analyzer.source_frequency == pytest.approx(1000.0, abs=1e-3, rel=1e-6)
        analyzer.source_voltage_offset = 0.0
        assert analyzer.source_voltage_offset == pytest.approx(0.0, abs=1e-3, rel=1e-6)
        analyzer.source_output_enabled = False
        assert analyzer.source_output_enabled is False
    finally:
        try:
            analyzer.source_frequency = original_frequency
        finally:
            try:
                analyzer.source_voltage_offset = original_offset
            finally:
                try:
                    analyzer.source_function = original_function
                finally:
                    analyzer.source_output_enabled = False


def test_hardware_input_ch1_coupling_roundtrip_restores_state(analyzer):
    """Toggle CH1 coupling AC/DC and restore original state in finally."""
    original_coupling = analyzer.ch1.coupling
    try:
        analyzer.ch1.coupling = "AC"
        assert str(analyzer.ch1.coupling).upper().startswith("AC")
        analyzer.ch1.coupling = "DC"
        assert str(analyzer.ch1.coupling).upper().startswith("DC")
    finally:
        analyzer.ch1.coupling = original_coupling


def test_hardware_input_ch1_autorange_roundtrip_restores_state(analyzer):
    """Toggle CH1 autorange and restore original state in finally."""
    original_autorange_enabled = analyzer.ch1.autorange_enabled
    try:
        analyzer.ch1.autorange_enabled = True
        assert isinstance(analyzer.ch1.autorange_enabled, bool)
    finally:
        analyzer.ch1.autorange_enabled = original_autorange_enabled


def test_hardware_trace_ascii_data_smoke(analyzer):
    """Read trace points/data in ASCII after safe FFT setup and restore state."""
    original_mode = analyzer.instrument_mode
    original_data_format = analyzer.data_format
    original_trace1_feed = None
    original_trace1_feed_raw = None
    try:
        original_trace1_feed = analyzer.trace1.feed
    except KeyError:
        raw_feed = analyzer.ask("CALCulate1:FEED?").strip()
        if raw_feed.startswith('"') and raw_feed.endswith('"'):
            raw_feed = raw_feed[1:-1]
        original_trace1_feed_raw = raw_feed

    try:
        analyzer.source_output_enabled = False
        analyzer.data_format = "ascii"
        analyzer.instrument_mode = "fft"
        analyzer.trace1.feed = "power_spectrum_ch1"
        analyzer.initiate()
        analyzer.wait_for_completion()

        points = analyzer.trace1.data_points()
        data = analyzer.trace1.read_data()
        x_axis = analyzer.trace1.read_x_data()

        assert isinstance(points, int)
        assert points > 0
        assert isinstance(data, list)
        assert isinstance(x_axis, list)
        assert len(data) > 0
        assert len(x_axis) > 0
    finally:
        try:
            if original_trace1_feed is not None:
                analyzer.trace1.feed = original_trace1_feed
            elif original_trace1_feed_raw:
                analyzer.write(f'CALCulate1:FEED "{original_trace1_feed_raw}"')
        finally:
            try:
                analyzer.instrument_mode = original_mode
            finally:
                analyzer.data_format = original_data_format
                analyzer.source_output_enabled = False


def test_hardware_format_data_roundtrip_restores_state(analyzer):
    """Roundtrip FORMat:DATA with ascii only and restore original state."""
    original_data_format = analyzer.data_format
    try:
        analyzer.data_format = "ascii"
        assert analyzer.data_format == "ascii"
    finally:
        analyzer.data_format = original_data_format


def test_hardware_display_safe_roundtrip_restores_state(analyzer):
    """Toggle display enable state and restore original state in finally."""
    original_display_enabled = analyzer.display_enabled
    try:
        analyzer.display_enabled = True
        assert isinstance(analyzer.display_enabled, bool)
    finally:
        analyzer.display_enabled = original_display_enabled


def test_hardware_beeper_enabled_roundtrip_restores_state(analyzer):
    """Toggle beeper state without immediate beep command, then restore original state."""
    original_beeper_enabled = analyzer.beeper_enabled
    try:
        analyzer.beeper_enabled = False
        assert analyzer.beeper_enabled is False
        analyzer.beeper_enabled = True
        assert analyzer.beeper_enabled is True
    finally:
        analyzer.beeper_enabled = original_beeper_enabled


def test_hardware_ch3_ch4_skip_if_no_option(analyzer):
    """Query CH3/CH4 only when AY6/A6J is installed; otherwise skip with clear reason."""
    options = analyzer.options()
    if not _has_ay6_option(options):
        pytest.skip(f"4-channel option (AY6/A6J) not installed; *OPT?={options!r}")
    assert isinstance(analyzer.ch3.coupling, str)
    assert isinstance(analyzer.ch4.coupling, str)
