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

from .Qt import QtCore, QtGui

from pymeasure.process import StoppableProcess
from .graph import ResultsCurve, Crosshairs, PlotWidget

import sys
from time import sleep
import pyqtgraph as pg


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



class Plotter(StoppableProcess):
    """ Plotter dynamically plots data from a file through the Results
    object and supports error bars.
    """

    def __init__(self, results, refresh_time=0.1):
        super(Plotter, self).__init__()
        self.results = results
        self.refresh_time = refresh_time

    def run(self):
        app = QtGui.QApplication(sys.argv)
        window = PlotterWindow(self, refresh_time=self.refresh_time)
        app.aboutToQuit.connect(window.quit)
        window.show()
        app.exec_()

    def wait_for_close(self, check_time=0.1):
        while not self.should_stop():
            sleep(check_time)
