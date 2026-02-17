import pytest
from pint import Quantity as Q_
import time
import pyvisa

# Importing driver classes
from pymeasure.instruments.smaract.scu_ascii import SmarActSCULinear


CHANNELS = ['0']
SENSOR = [True]
TYPE = ['Linear']

"You can paremetrize the following test with @pytest.mark.parametrize and for your number of channels:"



@pytest.fixture(scope="module")
def smaractascii(serial_port="ASRL3::INSTR"):
    """ connected_device_address as "ASRL3::INSTR" """
    """ to use the tests in this file invoke pytest as:
        pytest -k scu_ascii --device-address TCPIP::x.y.z.k::port::SOCKET
        where you replace x.y.z.k byt the device IP address and port by its port address
        """
    instr = SmarActSCULinear(serial_port)
    return instr


def test_connection_and_id(smaractascii):
    """Verify we can talk to the controller."""
    idn = smaractascii.id
    print(f"\nConnected to: {idn}")
    assert idn is not None

@pytest.mark.parametrize("channel,issensor", zip(CHANNELS, SENSOR))
def test_sensor(smaractascii, channel, issensor):
    """Simple test to verify if it has a sensor."""
    assert smaractascii.channels[channel].check_sensor_present() is issensor


def test_frequency_control(smaractascii):
    """Test setting and reading back a property."""
    target_freq = Q_(500, 'Hz')
    smaractascii.channels.frequency_max = target_freq
    assert smaractascii.channel0.frequency_max == target_freq


def test_zero_and_move_absolute_sequence(smaractascii):
    """
    Integration test validating the absolute movement sequence:
    1. Go to ref.
    2. Verify the position is read as 0 um.
    3. Move absolute to 500 um.
    4. Verify the final position is 500 um.
    """
    smaractascii.channel0.move_to_ref()

    time.sleep(0.2)

    initial_pos = smaractascii.channel0.get_position()
    assert initial_pos == pytest.approx(0.0, abs=0.1), \
        f"Expected 0 um after zeroing, got {initial_pos}"
    target_pos = Q_(500, 'um')
    smaractascii.channel0.move_abs(target_pos)
    time.sleep(2.0)

    final_pos = smaractascii.channel0.get_position()
    assert final_pos== pytest.approx(500.0, abs=1.0), \
        f"Expected 500 um, got {final_pos}"

def test_zero_and_move_rel_sequence(smaractascii):
        """
        Integration test validating the movement sequence:
        0. Get to ref.
        1. Verify the position is read as 0 um.
        2. Move rel to 500 .
        3. Verify the final position is 500 um.
        """
        smaractascii.channel0.move_to_ref()

        time.sleep(1)

        initial_pos = smaractascii.channel0.get_position()
        assert initial_pos== pytest.approx(0.0, abs=0.5), \
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

def test_stop_function(self, smaractascii):
    """Test the Emergency Stop functionality."""
    ch = smaractascii.channel0

    # 1. Go to 0
    ch.move_to_ref()
    time.sleep(1.0)

    # 2. Set slow speed to give us time to stop
    ch.frequency_max = Q_(50, 'Hz')

        # 3. Order a long move (5000 um)
    ch.move_abs(Q_(5000, 'um'))

    # 4. Wait briefly then STOP
    time.sleep(0.5)
    ch.stop()

    time.sleep(1.0)

    # 5. Verify we did NOT reach 5000
    final_pos = ch.get_position()
    print(f"Stopped at {final_pos}")
    assert final_pos.magnitude < 4000.0

    # Cleanup: Restore speed
    ch.frequency_max = Q_(1000, 'Hz')

#pytest test_scu_ascii_with_device.py --device-address "ASRL3::INSTR" -s


