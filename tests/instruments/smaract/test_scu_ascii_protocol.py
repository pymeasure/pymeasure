import pytest
import pyvisa

from pymeasure.test import expected_protocol
from pymeasure.instruments.smaract.scu_ascii import SmarActSCULinear
from pint import Quantity as Q_


CHANNELS = ['0']


def test_init():
    with expected_protocol(
            SmarActSCULinear,
            [],
    ):
        pass  # verify the expected communication.


def test_close():
    with expected_protocol(
            SmarActSCULinear,
            [],  # no communication expected
    ) as inst:
        inst.close()


@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_frequency_max_setter(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':SCLF{channel}F500'.encode(), None)],
    ) as inst:
        inst.channels[channel].frequency_max = Q_(500, 'Hz')


@pytest.mark.parametrize("channel", CHANNELS)
def test_frequency_max_getter(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':GCLF{channel}'.encode(), b':CLF0F500')],
    ) as inst:
        assert inst.channels[channel].frequency_max.magnitude == 500


def test_amplitude_setter():
    inst = SmarActSCULinear(adapter=None)
    inst.amplitude = Q_(300, 'dV')
    assert inst.amplitude == Q_(300, 'dV')


def test_frequency_setter():
    inst = SmarActSCULinear(adapter=None)
    inst.frequency = Q_(500, 'Hz')
    assert inst.frequency == Q_(500, 'Hz')


@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_set_zero(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':SZ{channel}'.encode(), None)],
    ) as inst:
        # must mock sensor present → otherwise NotImplementedError
        inst.channels[channel].check_sensor_present = lambda: True
        inst.channels[channel].set_zero_pos()


@pytest.mark.parametrize("channel", CHANNELS)
def test_safe_direction_setter(channel):
    for comm_pairs, value in ((((f':SSD{channel}D1'.encode(), None),), 'up'),
                              (((f':SSD{channel}D0'.encode(), None),), 'down')):
        with expected_protocol(
                SmarActSCULinear,
                comm_pairs,
        ) as inst:
            inst.channels[channel].safe_direction = value


@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_safe_direction_getter(channel):
    for comm_pairs, value in (
            (((f':GSD{channel}'.encode(), f':SD{channel}D1'.encode()),), 'up'),
            (((f':GSD{channel}'.encode(), f':SD{channel}D0'.encode()),), 'down'),
    ):
        with expected_protocol(
                SmarActSCULinear,
                comm_pairs,
        ) as inst:
            assert inst.channels[channel].safe_direction == value


def test_model_getter():
    with expected_protocol(
            SmarActSCULinear,
            [(b':I', b':ISmarAct CU-1D')],
    ) as inst:
        assert inst.model == 'SmarAct CU-1D'


def test_serial_nb_getter():
    with expected_protocol(
            SmarActSCULinear,
            [(b':GID', b':ID722998302')],
    ) as inst:
        assert inst.serial_nb == '722998302'


@pytest.mark.parametrize("channel", CHANNELS)
def test_ask(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':M{channel}'.encode(), f':M{channel}S'.encode())],
    ) as inst:
        assert inst.ask(*(f':M{channel}',), ) == f':M{channel}S'


@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_calibrate_sensor(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':CS{channel}'.encode(), None),
             (f':M{channel}'.encode(), f':M{channel}C'.encode())],
    ) as inst:
        assert inst.channels[channel].calibrate_sensor() == ':M0C'


@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_check_sensor_present(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':GSP{channel}'.encode(), f':SP{channel}P'.encode())],
    ) as inst:
        assert inst.channels[channel].check_sensor_present() is True


@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_get_position(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':GP{channel}'.encode(), f':P{channel}P-0.5'.encode())],
    ) as inst:
        assert inst.channels[channel].get_position() == Q_(-0.5, 'um')


@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_get_positioner_type(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':GST{channel}'.encode(), f':ST{channel}T21'.encode())],
    ) as inst:
        assert inst.channels[channel].get_positioner_type() == f':ST{channel}T21'


@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_set_positioner_type(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':SST{channel}T21'.encode(), None)],
    ) as inst:
        inst.channels[channel].set_positioner_type(21)


@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_move_abs(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':MPA{channel}P100'.encode(), None)],
    ) as inst:
        inst.channels[channel].move_abs((Q_(100, 'um')))


@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_move_rel(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':MPR{channel}P50'.encode(), None)],
    ) as inst:
        inst.channels[channel].move_rel((Q_(50, 'um')))


@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_move_steps_down(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':D{channel}F260A300S100'.encode(), None)],
    ) as inst:
        assert inst.channels[channel].move_steps_down(*(100,), ) is None


@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_move_steps_up(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':U{channel}F260A300S100'.encode(), None)],
    ) as inst:
        assert inst.channels[channel].move_steps_up(*(100,), ) is None


@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_move_to_end_down(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':MES{channel}DD'.encode(), None)],
    ) as inst:
        assert inst.channels[channel].move_to_end_down() is None


@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_move_to_end_up(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':MES{channel}DU'.encode(), None)],
    ) as inst:
        assert inst.channels[channel].move_to_end_up() is None


@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_move_to_ref(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':MTR{channel}H0Z1'.encode(), None)],
    ) as inst:
        assert inst.channels[channel].move_to_ref() is None


@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_stop(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':S{channel}'.encode(), None)],
    ) as inst:
        assert inst.channels[channel].stop() is None


def test_set_baudrate():
    with expected_protocol(
            SmarActSCULinear,
            [(b':CB9600', None), (b':R', None)],
    ) as inst:
        inst.set_baudrate(9600)


def test_set_baudrate_invalid():
    inst = SmarActSCULinear(adapter=None)
    with pytest.raises(pyvisa.VisaIOError):
        inst.set_baudrate(1234)


def test_reset():
    with expected_protocol(
            SmarActSCULinear,
            [(b':R', None)],
    ) as inst:
        assert inst.reset() is None
