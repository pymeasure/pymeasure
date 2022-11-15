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
from unittest.mock import MagicMock

from pymeasure import instruments
from pymeasure.instruments import Instrument


# Collect all instruments
devices = []
for manufacturer in dir(instruments):
    if manufacturer.startswith("__"):
        continue
    manu = getattr(instruments, manufacturer)
    for dev in dir(manu):
        if dev.startswith("__"):
            continue
        d = getattr(manu, dev)
        try:
            b = issubclass(d, Instrument)
        except TypeError:
            # d is no class
            continue
        else:
            if b:
                devices.append(d)

# Instruments unable to accept an Adapter instance.
proper_adapters = ["IBeamSmart", "ANC300Controller"]
# Instruments with communication in their __init__ which consequently fails.
init = ["ThorlabsPM100USB", "Keithley2700", "TC038", "Agilent34450A",
        "AWG401x_AWG", "AWG401x_AFG", "VARX", "HP8116A"]
# Instruments which require more input arguments
init.extend(["Instrument", "ATSBase"])


@pytest.mark.parametrize("cls", devices)
def test_args(cls):
    "Test that every instrument has adapter as their input argument"
    if cls.__name__ in proper_adapters:
        pytest.skip(f"{cls.__name__} does not accept an Adapter instance.")
    elif cls.__name__ in init:
        pytest.skip(f"{cls.__name__} requires communication in init.")
    cls(adapter=MagicMock())
