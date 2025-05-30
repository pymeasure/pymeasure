#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from pymeasure.instruments.hp.hp34401A import HP34401A


@pytest.mark.parametrize("function_", HP34401A.FUNCTIONS.keys())
def test_function(function_):
    with expected_protocol(
            HP34401A,
            [
                ("FUNC?", HP34401A.FUNCTIONS[function_]),
                (f"FUNC \"{HP34401A.FUNCTIONS[function_]}\"", None),
            ],
    ) as inst:
        assert function_ == inst.function_
        inst.function_ = function_


def test_range_dcv():
    with expected_protocol(
            HP34401A,
            [
                ("FUNC \"VOLT\"", None),
                ("FUNC?", "VOLT"),
                ("VOLT:RANG?", "1"),
                ("FUNC?", "VOLT"),
                ("VOLT:RANG 1", None),
            ],
    ) as inst:
        inst.function_ = "DCV"
        assert 1 == inst.range_
        inst.range_ = 1


def test_range_freq():
    with expected_protocol(
            HP34401A,
            [
                ("FUNC \"FREQ\"", None),
                ("FUNC?", "FREQ"),
                ("FREQ:VOLT:RANG?", "1"),
                ("FUNC?", "FREQ"),
                ("FREQ:VOLT:RANG 1", None),
            ],
    ) as inst:
        inst.function_ = "FREQ"
        assert 1 == inst.range_
        inst.range_ = 1


@pytest.mark.parametrize("enabled", [True, False])
def test_autorange_dcv(enabled):
    with expected_protocol(
            HP34401A,
            [
                ("FUNC \"VOLT\"", None),
                ("FUNC?", "VOLT"),
                ("VOLT:RANG:AUTO?", "1" if enabled else "0"),
                ("FUNC?", "VOLT"),
                (f"VOLT:RANG:AUTO {1 if enabled else 0}", None),
            ],
    ) as inst:
        inst.function_ = "DCV"
        assert enabled == inst.autorange
        inst.autorange = enabled


@pytest.mark.parametrize("enabled", [True, False])
def test_autorange_freq(enabled):
    with expected_protocol(
            HP34401A,
            [
                ("FUNC \"FREQ\"", None),
                ("FUNC?", "FREQ"),
                ("FREQ:VOLT:RANG:AUTO?", "1" if enabled else "0"),
                ("FUNC?", "FREQ"),
                (f"FREQ:VOLT:RANG:AUTO {1 if enabled else 0}", None),
            ],
    ) as inst:
        inst.function_ = "FREQ"
        assert enabled == inst.autorange
        inst.autorange = enabled


@pytest.mark.parametrize("function_", HP34401A.FUNCTIONS.keys())
def test_resolution(function_):
    with expected_protocol(
            HP34401A,
            [
                (f"FUNC \"{HP34401A.FUNCTIONS[function_]}\"", None),
                ("FUNC?", HP34401A.FUNCTIONS[function_]),
                (f"{HP34401A.FUNCTIONS[function_]}:RES?", "1"),
                ("FUNC?", HP34401A.FUNCTIONS[function_]),
                (f"{HP34401A.FUNCTIONS[function_]}:RES 1", None),
            ],
    ) as inst:
        inst.function_ = function_
        assert 1 == inst.resolution
        inst.resolution = 1


@pytest.mark.parametrize("function_", HP34401A.FUNCTIONS.keys())
def test_nplc(function_):
    with expected_protocol(
            HP34401A,
            [
                (f"FUNC \"{HP34401A.FUNCTIONS[function_]}\"", None),
                ("FUNC?", HP34401A.FUNCTIONS[function_]),
                (f"{HP34401A.FUNCTIONS[function_]}:NPLC?", "1"),
                ("FUNC?", HP34401A.FUNCTIONS[function_]),
                (f"{HP34401A.FUNCTIONS[function_]}:NPLC 1", None),
            ],
    ) as inst:
        inst.function_ = function_
        assert 1 == inst.nplc
        inst.nplc = 1


@pytest.mark.parametrize("function_", ["FREQ", "PERIOD"])
def test_gate_time(function_):
    with expected_protocol(
            HP34401A,
            [
                (f"FUNC \"{HP34401A.FUNCTIONS[function_]}\"", None),
                ("FUNC?", HP34401A.FUNCTIONS[function_]),
                (f"{HP34401A.FUNCTIONS[function_]}:APER?", "1"),
                ("FUNC?", HP34401A.FUNCTIONS[function_]),
                (f"{HP34401A.FUNCTIONS[function_]}:APER 1", None),
            ],
    ) as inst:
        inst.function_ = function_
        assert 1 == inst.gate_time
        inst.gate_time = 1


def test_detector_bandwidth():
    with expected_protocol(
            HP34401A,
            [
                ("DET:BAND?", "3"),
                ("DET:BAND 3", None),
            ],
    ) as inst:
        assert 3 == inst.detector_bandwidth
        inst.detector_bandwidth = 3


@pytest.mark.parametrize("enabled", [True, False])
def test_autozero_enabled(enabled):
    with expected_protocol(
            HP34401A,
            [
                ("ZERO:AUTO?", "1" if enabled else "0"),
                (f"ZERO:AUTO {1 if enabled else 0}", None),
            ],
    ) as inst:
        assert enabled == inst.autozero_enabled
        inst.autozero_enabled = enabled


def test_trigger_single_autozero():
    with expected_protocol(
            HP34401A,
            [
                ("ZERO:AUTO ONCE", None),
            ],
    ) as inst:
        inst.trigger_single_autozero()


@pytest.mark.parametrize("enabled", [True, False])
def test_auto_input_impedance_enabled(enabled):
    with expected_protocol(
            HP34401A,
            [
                ("INP:IMP:AUTO?", "1" if enabled else "0"),
                (f"INP:IMP:AUTO {1 if enabled else 0}", None),
            ],
    ) as inst:
        assert enabled == inst.auto_input_impedance_enabled
        inst.auto_input_impedance_enabled = enabled


def test_terminals_used():
    with expected_protocol(
            HP34401A,
            [
                ("ROUT:TERM?", "FRON"),
            ],
    ) as inst:
        assert "FRONT" == inst.terminals_used


def test_init_trigger():
    with expected_protocol(
            HP34401A,
            [
                ("INIT", None)
            ],
    ) as inst:
        inst.init_trigger()


def test_reading():
    with expected_protocol(
            HP34401A,
            [
                ("READ?", "1")
            ],
    ) as inst:
        assert 1 == inst.reading


@pytest.mark.parametrize("trigger_source", ["BUS", "EXT", "IMM"])
def test_trigger_source(trigger_source):
    with expected_protocol(
            HP34401A,
            [
                ("TRIG:SOUR?", trigger_source),
                (f"TRIG:SOUR {trigger_source}", None),
            ],
    ) as inst:
        assert trigger_source == inst.trigger_source
        inst.trigger_source = trigger_source


def test_trigger_delay():
    with expected_protocol(
            HP34401A,
            [
                ("TRIG:DEL?", "1"),
                ("TRIG:DEL 1", None),
            ],
    ) as inst:
        assert 1 == inst.trigger_delay
        inst.trigger_delay = 1


@pytest.mark.parametrize("enabled", [True, False])
def test_trigger_auto_delay_enabled(enabled):
    with expected_protocol(
            HP34401A,
            [
                ("TRIG:DEL:AUTO?", "1" if enabled else "0"),
                (f"TRIG:DEL:AUTO {1 if enabled else 0}", None),
            ],
    ) as inst:
        assert enabled == inst.trigger_auto_delay_enabled
        inst.trigger_auto_delay_enabled = enabled


def test_sample_count():
    with expected_protocol(
            HP34401A,
            [
                ("SAMP:COUN?", "1"),
                ("SAMP:COUN 1", None),
            ],
    ) as inst:
        assert 1 == inst.sample_count
        inst.sample_count = 1


def test_trigger_count():
    with expected_protocol(
            HP34401A,
            [
                ("TRIG:COUN?", "1"),
                ("TRIG:COUN 1", None),
            ],
    ) as inst:
        assert 1 == inst.trigger_count
        inst.trigger_count = 1


def test_stored_reading():
    with expected_protocol(
            HP34401A,
            [
                ("FETC?", "1"),
            ],
    ) as inst:
        assert 1 == inst.stored_reading


@pytest.mark.parametrize("enabled", [True, False])
def test_display_enabled(enabled):
    with expected_protocol(
            HP34401A,
            [
                ("DISP?", "1" if enabled else "0"),
                (f"DISP {1 if enabled else 0}", None),
            ],
    ) as inst:
        assert enabled == inst.display_enabled
        inst.display_enabled = enabled


def test_displayed_text():
    with expected_protocol(
            HP34401A,
            [
                ("DISP:TEXT?", "HELLO"),
                ("DISP:TEXT \"HELLO\"", None),
            ],
    ) as inst:
        assert "HELLO" == inst.displayed_text
        inst.displayed_text = "HELLO"


def test_beep():
    with expected_protocol(
            HP34401A,
            [
                ("SYST:BEEP", None),
            ],
    ) as inst:
        inst.beep()


@pytest.mark.parametrize("enabled", [True, False])
def test_beeper_enabled(enabled):
    with expected_protocol(
            HP34401A,
            [
                ("SYST:BEEP:STAT?", "1" if enabled else "0"),
                (f"SYST:BEEP:STAT {1 if enabled else 0}", None),
            ],
    ) as inst:
        assert enabled == inst.beeper_enabled
        inst.beeper_enabled = enabled


def test_scpi_version():
    with expected_protocol(
            HP34401A,
            [
                ("SYST:VERS?", "1-2-3"),
            ],
    ) as inst:
        assert "1-2-3" == inst.scpi_version


def test_stored_readings_count():
    with expected_protocol(
        HP34401A,
        [
            ("DATA:POIN?", "1"),
        ],
    ) as inst:
        assert 1 == inst.stored_readings_count


def test_self_test_result():
    with expected_protocol(
        HP34401A,
        [
            ("*TST?", "0"),
        ],
    ) as inst:
        assert 0 == inst.self_test_result
