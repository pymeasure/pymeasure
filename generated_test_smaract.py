import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.SCUController import SmarActSCULinear


def test_init():
    with expected_protocol(
            SmarActSCULinear,
            [],
    ):
        pass  # Verify the expected communication.
