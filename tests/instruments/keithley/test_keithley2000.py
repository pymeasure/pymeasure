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
from pymeasure.instruments.keithley.keithley2000 import Keithley2000


def test_voltage_read():
    with expected_protocol(
        Keithley2000,
        [(":READ?", "3.1415")],
    ) as inst:
        assert inst.voltage == pytest.approx(3.1415)


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


def test_current_read():
    with expected_protocol(
        Keithley2000,
        [(":READ?", "1.234")],
    ) as inst:
        assert inst.current == pytest.approx(1.234)


def test_current_range():
    with expected_protocol(
        Keithley2000,
        [(":SENS:CURR:RANG?", "0.5"),
         (":SENS:CURR:RANG:AUTO 0;:SENS:CURR:RANG 1.5", None),
         ],
    ) as inst:
        assert inst.current_range == pytest.approx(0.5)
        inst.current_range = 1.5


def test_current_reference():
    with expected_protocol(
        Keithley2000,
        [(":SENS:CURR:REF?", "-0.1"),
         (":SENS:CURR:REF 0.2", None),
         ],
    ) as inst:
        assert inst.current_reference == pytest.approx(-0.1)
        inst.current_reference = 0.2


def test_current_nplc():
    with expected_protocol(
        Keithley2000,
        [(":SENS:CURR:NPLC?", "1"),
         (":SENS:CURR:NPLC 5", None),
         ],
    ) as inst:
        assert inst.current_nplc == pytest.approx(1)
        inst.current_nplc = 5


def test_current_digits():
    with expected_protocol(
        Keithley2000,
        [(":SENS:CURR:DIG?", "5"),
         (":SENS:CURR:DIG 6", None),
         ],
    ) as inst:
        assert inst.current_digits == 5
        inst.current_digits = 6


def test_current_ac_range():
    with expected_protocol(
        Keithley2000,
        [(":SENS:CURR:AC:RANG?", "0.5"),
         (":SENS:CURR:AC:RANG:AUTO 0;:SENS:CURR:AC:RANG 1.5", None),
         ],
    ) as inst:
        assert inst.current_ac_range == pytest.approx(0.5)
        inst.current_ac_range = 1.5


def test_current_ac_reference():
    with expected_protocol(
        Keithley2000,
        [(":SENS:CURR:AC:REF?", "-0.1"),
         (":SENS:CURR:AC:REF 0.2", None),
         ],
    ) as inst:
        assert inst.current_ac_reference == pytest.approx(-0.1)
        inst.current_ac_reference = 0.2


def test_current_ac_nplc():
    with expected_protocol(
        Keithley2000,
        [(":SENS:CURR:AC:NPLC?", "1"),
         (":SENS:CURR:AC:NPLC 5", None),
         ],
    ) as inst:
        assert inst.current_ac_nplc == pytest.approx(1)
        inst.current_ac_nplc = 5


def test_current_ac_digits():
    with expected_protocol(
        Keithley2000,
        [(":SENS:CURR:AC:DIG?", "5"),
         (":SENS:CURR:AC:DIG 6", None),
         ],
    ) as inst:
        assert inst.current_ac_digits == 5
        inst.current_ac_digits = 6


@pytest.mark.parametrize("value", [3, 30, 300])
def test_current_ac_bandwidth(value):
    with expected_protocol(
        Keithley2000,
        [(":SENS:CURR:AC:DET:BAND?", f"{value}"),
         (f":SENS:CURR:AC:DET:BAND {value}", None),
         ],
    ) as inst:
        assert inst.current_ac_bandwidth == value
        inst.current_ac_bandwidth = value


def test_voltage_reference():
    with expected_protocol(
        Keithley2000,
        [(":SENS:VOLT:REF?", "-10"),
         (":SENS:VOLT:REF 5", None),
         ],
    ) as inst:
        assert inst.voltage_reference == pytest.approx(-10)
        inst.voltage_reference = 5


def test_voltage_nplc():
    with expected_protocol(
        Keithley2000,
        [(":SENS:VOLT:NPLC?", "1"),
         (":SENS:VOLT:NPLC 5", None),
         ],
    ) as inst:
        assert inst.voltage_nplc == pytest.approx(1)
        inst.voltage_nplc = 5


def test_voltage_digits():
    with expected_protocol(
        Keithley2000,
        [(":SENS:VOLT:DIG?", "5"),
         (":SENS:VOLT:DIG 6", None),
         ],
    ) as inst:
        assert inst.voltage_digits == 5
        inst.voltage_digits = 6


def test_voltage_ac_range():
    with expected_protocol(
        Keithley2000,
        [(":SENS:VOLT:AC:RANG?", "100"),
         (":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:AC:RANG 200", None),
         ],
    ) as inst:
        assert inst.voltage_ac_range == pytest.approx(100)
        inst.voltage_ac_range = 200


def test_voltage_ac_reference():
    with expected_protocol(
        Keithley2000,
        [(":SENS:VOLT:AC:REF?", "-10"),
         (":SENS:VOLT:AC:REF 5", None),
         ],
    ) as inst:
        assert inst.voltage_ac_reference == pytest.approx(-10)
        inst.voltage_ac_reference = 5


def test_voltage_ac_nplc():
    with expected_protocol(
        Keithley2000,
        [(":SENS:VOLT:AC:NPLC?", "1"),
         (":SENS:VOLT:AC:NPLC 5", None),
         ],
    ) as inst:
        assert inst.voltage_ac_nplc == pytest.approx(1)
        inst.voltage_ac_nplc = 5


def test_voltage_ac_digits():
    with expected_protocol(
        Keithley2000,
        [(":SENS:VOLT:AC:DIG?", "5"),
         (":SENS:VOLT:AC:DIG 6", None),
         ],
    ) as inst:
        assert inst.voltage_ac_digits == 5
        inst.voltage_ac_digits = 6


@pytest.mark.parametrize("value", [3, 30, 300])
def test_voltage_ac_bandwidth(value):
    with expected_protocol(
        Keithley2000,
        [(":SENS:VOLT:AC:DET:BAND?", f"{value}"),
         (f":SENS:VOLT:AC:DET:BAND {value}", None),
         ],
    ) as inst:
        assert inst.voltage_ac_bandwidth == value
        inst.voltage_ac_bandwidth = value


def test_resistance_read():
    with expected_protocol(
        Keithley2000,
        [(":READ?", "1234.5")],
    ) as inst:
        assert inst.resistance == pytest.approx(1234.5)


def test_resistance_range():
    with expected_protocol(
        Keithley2000,
        [(":SENS:RES:RANG?", "1000"),
         (":SENS:RES:RANG:AUTO 0;:SENS:RES:RANG 1e+06", None),
         ],
    ) as inst:
        assert inst.resistance_range == pytest.approx(1000)
        inst.resistance_range = 1e6


def test_resistance_reference():
    with expected_protocol(
        Keithley2000,
        [(":SENS:RES:REF?", "100"),
         (":SENS:RES:REF 200", None),
         ],
    ) as inst:
        assert inst.resistance_reference == pytest.approx(100)
        inst.resistance_reference = 200


def test_resistance_nplc():
    with expected_protocol(
        Keithley2000,
        [(":SENS:RES:NPLC?", "1"),
         (":SENS:RES:NPLC 5", None),
         ],
    ) as inst:
        assert inst.resistance_nplc == pytest.approx(1)
        inst.resistance_nplc = 5


def test_resistance_digits():
    with expected_protocol(
        Keithley2000,
        [(":SENS:RES:DIG?", "5"),
         (":SENS:RES:DIG 6", None),
         ],
    ) as inst:
        assert inst.resistance_digits == 5
        inst.resistance_digits = 6


def test_resistance_4W_range():
    with expected_protocol(
        Keithley2000,
        [(":SENS:FRES:RANG?", "1000"),
         (":SENS:FRES:RANG:AUTO 0;:SENS:FRES:RANG 1e+06", None),
         ],
    ) as inst:
        assert inst.resistance_4W_range == pytest.approx(1000)
        inst.resistance_4W_range = 1e6


def test_resistance_4W_reference():
    with expected_protocol(
        Keithley2000,
        [(":SENS:FRES:REF?", "100"),
         (":SENS:FRES:REF 200", None),
         ],
    ) as inst:
        assert inst.resistance_4W_reference == pytest.approx(100)
        inst.resistance_4W_reference = 200


def test_resistance_4W_nplc():
    with expected_protocol(
        Keithley2000,
        [(":SENS:FRES:NPLC?", "1"),
         (":SENS:FRES:NPLC 5", None),
         ],
    ) as inst:
        assert inst.resistance_4W_nplc == pytest.approx(1)
        inst.resistance_4W_nplc = 5


def test_resistance_4W_digits():
    with expected_protocol(
        Keithley2000,
        [(":SENS:FRES:DIG?", "5"),
         (":SENS:FRES:DIG 6", None),
         ],
    ) as inst:
        assert inst.resistance_4W_digits == 5
        inst.resistance_4W_digits = 6


def test_frequency_read():
    with expected_protocol(
        Keithley2000,
        [(":READ?", "50.0")],
    ) as inst:
        assert inst.frequency == pytest.approx(50.0)


def test_frequency_reference():
    with expected_protocol(
        Keithley2000,
        [(":SENS:FREQ:REF?", "1000"),
         (":SENS:FREQ:REF 2000", None),
         ],
    ) as inst:
        assert inst.frequency_reference == pytest.approx(1000)
        inst.frequency_reference = 2000


def test_frequency_digits():
    with expected_protocol(
        Keithley2000,
        [(":SENS:FREQ:DIG?", "5"),
         (":SENS:FREQ:DIG 6", None),
         ],
    ) as inst:
        assert inst.frequency_digits == 5
        inst.frequency_digits = 6


def test_frequency_threshold():
    with expected_protocol(
        Keithley2000,
        [(":SENS:FREQ:THR:VOLT:RANG?", "1"),
         (":SENS:FREQ:THR:VOLT:RANG 5", None),
         ],
    ) as inst:
        assert inst.frequency_threshold == pytest.approx(1)
        inst.frequency_threshold = 5


def test_frequency_aperature():
    with expected_protocol(
        Keithley2000,
        [(":SENS:FREQ:APER?", "0.1"),
         (":SENS:FREQ:APER 0.5", None),
         ],
    ) as inst:
        assert inst.frequency_aperature == pytest.approx(0.1)
        inst.frequency_aperature = 0.5


def test_period_read():
    with expected_protocol(
        Keithley2000,
        [(":READ?", "0.02")],
    ) as inst:
        assert inst.period == pytest.approx(0.02)


def test_period_reference():
    with expected_protocol(
        Keithley2000,
        [(":SENS:PER:REF?", "0.01"),
         (":SENS:PER:REF 0.05", None),
         ],
    ) as inst:
        assert inst.period_reference == pytest.approx(0.01)
        inst.period_reference = 0.05


def test_period_digits():
    with expected_protocol(
        Keithley2000,
        [(":SENS:PER:DIG?", "5"),
         (":SENS:PER:DIG 6", None),
         ],
    ) as inst:
        assert inst.period_digits == 5
        inst.period_digits = 6


def test_period_threshold():
    with expected_protocol(
        Keithley2000,
        [(":SENS:PER:THR:VOLT:RANG?", "1"),
         (":SENS:PRE:THR:VOLT:RANG 5", None),
         ],
    ) as inst:
        assert inst.period_threshold == pytest.approx(1)
        inst.period_threshold = 5


def test_period_aperature():
    with expected_protocol(
        Keithley2000,
        [(":SENS:PER:APER?", "0.1"),
         (":SENS:PER:APER 0.5", None),
         ],
    ) as inst:
        assert inst.period_aperature == pytest.approx(0.1)
        inst.period_aperature = 0.5


def test_temperature_read():
    with expected_protocol(
        Keithley2000,
        [(":READ?", "25.5")],
    ) as inst:
        assert inst.temperature == pytest.approx(25.5)


def test_temperature_reference():
    with expected_protocol(
        Keithley2000,
        [(":SENS:TEMP:REF?", "20"),
         (":SENS:TEMP:REF 25", None),
         ],
    ) as inst:
        assert inst.temperature_reference == pytest.approx(20)
        inst.temperature_reference = 25


def test_temperature_nplc():
    with expected_protocol(
        Keithley2000,
        [(":SENS:TEMP:NPLC?", "1"),
         (":SENS:TEMP:NPLC 5", None),
         ],
    ) as inst:
        assert inst.temperature_nplc == pytest.approx(1)
        inst.temperature_nplc = 5


def test_temperature_digits():
    with expected_protocol(
        Keithley2000,
        [(":SENS:TEMP:DIG?", "5"),
         (":SENS:TEMP:DIG 6", None),
         ],
    ) as inst:
        assert inst.temperature_digits == 5
        inst.temperature_digits = 6


def test_trigger_count():
    with expected_protocol(
        Keithley2000,
        [(":TRIG:COUN?", "5"),
         (":TRIG:COUN 10", None),
         ],
    ) as inst:
        assert inst.trigger_count == 5
        inst.trigger_count = 10


def test_trigger_delay():
    with expected_protocol(
        Keithley2000,
        [(":TRIG:SEQ:DEL?", "0.1"),
         (":TRIG:SEQ:DEL 0.5", None),
         ],
    ) as inst:
        assert inst.trigger_delay == pytest.approx(0.1)
        inst.trigger_delay = 0.5


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
    with pytest.raises(ValueError):
        with expected_protocol(
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
