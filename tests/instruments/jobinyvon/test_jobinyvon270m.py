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
import time
from pymeasure.test import expected_protocol
from pymeasure.instruments.jobinyvon.spectro270m import JY270M



def test_entrysteps_setter():
    with expected_protocol(
            JY270M,
            [(b'k0,0,50\r', None),
             ],
    ) as inst:
        inst.entrysteps = 50

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
            [(b'k0,2,100\r', None),
             ],
    ) as inst:
        inst.exitsteps = 100


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
            [(b'F0,1000\r', None)],
    ) as inst:
        inst.gsteps = 1000


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
        assert inst.get_entry_slit_microns() == 317.50063500127
        assert inst.get_entry_slit_microns() == -317.50063500127
        assert inst.get_entry_slit_microns() == 952.50190500381



def test_get_exit_slit_microns():
    with expected_protocol(
            JY270M,
            [(b'j0,2\r', b'o50\r'),
            (b'j0,2\r', b'o-50\r'),
            (b'j0,2\r', b'o150\r')
             ],
    ) as inst:
        assert inst.get_exit_slit_microns() == 317.50063500127
        assert inst.get_exit_slit_microns() == -317.50063500127
        assert inst.get_exit_slit_microns() == 952.50190500381

def test_get_grating_wavelength():
    with expected_protocol(
            JY270M,
            [(b'H0\r', b'o20801\r'),
             (b'H0\r', b'o5000\r'),
             (b'H0\r', b'o30000\r')],
    ) as inst:
        assert inst.get_grating_wavelength() == 650.0237500000001
        assert inst.get_grating_wavelength() == 156.24250000000006
        assert inst.get_grating_wavelength() == 937.4925000000001

def test_motor_busy_check():
    with expected_protocol(
            JY270M,
            [(b'E\r', b'oz\r')],
    ) as inst:
        assert inst.motor_busy_check() == None

def test_motor_stop():
    with expected_protocol(
            JY270M,
            [(b'L', b'o\r')],
    ) as inst:
        assert inst.motor_stop() == None

def test_move_entry_slit_microns():
    with expected_protocol(
            JY270M,
            [(b'j0,0\r', b'o100\r')
             ],
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

def test_move_grating_steps():
    with expected_protocol(
            JY270M,
            comm_pairs,
    ) as inst:
        assert inst.move_grating_steps() == value

def test_move_grating_wavelength():
    with expected_protocol(
            JY270M,
            [(b'H0\r', b'o19000\r'),
             (b'F0,1801\r', b'o')],
    ) as inst:
        assert inst.move_grating_wavelength() is None

def test_write_read():
    with expected_protocol(
            JY270M,
            [(b' ', b'F')],
    ) as inst:
        assert inst.write_read() == b'F'
