import pytest

from pymeasure.test import expected_protocol


from pymeasure.instruments.fwbell import FWBell5080


def test_init():
    with expected_protocol(
            FWBell5080, []) as instr:
        pass


def test_units():
    with expected_protocol(
            FWBell5080, [(b":UNIT:FLUXDC:GAUSS", None)]) as instr:
        instr.units = 'gauss'


@pytest.mark.xfail  # implementation is broken.
def test_field():
    with expected_protocol(
            FWBell5080, [(b":MEAS:FLUX?", b"123.45 T")]) as instr:
        assert instr.field == 123.45
