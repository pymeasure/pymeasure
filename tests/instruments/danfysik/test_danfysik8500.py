from pymeasure.test import expected_protocol

from pymeasure.instruments.danfysik import Danfysik8500


def test_init():
    with expected_protocol(
            Danfysik8500,
            [(b"ERRT", None), (b"UNLOCK", None)]
            ):
        pass
