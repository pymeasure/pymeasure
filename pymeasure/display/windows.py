#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands
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

import pyqtgraph as pg

from .Qt import QtCore, QtGui
from .widgets import PlotWidget
from .curves import ResultsCurve
from .browser import Browser, BrowserItem
from .manager import Manager, Experiment


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

        self.plot_widget = PlotWidget(columns)
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

    def __init__(self, procedure_class, browser_columns=[], x_axis=None, y_axis=None, parent=None):
        super(ManagedWindow, self).__init__(parent=parent)
        app = QtCore.QCoreApplication.instance()
        app.aboutToQuit.connect(self.quit)
        self.procedure_class = procedure_class
        self.browser_columns = browser_columns
        self.x_axis, self.y_axis = x_axis, y_axis
        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.queue_button = QtGui.QPushButton('Queue', self)
        self.queue_button.clicked.connect(self.queue)

        self.abort_button = QtGui.QPushButton('Abort', self)
        self.abort_button.setEnabled(False)
        self.abort_button.clicked.connect(self.abort)

        self.plot_widget = PlotWidget(self.procedure_class.DATA_COLUMNS, self.x_axis, self.y_axis)
        self.plot_widget.x_axis_changed.connect(self.x_axis_changed)
        self.plot_widget.y_axis_changed.connect(self.y_axis_changed)
        self.plot = self.plot_widget.plot

        self.browser = Browser(
            self.procedure_class,
            self.browser_columns, 
            [self.x_axis, self.y_axis],
            parent=self
        )
        
        self.browser.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.browser.customContextMenuRequested.connect(self.on_curve_context)
        self.browser.itemChanged.connect(self.browser_item_changed)

        self.manager = Manager(self.plot, self.browser, parent=self)
        self.manager.abort_returned.connect(self.abort_returned)
        self.manager.queued.connect(self.queued)
        self.manager.running.connect(self.running)
        self.manager.finished.connect(self.finished)

    def _layout(self):
        self.main = QtGui.QWidget(self)

        vbox = QtGui.QVBoxLayout(self.main)
        vbox.setSpacing(0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        hbox.addWidget(self.queue_button)
        hbox.addWidget(self.abort_button)
        vbox.addLayout(hbox)
        vbox.addWidget(self.plot_widget)
        vbox.addWidget(self.browser)

        self.main.setLayout(vbox)
        self.setCentralWidget(self.main)
        self.main.show()
        self.resize(800, 600)

    def x_axis_changed(self, axis):
        self.x_axis = axis

    def y_axis_changed(self, axis):
        self.y_axis = axis

    def quit(self, evt=None):
        self.close()

    def browser_item_changed(self, item, column):
        if column == 0:
            state = item.checkState(0)
            experiment = self.manager.experiments.with_browser_item(item)
            if state == 0:
                self.plot.removeItem(experiment.curve)
            else:
                self.plot.addItem(experiment.curve)

    def new_curve(self, results, color=None):
        if color is None:
            color = pg.intColor(self.browser.topLevelItemCount() % 8)
        curve = ResultsCurve(results, x=self.x_axis, y=self.y_axis, 
            pen=pg.mkPen(color=color, width=2), antialias=False)
        curve.setSymbol(None)
        curve.setSymbolBrush(None)
        return curve

    def new_experiment(self, results, curve=None):
        if curve is None:
            curve = self.new_curve(results)
        browser_item = BrowserItem(results, curve)
        return Experiment(results, curve, browser_item)

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

    def running(self, experiment):
        pass

    def abort_returned(self, experiment):
        if self.manager.experiments.has_next():
            self.abort_button.setText("Resume")
            self.abort_button.setEnabled(True)

    def finished(self, experiment):
        if not self.manager.experiments.has_next():
            self.abort_button.setEnabled(False) 