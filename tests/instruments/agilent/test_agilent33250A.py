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

import math

import pytest

from pymeasure.instruments.agilent.agilent33250A import Agilent33250A
from pymeasure.test import expected_protocol


@pytest.mark.parametrize("shape", ["SIN", "SQU", "RAMP", "PULS", "NOIS", "DC", "USER"])
def test_shape(shape):
    with expected_protocol(
        Agilent33250A,
        [("FUNC?", shape), (f"FUNC {shape}", None)],
    ) as inst:
        assert inst.shape == shape
        inst.shape = shape


@pytest.mark.parametrize("frequency, expected", [(1e-6, "1e-06"), (80e6, "8e+07")])
def test_frequency(frequency, expected):
    with expected_protocol(
        Agilent33250A,
        [("FREQ?", frequency), (f"FREQ {expected}", None)],
    ) as inst:
        assert inst.frequency == frequency
        inst.frequency = frequency


def test_frequency_out_of_range():
    with expected_protocol(Agilent33250A, []) as inst:
        with pytest.raises(ValueError):
            inst.frequency = 80e6 + 1


@pytest.mark.parametrize("amplitude, expected", [(1e-3, "0.001000"), (10, "10.000000")])
def test_amplitude(amplitude, expected):
    with expected_protocol(
        Agilent33250A,
        [("VOLT?", amplitude), (f"VOLT {expected}", None)],
    ) as inst:
        assert inst.amplitude == amplitude
        inst.amplitude = amplitude


@pytest.mark.parametrize("amplitude_unit", ["VPP", "VRMS", "DBM"])
def test_amplitude_unit(amplitude_unit):
    with expected_protocol(
        Agilent33250A,
        [("VOLT:UNIT?", amplitude_unit), (f"VOLT:UNIT {amplitude_unit}", None)],
    ) as inst:
        assert inst.amplitude_unit == amplitude_unit
        inst.amplitude_unit = amplitude_unit


def test_amplitude_unit_invalid():
    with expected_protocol(Agilent33250A, []) as inst:
        with pytest.raises(ValueError):
            inst.amplitude_unit = "VPK"


@pytest.mark.parametrize("offset, expected", [(-5, "-5.000000"), (5, "5.000000")])
def test_offset(offset, expected):
    with expected_protocol(
        Agilent33250A,
        [("VOLT:OFFS?", offset), (f"VOLT:OFFS {expected}", None)],
    ) as inst:
        assert inst.offset == offset
        inst.offset = offset


@pytest.mark.parametrize("value, expected", [(-5, "-5.000000"), (5, "5.000000")])
def test_voltage_high(value, expected):
    with expected_protocol(
        Agilent33250A,
        [("VOLT:HIGH?", value), (f"VOLT:HIGH {expected}", None)],
    ) as inst:
        assert inst.voltage_high == value
        inst.voltage_high = value


@pytest.mark.parametrize("value, expected", [(-5, "-5.000000"), (5, "5.000000")])
def test_voltage_low(value, expected):
    with expected_protocol(
        Agilent33250A,
        [("VOLT:LOW?", value), (f"VOLT:LOW {expected}", None)],
    ) as inst:
        assert inst.voltage_low == value
        inst.voltage_low = value


@pytest.mark.parametrize("state, as_int", [(True, 1), (False, 0)])
def test_output_enabled(state, as_int):
    with expected_protocol(
        Agilent33250A,
        [("OUTP?", as_int), (f"OUTP {as_int}", None)],
    ) as inst:
        assert inst.output_enabled is state
        inst.output_enabled = state


@pytest.mark.parametrize("value, response, expected_value", [
    (50, 50, 50.0),
    (10000, 10000, 10000.0),
    ("INF", "INF", float("inf")),
])
def test_output_load(value, response, expected_value):
    with expected_protocol(
        Agilent33250A,
        [("OUTP:LOAD?", response), (f"OUTP:LOAD {('INF' if value == 'INF' else value)}", None)],
    ) as inst:
        measured = inst.output_load
        if math.isinf(expected_value):
            assert math.isinf(measured)
        else:
            assert measured == expected_value
        inst.output_load = value


@pytest.mark.parametrize("value", ["INF", "INFINITY", float("inf")])
def test_output_load_inf_aliases(value):
    with expected_protocol(
        Agilent33250A,
        [("OUTP:LOAD INF", None)],
    ) as inst:
        inst.output_load = value


def test_output_load_inf_like_response():
    with expected_protocol(
        Agilent33250A,
        [("OUTP:LOAD?", "9.9E37")],
    ) as inst:
        assert math.isinf(inst.output_load)


def test_output_load_out_of_range():
    with expected_protocol(Agilent33250A, []) as inst:
        with pytest.raises(ValueError):
            inst.output_load = 0


@pytest.mark.parametrize("polarity", ["NORM", "INV"])
def test_output_polarity(polarity):
    with expected_protocol(
        Agilent33250A,
        [("OUTP:POL?", polarity), (f"OUTP:POL {polarity}", None)],
    ) as inst:
        assert inst.output_polarity == polarity
        inst.output_polarity = polarity


def test_output_polarity_invalid():
    with expected_protocol(Agilent33250A, []) as inst:
        with pytest.raises(ValueError):
            inst.output_polarity = "INVALID"


@pytest.mark.parametrize("state, as_int", [(True, 1), (False, 0)])
def test_sync_output_enabled(state, as_int):
    with expected_protocol(
        Agilent33250A,
        [("OUTP:SYNC?", as_int), (f"OUTP:SYNC {as_int}", None)],
    ) as inst:
        assert inst.sync_output_enabled is state
        inst.sync_output_enabled = state


@pytest.mark.parametrize("square_dutycycle, expected", [(20, "20"), (80, "80")])
def test_square_dutycycle(square_dutycycle, expected):
    with expected_protocol(
        Agilent33250A,
        [("FUNC:SQU:DCYC?", square_dutycycle), (f"FUNC:SQU:DCYC {expected}", None)],
    ) as inst:
        assert inst.square_dutycycle == square_dutycycle
        inst.square_dutycycle = square_dutycycle


def test_square_dutycycle_out_of_range():
    with expected_protocol(Agilent33250A, []) as inst:
        with pytest.raises(ValueError):
            inst.square_dutycycle = 19.999


@pytest.mark.parametrize("ramp_symmetry, expected", [(0, "0.000000"), (100, "100.000000")])
def test_ramp_symmetry(ramp_symmetry, expected):
    with expected_protocol(
        Agilent33250A,
        [("FUNC:RAMP:SYMM?", ramp_symmetry), (f"FUNC:RAMP:SYMM {expected}", None)],
    ) as inst:
        assert inst.ramp_symmetry == ramp_symmetry
        inst.ramp_symmetry = ramp_symmetry


@pytest.mark.parametrize("pulse_period, expected", [(20e-9, "2e-08"), (2000, "2000")])
def test_pulse_period(pulse_period, expected):
    with expected_protocol(
        Agilent33250A,
        [("PULS:PER?", pulse_period), (f"PULS:PER {expected}", None)],
    ) as inst:
        assert inst.pulse_period == pulse_period
        inst.pulse_period = pulse_period


def test_pulse_period_out_of_range():
    with expected_protocol(Agilent33250A, []) as inst:
        with pytest.raises(ValueError):
            inst.pulse_period = 10e-9


@pytest.mark.parametrize("pulse_width, expected", [(8e-9, "8e-09"), (2000, "2000")])
def test_pulse_width(pulse_width, expected):
    with expected_protocol(
        Agilent33250A,
        [("PULS:WIDT?", pulse_width), (f"PULS:WIDT {expected}", None)],
    ) as inst:
        assert inst.pulse_width == pulse_width
        inst.pulse_width = pulse_width


def test_pulse_width_out_of_range():
    with expected_protocol(Agilent33250A, []) as inst:
        with pytest.raises(ValueError):
            inst.pulse_width = 7e-9


@pytest.mark.parametrize("pulse_transition, expected", [(5e-9, "5e-09"), (1e-3, "0.001")])
def test_pulse_transition(pulse_transition, expected):
    with expected_protocol(
        Agilent33250A,
        [("PULS:TRAN?", pulse_transition), (f"PULS:TRAN {expected}", None)],
    ) as inst:
        assert inst.pulse_transition == pulse_transition
        inst.pulse_transition = pulse_transition


def test_pulse_transition_out_of_range():
    with expected_protocol(Agilent33250A, []) as inst:
        with pytest.raises(ValueError):
            inst.pulse_transition = 1.1e-3


@pytest.mark.parametrize("state, as_int", [(True, 1), (False, 0)])
def test_burst_enabled(state, as_int):
    with expected_protocol(
        Agilent33250A,
        [("BURS:STAT?", as_int), (f"BURS:STAT {as_int}", None)],
    ) as inst:
        assert inst.burst_enabled is state
        inst.burst_enabled = state


@pytest.mark.parametrize("burst_mode", ["TRIG", "GAT"])
def test_burst_mode(burst_mode):
    with expected_protocol(
        Agilent33250A,
        [("BURS:MODE?", burst_mode), (f"BURS:MODE {burst_mode}", None)],
    ) as inst:
        assert inst.burst_mode == burst_mode
        inst.burst_mode = burst_mode


def test_burst_mode_invalid():
    with expected_protocol(Agilent33250A, []) as inst:
        with pytest.raises(ValueError):
            inst.burst_mode = "UNKNOWN"


@pytest.mark.parametrize("value, response, expected_value", [
    (1, "1", 1),
    (1_000_000, "1000000", 1_000_000),
    ("INF", "INF", "INF"),
])
def test_burst_ncycles(value, response, expected_value):
    command_value = "INF" if value == "INF" else str(value)
    with expected_protocol(
        Agilent33250A,
        [("BURS:NCYC?", response), (f"BURS:NCYC {command_value}", None)],
    ) as inst:
        assert inst.burst_ncycles == expected_value
        inst.burst_ncycles = value


@pytest.mark.parametrize("value", ["INF", "INFINITY", float("inf")])
def test_burst_ncycles_inf_aliases(value):
    with expected_protocol(
        Agilent33250A,
        [("BURS:NCYC INF", None)],
    ) as inst:
        inst.burst_ncycles = value


def test_burst_ncycles_inf_like_response():
    with expected_protocol(
        Agilent33250A,
        [("BURS:NCYC?", "9.9E37")],
    ) as inst:
        assert inst.burst_ncycles == "INF"


def test_burst_ncycles_out_of_range():
    with expected_protocol(Agilent33250A, []) as inst:
        with pytest.raises(ValueError):
            inst.burst_ncycles = 0


@pytest.mark.parametrize("burst_period, expected", [(1e-6, "1e-06"), (500, "500")])
def test_burst_period(burst_period, expected):
    with expected_protocol(
        Agilent33250A,
        [("BURS:INT:PER?", burst_period), (f"BURS:INT:PER {expected}", None)],
    ) as inst:
        assert inst.burst_period == burst_period
        inst.burst_period = burst_period


def test_burst_period_out_of_range():
    with expected_protocol(Agilent33250A, []) as inst:
        with pytest.raises(ValueError):
            inst.burst_period = 500.001


@pytest.mark.parametrize("burst_phase, expected", [(-360, "-360"), (360, "360")])
def test_burst_phase(burst_phase, expected):
    with expected_protocol(
        Agilent33250A,
        [("BURS:PHAS?", burst_phase), (f"BURS:PHAS {expected}", None)],
    ) as inst:
        assert inst.burst_phase == burst_phase
        inst.burst_phase = burst_phase


def test_burst_phase_out_of_range():
    with expected_protocol(Agilent33250A, []) as inst:
        with pytest.raises(ValueError):
            inst.burst_phase = 360.1


@pytest.mark.parametrize("trigger_source", ["IMM", "EXT", "BUS"])
def test_trigger_source(trigger_source):
    with expected_protocol(
        Agilent33250A,
        [("TRIG:SOUR?", trigger_source), (f"TRIG:SOUR {trigger_source}", None)],
    ) as inst:
        assert inst.trigger_source == trigger_source
        inst.trigger_source = trigger_source


@pytest.mark.parametrize("trigger_delay, expected", [(0, "0"), (85, "85")])
def test_trigger_delay(trigger_delay, expected):
    with expected_protocol(
        Agilent33250A,
        [("TRIG:DEL?", trigger_delay), (f"TRIG:DEL {expected}", None)],
    ) as inst:
        assert inst.trigger_delay == trigger_delay
        inst.trigger_delay = trigger_delay


def test_trigger_delay_out_of_range():
    with expected_protocol(Agilent33250A, []) as inst:
        with pytest.raises(ValueError):
            inst.trigger_delay = -1


@pytest.mark.parametrize("trigger_slope", ["POS", "NEG"])
def test_trigger_slope(trigger_slope):
    with expected_protocol(
        Agilent33250A,
        [("TRIG:SLOP?", trigger_slope), (f"TRIG:SLOP {trigger_slope}", None)],
    ) as inst:
        assert inst.trigger_slope == trigger_slope
        inst.trigger_slope = trigger_slope


def test_trigger_slope_invalid():
    with expected_protocol(Agilent33250A, []) as inst:
        with pytest.raises(ValueError):
            inst.trigger_slope = "RISING"


@pytest.mark.parametrize("state, as_int", [(True, 1), (False, 0)])
def test_trigger_output_enabled(state, as_int):
    with expected_protocol(
        Agilent33250A,
        [("OUTP:TRIG?", as_int), (f"OUTP:TRIG {as_int}", None)],
    ) as inst:
        assert inst.trigger_output_enabled is state
        inst.trigger_output_enabled = state


@pytest.mark.parametrize("trigger_output_slope", ["POS", "NEG"])
def test_trigger_output_slope(trigger_output_slope):
    with expected_protocol(
        Agilent33250A,
        [
            ("OUTP:TRIG:SLOP?", trigger_output_slope),
            (f"OUTP:TRIG:SLOP {trigger_output_slope}", None),
        ],
    ) as inst:
        assert inst.trigger_output_slope == trigger_output_slope
        inst.trigger_output_slope = trigger_output_slope


def test_trigger_output_slope_invalid():
    with expected_protocol(Agilent33250A, []) as inst:
        with pytest.raises(ValueError):
            inst.trigger_output_slope = "UP"


def test_trigger():
    with expected_protocol(
        Agilent33250A,
        [("*TRG;*WAI", None)],
    ) as inst:
        inst.trigger()


def test_beep():
    with expected_protocol(
        Agilent33250A,
        [("SYST:BEEP", None)],
    ) as inst:
        inst.beep()


def test_wait_for_trigger():
    with expected_protocol(
        Agilent33250A,
        [("*OPC?", None), (None, ""), (None, "1")],
    ) as inst:
        inst.wait_for_trigger(timeout=1)


def test_scpi_mixin_standard_commands():
    with expected_protocol(
        Agilent33250A,
        [
            ("*IDN?", "Agilent Technologies,33250A,0,0"),
            ("*CLS", None),
            ("*RST", None),
        ],
    ) as inst:
        assert "33250A" in inst.id
        inst.clear()
        inst.reset()
