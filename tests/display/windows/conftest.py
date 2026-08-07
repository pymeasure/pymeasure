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

from unittest import mock

import pytest

from pymeasure.experiment import (
    BooleanParameter,
    FloatParameter,
    IntegerParameter,
    Procedure,
)
from pymeasure.experiment.results import Results


@pytest.fixture(autouse=True)
def _qpa_offscreen(monkeypatch):
    """Run Qt offscreen so window tests do not require a display server."""
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(autouse=True)
def _clean_root_logging_handlers():
    """Remove handlers added to the root logger during a window test.

    ManagedWindow subclasses add a LogWidget handler to the root logger; if the
    widget is destroyed while the handler remains registered, later tests that
    trigger logging raise RuntimeError on the deleted Qt object.
    """
    import logging
    root = logging.getLogger()
    before = list(root.handlers)
    yield
    for handler in list(root.handlers):
        if handler not in before:
            root.removeHandler(handler)


@pytest.fixture
def procedure_class():
    """A Procedure subclass with several parameter types and DATA_COLUMNS."""

    class TestProcedure(Procedure):
        """Procedure with float, int and boolean parameters for window tests."""

        voltage = FloatParameter("Voltage", units="V", minimum=-10, maximum=10, default=0)
        iterations = IntegerParameter("Iterations", minimum=0, maximum=1000, default=10)
        enabled = BooleanParameter("Enabled", default=True)

        DATA_COLUMNS = ["Voltage (V)", "Iterations", "Enabled"]

        def startup(self):
            pass

        def execute(self):
            pass

        def shutdown(self):
            pass

    return TestProcedure


@pytest.fixture
def results_factory(procedure_class, tmp_path):
    """Return a callable producing Results backed by a file in tmp_path."""

    counter = {"i": 0}

    def _make(procedure=None):
        if procedure is None:
            procedure = procedure_class()
        counter["i"] += 1
        filename = tmp_path / f"results_{counter['i']}.csv"
        return Results(procedure, str(filename))

    return _make


@pytest.fixture
def mock_procedure_class():
    """A MagicMock procedure class with named parameters, mirroring test_browser usage."""
    procedure_class = mock.MagicMock()
    param_voltage = mock.MagicMock()
    param_voltage.name = "Voltage"
    param_iterations = mock.MagicMock()
    param_iterations.name = "Iterations"
    param_enabled = mock.MagicMock()
    param_enabled.name = "Enabled"

    procedure_class.voltage = param_voltage
    procedure_class.iterations = param_iterations
    procedure_class.enabled = param_enabled
    return procedure_class
