#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import pytest
from pymeasure.units import ureg
import pyvisa

Q_ = ureg.Quantity

# Importing driver classes
from pymeasure.instruments.smaract.scu_ascii import SmarActSCULinear, SmarActSCUStepper


CHANNELS = ['0']
# Here you may add multiple channels ['0', '1', '2', ...]
SENSOR = [True]

# You can parameterize the following test"
# with @pytest.mark.parametrize for your number of channels:")


@pytest.fixture(scope="module")
def smaractascii(connected_device_address):
    """ An example of working device : connected_device_address as "ASRL3::INSTR" """
    """ to use the tests in this file invoke pytest as:
        pytest -k scu_ascii --device-address "ASRL3::INSTR" TCPIP::x.y.z.k::port::SOCKET
        where you replace x.y.z.k byt the device IP address and port by its port address
        """
    instr = SmarActSCULinear(adapter=connected_device_address)
    # ensure the device is in a defined state, e.g. by resetting it.
    yield instr
    instr.close()


@pytest.fixture(scope="module")
def smaractasciiSTEPPER(connected_device_address: str = "ASRL3::INSTR"):

    instz = SmarActSCUStepper(adapter=connected_device_address)
    yield instz
    instz.close()


class TestSCUIdentificate:

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
    def test_calibration(self, smaractascii, channel, issensor):
        status = smaractascii.channels[channel].calibrate_sensor()
        assert status == True

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_set_zero(self, smaractascii, channel):
        pos = smaractascii.channels[channel].position
        smaractascii.channels[channel].set_zero_position()
        assert smaractascii.channels[channel].set_zero_position() != pos


class TestSCUConfiguration:

    @pytest.mark.parametrize("value", [1, 3000, 18500])
    def test_check_freq_int_range(self, smaractascii, value):
        result = smaractascii.check_frequency(value)

        assert isinstance(result, Q_)
        assert result.magnitude == value
        assert str(result.units) == 'hertz'

    def test_check_freq_with_str(self, smaractascii):
        result = smaractascii.check_frequency('5000 Hz')
        assert result == Q_(5000, 'Hz')

    def test_frequency(self, smaractascii):
        smaractascii.frequency = Q_(500, "Hz")
        assert smaractascii.frequency == Q_(500, "Hz")

    @pytest.mark.parametrize("value", [150, 300, 1000])
    def test_check_amplitude_int_range(self, smaractascii, value):
        result = smaractascii.check_amplitude(value)

        assert isinstance(result, Q_)
        assert result.magnitude == value
        assert str(result.units) == 'decivolt'

    def test_check_amplitude_with_str(self, smaractascii):
        result = smaractascii.check_amplitude('300 dV')
        assert result == Q_(300, 'dV')

    def test_invalid_frequency(self, smaractascii):
        with pytest.raises(ValueError):
            smaractascii.frequency = Q_(20000, "Hz")

    def test_invalid_amplitude(self, smaractascii):
        with pytest.raises(ValueError):
            smaractascii.amplitude = Q_(50, "dV")


class TestSCUChannel:

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_safe_direction(self, smaractascii, channel):
        smaractascii.channels[channel].safe_direction = 'up'
        assert smaractascii.channels[channel].safe_direction == 'up'

        smaractascii.channels[channel].safe_direction = 'down'
        assert smaractascii.channels[channel].safe_direction == 'down'

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_frequency_max(self, smaractascii, channel):
        smaractascii.channels[channel].frequency_max = Q_(500, 'Hz')
        assert smaractascii.channels[channel].frequency_max == Q_(500, 'Hz')

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_read_status(self, smaractascii, channel):
        status = smaractascii.channels[channel].ask(f":M{channel}")
        assert status.startswith(f":M{channel}")

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_get_positioner_type(self, smaractascii, channel):
        t = smaractascii.channels[channel].positioner_type
        assert t.startswith(f":ST{channel}T")


class TestSCUMotion:

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_get_position(self, smaractascii, channel):
        pos = smaractascii.channels[channel].position

        # we verify we do receive a(Quantity)
        assert isinstance(pos, Q_)
        # we verify its unity is um
        assert str(pos.units) == 'micrometer'

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_to_ref(self, smaractascii, channel):
        smaractascii.channels[channel].move_to_ref()

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_abs(self, smaractascii, channel):
        target_pos = Q_(500, 'um')
        smaractascii.channels[channel].move_abs(target_pos)

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_rel(self, smaractascii, channel):
        target_pos = Q_(500, 'um')
        smaractascii.channels[channel].move_rel(target_pos)

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_steps_down(self, smaractascii, channel):
        smaractascii.channels[channel].move_steps_down(1000, 500, 500)

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_steps_up(self, smaractascii, channel):
        smaractascii.channels[channel].move_steps_up(1000, 500, 500)

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_up_to_end(self, smaractascii, channel):
        smaractascii.channels[channel].move_up_to_end()

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_down_to_end(self, smaractascii, channel):
        smaractascii.channels[channel].move_down_to_end()

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_stop(self, smaractascii, channel):
        smaractascii.channels[channel].stop()

# BAUDRATE TEST
    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("test_value, expected_outcome", [
        (9600, 9600),
        (1500, ValueError),
    ])
    def test_baudrate(self, smaractascii, test_value, expected_outcome, channel):
        if expected_outcome == ValueError:
            with pytest.raises(ValueError):
                smaractascii.set_baudrate(test_value)
        else:
            smaractascii.set_baudrate(test_value)

    def test_close(self, smaractascii):
        smaractascii.close()
        with pytest.raises(pyvisa.errors.InvalidSession):
            _ = smaractascii.serial_nb


class TestSCUStepperUnit:

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_initial_position(self, smaractasciiSTEPPER, channel):
        """Stepper position starts at instrument internal counter."""
        assert isinstance(smaractasciiSTEPPER.channels[channel].position_steps, int)

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_rel_positive(self, smaractasciiSTEPPER, channel):
        start = smaractasciiSTEPPER.channels[channel].position_steps
        smaractasciiSTEPPER.channels[channel].move_rel(100)
        assert smaractasciiSTEPPER.channels[channel].position_steps == start + 100

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_rel_negative(self, smaractasciiSTEPPER, channel):
        start = smaractasciiSTEPPER.channels[channel].position_steps
        smaractasciiSTEPPER.channels[channel].move_rel(-100)
        assert smaractasciiSTEPPER.channels[channel].position_steps == start - 100

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_move_abs(self, smaractasciiSTEPPER, channel):
        ch = smaractasciiSTEPPER.channels[channel]
        ch.move_rel(20)
        ch.move_abs(5)
        assert ch.position_steps == 5
