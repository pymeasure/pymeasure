import pytest
from pint import Quantity as Q_
import time
import pyvisa
#from six import integer_types

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

class TestSCUIdentifCalibrate:

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_model(self, smaractascii, channel):
        model = smaractascii.model
        assert isinstance(model, str)
        assert len(model) > 0

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_serial_number(self, smaractascii, channel):
        serial = smaractascii.serial_nb
        assert isinstance(serial, str)
        assert len(serial) > 0

    @pytest.mark.parametrize("channel,issensor", zip(CHANNELS, SENSOR))
    def test_sensor(self, smaractascii, channel, issensor):
        assert smaractascii.channels[channel].check_sensor_present() is issensor

    @pytest.mark.parametrize("channel,issensor", zip(CHANNELS, SENSOR))
    def test_calibration(self,smaractascii,channel,issensor):
        status = smaractascii.channels[channel].calibrate_sensor()
        assert status == ':M0C'

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_set_zero(self,smaractascii, channel):
        pos = smaractascii.channels[channel].get_position()
        smaractascii.channels[channel].set_zero_pos()
        assert smaractascii.channels[channel].set_zero_pos() != pos

class TestSCUConfiguration:

    def test_frequency(self, smaractascii):
        smaractascii.frequency = Q_(500, "Hz")
        assert smaractascii.frequency == Q_(500, "Hz")

    def test_amplitude(self, smaractascii):
        smaractascii.amplitude = Q_(300, "dV")
        assert smaractascii.amplitude == Q_(300, "dV")

    def test_invalid_frequency(self, smaractascii):
        with pytest.raises(ValueError):
            smaractascii.frequency = Q_(20000, "Hz")

    def test_invalid_amplitude(self, smaractascii):
        with pytest.raises(ValueError):
            smaractascii.amplitude = Q_(50, "dV")


class TestSCUChannel:

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_safe_direction(self, smaractascii,channel):
        smaractascii.channels[channel].safe_direction = 'up'
        assert smaractascii.channels[channel].safe_direction == 'up'

        smaractascii.channels[channel].safe_direction = 'down'
        assert smaractascii.channels[channel].safe_direction == 'down'


    @pytest.mark.parametrize("channel", CHANNELS)
    def test_frequency_max(self, smaractascii, channel):
        smaractascii.channels[channel].max_frequency = Q_(500, 'Hz')
        assert smaractascii.channels[channel].max_frequency == Q_(500, 'Hz')

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_read_status(self,smaractascii, channel):
        status = smaractascii.channels[channel].ask(f":M{channel}")
        assert status.startswith(f":M{channel}")

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_get_positioner_type(self, smaractascii,channel):
        t = smaractascii.channels[channel].get_positioner_type()
        assert t.startswith(f":ST{channel}T")

class TestSCUMotion:

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_get_position(self, smaractascii, channel):
        pos = smaractascii.channels[channel].get_position()

        # we verify we do recive a(Quantity)
        assert isinstance(pos, Q_)
        # we verify its unity is um
        assert str(pos.units) == 'micrometer'

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_to_ref(self,smaractascii, channel):
        smaractascii.channels[channel].move_to_ref()

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_abs(self,smaractascii, channel):
        target_pos = Q_(500, 'um')
        smaractascii.channels[channel].move_abs(target_pos)

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_rel(slef,smaractascii, channel):
        target_pos = Q_(500, 'um')
        smaractascii.channels[channel].move_rel(target_pos)

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_steps_down(self,smaractascii, channel):
        smaractascii.channels[channel].move_steps_down(1000, 500, 500)

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_steps_up(self,smaractascii, channel):
        smaractascii.channels[channel].move_steps_up(1000, 500, 500)

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_to_end_up(self,smaractascii, channel):
        smaractascii.channels[channel].move_to_end_up()

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_to_end_down(self,smaractascii, channel):
        smaractascii.channels[channel].move_to_end_down()

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_stop(self,smaractascii, channel):
        smaractascii.channels[channel].stop()

###BAUDRATE TEST###
    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("test_value, expected_outcome", [
        (9600, 9600),
        (1500, pyvisa.VisaIOError),
    ])
    def test_baudrate(self, smaractascii, test_value, expected_outcome, channel):
        if expected_outcome == pyvisa.VisaIOError:
            with pytest.raises(pyvisa.VisaIOError):
                smaractascii.set_baudrate(test_value)
        else:
            smaractascii.set_baudrate(test_value)




