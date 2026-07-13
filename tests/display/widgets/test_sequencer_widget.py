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

from inspect import signature
from io import StringIO
from unittest import mock

import pytest

from pymeasure.display.Qt import QtCore, QtWidgets, QtGui
from pymeasure.display.widgets.sequencer_widget import (
    ComboBoxDelegate,
    ExpressionValidator,
    LineEditDelegate,
    SequenceDialog,
    SequencerTreeModel,
    SequencerTreeView,
    SequencerWidget,
)
from pymeasure.experiment import Parameter, Procedure
from pymeasure.experiment.sequencer import SequenceHandler


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class _TestProcedure(Procedure):
    """Procedure with two parameters for sequencer tests."""

    x = Parameter("X", default=1)
    y = Parameter("Y", default=2)

    DATA_COLUMNS = ["X", "Y"]

    def startup(self):
        pass

    def execute(self):
        pass

    def shutdown(self):
        pass


def _make_queue(signature_only_procedure=True):
    """Return a fake ``queue`` callable accepting a ``procedure`` keyword."""

    def queue(procedure=None):
        pass

    if signature_only_procedure:
        queue.__signature__ = signature(lambda procedure=None: None)
    else:
        queue.__signature__ = signature(lambda: None)
    return queue


@pytest.fixture
def parent_widget(qtbot):
    """A QWidget stand-in for the ManagedWindow used by SequencerWidget."""
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    parent.queue = _make_queue()
    parent.procedure_class = lambda: _TestProcedure()
    parent.displays = ["x", "y"]
    parent.make_procedure = lambda: _TestProcedure()
    return parent


@pytest.fixture
def model():
    """A SequencerTreeModel wrapping an empty SequenceHandler."""
    return SequencerTreeModel(data=SequenceHandler())


@pytest.fixture
def populated_model(model):
    """A SequencerTreeModel with a parent P1 and child P2."""
    p1 = model.add_node("P1")
    model.add_node("P2", parent=p1)
    expr_idx = model.index(p1.row(), 2, model.parent(p1))
    model.setData(expr_idx, "[1, 2, 3]")
    child = next(n for n in model if n.internalPointer().parameter == "P2")
    child_expr = model.index(child.row(), 2, model.parent(child))
    model.setData(child_expr, "[4, 5]")
    return model


# ---------------------------------------------------------------------------
# SequencerTreeModel
# ---------------------------------------------------------------------------


def test_tree_model_initial_state(model):
    """The model starts empty with the configured header."""
    assert model.rowCount(QtCore.QModelIndex()) == 0
    assert model.columnCount(QtCore.QModelIndex()) == 3
    assert model.headerData(0, QtCore.Qt.Orientation.Horizontal,
                            QtCore.Qt.ItemDataRole.DisplayRole) == "Level"
    assert model.headerData(1, QtCore.Qt.Orientation.Horizontal,
                            QtCore.Qt.ItemDataRole.DisplayRole) == "Parameter"
    assert model.headerData(2, QtCore.Qt.Orientation.Horizontal,
                            QtCore.Qt.ItemDataRole.DisplayRole) == "Sequence"


def test_tree_model_custom_header():
    """A custom header is honoured."""
    model = SequencerTreeModel(data=SequenceHandler(),
                               header=("A", "B", "C"))
    assert model.headerData(1, QtCore.Qt.Orientation.Horizontal,
                            QtCore.Qt.ItemDataRole.DisplayRole) == "B"


def test_tree_model_add_node_root(model):
    """Adding a root node reports a valid index and increases row count."""
    idx = model.add_node("P1")
    assert idx.isValid()
    assert idx.row() == 0
    assert idx.column() == 0
    assert model.rowCount(QtCore.QModelIndex()) == 1
    assert idx.internalPointer().parameter == "P1"
    assert idx.internalPointer().level == 0


def test_tree_model_add_node_child(model):
    """A child node is added under the supplied parent index."""
    parent = model.add_node("P1")
    child = model.add_node("P2", parent=parent)
    assert child.isValid()
    assert child.row() == 0
    assert model.rowCount(parent) == 1
    assert child.internalPointer().level == 1
    assert child.internalPointer().parent is parent.internalPointer()


def test_tree_model_remove_node_leaf(model):
    """Removing a leaf node drops it from the model."""
    idx = model.add_node("P1")
    assert model.rowCount(QtCore.QModelIndex()) == 1
    model.remove_node(idx)
    assert model.rowCount(QtCore.QModelIndex()) == 0


def test_tree_model_remove_node_with_children(populated_model):
    """Removing a parent node also removes its descendants."""
    parent = next(n for n in populated_model
                  if n.internalPointer().parameter == "P1")
    populated_model.remove_node(parent)
    parameters = [n.internalPointer().parameter for n in populated_model]
    assert parameters == []


def test_tree_model_flags(model):
    """Flags are enabled/selectable everywhere and editable from column 1."""
    idx = model.add_node("P1")
    no_flags = model.flags(QtCore.QModelIndex())
    assert no_flags == QtCore.Qt.ItemFlag.NoItemFlags

    level_flags = model.flags(model.index(idx.row(), 0, model.parent(idx)))
    assert level_flags & QtCore.Qt.ItemFlag.ItemIsEnabled
    assert level_flags & QtCore.Qt.ItemFlag.ItemIsSelectable
    assert not (level_flags & QtCore.Qt.ItemFlag.ItemIsEditable)

    param_flags = model.flags(model.index(idx.row(), 1, model.parent(idx)))
    assert param_flags & QtCore.Qt.ItemFlag.ItemIsEditable


def test_tree_model_data(populated_model):
    """The data() method returns the parameter and expression strings."""
    p1 = next(n for n in populated_model
              if n.internalPointer().parameter == "P1")
    param_idx = populated_model.index(p1.row(), 1, populated_model.parent(p1))
    expr_idx = populated_model.index(p1.row(), 2, populated_model.parent(p1))
    assert (populated_model.data(param_idx, QtCore.Qt.ItemDataRole.DisplayRole)
            == "P1")
    assert (populated_model.data(expr_idx, QtCore.Qt.ItemDataRole.DisplayRole)
            == "[1, 2, 3]")


def test_tree_model_data_invalid_index(model):
    """An invalid index returns None."""
    assert model.data(QtCore.QModelIndex(),
                      QtCore.Qt.ItemDataRole.DisplayRole) is None


def test_tree_model_data_wrong_role(model):
    """A non-display role returns None."""
    idx = model.add_node("P1")
    param_idx = model.index(idx.row(), 1, model.parent(idx))
    assert (model.data(param_idx, QtCore.Qt.ItemDataRole.EditRole) is None)


def test_tree_model_index_and_parent(populated_model):
    """index() and parent() navigate the tree consistently."""
    p1 = next(n for n in populated_model
              if n.internalPointer().parameter == "P1")
    p2 = next(n for n in populated_model
              if n.internalPointer().parameter == "P2")
    assert p2.parent() == p1
    assert p1.parent() == QtCore.QModelIndex()


def test_tree_model_index_invalid_child(model):
    """Asking for an out-of-range child returns an invalid index."""
    parent = model.add_node("P1")
    assert not model.index(42, 0, parent).isValid()


def test_tree_model_rowCount_column(model):
    """rowCount returns 0 for non-zero columns of a valid parent."""
    parent = model.add_node("P1")
    col_idx = model.index(parent.row(), 1, model.parent(parent))
    assert model.rowCount(col_idx) == 0


def test_tree_model_set_data_updates_expression(model):
    """setData on the expression column persists the value on the item."""
    idx = model.add_node("P1")
    expr_idx = model.index(idx.row(), 2, model.parent(idx))
    assert model.setData(expr_idx, "[1, 2]") is True
    assert idx.internalPointer().expression == "[1, 2]"


def test_tree_model_set_data_emits_data_changed(qtbot, model):
    """setData emits the dataChanged signal for the edited index."""
    idx = model.add_node("P1")
    expr_idx = model.index(idx.row(), 2, model.parent(idx))
    received = []

    def _slot(top_left, bottom_right, roles):
        received.append((top_left, bottom_right, list(roles)))

    model.dataChanged.connect(_slot)
    model.setData(expr_idx, "[1, 2]")
    assert len(received) == 1
    assert received[0][0] == expr_idx
    assert received[0][2] == [QtCore.Qt.ItemDataRole.EditRole]


def test_tree_model_visit_tree(populated_model):
    """visit_tree yields nodes in depth-first order."""
    nodes = list(populated_model.visit_tree(None))
    assert [n.internalPointer().parameter for n in nodes] == ["P1", "P2"]


def test_tree_model_iter(populated_model):
    """Iteration over the model visits every node."""
    parameters = [n.internalPointer().parameter for n in populated_model]
    assert parameters == ["P1", "P2"]


def test_tree_model_save_round_trip(populated_model):
    """save() then load() preserves the tree contents."""
    buf = StringIO()
    populated_model.save(buf)
    assert buf.getvalue() == '- "P1", "[1, 2, 3]"\n-- "P2", "[4, 5]"'

    new_model = SequencerTreeModel(data=SequenceHandler())
    buf.seek(0)
    new_model.load(buf)
    new_params = [
        (n.internalPointer().parameter, n.internalPointer().expression)
        for n in new_model
    ]
    assert new_params == [("P1", "[1, 2, 3]"), ("P2", "[4, 5]")]


def test_tree_model_load_invalid_expression(qtbot):
    """Loading a file with an invalid expression logs but does not raise."""
    new_model = SequencerTreeModel(data=SequenceHandler())
    buf = StringIO('- "P1", "[1,2"')
    # The SequenceHandler.load does not validate expressions; the error
    # surfaces only during parameters_sequence. Loading succeeds.
    new_model.load(buf)
    assert [n.internalPointer().parameter for n in new_model] == ["P1"]


# ---------------------------------------------------------------------------
# ExpressionValidator
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "expression,expected", [
        ("[1, 2, 3]", QtGui.QValidator.State.Acceptable),
        ("range(1, 5)", QtGui.QValidator.State.Acceptable),
        ("list(range(10))", QtGui.QValidator.State.Acceptable),
        ("[1, 2", QtGui.QValidator.State.Intermediate),
        ("", QtGui.QValidator.State.Intermediate),
        ("__import__('os')", QtGui.QValidator.State.Intermediate),
    ],
)
def test_expression_validator(expression, expected):
    """The validator accepts valid expressions and rejects unsafe ones."""
    validator = ExpressionValidator()
    state, text, pos = validator.validate(expression, len(expression))
    assert state == expected
    assert text == expression


# ---------------------------------------------------------------------------
# ComboBoxDelegate
# ---------------------------------------------------------------------------


def test_combo_box_delegate_create_editor(qtbot):
    """createEditor returns a QComboBox populated with the choices."""
    delegate = ComboBoxDelegate(None, ["a", "b", "c"])
    editor = delegate.createEditor(None, None, QtCore.QModelIndex())
    qtbot.addWidget(editor)
    assert isinstance(editor, QtWidgets.QComboBox)
    assert editor.count() == 3
    assert editor.itemText(0) == "a"
    assert editor.itemText(2) == "c"


def test_combo_box_delegate_set_editor_data(qtbot, model):
    """setEditorData selects the item matching the current model value."""
    delegate = ComboBoxDelegate(None, ["X", "Y"])
    idx = model.add_node("X")
    param_idx = model.index(idx.row(), 1, model.parent(idx))
    editor = delegate.createEditor(None, None, param_idx)
    delegate.setEditorData(editor, param_idx)
    assert editor.currentIndex() == 0


def test_combo_box_delegate_set_model_data(qtbot, model):
    """setModelData writes the chosen text back to the model."""
    delegate = ComboBoxDelegate(None, ["X", "Y"])
    idx = model.add_node("X")
    param_idx = model.index(idx.row(), 1, model.parent(idx))
    editor = delegate.createEditor(None, None, param_idx)
    editor.setCurrentIndex(1)
    delegate.setModelData(editor, model, param_idx)
    assert idx.internalPointer().parameter == "Y"


# ---------------------------------------------------------------------------
# LineEditDelegate
# ---------------------------------------------------------------------------


def test_line_edit_delegate_create_editor(qtbot):
    """createEditor returns a QLineEdit with an ExpressionValidator."""
    delegate = LineEditDelegate(None)
    editor = delegate.createEditor(None, None, QtCore.QModelIndex())
    qtbot.addWidget(editor)
    assert isinstance(editor, QtWidgets.QLineEdit)
    assert isinstance(editor.validator(), ExpressionValidator)


def test_line_edit_delegate_set_editor_data(qtbot, model):
    """setEditorData sets the line edit text from the model."""
    delegate = LineEditDelegate(None)
    idx = model.add_node("P1")
    expr_idx = model.index(idx.row(), 2, model.parent(idx))
    model.setData(expr_idx, "[1, 2, 3]")
    editor = delegate.createEditor(None, None, expr_idx)
    delegate.setEditorData(editor, expr_idx)
    assert editor.text() == "[1, 2, 3]"


def test_line_edit_delegate_set_model_data(qtbot, model):
    """setModelData writes the line edit text back to the model."""
    delegate = LineEditDelegate(None)
    idx = model.add_node("P1")
    expr_idx = model.index(idx.row(), 2, model.parent(idx))
    editor = delegate.createEditor(None, None, expr_idx)
    editor.setText("[1, 2]")
    delegate.setModelData(editor, model, expr_idx)
    assert idx.internalPointer().expression == "[1, 2]"


# ---------------------------------------------------------------------------
# SequencerTreeView
# ---------------------------------------------------------------------------


def test_tree_view_save(qtbot, populated_model):
    """save() forwards to the model's save method."""
    view = SequencerTreeView()
    qtbot.addWidget(view)
    view.setModel(populated_model)
    buf = StringIO()
    view.save(buf)
    assert "P1" in buf.getvalue()


def test_tree_view_select_row(qtbot, model):
    """selectRow selects every column of the given index."""
    view = SequencerTreeView()
    qtbot.addWidget(view)
    view.setModel(model)
    idx = model.add_node("P1")
    view.selectRow(idx)
    selection = view.selectionModel().selection().indexes()
    selected_columns = {i.column() for i in selection}
    assert selected_columns == {0, 1, 2}


def test_tree_view_activate_persistent_editor(qtbot, populated_model):
    """activate_persistent_editor runs without error over the tree."""
    view = SequencerTreeView()
    qtbot.addWidget(view)
    view.setModel(populated_model)
    view.activate_persistent_editor()


def test_tree_view_set_model(qtbot, model):
    """setModel configures column widths and connects signals."""
    view = SequencerTreeView()
    qtbot.addWidget(view)
    view.setModel(model)
    assert view.model() is model
    assert view.columnWidth(0) > 0


# ---------------------------------------------------------------------------
# SequenceDialog
# ---------------------------------------------------------------------------


def test_sequence_dialog_save_mode(qtbot):
    """The save-mode dialog uses AcceptSave and any-file mode."""
    dialog = SequenceDialog(save=True)
    qtbot.addWidget(dialog)
    assert dialog.acceptMode() == QtWidgets.QFileDialog.AcceptMode.AcceptSave
    assert dialog.fileMode() == QtWidgets.QFileDialog.FileMode.AnyFile
    assert not hasattr(dialog, "append_checkbox")


def test_sequence_dialog_load_mode(qtbot):
    """The load-mode dialog shows an append checkbox."""
    dialog = SequenceDialog(save=False)
    qtbot.addWidget(dialog)
    assert dialog.fileMode() == QtWidgets.QFileDialog.FileMode.ExistingFile
    assert hasattr(dialog, "append_checkbox")
    assert (dialog.append_checkbox.checkState()
            == QtCore.Qt.CheckState.Checked)


def test_sequence_dialog_update_preview(qtbot, tmp_path):
    """update_preview loads a file into the preview tree."""
    seq_file = tmp_path / "seq.txt"
    seq_file.write_text('- "X", "[1, 2]"\n')
    dialog = SequenceDialog(save=False)
    qtbot.addWidget(dialog)
    dialog.update_preview(str(seq_file))
    preview_model = dialog.preview_param.model()
    assert preview_model.rowCount(QtCore.QModelIndex()) == 1


def test_sequence_dialog_update_preview_ignores_directory(qtbot, tmp_path):
    """update_preview ignores directories and empty filenames."""
    dialog = SequenceDialog(save=False)
    qtbot.addWidget(dialog)
    # Should not raise for a directory or empty string
    dialog.update_preview(str(tmp_path))
    dialog.update_preview("")


# ---------------------------------------------------------------------------
# SequencerWidget
# ---------------------------------------------------------------------------


def test_sequencer_widget_init(parent_widget, qtbot):
    """SequencerWidget constructs with the configured inputs."""
    widget = SequencerWidget(inputs=["x", "y"], parent=parent_widget)
    qtbot.addWidget(widget)
    assert widget.names == {"x": "X", "y": "Y"}
    assert widget.names_inv == {"X": "x", "Y": "y"}
    assert widget.names_choices == ["X", "Y"]


def test_sequencer_widget_init_default_inputs(parent_widget, qtbot):
    """Without explicit inputs, the parent displays list is used."""
    parent_widget.displays = ["x"]
    widget = SequencerWidget(parent=parent_widget)
    qtbot.addWidget(widget)
    assert widget._inputs == ["x"]


def test_sequencer_widget_check_queue_signature_raises(qtbot):
    """An AttributeError is raised if queue lacks a procedure argument."""
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    parent.queue = _make_queue(signature_only_procedure=False)
    parent.procedure_class = lambda: _TestProcedure()
    parent.displays = ["x"]
    parent.make_procedure = lambda: _TestProcedure()
    with pytest.raises(AttributeError, match="procedure"):
        SequencerWidget(inputs=["x"], parent=parent)


def test_sequencer_widget_get_properties(parent_widget, qtbot):
    """_get_properties builds the name mapping for every input."""
    widget = SequencerWidget(inputs=["x", "y"], parent=parent_widget)
    qtbot.addWidget(widget)
    widget._get_properties()
    assert widget.names == {"x": "X", "y": "Y"}
    assert set(widget.names_choices) == {"X", "Y"}


def test_sequencer_widget_add_tree_item(parent_widget, qtbot):
    """_add_tree_item adds a root node selected in the view."""
    widget = SequencerWidget(inputs=["x", "y"], parent=parent_widget)
    qtbot.addWidget(widget)
    widget._add_tree_item(level=0)
    model = widget.tree.model()
    assert model.rowCount(QtCore.QModelIndex()) == 1
    selection = widget.tree.selectionModel().selection().indexes()
    assert len(selection) >= 1


def test_sequencer_widget_add_tree_item_with_parameter(parent_widget, qtbot):
    """_add_tree_item pre-fills the parameter if supplied."""
    widget = SequencerWidget(inputs=["x", "y"], parent=parent_widget)
    qtbot.addWidget(widget)
    widget._add_tree_item(level=0, parameter="Y")
    nodes = [n.internalPointer().parameter for n in widget.tree.model()]
    assert nodes == ["Y"]


def test_sequencer_widget_add_child_item(parent_widget, qtbot):
    """Adding an item with a selected parent creates a child node."""
    widget = SequencerWidget(inputs=["x", "y"], parent=parent_widget)
    qtbot.addWidget(widget)
    widget._add_tree_item(level=0)
    parent_index = next(iter(widget.tree.model()))
    widget.tree.selectRow(parent_index)
    widget._add_tree_item()
    nodes = [(n.internalPointer().parameter, n.internalPointer().level)
             for n in widget.tree.model()]
    assert nodes == [("X", 0), ("X", 1)]


def test_sequencer_widget_remove_selected_tree_item(parent_widget, qtbot):
    """_remove_selected_tree_item removes the selected node."""
    widget = SequencerWidget(inputs=["x", "y"], parent=parent_widget)
    qtbot.addWidget(widget)
    widget._add_tree_item(level=0)
    parent_index = next(iter(widget.tree.model()))
    widget.tree.selectRow(parent_index)
    widget._remove_selected_tree_item()
    assert widget.tree.model().rowCount(QtCore.QModelIndex()) == 0


def test_sequencer_widget_remove_no_selection(parent_widget, qtbot):
    """Removing without selection is a no-op."""
    widget = SequencerWidget(inputs=["x", "y"], parent=parent_widget)
    qtbot.addWidget(widget)
    widget._add_tree_item(level=0)
    widget.tree.selectionModel().clear()
    widget._remove_selected_tree_item()
    assert widget.tree.model().rowCount(QtCore.QModelIndex()) == 1


def test_sequencer_widget_get_sequence(parent_widget, qtbot):
    """get_sequence returns the parameter combinations."""
    widget = SequencerWidget(inputs=["x"], parent=parent_widget)
    qtbot.addWidget(widget)
    widget._add_tree_item(level=0, parameter="X")
    model = widget.tree.model()
    idx = next(iter(model))
    expr_idx = model.index(idx.row(), 2, model.parent(idx))
    model.setData(expr_idx, "[1, 2, 3]")
    sequence = widget.get_sequence()
    assert sequence == [({"x": 1},), ({"x": 2},), ({"x": 3},)]


def test_sequencer_widget_queue_sequence(parent_widget, qtbot):
    """queue_sequence calls parent.queue once per sequence entry."""
    widget = SequencerWidget(inputs=["x"], parent=parent_widget)
    qtbot.addWidget(widget)
    widget._add_tree_item(level=0, parameter="X")
    model = widget.tree.model()
    idx = next(iter(model))
    expr_idx = model.index(idx.row(), 2, model.parent(idx))
    model.setData(expr_idx, "[1, 2]")

    queued = []

    def fake_queue(procedure=None):
        queued.append(procedure)

    fake_queue.__signature__ = signature(lambda procedure=None: None)
    parent_widget.queue = fake_queue
    parent_widget.make_procedure = lambda: _TestProcedure()

    widget.queue_sequence()
    assert len(queued) == 2
    assert [p.x for p in queued] == [1, 2]


def test_sequencer_widget_queue_sequence_disabled_during_run(parent_widget,
                                                              qtbot):
    """The queue button is disabled and re-enabled around queueing."""
    widget = SequencerWidget(inputs=["x"], parent=parent_widget)
    qtbot.addWidget(widget)
    widget._add_tree_item(level=0, parameter="X")
    model = widget.tree.model()
    idx = next(iter(model))
    expr_idx = model.index(idx.row(), 2, model.parent(idx))
    model.setData(expr_idx, "[1]")

    set_states = []

    original_set_enabled = widget.queue_button.setEnabled

    def track_set_enabled(value):
        set_states.append(value)
        original_set_enabled(value)

    widget.queue_button.setEnabled = track_set_enabled

    def fake_queue(procedure=None):
        pass

    fake_queue.__signature__ = signature(lambda procedure=None: None)
    parent_widget.queue = fake_queue
    parent_widget.make_procedure = lambda: _TestProcedure()

    widget.queue_sequence()
    # Disabled (False) at start, re-enabled (True) at the end.
    assert set_states[0] is False
    assert set_states[-1] is True


def test_sequencer_widget_save_sequence(parent_widget, qtbot, tmp_path):
    """save_sequence writes the current tree to a file."""
    widget = SequencerWidget(inputs=["x"], parent=parent_widget)
    qtbot.addWidget(widget)
    widget._add_tree_item(level=0, parameter="X")
    model = widget.tree.model()
    idx = next(iter(model))
    expr_idx = model.index(idx.row(), 2, model.parent(idx))
    model.setData(expr_idx, "[1, 2]")

    out_file = tmp_path / "out.txt"

    def fake_exec(self):
        self.selectFile(str(out_file))
        return QtWidgets.QFileDialog.DialogCode.Accepted

    with mock.patch.object(QtWidgets.QFileDialog, "exec", fake_exec):
        widget.save_sequence()

    assert out_file.read_text() == '- "X", "[1, 2]"'


def test_sequencer_widget_load_sequence(parent_widget, qtbot, tmp_path):
    """load_sequence reads a file into the widget tree."""
    seq_file = tmp_path / "seq.txt"
    seq_file.write_text('- "X", "[1, 2, 3]"\n')

    widget = SequencerWidget(inputs=["x"], parent=parent_widget)
    qtbot.addWidget(widget)
    widget.load_sequence(filename=str(seq_file))
    sequence = widget.get_sequence()
    assert sequence == [({"x": 1},), ({"x": 2},), ({"x": 3},)]


def test_sequencer_widget_load_sequence_via_constructor(parent_widget, qtbot,
                                                       tmp_path):
    """A sequence_file passed to the constructor is loaded."""
    seq_file = tmp_path / "seq.txt"
    seq_file.write_text('- "X", "[1, 2]"\n')

    widget = SequencerWidget(inputs=["x"], sequence_file=str(seq_file),
                             parent=parent_widget)
    qtbot.addWidget(widget)
    assert widget.get_sequence() == [({"x": 1},), ({"x": 2},)]


def test_sequencer_widget_load_sequence_dialog(parent_widget, qtbot,
                                                tmp_path):
    """load_sequence without a filename opens a dialog."""
    seq_file = tmp_path / "seq.txt"
    seq_file.write_text('- "X", "[1]"\n')

    widget = SequencerWidget(inputs=["x"], parent=parent_widget)
    qtbot.addWidget(widget)

    def fake_exec(self):
        self.selectFile(str(seq_file))
        return QtWidgets.QFileDialog.DialogCode.Accepted

    with mock.patch.object(QtWidgets.QFileDialog, "exec", fake_exec):
        widget.load_sequence(filename=None)

    assert widget.get_sequence() == [({"x": 1},)]


def test_sequencer_widget_load_sequence_dialog_canceled(parent_widget, qtbot):
    """A canceled load dialog leaves the widget unchanged."""
    widget = SequencerWidget(inputs=["x"], parent=parent_widget)
    qtbot.addWidget(widget)
    with mock.patch.object(QtWidgets.QFileDialog, "exec",
                           return_value=QtWidgets.QFileDialog.DialogCode.Rejected):
        widget.load_sequence(filename=None)
    assert widget.get_sequence() == []
