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

from pymeasure.instruments.keysight import Keysight35670A
from pymeasure.instruments.keysight.keysight35670A import (
    _coerce_bytes,
    _encode_definite_block,
    _format_limit_segment_data,
    _math_register_selector,
    _normalize_hardcopy_destination,
    _normalize_hardcopy_line_type,
    _normalize_hardcopy_source,
    _normalize_hardcopy_timestamp_format,
    _normalize_mass_memory_disk,
    _normalize_memory_catalog_item,
    _normalize_program_name,
    _normalize_program_state,
    _normalize_program_variable_name,
    _parse_ascii_floats,
    _parse_ascii_or_definite_block_floats,
    _parse_ascii_ints,
    _parse_csv_strings,
    _parse_definite_block,
    _parse_limit_segment_data,
    _quote_string,
    _require_confirmation,
    _strip_quotes,
    _tcap_selector,
    _trace_selector,
    _data_register_selector,
    _validate_int_pair,
    _validate_int_triplet,
)
from pymeasure.test import expected_protocol


# --- helper tests ---

def test_parse_ascii_floats_empty():
    """Verify empty replies return empty list."""
    assert _parse_ascii_floats("") == []
    assert _parse_ascii_floats("   ") == []


def test_parse_ascii_floats_values():
    """Verify values are parsed as floats."""
    assert _parse_ascii_floats("1, 2.5, -3E-1") == [1.0, 2.5, -0.3]


def test_parse_ascii_floats_skips_empty_tokens():
    """Verify empty CSV tokens are ignored by float parser."""
    assert _parse_ascii_floats("1,,2") == [1.0, 2.0]


def test_parse_ascii_floats_bad_token_raises():
    """Verify non-float tokens raise ValueError."""
    with pytest.raises(ValueError):
        _parse_ascii_floats("bad")


def test_parse_ascii_ints_empty():
    """Verify empty int replies return empty list."""
    assert _parse_ascii_ints("") == []
    assert _parse_ascii_ints("   ") == []


def test_parse_ascii_ints_values():
    """Verify integer values are parsed correctly."""
    assert _parse_ascii_ints("1, -2, +3") == [1, -2, 3]


def test_parse_ascii_ints_bad_token_raises():
    """Verify non-integer tokens raise ValueError."""
    with pytest.raises(ValueError):
        _parse_ascii_ints("bad")


def test_parse_csv_strings():
    """Verify CSV strings are parsed and unquoted."""
    assert _parse_csv_strings('"A","B,C", D ') == ["A", "B,C", "D"]


def test_parse_csv_strings_quoted_values():
    """Verify CSV parser keeps quoted commas and strips quotes."""
    assert _parse_csv_strings('"A","B,C","D"') == ["A", "B,C", "D"]


def test_strip_quotes():
    """Verify matching boundary quotes are removed."""
    assert _strip_quotes('"ABC"') == "ABC"
    assert _strip_quotes("'ABC'") == "ABC"
    assert _strip_quotes("ABC") == "ABC"


def test_quote_string():
    """Verify SCPI strings are safely quoted."""
    assert _quote_string("ABC") == '"ABC"'
    assert _quote_string('"ABC"') == '"ABC"'
    assert _quote_string('A"B') == '"A""B"'


def test_quote_string_rejects_non_string():
    """Verify quoting rejects non-string arguments."""
    with pytest.raises(TypeError):
        _quote_string(123)  # type: ignore[arg-type]


def test_require_confirmation_requires_true():
    """Verify risky actions require explicit confirmation."""
    with pytest.raises(ValueError, match="requires explicit confirmation"):
        _require_confirmation("delete state", confirmed=False)


def test_require_confirmation_accepts_true():
    """Verify confirmed=True does not raise."""
    _require_confirmation("delete state", confirmed=True)


def test_trace_selector_with_int_indices():
    """Verify trace selector helper for integer indices."""
    assert _trace_selector(1) == "TRACe1"
    assert _trace_selector(4) == "TRACe4"


def test_trace_selector_rejects_out_of_range_index():
    """Verify trace selector rejects invalid index."""
    with pytest.raises(ValueError):
        _trace_selector(0)


def test_trace_selector_accepts_direct_selector():
    """Verify trace selector accepts preformatted selector tokens."""
    assert _trace_selector("D1") == "D1"


def test_tcap_selector_with_int_indices():
    """Verify time-capture selector helper for integer indices."""
    assert _tcap_selector(1) == "TCAP1"
    assert _tcap_selector(4) == "TCAP4"


def test_tcap_selector_accepts_direct_selector():
    """Verify time-capture selector accepts preformatted selector."""
    assert _tcap_selector("TCAP4") == "TCAP4"


def test_tcap_selector_rejects_out_of_range_index():
    """Verify time-capture selector rejects invalid index."""
    with pytest.raises(ValueError):
        _tcap_selector(5)


def test_data_register_selector_valid_values():
    """Verify data-register selector accepts numeric and token forms."""
    assert _data_register_selector(1) == "D1"
    assert _data_register_selector("D8") == "D8"


def test_data_register_selector_rejects_out_of_range_index():
    """Verify data-register selector rejects invalid index."""
    with pytest.raises(ValueError):
        _data_register_selector(9)


def test_math_register_selector_valid_values():
    """Verify math-register selector accepts valid indexes."""
    assert _math_register_selector(1) == 1
    assert _math_register_selector(5) == 5


def test_math_register_selector_rejects_out_of_range_index():
    """Verify math-register selector rejects invalid index."""
    with pytest.raises(ValueError):
        _math_register_selector(6)


def test_validate_int_pair_valid():
    """Verify integer pair validator accepts valid tuples."""
    assert _validate_int_pair((1, 2), [(0, 4), (0, 4)]) == (1, 2)


def test_validate_int_pair_invalid_length_raises():
    """Verify integer pair validator rejects wrong tuple length."""
    with pytest.raises(ValueError):
        _validate_int_pair((1,), [(0, 4), (0, 4)])


def test_validate_int_pair_invalid_type_raises():
    """Verify integer pair validator rejects unsupported types."""
    with pytest.raises(ValueError):
        _validate_int_pair(3.14, [(0, 4), (0, 4)])


def test_validate_int_triplet_valid():
    """Verify integer triplet validator accepts valid tuples."""
    assert _validate_int_triplet((1, 2, 3), [(0, 4), (0, 4), (0, 4)]) == (1, 2, 3)


def test_validate_int_triplet_invalid_length_raises():
    """Verify integer triplet validator rejects wrong tuple length."""
    with pytest.raises(ValueError):
        _validate_int_triplet((1, 2), [(0, 4), (0, 4), (0, 4)])


def test_validate_int_triplet_invalid_type_raises():
    """Verify integer triplet validator rejects unsupported types."""
    with pytest.raises(ValueError):
        _validate_int_triplet(object(), [(0, 4), (0, 4), (0, 4)])


def test_encode_definite_block():
    """Verify definite-block encoding helper."""
    assert _encode_definite_block(b"ABC") == b"#13ABC"


def test_parse_definite_block():
    """Verify definite-block parsing helper."""
    assert _parse_definite_block(b"#14ABCD") == b"ABCD"


def test_parse_definite_block_empty_raises():
    """Verify empty definite block raises ValueError."""
    with pytest.raises(ValueError):
        _parse_definite_block(b"")


def test_parse_definite_block_missing_hash_raises():
    """Verify non-block payload raises ValueError."""
    with pytest.raises(ValueError):
        _parse_definite_block(b"ABC")


def test_parse_definite_block_malformed_header_raises():
    """Verify malformed header raises ValueError."""
    with pytest.raises(ValueError):
        _parse_definite_block(b"#x3ABC")


def test_parse_definite_block_incomplete_header_raises():
    """Verify incomplete byte-count header raises ValueError."""
    with pytest.raises(ValueError):
        _parse_definite_block(b"#23A")


def test_parse_definite_block_bad_byte_count_raises():
    """Verify non-numeric byte count raises ValueError."""
    with pytest.raises(ValueError):
        _parse_definite_block(b"#1AABC")


def test_parse_definite_block_short_payload_raises():
    """Verify short payload raises ValueError."""
    with pytest.raises(ValueError):
        _parse_definite_block(b"#14ABC")


def test_parse_definite_block_indefinite_length_path():
    """Verify #0 block path returns trailing payload bytes."""
    assert _parse_definite_block(b"#0ABC") == b"ABC"


def test_parse_ascii_or_definite_block_floats_ascii():
    """Verify mixed parser accepts ASCII CSV float payload."""
    assert _parse_ascii_or_definite_block_floats("1,2,3") == [1.0, 2.0, 3.0]


def test_parse_ascii_or_definite_block_floats_definite_block_ascii():
    """Verify mixed parser accepts ASCII definite block payload."""
    assert _parse_ascii_or_definite_block_floats(b"#151,2,3") == [1.0, 2.0, 3.0]


def test_parse_ascii_or_definite_block_floats_definite_block_not_float_raises():
    """Verify non-float ASCII block payload raises ValueError."""
    with pytest.raises(ValueError):
        _parse_ascii_or_definite_block_floats(b"#13ABC")


def test_parse_ascii_or_definite_block_floats_binary_block_raises():
    """Verify non-ASCII block payload raises ValueError."""
    with pytest.raises(ValueError):
        _parse_ascii_or_definite_block_floats(b"#13\xff\x00\x01")


def test_format_limit_segment_data_nested():
    """Verify limit segment formatter accepts nested tuples."""
    assert _format_limit_segment_data([(1, 2, 3, 4)]) == "1,2,3,4"


def test_format_limit_segment_data_flat():
    """Verify limit segment formatter accepts flat lists."""
    assert _format_limit_segment_data([1, 2, 3, 4]) == "1,2,3,4"


def test_format_limit_segment_data_invalid_segment_length_raises():
    """Verify limit segment formatter rejects malformed tuples."""
    with pytest.raises(ValueError):
        _format_limit_segment_data([(1, 2, 3)])


def test_format_limit_segment_data_flat_invalid_multiple_raises():
    """Verify limit segment formatter rejects non-multiple-of-4 flat lists."""
    with pytest.raises(ValueError):
        _format_limit_segment_data([1, 2, 3])


def test_format_limit_segment_data_non_sequence_raises():
    """Verify limit segment formatter rejects unsupported types."""
    with pytest.raises(ValueError):
        _format_limit_segment_data(123)


def test_parse_limit_segment_data_valid():
    """Verify limit segment parser returns 4-value tuples."""
    assert _parse_limit_segment_data("1,2,3,4") == [(1.0, 2.0, 3.0, 4.0)]


def test_parse_limit_segment_data_invalid_length_raises():
    """Verify limit segment parser rejects malformed payloads."""
    with pytest.raises(ValueError):
        _parse_limit_segment_data("1,2,3")


def test_normalize_hardcopy_destination_valid_and_invalid():
    """Verify hardcopy destination normalizer valid and invalid paths."""
    assert _normalize_hardcopy_destination("MMEMORY") == "MMEM"
    with pytest.raises(ValueError):
        _normalize_hardcopy_destination("INVALID")


def test_normalize_hardcopy_timestamp_format_variants():
    """Verify hardcopy timestamp format normalizer variants."""
    assert _normalize_hardcopy_timestamp_format("FORM1") == "FORM1"
    assert _normalize_hardcopy_timestamp_format("FORMAT1") == "FORM1"
    with pytest.raises(ValueError):
        _normalize_hardcopy_timestamp_format("FORM9")


def test_normalize_hardcopy_source_valid_and_invalid():
    """Verify hardcopy source normalizer valid and invalid paths."""
    assert _normalize_hardcopy_source("MARK") == "MARK"
    with pytest.raises(ValueError):
        _normalize_hardcopy_source("INVALID")


def test_normalize_hardcopy_line_type_variants_and_invalid():
    """Verify hardcopy line-type normalizer variants and invalid values."""
    assert _normalize_hardcopy_line_type("SOL") == "SOL"
    assert _normalize_hardcopy_line_type("DASH") == "DASH"
    assert _normalize_hardcopy_line_type("DOTT") == "DOTT"
    assert _normalize_hardcopy_line_type("STYL3") == "STYL3"
    with pytest.raises(ValueError):
        _normalize_hardcopy_line_type("STYL2")
    with pytest.raises(ValueError):
        _normalize_hardcopy_line_type("INVALID")


def test_normalize_memory_catalog_item_valid_and_invalid():
    """Verify memory-catalog item normalizer valid and invalid paths."""
    assert _normalize_memory_catalog_item("program") == "PROGram"
    with pytest.raises(ValueError):
        _normalize_memory_catalog_item("invalid")


def test_normalize_mass_memory_disk_variants_and_invalid():
    """Verify mass-memory disk normalizer variants and invalid values."""
    assert _normalize_mass_memory_disk("RAM") == "RAM:"
    assert _normalize_mass_memory_disk("NVRAM") == "NVRAM:"
    assert _normalize_mass_memory_disk("EXT") == "EXT:"
    with pytest.raises(ValueError):
        _normalize_mass_memory_disk("INVALID")


def test_normalize_program_name_variants_and_invalid():
    """Verify program name normalizer variants and invalid values."""
    assert _normalize_program_name("1") == "PROGram1"
    assert _normalize_program_name("PROG1") == "PROGram1"
    with pytest.raises(ValueError):
        _normalize_program_name("PROG9")


def test_normalize_program_state_variants_and_invalid():
    """Verify program state normalizer variants and invalid values."""
    assert _normalize_program_state("STOP") == "STOP"
    assert _normalize_program_state("PAUSE") == "PAUSe"
    assert _normalize_program_state("RUN") == "RUN"
    assert _normalize_program_state("CONTINUE") == "CONTinue"
    with pytest.raises(ValueError):
        _normalize_program_state("INVALID")


def test_normalize_program_variable_name_variants():
    """Verify program variable normalizer for numeric and string variants."""
    assert _normalize_program_variable_name(5) == "5"
    assert _normalize_program_variable_name(5, string_variable=True) == "S5$"
    assert _normalize_program_variable_name("A$", string_variable=True) == "A$"


def test_coerce_bytes_variants_and_invalid():
    """Verify bytes coercion accepts supported inputs and rejects invalid types."""
    assert _coerce_bytes(b"AB") == b"AB"
    assert _coerce_bytes(bytearray(b"AB")) == b"AB"
    assert _coerce_bytes("AB") == b"AB"
    with pytest.raises(TypeError):
        _coerce_bytes(123)


def test_input_channel_bias_enabled_bool_mapping():
    """Verify the channel bias enabled bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("INPut2:BIAS:STATe 1", None)],
    ) as inst:
        inst.ch2.bias_enabled = True


def test_input_channel_state_bool_mapping():
    """Verify the channel state bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("INPut2:STATe 1", None)],
    ) as inst:
        inst.ch2.state = True


def test_input_channel_enabled_alias():
    """Verify the channel enabled alias."""
    with expected_protocol(
        Keysight35670A,
        [("INPut4:STATe 1", None),
         ("INPut4:STATe?", "0")],
    ) as inst:
        inst.ch4.enabled = True
        assert inst.ch4.enabled is False


def test_input_channel_1_cannot_be_disabled():
    """Verify channel 1 enable state cannot be set to off."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="cannot be disabled"):
            inst.ch1.enabled = False


def test_input_channel_1_enable_command():
    """Verify channel 1 can be explicitly enabled."""
    with expected_protocol(
        Keysight35670A,
        [("INPut1:STATe 1", None)],
    ) as inst:
        inst.ch1.enabled = True


def test_input_channel_2_disable_command():
    """Verify channels other than 1 can be disabled."""
    with expected_protocol(
        Keysight35670A,
        [("INPut2:STATe 0", None)],
    ) as inst:
        inst.ch2.enabled = False


def test_input_channel_coupling():
    """Verify the channel coupling setter."""
    with expected_protocol(
        Keysight35670A,
        [("INPut1:COUPling AC", None)],
    ) as inst:
        inst.ch1.coupling = "AC"


def test_input_channel_a_weighting_enabled_bool_mapping():
    """Verify A-weighting bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("INPut1:FILTer:AWEighting:STATe 1", None)],
    ) as inst:
        inst.ch1.a_weighting_enabled = True


def test_input_channel_anti_alias_filter_enabled_bool_mapping():
    """Verify anti-alias filter bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("INPut1:FILTer:LPASs:STATe 0", None)],
    ) as inst:
        inst.ch1.anti_alias_filter_enabled = False


def test_input_channel_shield():
    """Verify the channel shield setter and getter."""
    with expected_protocol(
        Keysight35670A,
        [("INPut3:LOW GRO", None),
         ("INPut3:LOW?", "FLO")],
    ) as inst:
        inst.ch3.shield = "ground"
        assert inst.ch3.shield == "float"


def test_input_channel_reference_direction_setter_and_getter():
    """Verify channel reference direction roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("INPut2:REFerence:DIRection 3", None),
         ("INPut2:REFerence:DIRection?", "9")],
    ) as inst:
        inst.ch2.reference_direction = 3
        assert inst.ch2.reference_direction == 9


def test_input_channel_reference_point_setter_and_getter():
    """Verify channel reference point roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("INPut2:REFerence:POINt 12720", None),
         ("INPut2:REFerence:POINt?", "11081")],
    ) as inst:
        inst.ch2.reference_point = 12720
        assert inst.ch2.reference_point == 11081


def test_input_channel_range_dbvrms_valid_discrete_values():
    """Verify the channel range accepts valid discrete values."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:VOLTage1:RANGe -51", None)],
    ) as inst:
        inst.ch1.range_dbvrms = -51


def test_input_channel_autorange_direction_mapping():
    """Verify input autorange direction mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:VOLTage2:RANGe:AUTO:DIRection UP", None),
         ("SENSe:VOLTage2:RANGe:AUTO:DIRection?", "EITH")],
    ) as inst:
        inst.ch2.autorange_direction = "up"
        assert inst.ch2.autorange_direction == "either"


def test_input_channel_range_unit_user_label_setter_and_getter():
    """Verify input user unit label roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [('SENSe:VOLTage1:RANGe:UNIT:USER:LABel "Cdeg"', None),
         ("SENSe:VOLTage1:RANGe:UNIT:USER:LABel?", '"Pa"')],
    ) as inst:
        inst.ch1.range_unit_user_label = "Cdeg"
        assert inst.ch1.range_unit_user_label == "Pa"


def test_input_channel_range_unit_user_scale_factor_setter_and_getter():
    """Verify input user unit scale-factor roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:VOLTage3:RANGe:UNIT:USER:SFACtor 1.8e-06", None),
         ("SENSe:VOLTage3:RANGe:UNIT:USER:SFACtor?", "0.1")],
    ) as inst:
        inst.ch3.range_unit_user_scale_factor = 1.8e-06
        assert inst.ch3.range_unit_user_scale_factor == 0.1


def test_input_channel_range_unit_user_enabled_bool_mapping():
    """Verify input user unit enable bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:VOLTage2:RANGe:UNIT:USER:STATe 1", None),
         ("SENSe:VOLTage2:RANGe:UNIT:USER:STATe?", "0")],
    ) as inst:
        inst.ch2.range_unit_user_enabled = True
        assert inst.ch2.range_unit_user_enabled is False


def test_input_channel_range_unit_transducer_label_setter_and_getter():
    """Verify input transducer unit label roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:VOLTage4:RANGe:UNIT:XDCR:LABel PA", None),
         ("SENSe:VOLTage4:RANGe:UNIT:XDCR:LABel?", "USER")],
    ) as inst:
        inst.ch4.range_unit_transducer_label = "PA"
        assert inst.ch4.range_unit_transducer_label == "USER"


def test_input_channel_range_upper_setter():
    """Verify input upper range setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:VOLTage1:RANGe -20", None)],
    ) as inst:
        inst.ch1.range_upper = -20


def test_trace_feed_mapping():
    """Verify trace feed mapping for power_spectrum_ch1."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:FEED 'XFR:POW 1'", None)],
    ) as inst:
        inst.trace1.feed = "power_spectrum_ch1"


def test_trace_active_mapping():
    """Verify active trace-group mapping."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:ACTive ABCD", None),
         ("CALCulate2:ACTive?", "CD")],
    ) as inst:
        inst.trace2.active = "abcd"
        assert inst.trace2.active == "cd"


def test_trace_display_format_mapping():
    """Verify trace display-format mapping."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:FORMat GDEL", None),
         ("CALCulate3:FORMat?", "UPH")],
    ) as inst:
        inst.trace3.display_format = "group_delay"
        assert inst.trace3.display_format == "unwrapped_phase"


def test_trace_group_delay_aperture_setter_and_getter():
    """Verify trace group-delay aperture roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:GDAPerture:APERture 5", None),
         ("CALCulate1:GDAPerture:APERture?", "2.5")],
    ) as inst:
        inst.trace1.group_delay_aperture = 5
        assert inst.trace1.group_delay_aperture == 2.5


def test_trace_data_points():
    """Verify the trace data points method."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:DATA:HEADer:POINts?", "401")],
    ) as inst:
        assert inst.trace1.data_points() == 401


def test_trace_read_data_ascii():
    """Verify the trace data read method for ASCII data."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:DATA?", "1.0,2.0,3.5")],
    ) as inst:
        assert inst.trace1.read_data() == [1.0, 2.0, 3.5]


def test_trace_read_x_data_ascii():
    """Verify the trace x data read method for ASCII data."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:X:DATA?", "0.0,1.0,2.0")],
    ) as inst:
        assert inst.trace1.read_x_data() == [0.0, 1.0, 2.0]


def test_instrument_mode():
    """Verify the instrument mode setter and getter."""
    with expected_protocol(
        Keysight35670A,
        [("INSTrument:SELect FFT", None),
         ("INSTrument:SELect?", "SINE")],
    ) as inst:
        inst.instrument_mode = "fft"
        assert inst.instrument_mode == "swept_sine"


def test_selected_instrument_number():
    """Verify the selected instrument number setter and getter."""
    with expected_protocol(
        Keysight35670A,
        [("INSTrument:NSELect 3", None),
         ("INSTrument:NSELect?", 4)],
    ) as inst:
        inst.selected_instrument_number = 3
        assert inst.selected_instrument_number == 4


def test_selected_instrument_number_accepts_fft_code_zero():
    """Verify selected instrument number accepts FFT code 0."""
    with expected_protocol(
        Keysight35670A,
        [("INSTrument:NSELect 0", None)],
    ) as inst:
        inst.selected_instrument_number = 0


def test_source_function_setter_maps_periodic_chirp_to_pch():
    """Verify source function setter maps periodic chirp to PCH."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:FUNCtion:SHAPe PCH", None)],
    ) as inst:
        inst.source_function = "periodic_chirp"


def test_source_frequency_setter():
    """Verify source frequency setter."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:FREQuency:FIXed 1000", None)],
    ) as inst:
        inst.source_frequency = 1000


def test_source_frequency_cw_setter():
    """Verify source CW frequency setter."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:FREQuency 2000", None)],
    ) as inst:
        inst.source_frequency_cw = 2000


def test_source_frequency_fixed_setter():
    """Verify source fixed frequency setter."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:FREQuency:FIXed 3000", None)],
    ) as inst:
        inst.source_frequency_fixed = 3000


def test_source_burst_percent_setter():
    """Verify source burst percent setter."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:BURSt 25", None)],
    ) as inst:
        inst.source_burst_percent = 25


def test_source_user_capture_channel_setter():
    """Verify source user capture channel setter."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:USER:CAPTure 2", None)],
    ) as inst:
        inst.source_user_capture_channel = 2


def test_source_user_register_setter_and_getter():
    """Verify source user register mapping roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:USER:REGister D3", None),
         ("SOURce:USER:REGister?", "D7")],
    ) as inst:
        inst.source_user_register = 3
        assert inst.source_user_register == 7


def test_source_user_repeat_enabled_bool_mapping():
    """Verify source user repeat bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:USER:REPeat 1", None),
         ("SOURce:USER:REPeat?", "0")],
    ) as inst:
        inst.source_user_repeat_enabled = True
        assert inst.source_user_repeat_enabled is False


def test_source_voltage_autolevel_enabled_bool_mapping():
    """Verify source autolevel bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:VOLTage:LEVel:AUTO 1", None),
         ("SOURce:VOLTage:LEVel:AUTO?", "0")],
    ) as inst:
        inst.source_voltage_autolevel_enabled = True
        assert inst.source_voltage_autolevel_enabled is False


def test_source_voltage_amplitude_setter():
    """Verify source voltage amplitude setter."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:VOLTage:LEVel:IMMediate:AMPLitude 0.25", None)],
    ) as inst:
        inst.source_voltage_amplitude = 0.25


def test_source_voltage_reference_setter():
    """Verify source voltage reference setter."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:VOLTage:LEVel:REFerence -20", None)],
    ) as inst:
        inst.source_voltage_reference = -20.0


def test_source_voltage_reference_channel_setter_and_getter():
    """Verify source voltage reference channel mapping roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:VOLTage:LEVel:REFerence:CHANnel INP2", None),
         ("SOURce:VOLTage:LEVel:REFerence:CHANnel?", "INP4")],
    ) as inst:
        inst.source_voltage_reference_channel = 2
        assert inst.source_voltage_reference_channel == 4


def test_source_voltage_reference_tolerance_setter():
    """Verify source voltage reference tolerance setter."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:VOLTage:LEVel:REFerence:TOLerance 3", None)],
    ) as inst:
        inst.source_voltage_reference_tolerance = 3.0


def test_source_voltage_limit_amplitude_setter():
    """Verify source voltage limit amplitude setter."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:VOLTage:LIMit:AMPLitude 2", None)],
    ) as inst:
        inst.source_voltage_limit_amplitude = 2.0


def test_source_voltage_limit_input_setter():
    """Verify source voltage limit input setter."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:VOLTage:LIMit:INPut -10", None)],
    ) as inst:
        inst.source_voltage_limit_input = -10.0


def test_source_voltage_slew_setter():
    """Verify source voltage slew setter."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:VOLTage:SLEW 100", None)],
    ) as inst:
        inst.source_voltage_slew = 100.0


def test_source_voltage_offset_setter_and_getter():
    """Verify source voltage offset roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SOURce:VOLTage:LEVel:IMMediate:OFFSet 1.5", None),
         ("SOURce:VOLTage:LEVel:IMMediate:OFFSet?", "-0.25")],
    ) as inst:
        inst.source_voltage_offset = 1.5
        assert inst.source_voltage_offset == -0.25


def test_source_output_enabled_bool_mapping():
    """Verify source output enabled bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("OUTPut:STATe 1", None),
         ("OUTPut:STATe?", "0")],
    ) as inst:
        inst.source_output_enabled = True
        assert inst.source_output_enabled is False


def test_output_low_pass_filter_enabled_bool_mapping():
    """Verify output low-pass filter bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("OUTPut:FILTer:LPASs:STATe 1", None),
         ("OUTPut:FILTer:LPASs:STATe?", "0")],
    ) as inst:
        inst.output_low_pass_filter_enabled = True
        assert inst.output_low_pass_filter_enabled is False


def test_source_voltage_offset_range_validation():
    """Verify source voltage offset range validation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError):
            inst.source_voltage_offset = 10.1


def test_averaging_enabled_bool_mapping():
    """Verify averaging enabled bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:AVERage:STATe 1", None)],
    ) as inst:
        inst.averaging_enabled = True


def test_average_count_setter():
    """Verify average count setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:AVERage:COUNt 16", None)],
    ) as inst:
        inst.average_count = 16


def test_average_confidence_setter():
    """Verify average confidence setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:AVERage:CONFidence 0.5", None)],
    ) as inst:
        inst.average_confidence = 0.5


def test_average_hold_mapping():
    """Verify average hold mode mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:AVERage:HOLD MIN", None),
         ("SENSe:AVERage:HOLD?", "MAX")],
    ) as inst:
        inst.average_hold = "minimum"
        assert inst.average_hold == "maximum"


def test_average_impulse_enabled_bool_mapping():
    """Verify average impulse bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:AVERage:IMPulse 1", None),
         ("SENSe:AVERage:IMPulse?", "0")],
    ) as inst:
        inst.average_impulse_enabled = True
        assert inst.average_impulse_enabled is False


def test_average_iresult_rate_setter():
    """Verify average iresult update-rate setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:AVERage:IRESult:RATE 5", None)],
    ) as inst:
        inst.average_iresult_rate = 5


def test_average_iresult_enabled_bool_mapping():
    """Verify average iresult bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:AVERage:IRESult:STATe 1", None),
         ("SENSe:AVERage:IRESult:STATe?", "0")],
    ) as inst:
        inst.average_iresult_enabled = True
        assert inst.average_iresult_enabled is False


def test_average_preview_mapping():
    """Verify average preview mode mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:AVERage:PREView TIM", None),
         ("SENSe:AVERage:PREView?", "MAN")],
    ) as inst:
        inst.average_preview = "timed"
        assert inst.average_preview == "manual"


def test_average_preview_time_setter():
    """Verify average preview time setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:AVERage:PREView:TIME 10", None)],
    ) as inst:
        inst.average_preview_time = 10.0


def test_average_type_mapping():
    """Verify average type mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:AVERage:TYPE ECON", None)],
    ) as inst:
        inst.average_type = "equal_confidence"


def test_average_time_setter():
    """Verify average time setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:AVERage:TIME 0.5", None)],
    ) as inst:
        inst.average_time = 0.5


def test_average_tcontrol_mapping():
    """Verify average time-control mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:AVERage:TCONtrol EXP", None)],
    ) as inst:
        inst.average_tcontrol = "exponential"


def test_accept_average_preview_command():
    """Verify average preview accept command."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:AVERage:PREView:ACCept", None)],
    ) as inst:
        inst.accept_average_preview()


def test_reject_average_preview_command():
    """Verify average preview reject command."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:AVERage:PREView:REJect", None)],
    ) as inst:
        inst.reject_average_preview()


def test_window_type_mapping():
    """Verify measurement window type mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:WINDow2:TYPE HANN", None)],
    ) as inst:
        inst.window2.window_type = "hanning"


def test_force_window_setter():
    """Verify force window setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:WINDow4:FORCe 0.01", None)],
    ) as inst:
        inst.window4.force_window = 0.01


def test_sense_window_exponential_time_constant_setter():
    """Verify sense-window exponential time constant setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:WINDow2:EXPonential 0.1", None)],
    ) as inst:
        inst.sense_window2.exponential_window_time_constant = 0.1


def test_sense_window_force_window_width_setter():
    """Verify sense-window force width setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:WINDow3:FORCe 0.05", None)],
    ) as inst:
        inst.sense_window3.force_window_width = 0.05


def test_sense_window_type_mapping():
    """Verify sense-window type mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:WINDow4:TYPE LLAG", None),
         ("SENSe:WINDow4:TYPE?", "HANN")],
    ) as inst:
        inst.sense_window4.window_type = "llag"
        assert inst.sense_window4.window_type == "hanning"


def test_sense_window_order_dc_included_bool_mapping():
    """Verify sense-window order DC bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:WINDow1:ORDer:DC 0", None),
         ("SENSe:WINDow1:ORDer:DC?", "1")],
    ) as inst:
        inst.sense_window1.order_dc_included = False
        assert inst.sense_window1.order_dc_included is True


def test_order_track_order_mapping():
    """Verify order-track order setting for all tracks."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:ORDer:TRACk1 1", None),
         ("SENSe:ORDer:TRACk2 2", None),
         ("SENSe:ORDer:TRACk3 3", None),
         ("SENSe:ORDer:TRACk4 4", None),
         ("SENSe:ORDer:TRACk5 5", None)],
    ) as inst:
        inst.order_track1.order = 1
        inst.order_track2.order = 2
        inst.order_track3.order = 3
        inst.order_track4.order = 4
        inst.order_track5.order = 5


def test_order_track_enabled_bool_mapping():
    """Verify order-track state bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:ORDer:TRACk1:STATe 1", None),
         ("SENSe:ORDer:TRACk2:STATe 0", None),
         ("SENSe:ORDer:TRACk3:STATe 1", None),
         ("SENSe:ORDer:TRACk4:STATe 0", None),
         ("SENSe:ORDer:TRACk5:STATe 1", None),
         ("SENSe:ORDer:TRACk3:STATe?", "0")],
    ) as inst:
        inst.order_track1.enabled = True
        inst.order_track2.enabled = False
        inst.order_track3.enabled = True
        inst.order_track4.enabled = False
        inst.order_track5.enabled = True
        assert inst.order_track3.enabled is False


def test_trigger_source_mapping():
    """Verify trigger source mapping."""
    with expected_protocol(
        Keysight35670A,
        [("TRIGger:SOURce EXT", None),
         ("TRIGger:SOURce INT2", None),
         ("TRIGger:SOURce OUTP", None)],
    ) as inst:
        inst.trigger_source = "external"
        inst.trigger_source = "internal2"
        inst.trigger_source = "output"


def test_trigger_slope_mapping():
    """Verify trigger slope mapping."""
    with expected_protocol(
        Keysight35670A,
        [("TRIGger:SLOPe POS", None)],
    ) as inst:
        inst.trigger_slope = "positive"


def test_trigger_level_setter():
    """Verify trigger level setter."""
    with expected_protocol(
        Keysight35670A,
        [("TRIGger:LEVel 0.125", None)],
    ) as inst:
        inst.trigger_level = 0.125


def test_external_trigger_level_setter():
    """Verify external trigger level setter."""
    with expected_protocol(
        Keysight35670A,
        [("TRIGger:EXTernal:LEVel 0.5", None)],
    ) as inst:
        inst.external_trigger_level = 0.5


def test_external_trigger_filter_enabled_bool_mapping():
    """Verify external trigger filter bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("TRIGger:EXTernal:FILTer:LPAS:STATe 1", None),
         ("TRIGger:EXTernal:FILTer:LPAS:STATe?", "0")],
    ) as inst:
        inst.external_trigger_filter_enabled = True
        assert inst.external_trigger_filter_enabled is False


def test_external_trigger_range_mapping():
    """Verify external trigger range mapping."""
    with expected_protocol(
        Keysight35670A,
        [("TRIGger:EXTernal:RANGe LOW", None)],
    ) as inst:
        inst.external_trigger_range = "low"


def test_trigger_start_per_channel_setters():
    """Verify per-channel trigger start delay mapping."""
    with expected_protocol(
        Keysight35670A,
        [("TRIGger:STARt1 -0.001", None),
         ("TRIGger:STARt2 0.002", None),
         ("TRIGger:STARt3 0.003", None),
         ("TRIGger:STARt4 0.004", None)],
    ) as inst:
        inst.trigger_start1 = -0.001
        inst.trigger_start2 = 0.002
        inst.trigger_start3 = 0.003
        inst.trigger_start4 = 0.004


def test_tachometer_holdoff_setter():
    """Verify tachometer holdoff setter."""
    with expected_protocol(
        Keysight35670A,
        [("TRIGger:TACHometer:HOLDoff 0.01", None)],
    ) as inst:
        inst.tachometer_holdoff = 0.01


def test_tachometer_level_setter():
    """Verify tachometer trigger level setter."""
    with expected_protocol(
        Keysight35670A,
        [("TRIGger:TACHometer:LEVel 1.5", None)],
    ) as inst:
        inst.tachometer_level = 1.5


def test_tachometer_pulse_count_setter():
    """Verify tachometer pulse-count setter."""
    with expected_protocol(
        Keysight35670A,
        [("TRIGger:TACHometer:PCOunt 60", None)],
    ) as inst:
        inst.tachometer_pulse_count = 60


def test_tachometer_range_mapping():
    """Verify tachometer range mapping."""
    with expected_protocol(
        Keysight35670A,
        [("TRIGger:TACHometer:RANGe HIGH", None)],
    ) as inst:
        inst.tachometer_range = "high"


def test_tachometer_slope_mapping():
    """Verify tachometer slope mapping."""
    with expected_protocol(
        Keysight35670A,
        [("TRIGger:TACHometer:SLOPe NEG", None)],
    ) as inst:
        inst.tachometer_slope = "negative"


def test_tachometer_rpm_measurement():
    """Verify tachometer RPM query."""
    with expected_protocol(
        Keysight35670A,
        [("TRIGger:TACHometer:RPM?", "1234.5")],
    ) as inst:
        assert inst.tachometer_rpm == 1234.5


def test_trigger_immediate_command():
    """Verify immediate trigger command mapping."""
    with expected_protocol(
        Keysight35670A,
        [("TRIGger:IMMediate", None)],
    ) as inst:
        inst.trigger_immediate()


def test_display_enabled_bool_mapping():
    """Verify display enabled bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:STATe 0", None)],
    ) as inst:
        inst.display_enabled = False


def test_display_format_mapping():
    """Verify display format mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:FORMat QUAD", None)],
    ) as inst:
        inst.display_format = "quad"


def test_display_view_mapping():
    """Verify display view mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:VIEW CTAB", None)],
    ) as inst:
        inst.display_view = "calc_table"


def test_trace_y_autoscale_window_mapping():
    """Verify trace y autoscale command mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow3:TRACe:Y:SCALe:AUTO ONCE", None)],
    ) as inst:
        inst.window3.trace_y_autoscale = "once"


def test_trace_x_autoscale_window_mapping():
    """Verify trace x autoscale command mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow1:TRACe:X:SCALe:AUTO OFF", None)],
    ) as inst:
        inst.window1.trace_x_autoscale = "off"


def test_display_annotation_enabled_bool_mapping():
    """Verify display annotation bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:ANNotation:ALL 1", None),
         ("DISPlay:ANNotation:ALL?", "0")],
    ) as inst:
        inst.display_annotation_enabled = True
        assert inst.display_annotation_enabled is False


def test_display_bode_command():
    """Verify BODE display command."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:BODE", None)],
    ) as inst:
        inst.bode()


def test_display_brightness_setter_and_getter():
    """Verify display brightness roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:BRIGhtness 0.759", None),
         ("DISPlay:BRIGhtness?", "1")],
    ) as inst:
        inst.display_brightness = 0.759
        assert inst.display_brightness == 1


def test_display_error_command():
    """Verify display error text command."""
    with expected_protocol(
        Keysight35670A,
        [('DISPlay:ERRor "Please try again."', None)],
    ) as inst:
        inst.display_error("Please try again.")


def test_display_external_enabled_bool_mapping():
    """Verify external display bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:EXTernal:STATe 0", None),
         ("DISPlay:EXTernal:STATe?", "1")],
    ) as inst:
        inst.display_external_enabled = False
        assert inst.display_external_enabled is True


def test_display_gpib_echo_enabled_bool_mapping():
    """Verify display GPIB echo bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:GPIB:ECHO 1", None),
         ("DISPlay:GPIB:ECHO?", "0")],
    ) as inst:
        inst.display_gpib_echo_enabled = True
        assert inst.display_gpib_echo_enabled is False


def test_display_program_mode_mapping():
    """Verify display program mode mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:PROGram:MODE LOW", None),
         ("DISPlay:PROGram:MODE?", "UPP")],
    ) as inst:
        inst.display_program_mode = "lower"
        assert inst.display_program_mode == "upper"


def test_display_program_vector_buffer_enabled_bool_mapping():
    """Verify display program vector buffer bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:PROGram:VECTor:BUFFer:STATe 0", None),
         ("DISPlay:PROGram:VECTor:BUFFer:STATe?", "1")],
    ) as inst:
        inst.display_program_vector_buffer_enabled = False
        assert inst.display_program_vector_buffer_enabled is True


def test_display_rpm_enabled_bool_mapping():
    """Verify display RPM indicator bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:RPM:STATe 1", None),
         ("DISPlay:RPM:STATe?", "0")],
    ) as inst:
        inst.display_rpm_enabled = True
        assert inst.display_rpm_enabled is False


def test_display_show_all_enabled_bool_mapping():
    """Verify display show-all-lines bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:SHOWall:STATe 1", None),
         ("DISPlay:SHOWall:STATe?", "0")],
    ) as inst:
        inst.display_show_all_enabled = True
        assert inst.display_show_all_enabled is False


def test_display_time_capture_envelope_enabled_bool_mapping():
    """Verify display time-capture envelope bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:TCAPture:ENVelope:STATe 0", None),
         ("DISPlay:TCAPture:ENVelope:STATe?", "1")],
    ) as inst:
        inst.display_time_capture_envelope_enabled = False
        assert inst.display_time_capture_envelope_enabled is True


def test_display_program_key_box_command():
    """Verify display program key-box command."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:PROGram:KEY:BOX 3,1", None)],
    ) as inst:
        inst.program_key_box(3, True)


def test_display_program_key_box_query():
    """Verify display program key-box query."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:PROGram:KEY:BOX? 3", "3,0")],
    ) as inst:
        assert inst.program_key_box(3) is False


def test_display_program_key_bracket_command():
    """Verify display program key-bracket command."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:PROGram:KEY:BRACket 0,4,1", None)],
    ) as inst:
        inst.program_key_bracket(0, 4, True)


def test_display_program_key_bracket_query():
    """Verify display program key-bracket query."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:PROGram:KEY:BRACket? 0,4", "0,4,1")],
    ) as inst:
        assert inst.program_key_bracket(0, 4) is True


def test_program_edit_enabled_bool_mapping():
    """Verify Instrument BASIC editor enabled bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("PROGram:EDIT:ENABle 0", None),
         ("PROGram:EDIT:ENABle?", "1")],
    ) as inst:
        inst.program_edit_enabled = False
        assert inst.program_edit_enabled is True


def test_program_name_mapping():
    """Verify active Instrument BASIC program selection mapping."""
    with expected_protocol(
        Keysight35670A,
        [("PROGram:NAME PROGram4", None),
         ("PROGram:NAME?", "PROG2")],
    ) as inst:
        inst.program_name = "program4"
        assert inst.program_name == "PROGram2"


def test_program_label_setter_and_getter():
    """Verify active Instrument BASIC program label roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [('PROGram:LABel "START TEST"', None),
         ("PROGram:LABel?", '"PRINT REPORT"')],
    ) as inst:
        inst.program_label = "START TEST"
        assert inst.program_label == "PRINT REPORT"


def test_program_state_mapping():
    """Verify active Instrument BASIC program state mapping."""
    with expected_protocol(
        Keysight35670A,
        [("PROGram:STATe CONTinue", None),
         ("PROGram:STATe?", "PAUS")],
    ) as inst:
        inst.program_state = "continue"
        assert inst.program_state == "PAUSe"


def test_program_allocated_memory_query():
    """Verify Instrument BASIC allocated memory query."""
    with expected_protocol(
        Keysight35670A,
        [("PROGram:MALLocate?", "187046")],
    ) as inst:
        assert inst.program_allocated_memory == 187046


def test_allocate_program_memory_numeric():
    """Verify Instrument BASIC memory allocation command."""
    with expected_protocol(
        Keysight35670A,
        [("PROGram:MALLocate 416211", None)],
    ) as inst:
        inst.allocate_program_memory(416211)


def test_allocate_program_memory_default():
    """Verify Instrument BASIC memory allocation default command."""
    with expected_protocol(
        Keysight35670A,
        [("PROGram:MALLocate DEFault", None)],
    ) as inst:
        inst.allocate_program_memory("DEFAULT")


def test_allocate_program_memory_max():
    """Verify Instrument BASIC memory allocation MAX command."""
    with expected_protocol(
        Keysight35670A,
        [("PROGram:MALLocate MAX", None)],
    ) as inst:
        inst.allocate_program_memory("MAX")


def test_allocate_program_memory_min():
    """Verify Instrument BASIC memory allocation MIN command."""
    with expected_protocol(
        Keysight35670A,
        [("PROGram:MALLocate MIN", None)],
    ) as inst:
        inst.allocate_program_memory("MIN")


def test_define_program_command_definite_block():
    """Verify selected Instrument BASIC definition upload command."""
    with expected_protocol(
        Keysight35670A,
        [(b"PROGram:DEFine #11A", None)],
    ) as inst:
        inst.define_program("A")


def test_define_program_command_raw_block():
    """Verify selected Instrument BASIC definition upload in raw mode."""
    with expected_protocol(
        Keysight35670A,
        [(b"PROGram:DEFine #11A", None)],
    ) as inst:
        inst.define_program(b"#11A", raw=True)


def test_read_program_definition_query_block():
    """Verify selected Instrument BASIC definition query."""
    with expected_protocol(
        Keysight35670A,
        [("PROGram:DEFine?", b"#11A")],
    ) as inst:
        assert inst.read_program_definition() == "A"


def test_read_program_definition_query_block_raw():
    """Verify selected Instrument BASIC definition query in raw mode."""
    with expected_protocol(
        Keysight35670A,
        [("PROGram:DEFine?", b"#11A")],
    ) as inst:
        assert inst.read_program_definition(raw=True) == b"#11A"


def test_define_explicit_program_command_definite_block():
    """Verify explicit Instrument BASIC definition upload command."""
    with expected_protocol(
        Keysight35670A,
        [(b"PROGram:EXPLicit:DEFine PROGram3,#12AB", None)],
    ) as inst:
        inst.define_explicit_program("AB", program=3)


def test_read_explicit_program_definition_query_block():
    """Verify explicit Instrument BASIC definition query."""
    with expected_protocol(
        Keysight35670A,
        [("PROGram:EXPLicit:DEFine?", b"#12AB")],
    ) as inst:
        assert inst.read_explicit_program_definition() == "AB"


def test_set_explicit_program_label_command():
    """Verify explicit Instrument BASIC label command."""
    with expected_protocol(
        Keysight35670A,
        [('PROGram:EXPLicit:LABel PROGram5, "PRINT REPORT"', None)],
    ) as inst:
        inst.set_explicit_program_label("PRINT REPORT", program=5)


def test_read_explicit_program_label_query():
    """Verify explicit Instrument BASIC label query."""
    with expected_protocol(
        Keysight35670A,
        [("PROGram:EXPLicit:LABel?", '"START TEST"')],
    ) as inst:
        assert inst.read_explicit_program_label() == "START TEST"


def test_delete_all_programs_requires_confirmation():
    """Verify deleting all programs requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.delete_all_programs()


def test_delete_all_programs_command():
    """Verify deleting all programs command."""
    with expected_protocol(
        Keysight35670A,
        [("PROGram:DELete:ALL", None)],
    ) as inst:
        inst.delete_all_programs(confirmed=True)


def test_delete_selected_program_requires_confirmation():
    """Verify deleting selected program requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.delete_selected_program()


def test_delete_selected_program_command():
    """Verify deleting selected program command."""
    with expected_protocol(
        Keysight35670A,
        [("PROGram:DELete", None)],
    ) as inst:
        inst.delete_selected_program(confirmed=True)


def test_set_program_number_variable_command():
    """Verify program numeric variable set command."""
    with expected_protocol(
        Keysight35670A,
        [('PROGram:NUMBer "Address", 11', None)],
    ) as inst:
        inst.set_program_number_variable("Address", 11)


def test_set_program_number_variable_sequence_command():
    """Verify program numeric variable set command with sequence payload."""
    with expected_protocol(
        Keysight35670A,
        [('PROGram:NUMBer "3", 1,2,3.5', None)],
    ) as inst:
        inst.set_program_number_variable(3, (1, 2.0, 3.5))


def test_read_program_number_variable_query():
    """Verify program numeric variable query."""
    with expected_protocol(
        Keysight35670A,
        [('PROGram:NUMBer? "Address"', "11,7")],
    ) as inst:
        assert inst.read_program_number_variable("Address") == [11.0, 7.0]


def test_set_program_string_variable_command():
    """Verify program string variable set command."""
    with expected_protocol(
        Keysight35670A,
        [('PROGram:STRing "Message$", "Measuring"', None)],
    ) as inst:
        inst.set_program_string_variable("Message", "Measuring")


def test_read_program_string_variable_query():
    """Verify program string variable query."""
    with expected_protocol(
        Keysight35670A,
        [('PROGram:STRing? "Message$"', '"Done"')],
    ) as inst:
        assert inst.read_program_string_variable("Message") == "Done"


def test_display_window_data_table_marker_enabled_bool_mapping():
    """Verify display window data-table marker bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow4:DTABle:MARKer:STATe 1", None),
         ("DISPlay:WINDow4:DTABle:MARKer:STATe?", "0")],
    ) as inst:
        inst.display4.data_table_marker_enabled = True
        assert inst.display4.data_table_marker_enabled is False


def test_display_window_data_table_enabled_bool_mapping():
    """Verify display window data-table bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow4:DTABle:STATe 0", None),
         ("DISPlay:WINDow4:DTABle:STATe?", "1")],
    ) as inst:
        inst.display4.data_table_enabled = False
        assert inst.display4.data_table_enabled is True


def test_display_window_limit_display_enabled_bool_mapping():
    """Verify display window limit-line bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow2:LIMit:STATe 1", None),
         ("DISPlay:WINDow2:LIMit:STATe?", "0")],
    ) as inst:
        inst.display2.limit_display_enabled = True
        assert inst.display2.limit_display_enabled is False


def test_display_window_polar_clockwise_bool_mapping():
    """Verify display window polar clockwise bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow3:POLar:CLOCkwise 1", None),
         ("DISPlay:WINDow3:POLar:CLOCkwise?", "0")],
    ) as inst:
        inst.display3.polar_clockwise = True
        assert inst.display3.polar_clockwise is False


def test_display_window_polar_rotation_setter_and_getter():
    """Verify display window polar rotation roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow3:POLar:ROTation -311", None),
         ("DISPlay:WINDow3:POLar:ROTation?", "-76")],
    ) as inst:
        inst.display3.polar_rotation = -311
        assert inst.display3.polar_rotation == -76


def test_display_window_trace_a_power_enabled_bool_mapping():
    """Verify display window trace A power bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow1:TRACe:APOWer:STATe 0", None),
         ("DISPlay:WINDow1:TRACe:APOWer:STATe?", "1")],
    ) as inst:
        inst.display1.trace_a_power_enabled = False
        assert inst.display1.trace_a_power_enabled is True


def test_display_window_trace_b_power_enabled_bool_mapping():
    """Verify display window trace B power bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow1:TRACe:BPOWer:STATe 1", None),
         ("DISPlay:WINDow1:TRACe:BPOWer:STATe?", "0")],
    ) as inst:
        inst.display1.trace_b_power_enabled = True
        assert inst.display1.trace_b_power_enabled is False


def test_display_window_trace_graticule_grid_enabled_bool_mapping():
    """Verify display window graticule-grid bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow3:TRACe:GRATicule:GRID:STATe 0", None),
         ("DISPlay:WINDow3:TRACe:GRATicule:GRID:STATe?", "1")],
    ) as inst:
        inst.display3.trace_graticule_grid_enabled = False
        assert inst.display3.trace_graticule_grid_enabled is True


def test_display_window_trace_label_setter_and_getter():
    """Verify display window trace label roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [('DISPlay:WINDow2:TRACe:LABel "CEPSTRUM"', None),
         ("DISPlay:WINDow2:TRACe:LABel?", '"SPL"')],
    ) as inst:
        inst.display2.trace_label = "CEPSTRUM"
        assert inst.display2.trace_label == "SPL"


def test_display_window_trace_label_default_enabled_bool_mapping():
    """Verify display window default-label bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow2:TRACe:LABel:DEFault:STATe 0", None),
         ("DISPlay:WINDow2:TRACe:LABel:DEFault:STATe?", "1")],
    ) as inst:
        inst.display2.trace_label_default_enabled = False
        assert inst.display2.trace_label_default_enabled is True


def test_display_window_x_match_command():
    """Verify display window X-axis match command."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow4:TRACe:X:MATCh3", None)],
    ) as inst:
        inst.display4.x_match(3)


def test_display_window_x_match_command_window2():
    """Verify display2 X-axis match command keeps channel substitution."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow2:TRACe:X:MATCh1", None)],
    ) as inst:
        inst.display2.x_match(1)


def test_display_window_trace_x_left_setter_and_getter():
    """Verify display window X-left roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow2:TRACe:X:SCALe:LEFT 5.61155e+37", None),
         ("DISPlay:WINDow2:TRACe:X:SCALe:LEFT?", "-8.83941e+37")],
    ) as inst:
        inst.display2.trace_x_left = 5.61155e37
        assert inst.display2.trace_x_left == -8.83941e37


def test_display_window_trace_x_right_setter_and_getter():
    """Verify display window X-right roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow2:TRACe:X:SCALe:RIGHt -1.10689e+37", None),
         ("DISPlay:WINDow2:TRACe:X:SCALe:RIGHt?", "-9.29266e+37")],
    ) as inst:
        inst.display2.trace_x_right = -1.10689e37
        assert inst.display2.trace_x_right == -9.29266e37


def test_display_window_trace_x_spacing_mapping():
    """Verify display window X-spacing mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow4:TRACe:X:SPACing LOG", None),
         ("DISPlay:WINDow4:TRACe:X:SPACing?", "LIN")],
    ) as inst:
        inst.display4.trace_x_spacing = "logarithmic"
        assert inst.display4.trace_x_spacing == "linear"


def test_display_window_y_match_command():
    """Verify display window Y-axis match command."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow4:TRACe:Y:MATCh3", None)],
    ) as inst:
        inst.display4.y_match(3)


def test_display_window_y_match_command_window3():
    """Verify display3 Y-axis match command keeps channel substitution."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow3:TRACe:Y:MATCh2", None)],
    ) as inst:
        inst.display3.y_match(2)


def test_display_window_trace_y_bottom_setter_and_getter():
    """Verify display window Y-bottom roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow3:TRACe:Y:SCALe:BOTTom 3.87223e+37", None),
         ("DISPlay:WINDow3:TRACe:Y:SCALe:BOTTom?", "7.35957e+37")],
    ) as inst:
        inst.display3.trace_y_bottom = 3.87223e37
        assert inst.display3.trace_y_bottom == 7.35957e37


def test_display_window_trace_y_center_setter_and_getter():
    """Verify display window Y-center roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow3:TRACe:Y:SCALe:CENTer 0", None),
         ("DISPlay:WINDow3:TRACe:Y:SCALe:CENTer?", "-40")],
    ) as inst:
        inst.display3.trace_y_center = 0
        assert inst.display3.trace_y_center == -40


def test_display_window_trace_y_per_division_setter_and_getter():
    """Verify display window Y-per-division roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow1:TRACe:Y:SCALe:PDIVision 4.5054e+37", None),
         ("DISPlay:WINDow1:TRACe:Y:SCALe:PDIVision?", "9.20888e+37")],
    ) as inst:
        inst.display1.trace_y_per_division = 4.5054e37
        assert inst.display1.trace_y_per_division == 9.20888e37


def test_display_window_trace_y_reference_mapping():
    """Verify display window Y-reference mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow3:TRACe:Y:SCALe:REFerence CENT", None),
         ("DISPlay:WINDow3:TRACe:Y:SCALe:REFerence?", "RANG")],
    ) as inst:
        inst.display3.trace_y_reference = "center"
        assert inst.display3.trace_y_reference == "range"


def test_display_window_trace_y_top_setter_and_getter():
    """Verify display window Y-top roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow4:TRACe:Y:SCALe:TOP 5", None),
         ("DISPlay:WINDow4:TRACe:Y:SCALe:TOP?", "0")],
    ) as inst:
        inst.display4.trace_y_top = 5
        assert inst.display4.trace_y_top == 0


def test_display_window_trace_y_spacing_mapping():
    """Verify display window Y-spacing mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow2:TRACe:Y:SPACing LOG", None),
         ("DISPlay:WINDow2:TRACe:Y:SPACing?", "LIN")],
    ) as inst:
        inst.display2.trace_y_spacing = "logarithmic"
        assert inst.display2.trace_y_spacing == "linear"


def test_display_window_waterfall_baseline_setter_and_getter():
    """Verify display window waterfall baseline roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow3:WATerfall:BASeline 33", None),
         ("DISPlay:WINDow3:WATerfall:BASeline?", "30")],
    ) as inst:
        inst.display3.waterfall_baseline = 33
        assert inst.display3.waterfall_baseline == 30


def test_display_window_waterfall_bottom_setter_and_getter():
    """Verify display window waterfall bottom roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow2:WATerfall:BOTTom 8.84371e+37", None),
         ("DISPlay:WINDow2:WATerfall:BOTTom?", "3.94581e+37")],
    ) as inst:
        inst.display2.waterfall_bottom = 8.84371e37
        assert inst.display2.waterfall_bottom == 3.94581e37


def test_display_window_waterfall_count_setter_and_getter():
    """Verify display window waterfall count-value roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow2:WATerfall:COUNt 100", None),
         ("DISPlay:WINDow2:WATerfall:COUNt?", "5")],
    ) as inst:
        inst.display2.waterfall_count = 100
        assert inst.display2.waterfall_count == 5


def test_display_window_waterfall_height_setter_and_getter():
    """Verify display window waterfall height roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow4:WATerfall:HEIGht 69", None),
         ("DISPlay:WINDow4:WATerfall:HEIGht?", "84")],
    ) as inst:
        inst.display4.waterfall_height = 69
        assert inst.display4.waterfall_height == 84


def test_display_window_waterfall_hidden_enabled_bool_mapping():
    """Verify display window waterfall hidden-line bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow4:WATerfall:HIDDen 1", None),
         ("DISPlay:WINDow4:WATerfall:HIDDen?", "0")],
    ) as inst:
        inst.display4.waterfall_hidden_enabled = True
        assert inst.display4.waterfall_hidden_enabled is False


def test_display_window_waterfall_skew_enabled_bool_mapping():
    """Verify display window waterfall skew bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow3:WATerfall:SKEW 1", None),
         ("DISPlay:WINDow3:WATerfall:SKEW?", "0")],
    ) as inst:
        inst.display3.waterfall_skew_enabled = True
        assert inst.display3.waterfall_skew_enabled is False


def test_display_window_waterfall_skew_angle_setter_and_getter():
    """Verify display window waterfall skew-angle roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow3:WATerfall:SKEW:ANGLe 20", None),
         ("DISPlay:WINDow3:WATerfall:SKEW:ANGLe?", "30")],
    ) as inst:
        inst.display3.waterfall_skew_angle = 20
        assert inst.display3.waterfall_skew_angle == 30


def test_display_window_waterfall_enabled_bool_mapping():
    """Verify display window waterfall enable bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow1:WATerfall:STATe 1", None),
         ("DISPlay:WINDow1:WATerfall:STATe?", "0")],
    ) as inst:
        inst.display1.waterfall_enabled = True
        assert inst.display1.waterfall_enabled is False


def test_display_window_waterfall_top_setter_and_getter():
    """Verify display window waterfall top roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("DISPlay:WINDow3:WATerfall:TOP 9.26034e+37", None),
         ("DISPlay:WINDow3:WATerfall:TOP?", "2.70387e+37")],
    ) as inst:
        inst.display3.waterfall_top = 9.26034e37
        assert inst.display3.waterfall_top == 2.70387e37


def test_hardcopy_color_default_command():
    """Verify hardcopy color defaults command."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:COLor:DEFault", None)],
    ) as inst:
        inst.hardcopy_color_default()


def test_hardcopy_destination_setter_and_getter():
    """Verify hardcopy destination roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [('HCOPy:DESTination "MMEM"', None),
         ("HCOPy:DESTination?", '"SYST:COMM:CENT"')],
    ) as inst:
        inst.hardcopy_destination = "MMEM"
        assert inst.hardcopy_destination == "SYST:COMM:CENT"


def test_hardcopy_device_language_setter_and_getter():
    """Verify hardcopy device language roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:DEVice:LANGuage PCL", None),
         ("HCOPy:DEVice:LANGuage?", "HPGL")],
    ) as inst:
        inst.hardcopy_device_language = "PCL"
        assert inst.hardcopy_device_language == "HPGL"


def test_hardcopy_device_resolution_setter_and_getter():
    """Verify hardcopy device resolution roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:DEVice:RESolution 75", None),
         ("HCOPy:DEVice:RESolution?", "0")],
    ) as inst:
        inst.hardcopy_device_resolution = 75
        assert inst.hardcopy_device_resolution == 0


def test_hardcopy_device_speed_setter_and_getter():
    """Verify hardcopy device speed roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:DEVice:SPEed 53", None),
         ("HCOPy:DEVice:SPEed?", "10")],
    ) as inst:
        inst.hardcopy_device_speed = 53
        assert inst.hardcopy_device_speed == 10


def test_hardcopy_requires_confirmation():
    """Verify hardcopy execution requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.hardcopy()


def test_hardcopy_command():
    """Verify hardcopy immediate command."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:IMMediate", None)],
    ) as inst:
        inst.hardcopy(confirmed=True)


def test_print_or_plot_command():
    """Verify print_or_plot alias command."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:IMMediate", None)],
    ) as inst:
        inst.print_or_plot(confirmed=True)


def test_hardcopy_form_feed_enabled_bool_mapping():
    """Verify hardcopy form-feed bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:ITEM:FFEed:STATe 1", None),
         ("HCOPy:ITEM:FFEed:STATe?", "0")],
    ) as inst:
        inst.hardcopy_form_feed_enabled = True
        assert inst.hardcopy_form_feed_enabled is False


def test_hardcopy_label_color_setter_and_getter():
    """Verify hardcopy label color roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:ITEM:LABel:COLor 4", None),
         ("HCOPy:ITEM:LABel:COLor?", "5")],
    ) as inst:
        inst.hardcopy_label_color = 4
        assert inst.hardcopy_label_color == 5


def test_hardcopy_label_enabled_bool_mapping():
    """Verify hardcopy label enable bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:ITEM:LABel:STATe 1", None),
         ("HCOPy:ITEM:LABel:STATe?", "0")],
    ) as inst:
        inst.hardcopy_label_enabled = True
        assert inst.hardcopy_label_enabled is False


def test_hardcopy_label_text_setter_and_getter():
    """Verify hardcopy label text roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [('HCOPy:ITEM:LABel:TEXT "TEST 1 RESULTS"', None),
         ("HCOPy:ITEM:LABel:TEXT?", '"TEST LABEL"')],
    ) as inst:
        inst.hardcopy_label_text = "TEST 1 RESULTS"
        assert inst.hardcopy_label_text == "TEST LABEL"


def test_hardcopy_timestamp_format_setter_and_getter():
    """Verify hardcopy timestamp format roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:ITEM:TDSTamp:FORMat FORM2", None),
         ("HCOPy:ITEM:TDSTamp:FORMat?", "FORM5")],
    ) as inst:
        inst.hardcopy_timestamp_format = "format2"
        assert inst.hardcopy_timestamp_format == "FORM5"


def test_hardcopy_timestamp_enabled_bool_mapping():
    """Verify hardcopy timestamp enable bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:ITEM:TDSTamp:STATe 1", None),
         ("HCOPy:ITEM:TDSTamp:STATe?", "0")],
    ) as inst:
        inst.hardcopy_timestamp_enabled = True
        assert inst.hardcopy_timestamp_enabled is False


def test_hardcopy_page_dimensions_auto_enabled_bool_mapping():
    """Verify hardcopy page auto-dimensions bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:PAGE:DIMensions:AUTO 0", None),
         ("HCOPy:PAGE:DIMensions:AUTO?", "1")],
    ) as inst:
        inst.hardcopy_page_dimensions_auto_enabled = False
        assert inst.hardcopy_page_dimensions_auto_enabled is True


def test_hardcopy_page_user_lower_left_setter_and_getter():
    """Verify hardcopy lower-left page point roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:PAGE:DIMensions:USER:LLEFt 332,1195", None),
         ("HCOPy:PAGE:DIMensions:USER:LLEFt?", "4743,4286")],
    ) as inst:
        inst.hardcopy_page_user_lower_left = (332, 1195)
        assert inst.hardcopy_page_user_lower_left == (4743, 4286)


def test_hardcopy_page_user_upper_right_setter_and_getter():
    """Verify hardcopy upper-right page point roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:PAGE:DIMensions:USER:URIGht 9155,7377", None),
         ("HCOPy:PAGE:DIMensions:USER:URIGht?", "9155,4286")],
    ) as inst:
        inst.hardcopy_page_user_upper_right = (9155, 7377)
        assert inst.hardcopy_page_user_upper_right == (9155, 4286)


def test_hardcopy_plot_address_setter_and_getter():
    """Verify hardcopy plotter address roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:PLOT:ADDRess 5", None),
         ("HCOPy:PLOT:ADDRess?", "9")],
    ) as inst:
        inst.hardcopy_plot_address = 5
        assert inst.hardcopy_plot_address == 9


def test_hardcopy_print_address_setter_and_getter():
    """Verify hardcopy printer address roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:PRINt:ADDRess 3", None),
         ("HCOPy:PRINt:ADDRess?", "1")],
    ) as inst:
        inst.hardcopy_print_address = 3
        assert inst.hardcopy_print_address == 1


def test_hardcopy_title1_setter_and_getter():
    """Verify hardcopy title line 1 roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [('HCOPy:TITLe1 "BEARING CHARACTERISTICS"', None),
         ("HCOPy:TITLe1?", '"LINE 1"')],
    ) as inst:
        inst.hardcopy_title1 = "BEARING CHARACTERISTICS"
        assert inst.hardcopy_title1 == "LINE 1"


def test_hardcopy_title2_setter_and_getter():
    """Verify hardcopy title line 2 roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [('HCOPy:TITLe2 "RMS SUMMARY"', None),
         ("HCOPy:TITLe2?", '"LINE 2"')],
    ) as inst:
        inst.hardcopy_title2 = "RMS SUMMARY"
        assert inst.hardcopy_title2 == "LINE 2"


def test_hardcopy_source_setter_and_getter():
    """Verify hardcopy source roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:SOURce MARK", None),
         ("HCOPy:SOURce?", "REF")],
    ) as inst:
        inst.hardcopy_source = "marker"
        assert inst.hardcopy_source == "REF"


def test_display_window_hardcopy_trace_color_setter_and_getter():
    """Verify display-window hardcopy trace color roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:ITEM:WINDow2:TRACe:COLor 6", None),
         ("HCOPy:ITEM:WINDow2:TRACe:COLor?", "2")],
    ) as inst:
        inst.display2.hardcopy_trace_color = 6
        assert inst.display2.hardcopy_trace_color == 2


def test_display_window_hardcopy_trace_graticule_color_setter_and_getter():
    """Verify display-window hardcopy graticule color roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:ITEM:WINDow1:TRACe:GRATicule:COLor 8", None),
         ("HCOPy:ITEM:WINDow1:TRACe:GRATicule:COLor?", "1")],
    ) as inst:
        inst.display1.hardcopy_trace_graticule_color = 8
        assert inst.display1.hardcopy_trace_graticule_color == 1


def test_display_window_hardcopy_trace_limit_line_type_setter_and_getter():
    """Verify display-window hardcopy limit line type roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:ITEM:WINDow3:TRACe:LIMit:LTYPe STYL3", None),
         ("HCOPy:ITEM:WINDow3:TRACe:LIMit:LTYPe?", "DOTT")],
    ) as inst:
        inst.display3.hardcopy_trace_limit_line_type = "style3"
        assert inst.display3.hardcopy_trace_limit_line_type == "DOTT"


def test_display_window_hardcopy_trace_line_type_setter_and_getter():
    """Verify display-window hardcopy trace line type roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:ITEM:WINDow4:TRACe:LTYPe DASH", None),
         ("HCOPy:ITEM:WINDow4:TRACe:LTYPe?", "STYL4")],
    ) as inst:
        inst.display4.hardcopy_trace_line_type = "dashed"
        assert inst.display4.hardcopy_trace_line_type == "STYL4"


def test_display_window_hardcopy_trace_marker_color_setter_and_getter():
    """Verify display-window hardcopy marker color roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("HCOPy:ITEM:WINDow4:TRACe:MARKer:COLor 9", None),
         ("HCOPy:ITEM:WINDow4:TRACe:MARKer:COLor?", "6")],
    ) as inst:
        inst.display4.hardcopy_trace_marker_color = 9
        assert inst.display4.hardcopy_trace_marker_color == 6


def test_memory_catalog_query():
    """Verify volatile memory catalog query."""
    with expected_protocol(
        Keysight35670A,
        [("MEMory:CATalog?", "1,2,TCAP,TCAP,10")],
    ) as inst:
        assert inst.memory_catalog() == "1,2,TCAP,TCAP,10"


def test_memory_catalog_all_query():
    """Verify volatile memory full catalog query."""
    with expected_protocol(
        Keysight35670A,
        [("MEMory:CATalog:ALL?", "1,2,TCAP,TCAP,10")],
    ) as inst:
        assert inst.memory_catalog(all_entries=True) == "1,2,TCAP,TCAP,10"


def test_memory_catalog_name_query():
    """Verify volatile memory named-item catalog query."""
    with expected_protocol(
        Keysight35670A,
        [("MEMory:CATalog:NAME? PROGram", "PROG,1024,2048")],
    ) as inst:
        assert inst.memory_catalog_name("program") == "PROG,1024,2048"


def test_memory_free_query():
    """Verify volatile memory free query."""
    with expected_protocol(
        Keysight35670A,
        [("MEMory:FREE?", "4096,2048")],
    ) as inst:
        assert inst.memory_free() == "4096,2048"


def test_memory_free_all_query():
    """Verify volatile memory free-all query."""
    with expected_protocol(
        Keysight35670A,
        [("MEMory:FREE:ALL?", "4096,2048")],
    ) as inst:
        assert inst.memory_free(all_entries=True) == "4096,2048"


def test_memory_delete_all_requires_confirmation():
    """Verify volatile memory delete-all requires confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.memory_delete_all()


def test_memory_delete_all_command():
    """Verify volatile memory delete-all command."""
    with expected_protocol(
        Keysight35670A,
        [("MEMory:DELete:ALL", None)],
    ) as inst:
        inst.memory_delete_all(confirmed=True)


def test_memory_delete_requires_confirmation():
    """Verify volatile memory item delete requires confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.memory_delete("program")


def test_memory_delete_command():
    """Verify volatile memory item delete command."""
    with expected_protocol(
        Keysight35670A,
        [("MEMory:DELete PROGram", None)],
    ) as inst:
        inst.memory_delete("program", confirmed=True)


def test_mass_memory_disk_address_setter_and_getter():
    """Verify mass-memory disk address roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("MMEMory:DISK:ADDRess 21", None),
         ("MMEMory:DISK:ADDRess?", "6")],
    ) as inst:
        inst.mass_memory_disk_address = 21
        assert inst.mass_memory_disk_address == 6


def test_mass_memory_disk_unit_setter_and_getter():
    """Verify mass-memory disk unit roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("MMEMory:DISK:UNIT 1", None),
         ("MMEMory:DISK:UNIT?", "0")],
    ) as inst:
        inst.mass_memory_disk_unit = 1
        assert inst.mass_memory_disk_unit == 0


def test_mass_memory_filesystem_query():
    """Verify mass-memory filesystem query."""
    with expected_protocol(
        Keysight35670A,
        [("MMEMory:FSYStem?", "DOS")],
    ) as inst:
        assert inst.mass_memory_filesystem == "DOS"


def test_mass_memory_default_disk_setter_and_getter():
    """Verify mass-memory default disk roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:MSIS "RAM:"', None),
         ("MMEMory:MSIS?", '"INT:"')],
    ) as inst:
        inst.mass_memory_default_disk = "RAM:"
        assert inst.mass_memory_default_disk == "INT:"


def test_mass_memory_name_setter_and_getter():
    """Verify mass-memory name roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:NAME "INT:PLOT.HPG"', None),
         ("MMEMory:NAME?", '"INT:PRINT1.HPG"')],
    ) as inst:
        inst.mass_memory_name = "INT:PLOT.HPG"
        assert inst.mass_memory_name == "INT:PRINT1.HPG"


def test_mass_memory_load_continue_status_query():
    """Verify mass-memory load-continue status query."""
    with expected_protocol(
        Keysight35670A,
        [("MMEMory:LOAD:CONTinue?", "1")],
    ) as inst:
        assert inst.mass_memory_load_continue_status == 1


def test_mass_memory_store_continue_status_query():
    """Verify mass-memory store-continue status query."""
    with expected_protocol(
        Keysight35670A,
        [("MMEMory:STORe:CONTinue?", "0")],
    ) as inst:
        assert inst.mass_memory_store_continue_status == 0


def test_mass_memory_store_program_format_setter_and_getter():
    """Verify mass-memory program store format roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("MMEMory:STORe:PROGram:FORMat BIN", None),
         ("MMEMory:STORe:PROGram:FORMat?", "ASC")],
    ) as inst:
        inst.mass_memory_store_program_format = "binary"
        assert inst.mass_memory_store_program_format == "ASC"


def test_mass_memory_store_trace_format_setter_and_getter():
    """Verify mass-memory trace store format roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("MMEM:STORe:TRACe:FORMat ASCII", None),
         ("MMEM:STORe:TRACe:FORMat?", "SDF")],
    ) as inst:
        inst.mass_memory_store_trace_format = "ASCII"
        assert inst.mass_memory_store_trace_format == "SDF"


def test_mass_memory_copy_requires_confirmation():
    """Verify mass-memory copy requires confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.mass_memory_copy("INT:FILE1", "INT:FILE2")


def test_mass_memory_copy_command():
    """Verify mass-memory copy command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:COPY "INT:FILE1", "INT:FILE2"', None)],
    ) as inst:
        inst.mass_memory_copy("INT:FILE1", "INT:FILE2", confirmed=True)


def test_mass_memory_delete_requires_confirmation():
    """Verify mass-memory delete requires confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.mass_memory_delete("INT:FILE1")


def test_mass_memory_delete_command():
    """Verify mass-memory delete command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:DELete "INT:FILE1"', None)],
    ) as inst:
        inst.mass_memory_delete("INT:FILE1", confirmed=True)


def test_mass_memory_initialize_requires_confirmation():
    """Verify mass-memory initialize requires confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.mass_memory_initialize("INT:", "DOS", 0, 1)


def test_mass_memory_initialize_command():
    """Verify mass-memory initialize command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:INITialize "INT:" DOS 0 1', None)],
    ) as inst:
        inst.mass_memory_initialize("INT:", "DOS", 0, 1, confirmed=True)


def test_mass_memory_initialize_disk_only_command():
    """Verify mass-memory initialize command with disk-only argument."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:INITialize "RAM"', None)],
    ) as inst:
        inst.mass_memory_initialize("RAM", confirmed=True)


def test_mass_memory_initialize_full_optional_arguments_command():
    """Verify mass-memory initialize command with all optional arguments."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:INITialize "RAM" LIF 1 2', None)],
    ) as inst:
        inst.mass_memory_initialize("RAM", "LIF", 1, 2, confirmed=True)


def test_mass_memory_load_continue_requires_confirmation():
    """Verify mass-memory load-continue command requires confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.mass_memory_load_continue()


def test_mass_memory_load_continue_command():
    """Verify mass-memory load-continue command."""
    with expected_protocol(
        Keysight35670A,
        [("MMEMory:LOAD:CONTinue", None)],
    ) as inst:
        inst.mass_memory_load_continue(confirmed=True)


def test_mass_memory_load_cfit_command():
    """Verify mass-memory load curve-fit command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:LOAD:CFIT "INT:CURVE1.FIT"', None)],
    ) as inst:
        inst.mass_memory_load_cfit("INT:CURVE1.FIT", confirmed=True)


def test_mass_memory_load_data_table_trace_command():
    """Verify mass-memory load data-table trace command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:LOAD:DTABle:TRACe2 "INT:DTAB2.DAT"', None)],
    ) as inst:
        inst.mass_memory_load_data_table_trace(2, "INT:DTAB2.DAT", confirmed=True)


def test_mass_memory_load_data_table_trace_command_short_filename():
    """Verify mass-memory load data-table trace command trace-index rendering."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:LOAD:DTABle:TRACe2 "A"', None)],
    ) as inst:
        inst.mass_memory_load_data_table_trace(2, "A", confirmed=True)


def test_mass_memory_load_lower_limit_trace_command():
    """Verify mass-memory load lower-limit trace command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:LOAD:LIMit:LOWer:TRACe3 "INT:LOW3.LIM"', None)],
    ) as inst:
        inst.mass_memory_load_lower_limit_trace(3, "INT:LOW3.LIM", confirmed=True)


def test_mass_memory_load_lower_limit_trace_command_short_filename():
    """Verify mass-memory load lower-limit trace command trace-index rendering."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:LOAD:LIMit:LOWer:TRACe2 "A"', None)],
    ) as inst:
        inst.mass_memory_load_lower_limit_trace(2, "A", confirmed=True)


def test_mass_memory_load_upper_limit_trace_command():
    """Verify mass-memory load upper-limit trace command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:LOAD:LIMit:UPPer:TRACe4 "INT:UP4.LIM"', None)],
    ) as inst:
        inst.mass_memory_load_upper_limit_trace(4, "INT:UP4.LIM", confirmed=True)


def test_mass_memory_load_upper_limit_trace_command_short_filename():
    """Verify mass-memory load upper-limit trace command trace-index rendering."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:LOAD:LIMit:UPPer:TRACe2 "A"', None)],
    ) as inst:
        inst.mass_memory_load_upper_limit_trace(2, "A", confirmed=True)


def test_mass_memory_load_math_command():
    """Verify mass-memory load math command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:LOAD:MATH "INT:MATH.DEF"', None)],
    ) as inst:
        inst.mass_memory_load_math("INT:MATH.DEF", confirmed=True)


def test_mass_memory_load_program_command():
    """Verify mass-memory load program command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:LOAD:PROGram "INT:MYPROG.BAS"', None)],
    ) as inst:
        inst.mass_memory_load_program("INT:MYPROG.BAS", confirmed=True)


def test_mass_memory_load_state_command():
    """Verify mass-memory load state command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:LOAD:STATe 1, "INT:AUTO_ST.STA"', None)],
    ) as inst:
        inst.mass_memory_load_state("INT:AUTO_ST.STA", slot=1, confirmed=True)


def test_mass_memory_load_synthesis_command():
    """Verify mass-memory load synthesis command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:LOAD:SYNThesis "INT:SYNTH.SYN"', None)],
    ) as inst:
        inst.mass_memory_load_synthesis("INT:SYNTH.SYN", confirmed=True)


def test_mass_memory_load_time_capture_command():
    """Verify mass-memory load time-capture command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:LOAD:TCAPture "INT:TCAP1.SDF"', None)],
    ) as inst:
        inst.mass_memory_load_time_capture("INT:TCAP1.SDF", confirmed=True)


def test_mass_memory_load_trace_command():
    """Verify mass-memory load trace command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:LOAD:TRACe D4, "INT:TRACE4.SDF"', None)],
    ) as inst:
        inst.mass_memory_load_trace(4, "INT:TRACE4.SDF", confirmed=True)


def test_mass_memory_load_trace_with_no_scale_command():
    """Verify mass-memory load trace command with no-scale argument."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:LOAD:TRACe D1, "INT:TRACE1.SDF", 1', None)],
    ) as inst:
        inst.mass_memory_load_trace(1, "INT:TRACE1.SDF", no_scale=True, confirmed=True)


def test_mass_memory_load_trace_with_no_scale_false_command():
    """Verify mass-memory load trace command with explicit no-scale false value."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:LOAD:TRACe D2, "INT:TRACE2.SDF", 0', None)],
    ) as inst:
        inst.mass_memory_load_trace(2, "INT:TRACE2.SDF", no_scale=False, confirmed=True)


def test_mass_memory_load_waterfall_command():
    """Verify mass-memory load waterfall command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:LOAD:WATerfall W3, "INT:WAT3.SDF"', None)],
    ) as inst:
        inst.mass_memory_load_waterfall(3, "INT:WAT3.SDF", confirmed=True)


def test_mass_memory_make_directory_command():
    """Verify mass-memory make-directory command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:MDIRectory "INT:\\RESULTS"', None)],
    ) as inst:
        inst.mass_memory_make_directory("INT:\\RESULTS", confirmed=True)


def test_mass_memory_move_command():
    """Verify mass-memory move command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:MOVE "INT:OLD.DAT", "INT:NEW.DAT"', None)],
    ) as inst:
        inst.mass_memory_move("INT:OLD.DAT", "INT:NEW.DAT", confirmed=True)


def test_mass_memory_store_continue_requires_confirmation():
    """Verify mass-memory store-continue command requires confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.mass_memory_store_continue()


def test_mass_memory_store_continue_command():
    """Verify mass-memory store-continue command."""
    with expected_protocol(
        Keysight35670A,
        [("MMEMory:STORe:CONTinue", None)],
    ) as inst:
        inst.mass_memory_store_continue(confirmed=True)


def test_mass_memory_store_cfit_command():
    """Verify mass-memory store curve-fit command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:STORe:CFIT "INT:CURVE1.FIT"', None)],
    ) as inst:
        inst.mass_memory_store_cfit("INT:CURVE1.FIT", confirmed=True)


def test_mass_memory_store_data_table_trace_command():
    """Verify mass-memory store data-table trace command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:STORe:DTABle:TRACe1 "INT:DTAB1.DAT"', None)],
    ) as inst:
        inst.mass_memory_store_data_table_trace(1, "INT:DTAB1.DAT", confirmed=True)


def test_mass_memory_store_data_table_trace_command_short_filename():
    """Verify mass-memory store data-table trace command trace-index rendering."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:STORe:DTABle:TRACe3 "A"', None)],
    ) as inst:
        inst.mass_memory_store_data_table_trace(3, "A", confirmed=True)


def test_mass_memory_store_lower_limit_trace_command():
    """Verify mass-memory store lower-limit trace command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:STORe:LIMit:LOWer:TRACe2 "INT:LOW2.LIM"', None)],
    ) as inst:
        inst.mass_memory_store_lower_limit_trace(2, "INT:LOW2.LIM", confirmed=True)


def test_mass_memory_store_lower_limit_trace_command_short_filename():
    """Verify mass-memory store lower-limit trace command trace-index rendering."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:STORe:LIMit:LOWer:TRACe2 "A"', None)],
    ) as inst:
        inst.mass_memory_store_lower_limit_trace(2, "A", confirmed=True)


def test_mass_memory_store_upper_limit_trace_command():
    """Verify mass-memory store upper-limit trace command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:STORe:LIMit:UPPer:TRACe4 "INT:UP4.LIM"', None)],
    ) as inst:
        inst.mass_memory_store_upper_limit_trace(4, "INT:UP4.LIM", confirmed=True)


def test_mass_memory_store_upper_limit_trace_command_short_filename():
    """Verify mass-memory store upper-limit trace command trace-index rendering."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:STORe:LIMit:UPPer:TRACe2 "A"', None)],
    ) as inst:
        inst.mass_memory_store_upper_limit_trace(2, "A", confirmed=True)


def test_mass_memory_store_math_command():
    """Verify mass-memory store math command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:STORe:MATH "INT:MATH.DEF"', None)],
    ) as inst:
        inst.mass_memory_store_math("INT:MATH.DEF", confirmed=True)


def test_mass_memory_store_program_command():
    """Verify mass-memory store program command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:STORe:PROGram "INT:MYPROG.BAS"', None)],
    ) as inst:
        inst.mass_memory_store_program("INT:MYPROG.BAS", confirmed=True)


def test_mass_memory_store_state_command():
    """Verify mass-memory store state command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:STORe:STATe 1, "INT:AUTO_ST.STA"', None)],
    ) as inst:
        inst.mass_memory_store_state("INT:AUTO_ST.STA", slot=1, confirmed=True)


def test_mass_memory_store_synthesis_command():
    """Verify mass-memory store synthesis command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:STORe:SYNThesis "INT:SYNTH.SYN"', None)],
    ) as inst:
        inst.mass_memory_store_synthesis("INT:SYNTH.SYN", confirmed=True)


def test_mass_memory_store_time_capture_command():
    """Verify mass-memory store time-capture command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:STORe:TCAPture "INT:TCAP1.SDF"', None)],
    ) as inst:
        inst.mass_memory_store_time_capture("INT:TCAP1.SDF", confirmed=True)


def test_mass_memory_store_trace_command():
    """Verify mass-memory store trace command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:STORe:TRACe TRACe3, "INT:TRACE3.SDF"', None)],
    ) as inst:
        inst.mass_memory_store_trace(3, "INT:TRACE3.SDF", confirmed=True)


def test_mass_memory_store_waterfall_command():
    """Verify mass-memory store waterfall command."""
    with expected_protocol(
        Keysight35670A,
        [('MMEMory:STORe:WATerfall TRACe2, "INT:WAT2.SDF"', None)],
    ) as inst:
        inst.mass_memory_store_waterfall(2, "INT:WAT2.SDF", confirmed=True)


@pytest.mark.parametrize(
    ("method_name", "args", "kwargs"),
    [
        ("mass_memory_load_cfit", ("INT:CURVE1.FIT",), {}),
        ("mass_memory_load_data_table_trace", (2, "INT:DTAB2.DAT"), {}),
        ("mass_memory_load_lower_limit_trace", (2, "INT:LOW2.LIM"), {}),
        ("mass_memory_load_upper_limit_trace", (2, "INT:UP2.LIM"), {}),
        ("mass_memory_load_math", ("INT:MATH.DEF",), {}),
        ("mass_memory_load_program", ("INT:MYPROG.BAS",), {}),
        ("mass_memory_load_state", ("INT:STATE.STA",), {"slot": 1}),
        ("mass_memory_load_synthesis", ("INT:SYNTH.SYN",), {}),
        ("mass_memory_load_time_capture", ("INT:TCAP1.SDF",), {}),
        ("mass_memory_load_trace", (2, "INT:TRACE2.SDF"), {}),
        ("mass_memory_load_waterfall", (2, "INT:WAT2.SDF"), {}),
        ("mass_memory_make_directory", ("INT:\\RESULTS",), {}),
        ("mass_memory_move", ("INT:OLD.DAT", "INT:NEW.DAT"), {}),
        ("mass_memory_store_cfit", ("INT:CURVE1.FIT",), {}),
        ("mass_memory_store_data_table_trace", (3, "INT:DTAB3.DAT"), {}),
        ("mass_memory_store_lower_limit_trace", (2, "INT:LOW2.LIM"), {}),
        ("mass_memory_store_upper_limit_trace", (2, "INT:UP2.LIM"), {}),
        ("mass_memory_store_math", ("INT:MATH.DEF",), {}),
        ("mass_memory_store_program", ("INT:MYPROG.BAS",), {}),
        ("mass_memory_store_state", ("INT:STATE.STA",), {"slot": 1}),
        ("mass_memory_store_synthesis", ("INT:SYNTH.SYN",), {}),
        ("mass_memory_store_time_capture", ("INT:TCAP1.SDF",), {}),
        ("mass_memory_store_trace", (2, "INT:TRACE2.SDF"), {}),
        ("mass_memory_store_waterfall", (2, "INT:WAT2.SDF"), {}),
    ],
)
def test_mass_memory_methods_require_confirmation(method_name, args, kwargs):
    """Verify destructive mass-memory methods require explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        method = getattr(inst, method_name)
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            method(*args, **kwargs)


def test_trace_amplitude_unit_mapping():
    """Verify trace amplitude unit mapping."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:UNIT:AMPLitude PP", None),
         ("CALCulate1:UNIT:AMPLitude?", "RMS")],
    ) as inst:
        inst.trace1.amplitude_unit = "PP"
        assert inst.trace1.amplitude_unit == "RMS"


def test_trace_angle_unit_mapping():
    """Verify trace angle unit mapping."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:UNIT:ANGLe RAD", None)],
    ) as inst:
        inst.trace2.angle_unit = "radian"


def test_trace_x_unit_mapping():
    """Verify trace x unit mapping."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:UNIT:X ORD", None),
         ("CALCulate4:UNIT:X?", "CPM")],
    ) as inst:
        inst.trace4.x_unit = "orders"
        assert inst.trace4.x_unit == "cycles_per_minute"


def test_trace_db_reference_impedance_setter_and_getter():
    """Verify trace dB reference impedance roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:UNIT:DBReference:IMPedance 600", None),
         ("CALCulate3:UNIT:DBReference:IMPedance?", "50")],
    ) as inst:
        inst.trace3.db_reference_impedance = 600
        assert inst.trace3.db_reference_impedance == 50


def test_trace_db_reference_user_label_setter_and_getter():
    """Verify trace dB user label roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [('CALCulate2:UNIT:DBReference:USER:LABel "m/s2"', None),
         ("CALCulate2:UNIT:DBReference:USER:LABel?", '"Pa"')],
    ) as inst:
        inst.trace2.db_reference_user_label = "m/s2"
        assert inst.trace2.db_reference_user_label == "Pa"


def test_trace_db_reference_user_reference_setter_and_getter():
    """Verify trace dB user reference roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:UNIT:DBReference:USER:REFerence 20", None),
         ("CALCulate4:UNIT:DBReference:USER:REFerence?", "1e3")],
    ) as inst:
        inst.trace4.db_reference_user_reference = 20
        assert inst.trace4.db_reference_user_reference == 1e3


def test_trace_mechanical_unit_setter_and_getter():
    """Verify trace mechanical unit roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:UNIT:MECHanical M/S", None),
         ("CALCulate1:UNIT:MECHanical?", "MILS")],
    ) as inst:
        inst.trace1.mechanical_unit = "M/S"
        assert inst.trace1.mechanical_unit == "MILS"


def test_trace_voltage_unit_setter_and_getter():
    """Verify trace voltage unit roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:UNIT:VOLTage V2/HZ", None),
         ("CALCulate2:UNIT:VOLTage?", "V/RTHZ")],
    ) as inst:
        inst.trace2.voltage_unit = "V2/HZ"
        assert inst.trace2.voltage_unit == "V/RTHZ"


def test_trace_x_order_factor_setter_and_getter():
    """Verify trace x-axis order-factor roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:UNIT:X:ORDer:FACTor 600", None),
         ("CALCulate3:UNIT:X:ORDer:FACTor?", "10")],
    ) as inst:
        inst.trace3.x_order_factor = 600
        assert inst.trace3.x_order_factor == 10


def test_trace_x_user_frequency_factor_setter_and_getter():
    """Verify trace user frequency-factor roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:UNIT:X:USER:FREQuency:FACTor 0.159", None),
         ("CALCulate3:UNIT:X:USER:FREQuency:FACTor?", "1.667e-2")],
    ) as inst:
        inst.trace3.x_user_frequency_factor = 0.159
        assert inst.trace3.x_user_frequency_factor == 1.667e-2


def test_trace_x_user_frequency_label_setter_and_getter():
    """Verify trace user frequency-label roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [('CALCulate2:UNIT:X:USER:FREQuency:LABel "rad/s"', None),
         ("CALCulate2:UNIT:X:USER:FREQuency:LABel?", '"cpm"')],
    ) as inst:
        inst.trace2.x_user_frequency_label = "rad/s"
        assert inst.trace2.x_user_frequency_label == "cpm"


def test_trace_x_user_time_factor_setter_and_getter():
    """Verify trace user time-factor roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:UNIT:X:USER:TIME:FACTor 331.45", None),
         ("CALCulate4:UNIT:X:USER:TIME:FACTor?", "1.0789e3")],
    ) as inst:
        inst.trace4.x_user_time_factor = 331.45
        assert inst.trace4.x_user_time_factor == 1.0789e3


def test_trace_x_user_time_label_setter_and_getter():
    """Verify trace user time-label roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [('CALCulate1:UNIT:X:USER:TIME:LABel "ft"', None),
         ("CALCulate1:UNIT:X:USER:TIME:LABel?", '"m"')],
    ) as inst:
        inst.trace1.x_user_time_label = "ft"
        assert inst.trace1.x_user_time_label == "m"


def test_trace_limit_beeper_enabled_bool_mapping():
    """Verify trace limit beeper bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:LIMit:BEEP:STATe 1", None),
         ("CALCulate2:LIMit:BEEP:STATe?", "0")],
    ) as inst:
        inst.trace2.limit_beeper_enabled = True
        assert inst.trace2.limit_beeper_enabled is False


def test_trace_limit_failed_measurement_false():
    """Verify trace limit failed query maps 0 to False."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:LIMit:FAIL?", "0")],
    ) as inst:
        assert inst.trace1.limit_failed is False


def test_trace_limit_failed_measurement_true():
    """Verify trace limit failed query maps 1 to True."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:LIMit:FAIL?", "1")],
    ) as inst:
        assert inst.trace3.limit_failed is True


def test_trace_clear_lower_limit_requires_confirmation():
    """Verify lower-limit clear requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.trace1.clear_lower_limit()


def test_trace_clear_lower_limit_command():
    """Verify lower-limit clear command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:LIMit:LOWer:CLEar:IMMediate", None)],
    ) as inst:
        inst.trace1.clear_lower_limit(confirmed=True)


def test_trace_move_lower_limit_y_command():
    """Verify lower-limit move command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:LIMit:LOWer:MOVE:Y -2.5", None)],
    ) as inst:
        inst.trace1.move_lower_limit_y(-2.5)


def test_trace_read_lower_limit_report_x_ascii():
    """Verify lower-limit report X parser for ASCII data."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:LIMit:LOWer:REPort:DATA?", "1.0,2.0,3.5")],
    ) as inst:
        assert inst.trace4.read_lower_limit_report_x() == [1.0, 2.0, 3.5]


def test_trace_read_lower_limit_report_y_definite_block_ascii():
    """Verify lower-limit report Y parser for ASCII definite-block data."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:LIMit:LOWer:REPort:YDATa?", "#170.5,1.5")],
    ) as inst:
        assert inst.trace4.read_lower_limit_report_y() == [0.5, 1.5]


def test_trace_lower_limit_segment_setter_and_getter():
    """Verify lower-limit segment setter and getter."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:LIMit:LOWer:SEGMent 10,2,100,3,200,-5,300,-5", None),
         ("CALCulate2:LIMit:LOWer:SEGMent?", "#21010,2,100,3")],
    ) as inst:
        inst.trace2.lower_limit_segment = [(10, 2, 100, 3), (200, -5, 300, -5)]
        assert inst.trace2.lower_limit_segment == [(10.0, 2.0, 100.0, 3.0)]


def test_trace_clear_lower_limit_segment_requires_confirmation():
    """Verify lower-limit segment clear requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.trace3.clear_lower_limit_segment(100)


def test_trace_clear_lower_limit_segment_command():
    """Verify lower-limit segment clear command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:LIMit:LOWer:SEGMent:CLEar 100", None)],
    ) as inst:
        inst.trace3.clear_lower_limit_segment(100, confirmed=True)


def test_trace_make_lower_limit_from_trace_requires_confirmation():
    """Verify lower-limit trace conversion requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.trace1.make_lower_limit_from_trace()


def test_trace_make_lower_limit_from_trace_command():
    """Verify lower-limit trace conversion command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:LIMit:LOWer:TRACe:IMMediate", None)],
    ) as inst:
        inst.trace1.make_lower_limit_from_trace(confirmed=True)


def test_trace_limit_enabled_bool_mapping():
    """Verify trace limit enabled bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:LIMit:STATe 1", None),
         ("CALCulate2:LIMit:STATe?", "0")],
    ) as inst:
        inst.trace2.limit_enabled = True
        assert inst.trace2.limit_enabled is False


def test_trace_clear_upper_limit_requires_confirmation():
    """Verify upper-limit clear requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.trace1.clear_upper_limit()


def test_trace_clear_upper_limit_command():
    """Verify upper-limit clear command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:LIMit:UPPer:CLEar:IMMediate", None)],
    ) as inst:
        inst.trace1.clear_upper_limit(confirmed=True)


def test_trace_move_upper_limit_y_command():
    """Verify upper-limit move command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:LIMit:UPPer:MOVE:Y 4", None)],
    ) as inst:
        inst.trace1.move_upper_limit_y(4)


def test_trace_move_upper_limit_y_command_trace2():
    """Verify upper-limit move command keeps channel substitution."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:LIMit:UPPer:MOVE:Y 1.5", None)],
    ) as inst:
        inst.trace2.move_upper_limit_y(1.5)


def test_trace_read_upper_limit_report_x_ascii():
    """Verify upper-limit report X parser for ASCII data."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:LIMit:UPPer:REPort:DATA?", "4.0,5.0")],
    ) as inst:
        assert inst.trace4.read_upper_limit_report_x() == [4.0, 5.0]


def test_trace_read_upper_limit_report_y_definite_block_ascii():
    """Verify upper-limit report Y parser for ASCII definite-block data."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:LIMit:UPPer:REPort:YDATa?", "#171.0,2.0")],
    ) as inst:
        assert inst.trace4.read_upper_limit_report_y() == [1.0, 2.0]


def test_trace_upper_limit_segment_setter_and_getter():
    """Verify upper-limit segment setter and getter."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:LIMit:UPPer:SEGMent 10,5,100,6", None),
         ("CALCulate2:LIMit:UPPer:SEGMent?", "10,5,100,6,200,7,300,8")],
    ) as inst:
        inst.trace2.upper_limit_segment = [(10, 5, 100, 6)]
        assert inst.trace2.upper_limit_segment == [
            (10.0, 5.0, 100.0, 6.0),
            (200.0, 7.0, 300.0, 8.0),
        ]


def test_trace_clear_upper_limit_segment_requires_confirmation():
    """Verify upper-limit segment clear requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.trace3.clear_upper_limit_segment(100)


def test_trace_clear_upper_limit_segment_command():
    """Verify upper-limit segment clear command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:LIMit:UPPer:SEGMent:CLEar 100", None)],
    ) as inst:
        inst.trace3.clear_upper_limit_segment(100, confirmed=True)


def test_trace_make_upper_limit_from_trace_requires_confirmation():
    """Verify upper-limit trace conversion requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.trace1.make_upper_limit_from_trace()


def test_trace_make_upper_limit_from_trace_command():
    """Verify upper-limit trace conversion command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:LIMit:UPPer:TRACe:IMMediate", None)],
    ) as inst:
        inst.trace1.make_upper_limit_from_trace(confirmed=True)


def test_trace_marker_band_start_setter_and_getter():
    """Verify marker band start roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:MARKer:BAND:STARt 1000", None),
         ("CALCulate1:MARKer:BAND:STARt?", "2000")],
    ) as inst:
        inst.trace1.marker_band_start = 1000
        assert inst.trace1.marker_band_start == 2000


def test_trace_marker_band_stop_setter_and_getter():
    """Verify marker band stop roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:MARKer:BAND:STOP 10000", None),
         ("CALCulate1:MARKer:BAND:STOP?", "20000")],
    ) as inst:
        inst.trace1.marker_band_stop = 10000
        assert inst.trace1.marker_band_stop == 20000


def test_trace_markers_coupled_bool_mapping():
    """Verify coupled markers bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:MARKer:COUpled:STATe 1", None),
         ("CALCulate2:MARKer:COUpled:STATe?", "0")],
    ) as inst:
        inst.trace2.markers_coupled = True
        assert inst.trace2.markers_coupled is False


def test_trace_clear_marker_data_table_requires_confirmation():
    """Verify marker data-table clear requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.trace1.clear_marker_data_table()


def test_trace_clear_marker_data_table_command():
    """Verify marker data-table clear command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:MARKer:DTABle:CLEar:IMMediate", None)],
    ) as inst:
        inst.trace1.clear_marker_data_table(confirmed=True)


def test_trace_copy_marker_data_table_from_command():
    """Verify marker data-table copy command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:MARKer:DTABle:COPY1", None)],
    ) as inst:
        inst.trace4.copy_marker_data_table_from(1)


def test_trace_read_marker_data_table_y_ascii():
    """Verify marker data-table Y read parser for ASCII data."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:MARKer:DTABle:DATA?", "1.0,2.5,3.75")],
    ) as inst:
        assert inst.trace2.read_marker_data_table_y() == [1.0, 2.5, 3.75]


def test_trace_read_marker_data_table_x_definite_block_ascii():
    """Verify marker data-table X read parser for ASCII definite block."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:MARKer:DTABle:X:DATA?", "#1810,20,30")],
    ) as inst:
        assert inst.trace2.read_marker_data_table_x() == [10.0, 20.0, 30.0]


def test_trace_delete_marker_data_table_entry_requires_confirmation():
    """Verify marker data-table entry delete requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.trace2.delete_marker_data_table_entry()


def test_trace_delete_marker_data_table_entry_command():
    """Verify marker data-table entry delete command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:MARKer:DTABle:X:DELete", None)],
    ) as inst:
        inst.trace2.delete_marker_data_table_entry(confirmed=True)


def test_trace_marker_data_table_insert_x_setter_and_getter():
    """Verify marker data-table insert X roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:MARKer:DTABle:X:INSert 123.4", None),
         ("CALCulate3:MARKer:DTABle:X:INSert?", "567.8")],
    ) as inst:
        inst.trace3.marker_data_table_insert_x = 123.4
        assert inst.trace3.marker_data_table_insert_x == 567.8


def test_trace_marker_data_table_label_setter_and_getter():
    """Verify marker data-table label roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [('CALCulate1:MARKer:DTABle:X:LABel "Fundamental"', None),
         ("CALCulate1:MARKer:DTABle:X:LABel?", '"Carrier"')],
    ) as inst:
        inst.trace1.marker_data_table_label = "Fundamental"
        assert inst.trace1.marker_data_table_label == "Carrier"


def test_trace_marker_data_table_selected_point_setter_and_getter():
    """Verify marker data-table selected point roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:MARKer:DTABle:X:SELect:POINt 23", None),
         ("CALCulate4:MARKer:DTABle:X:SELect:POINt?", "32")],
    ) as inst:
        inst.trace4.marker_data_table_selected_point = 23
        assert inst.trace4.marker_data_table_selected_point == 32


def test_trace_marker_function_setter_and_getter():
    """Verify marker function mapping roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:MARKer:FUNCtion OVER", None),
         ("CALCulate2:MARKer:FUNCtion?", "FREQ")],
    ) as inst:
        inst.trace2.marker_function = "overshoot"
        assert inst.trace2.marker_function == "frequency"


def test_trace_marker_function_result_measurement():
    """Verify marker function result query."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:MARKer:FUNCtion:RESult?", "12.34")],
    ) as inst:
        assert inst.trace3.marker_function_result == 12.34


def test_trace_marker_harmonic_count_setter_and_getter():
    """Verify harmonic marker count roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:MARKer:HARMonic:COUNt 5", None),
         ("CALCulate1:MARKer:HARMonic:COUNt?", "3")],
    ) as inst:
        inst.trace1.marker_harmonic_count = 5
        assert inst.trace1.marker_harmonic_count == 3


def test_trace_marker_harmonic_fundamental_setter_and_getter():
    """Verify harmonic fundamental roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:MARKer:HARMonic:FUNDamental 440", None),
         ("CALCulate1:MARKer:HARMonic:FUNDamental?", "1750")],
    ) as inst:
        inst.trace1.marker_harmonic_fundamental = 440
        assert inst.trace1.marker_harmonic_fundamental == 1750


def test_trace_marker_to_global_maximum_command():
    """Verify trace marker global maximum command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:MARKer:MAXimum:GLOBAL", None)],
    ) as inst:
        inst.trace4.marker_to_global_maximum()


def test_trace_marker_global_maximum_tracking_enabled_roundtrip():
    """Verify global-maximum marker tracking bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:MARKer:MAXimum:GLOBal:TRACk 1", None),
         ("CALCulate3:MARKer:MAXimum:GLOBal:TRACk?", "0")],
    ) as inst:
        inst.trace3.marker_global_maximum_tracking_enabled = True
        assert inst.trace3.marker_global_maximum_tracking_enabled is False


def test_trace_marker_to_left_maximum_command():
    """Verify marker left-maximum command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:MARKer:MAXimum:LEFT", None)],
    ) as inst:
        inst.trace2.marker_to_left_maximum()


def test_trace_marker_to_right_maximum_command():
    """Verify marker right-maximum command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:MARKer:MAXimum:RIGHt", None)],
    ) as inst:
        inst.trace2.marker_to_right_maximum()


def test_trace_marker_mode_mapping():
    """Verify marker mode mapping."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:MARKer:MODE REL", None),
         ("CALCulate1:MARKer:MODE?", "ABS")],
    ) as inst:
        inst.trace1.marker_mode = "relative"
        assert inst.trace1.marker_mode == "absolute"


def test_trace_marker_position_setter_and_getter():
    """Verify marker position roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:MARKer:POSition 102400", None),
         ("CALCulate4:MARKer:POSition?", "0.013")],
    ) as inst:
        inst.trace4.marker_position = 102400
        assert inst.trace4.marker_position == 0.013


def test_trace_marker_position_point_setter_and_getter():
    """Verify marker position point roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:MARKer:POSition:POINt 558", None),
         ("CALCulate4:MARKer:POSition:POINt?", "49")],
    ) as inst:
        inst.trace4.marker_position_point = 558
        assert inst.trace4.marker_position_point == 49


def test_trace_marker_reference_x_setter_and_getter():
    """Verify marker reference X roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:MARKer:REFerence:X 10", None),
         ("CALCulate1:MARKer:REFerence:X?", "20")],
    ) as inst:
        inst.trace1.marker_reference_x = 10
        assert inst.trace1.marker_reference_x == 20


def test_trace_marker_reference_y_setter_and_getter():
    """Verify marker reference Y roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:MARKer:REFerence:Y -3", None),
         ("CALCulate1:MARKer:REFerence:Y?", "4")],
    ) as inst:
        inst.trace1.marker_reference_y = -3
        assert inst.trace1.marker_reference_y == 4


def test_trace_marker_sideband_carrier_setter_and_getter():
    """Verify marker sideband carrier roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:MARKer:SIDeband:CARRier 2200", None),
         ("CALCulate2:MARKer:SIDeband:CARRier?", "19800")],
    ) as inst:
        inst.trace2.marker_sideband_carrier = 2200
        assert inst.trace2.marker_sideband_carrier == 19800


def test_trace_marker_sideband_count_setter_and_getter():
    """Verify marker sideband count roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:MARKer:SIDeband:COUNt 2", None),
         ("CALCulate2:MARKer:SIDeband:COUNt?", "6")],
    ) as inst:
        inst.trace2.marker_sideband_count = 2
        assert inst.trace2.marker_sideband_count == 6


def test_trace_marker_sideband_increment_setter_and_getter():
    """Verify marker sideband increment roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:MARKer:SIDeband:INCRement 600", None),
         ("CALCulate2:MARKer:SIDeband:INCRement?", "1800")],
    ) as inst:
        inst.trace2.marker_sideband_increment = 600
        assert inst.trace2.marker_sideband_increment == 1800


def test_trace_marker_enabled_mapping():
    """Verify trace marker enabled mapping."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:MARKer:STATe 1", None),
         ("CALCulate2:MARKer:STATe?", "0")],
    ) as inst:
        inst.trace2.marker_enabled = True
        assert inst.trace2.marker_enabled is False


def test_trace_marker_x_setter_and_getter():
    """Verify trace marker x roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:MARKer:X 123.4", None),
         ("CALCulate1:MARKer:X?", "567.8")],
    ) as inst:
        inst.trace1.marker_x = 123.4
        assert inst.trace1.marker_x == 567.8


def test_trace_marker_x_relative_setter_and_getter():
    """Verify trace marker x-relative roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:MARKer:X:RELative 10.5", None),
         ("CALCulate3:MARKer:X:RELative?", "-2.25")],
    ) as inst:
        inst.trace3.marker_x_relative = 10.5
        assert inst.trace3.marker_x_relative == -2.25


def test_trace_marker_y_measurement():
    """Verify trace marker y measurement."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:MARKer:Y?", "2.5")],
    ) as inst:
        assert inst.trace3.marker_y == 2.5


def test_trace_marker_y_relative_setter_and_getter():
    """Verify trace marker y-relative roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:MARKer:Y:RELative 12.5", None),
         ("CALCulate3:MARKer:Y:RELative?", "-7.5")],
    ) as inst:
        inst.trace3.marker_y_relative = 12.5
        assert inst.trace3.marker_y_relative == -7.5


def test_trace_set_math_constant_real_command():
    """Verify math constant command with real value only."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:MATH:CONStant5 0.1151", None)],
    ) as inst:
        inst.trace2.set_math_constant(5, 0.1151)


def test_trace_set_math_constant_complex_command():
    """Verify math constant command with real and imaginary values."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:MATH:CONStant1 -1,1", None)],
    ) as inst:
        inst.trace1.set_math_constant(1, -1, 1)


def test_trace_set_math_constant_command_trace2():
    """Verify math constant command keeps channel substitution for trace 2."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:MATH:CONStant1 2", None)],
    ) as inst:
        inst.trace2.set_math_constant(1, 2.0)


def test_trace_math_constant_query():
    """Verify math constant query parser."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:MATH:CONStant4?", "2.5,-0.25")],
    ) as inst:
        assert inst.trace3.math_constant(4) == (2.5, -0.25)


def test_trace_set_math_expression_command():
    """Verify math expression set command."""
    with expected_protocol(
        Keysight35670A,
        [('CALCulate4:MATH:EXPRession2 "(K1*FRES)"', None)],
    ) as inst:
        inst.trace4.set_math_expression("(K1*FRES)", function_register=2)


def test_trace_set_math_expression_command_trace2():
    """Verify math expression command keeps channel substitution for trace 2."""
    with expected_protocol(
        Keysight35670A,
        [('CALCulate2:MATH:EXPRession3 "A+B"', None)],
    ) as inst:
        inst.trace2.set_math_expression("A+B", 3)


def test_trace_math_expression_query():
    """Verify math expression query."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:MATH:EXPRession2?", '"(F1+K2)"')],
    ) as inst:
        assert inst.trace4.math_expression(function_register=2) == "(F1+K2)"


def test_trace_math_data_query_parses_definite_block():
    """Verify math table query parses a definite block response."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:MATH:DATA?", b"#14ABCD")],
    ) as inst:
        assert inst.trace2.math_data() == b"ABCD"


def test_trace_math_data_query_raw():
    """Verify raw math table query returns unparsed block bytes."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:MATH:DATA?", b"#14ABCD")],
    ) as inst:
        assert inst.trace2.math_data(raw=True) == b"#14ABCD"


def test_trace_load_math_data_encodes_definite_block():
    """Verify math table upload encodes data as a definite block."""
    with expected_protocol(
        Keysight35670A,
        [(b"CALCulate2:MATH:DATA #14ABCD", None)],
    ) as inst:
        inst.trace2.load_math_data(b"ABCD")


def test_trace_load_math_data_raw():
    """Verify raw math table upload keeps caller-provided block framing."""
    with expected_protocol(
        Keysight35670A,
        [(b"CALCulate2:MATH:DATA #14ABCD", None)],
    ) as inst:
        inst.trace2.load_math_data(b"#14ABCD", raw=True)


def test_trace_math_selected_function_setter_and_getter():
    """Verify math selected-function roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:MATH:SELect F3", None),
         ("CALCulate1:MATH:SELect?", "F5")],
    ) as inst:
        inst.trace1.math_selected_function = "F3"
        assert inst.trace1.math_selected_function == "F5"


def test_trace_math_enabled_bool_mapping():
    """Verify math state bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:MATH:STATe 1", None),
         ("CALCulate1:MATH:STATe?", "0")],
    ) as inst:
        inst.trace1.math_enabled = True
        assert inst.trace1.math_enabled is False


def test_trace_abort_curve_fit_command():
    """Verify curve-fit abort command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:CFIT:ABORt", None)],
    ) as inst:
        inst.trace2.abort_curve_fit()


def test_trace_copy_synthesis_to_curve_fit_command():
    """Verify curve-fit copy-from-synthesis command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:CFIT:COPY SYNThesis", None)],
    ) as inst:
        inst.trace2.copy_synthesis_to_curve_fit()


def test_trace_cfit_data_query_parses_definite_block():
    """Verify curve-fit table query parses a definite block response."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:CFIT:DATA?", b"#14ABCD")],
    ) as inst:
        assert inst.trace3.cfit_data() == b"ABCD"


def test_trace_cfit_data_query_raw():
    """Verify raw curve-fit table query returns unparsed block bytes."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:CFIT:DATA?", b"#14ABCD")],
    ) as inst:
        assert inst.trace3.cfit_data(raw=True) == b"#14ABCD"


def test_trace_load_cfit_data_encodes_definite_block():
    """Verify curve-fit table upload encodes data as a definite block."""
    with expected_protocol(
        Keysight35670A,
        [(b"CALCulate3:CFIT:DATA #14ABCD", None)],
    ) as inst:
        inst.trace3.load_cfit_data(b"ABCD")


def test_trace_load_cfit_data_raw():
    """Verify raw curve-fit table upload keeps caller-provided block framing."""
    with expected_protocol(
        Keysight35670A,
        [(b"CALCulate3:CFIT:DATA #14ABCD", None)],
    ) as inst:
        inst.trace3.load_cfit_data(b"#14ABCD", raw=True)


def test_trace_cfit_destination_register_setter_and_getter():
    """Verify curve-fit destination register roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:CFIT:DESTination D5", None),
         ("CALCulate1:CFIT:DESTination?", "D8")],
    ) as inst:
        inst.trace1.cfit_destination_register = 5
        assert inst.trace1.cfit_destination_register == 8


def test_trace_cfit_frequency_auto_enabled_bool_mapping():
    """Verify curve-fit frequency AUTO bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:CFIT:FREQuency:AUTO 0", None),
         ("CALCulate2:CFIT:FREQuency:AUTO?", "1")],
    ) as inst:
        inst.trace2.cfit_frequency_auto_enabled = False
        assert inst.trace2.cfit_frequency_auto_enabled is True


def test_trace_cfit_frequency_start_setter_and_getter():
    """Verify curve-fit start frequency roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:CFIT:FREQuency:STARt 10.2", None),
         ("CALCulate2:CFIT:FREQuency:STARt?", "600")],
    ) as inst:
        inst.trace2.cfit_frequency_start = 10.2
        assert inst.trace2.cfit_frequency_start == 600


def test_trace_cfit_frequency_stop_setter_and_getter():
    """Verify curve-fit stop frequency roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:CFIT:FREQuency:STOP 800", None),
         ("CALCulate2:CFIT:FREQuency:STOP?", "1.2e3")],
    ) as inst:
        inst.trace2.cfit_frequency_stop = 800
        assert inst.trace2.cfit_frequency_stop == 1.2e3


def test_trace_cfit_frequency_scale_setter_and_getter():
    """Verify curve-fit frequency scale roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:CFIT:FSCale 582699", None),
         ("CALCulate4:CFIT:FSCale?", "604144")],
    ) as inst:
        inst.trace4.cfit_frequency_scale = 582699
        assert inst.trace4.cfit_frequency_scale == 604144


def test_trace_run_curve_fit_command():
    """Verify curve-fit immediate command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:CFIT:IMMediate", None)],
    ) as inst:
        inst.trace1.run_curve_fit()


def test_trace_cfit_order_auto_enabled_bool_mapping():
    """Verify curve-fit order AUTO bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:CFIT:ORDer:AUTO 0", None),
         ("CALCulate1:CFIT:ORDer:AUTO?", "1")],
    ) as inst:
        inst.trace1.cfit_order_auto_enabled = False
        assert inst.trace1.cfit_order_auto_enabled is True


def test_trace_cfit_order_poles_setter_and_getter():
    """Verify curve-fit pole-count roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:CFIT:ORDer:POLes 14", None),
         ("CALCulate3:CFIT:ORDer:POLes?", "5")],
    ) as inst:
        inst.trace3.cfit_order_poles = 14
        assert inst.trace3.cfit_order_poles == 5


def test_trace_cfit_order_zeros_setter_and_getter():
    """Verify curve-fit zero-count roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:CFIT:ORDer:ZERos 1", None),
         ("CALCulate3:CFIT:ORDer:ZERos?", "5")],
    ) as inst:
        inst.trace3.cfit_order_zeros = 1
        assert inst.trace3.cfit_order_zeros == 5


def test_trace_cfit_time_delay_setter_and_getter():
    """Verify curve-fit time-delay roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:CFIT:TDELay -19.0035", None),
         ("CALCulate4:CFIT:TDELay?", "71.4756")],
    ) as inst:
        inst.trace4.cfit_time_delay = -19.0035
        assert inst.trace4.cfit_time_delay == 71.4756


def test_trace_cfit_weight_auto_enabled_bool_mapping():
    """Verify curve-fit weight AUTO bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:CFIT:WEIGht:AUTO 1", None),
         ("CALCulate4:CFIT:WEIGht:AUTO?", "0")],
    ) as inst:
        inst.trace4.cfit_weight_auto_enabled = True
        assert inst.trace4.cfit_weight_auto_enabled is False


def test_trace_cfit_weight_register_setter_and_getter():
    """Verify curve-fit weight register roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:CFIT:WEIGht:REGister D1", None),
         ("CALCulate4:CFIT:WEIGht:REGister?", "D7")],
    ) as inst:
        inst.trace4.cfit_weight_register = 1
        assert inst.trace4.cfit_weight_register == 7


def test_trace_copy_curve_fit_to_synthesis_command():
    """Verify synthesis copy-from-curve-fit command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:SYNThesis:COPY CFIT", None)],
    ) as inst:
        inst.trace2.copy_curve_fit_to_synthesis()


def test_trace_synthesis_data_query_parses_definite_block():
    """Verify synthesis table query parses a definite block response."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:SYNThesis:DATA?", b"#14ABCD")],
    ) as inst:
        assert inst.trace2.synthesis_data() == b"ABCD"


def test_trace_synthesis_data_query_raw():
    """Verify raw synthesis table query returns unparsed block bytes."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:SYNThesis:DATA?", b"#14ABCD")],
    ) as inst:
        assert inst.trace2.synthesis_data(raw=True) == b"#14ABCD"


def test_trace_load_synthesis_data_encodes_definite_block():
    """Verify synthesis table upload encodes data as a definite block."""
    with expected_protocol(
        Keysight35670A,
        [(b"CALCulate2:SYNThesis:DATA #14ABCD", None)],
    ) as inst:
        inst.trace2.load_synthesis_data(b"ABCD")


def test_trace_load_synthesis_data_raw():
    """Verify raw synthesis table upload keeps caller-provided block framing."""
    with expected_protocol(
        Keysight35670A,
        [(b"CALCulate2:SYNThesis:DATA #14ABCD", None)],
    ) as inst:
        inst.trace2.load_synthesis_data(b"#14ABCD", raw=True)


def test_trace_synthesis_destination_register_setter_and_getter():
    """Verify synthesis destination register roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:SYNThesis:DESTination D3", None),
         ("CALCulate3:SYNThesis:DESTination?", "D8")],
    ) as inst:
        inst.trace3.synthesis_destination_register = 3
        assert inst.trace3.synthesis_destination_register == 8


def test_trace_synthesis_frequency_scale_setter_and_getter():
    """Verify synthesis frequency scale roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:SYNThesis:FSCale 669766", None),
         ("CALCulate3:SYNThesis:FSCale?", "300318")],
    ) as inst:
        inst.trace3.synthesis_frequency_scale = 669766
        assert inst.trace3.synthesis_frequency_scale == 300318


def test_trace_synthesis_gain_setter_and_getter():
    """Verify synthesis gain roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:SYNThesis:GAIN 4.33554e+37", None),
         ("CALCulate3:SYNThesis:GAIN?", "1.3059e+37")],
    ) as inst:
        inst.trace3.synthesis_gain = 4.33554e37
        assert inst.trace3.synthesis_gain == 1.3059e37


def test_trace_synthesis_gain_rejects_zero():
    """Verify synthesis gain rejects zero as invalid value."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError):
            inst.trace1.synthesis_gain = 0


def test_trace_run_synthesis_command():
    """Verify synthesis immediate command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:SYNThesis:IMMediate", None)],
    ) as inst:
        inst.trace1.run_synthesis()


def test_trace_synthesis_spacing_setter_and_getter():
    """Verify synthesis spacing roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:SYNThesis:SPACing LOG", None),
         ("CALCulate3:SYNThesis:SPACing?", "LIN")],
    ) as inst:
        inst.trace3.synthesis_spacing = "logarithmic"
        assert inst.trace3.synthesis_spacing == "linear"


def test_trace_synthesis_time_delay_setter_and_getter():
    """Verify synthesis time-delay roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:SYNThesis:TDELay 63.7533", None),
         ("CALCulate4:SYNThesis:TDELay?", "68.8017")],
    ) as inst:
        inst.trace4.synthesis_time_delay = 63.7533
        assert inst.trace4.synthesis_time_delay == 68.8017


def test_trace_synthesis_table_type_setter_and_getter():
    """Verify synthesis table-type mapping roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:SYNThesis:TTYPe PFR", None),
         ("CALCulate2:SYNThesis:TTYPe?", "POLY")],
    ) as inst:
        inst.trace2.synthesis_table_type = "pole_fraction"
        assert inst.trace2.synthesis_table_type == "polynomial"


def test_trace_waterfall_count_setter_and_getter():
    """Verify waterfall count roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:WATerfall:COUNt 50", None),
         ("CALCulate1:WATerfall:COUNt?", "32")],
    ) as inst:
        inst.trace1.waterfall_count = 50
        assert inst.trace1.waterfall_count == 32


def test_trace_waterfall_data_query_ascii():
    """Verify waterfall data parser for ASCII data."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:WATerfall:DATA?", "1.0,2.0,3.5")],
    ) as inst:
        assert inst.trace2.waterfall_data() == [1.0, 2.0, 3.5]


def test_trace_waterfall_data_query_definite_block_ascii():
    """Verify waterfall data parser for ASCII definite-block data."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:WATerfall:DATA?", "#151,2,3")],
    ) as inst:
        assert inst.trace2.waterfall_data() == [1.0, 2.0, 3.0]


def test_trace_waterfall_data_query_raw():
    """Verify raw waterfall query returns unparsed bytes."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:WATerfall:DATA?", b"#171,2,3")],
    ) as inst:
        assert inst.trace2.waterfall_data(raw=True) == b"#171,2,3"


def test_trace_copy_waterfall_slice_to_register_command():
    """Verify waterfall slice copy command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:WATerfall:SLICe:COPY D8", None)],
    ) as inst:
        inst.trace4.copy_waterfall_slice_to_register(8)


def test_trace_copy_waterfall_slice_to_register_command_trace2():
    """Verify waterfall slice copy command keeps channel substitution for trace 2."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:WATerfall:SLICe:COPY D4", None)],
    ) as inst:
        inst.trace2.copy_waterfall_slice_to_register(4)


def test_trace_waterfall_slice_select_setter_and_getter():
    """Verify waterfall slice select roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:WATerfall:SLICe:SELect 757455", None),
         ("CALCulate1:WATerfall:SLICe:SELect?", "880661")],
    ) as inst:
        inst.trace1.waterfall_slice_select = 757455
        assert inst.trace1.waterfall_slice_select == 880661


def test_trace_waterfall_slice_select_point_setter_and_getter():
    """Verify waterfall slice point-selection roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:WATerfall:SLICe:SELect:POINt 816", None),
         ("CALCulate3:WATerfall:SLICe:SELect:POINt?", "1409")],
    ) as inst:
        inst.trace3.waterfall_slice_select_point = 816
        assert inst.trace3.waterfall_slice_select_point == 1409


def test_trace_copy_waterfall_trace_to_register_command():
    """Verify waterfall trace copy command."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:WATerfall:TRACe:COPY D7", None)],
    ) as inst:
        inst.trace3.copy_waterfall_trace_to_register(7)


def test_trace_copy_waterfall_trace_to_register_command_trace2():
    """Verify waterfall trace copy command keeps channel substitution for trace 2."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate2:WATerfall:TRACe:COPY D5", None)],
    ) as inst:
        inst.trace2.copy_waterfall_trace_to_register(5)


def test_trace_waterfall_trace_select_setter_and_getter():
    """Verify waterfall trace selection by Z-axis value roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate1:WATerfall:TRACe:SELect 3.5", None),
         ("CALCulate1:WATerfall:TRACe:SELect?", "10")],
    ) as inst:
        inst.trace1.waterfall_trace_select = 3.5
        assert inst.trace1.waterfall_trace_select == 10


def test_trace_waterfall_trace_select_point_setter_and_getter():
    """Verify waterfall trace selection by point index roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate4:WATerfall:TRACe:SELect:POINt 15879", None),
         ("CALCulate4:WATerfall:TRACe:SELect:POINt?", "4104")],
    ) as inst:
        inst.trace4.waterfall_trace_select_point = 15879
        assert inst.trace4.waterfall_trace_select_point == 4104


def test_trace_db_reference_mapping():
    """Verify dB reference mapping."""
    with expected_protocol(
        Keysight35670A,
        [("CALCulate3:UNIT:DBReference DBV", None)],
    ) as inst:
        inst.trace3.db_reference = "dbv"


def test_operation_condition_query():
    """Verify operation condition query."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:OPERation:CONDition?", "42")],
    ) as inst:
        assert inst.operation_condition == 42


def test_questionable_condition_query():
    """Verify questionable condition query."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:QUEStionable:CONDition?", "5")],
    ) as inst:
        assert inst.questionable_condition == 5


def test_device_condition_query():
    """Verify device condition query."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:DEVice:CONDition?", "3")],
    ) as inst:
        assert inst.device_condition == 3


def test_status_preset_command():
    """Verify status preset command."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:PRESet", None)],
    ) as inst:
        inst.status_preset()


def test_device_enable_setter_and_getter():
    """Verify device enable mask roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:DEVice:ENABle 3", None),
         ("STATus:DEVice:ENABle?", "5")],
    ) as inst:
        inst.device_enable = 3
        assert inst.device_enable == 5


def test_device_event_query():
    """Verify device event query."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:DEVice:EVENt?", "1")],
    ) as inst:
        assert inst.device_event == 1


def test_device_negative_transition_setter_and_getter():
    """Verify device negative transition mask roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:DEVice:NTRansition 2", None),
         ("STATus:DEVice:NTRansition?", "6")],
    ) as inst:
        inst.device_negative_transition = 2
        assert inst.device_negative_transition == 6


def test_device_positive_transition_setter_and_getter():
    """Verify device positive transition mask roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:DEVice:PTRansition 9", None),
         ("STATus:DEVice:PTRansition?", "10")],
    ) as inst:
        inst.device_positive_transition = 9
        assert inst.device_positive_transition == 10


def test_operation_enable_setter_and_getter():
    """Verify operation enable mask roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:OPERation:ENABle 4", None),
         ("STATus:OPERation:ENABle?", "7")],
    ) as inst:
        inst.operation_enable = 4
        assert inst.operation_enable == 7


def test_operation_event_query():
    """Verify operation event query."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:OPERation:EVENt?", "8")],
    ) as inst:
        assert inst.operation_event == 8


def test_operation_negative_transition_setter_and_getter():
    """Verify operation negative transition mask roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:OPERation:NTRansition 1", None),
         ("STATus:OPERation:NTRansition?", "11")],
    ) as inst:
        inst.operation_negative_transition = 1
        assert inst.operation_negative_transition == 11


def test_operation_positive_transition_setter_and_getter():
    """Verify operation positive transition mask roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:OPERation:PTRansition 12", None),
         ("STATus:OPERation:PTRansition?", "13")],
    ) as inst:
        inst.operation_positive_transition = 12
        assert inst.operation_positive_transition == 13


def test_questionable_enable_setter_and_getter():
    """Verify questionable enable mask roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:QUEStionable:ENABle 14", None),
         ("STATus:QUEStionable:ENABle?", "15")],
    ) as inst:
        inst.questionable_enable = 14
        assert inst.questionable_enable == 15


def test_questionable_event_query():
    """Verify questionable event query."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:QUEStionable:EVENt?", "16")],
    ) as inst:
        assert inst.questionable_event == 16


def test_questionable_negative_transition_setter_and_getter():
    """Verify questionable negative transition mask roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:QUEStionable:NTRansition 17", None),
         ("STATus:QUEStionable:NTRansition?", "18")],
    ) as inst:
        inst.questionable_negative_transition = 17
        assert inst.questionable_negative_transition == 18


def test_questionable_positive_transition_setter_and_getter():
    """Verify questionable positive transition mask roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:QUEStionable:PTRansition 19", None),
         ("STATus:QUEStionable:PTRansition?", "20")],
    ) as inst:
        inst.questionable_positive_transition = 19
        assert inst.questionable_positive_transition == 20


def test_questionable_limit_condition_query():
    """Verify questionable limit condition query."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:QUEStionable:LIMit:CONDition?", "21")],
    ) as inst:
        assert inst.questionable_limit_condition == 21


def test_questionable_limit_enable_setter_and_getter():
    """Verify questionable limit enable mask roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:QUEStionable:LIMit:ENABle 22", None),
         ("STATus:QUEStionable:LIMit:ENABle?", "23")],
    ) as inst:
        inst.questionable_limit_enable = 22
        assert inst.questionable_limit_enable == 23


def test_questionable_limit_event_query():
    """Verify questionable limit event query."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:QUEStionable:LIMit:EVENt?", "24")],
    ) as inst:
        assert inst.questionable_limit_event == 24


def test_questionable_limit_negative_transition_setter_and_getter():
    """Verify questionable limit negative transition mask roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:QUEStionable:LIMit:NTRansition 25", None),
         ("STATus:QUEStionable:LIMit:NTRansition?", "26")],
    ) as inst:
        inst.questionable_limit_negative_transition = 25
        assert inst.questionable_limit_negative_transition == 26


def test_questionable_limit_positive_transition_setter_and_getter():
    """Verify questionable limit positive transition mask roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:QUEStionable:LIMit:PTRansition 27", None),
         ("STATus:QUEStionable:LIMit:PTRansition?", "28")],
    ) as inst:
        inst.questionable_limit_positive_transition = 27
        assert inst.questionable_limit_positive_transition == 28


def test_questionable_voltage_condition_query():
    """Verify questionable voltage condition query."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:QUEStionable:VOLTage:CONDition?", "29")],
    ) as inst:
        assert inst.questionable_voltage_condition == 29


def test_questionable_voltage_enable_setter_and_getter():
    """Verify questionable voltage enable mask roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:QUEStionable:VOLTage:ENABle 30", None),
         ("STATus:QUEStionable:VOLTage:ENABle?", "31")],
    ) as inst:
        inst.questionable_voltage_enable = 30
        assert inst.questionable_voltage_enable == 31


def test_questionable_voltage_event_query():
    """Verify questionable voltage event query."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:QUEStionable:VOLTage:EVENt?", "32")],
    ) as inst:
        assert inst.questionable_voltage_event == 32


def test_questionable_voltage_negative_transition_setter_and_getter():
    """Verify questionable voltage negative transition mask roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:QUEStionable:VOLTage:NTRansition 33", None),
         ("STATus:QUEStionable:VOLTage:NTRansition?", "34")],
    ) as inst:
        inst.questionable_voltage_negative_transition = 33
        assert inst.questionable_voltage_negative_transition == 34


def test_questionable_voltage_positive_transition_setter_and_getter():
    """Verify questionable voltage positive transition mask roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:QUEStionable:VOLTage:PTRansition 35", None),
         ("STATus:QUEStionable:VOLTage:PTRansition?", "36")],
    ) as inst:
        inst.questionable_voltage_positive_transition = 35
        assert inst.questionable_voltage_positive_transition == 36


def test_user_status_enable_setter_and_getter():
    """Verify user status enable mask roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:USER:ENABle 37", None),
         ("STATus:USER:ENABle?", "38")],
    ) as inst:
        inst.user_status_enable = 37
        assert inst.user_status_enable == 38


def test_user_status_event_query():
    """Verify user status event query."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:USER:EVENt?", "39")],
    ) as inst:
        assert inst.user_status_event == 39


def test_pulse_user_status_command():
    """Verify user status pulse command."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:USER:PULSe 32", None)],
    ) as inst:
        inst.pulse_user_status(32)


def test_user_status_pulse_alias_command():
    """Verify user status pulse alias command."""
    with expected_protocol(
        Keysight35670A,
        [("STATus:USER:PULSe 8", None)],
    ) as inst:
        inst.user_status_pulse(8)


def test_data_format_mapping():
    """Verify FORMat:DATA mapping helper."""
    with expected_protocol(
        Keysight35670A,
        [("FORMat:DATA REAL", None),
         ("FORMat:DATA?", "ASC,12")],
    ) as inst:
        inst.data_format = "real"
        assert inst.data_format == "ascii"


def test_read_trace_raw_data_ascii():
    """Verify reading trace data register values in ASCII format."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:DATA? D2", "1.0,2.0")],
    ) as inst:
        assert inst.read_trace_raw_data(register=2) == [1.0, 2.0]


def test_read_trace_raw_data_raw_bytes():
    """Verify reading raw trace register bytes."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:DATA? D4", b"#14ABCD")],
    ) as inst:
        assert inst.read_trace_raw_data(register="D4", raw=True) == b"#14ABCD"


def test_write_trace_raw_data_from_source_token():
    """Verify writing trace register from another trace source token."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:DATA D1, TRACe2", None)],
    ) as inst:
        inst.write_trace_raw_data("TRACe2", register=1)


def test_write_trace_raw_data_ascii_values():
    """Verify writing ASCII numeric values to a trace data register."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:DATA D3, 1,2.5,-3", None)],
    ) as inst:
        inst.write_trace_raw_data([1, 2.5, -3], register="D3")


def test_write_trace_raw_data_float_value():
    """Verify writing scalar float values to a trace data register."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:DATA D1, 1.5", None)],
    ) as inst:
        inst.write_trace_raw_data(1.5, register=1)


def test_write_trace_raw_data_encodes_definite_block():
    """Verify writing bytes auto-encodes to definite block for TRACe:DATA."""
    with expected_protocol(
        Keysight35670A,
        [(b"TRACe:DATA D4,#14ABCD", None)],
    ) as inst:
        inst.write_trace_raw_data(b"ABCD", register=4)


def test_write_trace_raw_data_raw_block_passthrough():
    """Verify writing raw pre-framed block for TRACe:DATA."""
    with expected_protocol(
        Keysight35670A,
        [(b"TRACe:DATA D4,#14ABCD", None)],
    ) as inst:
        inst.write_trace_raw_data(b"#14ABCD", register=4, raw=True)


def test_write_trace_raw_data_invalid_type_raises():
    """Verify writing unsupported TRACe:DATA payload type raises TypeError."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(TypeError):
            inst.write_trace_raw_data(object(), register=1)


def test_read_trace_x_data_ascii():
    """Verify trace X-axis data read helper."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:X:DATA?", "10,20,30")],
    ) as inst:
        assert inst.read_trace_x_data() == [10.0, 20.0, 30.0]


def test_read_trace_x_data_raw_bytes():
    """Verify raw trace X-axis data read helper."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:X:DATA?", b"#14ABCD")],
    ) as inst:
        assert inst.read_trace_x_data(raw=True) == b"#14ABCD"


def test_read_trace_x_unit():
    """Verify trace X-axis unit read helper."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:X:UNIT?", "HZ")],
    ) as inst:
        assert inst.read_trace_x_unit() == "HZ"


def test_read_trace_z_data_ascii():
    """Verify trace Z-axis data read helper."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:Z:DATA?", "0.25,0.5")],
    ) as inst:
        assert inst.read_trace_z_data() == [0.25, 0.5]


def test_read_trace_z_data_raw_bytes():
    """Verify raw trace Z-axis data read helper."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:Z:DATA?", b"#14ABCD")],
    ) as inst:
        assert inst.read_trace_z_data(raw=True) == b"#14ABCD"


def test_read_trace_z_unit():
    """Verify trace Z-axis unit read helper."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:Z:UNIT?", "VOLT")],
    ) as inst:
        assert inst.read_trace_z_unit() == "VOLT"


def test_read_trace_waterfall_data_ascii():
    """Verify trace waterfall data read helper."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:WATerfall:DATA?", "1.0,2.0,3.0")],
    ) as inst:
        assert inst.read_trace_waterfall_data() == [1.0, 2.0, 3.0]


def test_read_trace_waterfall_data_raw_bytes():
    """Verify raw trace waterfall data read helper."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:WATerfall:DATA?", b"#14ABCD")],
    ) as inst:
        assert inst.read_trace_waterfall_data(raw=True) == b"#14ABCD"


def test_write_trace_waterfall_data_from_source_token():
    """Verify writing waterfall register from a trace source token."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:WATerfall:DATA W2, TRACe3", None)],
    ) as inst:
        inst.write_trace_waterfall_data("TRACe3", register=2)


def test_write_trace_waterfall_data_ascii_values():
    """Verify writing ASCII numeric values to waterfall register."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:WATerfall:DATA W3, 1,2.5,-3", None)],
    ) as inst:
        inst.write_trace_waterfall_data([1, 2.5, -3], register="W3")


def test_write_trace_waterfall_data_float_value():
    """Verify writing scalar float values to a waterfall register."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:WATerfall:DATA W1, 1.5", None)],
    ) as inst:
        inst.write_trace_waterfall_data(1.5, register=1)


def test_write_trace_waterfall_data_encodes_definite_block():
    """Verify writing bytes auto-encodes to definite block for TRACe:WATerfall:DATA."""
    with expected_protocol(
        Keysight35670A,
        [(b"TRACe:WATerfall:DATA W4,#14ABCD", None)],
    ) as inst:
        inst.write_trace_waterfall_data(b"ABCD", register=4)


def test_write_trace_waterfall_data_raw_block_passthrough():
    """Verify writing raw pre-framed block for TRACe:WATerfall:DATA."""
    with expected_protocol(
        Keysight35670A,
        [(b"TRACe:WATerfall:DATA W4,#14ABCD", None)],
    ) as inst:
        inst.write_trace_waterfall_data(b"#14ABCD", register=4, raw=True)


def test_write_trace_waterfall_data_invalid_type_raises():
    """Verify writing unsupported waterfall payload type raises TypeError."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(TypeError):
            inst.write_trace_waterfall_data(object(), register=1)


def test_trace_data_transfer_wrapper():
    """Verify backward-compatible trace_data wrapper."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:DATA? D2", "1.0,2.0")],
    ) as inst:
        assert inst.trace_data(2) == [1.0, 2.0]


def test_trace_x_data_transfer_wrapper():
    """Verify backward-compatible trace_x_data wrapper."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:X:DATA?", "10,20,30")],
    ) as inst:
        assert inst.trace_x_data(3) == [10.0, 20.0, 30.0]


def test_trace_z_data_transfer_wrapper():
    """Verify backward-compatible trace_z_data wrapper."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:Z:DATA?", "0.25,0.5")],
    ) as inst:
        assert inst.trace_z_data() == [0.25, 0.5]


def test_trace_x_unit_transfer_wrapper():
    """Verify backward-compatible trace_x_unit wrapper."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:X:UNIT?", "HZ")],
    ) as inst:
        assert inst.trace_x_unit("D1") == "HZ"


def test_trace_z_unit_transfer_wrapper():
    """Verify backward-compatible trace_z_unit wrapper."""
    with expected_protocol(
        Keysight35670A,
        [("TRACe:Z:UNIT?", "VOLT")],
    ) as inst:
        assert inst.trace_z_unit(4) == "VOLT"


def test_beep_command():
    """Verify beeper command."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:BEEPer:IMMediate", None)],
    ) as inst:
        inst.beep()


def test_beeper_enabled_bool_mapping():
    """Verify beeper enabled bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:BEEPer:STATe 1", None)],
    ) as inst:
        inst.beeper_enabled = True


def test_gpib_address_setter():
    """Verify GPIB address setter."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:COMMunicate:GPIB:ADDRess 14", None)],
    ) as inst:
        inst.gpib_address = 14


def test_gpib_address_query():
    """Verify GPIB address query."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:COMMunicate:GPIB:ADDRess?", "14")],
    ) as inst:
        assert inst.gpib_address == 14


def test_serial_receive_baud_setter_and_getter():
    """Verify serial receive baud roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:COMMunicate:SERial:RECeive:BAUD 9600", None),
         ("SYSTem:COMMunicate:SERial:RECeive:BAUD?", "1200")],
    ) as inst:
        inst.serial_receive_baud = 9600
        assert inst.serial_receive_baud == 1200


def test_serial_receive_bits_setter_and_getter():
    """Verify serial receive bits roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:COMMunicate:SERial:RECeive:BITS 8", None),
         ("SYSTem:COMMunicate:SERial:RECeive:BITS?", "7")],
    ) as inst:
        inst.serial_receive_bits = 8
        assert inst.serial_receive_bits == 7


def test_serial_receive_pace_setter_and_getter():
    """Verify serial receive pacing roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:COMMunicate:SERial:RECeive:PACE XON", None),
         ("SYSTem:COMMunicate:SERial:RECeive:PACE?", "NONE")],
    ) as inst:
        inst.serial_receive_pace = "xon"
        assert inst.serial_receive_pace == "none"


def test_serial_receive_parity_check_setter_and_getter():
    """Verify serial receive parity-check bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:COMMunicate:SERial:RECeive:PARity:CHECk 1", None),
         ("SYSTem:COMMunicate:SERial:RECeive:PARity:CHECk?", "0")],
    ) as inst:
        inst.serial_receive_parity_check_enabled = True
        assert inst.serial_receive_parity_check_enabled is False


def test_serial_receive_parity_setter_and_getter():
    """Verify serial receive parity roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:COMMunicate:SERial:RECeive:PARity ODD", None),
         ("SYSTem:COMMunicate:SERial:RECeive:PARity?", "EVEN")],
    ) as inst:
        inst.serial_receive_parity = "odd"
        assert inst.serial_receive_parity == "even"


def test_serial_receive_stop_bits_setter_and_getter():
    """Verify serial receive stop bits roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:COMMunicate:SERial:RECeive:SBITs 2", None),
         ("SYSTem:COMMunicate:SERial:RECeive:SBITs?", "1")],
    ) as inst:
        inst.serial_receive_stop_bits = 2
        assert inst.serial_receive_stop_bits == 1


def test_serial_transmit_pace_setter_and_getter():
    """Verify serial transmit pacing roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:COMMunicate:SERial:TRANsmit:PACE DSR", None),
         ("SYSTem:COMMunicate:SERial:TRANsmit:PACE?", "XON")],
    ) as inst:
        inst.serial_transmit_pace = "dsr"
        assert inst.serial_transmit_pace == "xon"


def test_system_date_setter_and_getter():
    """Verify system date roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:DATE 1993,9,27", None),
         ("SYSTem:DATE?", "1994,12,25")],
    ) as inst:
        inst.system_date = (1993, 9, 27)
        assert inst.system_date == (1994, 12, 25)


def test_system_time_setter_and_getter():
    """Verify system time roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:TIME 15,5,0", None),
         ("SYSTem:TIME?", "9,30,45")],
    ) as inst:
        inst.system_time = (15, 5, 0)
        assert inst.system_time == (9, 30, 45)


def test_fan_state_setter_and_getter():
    """Verify fan-state roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:FAN:STATe FULL", None),
         ("SYSTem:FAN:STATe?", "AUTO")],
    ) as inst:
        inst.fan_state = "full"
        assert inst.fan_state == "auto"


def test_key_code_setter_and_getter():
    """Verify key-code command/query roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:KEY 21", None),
         ("SYSTem:KEY?", "53")],
    ) as inst:
        inst.key_code = 21
        assert inst.key_code == 53


def test_key_lock_enabled_bool_mapping():
    """Verify key lock bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:KLOCk 1", None)],
    ) as inst:
        inst.key_lock_enabled = True


def test_keyboard_locked_setter_and_getter():
    """Verify keyboard lock roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:KLOCk 1", None),
         ("SYSTem:KLOCk?", "0")],
    ) as inst:
        inst.keyboard_locked = True
        assert inst.keyboard_locked is False


def test_power_source_query():
    """Verify power source query."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:POWer:SOURce?", "AC")],
    ) as inst:
        assert inst.power_source == "AC"


def test_power_state_query():
    """Verify power state query."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:POWer:STATe?", "1")],
    ) as inst:
        assert inst.power_state == 1


def test_system_version_query():
    """Verify system version query."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:VERSion?", "A.01.11")],
    ) as inst:
        assert inst.system_version == "A.01.11"


def test_long_test_result_query():
    """Verify long confidence test-result query."""
    with expected_protocol(
        Keysight35670A,
        [("TEST:LONG:RESult?", "1")],
    ) as inst:
        assert inst.long_test_result == 1


def test_clear_test_log_requires_confirmation():
    """Verify test-log clear requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.clear_test_log()


def test_clear_test_log_command():
    """Verify test-log clear command."""
    with expected_protocol(
        Keysight35670A,
        [("TEST:LOG:CLEar", None)],
    ) as inst:
        inst.clear_test_log(confirmed=True)


def test_run_long_test_requires_confirmation():
    """Verify long test requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.run_long_test()


def test_run_long_test_command():
    """Verify long confidence test command."""
    with expected_protocol(
        Keysight35670A,
        [("TEST:LONG", None)],
    ) as inst:
        inst.run_long_test(confirmed=True)


def test_clear_fault_log_requires_confirmation():
    """Verify fault-log clear requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.clear_fault_log()


def test_clear_fault_log_command():
    """Verify fault-log clear command."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:FLOG:CLEar", None)],
    ) as inst:
        inst.clear_fault_log(confirmed=True)


def test_power_off_requires_confirmation():
    """Verify power-off requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.power_off()


def test_power_off_command():
    """Verify power-off command."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:POWer:STATe OFF", None)],
    ) as inst:
        inst.power_off(confirmed=True)


def test_system_preset_requires_confirmation():
    """Verify system preset requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.system_preset()


def test_system_preset_command():
    """Verify system preset command."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:PRESet", None)],
    ) as inst:
        inst.system_preset(confirmed=True)


def test_system_state_data_query_parses_definite_block():
    """Verify system-state query parses a definite block response."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:SET?", b"#14ABCD")],
    ) as inst:
        assert inst.system_state_data() == b"ABCD"


def test_system_state_data_query_raw():
    """Verify raw system-state query response."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:SET?", b"#14ABCD")],
    ) as inst:
        assert inst.system_state_data(raw=True) == b"#14ABCD"


def test_load_system_state_encodes_definite_block():
    """Verify system-state load encodes data as a definite block."""
    with expected_protocol(
        Keysight35670A,
        [(b"SYSTem:SET #14ABCD", None)],
    ) as inst:
        inst.load_system_state(b"ABCD")


def test_load_system_state_raw_writes_block_as_is():
    """Verify raw system-state load writes block bytes unchanged."""
    with expected_protocol(
        Keysight35670A,
        [(b"SYSTem:SET #14ABCD", None)],
    ) as inst:
        inst.load_system_state(b"#14ABCD", raw=True)


def test_frequency_span():
    """Verify the frequency span setter and getter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:FREQuency:SPAN 2000", None),
         ("SENSe:FREQuency:SPAN?", 2500)],
    ) as inst:
        inst.frequency_span = 2000.0
        assert inst.frequency_span == 2500.0


def test_sense_feed_mapping():
    """Verify sense feed mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:FEED TCAP", None),
         ("SENSe:FEED?", "INP")],
    ) as inst:
        inst.sense_feed = "time_capture"
        assert inst.sense_feed == "input"


def test_sense_data_frequency_start_query():
    """Verify sense data frequency start query."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:DATA:HEADer:FREQuency:STARt?", "0.0")],
    ) as inst:
        assert inst.sense_data_frequency_start == 0.0


def test_sense_data_frequency_stop_query():
    """Verify sense data frequency stop query."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:DATA:HEADer:FREQuency:STOP?", "102400.0")],
    ) as inst:
        assert inst.sense_data_frequency_stop == 102400.0


def test_sense_data_points_query():
    """Verify sense data points query helper."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:DATA:HEADer:POINts? TCAP3", "4096")],
    ) as inst:
        assert inst.sense_data_points(3) == 4096


def test_sense_data_query_parses_definite_block():
    """Verify sense data query parses a definite block response."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:DATA? TCAP2", b"#14ABCD")],
    ) as inst:
        assert inst.sense_data(2) == b"ABCD"


def test_sense_data_query_raw():
    """Verify sense data query raw response."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:DATA? TCAP2", b"#14ABCD")],
    ) as inst:
        assert inst.sense_data(2, raw=True) == b"#14ABCD"


def test_set_sense_data_encodes_definite_block():
    """Verify sense data upload encodes data as a definite block."""
    with expected_protocol(
        Keysight35670A,
        [(b"SENSe:DATA TCAP2,#14ABCD", None)],
    ) as inst:
        inst.set_sense_data(b"ABCD", 2)


def test_set_sense_data_raw_writes_block_as_is():
    """Verify raw sense data upload writes block bytes unchanged."""
    with expected_protocol(
        Keysight35670A,
        [(b"SENSe:DATA TCAP2,#14ABCD", None)],
    ) as inst:
        inst.set_sense_data(b"#14ABCD", 2, raw=True)


def test_sense_data_range_query():
    """Verify sense data range query helper."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:DATA:RANGe? TCAP1", "1500")],
    ) as inst:
        assert inst.sense_data_range(1) == 1500.0


def test_set_sense_data_range_command():
    """Verify sense data range setter helper."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:DATA:RANGe TCAP1, 1500", None)],
    ) as inst:
        inst.set_sense_data_range(1, 1500.0)


def test_frequency_block_size_setter_and_getter():
    """Verify frequency block-size roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:FREQuency:BLOCksize 1024", None),
         ("SENSe:FREQuency:BLOCksize?", "512")],
    ) as inst:
        inst.frequency_block_size = 1024
        assert inst.frequency_block_size == 512


def test_frequency_center_setter_and_getter():
    """Verify frequency center roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:FREQuency:CENTer 1000", None),
         ("SENSe:FREQuency:CENTer?", "2000")],
    ) as inst:
        inst.frequency_center = 1000.0
        assert inst.frequency_center == 2000.0


def test_frequency_manual_setter():
    """Verify frequency manual setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:FREQuency:MANual 123.5", None)],
    ) as inst:
        inst.frequency_manual = 123.5


def test_frequency_resolution_setter():
    """Verify frequency resolution setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:FREQuency:RESolution 400", None)],
    ) as inst:
        inst.frequency_resolution = 400.0


def test_frequency_resolution_auto_enabled_bool_mapping():
    """Verify frequency resolution auto bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:FREQuency:RESolution:AUTO 1", None),
         ("SENSe:FREQuency:RESolution:AUTO?", "0")],
    ) as inst:
        inst.frequency_resolution_auto_enabled = True
        assert inst.frequency_resolution_auto_enabled is False


def test_frequency_resolution_auto_max_change_setter():
    """Verify frequency resolution auto max-change setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:FREQuency:RESolution:AUTO:MCHange 2", None)],
    ) as inst:
        inst.frequency_resolution_auto_max_change = 2.0


def test_frequency_resolution_auto_minimum_setter():
    """Verify frequency resolution auto minimum setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:FREQuency:RESolution:AUTO:MINimum 200", None)],
    ) as inst:
        inst.frequency_resolution_auto_minimum = 200.0


def test_frequency_resolution_octave_mapping():
    """Verify frequency resolution octave mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:FREQuency:RESolution:OCTave THIR", None),
         ("SENSe:FREQuency:RESolution:OCTave?", "TWEL")],
    ) as inst:
        inst.frequency_resolution_octave = "third"
        assert inst.frequency_resolution_octave == "twelfth"


def test_set_full_frequency_span_command():
    """Verify full frequency span command."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:FREQuency:SPAN:FULL", None)],
    ) as inst:
        inst.set_full_frequency_span()


def test_frequency_span_link_mapping():
    """Verify frequency span link mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:FREQuency:SPAN:LINK CENT", None),
         ("SENSe:FREQuency:SPAN:LINK?", "STAR")],
    ) as inst:
        inst.frequency_span_link = "center"
        assert inst.frequency_span_link == "start"


def test_frequency_start_setter():
    """Verify frequency start setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:FREQuency:STARt 10", None)],
    ) as inst:
        inst.frequency_start = 10.0


def test_frequency_step_increment_setter():
    """Verify frequency step increment setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:FREQuency:STEP:INCRement 100", None)],
    ) as inst:
        inst.frequency_step_increment = 100.0


def test_frequency_stop_setter():
    """Verify frequency stop setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:FREQuency:STOP 10000", None)],
    ) as inst:
        inst.frequency_stop = 10000.0


def test_sweep_direction_mapping():
    """Verify sweep direction mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:SWEep:DIRection DOWN", None),
         ("SENSe:SWEep:DIRection?", "UP")],
    ) as inst:
        inst.sweep_direction = "down"
        assert inst.sweep_direction == "up"


def test_sweep_dwell_setter():
    """Verify sweep dwell setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:SWEep:DWELl 0.01", None)],
    ) as inst:
        inst.sweep_dwell = 0.01


def test_sweep_mode_mapping():
    """Verify sweep mode mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:SWEep:MODE MAN", None),
         ("SENSe:SWEep:MODE?", "AUTO")],
    ) as inst:
        inst.sweep_mode = "manual"
        assert inst.sweep_mode == "auto"


def test_sweep_overlap_setter():
    """Verify sweep overlap setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:SWEep:OVERlap 33", None)],
    ) as inst:
        inst.sweep_overlap = 33


def test_sweep_spacing_mapping():
    """Verify sweep spacing mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:SWEep:SPACing LOG", None),
         ("SENSe:SWEep:SPACing?", "LIN")],
    ) as inst:
        inst.sweep_spacing = "logarithmic"
        assert inst.sweep_spacing == "linear"


def test_sweep_settling_time_setter():
    """Verify sweep settling time setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:SWEep:STIMe 0.005", None)],
    ) as inst:
        inst.sweep_settling_time = 0.005


def test_sweep_time_setter():
    """Verify sweep time setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:SWEep:TIME 0.125", None)],
    ) as inst:
        inst.sweep_time = 0.125


def test_histogram_bins_setter_and_getter():
    """Verify histogram bins roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:HISTogram:BINS 400", None),
         ("SENSe:HISTogram:BINS?", "512")],
    ) as inst:
        inst.histogram_bins = 400
        assert inst.histogram_bins == 512


def test_order_maximum_setter_and_getter():
    """Verify order maximum roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:ORDer:MAXimum 10", None),
         ("SENSe:ORDer:MAXimum?", "20")],
    ) as inst:
        inst.order_maximum = 10.0
        assert inst.order_maximum == 20.0


def test_order_resolution_setter():
    """Verify order resolution setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:ORDer:RESolution 0.1", None)],
    ) as inst:
        inst.order_resolution = 0.1


def test_order_track_resolution_setter():
    """Verify order track resolution setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:ORDer:RESolution:TRACk 15", None)],
    ) as inst:
        inst.order_track_resolution = 15


def test_order_rpm_maximum_setter():
    """Verify order RPM maximum setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:ORDer:RPM:MAXimum 6000", None)],
    ) as inst:
        inst.order_rpm_maximum = 6000.0


def test_order_rpm_minimum_setter():
    """Verify order RPM minimum setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:ORDer:RPM:MINimum 600", None)],
    ) as inst:
        inst.order_rpm_minimum = 600.0


def test_reference_channels_mapping():
    """Verify reference channels mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:REFerence PAIR", None),
         ("SENSe:REFerence?", "SING")],
    ) as inst:
        inst.reference_channels = "pair"
        assert inst.reference_channels == "single"


def test_overload_rejection_enabled_bool_mapping():
    """Verify overload rejection bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:REJect:STATe 1", None),
         ("SENSe:REJect:STATe?", "0")],
    ) as inst:
        inst.overload_rejection_enabled = True
        assert inst.overload_rejection_enabled is False


def test_time_capture_length_setter_and_getter():
    """Verify time capture length roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:TCAPture:LENGth 1", None),
         ("SENSe:TCAPture:LENGth?", "2")],
    ) as inst:
        inst.time_capture_length = 1.0
        assert inst.time_capture_length == 2.0


def test_time_capture_start_channels_setter():
    """Verify all time capture start channel setters."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:TCAPture:STARt1 0.1", None),
         ("SENSe:TCAPture:STARt2 0.2", None),
         ("SENSe:TCAPture:STARt3 0.3", None),
         ("SENSe:TCAPture:STARt4 0.4", None)],
    ) as inst:
        inst.time_capture_start1 = 0.1
        inst.time_capture_start2 = 0.2
        inst.time_capture_start3 = 0.3
        inst.time_capture_start4 = 0.4


def test_time_capture_stop_channels_setter():
    """Verify all time capture stop channel setters."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:TCAPture:STOP1 1.1", None),
         ("SENSe:TCAPture:STOP2 1.2", None),
         ("SENSe:TCAPture:STOP3 1.3", None),
         ("SENSe:TCAPture:STOP4 1.4", None)],
    ) as inst:
        inst.time_capture_stop1 = 1.1
        inst.time_capture_stop2 = 1.2
        inst.time_capture_stop3 = 1.3
        inst.time_capture_stop4 = 1.4


def test_time_capture_tachometer_rpm_maximum_setter():
    """Verify time capture tachometer RPM maximum setter."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:TCAPture:TACHometer:RPM:MAXimum 6000", None)],
    ) as inst:
        inst.time_capture_tachometer_rpm_maximum = 6000.0


def test_time_capture_tachometer_enabled_bool_mapping():
    """Verify time capture tachometer bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:TCAPture:TACHometer:STATe 1", None),
         ("SENSe:TCAPture:TACHometer:STATe?", "0")],
    ) as inst:
        inst.time_capture_tachometer_enabled = True
        assert inst.time_capture_tachometer_enabled is False


def test_abort_time_capture_command():
    """Verify abort time capture command."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:TCAPture:ABORt", None)],
    ) as inst:
        inst.abort_time_capture()


def test_delete_time_capture_requires_confirmation():
    """Verify delete time capture requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.delete_time_capture()


def test_delete_time_capture_command():
    """Verify delete time capture command."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:TCAPture:DELete", None)],
    ) as inst:
        inst.delete_time_capture(confirmed=True)


def test_start_time_capture_command():
    """Verify start time capture command."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:TCAPture:IMMediate", None)],
    ) as inst:
        inst.start_time_capture()


def test_allocate_time_capture_memory_command():
    """Verify allocate time capture memory command."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:TCAPture:MALLocate", None)],
    ) as inst:
        inst.allocate_time_capture_memory()


def test_time_capture_file_query_parses_definite_block():
    """Verify time capture file query parses a definite block response."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:TCAPture:FILE?", b"#14ABCD")],
    ) as inst:
        assert inst.time_capture_file() == b"ABCD"


def test_time_capture_file_query_raw():
    """Verify raw time capture file query response."""
    with expected_protocol(
        Keysight35670A,
        [("SENSe:TCAPture:FILE?", b"#14ABCD")],
    ) as inst:
        assert inst.time_capture_file(raw=True) == b"#14ABCD"


def test_load_time_capture_file_encodes_definite_block():
    """Verify time capture file load encodes data as a definite block."""
    with expected_protocol(
        Keysight35670A,
        [(b"SENSe:TCAPture:FILE #14ABCD", None)],
    ) as inst:
        inst.load_time_capture_file(b"ABCD")


def test_load_time_capture_file_raw_writes_block_as_is():
    """Verify raw time capture file load writes block bytes unchanged."""
    with expected_protocol(
        Keysight35670A,
        [(b"SENSe:TCAPture:FILE #14ABCD", None)],
    ) as inst:
        inst.load_time_capture_file(b"#14ABCD", raw=True)


def test_abort():
    """Verify abort command."""
    with expected_protocol(
        Keysight35670A,
        [("ABORt", None)],
    ) as inst:
        inst.abort()


def test_initiate():
    """Verify initiate command."""
    with expected_protocol(
        Keysight35670A,
        [("INITiate:IMMediate", None)],
    ) as inst:
        inst.initiate()


def test_restart_measurement_sequence():
    """Verify restart command."""
    with expected_protocol(
        Keysight35670A,
        [("ABORt;:INITiate:IMMediate", None)],
    ) as inst:
        inst.restart_measurement()


def test_wait_for_completion():
    """Verify wait for completion command."""
    with expected_protocol(
        Keysight35670A,
        [("*OPC?", "1")],
    ) as inst:
        assert inst.wait_for_completion() == 1


def test_wait_for_completion_zero_response():
    """Verify wait for completion keeps an explicit zero response as integer 0."""
    with expected_protocol(
        Keysight35670A,
        [("*OPC?", "0")],
    ) as inst:
        assert inst.wait_for_completion() == 0


def test_wait_command():
    """Verify wait command."""
    with expected_protocol(
        Keysight35670A,
        [("*WAI", None)],
    ) as inst:
        inst.wait()


def test_operation_complete():
    """Verify operation complete query."""
    with expected_protocol(
        Keysight35670A,
        [("*OPC?", "1")],
    ) as inst:
        assert inst.operation_complete() == 1


def test_operation_complete_zero_response():
    """Verify operation complete query does not treat '0' as truthy."""
    with expected_protocol(
        Keysight35670A,
        [("*OPC?", "0")],
    ) as inst:
        result = inst.operation_complete()
        assert result == 0
        assert bool(result) is False


def test_self_test_result_query():
    """Verify self-test query."""
    with expected_protocol(
        Keysight35670A,
        [("*TST?", "0")],
    ) as inst:
        assert inst.self_test_result == 0


def test_run_self_calibration_requires_confirmation():
    """Verify self calibration requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.run_self_calibration()


def test_run_self_calibration():
    """Verify self calibration command helper."""
    with expected_protocol(
        Keysight35670A,
        [("*CAL?", "0")],
    ) as inst:
        assert inst.run_self_calibration(confirmed=True) == 0


def test_event_status_enable_setter_and_getter():
    """Verify event status enable register roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("*ESE 7", None),
         ("*ESE?", "3")],
    ) as inst:
        inst.event_status_enable = 7
        assert inst.event_status_enable == 3


def test_standard_event_status_query():
    """Verify standard event status query."""
    with expected_protocol(
        Keysight35670A,
        [("*ESR?", "1")],
    ) as inst:
        assert inst.standard_event_status == 1


def test_power_on_status_clear_setter_and_getter():
    """Verify power-on status clear register roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("*PSC -1", None),
         ("*PSC?", "1")],
    ) as inst:
        inst.power_on_status_clear = -1
        assert inst.power_on_status_clear == 1


def test_service_request_enable_setter_and_getter():
    """Verify service request enable register roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("*SRE 32", None),
         ("*SRE?", "64")],
    ) as inst:
        inst.service_request_enable = 32
        assert inst.service_request_enable == 64


def test_status_byte_query():
    """Verify status byte query."""
    with expected_protocol(
        Keysight35670A,
        [("*STB?", "48")],
    ) as inst:
        assert inst.status_byte == 48


def test_pass_control_back_address_primary_only():
    """Verify setting pass-control-back primary address."""
    with expected_protocol(
        Keysight35670A,
        [("*PCB 14", None)],
    ) as inst:
        inst.pass_control_back_address(14)


def test_pass_control_back_address_primary_and_secondary():
    """Verify setting pass-control-back primary and secondary addresses."""
    with expected_protocol(
        Keysight35670A,
        [("*PCB 14, 2", None)],
    ) as inst:
        inst.pass_control_back_address(14, 2)


def test_arm_command():
    """Verify arm command."""
    with expected_protocol(
        Keysight35670A,
        [("ARM:IMMediate", None)],
    ) as inst:
        inst.arm()


def test_arm_rpm_increment_setter_and_getter():
    """Verify arm RPM increment roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("ARM:RPM:INCRement 123.4", None),
         ("ARM:RPM:INCRement?", "50")],
    ) as inst:
        inst.arm_rpm_increment = 123.4
        assert inst.arm_rpm_increment == 50.0


def test_arm_rpm_mode_setter_and_getter():
    """Verify arm RPM mode roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("ARM:RPM:MODE UP", None),
         ("ARM:RPM:MODE?", "DOWN")],
    ) as inst:
        inst.arm_rpm_mode = "up"
        assert inst.arm_rpm_mode == "down"


def test_arm_rpm_threshold_setter_and_getter():
    """Verify arm RPM threshold roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("ARM:RPM:THReshold 1000", None),
         ("ARM:RPM:THReshold?", "250")],
    ) as inst:
        inst.arm_rpm_threshold = 1000.0
        assert inst.arm_rpm_threshold == 250.0


def test_arm_source_setter_and_getter():
    """Verify arm source roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("ARM:SOURce TIM", None),
         ("ARM:SOURce?", "MAN")],
    ) as inst:
        inst.arm_source = "timer"
        assert inst.arm_source == "manual"


def test_arm_timer_setter_and_getter():
    """Verify arm timer roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("ARM:TIMer 0.125", None),
         ("ARM:TIMer?", "1.5")],
    ) as inst:
        inst.arm_timer = 0.125
        assert inst.arm_timer == 1.5


def test_continuous_initiation_enabled_setter_and_getter():
    """Verify continuous initiation bool mapping."""
    with expected_protocol(
        Keysight35670A,
        [("INITiate:CONTinuous 1", None),
         ("INITiate:CONTinuous?", "0")],
    ) as inst:
        inst.continuous_initiation_enabled = True
        assert inst.continuous_initiation_enabled is False


def test_calibration_auto_setter_and_getter():
    """Verify calibration auto mode roundtrip."""
    with expected_protocol(
        Keysight35670A,
        [("CALibration:AUTO ONCE", None),
         ("CALibration:AUTO?", "ON")],
    ) as inst:
        inst.calibration_auto = "once"
        assert inst.calibration_auto == "on"


def test_run_calibration_requires_confirmation():
    """Verify CALibration:ALL requires explicit confirmation."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="requires explicit confirmation"):
            inst.run_calibration()


def test_run_calibration():
    """Verify CALibration:ALL query helper."""
    with expected_protocol(
        Keysight35670A,
        [("CALibration:ALL?", "0")],
    ) as inst:
        assert inst.run_calibration(confirmed=True) == 0


def test_drain_errors_no_error():
    """Verify drain errors returns cleanly for no-error response."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:ERRor?", "0,No error")],
    ) as inst:
        inst.drain_errors()


def test_drain_errors_no_error_plus_zero_with_quotes():
    """Verify '+0,\"No error\"' is treated as queue-empty sentinel."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:ERRor?", '+0,"No error"')],
    ) as inst:
        inst.drain_errors()


def test_drain_errors_raises_runtime_error():
    """Verify drain errors raises when queue contains failures."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:ERRor?", "-200,Execution error"),
         ("SYSTem:ERRor?", "0,No error")],
    ) as inst:
        with pytest.raises(RuntimeError, match="error queue is not empty"):
            inst.drain_errors()


def test_drain_errors_float_code_raises_runtime_error():
    """Verify float-like error code token is parsed and treated as error."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:ERRor?", '-100.0,"Command error"'),
         ("SYSTem:ERRor?", '+0,"No error"')],
    ) as inst:
        with pytest.raises(RuntimeError, match="error queue is not empty"):
            inst.drain_errors()


def test_drain_errors_unparseable_code_raises_runtime_error():
    """Verify unparseable error token does not crash parser and still raises RuntimeError."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:ERRor?", '"BAD","Malformed response"'),
         ("SYSTem:ERRor?", '+0,"No error"')],
    ) as inst:
        with pytest.raises(RuntimeError, match="error queue is not empty"):
            inst.drain_errors()


def test_drain_errors_respects_max_errors_limit():
    """Verify drain errors stops after max_errors reads and raises with collected errors."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:ERRor?", '-100,"Command error"'),
         ("SYSTem:ERRor?", '-200,"Execution error"'),
         ("SYSTem:ERRor?", '-300,"Device-specific error"')],
    ) as inst:
        with pytest.raises(RuntimeError, match="error queue is not empty"):
            inst.drain_errors(max_errors=3)


def test_drain_errors_rejects_invalid_max_errors():
    """Verify invalid max_errors rejects early without sending instrument commands."""
    with expected_protocol(Keysight35670A, []) as inst:
        with pytest.raises(ValueError, match="max_errors must be >= 1"):
            inst.drain_errors(max_errors=0)


def test_trigger():
    """Verify trigger command."""
    with expected_protocol(
        Keysight35670A,
        [("*TRG", None)],
    ) as inst:
        inst.trigger()


def test_clear():
    """Verify clear-status command."""
    with expected_protocol(
        Keysight35670A,
        [("*CLS", None)],
    ) as inst:
        inst.clear()


def test_reset():
    """Verify reset command."""
    with expected_protocol(
        Keysight35670A,
        [("*RST", None)],
    ) as inst:
        inst.reset()


def test_options():
    """Verify options query."""
    with expected_protocol(
        Keysight35670A,
        [("*OPT?", "A6J")],
    ) as inst:
        assert inst.options() == "A6J"


def test_system_error():
    """Verify system error query."""
    with expected_protocol(
        Keysight35670A,
        [("SYSTem:ERRor?", "0,No error")],
    ) as inst:
        assert inst.system_error() == "0,No error"


def test_id_query_accepts_hewlett_packard():
    """Verify check_id accepts Hewlett-Packard manufacturer."""
    with expected_protocol(
        Keysight35670A,
        [("*IDN?", "HEWLETT-PACKARD,35670A,MY42509215,A.01.11")],
    ) as inst:
        inst.check_id()


def test_id_query_accepts_keysight():
    """Verify check_id accepts Keysight manufacturer."""
    with expected_protocol(
        Keysight35670A,
        [("*IDN?", "KEYSIGHT TECHNOLOGIES,35670A,MY42509215,A.01.11")],
    ) as inst:
        inst.check_id()


def test_check_id_rejects_unsupported_model():
    """Verify check_id rejects unsupported models."""
    with expected_protocol(
        Keysight35670A,
        [("*IDN?", "KEYSIGHT,35665A,0,1.0")],
    ) as inst:
        with pytest.raises(ValueError, match="supported 35670A"):
            inst.check_id()


def test_check_id_rejects_invalid_response():
    """Verify check_id rejects malformed ID responses."""
    with expected_protocol(
        Keysight35670A,
        [("*IDN?", "BAD_RESPONSE")],
    ) as inst:
        with pytest.raises(ValueError, match="Unexpected instrument IDN response"):
            inst.check_id()
