import pytest

from pymeasure.test import expected_protocol


from pymeasure.instruments.anaheimautomation import DPSeriesMotorController


def test_init():
    with expected_protocol(
            DPSeriesMotorController, []) as instr:
        pass


def test_basespeed():
    with expected_protocol(
            DPSeriesMotorController,
            [(b"@0VB", b"123")],
            ) as instr:
        assert instr.basespeed == 123


def test_basespeed_setter():
    with expected_protocol(
            DPSeriesMotorController,
            [(b"@0B123", None)],
            ) as instr:
        instr.basespeed = 123


def test_step_position():
    with expected_protocol(
            DPSeriesMotorController,
            [(b"@0VZ", b"13")],
            ) as instr:
        assert instr.step_position == 13


def test_step_position_setter():
    with expected_protocol(
            DPSeriesMotorController,
            [(b"@0P13", None), (b"@0G", None)],
            ) as instr:
        instr.step_position = 13
