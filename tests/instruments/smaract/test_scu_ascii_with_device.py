import pytest
from pint import Quantity as Q_
from time import sleep

# Importing driver classes
from pymeasure.instruments.smaract.scu_ascii import SmarActSCU_USB, SmarActSCULinear


@pytest.fixture(scope="module")
def SmarActSCU_USB(connected_device_address):
    """ connected_device_address as "ASRL3::INSTR" """

    instr = SmarActSCU_USB(connected_device_address)

    return instr


def test_sensor(SmarActSCU_USB):
    """Simple test to verify we can talk to the device."""
   # Here we check sensor presence as a handshake.
    assert scu_ascii.check_sensor_present() is True


def test_frequency_control(SmarActSCU_USB):
    """Test setting and reading back a property."""
    target_freq = Q_(500, 'Hz')
    scu_ascii.frequency_max = target_freq
    Scu


    assert scu_ascii.frequency_max == target_freq