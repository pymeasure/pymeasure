#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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
import importlib.util

import pytest
from pytest import approx

from pymeasure.adapters import VISAAdapter
from pymeasure.instruments import Instrument

pyvisa_sim_installed = bool(importlib.util.find_spec('pyvisa_sim'))


def test_visa_version():
    assert VISAAdapter.has_supported_version()


@pytest.mark.skipif(not pyvisa_sim_installed, reason='pyvisa-sim required but not found.')
def test_correct_visa_kwarg():
    """Confirm that the query_delay kwargs gets passed through to the VISA connection."""
    instr = Instrument(adapter='ASRL1::INSTR', name='delayed', query_delay=0.5, visa_library='@sim')
    assert instr.adapter.connection.query_delay == approx(0.5)
