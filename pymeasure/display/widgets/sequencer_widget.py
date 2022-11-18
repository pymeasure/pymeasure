#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

import re
from functools import partial
import numpy
from collections import ChainMap
from itertools import product
from inspect import signature

from ..Qt import QtWidgets

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

""" This defines a list of functions that can be used to generate a sequence. """
SAFE_FUNCTIONS = {
    'range': range,
    'sorted': sorted,
    'list': list,
    'arange': numpy.arange,
    'linspace': numpy.linspace,
    'arccos': numpy.arccos,
    'arcsin': numpy.arcsin,
    'arctan': numpy.arctan,
    'arctan2': numpy.arctan2,
    'ceil': numpy.ceil,
    'cos': numpy.cos,
    'cosh': numpy.cosh,
    'degrees': numpy.degrees,
    'e': numpy.e,
    'exp': numpy.exp,
    'fabs': numpy.fabs,
    'floor': numpy.floor,
    'fmod': numpy.fmod,
    'frexp': numpy.frexp,
    'hypot': numpy.hypot,
    'ldexp': numpy.ldexp,
    'log': numpy.log,
    'log10': numpy.log10,
    'modf': numpy.modf,
    'pi': numpy.pi,
    'power': numpy.power,
    'radians': numpy.radians,
    'sin': numpy.sin,
    'sinh': numpy.sinh,
    'sqrt': numpy.sqrt,
    'tan': numpy.tan,
    'tanh': numpy.tanh,
}


class SequenceEvaluationException(Exception):
    """Raised when the evaluation of a sequence string goes wrong."""
    pass


class SequencerTreeWidget(QtWidgets.QTreeWidget):
    """
    Widget that allows to generate a sequence of measurements with varying
    parameters. Moreover, one can write a simple text file to easily load a
    sequence.

    Currently requires a queue function of the
    :class:`ManagedWindow<pymeasure.display.windows.managed_window.ManagedWindow>` to have a
    "procedure" argument.
    """

    MAXDEPTH = 10

    def __init__(self, inputs=None, parameter_objects=None, parent=None):
        super().__init__(parent)
        self._parent = parent
        self.parameter_objects = parameter_objects
        self._inputs = inputs

        self._get_properties()
        self._setup_ui()

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
        self.names = {key: parameter.name
                      for key, parameter
                      in self.parameter_objects.items()
                      if key in self._inputs}

        self.names_inv = {name: key for key, name in self.names.items()}

    def _setup_ui(self):
        self.setHeaderLabels(["Level", "Parameter", "Sequence"])
        width = self.viewport().size().width()
        self.setColumnWidth(0, int(0.7 * width))
        self.setColumnWidth(1, int(0.9 * width))
        self.setColumnWidth(2, int(0.9 * width))

    def _layout(self):
        pass

    def _add_tree_item(self, *, level=None, parameter=None, sequence=None, preview=False):
        """
        Add an item to the sequence tree. An item will be added as a child
        to the selected (existing) item, except when level is given.

        :param level: An integer value determining the level at which an
            item is added. If level is 0, a root item will be added.

        :param parameter: If given, the parameter field is pre-filled
        :param sequence: If given, the sequence field is pre-filled
        """

        selected = self.selectedItems()

        if len(selected) >= 1 and level != 0:
            parent = selected[0]
        else:
            parent = self.invisibleRootItem()

        if level is not None and level > 0:
            p_depth = self._depth_of_child(parent)

            while p_depth > level - 1:
                parent = parent.parent()
                p_depth = self._depth_of_child(parent)

        comboBox = QtWidgets.QComboBox()
        lineEdit = QtWidgets.QLineEdit()

        comboBox.addItems(list(sorted(self.names_inv.keys())))

        item = QtWidgets.QTreeWidgetItem(parent, [""])
        depth = self._depth_of_child(item)
        item.setText(0, f"{depth:d}")

        if preview:
            paramLine = QtWidgets.QLineEdit()
            paramLine.setReadOnly(True)
            lineEdit.setReadOnly(True)
            self.setItemWidget(item, 1, paramLine)
        else:
            self.setItemWidget(item, 1, comboBox)

        self.setItemWidget(item, 2, lineEdit)

        self.expandAll()

        for selected_item in selected:
            selected_item.setSelected(False)

        if parameter is not None:
            idx = comboBox.findText(parameter)
            if preview:
                self.itemWidget(item, 1).setText(parameter)
            else:
                self.itemWidget(item, 1).setCurrentIndex(idx)
            if idx == -1:
                log.error(
                    "Parameter '{}' not found while loading sequence".format(
                        parameter) + ", probably mistyped."
                )

        if sequence is not None:
            self.itemWidget(item, 2).setText(sequence)

        item.setSelected(True)

    def _remove_selected_tree_item(self):
        """
        Remove the selected item (and any child items) from the sequence tree.
        """

        selected = self.selectedItems()
        if len(selected) == 0:
            return

        item = selected[0]
        parent = item.parent()

        if parent is None:
            parent = self.invisibleRootItem()

        parent.removeChild(item)

        for selected_item in self.selectedItems():
            selected_item.setSelected(False)

        parent.setSelected(True)

    def get_sequence_from_tree(self):
        """
        Generate a list of parameters from the sequence tree.
        """

        iterator = QtWidgets.QTreeWidgetItemIterator(self)
        current_sequence = [[] for _ in range(self.MAXDEPTH)]
        temp_sequence = [[] for _ in range(self.MAXDEPTH)]

        while iterator.value():
            item = iterator.value()
            depth = self._depth_of_child(item)

            name = self.itemWidget(item, 1).currentText()
            parameter = self.names_inv[name]
            values = self.eval_string(
                self.itemWidget(item, 2).text(),
                name, depth,
            )

            try:
                sequence_entry = [{parameter: value} for value in values]
            except TypeError:
                log.error(
                    "TypeError, likely no sequence for one of the parameters"
                )
            else:
                current_sequence[depth].extend(sequence_entry)

            iterator += 1
            next_depth = self._depth_of_child(iterator.value())

            for depth_idx in range(depth, next_depth, -1):
                temp_sequence[depth_idx].extend(current_sequence[depth_idx])

                if depth_idx != 0:
                    sequence_products = list(product(
                        current_sequence[depth_idx - 1],
                        temp_sequence[depth_idx]
                    ))

                    for i in range(len(sequence_products)):
                        try:
                            element = sequence_products[i][1]
                        except IndexError:
                            log.error(
                                "IndexError, likely empty nested parameter"
                            )
                        else:
                            if isinstance(element, tuple):
                                sequence_products[i] = (
                                    sequence_products[i][0], *element)

                    temp_sequence[depth_idx - 1].extend(sequence_products)
                    temp_sequence[depth_idx] = []

                current_sequence[depth_idx] = []
                current_sequence[depth_idx - 1] = []

            if depth == next_depth:
                temp_sequence[depth].extend(current_sequence[depth])
                current_sequence[depth] = []

        sequences = temp_sequence[0]

        for idx in range(len(sequences)):
            if not isinstance(sequences[idx], tuple):
                sequences[idx] = (sequences[idx],)

        return sequences

    @staticmethod
    def _depth_of_child(item):
        """
        Determine the level / depth of a child item in the sequence tree.
        """

        depth = -1
        while item:
            item = item.parent()
            depth += 1
        return depth

    @staticmethod
    def eval_string(string, name=None, depth=None):
        """
        Evaluate the given string. The string is evaluated using a list of
        pre-defined functions that are deemed safe to use, to prevent the
        execution of malicious code. For this purpose, also any built-in
        functions or global variables are not available.

        :param string: String to be interpreted.
        :param name: Name of the to-be-interpreted string, only used for
            error messages.
        :param depth: Depth of the to-be-interpreted string, only used
            for error messages.
        """

        evaluated_string = None
        if len(string) > 0:
            try:
                evaluated_string = eval(
                    string, {"__builtins__": None}, SAFE_FUNCTIONS
                )
            except TypeError:
                log.error("TypeError, likely a typo in one of the " +
                          "functions for parameter '{}', depth {}".format(
                              name, depth
                          ))
                raise SequenceEvaluationException()
            except SyntaxError:
                log.error("SyntaxError, likely unbalanced brackets " +
                          f"for parameter '{name}', depth {depth}")
                raise SequenceEvaluationException()
            except ValueError:
                log.error("ValueError, likely wrong function argument " +
                          f"for parameter '{name}', depth {depth}")
                raise SequenceEvaluationException()
        else:
            log.error("No sequence entered for " +
                      f"for parameter '{name}', depth {depth}")
            raise SequenceEvaluationException()

        evaluated_string = numpy.array(evaluated_string)
        return evaluated_string

    def load_sequence(self, *, filename=None, preview=False):
        """
        Load a sequence from a .txt file.

        :param fileName: Filename (string) of the to-be-loaded file.
        """
        if len(filename) == 0:
            return

        content = []

        with open(filename) as file:
            content = file.readlines()

        pattern = re.compile("([-]+) \"(.*?)\", \"(.*?)\"")
        for line in content:
            line = line.strip()
            match = pattern.search(line)

            if not match:
                continue

            level = len(match.group(1)) - 1

            if level < 0:
                continue

            parameter = match.group(2)
            sequence = match.group(3)

            self._add_tree_item(
                level=level,
                parameter=parameter,
                sequence=sequence,
                preview=preview
            )

    def recurse_tree(self, item, dashes='-'):
        """
        Recursive function to compile items in the sequence tree

        :param item: item from QTreeWidget tree
        :param dashes: add dash to indicate depth for serialization
        """
        child_count = item.childCount()
        if child_count:
            return [
                (dashes, self.itemWidget(item, 1).currentText(), self.itemWidget(item, 2).text()),
                [self.recurse_tree(item.child(i), dashes + '-') for i in range(child_count)]]
        else:
            return dashes, self.itemWidget(item, 1).currentText(), self.itemWidget(item, 2).text()

    def flatten(self, leaves):
        """
        Recursive function to flatten items in the sequence tree

        :param leaves: list of leaves to be flattened
        """
        for leaf in leaves:
            if isinstance(leaf, list):
                yield from self.flatten(leaf)
            else:
                yield leaf

    def serialize_tree(self):
        """
        Generate a serialized form of the sequence tree
        """
        invis_root = self.invisibleRootItem()
        roots = invis_root.childCount()
        leaves = [self.recurse_tree(invis_root.child(i)) for i in range(roots)]
        return self.flatten(leaves)


class SequenceDialog(QtWidgets.QFileDialog):
    """
    Widget that displays a dialog box for loading or saving a sequence tree.
    It shows a preview of sequence tree in the dialog box
    """

    def __init__(self, save=False, parent=None):
        """
        Generate a serialized form of the sequence tree

        :param save: True if we are saving a file. Default False.
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

        self.preview_param = SequencerTreeWidget(inputs=[],
                                                 parameter_objects={},
                                                 parent=self)
        param_vbox.addWidget(self.preview_param)
        vbox_widget.setLayout(vbox)
        param_vbox_widget.setLayout(param_vbox)
        preview_tab.addTab(param_vbox_widget, "Sequence Parameters")
        self.layout().addWidget(preview_tab, 0, 5, 4, 1)
        self.layout().setColumnStretch(5, 1)
        self.setMinimumSize(900, 500)
        self.resize(900, 500)
        if self.save:
            self.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
            self.setFileMode(QtWidgets.QFileDialog.FileMode.AnyFile)
        else:
            self.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)
        self.currentChanged.connect(self.update_preview)

    def update_preview(self, filename):
        if not os.path.isdir(filename) and filename != '':
            self.preview_param.clear()
            self.preview_param.load_sequence(filename=filename, preview=True)


class SequencerWidget(QtWidgets.QWidget):
    """
    Widget that allows to generate a sequence of measurements with varying
    parameters. Moreover, one can write a simple text file to easily load a
    sequence.

    Currently requires a queue function of the
    :class:`ManagedWindow<pymeasure.display.windows.managed_window.ManagedWindow>` to have a
    "procedure" argument.
    """

    def __init__(self, inputs=None, sequence_file=None, parent=None):
        super().__init__(parent)
        self._parent = parent

        self._check_queue_signature()
        self.parameter_objects = self._parent.procedure_class().parameter_objects()

        # if no explicit inputs are given, use the displayed parameters
        if inputs is not None:
            self._inputs = inputs
        else:
            self._inputs = self._parent.displays

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

    def _setup_ui(self):

        self.tree = SequencerTreeWidget(inputs=self._inputs,
                                        parameter_objects=self.parameter_objects, parent=self)

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
            partial(self.tree._add_tree_item, level=0)
        )

        self.add_tree_item_btn = QtWidgets.QPushButton("Add item")
        self.add_tree_item_btn.clicked.connect(self.tree._add_tree_item)

        self.remove_tree_item_btn = QtWidgets.QPushButton("Remove item")
        self.remove_tree_item_btn.clicked.connect(self.tree._remove_selected_tree_item)

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

    def queue_sequence(self):
        """
        Obtain a list of parameters from the sequence tree, enter these into
        procedures, and queue these procedures.
        """

        self.queue_button.setEnabled(False)

        try:
            sequence = self.tree.get_sequence_from_tree()
        except SequenceEvaluationException:
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
            items = self.tree.serialize_tree()
            with open(filename, 'w') as file:
                for i in items:
                    file.write(i[0] + ' "' + i[1] + '", "' + i[2] + "\"\n")
                log.info('Saved sequence file %s' % filename)

    def load_sequence(self):
        dialog = SequenceDialog()
        if dialog.exec():
            filenames = dialog.selectedFiles()
            for filename in map(str, filenames):
                if filename == '':
                    return
                else:
                    self.tree.load_sequence(filename=filename)
                    log.info('Loaded sequence file %s' % filename)
