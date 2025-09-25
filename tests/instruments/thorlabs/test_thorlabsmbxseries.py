from pymeasure.test import expected_protocol
from pymeasure.instruments.thorlabs.thorlabsmbxseries import (
    ThorlabsMBXSeries,
    MzmMode,
    VoaMode,
)


def test_calibrate_mzm():
    protocol = [("MZM:RESET", b"1")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.calibrate_mzm()


def test_mzm_calibrating():
    protocol = [("MZM:CALIBRATING?", b"0")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.mzm_calibrating is False


def test_mzm_stable():
    protocol = [("MZM:SETPOINT?", b"1")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.mzm_stable is True


def test_mzm_mode_setter():
    protocol = [("MZM:MODE: 3", None)]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.mzm_mode = MzmMode.AUTOQUADPOS


def test_mzm_mode_getter():
    protocol = [("MZM:MODE?", b"5")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.mzm_mode == MzmMode.HOLDQUADPOS


def test_mzm_ratio_setpoint_setter():
    protocol = [("MZM:HOLD:RATIO: 500", None)]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.mzm_ratio_setpoint = 5.004


def test_mzm_ratio_setpoint_getter():
    protocol = [("MZM:HOLD:RATIO?", b"500")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.mzm_ratio_setpoint == 5.0


def test_mzm_voltage_setpoint_setter():
    protocol = [("MZM:HOLD:VOLTAGE: 5000", None)]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.mzm_voltage_setpoint = 5.0004


def test_mzm_voltage_setpoint_getter():
    protocol = [("MZM:HOLD:VOLTAGE?", b"5000")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.mzm_voltage_setpoint == 5


def test_mzm_voltage():
    protocol = [("MZM:VOLTAGE?", b"5.42")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.mzm_voltage == 5.42


def test_mzm_power():
    protocol = [("MZM:TAP:MW?", b"1.23")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.mzm_power == 1.23


def test_voa_enabled_setter():
    protocol = [("VOA:POWER: 1", None)]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.voa_enabled = True


def test_voa_enabled_getter():
    protocol = [("VOA:POWER?", b"0")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.voa_enabled is False


def test_voa_stable():
    protocol = [("VOA:SETPOINT?", b"0")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.voa_stable is False


def test_voa_mode_setter():
    protocol = [("VOA:MODE: 0", b"1")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.voa_mode = VoaMode.ATTENUATION


def test_voa_mode_getter():
    protocol = [("VOA:MODE?", b"1")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.voa_mode == VoaMode.POWER


def test_voa_attenuation_setpoint_setter():
    protocol = [("VOA:ATTEN: 5", None)]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.voa_attenuation_setpoint = 5


def test_voa_attenuation_setpoint_getter():
    protocol = [("VOA:ATTEN?", b"5")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.voa_attenuation_setpoint == 5


def test_voa_attenuation():
    protocol = [("VOA:MEASURED?", b"5")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.voa_attenuation == 5


def test_voa_attenuation_error():
    protocol = [("VOA:ERROR?", b"0.1")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.voa_attenuation_error == 0.1


def test_voa_power_setpoint_setter():
    protocol = [("VOA:OUTPUT:MW: 5", None)]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        inst.voa_power_setpoint = 5


def test_voa_power_setpoint_getter():
    protocol = [("VOA:OUTPUT:MW?", b"5")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.voa_power_setpoint == 5


def test_voa_power():
    protocol = [("VOA:TAP:MW?", b"5")]
    with expected_protocol(ThorlabsMBXSeries, protocol) as inst:
        assert inst.voa_power == 5
