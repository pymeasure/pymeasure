# Test all instruments

from inspect import isclass

import pytest

from pymeasure.adapters import FakeAdapter
from pymeasure import instruments

manufacturers = dir(instruments)

devices = []
for manufacturer in manufacturers:
    if manufacturer.startswith("__"):
        continue
    manu = getattr(instruments, manufacturer)
    devis = dir(manu)
    for dev in devis:
        if dev.startswith("__") or dev[0].islower():
            continue
        d = getattr(manu, dev)
        if isclass(d):
            devices.append(getattr(manu, dev))
print(devices)


@pytest.mark.parametrize("cls", devices)
def test_args(cls):
    adapter = FakeAdapter()
    instr = cls(adapter=adapter, **{'name': "test successful"})
    assert instr.name == "test successful"
