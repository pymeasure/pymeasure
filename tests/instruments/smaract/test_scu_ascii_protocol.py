import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.smaract.scu_ascii import SmarActSCULinear
from pint import Quantity as Q_


CHANNELS = ['0']


def test_init():
    with expected_protocol(
            SmarActSCULinear,
            [],
    ):
        pass  # Verify the expected communication.

@pytest.mark.parametrize("channel", CHANNELS)
def test_channel_frequency_max_setter(channel):
    with expected_protocol(
            SmarActSCULinear,
            [(f':SCLF{channel}F500'.encode(), None)],
    ) as inst:
        inst.channels[channel].frequency_max = Q_(500, 'Hz')


def test_channel0_frequency_max_getter():
    with expected_protocol(
            SmarActSCULinear,
            [(b':GCLF0', b':CLF0F500')],
    ) as inst:
        assert inst.channel0.frequency_max.magnitude == 500


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b':SSD0D1', None)],
     'up'),
    ([(b':SSD0D0', None)],
     'down'),
))
def test_channel0_safe_direction_setter(comm_pairs, value):
    with expected_protocol(
            SmarActSCULinear,
            comm_pairs,
    ) as inst:
        inst.channel0.safe_direction = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b':GSD0', b':SD0D1')],
     'up'),
    ([(b':GSD0', b':SD0D0')],
     'down'),
))
def test_channel0_safe_direction_getter(comm_pairs, value):
    with expected_protocol(
            SmarActSCULinear,
            comm_pairs,
    ) as inst:
        assert inst.channel0.safe_direction == value


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


def test_ask():
    with expected_protocol(
            SmarActSCULinear,
            [(b':M0', b':M0S')],
    ) as inst:
        assert inst.ask(*(':M0',), ) == ':M0S'


def test_channel0_calibrate_sensor():
    with expected_protocol(
            SmarActSCULinear,
            [(b':CS0', None),
             (b':M0', b':M0C')],
    ) as inst:
        assert inst.channel0.calibrate_sensor() == ':M0C'


def test_channel0_check_sensor_present():
    with expected_protocol(
            SmarActSCULinear,
            [(b':GSP0', b':SP0P')],
    ) as inst:
        assert inst.channel0.check_sensor_present() is True


def test_channel0_get_position():
    with expected_protocol(
            SmarActSCULinear,
            [(b':GP0', b':P0P-0.5')],
    ) as inst:
        assert inst.channel0.get_position() == Q_(-0.5, 'um')


def test_channel0_get_positioner_type():
    with expected_protocol(
            SmarActSCULinear,
            [(b':GST0', b':ST0T21')],
    ) as inst:
        assert inst.channel0.get_positioner_type() == ':ST0T21'


def test_channel0_move_abs():
    with expected_protocol(
            SmarActSCULinear,
            [(b':MPA0P100', None)],
    ) as inst:
        inst.channel0.move_abs((Q_(100, 'um')))


def test_channel0_move_rel():
    with expected_protocol(
            SmarActSCULinear,
            [(b':MPR0P50', None)],
    ) as inst:
        inst.channel0.move_rel((Q_(50, 'um')))


def test_channel0_move_steps_down():
    with expected_protocol(
            SmarActSCULinear,
            [(b':D0F260A300S100', None)],
    ) as inst:
        assert inst.channel0.move_steps_down(*(100,), ) is None


def test_channel0_move_steps_up():
    with expected_protocol(
            SmarActSCULinear,
            [(b':U0F260A300S100', None)],
    ) as inst:
        assert inst.channel0.move_steps_up(*(100,), ) is None


def test_channel0_move_to_end_down():
    with expected_protocol(
            SmarActSCULinear,
            [(b':MES0DD', None)],
    ) as inst:
        assert inst.channel0.move_to_end_down() is None


def test_channel0_move_to_end_up():
    with expected_protocol(
            SmarActSCULinear,
            [(b':MES0DU', None)],
    ) as inst:
        assert inst.channel0.move_to_end_up() is None


def test_channel0_move_to_ref():
    with expected_protocol(
            SmarActSCULinear,
            [(b':MTR0H0Z1', None)],
    ) as inst:
        assert inst.channel0.move_to_ref() is None


def test_channel0_stop():
    with expected_protocol(
            SmarActSCULinear,
            [(b':S0', None)],
    ) as inst:
        assert inst.channel0.stop() is None

def test_reset():
    with expected_protocol(
            SmarActSCULinear,
        [(b':R', None)],
    ) as inst:
        assert inst.reset() is None
