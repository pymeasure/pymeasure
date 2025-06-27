#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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
import logging
import os
from functools import partial
from inspect import signature
from collections import ChainMap

from ..Qt import QtCore, QtWidgets, QtGui
from ...experiment.sequencer import SequenceHandler, SequenceEvaluationError

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SequencerTreeModel(QtCore.QAbstractItemModel):
    """ Model for sequencer data

        :param header: List of string representing header data
        :param data: data associated with the model
        :param parent: A QWidget that QT will give ownership of this Widget to.
    """

    def __init__(self, data, header=("Level", "Parameter", "Sequence"), parent=None):
        super().__init__(parent)

        self.header = header
        self.root = data

    def add_node(self, parameter, parent=None):
        """ Add a row in the sequencer """
        if parent is None:
            parent = self.createIndex(-1, -1)

        idx = len(self.root.children(parent))
        parent_seq_item = parent.internalPointer()

        self.beginInsertRows(parent, idx, idx)
        seq_item, child_row = self.root.add_node(parameter, parent_seq_item)
        self.endInsertRows()
        return self.createIndex(child_row, 0, seq_item)

    def remove_node(self, index):
        """ Remove a row in the sequencer """

        children = self.rowCount(index)
        seq_item = index.internalPointer()
        # Remove children from last to first
        while (children > 0):
            child = children - 1
            children_seq_item = self.root.get_children(seq_item, child)
            self.remove_node(self.createIndex(child, 0, children_seq_item))
            children = self.rowCount(index)

        self.beginRemoveRows(index.parent(), index.row(), index.row())
        parent_seq_item, parent_row = self.root.remove_node(seq_item)
        self.endRemoveRows()
        return self.createIndex(parent_row, 0, parent_seq_item)

    def flags(self, index):
        """ Set the flags for the item at the given QModelIndex.

            Here, we just set all indexes to enabled, and selectable.
        """
        if not index.isValid():
            return_value = QtCore.Qt.ItemFlag.NoItemFlags
        else:
            return_value = QtCore.Qt.ItemFlag.ItemIsEnabled | \
                           QtCore.Qt.ItemFlag.ItemIsSelectable
            if index.column() >= 1:
                return_value |= QtCore.Qt.ItemFlag.ItemIsEditable
        return return_value

    def data(self, index, role):
        """ Return the data to display for the given index and the given role.

            This method should not be called directly.
            This method is called implicitly by the QTreeView that is
            displaying us, as the way of finding out what to display where.
        """
        if not index.isValid():
            return

        elif not role == QtCore.Qt.ItemDataRole.DisplayRole:
            return

        data = index.internalPointer()[index.column()]

        if not isinstance(data, QtCore.QObject):
            data = str(data)

        return data

    def index(self, row, col, parent):
        """ Return a QModelIndex instance pointing the row and column underneath the parent given.
            This method should not be called directly. This method is called implicitly by the
            QTreeView that is displaying us, as the way of finding out what to display where.
        """
        if not parent or not parent.isValid():
            parent_data = None
        else:
            parent_data = parent.internalPointer()

        seq_item = self.root.get_children(parent_data, row)
        child = seq_item
        if child is None:
            return QtCore.QModelIndex()
        index = self.createIndex(row, col, child)
        return index

    def parent(self, index=None):
        """ Return the index of the parent of a given index. If index is not supplied,
        return an invalid QModelIndex.

        :param index: QModelIndex optional.
        :return:
        """

        if not index or not index.isValid():
            return QtCore.QModelIndex()

        child = index.internalPointer()
        parent, parent_row = self.root.get_parent(child)

        if parent is None:
            return QtCore.QModelIndex()

        index = self.createIndex(parent_row, 0, parent)
        return index

    def rowCount(self, parent):
        """ Return the number of children of a given parent.

            If an invalid QModelIndex is supplied, return the number of children under the root.

        :param parent: QModelIndex
        """
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent = None
        else:
            parent = parent.internalPointer()

        rows = len(self.root.children(parent))
        return rows

    def columnCount(self, parent):
        """ Return the number of columns in the model header.

            The parent parameter exists only to support the signature of QAbstractItemModel.
        """
        return len(self.header)

    def headerData(self, section, orientation, role):
        """ Return the header data for the given section, orientation and role.

            This method should not be called directly.
            This method is called implicitly by the QTreeView that is displaying us,
            as the way of finding out what to display where.
        """
        if orientation == QtCore.Qt.Orientation.Horizontal and \
                role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self.header[section]

    def setData(self, index, value, role=QtCore.Qt.ItemDataRole.EditRole):
        return_value = False
        if role == QtCore.Qt.ItemDataRole.EditRole:
            return_value = self.root.set_data(index.internalPointer(),
                                              index.row(),
                                              index.column(),
                                              value)
            if return_value:
                self.dataChanged.emit(index, index, [role])
        return return_value

    def visit_tree(self, parent):
        """ Return a generator to enumerate all the nodes in the tree """
        parent_data = None
        if parent:
            parent_data = parent.internalPointer()

        for row, child in enumerate(self.root.children(parent_data)):
            node = self.index(row, 0, parent)
            if node.isValid():
                yield node
                yield from self.visit_tree(node)

    def __iter__(self):
        yield from self.visit_tree(None)

    def save(self, file_obj):
        self.root.save(file_obj)

    def load(self, file_obj, append=False):
        # Since we are loading new data, following Qt documentation,
        # we call beginResetModel to inform that any previous data reported
        # from the model is now invalid and has to be queried for again.
        # This also means that the current item and any selected items will become invalid.
        self.beginResetModel()
        try:
            self.root.load(file_obj, append=append)
        except SequenceEvaluationError as e:
            log.error(f"Error during sequence loading: {e}")
        # Complete model reset operation
        self.endResetModel()


class ComboBoxDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, owner, choices):
        super().__init__(owner)
        self.items = choices

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QComboBox(parent)
        editor.addItems(self.items)
        return editor

    def setEditorData(self, editor, index):
        value = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
        num = self.items.index(value)
        editor.setCurrentIndex(num)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, QtCore.Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class ExpressionValidator(QtGui.QValidator):
    def validate(self, input_string, pos):
        return_value = QtGui.QValidator.State.Acceptable
        try:
            SequenceHandler.eval_string(input_string, log_enabled=False)
        except SequenceEvaluationError:
            return_value = QtGui.QValidator.State.Intermediate
        return (return_value, input_string, pos)


class LineEditDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QtWidgets.QLineEdit(parent)
        editor.setValidator(ExpressionValidator())
        return editor

    def setEditorData(self, editor, index):
        value = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        value = editor.text()
        model.setData(index, value, QtCore.Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class SequencerTreeView(QtWidgets.QTreeView):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.width = self.viewport().size().width()

    def save(self, filename=None):
        self.model().save(filename)

    def selectRow(self, index):
        selection_model = self.selectionModel()
        selection_model.select(index,
                               QtCore.QItemSelectionModel.SelectionFlag.Clear)
        for column in range(self.model().columnCount(index)):
            idx = self.model().createIndex(index.row(), column,
                                           index.internalPointer())
            selection_model.select(idx,
                                   QtCore.QItemSelectionModel.SelectionFlag.Select)

    def activate_persistent_editor(self):
        model = self.model()
        for item in model:
            index = model.index(item.row(), 1, model.parent(item))
            self.openPersistentEditor(index)

    def setModel(self, model):
        super().setModel(model)
        self.setColumnWidth(0, int(0.7 * self.width))
        self.setColumnWidth(1, int(0.9 * self.width))
        self.setColumnWidth(2, int(0.9 * self.width))
        self.model().layoutChanged.connect(self.activate_persistent_editor)
        self.model().modelReset.connect(self.activate_persistent_editor)


class SequenceDialog(QtWidgets.QFileDialog):
    """
    Widget that displays a dialog box for loading or saving a sequence tree.

    It also shows a preview of sequence tree in the dialog box

    :param save: True if we are saving a file. Default False.
    """

    def __init__(self, save=False, parent=None):
        """
        Generate a serialized form of the sequence tree

        :param save: True if we are saving a file. Default False.
        :param parent: Passed on to QtWidgets.QWidget. Default is None
        """
        super().__init__(parent)
        self.save = save
        self.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
        self._setup_ui()

    def _setup_ui(self):
        preview_tab = QtWidgets.QTabWidget()
        vbox = QtWidgets.QVBoxLayout()
        param_vbox = QtWidgets.QVBoxLayout()
        vbox_widget = QtWidgets.QWidget()
        param_vbox_widget = QtWidgets.QWidget()

        self.preview_param = SequencerTreeView(parent=self)
        triggers = QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        self.preview_param.setEditTriggers(triggers)
        param_vbox.addWidget(self.preview_param)
        vbox_widget.setLayout(vbox)
        param_vbox_widget.setLayout(param_vbox)
        preview_tab.addTab(param_vbox_widget, "Sequence Parameters")
        if not self.save:
            self.append_checkbox = QtWidgets.QCheckBox("Append to existing sequence")
            self.append_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
            self.layout().addWidget(self.append_checkbox)
            self.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        else:
            self.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptSave)
            self.setFileMode(QtWidgets.QFileDialog.FileMode.AnyFile)
        self.layout().addWidget(preview_tab, 0, 5, 4, 1)
        self.layout().setColumnStretch(5, 1)
        self.setMinimumSize(900, 500)
        self.resize(900, 500)
        self.currentChanged.connect(self.update_preview)

    def update_preview(self, filename):
        if not os.path.isdir(filename) and filename != '':
            with open(filename, 'r') as file_object:
                data = SequenceHandler(file_obj=file_object)
            tree_model = SequencerTreeModel(data=data)
            self.preview_param.setModel(tree_model)
            self.preview_param.expandAll()


class SequencerWidget(QtWidgets.QWidget):
    """
    Widget that allows to generate a sequence of measurements

    It allows sweeping parameters and moreover, one can write a simple text file to easily load a
    sequence. Sequences can also be saved

    Currently requires a queue function of the
    :class:`ManagedWindow<pymeasure.display.windows.managed_window.ManagedWindow>` to have a
    "procedure" argument.

    :param inputs: List of strings representing the parameters name
    """

    def __init__(self, inputs=None, sequence_file=None, parent=None):
        super().__init__(parent)
        self._parent = parent

        self._check_queue_signature()

        # if no explicit inputs are given, use the displayed parameters
        if inputs is not None:
            self._inputs = inputs
        else:
            self._inputs = self._parent.displays

        self._get_properties()
        self._setup_ui()
        self._layout()

        self.data = SequenceHandler(list(self.names_inv.keys()))
        self.tree.setModel(SequencerTreeModel(data=self.data))
        if sequence_file is not None:
            self.load_sequence(filename=sequence_file)

    def _check_queue_signature(self):
        """
        Check if the call signature of the implementation of the`ManagedWindow.queue`
        method accepts the `procedure` keyword argument, which is required for using
        the sequencer.
        """

        call_signature = signature(self._parent.queue)

        if 'procedure' not in call_signature.parameters:
            raise AttributeError(
                "The queue method of of the ManagedWindow does not accept the 'procedure'"
                "keyword argument. Accepting this keyword argument is required when using"
                "the 'SequencerWidget'."
            )

    def _get_properties(self):
        """
        Obtain the names of the input parameters.
        """

        parameter_objects = self._parent.procedure_class().parameter_objects()

        self.names = {key: parameter.name
                      for key, parameter
                      in parameter_objects.items()
                      if key in self._inputs}

        self.names_inv = {name: key for key, name in self.names.items()}
        self.names_choices = list(sorted(self.names_inv.keys()))

    def _setup_ui(self):
        self.tree = SequencerTreeView(self)
        self.tree.setHeaderHidden(False)
        self.tree.setItemDelegateForColumn(1, ComboBoxDelegate(self, self.names_choices))
        self.tree.setItemDelegateForColumn(2, LineEditDelegate(self))
        self.load_seq_button = QtWidgets.QPushButton("Load sequence")
        self.load_seq_button.clicked.connect(self.load_sequence)
        self.load_seq_button.setToolTip("Load a sequence from a file.")

        self.save_seq_button = QtWidgets.QPushButton("Save sequence")
        self.save_seq_button.clicked.connect(self.save_sequence)
        self.save_seq_button.setToolTip("Save a sequence to a file.")

        self.queue_button = QtWidgets.QPushButton("Queue sequence")
        self.queue_button.clicked.connect(self.queue_sequence)

        self.add_root_item_btn = QtWidgets.QPushButton("Add root item")
        self.add_root_item_btn.clicked.connect(
            partial(self._add_tree_item, level=0)
        )

        self.add_tree_item_btn = QtWidgets.QPushButton("Add item")
        self.add_tree_item_btn.clicked.connect(self._add_tree_item)

        self.remove_tree_item_btn = QtWidgets.QPushButton("Remove item")
        self.remove_tree_item_btn.clicked.connect(self._remove_selected_tree_item)

    def _layout(self):

        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addWidget(self.load_seq_button)
        btn_box.addWidget(self.save_seq_button)

        btn_box_2 = QtWidgets.QHBoxLayout()
        btn_box_2.addWidget(self.add_root_item_btn)
        btn_box_2.addWidget(self.add_tree_item_btn)
        btn_box_2.addWidget(self.remove_tree_item_btn)

        btn_box_3 = QtWidgets.QHBoxLayout()
        btn_box_3.addWidget(self.queue_button)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(6)
        vbox.addLayout(btn_box)
        vbox.addWidget(self.tree)
        vbox.addLayout(btn_box_2)
        vbox.addLayout(btn_box_3)
        self.setLayout(vbox)

    def _add_tree_item(self, *, level=None, parameter=None):
        """
        Add an item to the sequence tree. An item will be added as a child
        to the selected (existing) item, except when level is given.

        :param level: An integer value determining the level at which an
            item is added. If level is 0, a root item will be added.

        :param parameter: If given, the parameter field is pre-filled
        """

        selected = self.tree.selectionModel().selection().indexes()

        if len(selected) >= 1 and level != 0:
            parent = selected[0]
        else:
            parent = None

        if parameter is None:
            parameter = self.names_choices[0]

        model = self.tree.model()
        node_index = model.add_node(parameter=parameter, parent=parent)
        self.tree.openPersistentEditor(model.index(node_index.row(), 1, parent))
        self.tree.expandAll()

        self.tree.selectRow(node_index)

    def _remove_selected_tree_item(self):
        """
        Remove the selected item (and any child items) from the sequence tree.
        """

        selected = self.tree.selectionModel().selection().indexes()

        if len(selected) == 0:
            return

        node_index = self.tree.model().remove_node(selected[0])

        if node_index.isValid():
            self.tree.selectRow(node_index)

    def get_sequence(self):
        return self.data.parameters_sequence(self.names_inv)

    def queue_sequence(self):
        """
        Obtain a list of parameters from the sequence tree, enter these into
        procedures, and queue these procedures.
        """

        self.queue_button.setEnabled(False)

        try:
            sequence = self.get_sequence()
        except SequenceEvaluationError:
            log.error("Evaluation of one of the sequence strings went wrong, no sequence queued.")
        else:
            log.info(
                "Queuing %d measurements based on the entered sequences." % len(sequence)
            )

            for entry in sequence:
                QtWidgets.QApplication.processEvents()
                parameters = dict(ChainMap(*entry[::-1]))

                procedure = self._parent.make_procedure()
                procedure.set_parameters(parameters)
                self._parent.queue(procedure=procedure)

        finally:
            self.queue_button.setEnabled(True)

    def save_sequence(self):
        dialog = SequenceDialog(save=True)
        if dialog.exec():
            filename = dialog.selectedFiles()[0]
            with open(filename, 'w') as file_object:
                self.tree.save(file_object)
            log.info('Saved sequence file %s' % filename)

    def load_sequence(self, *, filename=None):
        """
        Load a sequence from a .txt file.

        :param filename: Filename (string) of the to-be-loaded file.
        """
        append_flag = False

        if (filename is None) or (filename == ''):
            dialog = SequenceDialog()
            if dialog.exec():
                append_flag = dialog.append_checkbox.checkState() == QtCore.Qt.CheckState.Checked
                filenames = dialog.selectedFiles()
                filename = filenames[0]
            else:
                return

        with open(filename, 'r') as file_object:
            self.tree.model().load(file_object, append=append_flag)
        self.tree.expandAll()
