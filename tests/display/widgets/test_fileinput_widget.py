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

import pytest

from pymeasure.display.Qt import QtWidgets
from pymeasure.display.widgets.fileinput_widget import FileInputWidget
from pymeasure.experiment import FloatParameter, Procedure


class _DummyParent(QtWidgets.QWidget):
    """Minimal parent exposing the `procedure_class` attribute that
    `FileInputWidget` expects on its parent (used by `FilenameLineEdit`)."""

    def __init__(self, procedure_class):
        super().__init__()
        self.procedure_class = procedure_class

    @property
    def extensions(self):
        # FileInputWidget._extensions defaults to ["csv", "txt"]; expose the
        # same value here so `FilenameLineEdit.set_tool_tip` can read it.
        return ["csv", "txt"]


class _Procedure(Procedure):
    """Procedure with parameters that can serve as placeholders."""

    voltage = FloatParameter("Voltage", units="V", default=0)
    current = FloatParameter("Current", units="A", default=1)


@pytest.fixture
def widget(qtbot):
    parent = _DummyParent(_Procedure)
    qtbot.addWidget(parent)
    wdg = FileInputWidget(parent=parent)
    # Keep references alive: FileInputWidget accesses `parent` at runtime via
    # `self.parent()`, so it must outlive the test function scope.
    wdg._dummy_parent = parent
    wdg.show()
    return wdg


def test_directory_get_set(widget):
    widget.directory = "/tmp/data"
    assert widget.directory == "/tmp/data"


def test_filename_get_set(widget):
    widget.filename = "experiment.csv"
    assert widget.filename == "experiment.csv"


@pytest.mark.parametrize(
    "filename,base,extension", [
        ("data.csv", "data", "csv"),
        ("data.txt", "data", "txt"),
        ("data", "data", "csv"),
        ("data.unknown", "data.unknown", "csv"),
        ("archive.tar.gz", "archive.tar.gz", "csv"),
    ]
)
def test_filename_base_and_extension(widget, filename, base, extension):
    widget.filename = filename
    assert widget.filename_base == base
    assert widget.filename_extension == extension


def test_extensions_get_default(widget):
    assert widget.extensions == ["csv", "txt"]


def test_extensions_set_strips_dots(widget):
    widget.extensions = [".log", "json"]
    assert widget.extensions == ["log", "json"]


def test_extensions_set_updates_default(widget):
    widget.extensions = ["log", "json"]
    widget.filename = "data"
    assert widget.filename_extension == "log"


def test_store_measurement_toggle(widget):
    assert widget.store_measurement is True
    widget.store_measurement = False
    assert widget.store_measurement is False
    widget.store_measurement = True
    assert widget.store_measurement is True


def test_store_measurement_coerces_to_bool(widget):
    widget.store_measurement = 0
    assert widget.store_measurement is False
    widget.store_measurement = "yes"
    assert widget.store_measurement is True


def test_filename_fixed_default(widget):
    assert widget.filename_fixed is False


def test_filename_fixed_disables_input(widget):
    widget.filename_fixed = True
    assert widget.filename_input.isEnabled() is False


def test_filename_fixed_re_enable_when_unfixed(widget):
    widget.filename_fixed = True
    assert widget.filename_input.isEnabled() is False
    widget.filename_fixed = False
    assert widget.filename_input.isEnabled() is True


def test_set_input_fields_enabled_true(widget):
    widget.set_input_fields_enabled(True)
    assert widget.filename_input.isEnabled() is True
    assert widget.directory_input.isEnabled() is True


def test_set_input_fields_enabled_false(widget):
    widget.set_input_fields_enabled(False)
    assert widget.filename_input.isEnabled() is False
    assert widget.directory_input.isEnabled() is False


def test_set_input_fields_enabled_with_filename_fixed(widget):
    widget.filename_fixed = True
    # store_measurement True, but filename_fixed blocks filename input
    widget.set_input_fields_enabled(True)
    assert widget.filename_input.isEnabled() is False
    assert widget.directory_input.isEnabled() is True
    # store_measurement False disables both
    widget.set_input_fields_enabled(False)
    assert widget.filename_input.isEnabled() is False
    assert widget.directory_input.isEnabled() is False


def test_store_measurement_toggle_updates_input_fields(widget):
    """Toggling the checkbox should enable/disable the input fields."""
    widget.writefile_toggle.setChecked(False)
    assert widget.filename_input.isEnabled() is False
    assert widget.directory_input.isEnabled() is False
    widget.writefile_toggle.setChecked(True)
    assert widget.filename_input.isEnabled() is True
    assert widget.directory_input.isEnabled() is True


def test_filename_input_uses_procedure_placeholders(widget):
    """FilenameLineEdit should pick up placeholder names from the procedure."""
    placeholders = widget.filename_input.placeholders
    assert "Voltage" in placeholders
    assert "Current" in placeholders
    assert "date" in placeholders
    assert "time" in placeholders
