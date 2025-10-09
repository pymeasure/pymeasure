import pytest

from pymeasure.instruments.agilent import AgilentB1500
from pymeasure.instruments.agilent.agilentB1500 import ControlMode, PgSelectorConnectionStatus, PgSelectorPort
from pymeasure.test import expected_protocol


class TestB1500:
    """Tests for B1500 functionality."""

    def test_restore_settings(self):
        """Test restore settings method."""
        with expected_protocol(
            AgilentB1500,
            [("RZ", None)],
        ) as inst:
            inst.restore_settings()


    @pytest.mark.parametrize("control_mode", list(ControlMode))
    def test_control_mode(self, control_mode):
        """Test control mode property."""
        with expected_protocol(
            AgilentB1500,
            [(f"ERMOD {control_mode.value}", None),
            ("ERMOD?", control_mode.value)],
        ) as inst:
            inst.control_mode = control_mode
            assert inst.control_mode == control_mode


    @pytest.mark.parametrize("port", list(PgSelectorPort))
    @pytest.mark.parametrize("status", list(PgSelectorConnectionStatus))
    def test_set_port_connection(self, port, status):
        """Test set_port_connection method."""
        with expected_protocol(
            AgilentB1500,
            [(f"ERSSP {port.value}, {status.value}", None)],
        ) as inst:
            inst.set_port_connection(port, status)