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

from pymeasure.display.Qt import QtCore, QtGui, QtWidgets
from pymeasure.display.widgets.filename_widget import (
    FilenameLineEdit,
    FilenameValidator,
    PlaceholderCompleter,
)
from pymeasure.experiment import FloatParameter, Procedure


class _DummyParent(QtWidgets.QWidget):
    """Minimal parent exposing the `extensions` attribute used by
    `FilenameLineEdit.set_tool_tip`."""

    def __init__(self, extensions=("csv", "txt"), parent=None):
        super().__init__(parent=parent)
        self._extensions = list(extensions)

    @property
    def extensions(self):
        return self._extensions


class _Procedure(Procedure):
    """Procedure with parameters that can serve as placeholders."""

    voltage = FloatParameter("Voltage", units="V", default=0)
    current = FloatParameter("Current", units="A", default=1)


@pytest.fixture
def parent_widget(qtbot):
    parent = _DummyParent()
    qtbot.addWidget(parent)
    return parent


@pytest.fixture
def filename_line_edit(qtbot, parent_widget):
    edit = FilenameLineEdit(_Procedure, parent=parent_widget)
    qtbot.addWidget(edit)
    return edit


def test_filename_line_edit_default_text(filename_line_edit):
    assert filename_line_edit.text() == "DATA"


def test_filename_line_edit_has_completer(filename_line_edit):
    assert isinstance(filename_line_edit.completer(), PlaceholderCompleter)


def test_filename_line_edit_has_validator(filename_line_edit):
    assert isinstance(filename_line_edit.validator(), FilenameValidator)


def test_filename_line_edit_tool_tip_mentions_placeholders(filename_line_edit):
    tip = filename_line_edit.toolTip()
    assert "Voltage" in tip
    assert "Current" in tip
    assert "date" in tip
    assert "time" in tip


def test_filename_line_edit_tool_tip_lists_extensions(filename_line_edit):
    tip = filename_line_edit.toolTip()
    assert ".csv" in tip
    assert ".txt" in tip


# ---------------- PlaceholderCompleter.splitPath ----------------

def test_placeholder_completer_init_defaults():
    completer = PlaceholderCompleter(["foo", "bar"])
    assert completer.placeholders == ["foo", "bar"]
    assert (completer.completionMode()
            == QtWidgets.QCompleter.CompletionMode.PopupCompletion)
    assert completer.caseSensitivity() == QtCore.Qt.CaseInsensitive


def test_placeholder_completer_split_path_returns_path():
    completer = PlaceholderCompleter(["foo", "bar"])
    assert completer.splitPath("some_prefix") == ["some_prefix"]


def test_placeholder_completer_split_path_open_brace_populates_model():
    completer = PlaceholderCompleter(["foo", "bar"])
    completer.splitPath("data{")
    model = completer.model()
    assert model.rowCount() == 2
    items = [model.data(model.index(i), QtCore.Qt.DisplayRole) for i in range(model.rowCount())]
    assert "data{foo}" in items
    assert "data{bar}" in items


def test_placeholder_completer_split_path_balanced_braces_clears_model():
    completer = PlaceholderCompleter(["foo", "bar"])
    # First populate the model
    completer.splitPath("data{")
    assert completer.model().rowCount() == 2
    # Balanced braces should clear the model
    completer.splitPath("data{foo}")
    assert completer.model().rowCount() == 0


# ---------------- FilenameValidator ----------------

@pytest.fixture
def validator(filename_line_edit):
    return filename_line_edit.validator()


@pytest.mark.parametrize(
    "input", [
        "data",
        "DATA.csv",
        "data_001",
        "experiment-{Voltage:03}",
        "mixed_{Voltage}_{current}_data.txt",
        "{date}-{time}",
    ]
)
def test_validator_acceptable(validator, input):
    state, _text, _pos = validator.validate(input, len(input))
    assert state == QtGui.QValidator.Acceptable


@pytest.mark.parametrize(
    "input", [
        "data{Voltage",
        "experiment-{Voltage",
        "{date",
    ]
)
def test_validator_intermediate(validator, input):
    state, _text, _pos = validator.validate(input, len(input))
    assert state == QtGui.QValidator.Intermediate


@pytest.mark.parametrize(
    "input", [
        "data<file",
        'data"file',
        "data/file",
        "data\\file",
        "data|file",
        "data?file",
        "data*file",
        "data:file",
        "data{Voltage}:extra}",
    ]
)
def test_validator_invalid(validator, input):
    state, _text, _pos = validator.validate(input, len(input))
    assert state == QtGui.QValidator.Invalid


@pytest.mark.parametrize(
    "input,expected", [
        ("data{Voltage", "data{Voltage}"),
        ("experiment-{date", "experiment-{date}"),
        ("data", "data"),
        ("data{Voltage}", "data{Voltage}"),
    ]
)
def test_validator_fixup(validator, input, expected):
    assert validator.fixup(input) == expected


def test_validator_unknown_placeholder_adds_action(validator, filename_line_edit):
    assert filename_line_edit.actions() == []
    validator.validate("data{not_a_parameter}", 19)
    assert len(filename_line_edit.actions()) == 1
    act = filename_line_edit.actions()[0]
    assert "not_a_parameter" in act.toolTip()


def test_validator_unknown_placeholder_action_removed_when_valid(validator, filename_line_edit):
    validator.validate("data{not_a_parameter}", 19)
    assert len(filename_line_edit.actions()) == 1
    validator.validate("data", 4)
    assert filename_line_edit.actions() == []
