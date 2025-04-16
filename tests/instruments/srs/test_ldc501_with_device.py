import pytest

from pymeasure.instruments.srs import LDC500Series


class TestLDC501:
    
    ##################################
    # LDC501 device address goes here:
    RESOURCE = "GPIB0::12::INSTR"
    ##################################
    
    INSTR = LDC500Series(RESOURCE)
    
    INSTR.ld_current_range = "LOW"
    
    @pytest.fixture
    def instr(self):
        return self.INSTR
    
    def test_ld_current_setpoint_no_error(self, instr):
        instr.ld_current_setpoint = 100
        assert abs(instr.ld_current_setpoint - 100) < 1e-3
        
    
    def test_ld_current_setpoint_out_range(self, instr):
        with pytest.raises(Exception):
            instr.ld_current_setpoint = 300