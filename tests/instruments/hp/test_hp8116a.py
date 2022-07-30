import pytest

from pymeasure.test import expected_protocol


from pymeasure.instruments.hp import HP8116A as _HP8116A
from pymeasure.instruments.hp.hp8116a import Status


class HP8116A(_HP8116A):
    @property
    def status(self):
        return Status(5)


def test_init():
    with expected_protocol(
            HP8116A, [(b"CST", b"x" * 87 + b' ,\r\n')]) as instr:
        pass


@pytest.mark.xfail
def test_duty_cycle():
    with expected_protocol(
            HP8116A, [(b"CST", b"x" * 87 + b' ,\r\n'),
                      (b"IDTY", b"00000035")]) as instr:
        assert instr.duty_cycle == 35


def test_duty_cycle_setter():
    with expected_protocol(
            HP8116A, [(b"CST", b"x" * 87 + b' ,\r\n'),
                      (b"DTY 34.5 %", None)]) as instr:
        instr.duty_cycle = 34.5


