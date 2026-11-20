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

import os

import pytest

# pytest-qt's session-scoped `qapp` fixture is instantiated before any
# function-scoped fixture of a test, so setting the environment there via
# monkeypatch would be too late. Set the offscreen platform at conftest
# import time (before any test or fixture runs). Keep later-set variables:
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def pytest_configure(config):
    # Disable pytest-qt's Qt log capture for this run. Equivalent to passing
    # ``--no-qt-log``. With the capture handler installed, ``processEvents``
    # during test teardown may periodically segfault (a Python callback is
    # invoked from the Qt message handler while events are processed); the
    # crash occurs intermittently (~50% of runs) whenever the display suite is
    # exercised, and vanishes reliably with log capture disabled. The handler
    # is instead disabled whenever display tests are part of the run, where
    # the captured Qt messages are not needed to diagnose failures.
    config.option.qt_log = False


@pytest.fixture(autouse=True)
def _qpa_offscreen(monkeypatch):
    """Run Qt offscreen so the whole display test suite needs no display server."""
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
