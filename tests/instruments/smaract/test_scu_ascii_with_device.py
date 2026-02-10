import pytest
from pint import Quantity as Q_
import time

# Importing driver classes
from pymeasure.instruments.smaract.scu_ascii import SmarActSCULinear


@pytest.fixture(scope="module")
def smaractascii(connected_device_address):
    """ connected_device_address as "ASRL3::INSTR" """

    instr = SmarActSCULinear(connected_device_address)

    return instr

def test_sensor(smaractascii):
    """Simple test to verify if it has a sensor."""
    assert smaractascii.check_sensor_present() is True


def test_frequency_control(smaractascii):
    """Test setting and reading back a property."""
    target_freq = Q_(500, 'Hz')
    smaractascii.frequency_max = target_freq
    assert smaractascii.frequency_max == target_freq


def test_zero_and_move_absolute_sequence(smaractascii):
    """
    Integration test validating the absolute movement sequence:
    1. Go to ref.
    2. Verify the position is read as 0 um.
    3. Move absolute to 500 um.
    4. Verify the final position is 500 um.
    """
    smaractascii.move_to_ref()

    time.sleep(0.2)

    initial_pos = smaractascii.get_position()
    assert initial_pos == pytest.approx(0.0, abs=0.1), \
        f"Expected 0 um after zeroing, got {initial_pos}"
    target_pos = Q_(500, 'um')
    smaractascii.move_abs(target_pos)
    time.sleep(2.0)

    final_pos = smaractascii.get_position()
    assert final_pos== pytest.approx(500.0, abs=1.0), \
        f"Expected 500 um, got {final_pos}"

def test_zero_and_move_rel_sequence(smaractascii):
        """
        Integration test validating the movement sequence:
        0. Get to autozero.
        1. Verify the position is read as 0 um.
        2. Move rel to 500 .
        3. Verify the final position is 500 um.
        """
        smaractascii.move_to_ref()

        time.sleep(1)

        initial_pos = smaractascii.get_position()
        assert initial_pos== pytest.approx(0.0, abs=0.1), \
            f"Expected 0 um after zeroing, got {initial_pos}"
        target_pos = Q_(500, 'um')
        smaractascii.move_rel(target_pos)

        time.sleep(2.0)

        final_pos = smaractascii.get_position()
        assert final_pos== pytest.approx(500.0, abs=1.0), \
            f"Expected 500 um, got {final_pos}"

def test_move_step_sequence(smaractascii):
    """
    Integration test validating the movement sequence:
    0.Reset to Reference to ensure safe range of motion
    1. Set the current position as zero (reference).
    2. Verify the position is read as 0 um.
    3. Move absolute to 500 um.
    4. Verify the final position is 500 um.
    """
    smaractascii.move_to_ref()
    time.sleep(2.0)

    initial_pos=smaractascii.get_position()
    assert initial_pos.magnitude == pytest.approx(0.0, abs=1.0), \
        f"Expected 0 um after zeroing, got {initial_pos}"

    # 2. Define Step Parameters locally
    steps_to_move = 1000
    freq = Q_(1000, 'Hz')
    amp = Q_(1000, 'dV')  # Max amplitude
    smaractascii.set_steps_parameters(steps=steps_to_move, frequency=freq, amplitude=amp)
    smaractascii.move_steps_up(steps_to_move)
    time.sleep(2.0)
    smaractascii.move_steps_down(steps_to_move)


    time.sleep(2.0)

    final_pos = smaractascii.get_position()
    assert final_pos == pytest.approx(0.0, abs=1.0), \
        f"Expected 0 um, got {final_pos}"

#pytest test_scu_ascii_with_device.py --device-address "ASRL3::INSTR" -s

