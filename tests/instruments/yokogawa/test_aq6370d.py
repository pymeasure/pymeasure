import pytest

from pymeasure.instruments.yokogawa.aq6370d import AQ6370D
from pymeasure.test import expected_protocol


def test_init():
    with expected_protocol(
        AQ6370D,
        [],
    ):
        pass  # Verify the expected communication.


def test_resolution_bandwidth_setter():
    with expected_protocol(
        AQ6370D,
        [(b":SENSe:BWIDth:RESolution 1e-10", None)],
    ) as inst:
        inst.resolution_bandwidth = 1e-10
