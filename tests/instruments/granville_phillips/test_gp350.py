# This file is part of the PyMeasure package.
# Copyright (c) 2013-2025 PyMeasure Developers
# See LICENSE for details.

from pymeasure.instruments.granville_phillips.GP350 import GP350

class DummyAdapter:
    """Simulates the GP350 communication for testing."""
    def write(self, command):
        self.last_command = command

    def read(self):
        return "0.0"  # Simulated response


def test_gp350_init():
    adapter = DummyAdapter()
    instrument = GP350(adapter)
    assert instrument is not None
