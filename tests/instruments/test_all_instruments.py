#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pymeasure import instruments
from pymeasure.instruments import Instrument, Channel, generic_types


# Collect all instruments
def find_devices_in_module(module):
    devices = set()
    channels = set()
    base_dir = Path(module.__path__[0])
    base_import = module.__package__ + "."
    for inst_file in Path(base_dir).rglob("*.py"):
        relative_path = inst_file.relative_to(base_dir)
        if inst_file == "__init__.py":
            # import parent module when filename __init__.py
            relative_import = ".".join(relative_path.parts[:-1])[:-3]
        else:
            relative_import = ".".join(relative_path.parts)[:-3]
        try:
            submodule = importlib.import_module(base_import + relative_import)
            for dev in dir(submodule):
                if dev.startswith("__"):
                    continue
                d = getattr(submodule, dev)
                try:
                    i = issubclass(d, Instrument)
                    c = issubclass(d, Channel)
                except TypeError:
                    # d is no class
                    continue
                else:
                    if i:
                        devices.add(d)
                    elif c:
                        channels.add(d)
        except ModuleNotFoundError:
            # Some non-required driver dependencies may not be installed on test computer,
            # for example ni.VirtualBench
            pass
        except (OSError, AttributeError):
            # On Windows instruments.ni.daqmx can raise an OSError before ModuleNotFoundError
            # when checking installed driver files
            # it raises an AttributeError under Python 312
            pass
    return devices, channels


devices, channels = find_devices_in_module(instruments)

# Collect all properties
properties = []
for device in devices.union(channels):
    for property_name in dir(device):
        prop = getattr(device, property_name)
        if isinstance(prop, property):
            properties.append((device, property_name, prop))
for mixin in dir(generic_types):
    if mixin in ("Instrument", "Channel", "CommonBase"):  # exclucion list.
        continue
    elif mixin[0].isupper():
        # filter only classes
        device = getattr(generic_types, mixin)
        for property_name in dir(device):
            prop = getattr(device, property_name)
            if isinstance(prop, property):
                properties.append((device, property_name, prop))

# Instruments unable to accept an Adapter instance.
proper_adapters = []
# Instruments with communication in their __init__, which consequently fails.
need_init_communication = [
    "SwissArmyFake",
    "FakeInstrument",
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
    "Keithley2281S",
    "SpellmanXRV",
]
# Instruments whose property docstrings are not YET in accordance with the style (Get, Set, Control)
grandfathered_docstring_instruments = [
    "Agilent33521A",
    "Agilent8257D",
    "Agilent8722ES",
    "AgilentB1500",
    "AgilentE4408B",
    "AgilentE4980",
    "AnritsuMS2090A",
    "DPSeriesMotorController",
    "HP3437A",
    "HP34401A",
    "HP3478A",
    "HP6632A",
    "HP6633A",
    "HP6634A",
    "KeysightDSOX1102G",
    "IPS120_10",
    "ITC503",
    "PS120_10",
    "SFM",
    "SG380",
    "SM7045D",
    "SR570",
    "SR830",
    "SR860",
    "SR510",
]


@pytest.mark.parametrize("cls", devices)
def test_adapter_arg(cls):
    "Test that every instrument has adapter as their input argument."
    if cls.__name__ in proper_adapters:
        pytest.skip(f"{cls.__name__} does not accept an Adapter instance.")
    elif cls.__name__ in need_init_communication:
        pytest.skip(f"{cls.__name__} requires communication in init.")
    elif cls.__name__ == "Instrument":
        pytest.skip("`Instrument` requires a `name` parameter.")
    cls(adapter=MagicMock())


@pytest.mark.parametrize("cls", devices)
def test_name_argument(cls):
    "Test that every instrument accepts a name argument."
    if cls.__name__ in (*proper_adapters, *need_init_communication):
        pytest.skip(f"{cls.__name__} cannot be tested without communication.")
    inst = cls(adapter=MagicMock(), name="Name_Test")
    assert inst.name == "Name_Test"


# This uses a pyvisa-sim default instrument, we could also define our own.
SIM_RESOURCE = "ASRL2::INSTR"
is_pyvisa_sim_not_installed = not bool(importlib.util.find_spec("pyvisa_sim"))


@pytest.mark.skipif(
    is_pyvisa_sim_not_installed, reason="PyVISA tests require the pyvisa-sim library"
)
@pytest.mark.parametrize("cls", devices)
def test_kwargs_to_adapter(cls):
    """Verify that kwargs are accepted and handed to the adapter."""
    if cls.__name__ in (*proper_adapters, *need_init_communication):
        pytest.skip(f"{cls.__name__} cannot be tested without communication.")
    elif cls.__name__ == "Instrument":
        pytest.skip("`Instrument` requires a `name` parameter.")

    with pytest.raises(
        ValueError, match="'kwarg_test' is not a valid attribute for type SerialInstrument"
    ):
        cls(SIM_RESOURCE, visa_library="@sim", kwarg_test=True)


@pytest.mark.parametrize("cls", devices)
@pytest.mark.filterwarnings(
    "error:It is deprecated to specify `includeSCPI` implicitly:FutureWarning"
)
def test_includeSCPI_explicitly_set(cls):
    if cls.__name__ in (*proper_adapters, *need_init_communication):
        pytest.skip(f"{cls.__name__} cannot be tested without communication.")
    elif cls.__name__ == "Instrument":
        pytest.skip("`Instrument` requires a `name` parameter.")

    cls(adapter=MagicMock())
    # assert that no error is raised


@pytest.mark.parametrize("cls", devices)
@pytest.mark.filterwarnings(
    "error:Defining SCPI base functionality with `includeSCPI=True` is deprecated:FutureWarning"
)
def test_includeSCPI_not_set_to_True(cls):
    if cls.__name__ in (*proper_adapters, *need_init_communication):
        pytest.skip(f"{cls.__name__} cannot be tested without communication.")
    elif cls.__name__ == "Instrument":
        pytest.skip("`Instrument` requires a `name` parameter.")

    cls(adapter=MagicMock())
    # assert that no error is raised


def property_name_to_id(value):
    """Create a test id from `value`."""
    device, property_name, prop = value
    return f"{device.__name__}.{property_name}"


@pytest.mark.parametrize("prop_set", properties, ids=property_name_to_id)
def test_property_docstrings(prop_set):
    device, property_name, prop = prop_set
    if device.__name__ in grandfathered_docstring_instruments:
        pytest.skip(f"{device.__name__} is in the codebase and has to be refactored later on.")
    start = prop.__doc__.split(maxsplit=1)[0]
    assert start in ("Control", "Measure", "Set", "Get"), (
        f"'{device.__name__}.{property_name}' docstring does start with '{start}', not 'Control', "
        "'Measure', 'Get', or 'Set'."
    )
