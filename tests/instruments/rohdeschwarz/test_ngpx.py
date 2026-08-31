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

from pymeasure.instruments.rohdeschwarz.ngpx import NGPx, PwrChannel
from pymeasure.test import expected_protocol

# ---------------------------------------------------------------------------
# Test subclasses — suppress the constructor's *IDN? query so individual
# protocol tests can focus on the commands under test without prepending an
# IDN exchange to every expected_protocol list.
# ---------------------------------------------------------------------------


class _NGP4(NGPx):
    """4-channel test stand-in (NGP804 identity, no IDN query)."""

    def get_device_info(self) -> None:
        self.name = "NGP804"

    def check_is_dev_supported(self, *args, **kwargs) -> None:
        pass


class _NGP2(NGPx):
    """2-channel test stand-in (NGP802 identity, no IDN query)."""

    def get_device_info(self) -> None:
        self.name = "NGP802"

    def check_is_dev_supported(self, *args, **kwargs) -> None:
        pass


# ---------------------------------------------------------------------------
# Channel creation
# ---------------------------------------------------------------------------

class TestChannelCreation:
    def test_four_channels_for_ngp804(self):
        with expected_protocol(_NGP4, [], name="NGP804") as inst:
            assert inst.ch1.id == 1
            assert inst.ch2.id == 2
            assert inst.ch3.id == 3
            assert inst.ch4.id == 4

    def test_channels_are_pwrchannel_instances(self):
        with expected_protocol(_NGP4, [], name="NGP804") as inst:
            assert isinstance(inst.ch1, PwrChannel)

    def test_channels_dict_has_four_entries(self):
        with expected_protocol(_NGP4, [], name="NGP804") as inst:
            assert set(inst.channels.keys()) == {1, 2, 3, 4}

    def test_two_channels_for_ngp802(self):
        with expected_protocol(_NGP2, [], name="NGP802") as inst:
            assert inst.ch1.id == 1
            assert inst.ch2.id == 2
            assert not hasattr(inst, "ch3")

    def test_channels_dict_has_two_entries(self):
        with expected_protocol(_NGP2, [], name="NGP802") as inst:
            assert set(inst.channels.keys()) == {1, 2}


# ---------------------------------------------------------------------------
# Voltage / current setpoints
# ---------------------------------------------------------------------------

class TestChannelSetpoints:
    def test_voltage_setpoint_get(self):
        with expected_protocol(_NGP4, [("VOLT? (@1)", "5.000")], name="NGP804") as inst:
            assert inst.ch1.voltage_setpoint == pytest.approx(5.0)

    def test_voltage_setpoint_set(self):
        with expected_protocol(_NGP4, [("VOLT 5.000,(@2)", None)], name="NGP804") as inst:
            inst.ch2.voltage_setpoint = 5.0

    def test_current_limit_get(self):
        with expected_protocol(_NGP4, [("CURR? (@3)", "1.500")], name="NGP804") as inst:
            assert inst.ch3.current_limit == pytest.approx(1.5)

    def test_current_limit_set(self):
        with expected_protocol(_NGP4, [("CURR 2.000,(@4)", None)], name="NGP804") as inst:
            inst.ch4.current_limit = 2.0


# ---------------------------------------------------------------------------
# Measurements
# ---------------------------------------------------------------------------

class TestChannelMeasurements:
    def test_voltage_measurement(self):
        with expected_protocol(_NGP4, [("MEAS:VOLT? (@1)", "4.987")], name="NGP804") as inst:
            assert inst.ch1.voltage == pytest.approx(4.987)

    def test_current_measurement(self):
        with expected_protocol(_NGP4, [("MEAS:CURR? (@2)", "0.250")], name="NGP804") as inst:
            assert inst.ch2.current == pytest.approx(0.25)


# ---------------------------------------------------------------------------
# Safety limits
# ---------------------------------------------------------------------------

class TestChannelSafetyLimits:
    def test_safety_limits_ena_get_true(self):
        with expected_protocol(_NGP4, [("ALIM? (@1)", "1")], name="NGP804") as inst:
            assert inst.ch1.safety_limits_ena is True

    def test_safety_limits_ena_get_false(self):
        with expected_protocol(_NGP4, [("ALIM? (@1)", "0")], name="NGP804") as inst:
            assert inst.ch1.safety_limits_ena is False

    def test_safety_limits_ena_set(self):
        with expected_protocol(_NGP4, [("ALIM 1,(@1)", None)], name="NGP804") as inst:
            inst.ch1.safety_limits_ena = True

    def test_voltage_upper_limit(self):
        with expected_protocol(_NGP4,
                               [("VOLT:ALIM:UPP? (@1)", "6.000"),
                                ("VOLT:ALIM:UPP 6.000,(@1)", None)],
                               name="NGP804") as inst:
            assert inst.ch1.voltage_upper_limit == pytest.approx(6.0)
            inst.ch1.voltage_upper_limit = 6.0

    def test_current_upper_limit(self):
        with expected_protocol(_NGP4,
                               [("CURR:ALIM:UPP? (@1)", "5.000"),
                                ("CURR:ALIM:UPP 5.000,(@1)", None)],
                               name="NGP804") as inst:
            assert inst.ch1.current_upper_limit == pytest.approx(5.0)
            inst.ch1.current_upper_limit = 5.0


# ---------------------------------------------------------------------------
# Remote sense
# ---------------------------------------------------------------------------

class TestChannelSense:
    def test_sense_get_int(self):
        with expected_protocol(_NGP4, [("VOLT:SENS? (@1)", "INT")], name="NGP804") as inst:
            assert inst.ch1.sense == "INT"

    def test_sense_get_ext(self):
        with expected_protocol(_NGP4, [("VOLT:SENS? (@1)", "EXT")], name="NGP804") as inst:
            assert inst.ch1.sense == "EXT"

    def test_sense_set(self):
        with expected_protocol(_NGP4, [("VOLT:SENS EXT,(@1)", None)], name="NGP804") as inst:
            inst.ch1.sense = "EXT"

    def test_sense_invalid_raises(self):
        with expected_protocol(_NGP4, [], name="NGP804") as inst, pytest.raises(ValueError):
            inst.ch1.sense = "INVALID"


# ---------------------------------------------------------------------------
# Overvoltage protection
# ---------------------------------------------------------------------------

class TestChannelOVP:
    def test_ovp_enabled_get_true(self):
        with expected_protocol(_NGP4, [("VOLT:PROT? (@1)", "1")], name="NGP804") as inst:
            assert inst.ch1.ovp_enabled is True

    def test_ovp_enabled_get_false(self):
        with expected_protocol(_NGP4, [("VOLT:PROT? (@1)", "0")], name="NGP804") as inst:
            assert inst.ch1.ovp_enabled is False

    def test_ovp_level_get(self):
        with expected_protocol(_NGP4, [("VOLT:PROT:LEV? (@1)", "6.500")], name="NGP804") as inst:
            assert inst.ch1.ovp_level == pytest.approx(6.5)

    def test_ovp_level_set(self):
        with expected_protocol(_NGP4, [("VOLT:PROT:LEV 6.500,(@1)", None)], name="NGP804") as inst:
            inst.ch1.ovp_level = 6.5

    def test_ovp_tripped_false(self):
        with expected_protocol(_NGP4, [("VOLT:PROT:TRIP? (@1)", "0")], name="NGP804") as inst:
            assert inst.ch1.ovp_tripped is False

    def test_ovp_tripped_true(self):
        with expected_protocol(_NGP4, [("VOLT:PROT:TRIP? (@1)", "1")], name="NGP804") as inst:
            assert inst.ch1.ovp_tripped is True

    def test_ovp_clear(self):
        with expected_protocol(_NGP4, [("VOLT:PROT:CLE (@1)", None)], name="NGP804") as inst:
            inst.ch1.ovp_clear()


# ---------------------------------------------------------------------------
# Overcurrent protection
# ---------------------------------------------------------------------------

class TestChannelOCP:
    def test_ocp_enabled_get_true(self):
        with expected_protocol(_NGP4, [("FUSE? (@1)", "1")], name="NGP804") as inst:
            assert inst.ch1.ocp_enabled is True

    def test_ocp_enabled_get_false(self):
        with expected_protocol(_NGP4, [("FUSE? (@1)", "0")], name="NGP804") as inst:
            assert inst.ch1.ocp_enabled is False

    def test_ocp_delay_initial(self):
        with expected_protocol(_NGP4,
                               [("FUSE:DEL:INIT? (@1)", "0.500"),
                                ("FUSE:DEL:INIT 0.500,(@1)", None)],
                               name="NGP804") as inst:
            assert inst.ch1.ocp_delay_initial == pytest.approx(0.5)
            inst.ch1.ocp_delay_initial = 0.5

    def test_ocp_delay(self):
        with expected_protocol(_NGP4,
                               [("FUSE:DEL? (@1)", "1.000"),
                                ("FUSE:DEL 1.000,(@1)", None)],
                               name="NGP804") as inst:
            assert inst.ch1.ocp_delay == pytest.approx(1.0)
            inst.ch1.ocp_delay = 1.0

    def test_ocp_tripped_false(self):
        with expected_protocol(_NGP4, [("FUSE:TRIP? (@1)", "0")], name="NGP804") as inst:
            assert inst.ch1.ocp_tripped is False

    def test_ocp_tripped_true(self):
        with expected_protocol(_NGP4, [("FUSE:TRIP? (@1)", "1")], name="NGP804") as inst:
            assert inst.ch1.ocp_tripped is True

    def test_ocp_clear(self):
        with expected_protocol(_NGP4, [("FUSE:TRIP:CLE (@1)", None)], name="NGP804") as inst:
            inst.ch1.ocp_clear()


# ---------------------------------------------------------------------------
# Per-channel output
# ---------------------------------------------------------------------------

class TestChannelOutput:
    def test_output_get_true(self):
        with expected_protocol(_NGP4, [("OUTP? (@1)", "1")], name="NGP804") as inst:
            assert inst.ch1.output is True

    def test_output_get_false(self):
        with expected_protocol(_NGP4, [("OUTP? (@1)", "0")], name="NGP804") as inst:
            assert inst.ch1.output is False

    def test_output_set_on(self):
        with expected_protocol(_NGP4, [("OUTP 1,(@1)", None)], name="NGP804") as inst:
            inst.ch1.output = True

    def test_output_set_off(self):
        with expected_protocol(_NGP4, [("OUTP 0,(@2)", None)], name="NGP804") as inst:
            inst.ch2.output = False


# ---------------------------------------------------------------------------
# Channel selection (for bulk output control)
# ---------------------------------------------------------------------------

class TestChannelSelection:
    def test_select_get_false(self):
        with expected_protocol(_NGP4, [("OUTP:SEL? (@1)", "0")], name="NGP804") as inst:
            assert inst.ch1.select is False

    def test_select_get_true(self):
        with expected_protocol(_NGP4, [("OUTP:SEL? (@2)", "1")], name="NGP804") as inst:
            assert inst.ch2.select is True

    def test_select_set_updates_status(self):
        with expected_protocol(_NGP4, [("OUTP:SEL 1,(@1)", None)], name="NGP804") as inst:
            inst.ch1.select = True
            assert inst.ch1._selection_status is True

    def test_select_clear_updates_status(self):
        with expected_protocol(_NGP4, [("OUTP:SEL 0,(@1)", None)], name="NGP804") as inst:
            inst.ch1.select = False
            assert inst.ch1._selection_status is False


# ---------------------------------------------------------------------------
# Bulk output (master output over selected channels)
# ---------------------------------------------------------------------------

class TestBulkOutput:
    def test_output_setter_sends_correct_scpi(self):
        with expected_protocol(_NGP4,
                               [("OUTP:SEL 1,(@1)", None),
                                ("OUTP:SEL 1,(@3)", None),
                                ("OUTP 1,(@1,3)", None)],
                               name="NGP804") as inst:
            inst.ch1.select = True
            inst.ch3.select = True
            inst.output = True

    def test_output_getter_all_on_returns_true(self):
        with expected_protocol(_NGP4,
                               [("OUTP:SEL 1,(@1)", None),
                                ("OUTP:SEL 1,(@2)", None),
                                ("OUTP? (@1,2)", "1,1")],
                               name="NGP804") as inst:
            inst.ch1.select = True
            inst.ch2.select = True
            assert inst.output is True

    def test_output_getter_mixed_returns_false(self):
        with expected_protocol(_NGP4,
                               [("OUTP:SEL 1,(@1)", None),
                                ("OUTP:SEL 1,(@2)", None),
                                ("OUTP? (@1,2)", "1,0")],
                               name="NGP804") as inst:
            inst.ch1.select = True
            inst.ch2.select = True
            assert inst.output is False

    def test_output_setter_no_channels_warns(self):
        with expected_protocol(_NGP4, [], name="NGP804") as inst:
            inst.output = True  # no channels selected — should warn, do nothing

    def test_output_getter_no_channels_returns_false(self):
        with expected_protocol(_NGP4, [], name="NGP804") as inst:
            assert inst.output is False

    def test_output_general_get_false(self):
        with expected_protocol(_NGP4, [("OUTP:GEN?", "0")], name="NGP804") as inst:
            assert inst.output_general is False

    def test_output_general_get_true(self):
        with expected_protocol(_NGP4, [("OUTP:GEN?", "1")], name="NGP804") as inst:
            assert inst.output_general is True

    def test_output_general_set_on(self):
        with expected_protocol(_NGP4, [("OUTP:GEN 1", None)], name="NGP804") as inst:
            inst.output_general = True

    def test_output_general_set_off(self):
        with expected_protocol(_NGP4, [("OUTP:GEN 0", None)], name="NGP804") as inst:
            inst.output_general = False


# ---------------------------------------------------------------------------
# Tracking
# ---------------------------------------------------------------------------

class TestTracking:
    def test_tracking_select_get_false(self):
        with expected_protocol(_NGP4, [("TRAC:SEL:CH1?", "0")], name="NGP804") as inst:
            assert inst.ch1.tracking_select is False

    def test_tracking_select_get_true(self):
        with expected_protocol(_NGP4, [("TRAC:SEL:CH2?", "1")], name="NGP804") as inst:
            assert inst.ch2.tracking_select is True

    def test_tracking_select_set_updates_status(self):
        with expected_protocol(_NGP4, [("TRAC:SEL:CH1 1", None)], name="NGP804") as inst:
            inst.ch1.tracking_select = True
            assert inst.ch1._tracking_status is True

    def test_tracking_enabled_set_uses_comma_separator(self):
        """TRAC command must have a comma between state and channel list."""
        with expected_protocol(_NGP4,
                               [("TRAC:SEL:CH1 1", None),
                                ("TRAC:SEL:CH2 1", None),
                                ("TRAC 1,(@1,2)", None)],
                               name="NGP804") as inst:
            inst.ch1.tracking_select = True
            inst.ch2.tracking_select = True
            inst.tracking_enabled = True

    def test_tracking_enabled_get_true(self):
        with expected_protocol(_NGP4,
                               [("TRAC:SEL:CH1 1", None),
                                ("TRAC? (@1)", "1")],
                               name="NGP804") as inst:
            inst.ch1.tracking_select = True
            assert inst.tracking_enabled is True

    def test_tracking_enabled_no_channels_returns_false(self):
        with expected_protocol(_NGP4, [], name="NGP804") as inst:
            assert inst.tracking_enabled is False

    def test_tracking_enabled_set_no_channels_warns(self):
        with expected_protocol(_NGP4, [], name="NGP804") as inst:
            inst.tracking_enabled = True  # no channels — warn, do nothing

    def test_tracking_general_enabled_get_false(self):
        with expected_protocol(_NGP4, [("TRAC:GEN?", "0")], name="NGP804") as inst:
            assert inst.tracking_general_enabled is False

    def test_tracking_general_enabled_set_true(self):
        with expected_protocol(_NGP4, [("TRAC:GEN 1", None)], name="NGP804") as inst:
            inst.tracking_general_enabled = True


# ---------------------------------------------------------------------------
# OCP linking
# ---------------------------------------------------------------------------

class TestOCPLinking:
    def test_link_ocp(self):
        with expected_protocol(_NGP4, [("INST (@1);FUSE:LINK 2,3", None)], name="NGP804") as inst:
            inst.link_ocp(1, 2, 3)

    def test_link_ocp_ignores_self_link(self):
        with expected_protocol(_NGP4, [("INST (@1);FUSE:LINK 2", None)], name="NGP804") as inst:
            inst.link_ocp(1, 1, 2)

    def test_link_ocp_no_valid_targets_skips(self):
        with expected_protocol(_NGP4, [], name="NGP804") as inst:
            inst.link_ocp(1, 1)

    def test_unlink_ocp_all(self):
        with expected_protocol(_NGP4, [("INST (@1);FUSE:UNL 0", None)], name="NGP804") as inst:
            inst.unlink_ocp(1)

    def test_unlink_ocp_specific(self):
        with expected_protocol(_NGP4, [("INST (@1);FUSE:UNL 2", None)], name="NGP804") as inst:
            inst.unlink_ocp(1, 2)

    def test_get_ocp_linked_channels_empty(self):
        with expected_protocol(_NGP4, [("INST (@1);FUSE:LINK?", "0")], name="NGP804") as inst:
            assert inst.get_ocp_linked_channels(1) == []

    def test_get_ocp_linked_channels(self):
        with expected_protocol(_NGP4, [("INST (@1);FUSE:LINK?", "2,3")], name="NGP804") as inst:
            assert inst.get_ocp_linked_channels(1) == [2, 3]


# ---------------------------------------------------------------------------
# Local / remote control
# ---------------------------------------------------------------------------

class TestLocalRemote:
    def test_set2local(self):
        with expected_protocol(_NGP4, [("SYST:LOC", None)], name="NGP804") as inst:
            inst.set2local()

    def test_set2remote(self):
        with expected_protocol(_NGP4, [("SYST:REM", None)], name="NGP804") as inst:
            inst.set2remote()


# ---------------------------------------------------------------------------
# Constructor — identity query (uses real NGPx so the full init runs)
# ---------------------------------------------------------------------------

class TestNGPxConstructorIdentity:
    """Verify *IDN? query, attribute population, and dynamic channels.

    These tests use the real NGPx class so the full constructor path is
    exercised.  The expected_protocol list must include the IDN exchange.
    The context-manager calls shutdown() on exit which sends SYST:LOC.
    """

    def test_constructor_sets_name_from_idn(self):
        with expected_protocol(NGPx,
                               [("*IDN?", "Rohde&Schwarz,NGP804,123456,V1.00")],
                               name="NGP804") as inst:
            assert inst.name == "NGP804"

    def test_constructor_sets_vendor_serial_firmware(self):
        with expected_protocol(NGPx,
                               [("*IDN?", "Rohde&Schwarz,NGP804,123456,V1.00")],
                               name="NGP804") as inst:
            assert inst.vendor == "Rohde&Schwarz"
            assert inst.serial_number == "123456"
            assert inst.firmware_ref == "V1.00"

    def test_constructor_creates_ch1_to_ch4_for_ngp804(self):
        with expected_protocol(NGPx,
                               [("*IDN?", "Rohde&Schwarz,NGP804,123456,V1.00")],
                               name="NGP804") as inst:
            for i in (1, 2, 3, 4):
                assert hasattr(inst, f"ch{i}")
                assert isinstance(getattr(inst, f"ch{i}"), PwrChannel)

    def test_constructor_creates_ch1_to_ch2_for_ngp802(self):
        with expected_protocol(NGPx,
                               [("*IDN?", "Rohde&Schwarz,NGP802,999,V2.00")],
                               name="NGP802") as inst:
            assert hasattr(inst, "ch1")
            assert hasattr(inst, "ch2")
            assert not hasattr(inst, "ch3")

    def test_constructor_rejects_unsupported_model(self):
        with pytest.raises(AssertionError), expected_protocol(NGPx,
                               [("*IDN?", "Rohde&Schwarz,NGP999,123456,V1.00")],
                               name="NGP999"):
            pass
