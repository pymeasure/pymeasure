import pytest

from pymeasure.errors import Error
from pymeasure.instruments.srs import LDC500Series


class TestLDC501:

    ##################################
    # LDC501 device address goes here:
    RESOURCE = "GPIB0::12::INSTR"
    ##################################

    INSTR = LDC500Series(RESOURCE)

    INSTR.reset()
    INSTR.check_errors()
    INSTR.ld_current_range = "LOW"

    @pytest.fixture
    def instr(self):
        return self.INSTR

    # --- ld current ---

    def test_ld_current_limit_no_error(self, instr):
        instr.ld_current_limit = 100
        assert instr.ld_current_limit == 100

    def test_ld_current_limit_out_range(self, instr):
        with pytest.raises(Error):
            instr.ld_current_limit = 300

    def test_ld_current_setpoint_no_error(self, instr):
        instr.ld_current_limit = 100
        instr.ld_current_setpoint = 25
        assert instr.ld_current_setpoint == 25

    def test_ld_current_setpoint_out_range(self, instr):
        instr.ld_current_limit = 100
        with pytest.raises(Error):
            instr.ld_current_setpoint = 101

    # --- tec current ---

    def test_tec_current_setpoint_no_error(self, instr):
        instr.tec_current_limit = 1
        instr.tec_current_setpoint = 0.5
        assert instr.tec_current_setpoint == 0.5

    def test_tec_current_setpoint_out_range(self, instr):
        instr.tec_current_limit = 1
        with pytest.raises(Error):
            instr.tec_current_setpoint = 1.1

    # --- tec temperature ---

    def test_tec_temperature_limits_no_error(self, instr):
        instr.tec_temperature_limits = (25, 75)
        assert instr.tec_temperature_limits == (25, 75)

    def test_tec_temperature_low_limit_out_range(self, instr):
        with pytest.raises(Error):
            instr.tec_temperature_low_limit = -300

    def test_tec_temperature_high_limit_out_range(self, instr):
        with pytest.raises(Error):
            instr.tec_temperature_high_limit = 300

    def test_tec_temperature_setpoint_no_error(self, instr):
        instr.tec_temperature_limits = (25, 75)
        instr.tec_temperature_setpoint = 55
        assert instr.tec_temperature_setpoint == 55

    def test_tec_temperature_setpoint_out_range(self, instr):
        instr.tec_temperature_limits = (25, 75)
        with pytest.raises(Error):
            instr.tec_temperature_setpoint = 100
