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

from typing import Any

import pytest

from pymeasure.display.Qt import QtCore, QtGui, QtWidgets
from pymeasure.display.widgets.sequencer_widget import ComboBoxDelegate, SequencerWidget
from pymeasure.experiment import Procedure


class _FakeProcedure(Procedure):
    DATA_COLUMNS = []


class _FakeParent(QtWidgets.QWidget):
    """Minimal parent implementing the SequencerParent interface."""

    procedure_class: type[Procedure] = _FakeProcedure
    displays: list[str] = []

    def make_procedure(self) -> Procedure:
        return _FakeProcedure()

    def queue(self, procedure: Procedure | None = None) -> None:
        self.queued = procedure


def test_fake_parent_constructs(qtbot):
    """A parent implementing the protocol is accepted."""
    parent = _FakeParent()
    qtbot.addWidget(parent)

    widget = SequencerWidget(parent=parent)
    qtbot.addWidget(widget)

    assert widget._parent is parent


def test_plain_qwidget_parent_rejected(qtbot):
    """A plain QWidget does not implement SequencerParent and is rejected at runtime."""
    # Annotated as Any so this exercises the runtime guard without a static type error;
    # the static rejection of a plain QWidget is covered by pyright.
    plain_parent: Any = QtWidgets.QWidget()
    qtbot.addWidget(plain_parent)

    with pytest.raises(TypeError, match="make_procedure"):
        SequencerWidget(parent=plain_parent)


def test_non_qwidget_parent_rejected():
    """An object implementing the protocol but not a QWidget is rejected at runtime."""

    class _ProtocolOnlyParent:
        procedure_class: type[Procedure] = _FakeProcedure
        displays: list[str] = []

        def make_procedure(self) -> Procedure:
            return _FakeProcedure()

        def queue(self, procedure: Procedure | None = None) -> None:
            pass

    with pytest.raises(TypeError, match="must be a QWidget"):
        SequencerWidget(parent=_ProtocolOnlyParent())


def test_combobox_delegate_materializes_choices(qtbot):
    """An iterable of choices is materialized, so its values survive iteration."""
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    choices = (choice for choice in ["a", "b"])

    delegate = ComboBoxDelegate(parent, choices)

    assert delegate.items == ["a", "b"]


def test_combobox_delegate_reuses_choices_across_editors(qtbot):
    """Every editor receives all choices, even from a single-pass iterable."""
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    choices = (choice for choice in ["a", "b"])
    delegate = ComboBoxDelegate(parent, choices)
    index = QtCore.QModelIndex()
    option = QtWidgets.QStyleOptionViewItem()

    first_editor = delegate.createEditor(parent, option, index)
    second_editor = delegate.createEditor(parent, option, index)

    for editor in (first_editor, second_editor):
        assert [editor.itemText(i) for i in range(editor.count())] == ["a", "b"]


def test_combobox_delegate_set_editor_data_uses_materialized_items(qtbot):
    """The current cell value is selected after the choices have been consumed."""
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    choices = (choice for choice in ["a", "b"])
    delegate = ComboBoxDelegate(parent, choices)
    model = QtGui.QStandardItemModel(1, 1)
    model.setData(model.index(0, 0), "b")
    index = model.index(0, 0)

    editor = delegate.createEditor(parent, QtWidgets.QStyleOptionViewItem(), index)
    delegate.setEditorData(editor, index)

    assert editor.currentText() == "b"
