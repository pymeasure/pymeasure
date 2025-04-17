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

from pymeasure.test import expected_protocol
from pymeasure.instruments.srs.ldc500series import LDC500Series, ThemometerType


def test_init():
    with expected_protocol(LDC500Series, []):
        pass


# =========================
# === Laser Diode Tests ===
# =========================


def test_interlock_closed_getter():
    with expected_protocol(LDC500Series, [(b"ILOC?", b"CLOSED\n")]) as inst:
        assert inst.interlock_closed is True


# --- ld_enabled ---
def test_ld_enabled_setter():
    with expected_protocol(LDC500Series, [(b"LDON ON", None)]) as inst:
        inst.ld.enabled = True


def test_ld_enabled_getter():
    with expected_protocol(LDC500Series, [(b"LDON?", b"ON\n")]) as inst:
        assert inst.ld.enabled is True


# --- ld_mode ---
def test_ld_mode_setter():
    with expected_protocol(
        LDC500Series, [(b"SMOD CP", None), (b"LEXE?", b"0"), (b"LCME?", b"0")]
    ) as inst:
        inst.ld.mode = "CP"


def test_ld_mode_getter():
    with expected_protocol(LDC500Series, [(b"SMOD?", b"CC\n")]) as inst:
        assert inst.ld.mode == "CC"


# --- ld_current ---
def test_ld_current_getter():
    with expected_protocol(LDC500Series, [(b"RILD?", b"10")]) as inst:
        assert inst.ld.current == 10


# --- ld_current_setpoint ---
def test_ld_current_setpoint_setter():
    with expected_protocol(
        LDC500Series, [(b"SILD 15", None), (b"LEXE?", b"0"), (b"LCME?", b"0")]
    ) as inst:
        inst.ld.current_setpoint = 15


def test_ld_current_setpoint_getter():
    with expected_protocol(LDC500Series, [(b"SILD?", b"15\n")]) as inst:
        assert inst.ld.current_setpoint == 15


# --- ld_current_limit ---
def test_ld_current_limit_setter():
    with expected_protocol(
        LDC500Series, [(b"SILM 20", None), (b"LEXE?", b"0"), (b"LCME?", b"0")]
    ) as inst:
        inst.ld.current_limit = 20


def test_ld_current_limit_getter():
    with expected_protocol(LDC500Series, [(b"SILM?", b"20\n")]) as inst:
        assert inst.ld.current_limit == 20


# --- ld_current_range ---
def test_ld_current_range_setter():
    with expected_protocol(LDC500Series, [(b"RNGE HIGH", None)]) as inst:
        inst.ld.current_range = "HIGH"


def test_ld_current_range_getter():
    with expected_protocol(LDC500Series, [(b"RNGE?", b"HIGH\n")]) as inst:
        assert inst.ld.current_range == "HIGH"


# --- ld_voltage ---
def test_ld_voltage_getter():
    with expected_protocol(LDC500Series, [(b"RVLD?", b"2")]) as inst:
        assert inst.ld.voltage == 2


# --- ld_voltage_limit ---
def test_ld_voltage_limit_setter():
    with expected_protocol(LDC500Series, [(b"SVLM 8", None)]) as inst:
        inst.ld.voltage_limit = 8


def test_ld_voltage_limit_getter():
    with expected_protocol(LDC500Series, [(b"SVLM?", b"8\n")]) as inst:
        assert inst.ld.voltage_limit == 8


# --- ld_modulation_enabled ---
def test_ld_modulation_enabled_setter():
    with expected_protocol(LDC500Series, [(b"MODU ON", None)]) as inst:
        inst.ld.modulation_enabled = True


def test_ld_modulation_enabled_getter():
    with expected_protocol(LDC500Series, [(b"MODU?", b"ON\n")]) as inst:
        assert inst.ld.modulation_enabled is True


# --- ld_modulation_bandwidth ---
def test_ld_modulation_bandwidth_setter():
    with expected_protocol(LDC500Series, [(b"SIBW HIGH", None)]) as inst:
        inst.ld.modulation_bandwidth = "HIGH"


def test_ld_modulation_bandwidth_getter():
    with expected_protocol(LDC500Series, [(b"SIBW?", b"HIGH\n")]) as inst:
        assert inst.ld.modulation_bandwidth == "HIGH"


# ========================
# === Photodiode Tests ===
# ========================


# --- pd_units ---
def test_pd_units_setter():
    with expected_protocol(LDC500Series, [(b"PDMW ON", None)]) as inst:
        inst.pd.units = "mW"


def test_pd_units_getter():
    with expected_protocol(LDC500Series, [(b"PDMW?", b"ON\n")]) as inst:
        # Mapped value "ON" converts back to "mW"
        assert inst.pd.units == "mW"


# --- pd_bias ---
def test_pd_bias_setter():
    with expected_protocol(LDC500Series, [(b"BIAS 3", None)]) as inst:
        inst.pd.bias = 3


def test_pd_bias_getter():
    with expected_protocol(LDC500Series, [(b"BIAS?", b"3\n")]) as inst:
        assert inst.pd.bias == 3


# --- pd_current ---
def test_pd_current_getter():
    with expected_protocol(LDC500Series, [(b"RIPD?", b"20")]) as inst:
        assert inst.pd.current == 20


# --- pd_current_setpoint ---
def test_pd_current_setpoint_setter():
    with expected_protocol(
        LDC500Series, [(b"SIPD 1500", None), (b"LEXE?", b"0"), (b"LCME?", b"0")]
    ) as inst:
        inst.pd.current_setpoint = 1500


def test_pd_current_setpoint_getter():
    with expected_protocol(LDC500Series, [(b"SIPD?", b"1500\n")]) as inst:
        assert inst.pd.current_setpoint == 1500


# --- pd_current_limit ---
def test_pd_current_limit_setter():
    with expected_protocol(LDC500Series, [(b"PILM 1800", None)]) as inst:
        inst.pd.current_limit = 1800


def test_pd_current_limit_getter():
    with expected_protocol(LDC500Series, [(b"PILM?", b"1800\n")]) as inst:
        assert inst.pd.current_limit == 1800


# --- pd_calibrate ---
def test_pd_calibrate_func():
    with expected_protocol(LDC500Series, [(b"CALP 10", None)]) as inst:
        inst.pd.calibrate(10)


# --- pd_responsivity ---
def test_pd_responsivity_setter():
    with expected_protocol(LDC500Series, [(b"RESP 0.5", None)]) as inst:
        inst.pd.responsivity = 0.5


def test_pd_responsivity_getter():
    with expected_protocol(LDC500Series, [(b"RESP?", b"0.5\n")]) as inst:
        assert inst.pd.responsivity == 0.5


# --- pd_power ---
def test_pd_power_getter():
    with expected_protocol(LDC500Series, [(b"RWPD?", b"2.5")]) as inst:
        assert inst.pd.power == 2.5


# --- pd_power_setpoint ---
def test_pd_power_setpoint_setter():
    with expected_protocol(LDC500Series, [(b"SWPD 2.5", None)]) as inst:
        inst.pd.power_setpoint = 2.5


def test_pd_power_setpoint_getter():
    with expected_protocol(LDC500Series, [(b"SWPD?", b"2.5\n")]) as inst:
        assert inst.pd.power_setpoint == 2.5


# --- pd_power_limit ---
def test_pd_power_limit_setter():
    with expected_protocol(LDC500Series, [(b"PWLM 3", None)]) as inst:
        inst.pd.power_limit = 3


def test_pd_power_limit_getter():
    with expected_protocol(LDC500Series, [(b"PWLM?", b"3\n")]) as inst:
        assert inst.pd.power_limit == 3


# ============================
# === TEC Controller Tests ===
# ============================


# --- tec_enabled ---
def test_tec_enabled_setter():
    with expected_protocol(LDC500Series, [(b"TEON 1", None)]) as inst:
        inst.tec.enabled = True


def test_tec_enabled_getter():
    with expected_protocol(LDC500Series, [(b"TEON?", b"1\n")]) as inst:
        assert inst.tec.enabled is True


# --- tec_mode ---
def test_tec_mode_setter():
    with expected_protocol(LDC500Series, [(b"TMOD CT", None)]) as inst:
        inst.tec.mode = "CT"


def test_tec_mode_getter():
    with expected_protocol(LDC500Series, [(b"TMOD?", b"CT\n")]) as inst:
        assert inst.tec.mode == "CT"


# --- tec_thermometer_type ---
def test_tec_thermometer_type_setter():
    with expected_protocol(LDC500Series, [(b"TSNR 0", None)]) as inst:
        inst.tec.thermometer_type = ThemometerType.NTC10UA


def test_tec_thermometer_type_getter():
    with expected_protocol(LDC500Series, [(b"TSNR?", b"0\n")]) as inst:
        assert inst.tec.thermometer_type == ThemometerType.NTC10UA


# --- tec_current ---
def test_tec_current_getter():
    with expected_protocol(LDC500Series, [(b"TIRD?", b"0.2")]) as inst:
        assert inst.tec.current == 0.2


# --- tec_current_setpoint ---
def test_tec_current_setpoint_setter():
    with expected_protocol(
        LDC500Series, [(b"TCUR 0.3", None), (b"LEXE?", b"0"), (b"LCME?", b"0")]
    ) as inst:
        inst.tec.current_setpoint = 0.3


def test_tec_current_setpoint_getter():
    with expected_protocol(LDC500Series, [(b"TCUR?", b"0.3\n")]) as inst:
        assert inst.tec.current_setpoint == 0.3


# --- tec_current_limit ---
def test_tec_current_limit_setter():
    with expected_protocol(LDC500Series, [(b"TILM 0.4", None)]) as inst:
        inst.tec.current_limit = 0.4


def test_tec_current_limit_getter():
    with expected_protocol(LDC500Series, [(b"TILM?", b"0.4\n")]) as inst:
        assert inst.tec.current_limit == 0.4


# --- tec_voltage ---
def test_tec_voltage_getter():
    with expected_protocol(LDC500Series, [(b"TVRD?", b"5")]) as inst:
        assert inst.tec.voltage == 5


# --- tec_voltage_limit ---
def test_tec_voltage_limit_setter():
    with expected_protocol(LDC500Series, [(b"TVLM 7", None)]) as inst:
        inst.tec.voltage_limit = 7


def test_tec_voltage_limit_getter():
    with expected_protocol(LDC500Series, [(b"TVLM?", b"7\n")]) as inst:
        assert inst.tec.voltage_limit == 7


# --- tec_temperature ---
def test_tec_temperature_getter():
    with expected_protocol(LDC500Series, [(b"TTRD?", b"25")]) as inst:
        assert inst.tec.temperature == 25


# --- tec_thermometer_raw
def test_tec_thermometer_raw_getter():
    with expected_protocol(LDC500Series, [(b"TRAW?", b"1.5")]) as inst:
        assert inst.tec.thermometer_raw == 1.5


# --- tec_temperature_setpoint ---
def test_tec_temperature_setpoint_setter():
    with expected_protocol(
        LDC500Series, [(b"TEMP 30", None), (b"LEXE?", b"0"), (b"LCME?", b"0")]
    ) as inst:
        inst.tec.temperature_setpoint = 30


def test_tec_temperature_setpoint_getter():
    with expected_protocol(LDC500Series, [(b"TEMP?", b"30\n")]) as inst:
        assert inst.tec.temperature_setpoint == 30


# --- tec_temperature_low_limit ---
def test_tec_temperature_low_limit_setter():
    with expected_protocol(
        LDC500Series, [(b"TMIN 15", None), (b"LEXE?", b"0"), (b"LCME?", b"0")]
    ) as inst:
        inst.tec.temperature_low_limit = 15


def test_tec_temperature_low_limit_getter():
    with expected_protocol(LDC500Series, [(b"TMIN?", b"15\n")]) as inst:
        assert inst.tec.temperature_low_limit == 15


# --- tec_temperature_high_limit ---
def test_tec_temperature_high_limit_setter():
    with expected_protocol(
        LDC500Series, [(b"TMAX 35", None), (b"LEXE?", b"0"), (b"LCME?", b"0")]
    ) as inst:
        inst.tec.temperature_high_limit = 35


def test_tec_temperature_high_limit_getter():
    with expected_protocol(LDC500Series, [(b"TMAX?", b"35\n")]) as inst:
        assert inst.tec.temperature_high_limit == 35


# --- tec_temperature_limits ---
def test_tec_temperature_limits_setter():
    with expected_protocol(
        LDC500Series,
        [
            (b"TMIN 15", None),
            (b"LEXE?", b"0"),
            (b"LCME?", b"0"),
            (b"TMAX 35", None),
            (b"LEXE?", b"0"),
            (b"LCME?", b"0"),
        ],
    ) as inst:
        inst.tec.temperature_limits = (15, 35)


def test_tec_temperature_limits_getter():
    with expected_protocol(LDC500Series, [(b"TMIN?", b"15\n"), (b"TMAX?", b"35\n")]) as inst:
        assert inst.tec.temperature_limits == (15, 35)


# --- tec_resistance_setpoint ---
def test_tec_resistance_setpoint_setter():
    with expected_protocol(
        LDC500Series, [(b"TRTH 2", None), (b"LEXE?", b"0"), (b"LCME?", b"0")]
    ) as inst:
        inst.tec.resistance_setpoint = 2


def test_tec_resistance_setpoint_getter():
    with expected_protocol(LDC500Series, [(b"TRTH?", b"2\n")]) as inst:
        assert inst.tec.resistance_setpoint == 2


# --- tec_resistance_low_limit ---
def test_tec_resistance_low_limit_setter():
    with expected_protocol(
        LDC500Series, [(b"TRMN 1", None), (b"LEXE?", b"0"), (b"LCME?", b"0")]
    ) as inst:
        inst.tec.resistance_low_limit = 1


def test_tec_resistance_low_limit_getter():
    with expected_protocol(LDC500Series, [(b"TRMN?", b"1\n")]) as inst:
        assert inst.tec.resistance_low_limit == 1


# --- tec_resistance_high_limit ---
def test_tec_resistance_high_limit_setter():
    with expected_protocol(
        LDC500Series, [(b"TRMX 3", None), (b"LEXE?", b"0"), (b"LCME?", b"0")]
    ) as inst:
        inst.tec.resistance_high_limit = 3


def test_tec_resistance_high_limit_getter():
    with expected_protocol(LDC500Series, [(b"TRMX?", b"3\n")]) as inst:
        assert inst.tec.resistance_high_limit == 3


# --- tec_resistance_limits ---
def test_tec_resistance_limits_setter():
    with expected_protocol(
        LDC500Series,
        [
            (b"TRMN 1", None),
            (b"LEXE?", b"0"),
            (b"LCME?", b"0"),
            (b"TRMX 3", None),
            (b"LEXE?", b"0"),
            (b"LCME?", b"0"),
        ],
    ) as inst:
        inst.tec.resistance_limits = (1, 3)


def test_tec_resistance_limits_getter():
    with expected_protocol(LDC500Series, [(b"TRMN?", b"1\n"), (b"TRMX?", b"3\n")]) as inst:
        assert inst.tec.resistance_limits == (1, 3)
