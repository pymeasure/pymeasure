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
from pymeasure.instruments.advantest import AdvantestQ8381


def test_init():
    with expected_protocol(AdvantestQ8381, [], ):
        pass  # Verify the expected communication.


def test_wavelength_center():
    with expected_protocol(
        AdvantestQ8381,
        [("CEN 10nm", None),
         ("CEN?", "10")]
    ) as inst:
        instr = inst    # type: AdvantestQ8381
        instr.wavelength_center = 10.0
        assert instr.wavelength_center == 10.0


def test_wavelength_span():
    with expected_protocol(
        AdvantestQ8381,
        [("SPA 15.6nm", None),
         ("SPA?", "15.6")]
    ) as inst:
        instr = inst    # type: AdvantestQ8381
        instr.wavelength_span = 15.6
        assert instr.wavelength_span == 15.6


def test_wavelength_start():
    with expected_protocol(
        AdvantestQ8381,
        [("STA 15.6nm", None),
         ("STA?", "15.6")]
    ) as inst:
        instr = inst    # type: AdvantestQ8381
        instr.wavelength_start = 15.6
        assert instr.wavelength_start == 15.6


def test_wavelength_stop():
    with expected_protocol(
        AdvantestQ8381,
        [("STO 15.6nm", None),
         ("STO?", "15.6")]
    ) as inst:
        instr = inst    # type: AdvantestQ8381
        instr.wavelength_stop = 15.6
        assert instr.wavelength_stop == 15.6


def test_wavelength_marker_value():
    with expected_protocol(
        AdvantestQ8381,
        [("MKV WL", None),
         ("MKV?", "WL"),
         ("MKV FREQ", None),
         ("MKV?", "FREQ")]

    ) as inst:
        instr = inst    # type: AdvantestQ8381
        instr.wavelength_marker_value = "WL"
        assert instr.wavelength_marker_value == "WL"
        instr.wavelength_marker_value = "FREQ"
        assert instr.wavelength_marker_value == "FREQ"
        # test any other value is invalid
        with pytest.raises(ValueError):
            instr.wavelength_marker_value = "DUMMY"


def test_wavelength_value_in():
    with expected_protocol(
        AdvantestQ8381,
        [("WDP VACUUM", None),
         ("WDP?", "VACUUM"),
         ("WDP AIR", None),
         ("WDP?", "AIR")]

    ) as inst:
        instr = inst    # type: AdvantestQ8381
        instr.wavelength_value_in = "VACUUM"
        assert instr.wavelength_value_in == "VACUUM"
        instr.wavelength_value_in = "AIR"
        assert instr.wavelength_value_in == "AIR"
        # test any other value is invalid
        with pytest.raises(ValueError):
            instr.wavelength_value_in = "DUMMY"


def test_level_scale():
    with expected_protocol(
        AdvantestQ8381,
        [("LVS LOG", None),
         ("LVS?", "LOG"),
         ("LVS LIN", None),
         ("LVS?", "LIN")]

    ) as inst:
        instr = inst    # type: AdvantestQ8381
        instr.level_scale = "LOG"
        assert instr.level_scale == "LOG"
        instr.level_scale = "LIN"
        assert instr.level_scale == "LIN"
        # test any other value is invalid
        with pytest.raises(ValueError):
            instr.level_scale = "DUMMY"
