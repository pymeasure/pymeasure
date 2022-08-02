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
import platform
import os

from ..browser import Browser
from ..Qt import QtCore, QtGui
from ..manager import Manager
from pymeasure.display.widgets.results_dialog import ResultsDialog
from pymeasure.experiment.results import Results

import subprocess

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class BrowserWidget(QtGui.QWidget):
    """
    Widget wrapper for :class:`Browser<pymeasure.display.browser.Browser>` class
    """
    def __init__(self, *args, parent=None):
        super().__init__(parent)
        self._parent = parent
        self.browser_args = args
        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.browser = Browser(*self.browser_args, parent=self)
        self.clear_button = QtGui.QPushButton('Clear all', self)
        self.clear_button.setEnabled(False)
        self.clear_unfinished_button = QtGui.QPushButton('Clear unfinished', self)
        self.clear_unfinished_button.setEnabled(False)
        self.hide_button = QtGui.QPushButton('Hide all', self)
        self.hide_button.setEnabled(False)
        self.show_button = QtGui.QPushButton('Show all', self)
        self.show_button.setEnabled(False)
        self.open_button = QtGui.QPushButton('Open', self)
        self.open_button.setEnabled(True)

        self.manager = Manager(self._parent.widget_list,
                               self.browser,
                               port=self._parent.port,
                               log_level=self._parent.log_level,
                               parent=self._parent)
        self.manager.abort_returned.connect(self.abort_returned)
        self.manager.queued.connect(self.queued)
        self.manager.running.connect(self.running)
        self.manager.finished.connect(self.finished)
        self.manager.failed.connect(self.failed)
        self.manager.log.connect(self._parent.log.handle)

        self.show_button.clicked.connect(self.show_experiments)
        self.hide_button.clicked.connect(self.hide_experiments)
        self.clear_button.clicked.connect(self.clear_experiments)
        self.clear_unfinished_button.clicked.connect(self.clear_unfinished)
        self.open_button.clicked.connect(self.open_experiment)

        self.browser.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.browser.itemChanged.connect(self.browser_item_changed)
        self.browser.customContextMenuRequested.connect(self.browser_item_menu)

    def _layout(self):
        vbox = QtGui.QVBoxLayout(self)
        vbox.setSpacing(0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        hbox.addWidget(self.show_button)
        hbox.addWidget(self.hide_button)
        hbox.addWidget(self.clear_button)
        hbox.addWidget(self.clear_unfinished_button)
        hbox.addStretch()
        hbox.addWidget(self.open_button)

        vbox.addLayout(hbox)
        vbox.addWidget(self.browser)
        self.setLayout(vbox)

    def browser_item_changed(self, item, column):
        if column == 0:
            state = item.checkState(0)
            experiment = self.manager.experiments.with_browser_item(item)
            if state == 0:
                for wdg, curve in zip(self._parent.widget_list, experiment.curve_list):
                    wdg.remove(curve)
            else:
                for wdg, curve in zip(self._parent.widget_list, experiment.curve_list):
                    wdg.load(curve)

        self.ensure_button_consistency()

    def ensure_button_consistency(self):
        pass

    def browser_item_menu(self, position):
        item = self.browser.itemAt(position)

        if item is not None:
            experiment = self.manager.experiments.with_browser_item(item)

            menu = QtGui.QMenu(self)

            # Open
            action_open = QtGui.QAction(menu)
            action_open.setText("Open Data Externally")
            action_open.triggered.connect(
                lambda: self.open_file_externally(experiment.results.data_filename))
            menu.addAction(action_open)

            # Change Color
            action_change_color = QtGui.QAction(menu)
            action_change_color.setText("Change Color")
            action_change_color.triggered.connect(
                lambda: self.change_color(experiment))
            menu.addAction(action_change_color)

            # Remove
            action_remove = QtGui.QAction(menu)
            action_remove.setText("Remove Graph")
            if self.manager.is_running():
                if self.manager.running_experiment() == experiment:  # Experiment running
                    action_remove.setEnabled(False)
            action_remove.triggered.connect(lambda: self.remove_experiment(experiment))
            menu.addAction(action_remove)

            # Use parameters
            action_use = QtGui.QAction(menu)
            action_use.setText("Use These Parameters")
            action_use.triggered.connect(
                lambda: self.set_parameters(experiment.procedure.parameter_objects()))
            menu.addAction(action_use)
            menu.exec_(self.browser.viewport().mapToGlobal(position))

    def change_color(self, experiment):
        color = QtGui.QColorDialog.getColor(
            parent=self)
        if color.isValid():
            pixelmap = QtGui.QPixmap(24, 24)
            pixelmap.fill(color)
            experiment.browser_item.setIcon(0, QtGui.QIcon(pixelmap))
            for wdg, curve in zip(self._parent.widget_list, experiment.curve_list):
                wdg.set_color(curve, color=color)

    def remove_experiment(self, experiment):
        reply = QtGui.QMessageBox.question(self, 'Remove Graph',
                                           "Are you sure you want to remove the graph?",
                                           QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.manager.remove(experiment)

    def open_file_externally(self, filename):
        """ Method to open the datafile using an external editor or viewer. Uses the default
        application to open a datafile of this filetype, but can be overridden by the child
        class in order to open the file in another application of choice.
        """
        system = platform.system()
        if (system == 'Windows'):
            # The empty argument after the start is needed to be able to cope
            # correctly with filenames with spaces
            _ = subprocess.Popen(['start', '', filename], shell=True)
        elif (system == 'Linux'):
            _ = subprocess.Popen(['xdg-open', filename])
        elif (system == 'Darwin'):
            _ = subprocess.Popen(['open', filename])
        else:
            raise Exception("{cls} method open_file_externally does not support {system} OS".format(
                cls=type(self).__name__, system=system))

    def show_experiments(self):
        root = self.browser.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            item.setCheckState(0, QtCore.Qt.Checked)

    def hide_experiments(self):
        root = self.browser.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            item.setCheckState(0, QtCore.Qt.Unchecked)

    def clear_experiments(self):
        self.manager.clear()

    def clear_unfinished(self):
        self.manager.clear_unfinished()
        self.clear_unfinished_button.setEnabled(False)
        current_abort_button_text = self._parent.abort_button.text()

        if current_abort_button_text == "Abort":
            pass
        elif current_abort_button_text == 'Resume':
            self._parent.abort_button.setEnabled(False)
        else:
            raise ValueError(f'got unexpected button text {current_abort_button_text}')



    def open_experiment(self):
        dialog = ResultsDialog(self._parent.procedure_class.DATA_COLUMNS, self.x_axis, self.y_axis)
        if dialog.exec_():
            filenames = dialog.selectedFiles()
            for filename in map(str, filenames):
                if filename in self.manager.experiments:
                    QtGui.QMessageBox.warning(
                        self, "Load Error",
                        "The file %s cannot be opened twice." % os.path.basename(filename)
                    )
                elif filename == '':
                    return
                else:
                    results = Results.load(filename)
                    experiment = self._parent.new_experiment(results)
                    for curve in experiment.curve_list:
                        if curve:
                            curve.update_data()
                    experiment.browser_item.progressbar.setValue(100.)
                    self.manager.load(experiment)
                    log.info('Opened data file %s' % filename)

    def abort(self):
        self._parent.abort_button.setEnabled(False)
        self._parent.abort_button.setText("Resume")
        self._parent.abort_button.clicked.disconnect()
        self._parent.abort_button.clicked.connect(self.resume)
        try:
            self.manager.abort()
        except:  # noqa
            log.error('Failed to abort experiment', exc_info=True)
            self._parent.abort_button.setText("Abort")
            self._parent.abort_button.clicked.disconnect()
            self._parent.abort_button.clicked.connect(self.abort)

    def resume(self):
        self._parent.abort_button.setText("Abort")
        self._parent.abort_button.clicked.disconnect()
        self._parent.abort_button.clicked.connect(self.abort)
        if self.manager.experiments.has_next():
            self.manager.resume()
        else:
            self._parent.abort_button.setEnabled(False)

    def queued(self, experiment):
        self._parent.abort_button.setEnabled(True)
        self.show_button.setEnabled(True)
        self.hide_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.clear_unfinished_button.setEnabled(True)

    def failed(self, experiment):
        self._parent.abort_button.setText("Resume")
        self._parent.abort_button.clicked.disconnect()
        self._parent.abort_button.clicked.connect(self.resume)
        self.clear_button.setEnabled(True)
        self.clear_unfinished_button.setEnabled(True)

    def running(self, experiment):
        self.clear_button.setEnabled(False)

    def abort_returned(self, experiment):
        if self.manager.experiments.has_next():
            self._parent.abort_button.setText("Resume")
            self._parent.abort_button.setEnabled(True)
            self.clear_unfinished_button.setEnabled(True)
        else:
            self.clear_button.setEnabled(True)
            self.clear_unfinished_button.setEnabled(True)

    def finished(self, experiment):

        if not self.manager.experiments.has_next():
            self._parent.abort_button.setEnabled(False)
            self.clear_button.setEnabled(True)
            self.clear_unfinished_button.setEnabled(False)