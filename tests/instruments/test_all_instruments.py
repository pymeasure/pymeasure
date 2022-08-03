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


from inspect import isclass

import pytest

from pymeasure.adapters import FakeAdapter
from pymeasure import instruments


class Adapter(FakeAdapter):
    class Connection:
        def clear(self):
            pass

        def close(self):
            pass

        def read_stb(self):
            return 5

    def __init__(self):
        super().__init__()
        self.connection = self.Connection()

    def read_bytes(self, count=0):
        return b""


# Collect all instruments
devices = []
for manufacturer in dir(instruments):
    if manufacturer.startswith("__"):
        continue
    manu = getattr(instruments, manufacturer)
    for dev in dir(manu):
        if dev.startswith("__") or dev[0].islower():
            continue
        d = getattr(manu, dev)
        if isclass(d):
            devices.append(getattr(manu, dev))

# List of adapters and other classes to be skipped
adapters = ["Decimal", "VISAAdapter", "DynamicProperty", "TopticaAdapter",
            "OxfordInstrumentsAdapter", "LakeShoreUSBAdapter",
            "DanfysikAdapter", "AttocubeConsoleAdapter"]
# Instruments using their own adapter, thus raising an error with the FakeAdapter
proper_adapters = ["IBeamSmart", "ParkerGV6", "LakeShore425", "FWBell5080",
                   "Danfysik8500", "ANC300Controller"]
# Instruments with communication in their __init__ which consequently fails
init = ["ThorlabsPM100USB", "Keithley2700", "TC038", "Agilent34450A",
        "AWG401x_AWG", "AWG401x_AFG", "VARX"]


@pytest.mark.parametrize("cls", devices)
def test_args(cls):
    if cls.__name__ in adapters:
        pytest.skip(f"{cls.__name__} is an adapter.")
    elif cls.__name__ in proper_adapters:
        pytest.skip(f"Instrument {cls.__name__} defines its own adapter.")
    elif cls.__name__ in init:
        pytest.skip(f"Instrument {cls.__name__} requires communication in init.")
    adapter = Adapter()
    instr = cls(adapter=adapter, **{'name': "test successful"})
    assert instr.name == "test successful"
