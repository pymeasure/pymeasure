import pytest
import numpy as np
import numpy.testing as npt
from pymeasure.test import expected_protocol
from pymeasure.instruments.srs import SR830


def test_init():
    with expected_protocol(SR830, []):
        pass  # Verify the expected communication.


def test_filter_slope_setter():
    with expected_protocol(SR830, [(b'OFSL3', None)]) as inst:
        inst.filter_slope = 24


def test_sample_frequency_setter():
    with expected_protocol(SR830, [(b'SRAT4.000000', None)]) as inst:
        inst.sample_frequency = 1


def test_time_constant_setter():
    with expected_protocol(SR830, [(b'OFLT8', None)]) as inst:
        inst.time_constant = 0.1


@pytest.mark.parametrize(
    "comm_pairs, args, kwargs, value",
    [
        (
            [
                (b'REST', None),
                (b'FAST0;STRT', None),
                *[(b'SPTS?', b'1\n')] * 62,
                (b'SPTS?', b'2\n'),
                *[(b'SPTS?', b'2\n')] * 20,
                (b'SPTS?', b'3\n'),
                *[(b'SPTS?', b'3\n')] * 20,
                (b'SPTS?', b'4\n'),
                *[(b'SPTS?', b'4\n')] * 40,
                (b'SPTS?', b'5\n'),
                *[(b'SPTS?', b'5\n')] * 60,
                (b'SPTS?', b'6\n'),
                *[(b'SPTS?', b'6\n')] * 70,
                (b'SPTS?', b'7\n'),
                *[(b'SPTS?', b'7\n')] * 80,
                (b'SPTS?', b'8\n'),
                *[(b'SPTS?', b'8\n')] * 90,
                (b'SPTS?', b'9\n'),
                *[(b'SPTS?', b'9\n')] * 100,
                (b'SPTS?', b'10\n'),
                (b'PAUS', None),
                (b'SPTS?', b'10\n'),
                (
                    b'TRCL?1,0,10',
                    b'W n\x00X n\x00X n\x00X n\x00X n\x00X n\x00X n\x00X n\x00W n\x00X n\x00'
                ),
                (
                    b'TRCL?2,0,10',
                    b'W n\x00W n\x00W n\x00W n\x00W n\x00W n\x00W n\x00W n\x00W n\x00W n\x00'
                ),
            ],
            (),
            {'buffer_size': 10, 'fast': False},
            (
                np.array([0.50531006, 0.50537109, 0.50537109, 0.50537109, 0.50537109,
                          0.50537109, 0.50537109, 0.50537109, 0.50531006, 0.50537109]),
                np.array([0.50531006, 0.50531006, 0.50531006, 0.50531006, 0.50531006,
                          0.50531006, 0.50531006, 0.50531006, 0.50531006, 0.50531006])
            )
        ),
        (
            [
                (b'REST', None),
                (b'SRAT?', b'4\n'),
                (
                    b'FAST2;STRD', 
                    b'9;9;9;9;9;:;:;9;:;9;:;9;9;:;:;:;:;9;:;9;'
                ),
                (b'PAUS', b''),
                (b'OEXP? 1', b'0,0\n'),
                (b'OEXP? 2', b'0,0\n'),
                (b'SENS?', b'26\n'),
                (b'SENS?', b'26\n'),
                (b'SENS?', b'26\n')
            ],
            (),
            {'buffer_size': 10, 'fast': True},
            (
                np.array([0.50536667, 0.50536667, 0.50536667, 0.5054, 0.5054,
                          0.5054, 0.50536667, 0.5054, 0.5054, 0.5054]),
                np.array([0.50536667, 0.50536667, 0.5054, 0.50536667, 0.50536667,
                          0.50536667, 0.5054, 0.5054, 0.50536667, 0.50536667])
            )
        )
    ]
)
def test_buffer_measure_fast(comm_pairs, args, kwargs, value):
    with expected_protocol(SR830, comm_pairs) as inst:
        result = inst.buffer_measure_fast(*args, **kwargs)
        npt.assert_array_almost_equal(result[0], value[0])
        npt.assert_array_almost_equal(result[1], value[1])
