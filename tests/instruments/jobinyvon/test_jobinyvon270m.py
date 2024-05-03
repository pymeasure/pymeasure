#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
from pymeasure.instruments.jobinyvon.jobinyvon270m import JY270M


def test_entrysteps_setter():
    with expected_protocol(
            JY270M,
            [(b'k0,0,50\r', None),
             (b'k0,0,1500\r', None),
             (b'k0,0,-50\r', None)
             ],
    ) as inst:
        inst.entrysteps = 50
        inst.entrysteps = 1500
        inst.entrysteps = -50


def test_entrysteps_getter():
    with expected_protocol(
            JY270M,
            [(b'j0,0\r', b'o50\r'),
             (b'j0,0\r', b'o-50\r'),
             (b'j0,0\r', b'o1550\r')
             ],
    ) as inst:
        assert inst.entrysteps == 50
        assert inst.entrysteps == -50
        assert inst.entrysteps == 1550


def test_exitsteps_setter():
    with expected_protocol(
            JY270M,
            [(b'k0,2,50\r', None),
             (b'k0,2,1500\r', None),
             (b'k0,2,-50\r', None)
             ],
    ) as inst:
        inst.exitsteps = 50
        inst.exitsteps = 1500
        inst.exitsteps = -50


def test_exitsteps_getter():
    with expected_protocol(
            JY270M,
            [(b'j0,2\r', b'o100\r'),
             (b'j0,2\r', b'o-30\r'),
             (b'j0,2\r', b'o250\r')
             ],
    ) as inst:
        assert inst.exitsteps == 100
        assert inst.exitsteps == -30
        assert inst.exitsteps == 250


def test_motor_init():
    with expected_protocol(
            JY270M,
            [(b'A', b'o')
             ],
    ) as inst:
        inst.motor_init()


def test_gsteps_setter():
    with expected_protocol(
            JY270M,
            [(b'F0,1000\r', None),
             (b'F0,5000\r', None),
             (b'F0,-50\r', None)],
    ) as inst:
        inst.gsteps = 1000
        inst.gsteps = 5000
        inst.gsteps = -50


def test_gsteps_getter():
    with expected_protocol(
            JY270M,
            [(b'H0\r', b'o1000\r'),
             (b'H0\r', b'o350\r'),
             (b'H0\r', b'o12000\r')
             ],
    ) as inst:
        assert inst.gsteps == 1000
        assert inst.gsteps == 350
        assert inst.gsteps == 12000


def test_get_entry_slit_microns():
    with expected_protocol(
            JY270M,
            [(b'j0,0\r', b'o50\r'),
             (b'j0,0\r', b'o-50\r'),
             (b'j0,0\r', b'o150\r')
             ],
    ) as inst:
        assert inst.get_entry_slit_microns() == pytest.approx(89.28571428571428)
        assert inst.get_entry_slit_microns() == pytest.approx(-89.28571428571428)
        assert inst.get_entry_slit_microns() == pytest.approx(267.85714285714283)


def test_get_exit_slit_microns():
    with expected_protocol(
            JY270M,
            [(b'j0,2\r', b'o50\r'),
             (b'j0,2\r', b'o-50\r'),
             (b'j0,2\r', b'o150\r')
             ],
    ) as inst:
        assert inst.get_exit_slit_microns() == pytest.approx(89.28571428571428)
        assert inst.get_exit_slit_microns() == pytest.approx(-89.28571428571428)
        assert inst.get_exit_slit_microns() == pytest.approx(267.85714285714283)


def test_get_grating_wavelength():
    with expected_protocol(
            JY270M,
            [(b'H0\r', b'o20801\r'),
             (b'H0\r', b'o5000\r'),
             (b'H0\r', b'o30000\r')],
    ) as inst:
        assert inst.get_grating_wavelength() == pytest.approx(650.0237500000001)
        assert inst.get_grating_wavelength() == pytest.approx(156.24250000000006)
        assert inst.get_grating_wavelength() == pytest.approx(937.4925000000001)


def test_motor_busy_check():
    with expected_protocol(
            JY270M,
            [(b'E\r', b'oz\r')],
    ) as inst:
        assert inst.motor_busy_check() is None


def test_motor_stop():
    with expected_protocol(
            JY270M,
            [(b'L', b'o\r')],
    ) as inst:
        assert inst.motor_stop() is None


def test_move_entry_slit_microns():
    with expected_protocol(
            JY270M,
            [(b'j0,0\r', b'o0\r'),
             (b'k0,0,50\r', b'o'),
             (b'j0,0\r', b'o0\r'),
             (b'k0,0,5000\r', b'o'),
             (b'j0,0\r', b'o0\r'),
             (b'k0,0,1500\r', b'o')
             ],
    ) as inst:
        assert inst.move_entry_slit_microns(50 * inst.micrometers_in_one_step) is None
        assert inst.move_entry_slit_microns(5000 * inst.micrometers_in_one_step) is None
        assert inst.move_entry_slit_microns(1500 * inst.micrometers_in_one_step) is None


def test_move_entry_slit_steps():
    with expected_protocol(
            JY270M,
            [(b'j0,0\r', b'o0\r'),
             (b'k0,0,50\r', b'o'),
             (b'j0,0\r', b'o0\r'),
             (b'k0,0,5000\r', b'o'),
             (b'j0,0\r', b'o0\r'),
             (b'k0,0,1500\r', b'o')
             ],
    ) as inst:
        assert inst.move_entry_slit_steps(50) is None
        assert inst.move_entry_slit_steps(5000) is None
        assert inst.move_entry_slit_steps(1500) is None


def test_move_exit_slit_microns():
    with expected_protocol(
            JY270M,
            [(b'j0,2\r', b'o0\r'),
             (b'k0,2,50\r', b'o'),
             (b'j0,2\r', b'o0\r'),
             (b'k0,2,5000\r', b'o'),
             (b'j0,2\r', b'o0\r'),
             (b'k0,2,1500\r', b'o')
             ],
    ) as inst:
        assert inst.move_exit_slit_microns(50 * inst.micrometers_in_one_step) is None
        assert inst.move_exit_slit_microns(5000 * inst.micrometers_in_one_step) is None
        assert inst.move_exit_slit_microns(1500 * inst.micrometers_in_one_step) is None


def test_move_exit_slit_steps():
    with expected_protocol(
            JY270M,
            [(b'j0,2\r', b'o0\r'),
             (b'k0,2,50\r', b'o'),
             (b'j0,2\r', b'o0\r'),
             (b'k0,2,5000\r', b'o'),
             (b'j0,2\r', b'o0\r'),
             (b'k0,2,1500\r', b'o')
             ],
    ) as inst:
        assert inst.move_exit_slit_steps(50) is None
        assert inst.move_exit_slit_steps(5000) is None
        assert inst.move_exit_slit_steps(1500) is None


def test_move_grating_steps():
    with expected_protocol(
            JY270M,
            [(b'H0\r', b'o0\r'),
             (b'F0,1000\r', b'o'),
             (b'H0\r', b'o0\r'),
             (b'F0,15000\r', b'o'),
             (b'H0\r', b'o0\r'),
             (b'F0,35000\r', b'o')
             ],
    ) as inst:
        assert inst.move_grating_steps(1000) is None
        assert inst.move_grating_steps(15000) is None
        assert inst.move_grating_steps(35000) is None


def test_move_grating_wavelength():
    with expected_protocol(
            JY270M,
            [(b'H0\r', b'o0\r'),
             (b'F0,1001\r', b'o'),
             (b'H0\r', b'o0\r'),
             (b'F0,551\r', b'o'),
             (b'H0\r', b'o0\r'),
             (b'F0,101\r', b'o')
             ],
    ) as inst:
        assert inst.move_grating_wavelength(1000 / inst.steps_in_one_nanometer) is None
        assert inst.move_grating_wavelength(550 / inst.steps_in_one_nanometer) is None
        assert inst.move_grating_wavelength(100 / inst.steps_in_one_nanometer) is None


def test_write_read():
    with expected_protocol(
            JY270M,
            [(b' ', b'F')],
    ) as inst:
        assert inst.write_read(b' ', 1) == b'F'
