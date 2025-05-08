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

from ..Qt import QtCore, QtWidgets
from ...experiment.results import Results

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ResultsDialog(QtWidgets.QFileDialog):
    """
    Widget that displays a dialog box for loading a past experiment run.
    It shows a preview of curves from the results file when selected in the dialog box.

    This widget used by the `open_experiment` method in
    :class:`ManagedWindowBase<pymeasure.display.windows.managed_window.ManagedWindowBase>` class
    """

    def __init__(self, procedure_class, widget_list=(), parent=None):
        super().__init__(parent)
        self.procedure_class = procedure_class
        self.widget_list = widget_list
        self.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
        self._setup_ui()

    def _setup_ui(self):
        preview_tab = QtWidgets.QTabWidget()
        param_vbox = QtWidgets.QVBoxLayout()
        metadata_vbox = QtWidgets.QVBoxLayout()
        param_vbox_widget = QtWidgets.QWidget()
        metadata_vbox_widget = QtWidgets.QWidget()

        self.preview_widget_list = []
        # Add preview tabs as appropriate
        for widget in self.widget_list:
            preview_widget = widget.preview_widget(parent=self)
            if preview_widget:
                self.preview_widget_list.append(preview_widget)
                vbox = QtWidgets.QVBoxLayout()
                vbox_widget = QtWidgets.QWidget()
                vbox.addWidget(preview_widget)
                vbox_widget.setLayout(vbox)
                preview_tab.addTab(vbox_widget, preview_widget.name)
        self.preview_param = QtWidgets.QTreeWidget()
        param_header = QtWidgets.QTreeWidgetItem(["Name", "Value"])
        self.preview_param.setHeaderItem(param_header)
        self.preview_param.setColumnWidth(0, 150)
        self.preview_param.setAlternatingRowColors(True)

        self.preview_metadata = QtWidgets.QTreeWidget()
        param_header = QtWidgets.QTreeWidgetItem(["Name", "Value"])
        self.preview_metadata.setHeaderItem(param_header)
        self.preview_metadata.setColumnWidth(0, 150)
        self.preview_metadata.setAlternatingRowColors(True)

        param_vbox.addWidget(self.preview_param)
        metadata_vbox.addWidget(self.preview_metadata)
        param_vbox_widget.setLayout(param_vbox)
        metadata_vbox_widget.setLayout(metadata_vbox)
        preview_tab.addTab(param_vbox_widget, "Run Parameters")
        preview_tab.addTab(metadata_vbox_widget, "Metadata")
        self.layout().addWidget(preview_tab, 0, 5, 4, 1)
        self.layout().setColumnStretch(5, 1)
        self.setMinimumSize(900, 500)
        self.resize(900, 500)

        self.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)
        self.currentChanged.connect(self.update_preview)

    def update_preview(self, filename):
        # Add preview tabs as appropriate
        if not os.path.isdir(filename) and filename != '':
            try:
                results = Results.load(str(filename))
            except ValueError:
                return
            except Exception as e:
                raise e
            for widget in self.preview_widget_list:
                widget.clear_widget()
                widget.load(widget.new_curve(results))

            self.preview_param.clear()
            for key, param in results.procedure.parameter_objects().items():
                new_item = QtWidgets.QTreeWidgetItem([param.name, str(param)])
                self.preview_param.addTopLevelItem(new_item)
            self.preview_param.sortItems(0, QtCore.Qt.SortOrder.AscendingOrder)

            self.preview_metadata.clear()
            for key, metadata in results.procedure.metadata_objects().items():
                new_item = QtWidgets.QTreeWidgetItem([metadata.name, str(metadata)])
                self.preview_metadata.addTopLevelItem(new_item)
            self.preview_metadata.sortItems(0, QtCore.Qt.SortOrder.AscendingOrder)
