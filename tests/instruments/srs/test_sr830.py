#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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

from pymeasure.test import expected_protocol
from pymeasure.instruments.srs.sr830 import SR830
import numpy as np
import numpy.testing as npt

def test_id():
    """Verify the communication of the device type."""
    with expected_protocol(
        SR830,
        [("*IDN?", "Stanford_Research_Systems,SR830,s/n12345,ver1.07"),],
    ) as inst:
        assert inst.id == "Stanford_Research_Systems,SR830,s/n12345,ver1.07"


@pytest.mark.parametrize("number, value", (
        ("0", 2e-9),
        ("14", 100e-6),
        ("25", 0.5),
))
def test_sensitivity(number, value):
    """Verify the communication of the sensitivity getter."""
    with expected_protocol(
        SR830,
        [("SENS?", number),],
    ) as inst:
        assert inst.sensitivity == pytest.approx(value)


def test_frequency():
    """Verify the communication of the frequency getter."""
    with expected_protocol(
        SR830,
        [("FREQ?", "121.98"),],
    ) as inst:
        assert inst.frequency == pytest.approx(121.98)


def test_snap():
    """Verify the communication of the measurement values."""
    with expected_protocol(
        SR830,
        [("SNAP? 1,2", "-4.17234e-007,-5.9605e-007"),],
    ) as inst:
        xy = inst.xy
        assert len(xy) == 2
        assert xy[0] == pytest.approx(-4.17234e-007)
        assert xy[1] == pytest.approx(-5.9605e-007)


def test_get_scaling():
    """Verify the communication of the X channel scaling settings."""
    with expected_protocol(
        SR830,
        [("OEXP? 1", "9.7,1"),],
    ) as inst:
        offset, expand = inst.get_scaling("X")
        assert offset == pytest.approx(9.7)
        assert expand == pytest.approx(10)


def test_output_conversion():
    """Verify the communication of the X channel value with conversion."""
    with expected_protocol(
        SR830,
        [("OEXP? 1", "10,1"),
         ("SENS?", "19"),
         ("OUTP?1", "-0.000500266"),
         ],
    ) as inst:
        conv = inst.output_conversion("X")
        assert conv(inst.x) == pytest.approx(-2.66e-7)

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
