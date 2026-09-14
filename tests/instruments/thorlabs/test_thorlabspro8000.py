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

from pymeasure.instruments.thorlabs.thorlabspro8000 import (
    ITCChannel,
    LDCChannel,
    PDAChannel,
    PDAPortChannel,
    TEDChannel,
    ThorlabsPro8000,
)
from pymeasure.test import expected_protocol

# Module map used for most tests: slot 1 = LDC, slot 2 = TED, slot 3 = ITC,
# slot 4 = PDA8000-2 (two ports), the remaining slots are empty.
# ``:CONFIG:PLUG?`` returns (type, subtype) pairs; for a PDA the subtype is the
# model variant and equals the port count (1 = PDA8000-1, 2 = PDA8000-2).
CONFIG = "191,0,223,0,159,0,107,2,0,0,0,0,0,0,0,0"

# Communication that every connection performs in ``__init__``.
INIT = [
    (":SYST:ANSW VALUE", None),
    (":CONFIG:PLUG?", CONFIG),
]


def test_init():
    """The mainframe queries its modules and creates one channel per populated slot."""
    with expected_protocol(ThorlabsPro8000, INIT) as inst:
        assert set(inst.channels.keys()) == {1, 2, 3, 4}
        assert isinstance(inst.channels[1], LDCChannel)
        assert isinstance(inst.channels[2], TEDChannel)
        assert isinstance(inst.channels[3], ITCChannel)
        assert isinstance(inst.channels[4], PDAChannel)


def test_pda8000_2_has_two_ports():
    """A PDA8000-2 (subtype 2) exposes two ports."""
    with expected_protocol(ThorlabsPro8000, INIT) as inst:
        assert set(inst.channels[4].ports.keys()) == {1, 2}
        assert isinstance(inst.channels[4].port_1, PDAPortChannel)
        assert isinstance(inst.channels[4].port_2, PDAPortChannel)


def test_pda8000_1_has_one_port():
    """A PDA8000-1 (subtype 1) exposes a single port and no second one."""
    config = "107,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    with expected_protocol(
        ThorlabsPro8000,
        [(":SYST:ANSW VALUE", None), (":CONFIG:PLUG?", config)],
    ) as inst:
        assert set(inst.channels[1].ports.keys()) == {1}
        assert isinstance(inst.channels[1].port_1, PDAPortChannel)
        assert not hasattr(inst.channels[1], "port_2")


def test_pda_port_selects_slot_and_port():
    """A PDA port command selects both slot and port before the command."""
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 4", None), (":PORT 2", None), (":IPD:ACT?", "1.5E-06")],
    ) as inst:
        assert inst.channels[4].port_2.current == pytest.approx(1.5e-6)


def test_pda_optical_power():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 4", None), (":PORT 1", None), (":POPT:ACT?", "0.002")],
    ) as inst:
        assert inst.channels[4].port_1.optical_power == pytest.approx(0.002)


def test_pda_range_setter():
    # 100e-6 A full scale maps to range index 5.
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 4", None), (":PORT 1", None), (":RANGE 5", None)],
    ) as inst:
        inst.channels[4].port_1.measurement_range = 100e-6


def test_pda_range_getter():
    # Range index 3 maps to 1e-6 A full scale.
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 4", None), (":PORT 1", None), (":RANGE?", "3")],
    ) as inst:
        assert inst.channels[4].port_1.measurement_range == 1e-6


def test_pda_bias_enabled_setter():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 4", None), (":PORT 2", None), (":PDBIA ON", None)],
    ) as inst:
        inst.channels[4].port_2.bias_enabled = True


def test_pda_bias_voltage_setter():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 4", None), (":PORT 1", None), (":VBIAS:SET 5", None)],
    ) as inst:
        inst.channels[4].port_1.bias_voltage = 5


def test_no_channel_for_empty_or_unsupported_slots():
    """Empty (0) and unsupported (MLC=47, WDM-B=249) slots do not create a channel."""
    config = "47,0,249,0,0,0,0,0,0,0,0,0,0,0,0,0"
    with expected_protocol(
        ThorlabsPro8000,
        [(":SYST:ANSW VALUE", None), (":CONFIG:PLUG?", config)],
    ) as inst:
        assert inst.channels == {}


def test_channel_selects_slot_before_command():
    """Every channel command is prefixed by a separate ``:SLOT`` selection."""
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 1", None), (":ILD:SET 0.05", None)],
    ) as inst:
        inst.channels[1].current_setpoint = 0.05


def test_ldc_laser_enabled_setter():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 1", None), (":LASER ON", None)],
    ) as inst:
        inst.channels[1].laser_enabled = True


def test_ldc_laser_enabled_getter():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 1", None), (":LASER?", "OFF")],
    ) as inst:
        assert inst.channels[1].laser_enabled is False


def test_ldc_current_measurement():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 1", None), (":ILD:ACT?", "5.1234E-02")],
    ) as inst:
        assert inst.channels[1].current == pytest.approx(0.051234)


def test_ldc_voltage_measurement():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 1", None), (":VLD:ACT?", "1.85")],
    ) as inst:
        assert inst.channels[1].voltage == pytest.approx(1.85)


def test_ldc_hardware_limit():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 1", None), (":LIMCP:ACT?", "0.2")],
    ) as inst:
        assert inst.channels[1].current_hardware_limit == pytest.approx(0.2)


def test_ldc_polarity_setter():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 1", None), (":LDPOL CG", None)],
    ) as inst:
        inst.channels[1].ld_polarity = "CG"


def test_ldc_polarity_getter():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 1", None), (":LDPOL?", "AG")],
    ) as inst:
        assert inst.channels[1].ld_polarity == "AG"


def test_ldc_polarity_invalid():
    with expected_protocol(ThorlabsPro8000, INIT) as inst, pytest.raises(ValueError):
        inst.channels[1].ld_polarity = "XX"


def test_ldc_mode_setter():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 1", None), (":MODE CP", None)],
    ) as inst:
        inst.channels[1].mode = "CP"


def test_ted_enabled_setter():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 2", None), (":TEC OFF", None)],
    ) as inst:
        inst.channels[2].tec_enabled = False


def test_ted_temperature_measurement():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 2", None), (":TEMP:ACT?", "25.3")],
    ) as inst:
        assert inst.channels[2].temperature == pytest.approx(25.3)


def test_ted_temperature_setpoint():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 2", None), (":TEMP:SET 21", None)],
    ) as inst:
        inst.channels[2].temperature_setpoint = 21


def test_ted_tec_current():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 2", None), (":ITE:ACT?", "0.42")],
    ) as inst:
        assert inst.channels[2].tec_current == pytest.approx(0.42)


def test_ted_pid_share_setter():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 2", None), (":SHAREP:SET 30", None)],
    ) as inst:
        inst.channels[2].pid_p_share = 30


def test_ted_pid_share_out_of_range():
    with expected_protocol(ThorlabsPro8000, INIT) as inst, pytest.raises(ValueError):
        inst.channels[2].pid_i_share = 150


def test_itc_has_both_laser_and_tec():
    """An ITC channel exposes both laser (LDC) and temperature (TED) commands."""
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [
            (":SLOT 3", None), (":LASER ON", None),
            (":SLOT 3", None), (":TEMP:ACT?", "20.0"),
        ],
    ) as inst:
        inst.channels[3].laser_enabled = True
        assert inst.channels[3].temperature == pytest.approx(20.0)


def test_module_type_query():
    with expected_protocol(
        ThorlabsPro8000,
        INIT + [(":SLOT 1", None), (":TYPE:TXT?", "LDC8xxx")],
    ) as inst:
        assert inst.channels[1].module_type == "LDC8xxx"
