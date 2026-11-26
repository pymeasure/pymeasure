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

from pymeasure.adapters.protocol import ProtocolAdapter
from pymeasure.instruments.keysight import Keysight34465A
from pymeasure.instruments.keysight.keysight34465a import MeasurementError
from pymeasure.test import expected_protocol

# SCPI choices below follow the manufacturer-authored Keysight Truevolt Series Operating and
# Service Guide, 34460-90901 Edition 7 (March 2020). PDF page numbers are one lower than the
# printed page labels in the supplied copy.
_NO_ERROR = ("SYST:ERR?", "0,No error")


def _checked_writes(*commands):
    """Return expected command/error-query pairs for writes accepted by the instrument."""
    return [pair for command in commands for pair in ((command, None), _NO_ERROR)]


@pytest.mark.parametrize(
    ("function", "range_", "command"),
    [
        ("DCV", 10.0, "CONF:VOLT:DC 10"),
        ("DCI", 10.0, "CONF:CURR:DC 10"),
        ("RES", 1000.0, "CONF:RES 1000"),
        ("FRES", 100.0, "CONF:FRES 100"),
        ("FREQ", None, "CONF:FREQ"),
        ("PER", None, "CONF:PER"),
        ("CONT", None, "CONF:CONT"),
        ("DIOD", None, "CONF:DIOD"),
    ],
)
def test_configure_functions(function, range_, command):
    # CONF function support and fixed ranges: manual PDF pp. 245-249 and 251.
    with expected_protocol(
        Keysight34465A, [(command, None), _NO_ERROR]
    ) as instrument:
        instrument.configure(function, range_=range_)


def test_configure_frequency_range_means_input_voltage_range():
    # The frequency/period range is an input-voltage range, manual PDF pp. 248 and 341-342.
    with expected_protocol(
        Keysight34465A,
        [
            ("CONF:FREQ", None),
            _NO_ERROR,
            ("FREQ:VOLT:RANG 10", None),
            _NO_ERROR,
        ],
    ) as instrument:
        instrument.configure("FREQ", range_=10.0)


def test_configure_validates_before_write():
    adapter = ProtocolAdapter([])
    instrument = Keysight34465A(adapter)

    with pytest.raises(ValueError, match="does not support NPLC"):
        instrument.configure("FREQ", range_=10.0, nplc=1.0)

    assert adapter._index == 0
    assert adapter._write_buffer is None


def test_configure_rejects_fixed_range_for_continuity():
    adapter = ProtocolAdapter([])
    instrument = Keysight34465A(adapter)

    with pytest.raises(ValueError, match="does not support a selectable range"):
        instrument.configure("CONT", range_=100.0)

    assert adapter._index == 0


def test_configure_rejects_auto_range_for_diode():
    adapter = ProtocolAdapter([])
    instrument = Keysight34465A(adapter)

    with pytest.raises(ValueError, match="does not support a selectable range"):
        instrument.configure("DIOD", range_="AUTO")

    assert adapter._index == 0


def test_configure_dig_nplc_checks_installed_option_before_writing():
    # NPLC values below 0.02 require DIG, manual PDF pp. 328, 347, and 381.
    with expected_protocol(
        Keysight34465A,
        [
            ("*OPT?", "DIG"),
            ("CONF:VOLT:DC", None),
            _NO_ERROR,
            ("VOLT:DC:NPLC 0.001", None),
            _NO_ERROR,
        ],
    ) as instrument:
        instrument.configure("DCV", nplc=0.001)


def test_four_wire_autozero_uses_two_wire_scpi_command():
    # The manual uses RES:ZERO:AUTO for 4-wire; it has no effect on 4-wire behavior (PDF p. 356).
    with expected_protocol(
        Keysight34465A,
        [
            ("CONF:FRES", None),
            _NO_ERROR,
            ("RES:ZERO:AUTO 1", None),
            _NO_ERROR,
        ],
    ) as instrument:
        instrument.configure("FRES", autozero_enabled=True)


def test_configure_can_enable_autozero_with_fast_nplc():
    # The manual allows independent ZERO:AUTO and NPLC settings; see PDF pp. 331 and 384.
    with expected_protocol(
        Keysight34465A,
        [
            ("CONF:VOLT:DC", None),
            _NO_ERROR,
            ("VOLT:DC:NPLC 0.2", None),
            _NO_ERROR,
            ("VOLT:DC:ZERO:AUTO 1", None),
            _NO_ERROR,
        ],
    ) as instrument:
        instrument.configure("DCV", nplc=0.2, autozero_enabled=True)


def test_configure_rejects_dig_nplc_without_option_before_writing():
    with expected_protocol(Keysight34465A, [("*OPT?", "0")]) as instrument, pytest.raises(
        ValueError, match="requires the optional DIG option"
    ):
        instrument.configure("DCV", nplc=0.001)


def test_set_internal_trigger_source_checks_dig_option():
    # INT is listed for the 34465A only with DIG, manual PDF p. 432.
    with expected_protocol(
        Keysight34465A,
        [
            ("*OPT?", "DIG"),
            ("TRIG:SOUR INT", None),
            _NO_ERROR,
        ],
    ) as instrument:
        instrument.set_trigger_source("int")


def test_set_trigger_source_raises_on_scpi_error():
    with expected_protocol(
        Keysight34465A,
        [
            ("TRIG:SOUR EXT", None),
            ("SYST:ERR?", '-222,"Data out of range"'),
            _NO_ERROR,
        ],
    ) as instrument, pytest.raises(RuntimeError, match="reported SCPI errors"):
        instrument.set_trigger_source("EXT")


def test_configure_stops_after_scpi_error():
    with expected_protocol(
        Keysight34465A,
        [
            ("CONF:VOLT:DC", None),
            ("SYST:ERR?", '-222,"Data out of range"'),
            _NO_ERROR,
        ],
    ) as instrument, pytest.raises(RuntimeError, match="reported SCPI errors"):
        instrument.configure("DCV", nplc=1.0)


def test_arm_stops_after_init_scpi_error_without_fetching():
    with expected_protocol(
        Keysight34465A,
        [
            *_checked_writes(
                "ABOR", "TRIG:SOUR BUS", "SAMP:COUN 1", "TRIG:COUN 1", "TRIG:DEL:AUTO ON"
            ),
            ("INIT", None),
            ("SYST:ERR?", '-213,"Init ignored"'),
            _NO_ERROR,
        ],
    ) as instrument, pytest.raises(RuntimeError, match="reported SCPI errors"):
        instrument.arm(sample_count=1)


def test_frequency_input_voltage_range_property():
    with expected_protocol(
        Keysight34465A,
        [
            ("FREQ:VOLT:RANG?", "10"),
            ("FREQ:VOLT:RANG 10", None),
            ("SYST:ERR?", "0,No error"),
        ],
    ) as instrument:
        assert instrument.frequency_input_voltage_range == 10.0
        instrument.frequency_input_voltage_range = 10.0


def test_configure_frequency_autorange():
    with expected_protocol(
        Keysight34465A,
        [
            ("CONF:PER", None),
            _NO_ERROR,
            ("FREQ:VOLT:RANG:AUTO ON", None),
            _NO_ERROR,
        ],
    ) as instrument:
        instrument.configure("PER", range_="AUTO")


def test_voltage_range_and_autorange_properties():
    with expected_protocol(
        Keysight34465A,
        [
            ("VOLT:DC:RANG?", "10"),
            ("VOLT:DC:RANG 10", None),
            ("SYST:ERR?", "0,No error"),
            ("VOLT:DC:RANG:AUTO?", "1"),
            ("VOLT:DC:RANG:AUTO 0", None),
            ("SYST:ERR?", "0,No error"),
        ],
    ) as instrument:
        assert instrument.voltage_range == 10.0
        instrument.voltage_range = 10.0
        assert instrument.voltage_autorange_enabled is True
        instrument.voltage_autorange_enabled = False


def test_current_and_resistance_fixed_ranges():
    with expected_protocol(
        Keysight34465A,
        [
            ("CURR:DC:RANG 3", None),
            ("SYST:ERR?", "0,No error"),
            ("RES:RANG 1000000", None),
            ("SYST:ERR?", "0,No error"),
        ],
    ) as instrument:
        instrument.current_range = 3.0
        instrument.resistance_range = 1_000_000.0


@pytest.mark.parametrize(
    ("current_range", "reply", "command"),
    [
        (1e-6, "1e-6", "CURR:DC:RANG 0.000001"),
        (1e-5, "1e-5", "CURR:DC:RANG 0.00001"),
    ],
)
def test_current_microamp_ranges(current_range, reply, command):
    # Truevolt manual PDF p. 323 (printed p. 324) lists 1 uA and 10 uA DC sense ranges;
    # the separate CONF range table on PDF p. 246 starts at 100 uA and includes 10 A.
    with expected_protocol(
        Keysight34465A,
        [
            ("CURR:DC:RANG?", reply),
            (command, None),
            _NO_ERROR,
        ],
    ) as instrument:
        assert instrument.current_range == current_range
        instrument.current_range = current_range


def test_nplc_and_autozero_properties():
    # Resistance autozero uses RES:ZERO:AUTO for both RES and FRES; manual PDF p. 356.
    with expected_protocol(
        Keysight34465A,
        [
            ("VOLT:DC:NPLC?", "1"),
            ("VOLT:DC:NPLC 0.2", None),
            ("SYST:ERR?", "0,No error"),
            ("CURR:DC:NPLC 10", None),
            ("SYST:ERR?", "0,No error"),
            ("RES:NPLC 100", None),
            ("SYST:ERR?", "0,No error"),
            ("RES:ZERO:AUTO 0", None),
            ("SYST:ERR?", "0,No error"),
        ],
    ) as instrument:
        assert instrument.voltage_nplc == 1.0
        instrument.voltage_nplc = 0.2
        instrument.current_nplc = 10.0
        instrument.resistance_nplc = 100.0
        instrument.resistance_autozero_enabled = False


def test_display_enable_property():
    with expected_protocol(
        Keysight34465A,
        [
            ("DISP:STAT?", "1"),
            ("DISP:STAT 0", None),
            ("SYST:ERR?", "0,No error"),
        ],
    ) as instrument:
        assert instrument.display_enabled is True
        instrument.display_enabled = False


def test_trigger_controls_properties():
    with expected_protocol(
        Keysight34465A,
        [
            ("TRIG:SOUR?", "BUS"),
            ("TRIG:SOUR EXT", None),
            ("SYST:ERR?", "0,No error"),
            ("SAMP:COUN?", "4"),
            ("SAMP:COUN 5", None),
            ("SYST:ERR?", "0,No error"),
            ("TRIG:COUN?", "2"),
            ("TRIG:COUN 3", None),
            ("SYST:ERR?", "0,No error"),
            ("TRIG:DEL?", "1"),
            ("TRIG:DEL 0.5", None),
            ("SYST:ERR?", "0,No error"),
        ],
    ) as instrument:
        assert instrument.trigger_source == "BUS"
        instrument.trigger_source = "ext"
        assert instrument.sample_count == 4
        instrument.sample_count = 5
        assert instrument.trigger_count == 2
        instrument.trigger_count = 3
        assert instrument.trigger_delay == 1.0
        instrument.trigger_delay = 0.5


def test_measure_group_measure_resets_trigger_state():
    # INIT clears old memory and FETC? copies available readings; manual PDF pp. 201-202.
    # READ? is absent so each operation's source and counts stay explicit.
    sequence = []
    for count, response in ((1, "+1.25E+00"), (3, "-1E-3,+2E-3,9.9E37"), (1, "-4.5E-2")):
        sequence.extend(
            _checked_writes(
                "ABOR",
                "TRIG:SOUR IMM",
                f"SAMP:COUN {count}",
                "TRIG:COUN 1",
                "TRIG:DEL:AUTO ON",
                "INIT",
            )
        )
        sequence.extend(
            [("FORM:DATA ASC", None), _NO_ERROR, ("FETC?", response), _NO_ERROR]
        )

    with expected_protocol(Keysight34465A, sequence) as instrument:
        assert instrument.measure() == 1.25
        assert instrument.acquire(3) == [-0.001, 0.002, 9.9e37]
        assert instrument.measure() == -0.045


def test_acquire_one_returns_list():
    with expected_protocol(
        Keysight34465A,
        [
            *_checked_writes(
                "ABOR", "TRIG:SOUR IMM", "SAMP:COUN 1", "TRIG:COUN 1", "TRIG:DEL:AUTO ON", "INIT"
            ),
            ("FORM:DATA ASC", None),
            _NO_ERROR,
            ("FETC?", "+1E+2"),
            _NO_ERROR,
        ],
    ) as instrument:
        assert instrument.acquire(1) == [100.0]


def test_bus_arm_trigger_fetch_order():
    # The manual's BUS example uses INIT, *TRG, FETC?; see PDF p. 202.
    with expected_protocol(
        Keysight34465A,
        [
            *_checked_writes(
                "ABOR", "TRIG:SOUR BUS", "SAMP:COUN 3", "TRIG:COUN 2", "TRIG:DEL 0.5", "INIT"
            ),
            *_checked_writes("*TRG", "*TRG"),
            ("FORM:DATA ASC", None),
            _NO_ERROR,
            ("FETC?", "+1E+1,-2E+1,+3E+1,+4E+1,+5E+1,+6E+1"),
            _NO_ERROR,
        ],
    ) as instrument:
        instrument.arm(sample_count=3, trigger_count=2, trigger_delay=0.5)
        instrument.trigger()
        instrument.trigger()
        assert instrument.fetch() == [10.0, -20.0, 30.0, 40.0, 50.0, 60.0]


def test_fetch_uses_ascii_and_does_not_retrigger():
    # FORM:DATA persists and controls FETC? encoding; manual PDF pp. 260-261.
    with expected_protocol(
        Keysight34465A,
        [("FORM:DATA ASC", None), _NO_ERROR, ("FETC?", "+1E+0,-2E+0"), _NO_ERROR],
    ) as instrument:
        assert instrument.fetch() == [1.0, -2.0]


@pytest.mark.parametrize("response", ["", "1.0,not-a-number"])
def test_fetch_rejects_empty_or_malformed_reply(response):
    with expected_protocol(
        Keysight34465A, [("FORM:DATA ASC", None), _NO_ERROR, ("FETC?", response), _NO_ERROR]
    ) as instrument, pytest.raises(MeasurementError):
        instrument.fetch()


def test_acquire_rejects_partial_result():
    with expected_protocol(
        Keysight34465A,
        [
            *_checked_writes(
                "ABOR", "TRIG:SOUR IMM", "SAMP:COUN 3", "TRIG:COUN 1", "TRIG:DEL:AUTO ON", "INIT"
            ),
            ("FORM:DATA ASC", None),
            _NO_ERROR,
            ("FETC?", "1,2"),
            _NO_ERROR,
        ],
    ) as instrument, pytest.raises(MeasurementError, match="expected 3"):
        instrument.acquire(3)


def test_adapter_read_error_propagates():
    adapter = ProtocolAdapter(
        [
            ("FORM:DATA ASC", None),
            ("SYST:ERR?", "0,No error"),
            ("FETC?", "1"),
        ]
    )
    original_read = adapter._read

    def fail_fetch_read(**kwargs):
        if adapter._index == 3:
            raise OSError("transport failure")
        return original_read(**kwargs)

    adapter._read = fail_fetch_read
    instrument = Keysight34465A(adapter)

    with pytest.raises(OSError, match="transport failure"):
        instrument.fetch()


@pytest.mark.parametrize(
    ("method_name", "args", "kwargs"),
    [
        ("configure", ("unknown",), {}),
        ("configure", ("DCV",), {"range_": 0.5}),
        ("configure", ("CONT",), {"range_": 100.0}),
        ("configure", ("FREQ",), {"nplc": 1.0}),
        ("configure", ("DCV",), {"nplc": 0.5}),
        ("acquire", (True,), {}),
        ("acquire", (2.5,), {}),
        ("acquire", (50_001,), {}),
        ("acquire", (2,), {"trigger_delay": float("nan")}),
        ("arm", (2, 0), {}),
        ("arm", (2,), {"trigger_delay": float("inf")}),
    ],
)
def test_invalid_composite_arguments_do_not_write(method_name, args, kwargs):
    adapter = ProtocolAdapter([])
    instrument = Keysight34465A(adapter)

    with pytest.raises((TypeError, ValueError)):
        getattr(instrument, method_name)(*args, **kwargs)

    assert adapter._index == 0
    assert adapter._write_buffer is None


@pytest.mark.parametrize(
    ("property_name", "value"),
    [
        ("voltage_range", 0.5),
        ("sample_count", 1.5),
        ("trigger_count", 0),
        ("trigger_delay", float("nan")),
        ("display_enabled", 1),
        ("trigger_source", "INT"),
    ],
)
def test_invalid_control_values_do_not_write(property_name, value):
    adapter = ProtocolAdapter([])
    instrument = Keysight34465A(adapter)

    with pytest.raises((TypeError, ValueError)):
        setattr(instrument, property_name, value)

    assert adapter._index == 0
    assert adapter._write_buffer is None
