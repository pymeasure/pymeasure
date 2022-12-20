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


# Instruments which do not yet accept "name" argument
nameless_instruments = [
    "AdvantestR3767CG",
    "Agilent33220A",
    "Agilent33500",
    "Agilent33521A",
    "Agilent34410A",
    "Agilent4156",
    "Agilent8257D",
    "Agilent8722ES",
    "AgilentB1500",
    "AgilentE4408B",
    "AgilentE4980",
    "Ametek7270",
    "AMI430",
    "DPSeriesMotorController",
    "APSIN12G",
    "AnritsuMG3692C",
    "AnritsuMS9740A",
    "BKPrecision9130B",
    "Danfysik8500",
    "SM7045D",  # deltaelektronika
    "Nxds",  # edwards
    "EurotestHPP120256",
    "Fluke7341",
    "FWBell5080",
    "ND287",
    "HP33120A",
    "HP3437A",
    "HP34401A",
    "HP3478A",
    "HP6632A",
    "HP6633A",
    "HP6634A",
    "HP8657B",
    "Keithley2000",
    "Keithley2306",
    "Keithley2400",
    "Keithley2450",
    "Keithley2600",
    "Keithley2750",
    "Keithley6221",
    "Keithley6517B",
    "KeysightDSOX1102G",
    "KeysightN5767A",
    "KeysightN7776C",
    "LakeShore331",
    "LakeShore421",
    "LakeShore425",
    "LeCroyT3DSO1204",
    "ESP300",
    "ParkerGV6",
    "CNT91",  # pendulum
    "razorbillRP100",
    "FSL",
    "SFM",
    "SPD1168X",  # siglenttechnologies
    "SPD1305X",  # siglenttechnologies
    "DSP7265",
    "SG380",
    "SR510",
    "SR570",
    "SR830",
    "SR860",
    "AFG3152C",
    "TDS2000",  # tectronix
    "ATS525",  # temptronic
    "ATS545",  # temptronic
    "ECO560",  # temptronic
    "TexioPSW360L30",
    "Thermotron3800",
    "ThorlabsPro8000",
    "Yokogawa7651",
    "YokogawaGS200",
]


@pytest.mark.parametrize("cls", devices)
def test_name_argument(cls):
    "Test that every instrument accepts a name argument"
    if cls.__name__ in (*proper_adapters, *need_init_communication):
        pytest.skip(f"{cls.__name__} cannot be tested without communication.")
    elif cls.__name__ in nameless_instruments:
        pytest.skip(f"{cls.__name__} does not accept a name argument yet.")
    inst = cls(adapter=MagicMock(), name="Name_Test")
    assert inst.name == "Name_Test"
