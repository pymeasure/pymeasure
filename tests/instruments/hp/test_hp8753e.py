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

import logging

from pymeasure.instruments.hp import HP8753E
from pymeasure.test import expected_protocol

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def test_hp8753e_id():
    """Verify *IDN? communication"""
    with expected_protocol(
        HP8753E,
        [("*IDN?", "HEWLETT PACKARD,8753E,0,7.10\n"), ("*IDN?", "HEWLETT PACKARD,8753E,0,7.10\n")],
    ) as inst:
        assert inst.id == ["HEWLETT PACKARD", "8753E", "0", "7.10"]


def test_hp8753e_start_frequency():
    with expected_protocol(
        HP8753E,
        [
            ("*IDN?", "HEWLETT PACKARD,8753E,0,7.10\n"),
            ("STAR?", "30E+003\n"),
            ("STAR 4.000000e+05 Hz", None),
            ("STAR?", "400E+003\n"),
        ],
    ) as inst:
        assert inst.start_frequency == 30_000
        inst.start_frequency = 400e3
        assert inst.start_frequency == 400_000


def test_hp8753e_set_sweep_time_fastest():
    with expected_protocol(
        HP8753E, [("*IDN?", "HEWLETT PACKARD,8753E,0,7.10\n"), ("SWEA", None)]
    ) as inst:
        assert inst.set_sweep_time_fastest() is None


def test_hp8753e_manu():
    with expected_protocol(HP8753E, [("*IDN?", "HEWLETT PACKARD,8753E,0,7.10\n")]) as inst:
        assert inst.manu == "HEWLETT PACKARD"


def test_hp8753e_model():
    with expected_protocol(HP8753E, [("*IDN?", "HEWLETT PACKARD,8753E,0,7.10\n")]) as inst:
        assert inst.model == "8753E"


def test_hp8753e_fw():
    with expected_protocol(HP8753E, [("*IDN?", "HEWLETT PACKARD,8753E,0,7.10\n")]) as inst:
        assert inst.fw == "7.10"


def test_hp8753e_set_single_frequency_scan():
    with expected_protocol(
        HP8753E,
        [
            ("*IDN?", "HEWLETT PACKARD,8753E,0,7.10\n"),
            ("STAR 5.000000e+07 Hz", None),
            ("STOP 5.000000e+07 Hz", None),
            ("POIN3", None),
        ],
    ) as inst:
        inst.set_fixed_frequency(50e6)


def test_hp8753e_measuring_parameter():
    with expected_protocol(
        HP8753E,
        [
            ("*IDN?", "HEWLETT PACKARD,8753E,0,7.10\n"),
            ("S21", None),
            ("S11?", "0\n"),
            ("S12?", "0\n"),
            ("S21?", "1\n"),
        ],
    ) as inst:
        assert inst.MEASURING_PARAMETER_MAP == {
            "A/R": "AR",
            "B/R": "BR",
            "A/B": "AB",
            "A": "MEASA",
            "B": "MEASB",
            "R": "MEASR",
        }
        inst.measuring_parameter = "S21"
        assert inst.measuring_parameter == "S21"


def test_hp8753e_reset():
    with expected_protocol(
        HP8753E, [("*IDN?", "HEWLETT PACKARD,8753E,0,7.10\n"), ("*RST", None)]
    ) as inst:
        inst.reset()


def test_hp8753e_shutdown():
    with expected_protocol(
        HP8753E, [("*IDN?", "HEWLETT PACKARD,8753E,0,7.10\n"), ("SOUP0", None)]
    ) as inst:
        inst.shutdown()


def test_hp8753e_averaging_restart():
    with expected_protocol(
        HP8753E, [("*IDN?", "HEWLETT PACKARD,8753E,0,7.10\n"), ("AVERREST", None)]
    ) as inst:
        inst.averaging_restart()


def test_hp8753e_emit_beep():
    with expected_protocol(
        HP8753E, [("*IDN?", "HEWLETT PACKARD,8753E,0,7.10\n"), ("EMIB", None)]
    ) as inst:
        inst.emit_beep()
