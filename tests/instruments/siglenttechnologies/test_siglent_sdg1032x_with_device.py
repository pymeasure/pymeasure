

import pytest
from pymeasure.instruments.siglenttechnologies.siglent_sdg1032x import SDG1023X
from math import pi, sin


pytest.skip('Only works with connected hardware', allow_module_level=True)


@pytest.fixture(scope="session")
def generator():
    try:
        generator = SDG1023X("")
    except IOError:
        print("Not able to connect to waveform generator.")
        assert False

    yield generator
