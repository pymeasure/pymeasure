import pytest
from pymeasure.instruments.granville_phillips import GP350UHV

class DummyAdapter:
    def write(self, cmd): pass
    def read(self): return "0"

def test_gp350_init():
    inst = GP350(DummyAdapter(), "GP350 Test")
    assert inst.name == "GP350 Test"
