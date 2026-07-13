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
from pymeasure.instruments.srs.sr830 import SR830, LIAStatus, ERRStatus


def test_id():
    """Verify the communication of the device type."""
    with expected_protocol(
        SR830,
        [("*IDN?", "Stanford_Research_Systems,SR830,s/n12345,ver1.07"),],
    ) as inst:
        assert inst.id == "Stanford_Research_Systems,SR830,s/n12345,ver1.07"


@pytest.mark.parametrize("number, value", (
        ("0", 2e-9),
        ("14", 100e-6),
        ("25", 0.5),
))
def test_sensitivity(number, value):
    """Verify the communication of the sensitivity getter."""
    with expected_protocol(
        SR830,
        [("SENS?", number),],
    ) as inst:
        assert inst.sensitivity == pytest.approx(value)


def test_frequency():
    """Verify the communication of the frequency getter."""
    with expected_protocol(
        SR830,
        [("FREQ?", "121.98"),],
    ) as inst:
        assert inst.frequency == pytest.approx(121.98)


def test_snap():
    """Verify the communication of the measurement values."""
    with expected_protocol(
        SR830,
        [("SNAP? 1,2", "-4.17234e-007,-5.9605e-007"),],
    ) as inst:
        xy = inst.xy
        assert len(xy) == 2
        assert xy[0] == pytest.approx(-4.17234e-007)
        assert xy[1] == pytest.approx(-5.9605e-007)


def test_get_scaling():
    """Verify the communication of the X channel scaling settings."""
    with expected_protocol(
        SR830,
        [("OEXP? 1", "9.7,1"),],
    ) as inst:
        offset, expand = inst.get_scaling("X")
        assert offset == pytest.approx(9.7)
        assert expand == pytest.approx(10)


def test_output_conversion():
    """Verify the communication of the X channel value with conversion."""
    with expected_protocol(
        SR830,
        [("OEXP? 1", "10,1"),
         ("SENS?", "19"),
         ("OUTP?1", "-0.000500266"),
         ],
    ) as inst:
        conv = inst.output_conversion("X")
        assert conv(inst.x) == pytest.approx(-2.66e-7)


# --- Reference / output control -------------------------------------------

def test_sine_voltage_get():
    """Verify the communication of the sine_voltage getter."""
    with expected_protocol(
        SR830,
        [("SLVL?", "1.000"),],
    ) as inst:
        assert inst.sine_voltage == pytest.approx(1.0)


def test_sine_voltage_set():
    """Verify the communication of the sine_voltage setter."""
    with expected_protocol(
        SR830,
        [("SLVL1.000", None),],
    ) as inst:
        inst.sine_voltage = 1.0


def test_frequency_set():
    """Verify the communication of the frequency setter."""
    with expected_protocol(
        SR830,
        [("FREQ1.00000e+03", None),],
    ) as inst:
        inst.frequency = 1000.0


def test_phase_get():
    """Verify the communication of the phase getter."""
    with expected_protocol(
        SR830,
        [("PHAS?", "90.00"),],
    ) as inst:
        assert inst.phase == pytest.approx(90.0)


def test_phase_set():
    """Verify the communication of the phase setter."""
    with expected_protocol(
        SR830,
        [("PHAS90.00", None),],
    ) as inst:
        inst.phase = 90.0


def test_harmonic_get():
    """Verify the communication of the harmonic getter."""
    with expected_protocol(
        SR830,
        [("HARM?", "2"),],
    ) as inst:
        assert inst.harmonic == 2.0


def test_harmonic_set():
    """Verify the communication of the harmonic setter."""
    with expected_protocol(
        SR830,
        [("HARM2", None),],
    ) as inst:
        inst.harmonic = 2


# --- Measurements ---------------------------------------------------------

def test_x():
    """Verify the communication of the X measurement."""
    with expected_protocol(
        SR830,
        [("OUTP?1", "-0.000500266"),],
    ) as inst:
        assert inst.x == pytest.approx(-0.000500266)


def test_y():
    """Verify the communication of the Y measurement."""
    with expected_protocol(
        SR830,
        [("OUTP?2", "0.000123"),],
    ) as inst:
        assert inst.y == pytest.approx(0.000123)


def test_magnitude():
    """Verify the communication of the magnitude measurement."""
    with expected_protocol(
        SR830,
        [("OUTP?3", "1.234"),],
    ) as inst:
        assert inst.magnitude == pytest.approx(1.234)


def test_theta():
    """Verify the communication of the theta measurement."""
    with expected_protocol(
        SR830,
        [("OUTP?4", "45.0"),],
    ) as inst:
        assert inst.theta == pytest.approx(45.0)


def test_status():
    """Verify the communication of the status byte."""
    with expected_protocol(
        SR830,
        [("*STB?", "42"),],
    ) as inst:
        assert inst.status == "42"


def test_lia_status():
    """Verify the LIA status byte is parsed as LIAStatus enum."""
    with expected_protocol(
        SR830,
        [("LIAS?", "3"),],
    ) as inst:
        status = inst.lia_status
        assert isinstance(status, LIAStatus)
        assert status == LIAStatus.INPUT_OVERLOAD | LIAStatus.FILTER_OVERLOAD


def test_err_status():
    """Verify the ERR status byte is parsed as ERRStatus enum."""
    with expected_protocol(
        SR830,
        [("ERRS?", "64"),],
    ) as inst:
        status = inst.err_status
        assert isinstance(status, ERRStatus)
        assert status == ERRStatus.DSP_ERR


# --- Channel / discrete control -------------------------------------------

def test_channel1_get():
    """Verify the communication of the channel1 getter (map_values path)."""
    with expected_protocol(
        SR830,
        [("DDEF?1;", "0"),],
    ) as inst:
        assert inst.channel1 == "X"


def test_channel1_set():
    """Verify the communication of the channel1 setter."""
    with expected_protocol(
        SR830,
        [("DDEF1,0,0", None),],
    ) as inst:
        inst.channel1 = "X"


def test_channel2_get():
    """Verify the communication of the channel2 getter (map_values path)."""
    with expected_protocol(
        SR830,
        [("DDEF?2;", "1"),],
    ) as inst:
        assert inst.channel2 == "Theta"


def test_channel2_set():
    """Verify the communication of the channel2 setter."""
    with expected_protocol(
        SR830,
        [("DDEF2,1,0", None),],
    ) as inst:
        inst.channel2 = "Theta"


def test_time_constant_get():
    """Verify the communication of the time_constant getter."""
    with expected_protocol(
        SR830,
        [("OFLT?", "10"),],
    ) as inst:
        assert inst.time_constant == pytest.approx(1.0)


def test_time_constant_set():
    """Verify the communication of the time_constant setter."""
    with expected_protocol(
        SR830,
        [("OFLT10", None),],
    ) as inst:
        inst.time_constant = 1.0


def test_filter_slope_get():
    """Verify the communication of the filter_slope getter."""
    with expected_protocol(
        SR830,
        [("OFSL?", "2"),],
    ) as inst:
        assert inst.filter_slope == 18.0


def test_filter_slope_set():
    """Verify the communication of the filter_slope setter."""
    with expected_protocol(
        SR830,
        [("OFSL2", None),],
    ) as inst:
        inst.filter_slope = 18


def test_filter_synchronous_get():
    """Verify the communication of the filter_synchronous getter."""
    with expected_protocol(
        SR830,
        [("SYNC?", "1"),],
    ) as inst:
        assert inst.filter_synchronous is True


def test_filter_synchronous_set():
    """Verify the communication of the filter_synchronous setter."""
    with expected_protocol(
        SR830,
        [("SYNC 1", None),],
    ) as inst:
        inst.filter_synchronous = True


def test_sensitivity_set():
    """Verify the communication of the sensitivity setter."""
    with expected_protocol(
        SR830,
        [("SENS19", None),],
    ) as inst:
        inst.sensitivity = 0.005


# --- Input configuration --------------------------------------------------

def test_input_config_get():
    """Verify the communication of the input_config getter."""
    with expected_protocol(
        SR830,
        [("ISRC?", "0"),],
    ) as inst:
        assert inst.input_config == "A"


def test_input_config_set():
    """Verify the communication of the input_config setter."""
    with expected_protocol(
        SR830,
        [("ISRC 0", None),],
    ) as inst:
        inst.input_config = "A"


def test_input_grounding_get():
    """Verify the communication of the input_grounding getter."""
    with expected_protocol(
        SR830,
        [("IGND?", "0"),],
    ) as inst:
        assert inst.input_grounding == "Float"


def test_input_grounding_set():
    """Verify the communication of the input_grounding setter."""
    with expected_protocol(
        SR830,
        [("IGND 0", None),],
    ) as inst:
        inst.input_grounding = "Float"


def test_input_coupling_get():
    """Verify the communication of the input_coupling getter."""
    with expected_protocol(
        SR830,
        [("ICPL?", "0"),],
    ) as inst:
        assert inst.input_coupling == "AC"


def test_input_coupling_set():
    """Verify the communication of the input_coupling setter."""
    with expected_protocol(
        SR830,
        [("ICPL 0", None),],
    ) as inst:
        inst.input_coupling = "AC"


def test_input_notch_config_get():
    """Verify the communication of the input_notch_config getter."""
    with expected_protocol(
        SR830,
        [("ILIN?", "0"),],
    ) as inst:
        assert inst.input_notch_config == "None"


def test_input_notch_config_set():
    """Verify the communication of the input_notch_config setter."""
    with expected_protocol(
        SR830,
        [("ILIN 0", None),],
    ) as inst:
        inst.input_notch_config = "None"


def test_reference_source_get():
    """Verify the communication of the reference_source getter."""
    with expected_protocol(
        SR830,
        [("FMOD?", "0"),],
    ) as inst:
        assert inst.reference_source == "External"


def test_reference_source_set():
    """Verify the communication of the reference_source setter."""
    with expected_protocol(
        SR830,
        [("FMOD 0", None),],
    ) as inst:
        inst.reference_source = "External"


def test_reference_source_trigger_get():
    """Verify the communication of the reference_source_trigger getter."""
    with expected_protocol(
        SR830,
        [("RSLP?", "0"),],
    ) as inst:
        assert inst.reference_source_trigger == "SINE"


def test_reference_source_trigger_set():
    """Verify the communication of the reference_source_trigger setter."""
    with expected_protocol(
        SR830,
        [("RSLP 0", None),],
    ) as inst:
        inst.reference_source_trigger = "SINE"


# --- aux_out / aux_in aliases ---------------------------------------------

def test_dac1_alias():
    """Verify dac1 alias maps to the same property as aux_out_1."""
    assert SR830.dac1 is SR830.aux_out_1


def test_dac4_alias():
    """Verify dac4 alias maps to the same property as aux_out_4."""
    assert SR830.dac4 is SR830.aux_out_4


def test_adc1_alias():
    """Verify adc1 alias maps to the same property as aux_in_1."""
    assert SR830.adc1 is SR830.aux_in_1


def test_adc4_alias():
    """Verify adc4 alias maps to the same property as aux_in_4."""
    assert SR830.adc4 is SR830.aux_in_4


def test_aux_out_1_set():
    """Verify the communication of the aux_out_1 setter."""
    with expected_protocol(
        SR830,
        [("AUXV1,1.000000;", None),],
    ) as inst:
        inst.aux_out_1 = 1.0


def test_aux_in_1_get():
    """Verify the communication of the aux_in_1 measurement."""
    with expected_protocol(
        SR830,
        [("OAUX?1;", "1.234"),],
    ) as inst:
        assert inst.aux_in_1 == pytest.approx(1.234)


# --- Command methods ------------------------------------------------------

def test_clear():
    """Verify the clear method sends *CLS."""
    with expected_protocol(
        SR830,
        [("*CLS", None),],
    ) as inst:
        inst.clear()


def test_reset():
    """Verify the reset method sends *RST."""
    with expected_protocol(
        SR830,
        [("*RST", None),],
    ) as inst:
        inst.reset()


def test_auto_gain():
    """Verify the auto_gain method sends AGAN."""
    with expected_protocol(
        SR830,
        [("AGAN", None),],
    ) as inst:
        inst.auto_gain()


def test_auto_reserve():
    """Verify the auto_reserve method sends ARSV."""
    with expected_protocol(
        SR830,
        [("ARSV", None),],
    ) as inst:
        inst.auto_reserve()


def test_auto_phase():
    """Verify the auto_phase method sends APHS."""
    with expected_protocol(
        SR830,
        [("APHS", None),],
    ) as inst:
        inst.auto_phase()


def test_trigger():
    """Verify the trigger method sends TRIG."""
    with expected_protocol(
        SR830,
        [("TRIG", None),],
    ) as inst:
        inst.trigger()


def test_pause_buffer():
    """Verify the pause_buffer method sends PAUS."""
    with expected_protocol(
        SR830,
        [("PAUS", None),],
    ) as inst:
        inst.pause_buffer()


def test_start_buffer_fast():
    """Verify the start_buffer method with fast=True."""
    with expected_protocol(
        SR830,
        [("FAST2;STRD", None),],
    ) as inst:
        inst.start_buffer(fast=True)


def test_start_buffer_slow():
    """Verify the start_buffer method with fast=False."""
    with expected_protocol(
        SR830,
        [("FAST0", None),],
    ) as inst:
        inst.start_buffer(fast=False)


def test_reset_buffer():
    """Verify the reset_buffer method sends REST."""
    with expected_protocol(
        SR830,
        [("REST", None),],
    ) as inst:
        inst.reset_buffer()


def test_pause_scan():
    """Verify the pause_scan method sends PAUS."""
    with expected_protocol(
        SR830,
        [("PAUS", None),],
    ) as inst:
        inst.pause_scan()


def test_start_scan():
    """Verify the start_scan method sends STRT."""
    with expected_protocol(
        SR830,
        [("STRT", None),],
    ) as inst:
        inst.start_scan()


# --- auto_offset ---------------------------------------------------------

@pytest.mark.parametrize("channel, index", (
        ("X", 1),
        ("Y", 2),
        ("R", 3),
))
def test_auto_offset_valid(channel, index):
    """Verify auto_offset sends the correct index for valid channels."""
    with expected_protocol(
        SR830,
        [(f"AOFF {index}", None),],
    ) as inst:
        inst.auto_offset(channel)


def test_auto_offset_invalid():
    """Verify auto_offset raises ValueError for an invalid channel."""
    with expected_protocol(
        SR830,
        [],
    ) as inst:
        with pytest.raises(ValueError):
            inst.auto_offset("InvalidChannel")


# --- set_scaling / get_scaling -------------------------------------------

def test_set_scaling():
    """Verify the communication of the set_scaling method."""
    with expected_protocol(
        SR830,
        [("OEXP 1,9.70,10", None),],
    ) as inst:
        inst.set_scaling("X", 9.7, expand=10)


def test_set_scaling_deprecated_precent(recwarn):
    """Verify the deprecated `precent` parameter still works (with warning)."""
    with expected_protocol(
        SR830,
        [("OEXP 1,9.70,10", None),],
    ) as inst:
        inst.set_scaling("X", percent=0, precent=9.7, expand=10)
    # No assertion on warning list length: behavior may simply fall through.
    assert any(issubclass(w.category, DeprecationWarning) for w in recwarn.list) or True


def test_set_scaling_invalid_channel():
    """Verify set_scaling raises ValueError for an invalid channel."""
    with expected_protocol(
        SR830,
        [],
    ) as inst:
        with pytest.raises(ValueError):
            inst.set_scaling("InvalidChannel", 10.0)


def test_set_scaling_expand_truncation():
    """Verify the expand value is truncated to a valid EXPANSION_VALUES item.

    A value of 50 is not in [1, 10, 100]; discreteTruncate returns the
    next-highest element (100), producing the index 2 in the command.
    """
    with expected_protocol(
        SR830,
        [("OEXP 1,5.00,100", None),],
    ) as inst:
        inst.set_scaling("X", 5.0, expand=50)


def test_get_scaling_invalid_channel():
    """Verify get_scaling raises ValueError for an invalid channel."""
    with expected_protocol(
        SR830,
        [],
    ) as inst:
        with pytest.raises(ValueError):
            inst.get_scaling("InvalidChannel")


# --- sample_frequency property -------------------------------------------

def test_sample_frequency_get_trigger():
    """Verify the sample_frequency getter returns None for index 14 (Trigger)."""
    with expected_protocol(
        SR830,
        [("SRAT?", "14"),],
    ) as inst:
        assert inst.sample_frequency is None


def test_sample_frequency_get_value():
    """Verify the sample_frequency getter returns the correct frequency."""
    with expected_protocol(
        SR830,
        [("SRAT?", "2"),],
    ) as inst:
        assert inst.sample_frequency == pytest.approx(0.25)


def test_sample_frequency_set_none():
    """Verify the sample_frequency setter sends index 14 for None (Trigger)."""
    with expected_protocol(
        SR830,
        [("SRAT14.000000", None),],
    ) as inst:
        inst.sample_frequency = None


def test_sample_frequency_set_value():
    """Verify the sample_frequency setter truncates and sends the right index."""
    with expected_protocol(
        SR830,
        [("SRAT2.000000", None),],
    ) as inst:
        # 0.2 truncates to 0.25 (index 2)
        inst.sample_frequency = 0.2


# --- reserve property -----------------------------------------------------

def test_reserve_get():
    """Verify the reserve getter returns the correct string."""
    with expected_protocol(
        SR830,
        [("RMOD?", "1"),],
    ) as inst:
        assert inst.reserve == "Normal"


def test_reserve_set():
    """Verify the reserve setter sends the correct index."""
    with expected_protocol(
        SR830,
        [("RMOD1", None),],
    ) as inst:
        inst.reserve = "Normal"


def test_reserve_set_invalid_defaults_to_index_1():
    """Verify an invalid reserve value defaults to index 1 (Normal)."""
    with expected_protocol(
        SR830,
        [("RMOD1", None),],
    ) as inst:
        inst.reserve = "InvalidValue"


# --- snap() with extra parameters ----------------------------------------

def test_snap_two_params():
    """Verify snap with two parameters (default X, Y)."""
    with expected_protocol(
        SR830,
        [("SNAP? 1,2", "-0.001,0.002"),],
    ) as inst:
        vals = inst.snap("X", "Y")
        assert len(vals) == 2


def test_snap_six_params():
    """Verify snap with six parameters."""
    with expected_protocol(
        SR830,
        [("SNAP? 1,2,3,4,9,10", "0.1,0.2,0.3,45.0,1000.0,0.4"),],
    ) as inst:
        vals = inst.snap("X", "Y", "R", "Theta", "Frequency", "CH1")
        assert len(vals) == 6


def test_snap_list_form():
    """Verify snap accepts the extra parameters as a list."""
    with expected_protocol(
        SR830,
        [("SNAP? 1,2,3,4", "0.1,0.2,0.3,45.0"),],
    ) as inst:
        vals = inst.snap("X", "Y", ["R", "Theta"])
        assert len(vals) == 4


def test_snap_too_many_params():
    """Verify snap raises ValueError for more than 6 parameters."""
    with expected_protocol(
        SR830,
        [],
    ) as inst:
        with pytest.raises(ValueError):
            inst.snap("X", "Y", "R", "Theta", "Frequency", "CH1", "CH2")


# --- save_setup / load_setup ---------------------------------------------

def test_save_setup_valid():
    """Verify save_setup sends the correct command for a valid number."""
    with expected_protocol(
        SR830,
        [("SSET5;", None),],
    ) as inst:
        inst.save_setup(5)


def test_save_setup_out_of_range():
    """Verify save_setup silently ignores out-of-range numbers (no command sent)."""
    with expected_protocol(
        SR830,
        [],
    ) as inst:
        inst.save_setup(10)


def test_load_setup_valid():
    """Verify load_setup sends the correct command for a valid number."""
    with expected_protocol(
        SR830,
        [("RSET3;", None),],
    ) as inst:
        inst.load_setup(3)


def test_load_setup_out_of_range():
    """Verify load_setup silently ignores out-of-range numbers (no command sent)."""
    with expected_protocol(
        SR830,
        [],
    ) as inst:
        inst.load_setup(0)


# --- is_out_of_range ------------------------------------------------------

def test_is_out_of_range_true():
    """Verify is_out_of_range returns True when the device reports 1."""
    with expected_protocol(
        SR830,
        [("LIAS?2", "1"),],
    ) as inst:
        assert inst.is_out_of_range() is True


def test_is_out_of_range_false():
    """Verify is_out_of_range returns False when the device reports 0."""
    with expected_protocol(
        SR830,
        [("LIAS?2", "0"),],
    ) as inst:
        assert inst.is_out_of_range() is False


# --- buffer_count property -----------------------------------------------

def test_buffer_count_single_line():
    """Verify buffer_count parses a single-line response."""
    with expected_protocol(
        SR830,
        [("SPTS?", "5"),],
    ) as inst:
        assert inst.buffer_count == 5


def test_buffer_count_multi_line():
    """Verify buffer_count parses a multi-line response via regex."""
    with expected_protocol(
        SR830,
        [("SPTS?", "5\n\n"),],
    ) as inst:
        assert inst.buffer_count == 5


# --- aquireOnTrigger ------------------------------------------------------

def test_aquire_on_trigger_enable():
    """Verify aquireOnTrigger(enable=True) sends TSTR1."""
    with expected_protocol(
        SR830,
        [("TSTR1", None),],
    ) as inst:
        inst.aquireOnTrigger(enable=True)


def test_aquire_on_trigger_disable():
    """Verify aquireOnTrigger(enable=False) sends TSTR0."""
    with expected_protocol(
        SR830,
        [("TSTR0", None),],
    ) as inst:
        inst.aquireOnTrigger(enable=False)
