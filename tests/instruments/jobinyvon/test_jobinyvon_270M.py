import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.jobinyvon.spectro270m import JY270M


def test_init():
    with expected_protocol(
            JY270M,
            [],
    ):
        pass  # Verify the expected communication.


def test_entrysteps_setter():
    with expected_protocol(
            JY270M,
            [(b'k0,0,-50\r', None)],
    ) as inst:
        inst.entrysteps = -50


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'j0,0\r', b'o0\r')],
     0),
    ([(b'j0,0\r', b'o50\r')],
     50),
    ([(b'j0,0\r', b'oo0\r')],
     0),
))
def test_entrysteps_getter(comm_pairs, value):
    with expected_protocol(
            JY270M,
            comm_pairs,
    ) as inst:
        assert inst.entrysteps == value


def test_exitsteps_setter():
    with expected_protocol(
            JY270M,
            [(b'k0,2,-50\r', None)],
    ) as inst:
        inst.exitsteps = -50


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'j0,2\r', b'o0\r')],
     0),
    ([(b'j0,2\r', b'o50\r')],
     50),
    ([(b'j0,2\r', b'oo0\r')],
     0),
))
def test_exitsteps_getter(comm_pairs, value):
    with expected_protocol(
            JY270M,
            comm_pairs,
    ) as inst:
        assert inst.exitsteps == value


def test_gsteps_setter():
    with expected_protocol(
            JY270M,
            [(b'F0,-1000\r', None)],
    ) as inst:
        inst.gsteps = -1000


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'H0\r', b'oo37494\r')],
     37494),
    ([(b'H0\r', b'o31100\r')],
     31100),
    ([(b'H0\r', b'o20000\r')],
     20000),
    ([(b'H0\r', b'oo19000\r')],
     19000),
))
def test_gsteps_getter(comm_pairs, value):
    with expected_protocol(
            JY270M,
            comm_pairs,
    ) as inst:
        assert inst.gsteps == value


def test_motor_init_getter():
    with expected_protocol(
            JY270M,
            [(b'A', None)],
    ) as inst:
        assert inst.motor_init == ''


def test_auto_baud():
    with expected_protocol(
            JY270M,
            [(b' ', b'F')],
    ) as inst:
        assert inst.auto_baud() is True


@pytest.mark.parametrize("comm_pairs, args, kwargs, value", (
    ([(b'j0,0\r', b'o50\r')],
     (), {}, 317.50063500127),
    ([(b'j0,0\r', b'o15\r')],
     (), {}, 95.250190500381),
))
def test_get_entry_slit_microns(comm_pairs, args, kwargs, value):
    with expected_protocol(
            JY270M,
            comm_pairs,
    ) as inst:
        assert inst.get_entry_slit_microns(*args, **kwargs) == value


@pytest.mark.parametrize("comm_pairs, args, kwargs, value", (
    ([(b'j0,2\r', b'o50\r')],
     (), {}, 317.50063500127),
    ([(b'j0,2\r', b'o15\r')],
     (), {}, 95.250190500381),
))
def test_get_exit_slit_microns(comm_pairs, args, kwargs, value):
    with expected_protocol(
            JY270M,
            comm_pairs,
    ) as inst:
        assert inst.get_exit_slit_microns(*args, **kwargs) == value


def test_get_grating_wavelength():
    with expected_protocol(
            JY270M,
            [(b'H0\r', b'o20801\r')],
    ) as inst:
        assert inst.get_grating_wavelength() == 650.0237500000001


def test_motor_busy_check():
    with expected_protocol(
            JY270M,
            [(b'E\r', b'oz')],
    ) as inst:
        assert inst.motor_busy_check() is False


def test_motor_stop():
    with expected_protocol(
            JY270M,
            [(b'L', b'o')],
    ) as inst:
        assert inst.motor_stop() is None


def test_move_entry_slit_microns():
    with expected_protocol(
            JY270M,
            [(b'j0,0\r', b'o0\r'),
             (b'k0,0,15.748000000000001\r', b'o')],
    ) as inst:
        assert inst.move_entry_slit_microns(*(100,), ) is None


def test_move_entry_slit_steps():
    with expected_protocol(
            JY270M,
            [(b'j0,0\r', b'o0\r'),
             (b'k0,0,50\r', b'o')],
    ) as inst:
        assert inst.move_entry_slit_steps(*(50,), ) is None


def test_move_exit_slit_microns():
    with expected_protocol(
            JY270M,
            [(b'j0,2\r', b'o0\r'),
             (b'k0,2,15.748000000000001\r', b'o')],
    ) as inst:
        assert inst.move_exit_slit_microns(*(100,), ) is None


def test_move_exit_slit_steps():
    with expected_protocol(
            JY270M,
            [(b'j0,2\r', b'o0\r'),
             (b'k0,2,50\r', b'o')],
    ) as inst:
        assert inst.move_exit_slit_steps(*(50,), ) is None


@pytest.mark.parametrize("comm_pairs, args, kwargs, value", (
    ([(b'H0\r', b'o37494\r'),
      (b'F0,-37494\r', b'o')],
     (0,), {}, None),
    ([(b'H0\r', b'o31100\r'),
      (b'F0,-11100\r', b'o')],
     (20000,), {}, None),
))
def test_move_grating_steps(comm_pairs, args, kwargs, value):
    with expected_protocol(
            JY270M,
            comm_pairs,
    ) as inst:
        assert inst.move_grating_steps(*args, **kwargs) == value


def test_move_grating_wavelength():
    with expected_protocol(
            JY270M,
            [(b'H0\r', b'o19000\r'),
             (b'F0,1801\r', b'o')],
    ) as inst:
        assert inst.move_grating_wavelength(*(650,), ) is None


def test_write_read():
    with expected_protocol(
            JY270M,
            [(b' ', b'F')],
    ) as inst:
        assert inst.write_read(*(b' ',), ) == b'F'
