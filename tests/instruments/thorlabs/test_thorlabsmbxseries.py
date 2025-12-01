from pymeasure.test import expected_protocol
from pymeasure.instruments.thorlabs.thorlabsmbxseries import (
    ThorlabsMBXSeries,
    MzmMode,
    VoaMode,
    RgbPowerMode,
)


def test_calibrate_mzm():
    protocol = [("MZM:RESET", b"1")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.mzm.calibrate()


def test_mzm_is_calibrating():
    protocol = [("MZM:CALIBRATING?", b"0")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.mzm.is_calibrating is False


def test_mzm_is_stable():
    protocol = [("MZM:SETPOINT?", b"1")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.mzm.is_stable is True


def test_mzm_mode_setter():
    protocol = [("MZM:MODE: 3", None)]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.mzm.mode = MzmMode.AUTOQUADPOS


def test_mzm_mode_getter():
    protocol = [("MZM:MODE?", b"5")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.mzm.mode == MzmMode.HOLDQUADPOS


def test_mzm_ratio_setpoint_setter():
    protocol = [("MZM:HOLD:RATIO: 500", None)]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.mzm.ratio_setpoint = 5.004


def test_mzm_ratio_setpoint_getter():
    protocol = [("MZM:HOLD:RATIO?", b"500")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.mzm.ratio_setpoint == 5.0


def test_mzm_voltage_setpoint_setter():
    protocol = [("MZM:HOLD:VOLTAGE: 5000", None)]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.mzm.voltage_setpoint = 5.0004


def test_mzm_voltage_setpoint_getter():
    protocol = [("MZM:HOLD:VOLTAGE?", b"5000")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.mzm.voltage_setpoint == 5


def test_mzm_voltage():
    protocol = [("MZM:VOLTAGE?", b"5.42")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.mzm.voltage == 5.42


def test_mzm_power():
    protocol = [("MZM:TAP:MW?", b"1.23")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.mzm.power == 1.23


def test_voa_enabled_setter():
    protocol = [("VOA:POWER: 1", None)]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.voa.enabled = True


def test_voa_enabled_getter():
    protocol = [("VOA:POWER?", b"0")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.voa.enabled is False


def test_voa_is_stable():
    protocol = [("VOA:SETPOINT?", b"0")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.voa.is_stable is False


def test_voa_mode_setter():
    protocol = [("VOA:MODE: 0", b"1")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.voa.mode = VoaMode.ATTENUATION


def test_voa_mode_getter():
    protocol = [("VOA:MODE?", b"1")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.voa.mode == VoaMode.POWER


def test_voa_attenuation_setpoint_setter():
    protocol = [("VOA:ATTEN: 5", None)]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.voa.attenuation_setpoint = 5


def test_voa_attenuation_setpoint_getter():
    protocol = [("VOA:ATTEN?", b"5")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.voa.attenuation_setpoint == 5


def test_voa_attenuation():
    protocol = [("VOA:MEASURED?", b"5")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.voa.attenuation == 5


def test_voa_attenuation_error():
    protocol = [("VOA:ERROR?", b"0.1")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.voa.attenuation_error == 0.1


def test_voa_power_setpoint_setter():
    protocol = [("VOA:OUTPUT:MW: 5", None)]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.voa.power_setpoint = 5


def test_voa_power_setpoint_getter():
    protocol = [("VOA:OUTPUT:MW?", b"5")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.voa.power_setpoint == 5


def test_voa_power():
    protocol = [("VOA:TAP:MW?", b"5")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.voa.power == 5


def test_rgb_mode_setter():
    protocol = [("RGB:POWER: 0", None)]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.rgb.mode = RgbPowerMode.OFF


def test_rgb_mode_getter():
    protocol = [("RGB:POWER?", b"2")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.rgb.mode == RgbPowerMode.WHITE


def test_rgb_rgb_setter():
    protocol = [("RGB:RED: 55", None), ("RGB:GREEN: 65", None), ("RGB:BLUE: 75", None)]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.rgb.rgb = (55, 65, 75)


def test_rgb_rgb_getter():
    protocol = [("RGB:RED?", b"25"), ("RGB:GREEN?", b"35"), ("RGB:BLUE?", b"45")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.rgb.rgb == (25, 35, 45)


def test_rgb_white_setter():
    protocol = [("RGB:WHITE: 50", None)]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.rgb.white = 50


def test_rgb_white_getter():
    protocol = [("RGB:WHITE?", 40)]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.rgb.white == 40
