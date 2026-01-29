import pytest
from pint import Quantity as Q_
from time import sleep

# Importing driver classes
from scu_ascii import SmarActSCULinear


@pytest.fixture(scope="module")
def scu_ascii(connected_device_address):
    """ connected_device_address as "ASRL3::INSTR" """


    instr = SmarActSCULinear(connected_device_address)

    return instr


def test_sensor(scu_ascii):
    """Simple test to verify we can talk to the device."""
   # Here we check sensor presence as a handshake.
    assert scu_ascii.check_sensor_present() is True


def test_frequency_control(scu_ascii):
    """Test setting and reading back a property."""
    target_freq = Q_(500, 'Hz')
    scu_ascii.frequency_max = target_freq


    assert scu_ascii.frequency_max == target_freq



