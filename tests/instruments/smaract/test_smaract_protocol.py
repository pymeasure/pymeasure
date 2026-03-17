from pymeasure.generator import Generator
from pymeasure.instruments.smaract.scu_ascii import SmarActSCULinear
import pytest
from pint import Quantity as Q_
import time
import pyvisa
generator = Generator()
adapter_string = 'ASRL3::INSTR'
smaractascii= generator.instantiate(
    SmarActSCULinear,
    adapter_string,
    'SCUController',
    adapter_kwargs={'read_termination': '\n', 'write_termination': '\n'}
)

""" Test properties (Setter then Getter)"""
CHANNELS = ['0']
SENSOR = [True]
#TYPE = ['Linear'] hesitating on adding this function, since it may not be as simple as imagined, and can be easily done by SENSOR


"You can paremetrize the following test with @pytest.mark.parametrize and for your number of channels:"




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
    if expected_outcome == pyvisa.VisaIOError:
        with pytest.raises(pyvisa.VisaIOError):
            smaractascii.set_baudrate(test_value)
    else:
        smaractascii.set_baudrate(test_value)


""" This tests the frequency and amplitude values for a given instrument, assuming that the frequency 
    and amplitude will be similar on multiple channels if there exist more than one channel"""

@pytest.mark.parametrize("property_name, test_value, expected_outcome", [
    # --- FREQUENCY TESTS
    ("frequency", Q_(500, 'Hz'), Q_(500, 'Hz')),  # Valid
    ("frequency", Q_(0.5, 'Hz'), ValueError),  # Invalid: Too low
    ("frequency", Q_(20000, 'Hz'), ValueError),  # Invalid: Too high

    # --- AMPLITUDE TESTS
    ("amplitude", Q_(500, 'dV'), Q_(500, 'dV')),  # Valid
    ("amplitude", Q_(100, 'dV'), ValueError),  # Invalid: Too low
    ("amplitude", Q_(1300, 'dV'), ValueError),  # Invalid: Too high
])
def test_instrument_properties(smaractascii, property_name, test_value, expected_outcome):
    # We expect a ValueError (Negative Testing)
    if expected_outcome == ValueError:
        with pytest.raises(ValueError):
            if property_name == "frequency":
                smaractascii.frequency = test_value
            elif property_name == "amplitude":
                smaractascii.amplitude = test_value

    # We expect it to succeed
    else:
        if property_name == "frequency":
            smaractascii.frequency = test_value
            assert smaractascii.frequency == expected_outcome
        elif property_name == "amplitude":
            smaractascii.amplitude = test_value
            assert smaractascii.amplitude == expected_outcome

@pytest.mark.parametrize("test_steps, expected_outcome", [
    (1000, 1000),  # Valid: Normal steps
    (0, ValueError),  # Invalid: Too low
    (40000, ValueError),  # Invalid: Too high
])
def test_check_steps_method(smaractascii, test_steps, expected_outcome):
    """
    Parametrized test specifically for the check_steps method.
    """

    #  We expect an error
    if expected_outcome == ValueError:
        with pytest.raises(ValueError):
            smaractascii.check_steps(test_steps)

    #  We expect a valid return value
    else:
        result = smaractascii.check_steps(test_steps)
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
    smaractascii.channels[channel].move_to_ref()
    status = smaractascii.ask(f":M{channel}")
    while status == f":M{channel}R":
        time.sleep(1.0)
        status = smaractascii.ask(f":M{channel}")
    initial_pos = smaractascii.channel0.get_position()
    assert initial_pos.magnitude == pytest.approx(0.0, abs=5), \
        f"Expected 0 um after zeroing, got {initial_pos}"
    target_pos = Q_(500, 'um')
    smaractascii.channel0.move_abs(target_pos)
    status = smaractascii.ask(f":M{channel}")
    while status == f":M{channel}T":
        time.sleep(1.0)
        status = smaractascii.ask(f":M{channel}")

    final_pos = smaractascii.channel0.get_position()
    assert final_pos.magnitude== pytest.approx(500.0, abs=2), \
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
        status = smaractascii.ask(f":M{channel}")
        while status == f":M{channel}R":
            time.sleep(1.0)
            status = smaractascii.ask(f":M{channel}")
        initial_pos = smaractascii.channels[channel].get_position()
        assert initial_pos.magnitude == pytest.approx(0.0, abs=0.5), \
            f"Expected 0 um after zeroing, got {initial_pos}"
        target_pos = Q_(500, 'um')
        smaractascii.channels[channel].move_rel(target_pos)
        status = smaractascii.ask(f":M{channel}")
        while status == f":M{channel}T":
            time.sleep(1.0)
            status = smaractascii.ask(f":M{channel}")
        final_pos = smaractascii.channels[channel].get_position()
        assert final_pos.magnitude== pytest.approx(500.0, abs=1.0), \
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

    IMPORTANT : The hardware of the SmarAct SCU will be limiting the
                precision of the movement sequence with steps. The main
                factor that will play a role is the amplitude (dV), which
                above ~200dV will not be as precise (above 2µm of imprecision)

    """
    smaractascii.channels[channel].move_to_ref()
    status = smaractascii.ask(f":M{channel}")
    while status == f":M{channel}R":
        time.sleep(1.0)
        status = smaractascii.ask(f":M{channel}")

    initial_pos=smaractascii.channels[channel].get_position()
    assert initial_pos.magnitude == pytest.approx(0.0, abs=1.0), \
        f"Expected 0 um after zeroing, got {initial_pos}"

    # 2. Define Step Parameters locally
    steps_to_move = 100
    freq = Q_(1000, 'Hz')
    amp = Q_(200, 'dV')  # Max amplitude
    smaractascii.channels[channel].move_steps_up(steps_to_move, freq, amp)
    time.sleep(2.0)
    smaractascii.channels[channel].move_steps_down(steps_to_move,freq, amp)

    time.sleep(2.0)

    final_pos = smaractascii.channels[channel].get_position()
    assert final_pos.magnitude == pytest.approx(0.0, abs=2.0), \
        f"Expected 0 um, got {final_pos}"

"""DANGEROUS ELEMENT WHICH IS UNSTABLE AND MAY CAUSE HARM TO THE INSTRUMENT"""
@pytest.mark.parametrize("channel", CHANNELS)
def test_stop_function(smaractascii, channel):
    """Test the Emergency Stop functionality."""
     # 1. Go to 0
    smaractascii.channels[channel].move_to_ref()
    time.sleep(1.0)

     # 2. Set slow speed to give us time to stop
    smaractascii.channels[channel].frequency_max = Q_(500, 'Hz')

         # 3. Order a long move (5000 um)
    smaractascii.channels[channel].move_abs(Q_(5000, 'um'))

     # 4. Wait briefly then STOP
    time.sleep(1)
    smaractascii.channels[channel].stop()

    final_pos = smaractascii.channels[channel].get_position()
    print(f"Stopped at {final_pos}")
    assert final_pos.magnitude < 4000.0

     # Cleanup: Restore speed
    smaractascii.channels[channel].frequency_max = Q_(1000, 'Hz')

@pytest.mark.parametrize("channel", CHANNELS)
def test_move_to_end(smaractascii,channel):
    smaractascii.channels[channel].move_to_end_up()
    status = smaractascii.ask(f":M{channel}")
    while status==f"M{channel}T" :
        time.sleep(1.0)
        status = smaractascii.ask(f":M{channel}")

    smaractascii.channels[channel].move_to_end_down()

#pytest test_scu_ascii_with_device.py --device-address "ASRL3::INSTR" -s




# This creates the file with all the expected_protocol tests.
generator.write_file("generated_test_smaract.py")
print("Done! Open 'generated_test_smaract.py' to see the magic.")