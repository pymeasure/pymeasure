#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""Helpers for the Eurotherm tests run on a real controller (``*_with_device.py``)."""

import os

import pytest


def connection_kwargs() -> dict:
    """Return the Modbus address and baud rate set by environment variables."""
    kwargs = {"address": int(os.environ.get("EUROTHERM_ADDRESS", "1"))}
    if "EUROTHERM_BAUD_RATE" in os.environ:
        kwargs["baud_rate"] = int(os.environ["EUROTHERM_BAUD_RATE"])
    return kwargs


def assert_plausible_temperature(value) -> None:
    """Check that `value` is a float in a plausible temperature range."""
    assert isinstance(value, float)
    assert -300 < value < 3000


def assert_plausible_output(value) -> None:
    """Check that `value` is a float in a plausible output power range (percent)."""
    assert isinstance(value, float)
    assert -100.1 <= value <= 100.1


def assert_changes_and_restores(obj, name: str, new) -> None:
    """Set the property `name` of `obj` to `new`, check it, then restore the old value."""
    old = getattr(obj, name)
    try:
        setattr(obj, name, new)
        assert getattr(obj, name) == pytest.approx(new, rel=1e-6, abs=1e-3)
    finally:
        setattr(obj, name, old)
    assert getattr(obj, name) == pytest.approx(old, rel=1e-6, abs=1e-3)
