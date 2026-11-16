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

import datetime

import pytest

from pymeasure.instruments.redpitaya import RedPitayaScpi


@pytest.fixture(scope="module")
def redpitaya_scpi(connected_device_address: str):
    """ to use the tests in this file invoke pytest as:
    pytest -k redpitaya_scpi --device-address TCPIP::x.y.z.k::port::SOCKET
    where you replace x.y.z.k byt the device IP address and port by its port address
    """
    instr = RedPitayaScpi(adapter=connected_device_address)
    # ensure the device is in a defined state, e.g. by resetting it.
    instr.digital_reset()
    instr.analog_reset()
    return instr


class TestRedpitaya:

    def test_time_date(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.time = datetime.time(13, 7, 20)
        assert inst.time.hour == 13
        assert inst.time.minute == 7

        inst.date = datetime.date(2023, 12, 22)
        assert inst.date == datetime.date(2023, 12, 22)

    def test_led_dio(self, redpitaya_scpi):
        inst = redpitaya_scpi

        for ind in range(8):
            inst.led[ind].enabled = True
            assert inst.led[ind].enabled

            inst.led[ind].enabled = False
            assert not inst.led[ind].enabled

        for ind in range(7):
            inst.dioN[ind].direction_in = True
            assert inst.dioN[ind].direction_in
            inst.dioN[ind].direction_in = False
            assert not inst.dioN[ind].direction_in

            inst.dioN[ind].enabled = True
            assert inst.dioN[ind].enabled

            inst.dioN[ind].enabled = False
            assert not inst.dioN[ind].enabled

        for ind in range(7):
            inst.dioP[ind].direction_in = True
            assert inst.dioP[ind].direction_in
            inst.dioP[ind].direction_in = False
            assert not inst.dioP[ind].direction_in

            inst.dioP[ind].enabled = True
            assert inst.dioP[ind].enabled

            inst.dioP[ind].enabled = False
            assert not inst.dioP[ind].enabled

    def test_analog_slow(self, redpitaya_scpi):
        inst = redpitaya_scpi

        for ind in range(4):
            _ = inst.analog_in_slow[ind].voltage
            inst.analog_out_slow[ind].voltage = 0.5

    def test_decimation(self, redpitaya_scpi):
        inst = redpitaya_scpi

        for ind in range(17):
            inst.decimation = 2**ind
            assert inst.decimation == 2**ind

    def test_average_skipped_samples(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.average_skipped_samples = False
        assert inst.average_skipped_samples is False
        inst.average_skipped_samples = True
        assert inst.average_skipped_samples

    def test_average_acq_units(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.acq_units = 'RAW'
        assert inst.acq_units == 'RAW'

    def test_buffer_length(self, redpitaya_scpi):
        inst = redpitaya_scpi
        assert inst.buffer_length == 16384

    def test_trigger_source(self, redpitaya_scpi):
        inst = redpitaya_scpi
        for trigger_source in inst.TRIGGER_SOURCES:
            inst.acq_trigger_source = trigger_source
            if trigger_source == "NOW":
                assert inst.acq_trigger_status

    def test_buffer_filled(self, redpitaya_scpi):
        inst = redpitaya_scpi
        assert inst.acq_buffer_filled is False

    def test_acq_trigger_delay(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.acq_trigger_delay_samples = 0
        assert inst.acq_trigger_delay_samples == 0
        assert inst.acq_trigger_delay_ns == 0

    def test_acq_trigger_delay_non_zero(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.acq_trigger_delay_samples = 500
        assert inst.acq_trigger_delay_samples == 500
        assert inst.acq_trigger_delay_ns == int(500 / inst.CLOCK * 1e9)

        inst.acq_trigger_delay_ns = RedPitayaScpi.DELAY_NS[10]
        assert inst.acq_trigger_delay_ns == RedPitayaScpi.DELAY_NS[10]
        assert inst.acq_trigger_delay_samples == -8192 + 10

    def test_acq_trig_level(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.acq_trigger_level = 0.5
        assert inst.acq_trigger_level == pytest.approx(0.5)

    def test_gain(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.ain1.gain = 'LV'
        assert inst.ain1.gain == 'LV'

    def test_ascii_get_data(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.acq_format = 'ASCII'
        inst.ain1.get_data(1,)

    def test_ao_shape(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.aout1.shape = 'SQUARE'
        assert inst.aout1.shape == 'SQUARE'

    def test_ao_freq(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.aout1.frequency = 1e4
        assert inst.aout1.frequency == 1e4

    def test_ao_amp(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.aout1.amplitude = 0.05
        assert inst.aout1.amplitude == 0.05

    def test_ao_offset(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.aout1.offset = 0.1
        assert inst.aout1.offset == 0.1

    def test_ao_phase(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.aout1.phase = 45
        assert inst.aout1.phase == 45

    def test_ao_duty(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.aout1.dutycycle = 0.3
        assert inst.aout1.dutycycle == 0.3

    def test_ao_gen_trig_source(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.aout1.gen_trigger_source = 'INT'
        assert inst.aout1.gen_trigger_source == 'INT'

    def test_ao_enabled(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.aout1.enable = True
        assert inst.aout1.enable

    def test_ao_sweep_mode(self, redpitaya_scpi):
        inst = redpitaya_scpi
        # Sweep Mode
        inst.aout1.sweep_mode = 'LOG'
        assert inst.aout1.sweep_mode == 'LOG'

    def test_ao_sweep_start(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.aout1.sweep_start_frequency = 1e3
        assert inst.aout1.sweep_start_frequency == 1e3

    def test_ao_sweep_stop(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.aout1.sweep_stop_frequency = 1e5
        assert inst.aout1.sweep_stop_frequency == 1e5

    def test_ao_sweep_time(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.aout1.sweep_time = 5e5
        assert inst.aout1.sweep_time == 5e5

    def test_ao_sweep_state(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.aout1.sweep_state = False
        assert inst.aout1.sweep_state is False

    def test_ao_sweep_direction(self, redpitaya_scpi):
        inst = redpitaya_scpi
        inst.aout1.sweep_direction = 'NORMAL'
        assert inst.aout1.sweep_direction == 'NORMAL'

        # #Burst Mode not working
        # inst.aout1.burst_mode = 'CONTINUOUS'
        # assert inst.aout1.burst_mode == 'CONTINUOUS'
        #
        # inst.aout1.burst_initial_voltage = 0.5
        # assert inst.aout1.burst_initial_voltage == 0.5
        #
        # inst.aout1.burst_last_voltage = 0.7
        # assert inst.aout1.burst_last_voltage == 0.7
        #
        # inst.aout1.burst_num_cycles = 2
        # assert inst.aout1.burst_num_cycles == 2
        #
        # inst.aout1.burst_num_repetitions = 4
        # assert inst.aout1.burst_num_repetitions == 4
        #
        # inst.aout1.burst_period = 1e5
        # assert inst.aout1.burst_period == 1e5
