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

import importlib
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
proper_adapters = []
# Instruments with communication in their __init__, which consequently fails.
need_init_communication = [
    "ThorlabsPM100USB",
    "Keithley2700",
    "TC038",
    "Agilent34450A",
    "AWG401x_AWG",
    "AWG401x_AFG",
    "VARX",
    "HP8116A",
    "IBeamSmart",
    "ANC300Controller",
]


@pytest.mark.parametrize("cls", devices)
def test_adapter_arg(cls):
    "Test that every instrument has adapter as their input argument"
    if cls.__name__ in proper_adapters:
        pytest.skip(f"{cls.__name__} does not accept an Adapter instance.")
    elif cls.__name__ in need_init_communication:
        pytest.skip(f"{cls.__name__} requires communication in init.")
    elif cls.__name__ == "Instrument":
        pytest.skip("`Instrument` requires a `name` parameter.")
    cls(adapter=MagicMock())


@pytest.mark.parametrize("cls", devices)
def test_name_argument(cls):
    "Test that every instrument accepts a name argument"
    if cls.__name__ in (*proper_adapters, *need_init_communication):
        pytest.skip(f"{cls.__name__} cannot be tested without communication.")
    inst = cls(adapter=MagicMock(), name="Name_Test")
    assert inst.name == "Name_Test"


# This uses a pyvisa-sim default instrument, we could also define our own.
SIM_RESOURCE = 'ASRL2::INSTR'
is_pyvisa_sim_not_installed = not bool(importlib.util.find_spec('pyvisa_sim'))


@pytest.mark.skipif(is_pyvisa_sim_not_installed,
                    reason='PyVISA tests require the pyvisa-sim library')
@pytest.mark.parametrize("cls", devices)
def test_kwargs_to_adapter(cls):
    """Verify that kwargs are accepted and handed to the adapter."""
    if cls.__name__ in (*proper_adapters, *need_init_communication):
        pytest.skip(f"{cls.__name__} cannot be tested without communication.")
    elif cls.__name__ == "Instrument":
        pytest.skip("`Instrument` requires a `name` parameter.")

    with pytest.raises(ValueError,
                       match="'kwarg_test' is not a valid attribute for type SerialInstrument"):
        cls(SIM_RESOURCE, visa_library='@sim', kwarg_test=True)
