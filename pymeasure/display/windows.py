#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import os
import pyqtgraph as pg

from .Qt import QtCore, QtGui
from .widgets import PlotWidget, BrowserWidget, InputsWidget, LogWidget, ResultsDialog
from .curves import ResultsCurve
from .browser import BrowserItem
from .manager import Manager, Experiment
from .log import LogHandler
from ..experiment.results import Results


class PlotterWindow(QtGui.QMainWindow):

    def __init__(self, plotter, refresh_time=0.1, parent=None):
        super(PlotterWindow, self).__init__(parent)
        self.plotter = plotter
        columns = plotter.results.procedure.DATA_COLUMNS

        self.setWindowTitle('Results Plotter')
        self.main = QtGui.QWidget(self)

        vbox = QtGui.QVBoxLayout(self.main)
        vbox.setSpacing(0)

        hbox1 = QtGui.QHBoxLayout()
        hbox1.setSpacing(6)
        hbox1.setContentsMargins(-1, 6, -1, -1)        

        file_label = QtGui.QLabel(self.main)
        file_label.setText('Data Filename:')

        self.file = QtGui.QLineEdit(self.main)
        self.file.setText(plotter.results.data_filename)

        hbox1.addWidget(file_label)
        hbox1.addWidget(self.file)
        vbox.addLayout(hbox1)

        self.plot_widget = PlotWidget(columns, check_status=False)
        self.plot = self.plot_widget.plot

        vbox.addWidget(self.plot_widget)

        self.main.setLayout(vbox)
        self.setCentralWidget(self.main)
        self.main.show()
        self.resize(800, 600)

        self.curve = ResultsCurve(plotter.results, columns[0], columns[1],
            pen=pg.mkPen(color=pg.intColor(0), width=2), antialias=False)
        self.plot.addItem(self.curve)

        self.plot_widget.updated.connect(self.check_stop)

    def quit(self, evt=None):
        log.info("Quitting the Plotter")
        self.close()
        self.plotter.stop()
    
    def check_stop(self):
        """ Checks if the Plotter should stop and exits the Qt main loop if so
        """
        if self.plotter.should_stop():
            QtCore.QCoreApplication.instance().quit()


class ManagedWindow(QtGui.QMainWindow):
    """ The ManagedWindow uses a Manager to control Workers in a Queue,
    and provides a simple interface. The queue method must be overwritten
    by a child class which is required to pass an Experiment containing the
    Results and Procedure to self.manager.queue.
    """
    EDITOR = 'gedit'

    def __init__(self, procedure_class, inputs=[], displays=[], x_axis=None, y_axis=None, log_channel='', log_level=logging.INFO, parent=None):
        super(ManagedWindow, self).__init__(parent=parent)
        app = QtCore.QCoreApplication.instance()
        app.aboutToQuit.connect(self.quit)
        self.procedure_class = procedure_class
        self.inputs = inputs
        self.displays = displays
        self.log = logging.getLogger(log_channel)
        self.log_level = log_level
        log.setLevel(log_level)
        self.log.setLevel(log_level)
        self.x_axis, self.y_axis = x_axis, y_axis
        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.log_widget = LogWidget()
        self.log.addHandler(self.log_widget.handler) # needs to be in Qt context?
        log.info("ManagedWindow connected to logging")

        self.queue_button = QtGui.QPushButton('Queue', self)
        self.queue_button.clicked.connect(self.queue)

        self.abort_button = QtGui.QPushButton('Abort', self)
        self.abort_button.setEnabled(False)
        self.abort_button.clicked.connect(self.abort)

        self.plot_widget = PlotWidget(self.procedure_class.DATA_COLUMNS, self.x_axis, self.y_axis)
        self.plot = self.plot_widget.plot

        self.browser_widget = BrowserWidget(
            self.procedure_class,
            self.displays, 
            [self.x_axis, self.y_axis],
            parent=self
        )
        self.browser_widget.show_button.clicked.connect(self.show_experiments)
        self.browser_widget.hide_button.clicked.connect(self.hide_experiments)
        self.browser_widget.clear_button.clicked.connect(self.clear_experiments)
        self.browser_widget.open_button.clicked.connect(self.open_experiment)
        self.browser = self.browser_widget.browser
        
        self.browser.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.browser.customContextMenuRequested.connect(self.browser_item_menu)
        self.browser.itemChanged.connect(self.browser_item_changed)

        self.inputs = InputsWidget(
            self.procedure_class,
            self.inputs,
            parent=self
        )

        self.manager = Manager(self.plot, self.browser, log_level=self.log_level, parent=self)
        self.manager.abort_returned.connect(self.abort_returned)
        self.manager.queued.connect(self.queued)
        self.manager.running.connect(self.running)
        self.manager.finished.connect(self.finished)
        self.manager.log.connect(self.log.handle)

    def _layout(self):
        self.main = QtGui.QWidget(self)

        inputs_dock = QtGui.QWidget(self)
        inputs_vbox = QtGui.QVBoxLayout(self.main)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        hbox.addWidget(self.queue_button)
        hbox.addWidget(self.abort_button)
        hbox.addStretch()

        inputs_vbox.addWidget(self.inputs)
        inputs_vbox.addLayout(hbox)
        inputs_vbox.addStretch()
        inputs_dock.setLayout(inputs_vbox)

        dock = QtGui.QDockWidget('Input Parameters')
        dock.setWidget(inputs_dock)
        dock.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)

        tabs = QtGui.QTabWidget(self.main)
        tabs.addTab(self.plot_widget, "Results Graph")
        tabs.addTab(self.log_widget, "Experiment Log")

        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(tabs)
        splitter.addWidget(self.browser_widget)
        self.plot_widget.setMinimumSize(100, 200)

        vbox = QtGui.QVBoxLayout(self.main)
        vbox.setSpacing(0)
        vbox.addWidget(splitter)

        self.main.setLayout(vbox)
        self.setCentralWidget(self.main)
        self.main.show()
        self.resize(1000, 800)

    def quit(self, evt=None):
        self.close()

    def browser_item_changed(self, item, column):
        if column == 0:
            state = item.checkState(0)
            experiment = self.manager.experiments.with_browser_item(item)
            if state == 0:
                self.plot.removeItem(experiment.curve)
            else:
                experiment.curve.x = self.plot_widget.plot_frame.x_axis
                experiment.curve.y = self.plot_widget.plot_frame.y_axis
                experiment.curve.update()
                self.plot.addItem(experiment.curve)

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
                if self.manager.running_experiment() == experiment: # Experiment running
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

    def remove_experiment(self, experiment):
        reply = QtGui.QMessageBox.question(self, 'Remove Graph',
            "Are you sure you want to remove the graph?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.manager.remove(experiment)

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

    def open_experiment(self):
        dialog = ResultsDialog(self.procedure_class.DATA_COLUMNS, self.x_axis, self.y_axis)
        if dialog.exec_():
            filenames = dialog.selectedFiles()
            for filename in map(str,filenames):
                if filename in self.manager.experiments:
                    QtGui.QMessageBox.warning(self, "Load Error", 
                            "The file %s cannot be opened twice." % os.path.basename(filename))   
                elif filename == '':
                    return
                else:
                    results = Results.load(filename)
                    experiment = self.new_experiment(results)
                    experiment.curve.update()
                    experiment.browser_item.progressbar.setValue(100.)
                    self.manager.load(experiment)
                    log.info('Opened data file %s' % filename)

    def change_color(self, experiment):
        color = QtGui.QColorDialog.getColor(
            initial=experiment.curve.opts['pen'].color(), parent=self)
        if color.isValid():
            pixelmap = QtGui.QPixmap(24, 24)
            pixelmap.fill(color)
            experiment.browser_item.setIcon(0, QtGui.QIcon(pixelmap))
            experiment.curve.setPen(pg.mkPen(color=color, width=2))

    def open_file_externally(self, filename):
        # TODO: Make this function OS-agnostic
        import subprocess
        proc = subprocess.Popen([self.EDITOR, filename])

    def make_procedure(self):
        if not isinstance(self.inputs, InputsWidget):
            raise Exception("ManagedWindow can not make a Procedure"
                            " without a InputsWidget type")
        return self.inputs.get_procedure()

    def new_curve(self, results, color=None, **kwargs):
        if color is None:
            color = pg.intColor(self.browser.topLevelItemCount() % 8)
        return self.plot_widget.new_curve(results, color=color, **kwargs)

    def new_experiment(self, results, curve=None):
        if curve is None:
            curve = self.new_curve(results)
        browser_item = BrowserItem(results, curve)
        return Experiment(results, curve, browser_item)

    def set_parameters(self, parameters):
        """ This method should be overwritten by the child class. The
        parameters argument is a dictionary of Parameter objects.
        The Parameters should overwrite the GUI values so that a user
        can click "Queue" to capture the same parameters.
        """
        if not isinstance(self.inputs, InputsWidget):
            raise Exception("ManagedWindow can not set parameters"
                            " without a InputsWidget")
        self.inputs.set_parameters(parameters)

    def queue(self):
        """ This method should be overwritten by the child class. The
        self.manager.queue method should be passed an Experiment object
        which contains the Results and Procedure to be run.
        """
        raise Exception("ManagedWindow child class does not implement queue method")

    def abort(self):
        self.abort_button.setEnabled(False)
        self.abort_button.setText("Resume")
        self.abort_button.clicked.disconnect()
        self.abort_button.clicked.connect(self.resume)
        try:
            self.manager.abort()
        except:
            log.error('Failed to abort experiment', exc_info=True)
            self.abort_button.setText("Abort")
            self.abort_button.clicked.disconnect()
            self.abort_button.clicked.connect(self.abort)

    def resume(self):
        self.abort_button.setText("Abort")
        self.abort_button.clicked.disconnect()
        self.abort_button.clicked.connect(self.abort)
        if self.manager.experiments.has_next():
            self.manager.resume()
        else:
            self.abort_button.setEnabled(False)

    def queued(self, experiment):
        self.abort_button.setEnabled(True)
        self.browser_widget.show_button.setEnabled(True)
        self.browser_widget.hide_button.setEnabled(True)
        self.browser_widget.clear_button.setEnabled(True)

    def running(self, experiment):
        self.browser_widget.clear_button.setEnabled(False)

    def abort_returned(self, experiment):
        if self.manager.experiments.has_next():
            self.abort_button.setText("Resume")
            self.abort_button.setEnabled(True)
        else:
            self.browser_widget.clear_button.setEnabled(True)

    def finished(self, experiment):
        if not self.manager.experiments.has_next():
            self.abort_button.setEnabled(False) 
            self.browser_widget.clear_button.setEnabled(True)