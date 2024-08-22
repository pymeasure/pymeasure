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


def test_buffer_measure_fast():
    with expected_protocol(
        SR830,
        [
            (b'REST', None),
            (b'FAST0;STRT', None),
            *[(b'SPTS?', b'9\n')] * 292,
            (b'SPTS?', b'10\n'),
            (b'PAUS', None),
            (b'SPTS?', b'10\n'),
            (
                b'TRCL?1,0,10',
                b'Y n\x00Y n\x00X n\x00X n\x00X n\x00Y n\x00X n\x00Y n\x00X n\x00X n\x00'
            ),
            (
                b'TRCL?2,0,10',
                b'W n\x00W n\x00W n\x00W n\x00W n\x00W n\x00W n\x00W n\x00W n\x00W n\x00'
            ),
        ]
    ) as inst:
        result = inst.buffer_measure_fast(buffer_size=10, fast=False)
        expected_x = np.array([
            0.50543213, 0.50543213, 0.50537109, 0.50537109, 0.50537109,
            0.50543213, 0.50537109, 0.50543213, 0.50537109, 0.50537109
        ])
        expected_y = np.array([
            0.50531006, 0.50531006, 0.50531006, 0.50531006, 0.50531006,
            0.50531006, 0.50531006, 0.50531006, 0.50531006, 0.50531006
        ])
        npt.assert_array_almost_equal(result[0], expected_x)
        npt.assert_array_almost_equal(result[1], expected_y)
