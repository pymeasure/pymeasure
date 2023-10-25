#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

from pymeasure.instruments.philips.PM6669 import PM6669, Functions
from pymeasure.adapters import prologix


@pytest.skip('Only work with connected hardware', allow_module_level=True)
class TestPhilipsPM6669:
    """
    Unit tests for PM6669 class.

    This test suite, needs the following setup to work properly:
        - A PM6669 device should be connected to the computer;
        - The device's address must be set in the RESOURCE constant.
    """

    RESOURCE = prologix.PrologixAdapter("ASRL/dev/cu.usbmodem23201::INSTR",7, visa_library="@py", gpib_read_timeout=1000)

    FUNCTION_STRINGS = [
        ("FREQ A", Functions.FREQUENCY_A),
        ("PER A", Functions.PER_A),
        ("FREQ B", Functions.FREQUENCY_B),
        ("TOTM A", Functions.TOT_A),
        ("WIDTH A", Functions.WIDTH_A)
    ]
    TIMEOUT_TIMES = [0, 0.1, 10, 25.5]
    MEASUREMENT_TIMES = [0.2, 1, 10]
    BOOLEAN_CASES = [True, False]
    instr = PM6669(RESOURCE)

    @pytest.fixture
    def make_resetted_instr(self):
        self.instr.reset_to_defaults()
        return self.instr

    @pytest.mark.parametrize('case, expected', FUNCTION_STRINGS)
    def test_function_modes(self, make_resetted_instr, case, expected):
        instr = make_resetted_instr
        instr.function = case
        assert instr.function == expected

    @pytest.mark.parametrize('case', TIMEOUT_TIMES)
    def test_timeout_times(self, make_resetted_instr, case):
        instr = make_resetted_instr
        instr.measurement_timeout = case
        assert instr.measurement_timeout == case

    @pytest.mark.parametrize('case', MEASUREMENT_TIMES)
    def test_measurement_times(self, make_resetted_instr, case):
        instr = make_resetted_instr
        instr.measurement_time = case
        assert instr.measurement_time == case

    @pytest.mark.parametrize('case', BOOLEAN_CASES)
    def test_freerun(self, make_resetted_instr, case):
        instr = make_resetted_instr
        instr.freerun = case
        assert instr.freerun == case
