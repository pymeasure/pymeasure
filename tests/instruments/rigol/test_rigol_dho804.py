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

from pymeasure.test import expected_protocol
from pymeasure.instruments.rigol import DHO804


# ======================================================================= #
#  Status and OPC                                                          #
# ======================================================================= #


class TestStatus:

    def test_wait_for_opc(self):
        with expected_protocol(
            DHO804, [("*OPC?", "1")]
        ) as inst:
            inst.wait_for_opc()

    def test_clear_status(self):
        with expected_protocol(
            DHO804, [("*CLS", None)]
        ) as inst:
            inst.clear_status()

    def test_status_byte(self):
        with expected_protocol(
            DHO804, [("*STB?", "0")]
        ) as inst:
            assert inst.status_byte == 0

# ======================================================================= #
#  Channel properties                                                      #
# ======================================================================= #


class TestChannel:
    """One class covers all channel properties.

    Testing strategy:
    - Use ch_1 for most tests; use ch_2 for one test per property so that
      {ch} substitution is verified without testing all four channels.
    - For enum properties: verify one valid set, one valid get, one invalid.
    - For bool properties: test both True and False (different code paths).
    - For numeric properties: one set + one get is sufficient.
    """

    # -- display (bool, mapped to 0/1) -----------------------------------

    @pytest.mark.parametrize("ch_n, value, raw", [
        (1, True,  "1"),
        (2, False, "0"),   # second channel proves {ch} is dynamic
    ])
    def test_display_get(self, ch_n, value, raw):
        with expected_protocol(
            DHO804, [(f":CHAN{ch_n}:DISP?", raw)]
        ) as inst:
            assert getattr(inst, f"ch_{ch_n}").display_enabled is value

    @pytest.mark.parametrize("ch_n, value, raw", [
        (1, True,  "1"),
        (2, False, "0"),
    ])
    def test_display_set(self, ch_n, value, raw):
        with expected_protocol(
            DHO804, [(f":CHAN{ch_n}:DISP {raw}", None)]
        ) as inst:
            getattr(inst, f"ch_{ch_n}").display_enabled = value

    def test_display_accepts_int(self):
        """0 and 1 are accepted alongside False/True."""
        with expected_protocol(
            DHO804,
            [(":CHAN1:DISP 1", None), (":CHAN1:DISP 0", None)],
        ) as inst:
            inst.ch_1.display_enabled = 1
            inst.ch_1.display_enabled = 0

    # -- coupling --------------------------------------------------------

    @pytest.mark.parametrize("value", ["AC", "DC", "GND"])
    def test_coupling_set(self, value):
        with expected_protocol(
            DHO804, [(f":CHAN1:COUP {value}", None)]
        ) as inst:
            inst.ch_1.coupling = value

    def test_coupling_get(self):
        with expected_protocol(
            DHO804, [(":CHAN2:COUP?", "DC")]
        ) as inst:
            assert inst.ch_2.coupling == "DC"

    def test_coupling_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.ch_1.coupling = "INVALID"

    # -- bandwidth_limit -------------------------------------------------

    @pytest.mark.parametrize("value", ["OFF", "20M", "100M"])
    def test_bandwidth_limit_set(self, value):
        with expected_protocol(
            DHO804, [(f":CHAN1:BWL {value}", None)]
        ) as inst:
            inst.ch_1.bandwidth_limit = value

    def test_bandwidth_limit_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.ch_1.bandwidth_limit = "200M"

    # -- scale -----------------------------------------------------------

    def test_scale_set(self):
        with expected_protocol(
            DHO804, [(":CHAN1:SCAL 0.5", None)]
        ) as inst:
            inst.ch_1.scale = 0.5

    def test_scale_get(self):
        with expected_protocol(
            DHO804, [(":CHAN1:SCAL?", "0.5")]
        ) as inst:
            assert inst.ch_1.scale == pytest.approx(0.5)

    def test_scale_out_of_range_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.ch_1.scale = 11.0

    # -- offset ----------------------------------------------------------

    def test_offset_set(self):
        with expected_protocol(
            DHO804, [(":CHAN1:OFFS -1.5", None)]
        ) as inst:
            inst.ch_1.offset = -1.5

    def test_offset_get(self):
        with expected_protocol(
            DHO804, [(":CHAN2:OFFS?", "-1.5")]
        ) as inst:
            assert inst.ch_2.offset == pytest.approx(-1.5)

    # -- probe -----------------------------------------------------------

    def test_probe_set(self):
        with expected_protocol(
            DHO804, [(":CHAN1:PROB 10", None)]
        ) as inst:
            inst.ch_1.probe = 10

    def test_probe_get(self):
        with expected_protocol(
            DHO804, [(":CHAN1:PROB?", "10")]
        ) as inst:
            assert inst.ch_1.probe == pytest.approx(10.0)

    def test_probe_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.ch_1.probe = 7

    # -- invert (bool) ---------------------------------------------------

    @pytest.mark.parametrize("value, raw", [(True, "1"), (False, "0")])
    def test_invert_set(self, value, raw):
        with expected_protocol(
            DHO804, [(f":CHAN1:INV {raw}", None)]
        ) as inst:
            inst.ch_1.invert = value

    @pytest.mark.parametrize("value, raw", [(True, "1"), (False, "0")])
    def test_invert_get(self, value, raw):
        with expected_protocol(
            DHO804, [(":CHAN1:INV?", raw)]
        ) as inst:
            assert inst.ch_1.invert is value

    # -- units -----------------------------------------------------------

    def test_units_set(self):
        with expected_protocol(
            DHO804, [(":CHAN1:UNIT AMP", None)]
        ) as inst:
            inst.ch_1.units = "AMP"

    def test_units_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.ch_1.units = "DBM"

    # -- label -----------------------------------------------------------

    def test_label_set(self):
        with expected_protocol(
            DHO804, [(":CHAN1:LAB:CONT CLK", None)]
        ) as inst:
            inst.ch_1.label = "CLK"

    def test_label_get(self):
        with expected_protocol(
            DHO804, [(":CHAN1:LAB:CONT?", "CLK")]
        ) as inst:
            assert inst.ch_1.label == "CLK"

    @pytest.mark.parametrize("value, raw", [(True, "1"), (False, "0")])
    def test_label_enable_set(self, value, raw):
        with expected_protocol(
            DHO804, [(f":CHAN1:LAB:SHOW {raw}", None)]
        ) as inst:
            inst.ch_1.label_enabled = value


# ======================================================================= #
#  Acquisition                                                             #
# ======================================================================= #

class TestAcquisition:

    @pytest.mark.parametrize("value", ["NORM", "AVER", "PEAK", "ULTR"])
    def test_acquisition_type_set(self, value):
        with expected_protocol(
            DHO804, [(f":ACQ:TYPE {value}", None)]
        ) as inst:
            inst.acquisition_type = value

    def test_acquisition_type_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.acquisition_type = "NORMal"

    def test_acquisition_averages_set(self):
        with expected_protocol(
            DHO804, [(":ACQ:AVER 64", None)]
        ) as inst:
            inst.acquisition_averages = 64

    def test_acquisition_averages_get(self):
        with expected_protocol(
            DHO804, [(":ACQ:AVER?", "64")]
        ) as inst:
            assert inst.acquisition_averages == 64

    def test_acquisition_averages_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.acquisition_averages = 3  # not a power of 2

    def test_memory_depth_set(self):
        with expected_protocol(
            DHO804, [(":ACQ:MDEP 1000000", None)]
        ) as inst:
            inst.acquisition_memory_depth = 1_000_000

    def test_sample_rate(self):
        with expected_protocol(
            DHO804, [(":ACQ:SRAT?", "2.5E+08")]
        ) as inst:
            assert inst.sample_rate == pytest.approx(2.5e8)


# ======================================================================= #
#  Timebase                                                                #
# ======================================================================= #

class TestTimebase:

    # Two values to cover %g formatting edge cases (scientific vs decimal)
    @pytest.mark.parametrize("value, sent", [
        (1e-6, "1e-06"),
        (1e-3, "0.001"),
    ])
    def test_timebase_scale_set(self, value, sent):
        with expected_protocol(
            DHO804, [(f":TIM:MAIN:SCAL {sent}", None)]
        ) as inst:
            inst.timebase_scale = value

    def test_timebase_scale_get(self):
        with expected_protocol(
            DHO804, [(":TIM:MAIN:SCAL?", "1e-3")]
        ) as inst:
            assert inst.timebase_scale == pytest.approx(1e-3)

    def test_timebase_scale_out_of_range_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.timebase_scale = 1001.0

    def test_timebase_offset_set(self):
        with expected_protocol(
            DHO804, [(":TIM:MAIN:OFFS -0.5", None)]
        ) as inst:
            inst.timebase_offset = -0.5

    def test_timebase_offset_get(self):
        with expected_protocol(
            DHO804, [(":TIM:MAIN:OFFS?", "0.0005")]
        ) as inst:
            assert inst.timebase_offset == pytest.approx(5e-4)

    @pytest.mark.parametrize("value", ["MAIN", "XY", "ROLL"])
    def test_timebase_mode_set(self, value):
        with expected_protocol(
            DHO804, [(f":TIM:MODE {value}", None)]
        ) as inst:
            inst.timebase_mode = value

    def test_timebase_mode_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.timebase_mode = "ZOOM"


# ======================================================================= #
#  Trigger                                                                 #
# ======================================================================= #

class TestTrigger:

    # One representative mode is enough – the rest are enum validation
    def test_trigger_mode_set(self):
        with expected_protocol(
            DHO804, [(":TRIG:MODE EDGE", None)]
        ) as inst:
            inst.trigger_mode = "EDGE"

    def test_trigger_mode_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.trigger_mode = "INVALID"

    @pytest.mark.parametrize("value", ["AUTO", "NORM", "SING"])
    def test_trigger_sweep_set(self, value):
        with expected_protocol(
            DHO804, [(f":TRIG:SWE {value}", None)]
        ) as inst:
            inst.trigger_sweep = value

    def test_trigger_sweep_get(self):
        with expected_protocol(
            DHO804, [(":TRIG:SWE?", "AUTO")]
        ) as inst:
            assert inst.trigger_sweep == "AUTO"

    @pytest.mark.parametrize("value",
                             ["CHAN1", "CHAN2", "CHAN3", "CHAN4", "EXT", "AC"])
    def test_trigger_source_set(self, value):
        with expected_protocol(
            DHO804, [(f":TRIG:EDGE:SOUR {value}", None)]
        ) as inst:
            inst.trigger_source = value

    def test_trigger_source_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.trigger_source = "CH5"

    @pytest.mark.parametrize("value", ["POS", "NEG", "RFAL"])
    def test_trigger_slope_set(self, value):
        with expected_protocol(
            DHO804, [(f":TRIG:EDGE:SLOP {value}", None)]
        ) as inst:
            inst.trigger_slope = value

    def test_trigger_slope_get(self):
        with expected_protocol(
            DHO804, [(":TRIG:EDGE:SLOP?", "POS")]
        ) as inst:
            assert inst.trigger_slope == "POS"

    def test_trigger_level_set(self):
        with expected_protocol(
            DHO804, [(":TRIG:EDGE:LEV 1.5", None)]
        ) as inst:
            inst.trigger_level = 1.5

    def test_trigger_level_get(self):
        with expected_protocol(
            DHO804, [(":TRIG:EDGE:LEV?", "1.65")]
        ) as inst:
            assert inst.trigger_level == pytest.approx(1.65)

    def test_trigger_coupling_set(self):
        with expected_protocol(
            DHO804, [(":TRIG:COUP LFR", None)]
        ) as inst:
            inst.trigger_coupling = "LFR"

    def test_trigger_holdoff_set(self):
        with expected_protocol(
            DHO804, [(":TRIG:HOLD 1e-06", None)]
        ) as inst:
            inst.trigger_holdoff = 1e-6

    @pytest.mark.parametrize("status", ["TD", "WAIT", "RUN", "AUTO", "STOP"])
    def test_trigger_status_get(self, status):
        with expected_protocol(
            DHO804, [(":TRIG:STAT?", status)]
        ) as inst:
            assert inst.trigger_status == status


# ======================================================================= #
#  Run control                                                             #
# ======================================================================= #

class TestRunControl:

    @pytest.mark.parametrize("method, cmd", [
        ("run",           ":RUN"),
        ("stop",          ":STOP"),
        ("single",        ":SING"),
        ("force_trigger", ":TFOR"),
        ("autoset",       ":AUTO"),
    ])
    def test_command(self, method, cmd):
        with expected_protocol(DHO804, [(cmd, None)]) as inst:
            getattr(inst, method)()


# ======================================================================= #
#  Measurements                                                            #
# ======================================================================= #

class TestMeasurements:

    def test_measure_returns_float(self):
        # measure() activates via SET then queries via GET
        with expected_protocol(
            DHO804,
            [
                (":MEAS:ITEM? VPP,CHAN1", "3.35"),
            ],
        ) as inst:
            assert inst.measure("VPP") == pytest.approx(3.35)

    def test_measure_custom_source(self):
        with expected_protocol(
            DHO804,
            [
                (":MEAS:ITEM? FREQ,CHAN3", "1.0E+06"),
            ],
        ) as inst:
            assert inst.measure("FREQ", 3) == pytest.approx(1e6)

    def test_measure_unavailable_returns_nan(self):
        with expected_protocol(
            DHO804,
            [
                (":MEAS:ITEM? VMAX,CHAN1", "****"),
            ],
        ) as inst:
            assert math.isnan(inst.measure("VMAX"))

    def test_clear_measurements(self):
        with expected_protocol(
            DHO804, [(":MEAS:CLE:ALL", None)]
        ) as inst:
            inst.clear_measurements()


# ======================================================================= #
#  Cursor and Display                                                      #
# ======================================================================= #

class TestCursorAndDisplay:

    @pytest.mark.parametrize("value", ["OFF", "MAN", "TRAC", "XY"])
    def test_cursor_mode_set(self, value):
        with expected_protocol(
            DHO804, [(f":CURS:MODE {value}", None)]
        ) as inst:
            inst.cursor_mode = value

    def test_clear_screen(self):
        with expected_protocol(
            DHO804, [(":DISP:CLE", None)]
        ) as inst:
            inst.clear_screen()

    @pytest.mark.parametrize("value, expected_cmd", [
        (True, b":DISP:TYPE VECT"),
        (False, b":DISP:TYPE DOTS")
    ])
    def test_display_type_vector_enabled_set(self, value, expected_cmd):
        with expected_protocol(
            DHO804, [(expected_cmd, None)]
        ) as inst:
            inst.display_type_vector_enabled = value

    def test_display_grading_time_set(self):
        with expected_protocol(
            DHO804, [(":DISP:GRAD:TIME INF", None)]
        ) as inst:
            inst.display_grading_time = "INF"

    def test_display_grading_time_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.display_grading_time = "2"

# ======================================================================= #
#  Waveform                                                                #
# ======================================================================= #


# Minimal preamble string used across waveform tests
PREAMBLE = "0,1,1000,1,4.0E-7,-2.0E-4,0,1.6E-3,-87,128"


class TestWaveform:

    def test_set_waveform_source(self):
        with expected_protocol(
            DHO804, [(":WAV:SOUR CHAN2", None)]
        ) as inst:
            inst._set_waveform_source(2)

    def test_get_waveform_preamble(self):
        with expected_protocol(
            DHO804,
            [
                (":WAV:SOUR CHAN1", None),
                (":WAV:PRE?", PREAMBLE),
            ],
        ) as inst:
            pre = inst.get_waveform_preamble(1)
            assert pre["points"] == 1000
            assert pre["xincrement"] == pytest.approx(4e-7)
            assert pre["yincrement"] == pytest.approx(1.6e-3)
            assert pre["yreference"] == 128
            assert pre["xreference"] == 0

    def test_get_waveform_invalid_fmt_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.get_waveform(fmt="ASC")

    def test_get_waveform_invalid_mode_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.get_waveform(mode="INVALID")

    def test_get_waveform_norm_byte(self):
        raw_samples = bytes([128, 130, 126, 132])  # 4 uint8 samples
        ieee_block = b'#1' + str(
            len(raw_samples)).encode() + raw_samples + b'\n'

        with expected_protocol(
            DHO804,
            [
                (":TRIG:STAT?", "STOP"),          # was_running check
                (":WAV:SOUR CHAN1", None),
                (":WAV:MODE NORM", None),
                (":WAV:FORM BYTE", None),
                (":WAV:SOUR CHAN1", None),         # from get_waveform_preamble
                (":WAV:PRE?", PREAMBLE),
                (":WAV:STAR 1", None),
                (":WAV:STOP 1000", None),
                (":WAV:DATA?", ieee_block),
            ],
        ) as inst:
            t, v = inst.get_waveform(channel=1, mode="NORM", fmt="BYTE")
            assert len(t) == 4
            assert len(v) == 4

    def test_get_waveform_ascii(self):
        csv = "0.1,0.2,0.3,0.4"
        with expected_protocol(
            DHO804,
            [
                (":WAV:SOUR CHAN1", None),
                (":WAV:MODE NORM", None),
                (":WAV:FORM ASC", None),
                (":WAV:SOUR CHAN1", None),   # from get_waveform_preamble
                (":WAV:PRE?", PREAMBLE),
                (":WAV:STAR 1", None),
                (":WAV:STOP 1000", None),
                (":WAV:DATA?", csv),
            ],
        ) as inst:
            t, v = inst.get_waveform_ascii(channel=1)
            assert len(v) == 4
            assert v[0] == pytest.approx(0.1)
            assert len(t) == len(v)
