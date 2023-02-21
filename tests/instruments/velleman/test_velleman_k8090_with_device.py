"""
Test the instrument class for the Velleman F8090.

This tests the instrument class with the real device connected.
"""

import pytest
from time import sleep

from pymeasure.adapters import SerialAdapter
from pymeasure.instruments.velleman import VellemanK8090


@pytest.fixture()
def instrument(connected_device_address):
    adapter = SerialAdapter(connected_device_address, baudrate=19200, timeout=5.0)
    return VellemanK8090(adapter)


def test_version(instrument):
    ver = instrument.version

    assert ver is not None and isinstance(ver, tuple)


def test_status(instrument):
    last_on, curr_on, time_on = instrument.status

    assert isinstance(curr_on, list)


def test_switch_on_off(instrument):
    """Test switch on-off together.

    This tests the physical switches and the status feedback.
    You must also hear the real relays clicking, and verify the
    LEDs 1 and 3 alone light up.
    """
    instrument.switch_off = [1, 2, 3, 4, 5, 6, 7, 8]
    sleep(0.5)

    instrument.switch_on = [1, 3]
    sleep(0.5)

    _, curr_on_1, _ = instrument.status

    instrument.switch_off = [1, 2, 3, 4, 5, 6, 7, 8]
    sleep(0.5)

    _, curr_on_2, _ = instrument.status

    assert curr_on_1 == [True, False, True, False, False, False, False, False]
    assert not any(curr_on_2)


def test_switch_on_off_blocking(instrument):
    """Test the blocking versions of the on/off switching.

    You should also verify the sound of the toggling relays and
    LEDs for 2 and 4 should alone be on.
    """
    instrument.switch_off = [1, 2, 3, 4, 5, 6, 7, 8]
    sleep(0.5)  # Start with all off

    _, curr_on_1, _ = instrument.switch_on_blocking([2, 4])

    sleep(0.5)

    _, curr_on_2, _ = instrument.switch_off_blocking([2, 4])

    sleep(0.5)

    instrument.switch_off = [1, 2, 3, 4, 5, 6, 7, 8]
    sleep(0.5)  # Stop with all off

    assert curr_on_1 == [False, True, False, True, False, False, False, False]
    assert not any(curr_on_2)
