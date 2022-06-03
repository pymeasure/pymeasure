# NOTE: this is just for demonstration for instrument specific tests, see #632.
# Delete before merging into master.

import pytest


@pytest.fixture(scope="session")
def dummy_instrument(pytestconfig):
    resource_name = pytestconfig.getoption("resource_name")
    dummmy_instrument = resource_name
    return dummmy_instrument


def test_allways_run():
    "This test always runs and succeeds"
    assert True


@pytest.mark.needs_instrument
def test_needs_instrument(dummy_instrument):
    "This test needs a dummy instrument to run and succeed"
    print(dummy_instrument)
    assert dummy_instrument
