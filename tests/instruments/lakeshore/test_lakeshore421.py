import pytest

from pymeasure.test import expected_protocol


from pymeasure.instruments.lakeshore import LakeShore421


def test_init():
    with expected_protocol(
            LakeShore421, []) as instr:
        pass


def test_unit():
    with expected_protocol(
            LakeShore421, [(b"UNIT?", b"G")]) as instr:
        assert instr.unit == "G"


def test_unit_setter():
    with expected_protocol(
            LakeShore421, [(b"UNIT G", None)]) as instr:
        instr.unit = "G"


def test_max_hold_reset():
    with expected_protocol(
            LakeShore421, [(b"MAXC", None)]) as instr:
        instr.max_hold_reset()
