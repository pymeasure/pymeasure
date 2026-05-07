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

"""
Tests for the Rigol DHO804 oscilloscope driver.

Two test modes are supported:

1. **Protocol tests** (default, no hardware needed)::

       pytest tests/instruments/rigol/test_rigol_dho804.py -v

2. **Live hardware tests** (requires a connected DHO804)::

       pytest tests/instruments/rigol/test_rigol_dho804.py -v \\
           --device-address "TCPIP::10.150.45.211::INSTR"

   When ``--device-address`` is provided, the ``TestLiveDevice`` class
   runs against the real instrument.  All other (protocol) tests are
   skipped because they use ``expected_protocol``.
"""

import math
import pytest

from pymeasure.test import expected_protocol

from pymeasure.instruments.rigol import DHO804


# ======================================================================= #
#  pytest CLI option                                                       #
# ======================================================================= #

def pytest_addoption(parser):
    parser.addoption(
        "--device-address",
        action="store",
        default=None,
        help="VISA resource string for a real DHO804, e.g. "
             "'TCPIP::10.150.45.211::INSTR'",
    )


# ======================================================================= #
#  Fixtures                                                                #
# ======================================================================= #

@pytest.fixture(scope="module")
def real_instrument(request):
    """Open a connection to a real DHO804 if --device-address was given.

    Tests that use this fixture are automatically skipped when no address
    is provided.

    ``pytest_addoption`` is only guaranteed to work from conftest.py, so we
    catch ValueError in case the option was not registered (e.g. when the
    test file is collected stand-alone without conftest.py).
    """
    try:
        address = request.config.getoption("--device-address")
    except ValueError:
        address = None
    if not address:
        pytest.skip("No --device-address given – skipping live hardware test")
    scope = DHO804(address)
    yield scope
    scope.adapter.close()


# ======================================================================= #
#  Helpers                                                                 #
# ======================================================================= #

def ch(n):
    """Return the channel accessor for channel number *n* (1-4)."""
    return lambda inst: getattr(inst, f"ch_{n}")


# ======================================================================= #
#  Channel – display                                                       #
# ======================================================================= #

class TestChannelDisplay:

    @pytest.mark.parametrize("ch_n", [1, 2, 3, 4])
    def test_display_get_true(self, ch_n):
        with expected_protocol(
            DHO804,
            [(f":CHAN{ch_n}:DISPlay?", "1")],
        ) as inst:
            assert ch(ch_n)(inst).display is True

    @pytest.mark.parametrize("ch_n", [1, 2, 3, 4])
    def test_display_get_false(self, ch_n):
        with expected_protocol(
            DHO804,
            [(f":CHAN{ch_n}:DISPlay?", "0")],
        ) as inst:
            assert ch(ch_n)(inst).display is False

    @pytest.mark.parametrize("ch_n", [1, 2, 3, 4])
    def test_display_set_true(self, ch_n):
        with expected_protocol(
            DHO804,
            [(f":CHAN{ch_n}:DISPlay 1", None)],
        ) as inst:
            ch(ch_n)(inst).display = True

    @pytest.mark.parametrize("ch_n", [1, 2, 3, 4])
    def test_display_set_false(self, ch_n):
        with expected_protocol(
            DHO804,
            [(f":CHAN{ch_n}:DISPlay 0", None)],
        ) as inst:
            ch(ch_n)(inst).display = False

    def test_display_set_int_1(self):
        """Integer 1 is accepted in place of True."""
        with expected_protocol(
            DHO804,
            [(":CHAN1:DISPlay 1", None)],
        ) as inst:
            inst.ch_1.display = 1

    def test_display_set_int_0(self):
        """Integer 0 is accepted in place of False."""
        with expected_protocol(
            DHO804,
            [(":CHAN1:DISPlay 0", None)],
        ) as inst:
            inst.ch_1.display = 0


# ======================================================================= #
#  Channel – coupling                                                      #
# ======================================================================= #

class TestChannelCoupling:

    @pytest.mark.parametrize("value", ["AC", "DC", "GND"])
    def test_coupling_get(self, value):
        with expected_protocol(
            DHO804,
            [(":CHAN1:COUPling?", value)],
        ) as inst:
            assert inst.ch_1.coupling == value

    @pytest.mark.parametrize("value", ["AC", "DC", "GND"])
    def test_coupling_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":CHAN1:COUPling {value}", None)],
        ) as inst:
            inst.ch_1.coupling = value

    def test_coupling_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.ch_1.coupling = "INVALID"


# ======================================================================= #
#  Channel – bandwidth limit                                               #
# ======================================================================= #

class TestChannelBandwidthLimit:

    @pytest.mark.parametrize("value", ["OFF", "20M", "100M"])
    def test_bandwidth_limit_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":CHAN2:BWLimit {value}", None)],
        ) as inst:
            inst.ch_2.bandwidth_limit = value

    @pytest.mark.parametrize("value", ["OFF", "20M", "100M"])
    def test_bandwidth_limit_get(self, value):
        with expected_protocol(
            DHO804,
            [(":CHAN2:BWLimit?", value)],
        ) as inst:
            assert inst.ch_2.bandwidth_limit == value

    def test_bandwidth_limit_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.ch_1.bandwidth_limit = "200M"


# ======================================================================= #
#  Channel – vertical scale                                                #
# ======================================================================= #

class TestChannelScale:

    @pytest.mark.parametrize("value", [500e-6, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0])
    def test_scale_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":CHAN1:SCALe {value:g}", None)],
        ) as inst:
            inst.ch_1.scale = value

    def test_scale_get(self):
        with expected_protocol(
            DHO804,
            [(":CHAN1:SCALe?", "1.0")],
        ) as inst:
            assert inst.ch_1.scale == pytest.approx(1.0)

    def test_scale_too_large_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.ch_1.scale = 11.0

    def test_scale_too_small_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.ch_1.scale = 1e-7


# ======================================================================= #
#  Channel – vertical offset                                               #
# ======================================================================= #

class TestChannelOffset:

    @pytest.mark.parametrize("value", [-5.0, -1.5, 0.0, 1.5, 5.0])
    def test_offset_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":CHAN1:OFFSet {value:g}", None)],
        ) as inst:
            inst.ch_1.offset = value

    def test_offset_get(self):
        with expected_protocol(
            DHO804,
            [(":CHAN3:OFFSet?", "-2.5")],
        ) as inst:
            assert inst.ch_3.offset == pytest.approx(-2.5)


# ======================================================================= #
#  Channel – probe ratio                                                   #
# ======================================================================= #

class TestChannelProbe:

    @pytest.mark.parametrize("value", [1, 10, 100, 1000])
    def test_probe_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":CHAN1:PROBe {value:g}", None)],
        ) as inst:
            inst.ch_1.probe = value

    def test_probe_get(self):
        with expected_protocol(
            DHO804,
            [(":CHAN1:PROBe?", "10")],
        ) as inst:
            assert inst.ch_1.probe == pytest.approx(10.0)

    def test_probe_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.ch_1.probe = 7  # not a valid attenuation ratio


# ======================================================================= #
#  Channel – invert                                                        #
# ======================================================================= #

class TestChannelInvert:

    def test_invert_set_true(self):
        with expected_protocol(
            DHO804,
            [(":CHAN1:INVert 1", None)],
        ) as inst:
            inst.ch_1.invert = True

    def test_invert_set_false(self):
        with expected_protocol(
            DHO804,
            [(":CHAN1:INVert 0", None)],
        ) as inst:
            inst.ch_1.invert = False

    def test_invert_get_true(self):
        with expected_protocol(
            DHO804,
            [(":CHAN1:INVert?", "1")],
        ) as inst:
            assert inst.ch_1.invert is True

    def test_invert_get_false(self):
        with expected_protocol(
            DHO804,
            [(":CHAN1:INVert?", "0")],
        ) as inst:
            assert inst.ch_1.invert is False


# ======================================================================= #
#  Channel – units                                                         #
# ======================================================================= #

class TestChannelUnits:

    @pytest.mark.parametrize("value", ["VOLT", "WATT", "AMP", "UNKN"])
    def test_units_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":CHAN1:UNITs {value}", None)],
        ) as inst:
            inst.ch_1.units = value

    def test_units_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.ch_1.units = "DBM"


# ======================================================================= #
#  Channel – label                                                         #
# ======================================================================= #

class TestChannelLabel:

    def test_label_set(self):
        with expected_protocol(
            DHO804,
            [(":CHAN1:LABel MySignal", None)],
        ) as inst:
            inst.ch_1.label = "MySignal"

    def test_label_get(self):
        with expected_protocol(
            DHO804,
            [(":CHAN1:LABel?", "CLK")],
        ) as inst:
            assert inst.ch_1.label == "CLK"

    def test_label_display_set_true(self):
        with expected_protocol(
            DHO804,
            [(":CHAN1:LABel:DISPlay 1", None)],
        ) as inst:
            inst.ch_1.label_display = True

    def test_label_display_set_false(self):
        with expected_protocol(
            DHO804,
            [(":CHAN1:LABel:DISPlay 0", None)],
        ) as inst:
            inst.ch_1.label_display = False


# ======================================================================= #
#  Acquisition                                                             #
# ======================================================================= #

class TestAcquisition:

    @pytest.mark.parametrize("value", ["NORM", "AVER", "PEAK", "ULTR"])
    def test_acquisition_type_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":ACQuire:TYPE {value}", None)],
        ) as inst:
            inst.acquisition_type = value

    def test_acquisition_type_get(self):
        with expected_protocol(
            DHO804,
            [(":ACQuire:TYPE?", "NORM")],
        ) as inst:
            assert inst.acquisition_type == "NORM"

    def test_acquisition_type_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.acquisition_type = "NORMal"  # long form not accepted

    @pytest.mark.parametrize("value", [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
    def test_acquisition_averages_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":ACQuire:AVERages {value}", None)],
        ) as inst:
            inst.acquisition_averages = value

    def test_acquisition_averages_get(self):
        with expected_protocol(
            DHO804,
            [(":ACQuire:AVERages?", "64")],
        ) as inst:
            assert inst.acquisition_averages == 64

    def test_acquisition_averages_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.acquisition_averages = 3  # not a power of 2

    @pytest.mark.parametrize("value", ["AUTO", 1_000, 1_000_000])
    def test_memory_depth_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":ACQuire:MDEPth {value}", None)],
        ) as inst:
            inst.acquisition_memory_depth = value

    def test_sample_rate(self):
        with expected_protocol(
            DHO804,
            [(":ACQuire:SRATe?", "2.5E+08")],
        ) as inst:
            assert inst.sample_rate == pytest.approx(2.5e8)


# ======================================================================= #
#  Timebase                                                                #
# ======================================================================= #

class TestTimebase:

    @pytest.mark.parametrize("value,sent", [
        (1e-9,  "1e-09"),
        (1e-6,  "1e-06"),
        (1e-3,  "0.001"),
        (1.0,   "1"),
        (100.0, "100"),
    ])
    def test_timebase_scale_set(self, value, sent):
        with expected_protocol(
            DHO804,
            [(f":TIMebase:MAIN:SCALe {sent}", None)],
        ) as inst:
            inst.timebase_scale = value

    def test_timebase_scale_get(self):
        with expected_protocol(
            DHO804,
            [(":TIMebase:MAIN:SCALe?", "1e-3")],
        ) as inst:
            assert inst.timebase_scale == pytest.approx(1e-3)

    def test_timebase_scale_too_large_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.timebase_scale = 1001.0

    @pytest.mark.parametrize("value", [-0.5, 0.0, 0.5e-3])
    def test_timebase_offset_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":TIMebase:MAIN:OFFSet {value:g}", None)],
        ) as inst:
            inst.timebase_offset = value

    def test_timebase_offset_get(self):
        with expected_protocol(
            DHO804,
            [(":TIMebase:MAIN:OFFSet?", "0.0005")],
        ) as inst:
            assert inst.timebase_offset == pytest.approx(5e-4)

    @pytest.mark.parametrize("value", ["MAIN", "XY", "ROLL"])
    def test_timebase_mode_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":TIMebase:MODE {value}", None)],
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

    @pytest.mark.parametrize("value", [
        "EDGE", "PULS", "RUNT", "WIND", "NEDG", "SLOP",
        "VID", "PATT", "DEL", "TIM", "DUR", "SHOL",
        "RS232", "IIC", "SPI", "CAN", "LIN",
    ])
    def test_trigger_mode_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":TRIGger:MODE {value}", None)],
        ) as inst:
            inst.trigger_mode = value

    @pytest.mark.parametrize("value", ["AUTO", "NORM", "SINGl"])
    def test_trigger_sweep_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":TRIGger:SWEep {value}", None)],
        ) as inst:
            inst.trigger_sweep = value

    def test_trigger_sweep_get(self):
        with expected_protocol(
            DHO804,
            [(":TRIGger:SWEep?", "AUTO")],
        ) as inst:
            assert inst.trigger_sweep == "AUTO"

    @pytest.mark.parametrize("value", ["CHAN1", "CHAN2", "CHAN3", "CHAN4", "EXT", "AC"])
    def test_trigger_source_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":TRIGger:EDGE:SOURce {value}", None)],
        ) as inst:
            inst.trigger_source = value

    @pytest.mark.parametrize("value", ["D0", "D7", "D15"])
    def test_trigger_source_digital(self, value):
        with expected_protocol(
            DHO804,
            [(f":TRIGger:EDGE:SOURce {value}", None)],
        ) as inst:
            inst.trigger_source = value

    def test_trigger_source_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.trigger_source = "CHAN5"

    @pytest.mark.parametrize("value", ["POS", "NEG", "RFAL"])
    def test_trigger_slope_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":TRIG:EDGE:SLOPe {value}", None)],
        ) as inst:
            inst.trigger_slope = value

    def test_trigger_slope_get(self):
        with expected_protocol(
            DHO804,
            [(":TRIG:EDGE:SLOPe?", "POS")],
        ) as inst:
            assert inst.trigger_slope == "POS"

    @pytest.mark.parametrize("value", [-5.0, 0.0, 1.5, 3.3])
    def test_trigger_level_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":TRIGger:EDGE:LEVel {value:g}", None)],
        ) as inst:
            inst.trigger_level = value

    def test_trigger_level_get(self):
        with expected_protocol(
            DHO804,
            [(":TRIGger:EDGE:LEVel?", "1.65")],
        ) as inst:
            assert inst.trigger_level == pytest.approx(1.65)

    @pytest.mark.parametrize("value", ["AC", "DC", "LFR", "HFR"])
    def test_trigger_coupling_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":TRIGger:COUPling {value}", None)],
        ) as inst:
            inst.trigger_coupling = value

    def test_trigger_holdoff_set(self):
        with expected_protocol(
            DHO804,
            [(":TRIGger:HOLDoff 1e-06", None)],
        ) as inst:
            inst.trigger_holdoff = 1e-6

    @pytest.mark.parametrize("status", ["TD", "WAIT", "RUN", "AUTO", "STOP"])
    def test_trigger_status_get(self, status):
        with expected_protocol(
            DHO804,
            [(":TRIGger:STATus?", status)],
        ) as inst:
            assert inst.trigger_status == status


# ======================================================================= #
#  Run control                                                             #
# ======================================================================= #

class TestRunControl:

    def test_run(self):
        with expected_protocol(
            DHO804,
            [(":RUN", None)],
        ) as inst:
            inst.run()

    def test_stop(self):
        with expected_protocol(
            DHO804,
            [(":STOP", None)],
        ) as inst:
            inst.stop()

    def test_single(self):
        with expected_protocol(
            DHO804,
            [(":SINGle", None)],
        ) as inst:
            inst.single()

    def test_force_trigger(self):
        with expected_protocol(
            DHO804,
            [(":TFORce", None)],
        ) as inst:
            inst.force_trigger()

    def test_autoset(self):
        with expected_protocol(
            DHO804,
            [(":AUTOset", None)],
        ) as inst:
            inst.autoset()


# ======================================================================= #
#  Measurements                                                            #
# ======================================================================= #

class TestMeasurements:

    @pytest.mark.parametrize("item,response,expected", [
        ("VMAX",  "3.3",     3.3),
        ("VMIN",  "-0.05",  -0.05),
        ("VPP",   "3.35",    3.35),
        ("FREQ",  "1.0E+06", 1e6),
        ("PER",   "1.0E-06", 1e-6),
        ("RISE",  "2.5E-09", 2.5e-9),
    ])
    def test_measure_item(self, item, response, expected):
        with expected_protocol(
            DHO804,
            [(f":MEASure:ITEM? {item},CHAN1", response)],
        ) as inst:
            assert inst.measure(item) == pytest.approx(expected)

    def test_measure_custom_source(self):
        with expected_protocol(
            DHO804,
            [(":MEASure:ITEM? VPP,CHAN3", "2.0")],
        ) as inst:
            assert inst.measure("VPP", "CHAN3") == pytest.approx(2.0)

    def test_measure_unavailable_returns_nan(self):
        """Instrument returns '****' when measurement is not possible."""
        with expected_protocol(
            DHO804,
            [(":MEASure:ITEM? VMAX,CHAN1", "****")],
        ) as inst:
            assert math.isnan(inst.measure("VMAX"))

    def test_clear_measurements(self):
        with expected_protocol(
            DHO804,
            [(":MEASure:CLEar:ALL", None)],
        ) as inst:
            inst.clear_measurements()


# ======================================================================= #
#  Cursor                                                                  #
# ======================================================================= #

class TestCursor:

    @pytest.mark.parametrize("value", ["OFF", "MAN", "TRAC", "XY"])
    def test_cursor_mode_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":CURSor:MODE {value}", None)],
        ) as inst:
            inst.cursor_mode = value

    def test_cursor_mode_get(self):
        with expected_protocol(
            DHO804,
            [(":CURSor:MODE?", "MAN")],
        ) as inst:
            assert inst.cursor_mode == "MAN"


# ======================================================================= #
#  Display                                                                 #
# ======================================================================= #

class TestDisplay:

    def test_clear_screen(self):
        with expected_protocol(
            DHO804,
            [(":DISPlay:CLEar", None)],
        ) as inst:
            inst.clear_screen()

    @pytest.mark.parametrize("value", ["VECT", "DOTS"])
    def test_display_type_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":DISPlay:TYPE {value}", None)],
        ) as inst:
            inst.display_type = value

    def test_display_type_get(self):
        with expected_protocol(
            DHO804,
            [(":DISPlay:TYPE?", "VECT")],
        ) as inst:
            assert inst.display_type == "VECT"

    @pytest.mark.parametrize("value", ["MIN", "0.1", "0.5", "1", "5", "10", "INF"])
    def test_display_grading_time_set(self, value):
        with expected_protocol(
            DHO804,
            [(f":DISPlay:GRADing:TIME {value}", None)],
        ) as inst:
            inst.display_grading_time = value

    def test_display_grading_time_invalid_raises(self):
        with expected_protocol(DHO804, []) as inst:
            with pytest.raises(ValueError):
                inst.display_grading_time = "2"


# ======================================================================= #
#  SCPIMixin / utility                                                     #
# ======================================================================= #

class TestUtility:

    def test_id(self):
        with expected_protocol(
            DHO804,
            [("*IDN?", "RIGOL TECHNOLOGIES,DHO804,DHO804XXXXXX,00.01.01")],
        ) as inst:
            assert "DHO804" in inst.id

    def test_reset(self):
        with expected_protocol(
            DHO804,
            [("*RST", None)],
        ) as inst:
            inst.write("*RST")

    def test_wait_for_opc(self):
        with expected_protocol(
            DHO804,
            [("*OPC?", "1")],
        ) as inst:
            inst.wait_for_opc()

    def test_clear_status(self):
        with expected_protocol(
            DHO804,
            [("*CLS", None)],
        ) as inst:
            inst.clear_status()

    def test_status_byte(self):
        with expected_protocol(
            DHO804,
            [("*STB?", "0")],
        ) as inst:
            assert inst.status_byte == 0


# ======================================================================= #
#  Live hardware tests                                                     #
# ======================================================================= #

class TestLiveDevice:
    """Smoke tests that run only when --device-address is supplied.

    These tests verify real communication with the DHO804.  They are
    intentionally lightweight – the goal is to confirm the driver talks
    to the instrument correctly, not to exhaustively test every setting.

    Usage::

        pytest tests/instruments/rigol/test_rigol_dho804.py -v \\
            --device-address "TCPIP::10.150.45.211::INSTR"
    """

    # -- Identity --------------------------------------------------------

    def test_idn_contains_dho804(self, real_instrument):
        """*IDN? must identify the instrument as a DHO804."""
        idn = real_instrument.id
        assert "DHO804" in idn, f"Unexpected IDN response: {idn!r}"

    # -- Channel basics --------------------------------------------------

    @pytest.mark.parametrize("ch_n", [1, 2, 3, 4])
    def test_channel_display_roundtrip(self, real_instrument, ch_n):
        """Write and read back the display state for each channel."""
        channel = getattr(real_instrument, f"ch_{ch_n}")
        original = channel.display
        channel.display = not original
        assert channel.display is not original
        channel.display = original  # restore

    @pytest.mark.parametrize("coupling", ["AC", "DC", "GND"])
    def test_channel_coupling_roundtrip(self, real_instrument, coupling):
        original = real_instrument.ch_1.coupling
        real_instrument.ch_1.coupling = coupling
        assert real_instrument.ch_1.coupling == coupling
        real_instrument.ch_1.coupling = original  # restore

    def test_channel_scale_roundtrip(self, real_instrument):
        original = real_instrument.ch_1.scale
        real_instrument.ch_1.scale = 1.0
        assert real_instrument.ch_1.scale == pytest.approx(1.0, rel=1e-3)
        real_instrument.ch_1.scale = original  # restore

    def test_channel_offset_roundtrip(self, real_instrument):
        original = real_instrument.ch_1.offset
        real_instrument.ch_1.offset = 0.0
        assert real_instrument.ch_1.offset == pytest.approx(0.0, abs=1e-3)
        real_instrument.ch_1.offset = original  # restore

    # -- Timebase --------------------------------------------------------

    def test_timebase_scale_roundtrip(self, real_instrument):
        original = real_instrument.timebase_scale
        real_instrument.timebase_scale = 1e-3
        assert real_instrument.timebase_scale == pytest.approx(1e-3, rel=1e-3)
        real_instrument.timebase_scale = original  # restore

    # -- Trigger ---------------------------------------------------------

    def test_trigger_source_roundtrip(self, real_instrument):
        original = real_instrument.trigger_source
        real_instrument.trigger_source = "CHAN1"
        assert real_instrument.trigger_source == "CHAN1"
        real_instrument.trigger_source = original  # restore

    def test_trigger_level_roundtrip(self, real_instrument):
        original = real_instrument.trigger_level
        real_instrument.trigger_level = 0.0
        assert real_instrument.trigger_level == pytest.approx(0.0, abs=0.01)
        real_instrument.trigger_level = original  # restore

    def test_trigger_status_is_valid(self, real_instrument):
        status = real_instrument.trigger_status
        assert status in ("TD", "WAIT", "RUN", "AUTO", "STOP"), (
            f"Unexpected trigger status: {status!r}"
        )

    # -- Run control -----------------------------------------------------

    def test_run_stop_single(self, real_instrument):
        real_instrument.run()
        real_instrument.stop()
        real_instrument.single()
        real_instrument.run()   # leave scope in running state

    # -- Acquisition -----------------------------------------------------

    def test_sample_rate_positive(self, real_instrument):
        sr = real_instrument.sample_rate
        assert sr > 0, f"Sample rate must be positive, got {sr}"

    # -- Measurement -----------------------------------------------------

    def test_measure_vpp_returns_float(self, real_instrument):
        """measure() must return a float (NaN is acceptable if no signal)."""
        result = real_instrument.measure("VPP", "CHAN1")
        assert isinstance(result, float)

    # -- Waveform download -----------------------------------------------

    def test_get_waveform_shape(self, real_instrument):
        """Waveform arrays must be non-empty and the same length."""
        real_instrument.stop()
        t, v = real_instrument.get_waveform(channel=1, mode="NORMal", fmt="BYTE")
        assert len(t) > 0
        assert len(t) == len(v)
        real_instrument.run()

    def test_get_waveform_time_monotonic(self, real_instrument):
        """Time axis must be strictly increasing."""
        real_instrument.stop()
        t, _ = real_instrument.get_waveform(channel=1)
        assert all(t[i] < t[i + 1] for i in range(len(t) - 1))
        real_instrument.run()