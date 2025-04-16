import pytest

from pymeasure.errors import Error
from pymeasure.instruments.srs import LDC500Series

##################################
# LDC501 device address goes here:
connected_device_address = "GPIB0::12::INSTR"
##################################


@pytest.fixture(scope="module")
def ldc501(connected_device_address):
    instr = LDC500Series(connected_device_address)
    instr.reset()
    instr.check_errors()
    instr.ld_current_range = "LOW"
    return instr


# --- ld current ---


def test_ld_current_limit_no_error(ldc501):
    ldc501.ld_current_limit = 100
    assert ldc501.ld_current_limit == 100


def test_ld_current_limit_out_range(ldc501):
    with pytest.raises(Error):
        ldc501.ld_current_limit = 300


def test_ld_current_setpoint_no_error(ldc501):
    ldc501.ld_current_limit = 100
    ldc501.ld_current_setpoint = 25
    assert ldc501.ld_current_setpoint == 25


def test_ld_current_setpoint_out_range(ldc501):
    ldc501.ld_current_limit = 100
    with pytest.raises(Error):
        ldc501.ld_current_setpoint = 101


# --- tec current ---


def test_tec_current_setpoint_no_error(ldc501):
    ldc501.tec_current_limit = 1
    ldc501.tec_current_setpoint = 0.5
    assert ldc501.tec_current_setpoint == 0.5


def test_tec_current_setpoint_out_range(ldc501):
    ldc501.tec_current_limit = 1
    with pytest.raises(Error):
        ldc501.tec_current_setpoint = 1.1


# --- tec temperature ---


def test_tec_temperature_limits_no_error(ldc501):
    ldc501.tec_temperature_limits = (25, 75)
    assert ldc501.tec_temperature_limits == (25, 75)


def test_tec_temperature_low_limit_out_range(ldc501):
    with pytest.raises(Error):
        ldc501.tec_temperature_low_limit = -300


def test_tec_temperature_high_limit_out_range(ldc501):
    with pytest.raises(Error):
        ldc501.tec_temperature_high_limit = 300


def test_tec_temperature_setpoint_no_error(ldc501):
    ldc501.tec_temperature_limits = (25, 75)
    ldc501.tec_temperature_setpoint = 55
    assert ldc501.tec_temperature_setpoint == 55


def test_tec_temperature_setpoint_out_range(ldc501):
    ldc501.tec_temperature_limits = (25, 75)
    with pytest.raises(Error):
        ldc501.tec_temperature_setpoint = 100
