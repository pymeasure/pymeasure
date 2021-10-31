#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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
from pymeasure.display.Qt import QtCore, QtGui
from pymeasure.display.treemodel import TreeModel
from pymeasure.experiment.sequencer import SequenceFileHandler, SequenceEvaluationException
from functools import partial
from inspect import signature
from logging import Handler
from collections import ChainMap

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class ComboBoxDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, owner, choices):
        super().__init__(owner)
        self.items = choices

    def paint(self, painter, option, index):
        # TODO: is needed ?
        #print ("paint", painter, option, index, index.internalPointer())
        super().paint(painter, option, index)

    def createEditor(self, parent, option, index):
        editor = QtGui.QComboBox(parent)
        editor.currentIndexChanged.connect(self.commit_editor)
        editor.addItems(self.items)
        return editor

    def commit_editor(self):
        editor = self.sender()
        self.commitData.emit(editor)

    def setEditorData(self, editor, index):
        value = index.data(QtCore.Qt.DisplayRole)
        num = self.items.index(value)
        editor.setCurrentIndex(num)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class ExpressionValidator(QtGui.QValidator):
    def validate(self, input_string, pos):
        return_value = QtGui.QValidator.Acceptable
        try:
            SequenceFileHandler.eval_string(input_string)
        except SequenceEvaluationException as e:
            return_value = QtGui.QValidator.Intermediate
        return return_value

class LineEditDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, owner):
        # TODO: is needed ?
        super().__init__(owner)

    def paint(self, painter, option, index):
        # TODO: is needed ?
        super().paint(painter, option, index)

    def createEditor(self, parent, option, index):
        editor = QtGui.QLineEdit(parent)
        editor.setValidator(ExpressionValidator())
        return editor

    def setEditorData(self, editor, index):
        value = index.data(QtCore.Qt.DisplayRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        value = editor.text()
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class TreeView(QtGui.QTreeView):
    def save(self, filename=None):
        self.model().save(filename)

    def _setup_ui(self):
        pass
        
class SequencerWidget(QtGui.QWidget):
    """
    Widget that allows to generate a sequence of measurements with varying
    parameters. Moreover, one can write a simple text file to easily load a
    sequence.

    Currently requires a queue function of the ManagedWindow to have a
    "procedure" argument.
    """

    MAXDEPTH = 10

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

        # Load the sequence file if supplied.
        if sequence_file is not None:
            self.load_sequence(fileName=sequence_file)

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
        self.tree = TreeView(self)
        self.tree.setHeaderHidden(False)
        width = self.tree.viewport().size().width()
        self.tree.setColumnWidth(0, int(0.7 * width))
        self.tree.setColumnWidth(1, int(0.9 * width))
        self.tree.setColumnWidth(2, int(0.9 * width))
        self.tree.setItemDelegateForColumn(1, ComboBoxDelegate(self, self.names_choices))
        self.tree.setItemDelegateForColumn(2, LineEditDelegate(self))
        self.add_root_item_btn = QtGui.QPushButton("Add root item")
        self.add_root_item_btn.clicked.connect(
            partial(self._add_tree_item, level=0)
        )

        self.add_tree_item_btn = QtGui.QPushButton("Add item")
        self.add_tree_item_btn.clicked.connect(self._add_tree_item)

        self.remove_tree_item_btn = QtGui.QPushButton("Remove item")
        self.remove_tree_item_btn.clicked.connect(self._remove_selected_tree_item)

        self.load_seq_button = QtGui.QPushButton("Load sequence")
        self.load_seq_button.clicked.connect(self.load_sequence)
        self.load_seq_button.setToolTip("Load a sequence from a file.")

        self.queue_button = QtGui.QPushButton("Queue sequence")
        self.queue_button.clicked.connect(self.queue_sequence)

    def _layout(self):
        btn_box = QtGui.QHBoxLayout()
        btn_box.addWidget(self.add_root_item_btn)
        btn_box.addWidget(self.add_tree_item_btn)
        btn_box.addWidget(self.remove_tree_item_btn)

        btn_box_2 = QtGui.QHBoxLayout()
        btn_box_2.addWidget(self.load_seq_button)
        btn_box_2.addWidget(self.queue_button)

        vbox = QtGui.QVBoxLayout(self)
        vbox.setSpacing(6)
        vbox.addWidget(self.tree)
        vbox.addLayout(btn_box)
        vbox.addLayout(btn_box_2)
        self.setLayout(vbox)

    def _add_tree_item(self, *, level=None, parameter=None, sequence=None):
        """
        Add an item to the sequence tree. An item will be added as a child
        to the selected (existing) item, except when level is given.

        :param level: An integer value determining the level at which an
            item is added. If level is 0, a root item will be added.

        :param parameter: If given, the parameter field is pre-filled
        :param sequence: If given, the sequence field is pre-filled
        """

        selected = self.tree.selectionModel().selection().indexes()

        if len(selected) >= 1 and level != 0:
            parent = selected[0]
        else:
            parent = None

        if parameter is None:
            parameter = self.names_choices[0]

        self.tree.model().add_node(parameter=parameter, parent=parent)

        self.tree.expandAll()
        return

        # Select new created row

        #for selected_item in selected:
        #    selected_item.setSelected(False)

        #item.setSelected(True)

        # Select parameter
        #if parameter is not None:
        #    idx = self.tree.itemWidget(item, 1).findText(parameter)
        #    self.tree.itemWidget(item, 1).setCurrentIndex(idx)
        #    if idx == -1:
        #        log.error(
        #            "Parameter '{}' not found while loading sequence".format(
        #                parameter) + ", probably mistyped."
        #        )

    def _remove_selected_tree_item(self):
        """
        Remove the selected item (and any child items) from the sequence tree.
        """

        selected = self.tree.selectionModel().selection().indexes()

        if len(selected) == 0:
            return

        self.tree.model().remove_node(selected[0])

        #for selected_item in self.tree.selectedItems():
        #    selected_item.setSelected(False)

        #parent.setSelected(True)

    def queue_sequence(self):
        """
        Obtain a list of parameters from the sequence tree, enter these into
        procedures, and queue these procedures.
        """

        self.queue_button.setEnabled(False)

        try:
            sequence = self.data.parameters_sequence(self.names_inv)
        except SequenceEvaluationException:
            log.error("Evaluation of one of the sequence strings went wrong, no sequence queued.")
        else:
            log.info(
                "Queuing %d measurements based on the entered sequences." % len(sequence)
            )

            for entry in sequence:
                QtGui.QApplication.processEvents()
                parameters = dict(ChainMap(*entry[::-1]))

                procedure = self._parent.make_procedure()
                procedure.set_parameters(parameters)
                self._parent.queue(procedure=procedure)

        finally:
            self.queue_button.setEnabled(True)

    def load_sequence(self, *, fileName=None):
        """
        Load a sequence from a .txt file.

        :param fileName: Filename (string) of the to-be-loaded file.
        """

        if fileName is None:
            fileName, _ = QtGui.QFileDialog.getOpenFileName(self, 'OpenFile')

        if len(fileName) == 0:
            return

        content = []

        self.data=SequenceFileHandler(open(fileName, "r"))
        self.tree_model = TreeModel(header=["Level", "Parameter", "Sequence"], data=self.data)
        self.tree.setModel(self.tree_model)
        self.tree.expandAll()

class AppDemo(QtGui.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sequencer Manager')
        self.resize(500, 700)

        self.treeView = TreeView()
        self.treeView.setHeaderHidden(False)
        data=SequenceFileHandler(open(sys.argv[1]))
        treeModel = TreeModel(header=["Level", "Parameter", "Sequence"], data=data)

        self.treeView.setModel(treeModel)
        self.treeView.expandAll()
        self.treeView.doubleClicked.connect(self.getValue)

        self.setCentralWidget(self.treeView)

    def getValue(self, val):
        row = val.row()
        column = val.column()
        print (val)
        print(val.data())
        print(val.row())
        print(val.column())
        if row == 0 and column == 0:
            self.treeView.save()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)        

    demo = AppDemo()
    demo.show()
    
    sys.exit(app.exec_())
