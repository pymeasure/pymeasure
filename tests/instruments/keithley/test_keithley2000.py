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

from pymeasure.instruments.keithley.keithley2000 import Keithley2000
from pymeasure.test import expected_protocol


@pytest.mark.parametrize(
    ("prop", "reply"),
    (("voltage", "3.1415"),
     ("current", "1.234"),
     ("resistance", "1234.5"),
     ("frequency", "50.0"),
     ("period", "0.02"),
     ("temperature", "25.5")),
)
def test_read_value(prop, reply):
    """Read properties all fetch their value via a plain ':READ?' query."""
    with expected_protocol(
        Keithley2000,
        [(":READ?", reply)],
    ) as inst:
        assert getattr(inst, prop) == pytest.approx(float(reply))


def test_voltage_range():
    with expected_protocol(
        Keithley2000,
        [(":SENS:VOLT:RANG?", "955"),
         (":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG 234", None)
         ],
    ) as inst:
        assert inst.voltage_range == 955
        inst.voltage_range = 234


def test_voltage_range_trunc():
    with expected_protocol(
        Keithley2000,
        [(":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG 1010", None),
         (":SENS:VOLT:RANG?", "1010"),
         ],
    ) as inst:
        inst.voltage_range = 3333  # too large, gets truncated
        assert inst.voltage_range == 1010


def test_mode():
    "Confirm that mode string mapping works correctly"
    with expected_protocol(
        Keithley2000,
        [(":CONF?", "VOLT:AC"),
         (":CONF:FRES", None),
         ],
    ) as inst:
        assert inst.mode == 'voltage ac'
        inst.mode = 'resistance 4W'


def test_measure_voltage():
    with expected_protocol(
        Keithley2000,
        [(":CONF:VOLT:AC", None),
         (":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:AC:RANG 300", None),
         ],
    ) as inst:
        inst.measure_voltage(max_voltage=300, ac=True)


def test_enable_filter():
    with expected_protocol(
        Keithley2000,
        [(":SENS:VOLT:AC:AVER:STAT 1", None),
         (":SENS:VOLT:AC:AVER:TCON repeat", None),
         (":SENS:VOLT:AC:AVER:COUN 10", None),
         ],
    ) as inst:
        inst.enable_filter(mode='voltage ac', type='repeat', count=10)


GET_SET_CASES = (
    # (property, sensor command, getter reply string, full set command, value to set)
    # --- current ---
    ("current_range",
     ":SENS:CURR:RANG", "0.5",
     ":SENS:CURR:RANG:AUTO 0;:SENS:CURR:RANG 1.5", 1.5),
    ("current_reference",
     ":SENS:CURR:REF", "-0.1",
     ":SENS:CURR:REF 0.2", 0.2),
    ("current_nplc",
     ":SENS:CURR:NPLC", "1",
     ":SENS:CURR:NPLC 5", 5),
    ("current_digits",
     ":SENS:CURR:DIG", "5",
     ":SENS:CURR:DIG 6", 6),
    # --- current ac ---
    ("current_ac_range",
     ":SENS:CURR:AC:RANG", "0.5",
     ":SENS:CURR:AC:RANG:AUTO 0;:SENS:CURR:AC:RANG 1.5", 1.5),
    ("current_ac_reference",
     ":SENS:CURR:AC:REF", "-0.1",
     ":SENS:CURR:AC:REF 0.2", 0.2),
    ("current_ac_nplc",
     ":SENS:CURR:AC:NPLC", "1",
     ":SENS:CURR:AC:NPLC 5", 5),
    ("current_ac_digits",
     ":SENS:CURR:AC:DIG", "5",
     ":SENS:CURR:AC:DIG 6", 6),
    # --- voltage ---
    ("voltage_reference",
     ":SENS:VOLT:REF", "-10",
     ":SENS:VOLT:REF 5", 5),
    ("voltage_nplc",
     ":SENS:VOLT:NPLC", "1",
     ":SENS:VOLT:NPLC 5", 5),
    ("voltage_digits",
     ":SENS:VOLT:DIG", "5",
     ":SENS:VOLT:DIG 6", 6),
    # --- voltage ac ---
    ("voltage_ac_range",
     ":SENS:VOLT:AC:RANG", "100",
     # NOTE: the auto-range-off prefix is *not* under the AC subnode here.
     ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:AC:RANG 200", 200),
    ("voltage_ac_reference",
     ":SENS:VOLT:AC:REF", "-10",
     ":SENS:VOLT:AC:REF 5", 5),
    ("voltage_ac_nplc",
     ":SENS:VOLT:AC:NPLC", "1",
     ":SENS:VOLT:AC:NPLC 5", 5),
    ("voltage_ac_digits",
     ":SENS:VOLT:AC:DIG", "5",
     ":SENS:VOLT:AC:DIG 6", 6),
    # --- resistance ---
    ("resistance_range",
     ":SENS:RES:RANG", "1000",
     ":SENS:RES:RANG:AUTO 0;:SENS:RES:RANG 1e+06", 1e6),
    ("resistance_reference",
     ":SENS:RES:REF", "100",
     ":SENS:RES:REF 200", 200),
    ("resistance_nplc",
     ":SENS:RES:NPLC", "1",
     ":SENS:RES:NPLC 5", 5),
    ("resistance_digits",
     ":SENS:RES:DIG", "5",
     ":SENS:RES:DIG 6", 6),
    # --- 4-wire resistance ---
    ("resistance_4W_range",
     ":SENS:FRES:RANG", "1000",
     ":SENS:FRES:RANG:AUTO 0;:SENS:FRES:RANG 1e+06", 1e6),
    ("resistance_4W_reference",
     ":SENS:FRES:REF", "100",
     ":SENS:FRES:REF 200", 200),
    ("resistance_4W_nplc",
     ":SENS:FRES:NPLC", "1",
     ":SENS:FRES:NPLC 5", 5),
    ("resistance_4W_digits",
     ":SENS:FRES:DIG", "5",
     ":SENS:FRES:DIG 6", 6),
    # --- frequency ---
    ("frequency_reference",
     ":SENS:FREQ:REF", "1000",
     ":SENS:FREQ:REF 2000", 2000),
    ("frequency_digits",
     ":SENS:FREQ:DIG", "5",
     ":SENS:FREQ:DIG 6", 6),
    ("frequency_threshold",
     ":SENS:FREQ:THR:VOLT:RANG", "1",
     ":SENS:FREQ:THR:VOLT:RANG 5", 5),
    ("frequency_aperature",
     ":SENS:FREQ:APER", "0.1",
     ":SENS:FREQ:APER 0.5", 0.5),
    # --- period ---
    ("period_reference",
     ":SENS:PER:REF", "0.01",
     ":SENS:PER:REF 0.05", 0.05),
    ("period_digits",
     ":SENS:PER:DIG", "5",
     ":SENS:PER:DIG 6", 6),
    ("period_threshold",
     ":SENS:PER:THR:VOLT:RANG", "1",
     ":SENS:PER:THR:VOLT:RANG 5", 5),
    ("period_aperature",
     ":SENS:PER:APER", "0.1",
     ":SENS:PER:APER 0.5", 0.5),
    # --- temperature ---
    ("temperature_reference",
     ":SENS:TEMP:REF", "20",
     ":SENS:TEMP:REF 25", 25),
    ("temperature_nplc",
     ":SENS:TEMP:NPLC", "1",
     ":SENS:TEMP:NPLC 5", 5),
    ("temperature_digits",
     ":SENS:TEMP:DIG", "5",
     ":SENS:TEMP:DIG 6", 6),
    # --- trigger ---
    ("trigger_count",
     ":TRIG:COUN", "5",
     ":TRIG:COUN 10", 10),
    ("trigger_delay",
     ":TRIG:SEQ:DEL", "0.1",
     ":TRIG:SEQ:DEL 0.5", 0.5),
)


@pytest.mark.parametrize(("prop", "command", "reply", "set_command", "value"),
                         GET_SET_CASES, ids=[row[0] for row in GET_SET_CASES])
def test_get_and_set(prop, command, reply, set_command, value):
    """Get and set a sensor property; protocol strings are pinned byte-exact.

    The getter queries ``<command>?`` and expects ``reply``; the setter writes
    the full ``set_command`` string (which sometimes differs from
    ``<command> <value>``, e.g. where the auto-range-off prefix is coupled to
    the range write).
    """
    with expected_protocol(
        Keithley2000,
        [(f"{command}?", reply), (set_command, None)],
    ) as inst:
        assert getattr(inst, prop) == pytest.approx(float(reply))
        setattr(inst, prop, value)


@pytest.mark.parametrize(("prop", "command"), (
    ("current_ac_bandwidth", ":SENS:CURR:AC:DET:BAND"),
    ("voltage_ac_bandwidth", ":SENS:VOLT:AC:DET:BAND"),
))
@pytest.mark.parametrize("value", (3, 30, 300))
def test_ac_bandwidth(prop, command, value):
    """AC bandwidth accepts the discrete 3/30/300 Hz detector bandwidths."""
    with expected_protocol(
        Keithley2000,
        [(f"{command}?", f"{value}"),
         (f"{command} {value}", None),
         ],
    ) as inst:
        assert getattr(inst, prop) == value
        setattr(inst, prop, value)


def test_beep_state():
    with expected_protocol(
        Keithley2000,
        [(":SYST:BEEP:STAT?", "1"),
         (":SYST:BEEP:STAT 0", None),
         ],
    ) as inst:
        assert inst.beep_state == 'enabled'
        inst.beep_state = 'disabled'


def test_measure_current_dc():
    with expected_protocol(
        Keithley2000,
        [(":CONF:CURR:DC", None),
         (":SENS:CURR:RANG:AUTO 0;:SENS:CURR:RANG 0.1", None),
         ],
    ) as inst:
        inst.measure_current(max_current=0.1, ac=False)


def test_measure_current_ac():
    with expected_protocol(
        Keithley2000,
        [(":CONF:CURR:AC", None),
         (":SENS:CURR:AC:RANG:AUTO 0;:SENS:CURR:AC:RANG 0.1", None),
         ],
    ) as inst:
        inst.measure_current(max_current=0.1, ac=True)


def test_measure_resistance_2wire():
    with expected_protocol(
        Keithley2000,
        [(":CONF:RES", None),
         (":SENS:RES:RANG:AUTO 0;:SENS:RES:RANG 1e+06", None),
         ],
    ) as inst:
        inst.measure_resistance(max_resistance=1e6, wires=2)


def test_measure_resistance_4wire():
    with expected_protocol(
        Keithley2000,
        [(":CONF:FRES", None),
         (":SENS:FRES:RANG:AUTO 0;:SENS:FRES:RANG 1e+06", None),
         ],
    ) as inst:
        inst.measure_resistance(max_resistance=1e6, wires=4)


def test_measure_resistance_invalid_wires():
    with pytest.raises(ValueError), expected_protocol(
        Keithley2000,
        [],
    ) as inst:
        inst.measure_resistance(wires=3)


def test_measure_period():
    with expected_protocol(
        Keithley2000,
        [(":CONF:PER", None)],
    ) as inst:
        inst.measure_period()


def test_measure_frequency():
    with expected_protocol(
        Keithley2000,
        [(":CONF:FREQ", None)],
    ) as inst:
        inst.measure_frequency()


def test_measure_temperature():
    with expected_protocol(
        Keithley2000,
        [(":CONF:TEMP", None)],
    ) as inst:
        inst.measure_temperature()


def test_measure_diode():
    with expected_protocol(
        Keithley2000,
        [(":CONF:DIOD", None)],
    ) as inst:
        inst.measure_diode()


def test_measure_continuity():
    with expected_protocol(
        Keithley2000,
        [(":CONF:CONT", None)],
    ) as inst:
        inst.measure_continuity()


def test_auto_range_active_mode():
    with expected_protocol(
        Keithley2000,
        [(":CONF?", "VOLT:DC"),
         (":SENS:VOLT:DC:RANG:AUTO 1", None),
         ],
    ) as inst:
        inst.auto_range()


def test_auto_range_explicit_mode():
    with expected_protocol(
        Keithley2000,
        [(":SENS:CURR:DC:RANG:AUTO 1", None)],
    ) as inst:
        inst.auto_range(mode='current')


def test_enable_reference_active_mode():
    with expected_protocol(
        Keithley2000,
        [(":CONF?", "VOLT:DC"),
         (":SENS:VOLT:DC:REF:STAT 1", None),
         ],
    ) as inst:
        inst.enable_reference()


def test_enable_reference_explicit_mode():
    with expected_protocol(
        Keithley2000,
        [(":SENS:CURR:DC:REF:STAT 1", None)],
    ) as inst:
        inst.enable_reference(mode='current')


def test_disable_reference_active_mode():
    with expected_protocol(
        Keithley2000,
        [(":CONF?", "VOLT:DC"),
         (":SENS:VOLT:DC:REF:STAT 0", None),
         ],
    ) as inst:
        inst.disable_reference()


def test_disable_reference_explicit_mode():
    with expected_protocol(
        Keithley2000,
        [(":SENS:CURR:DC:REF:STAT 0", None)],
    ) as inst:
        inst.disable_reference(mode='current')


def test_acquire_reference_active_mode():
    with expected_protocol(
        Keithley2000,
        [(":CONF?", "VOLT:DC"),
         (":SENS:VOLT:DC:REF:ACQ", None),
         ],
    ) as inst:
        inst.acquire_reference()


def test_acquire_reference_explicit_mode():
    with expected_protocol(
        Keithley2000,
        [(":SENS:CURR:DC:REF:ACQ", None)],
    ) as inst:
        inst.acquire_reference(mode='current')


def test_disable_filter_active_mode():
    with expected_protocol(
        Keithley2000,
        [(":CONF?", "VOLT:DC"),
         (":SENS:VOLT:DC:AVER:STAT 0", None),
         ],
    ) as inst:
        inst.disable_filter()


def test_disable_filter_explicit_mode():
    with expected_protocol(
        Keithley2000,
        [(":SENS:CURR:DC:AVER:STAT 0", None)],
    ) as inst:
        inst.disable_filter(mode='current')


def test_local():
    with expected_protocol(
        Keithley2000,
        [(":SYST:LOC", None)],
    ) as inst:
        inst.local()


def test_remote():
    with expected_protocol(
        Keithley2000,
        [(":SYST:REM", None)],
    ) as inst:
        inst.remote()


def test_remote_lock():
    with expected_protocol(
        Keithley2000,
        [(":SYST:RWL", None)],
    ) as inst:
        inst.remote_lock()


def test_reset():
    with expected_protocol(
        Keithley2000,
        [(":STAT:QUEUE:CLEAR;*RST;:STAT:PRES;:*CLS;", None)],
    ) as inst:
        inst.reset()


def test_beep():
    with expected_protocol(
        Keithley2000,
        [(":SYST:BEEP 1000, 0.5", None)],
    ) as inst:
        inst.beep(1000, 0.5)
