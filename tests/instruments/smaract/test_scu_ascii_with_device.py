import pytest
from pint import Quantity as Q_
import time
import pyvisa
from six import integer_types

# Importing driver classes
from pymeasure.instruments.smaract.scu_ascii import SmarActSCULinear


CHANNELS = ['0']
SENSOR = [True]
#TYPE = ['Linear'] hesitating on adding this function, since it may not be as simple as imagined, and can be easily done by SENSOR


"You can paremetrize the following test with @pytest.mark.parametrize and for your number of channels:"

@pytest.fixture(scope="module")
def smaractascii(connected_device_address: str = "ASRL3::INSTR"):
    """ connected_device_address as "ASRL3::INSTR" """
    """ to use the tests in this file invoke pytest as:
        pytest -k scu_ascii --device-address "ASRL3::INSTR" TCPIP::x.y.z.k::port::SOCKET
        where you replace x.y.z.k byt the device IP address and port by its port address
        """
    instr = SmarActSCULinear(adapter=connected_device_address)
    # ensure the device is in a defined state, e.g. by resetting it.
    return instr



@pytest.mark.parametrize("channel,issensor", zip(CHANNELS, SENSOR))
def test_sensor(smaractascii, channel, issensor):
    """Simple test to verify if it has a sensor."""
    assert smaractascii.channels[channel].check_sensor_present() is issensor

@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("test_value, expected_outcome", [
    (9600, 9600),
    (1500, pyvisa.VisaIOError),
])
def test_baudrate(smaractascii, test_value, expected_outcome, channel):
    ch = smaractascii.channels[channel]
    if expected_outcome == pyvisa.VisaIOError:
        with pytest.raises(pyvisa.VisaIOError):
            ch.baudrate = test_value
    else:
        ch.baudrate = test_value
        assert ch.baudrate == expected_outcome

@pytest.mark.parametrize("property_name, test_value, expected_outcome, channel", [
    # --- FREQUENCY TESTS (Limits: > 1 Hz and < frequency_max)
    ("frequency", Q_(500, 'Hz'), Q_(500, 'Hz'),CHANNELS),  # Valid
    ("frequency", Q_(0.5, 'Hz'), ValueError,CHANNELS),  # Invalid: Too low
    ("frequency", Q_(20000, 'Hz'), ValueError,CHANNELS),  # Invalid: Too high

    # --- AMPLITUDE TESTS (Limits: 150 to 1000 dV)
    ("amplitude", Q_(500, 'dV'), Q_(500, 'dV'),CHANNELS),  # Valid
    ("amplitude", Q_(100, 'dV'), ValueError,CHANNELS),  # Invalid: Too low
    ("amplitude", Q_(1500, 'dV'), ValueError,CHANNELS),  # Invalid: Too high
])
def test_instrument_properties(smaractascii, property_name, test_value, expected_outcome,channel):
    """
    Parametrized test for the Instrument properties.

    """
    # We expect a ValueError (Negative Testing)
    if expected_outcome == ValueError:
        with pytest.raises(ValueError):
            if property_name == "frequency":
                smaractascii.channels[channel].frequency = test_value
            elif property_name == "amplitude":
                smaractascii.channels[channel].amplitude = test_value

    # We expect it to succeed (values in boundries)
    else:
        if property_name == "frequency":
            smaractascii.channels[channel].frequency = test_value
            assert smaractascii.channels[channel].frequency == expected_outcome

        elif property_name == "amplitude":
            smaractascii.channels[channel].amplitude = test_value
            assert smaractascii.channels[channel].amplitude == expected_outcome


@pytest.mark.parametrize("test_steps, expected_outcome", [
    (1000, 1000),  # Valid: Normal steps
    (0, ValueError),  # Invalid: Too low
    (40000, ValueError),  # Invalid: Too high
])
def test_check_steps_method(smaract, test_steps, expected_outcome):
    """
    Parametrized test specifically for the check_steps method.
    """

    #  We expect an error
    if expected_outcome == ValueError:
        with pytest.raises(ValueError):
            smaract.check_steps(test_steps)

    #  We expect a valid return value
    else:
        result = smaract.check_steps(test_steps)
        assert result == expected_outcome

@pytest.mark.parametrize("channel", CHANNELS)
def test_ref_and_move_absolute_sequence(smaractascii,channel):
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
@pytest.mark.parametrize("channel", CHANNELS)
def test_zero_and_move_rel_sequence(smaractascii,channel):
        """
        Integration test validating the movement sequence:
        0. Get to ref.
        1. Verify the position is read as 0 um.
        2. Move rel to 500 .
        3. Verify the final position is 500 um.
        """
        smaractascii.channels[channel].move_to_ref()

        time.sleep(1)

        initial_pos = smaractascii.channels[channel].get_position()
        assert initial_pos== pytest.approx(0.0, abs=0.5), \
            f"Expected 0 um after zeroing, got {initial_pos}"
        target_pos = Q_(500, 'um')
        smaractascii.channels[channel].move_rel(target_pos)

        time.sleep(2.0)

        final_pos = smaractascii.channels[channel].get_position()
        assert final_pos== pytest.approx(500.0, abs=1.0), \
            f"Expected 500 um, got {final_pos}"

@pytest.mark.parametrize("channel", CHANNELS)
def test_move_step_sequence(smaractascii,channel):
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
    smaractascii.channels[channel].move_steps_up(steps_to_move,steps=steps_to_move, frequency=freq, amplitude=amp)
    time.sleep(2.0)
    smaractascii.channels[channel].move_steps_down(steps_to_move)


    time.sleep(2.0)

    final_pos = smaractascii.get_position()
    assert final_pos == pytest.approx(0.0, abs=1.0), \
        f"Expected 0 um, got {final_pos}"

def test_stop_function(smaractascii):
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



    # 5. Verify we did NOT reach 5000
    final_pos = ch.get_position()
    print(f"Stopped at {final_pos}")
    assert final_pos.magnitude < 4000.0

    # Cleanup: Restore speed
    ch.frequency_max = Q_(1000, 'Hz')

@pytest.mark.parametrize("channel", CHANNELS)
def test_move_to_end(smaractascii,channel):
    smaractascii.channels[channel].move_to_end_up()
    status = self.ask(f":M{channel}")
    while status==f"M{channel}T" :
        time.sleep(1.0)
        status = self.ask(f":M{channel}")



    smaractascii.channels[channel].move_to_end_down()

#pytest test_scu_ascii_with_device.py --device-address "ASRL3::INSTR" -s


