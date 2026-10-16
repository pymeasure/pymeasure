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

import ctypes
import importlib
import sys
from unittest import mock

import numpy  # noqa: F401  (imported before sys.platform is faked, see below)
import pytest

_REAL_WINDLL = getattr(ctypes, "windll", None)


class _MissingNIDaqmxLibrary:
    """Stand-in for :code:`ctypes.windll` without the NI-DAQmx library.

    Only the :code:`nicaiu` lookup fails, so unrelated consumers of
    :code:`ctypes.windll` keep working.
    """

    def __getattr__(self, name):
        if name == "nicaiu":
            raise AttributeError("nicaiu")
        if _REAL_WINDLL is None:
            raise AttributeError(name)
        return getattr(_REAL_WINDLL, name)


@pytest.fixture
def reload_ni_package():
    """Drop the cached :code:`ni` modules so that the package is imported again."""
    def loaded():
        return {name: module for name, module in sys.modules.items()
                if name == "pymeasure.instruments.ni"
                or name.startswith("pymeasure.instruments.ni.")}

    saved = loaded()
    for name in saved:
        del sys.modules[name]
    yield
    for name in list(loaded()):
        del sys.modules[name]
    sys.modules.update(saved)


def test_ni_package_imports_without_ni_daqmx_library(reload_ni_package):
    """The ni package imports even if the NI-DAQmx library is not installed.

    Loading that library raises an AttributeError (rather than an OSError) when it
    is missing, which the package has to tolerate.
    The library is only looked up on Windows, so the platform is faked in order to
    exercise that branch on every CI platform.
    """
    # Import the parent package first: it pulls in pyserial, which needs the real
    # ctypes.windll while sys.platform is faked.
    importlib.import_module("pymeasure.instruments")

    with mock.patch("sys.platform", "win32"), \
            mock.patch("ctypes.windll", _MissingNIDaqmxLibrary(), create=True):
        module = importlib.import_module("pymeasure.instruments.ni")

    assert not hasattr(module, "DAQmx")
