import pytest
from pymeasure.test import expected_protocol
from pymeasure.instruments.jobinyvon.spectro270m import JY270M

def test_motor_init():
    """Verify the initialization function of the motor"""
    with expected_protocol(
            JY270M,
            [],
    ):
        pass


test_motor_init()