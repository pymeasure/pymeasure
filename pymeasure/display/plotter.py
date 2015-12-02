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

from .qt_variant import QtCore, QtGui

from pymeasure.process import StoppableProcess
from .graph import ResultsCurve, Crosshairs, PlotFrame

import sys
from time import sleep
import pyqtgraph as pg


class PlotterWindow(QtGui.QMainWindow):

    def __init__(self, plotter, refresh_time=0.1, parent=None):
        super(PlotterWindow, self).__init__(parent)
        self.plotter = plotter

        self.setWindowTitle('Results Plotter')
        self.main = QtGui.QWidget(self)

        vbox = QtGui.QVBoxLayout(self.main)
        vbox.setSpacing(0)

        info_box = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setSpacing(6)
        hbox1.setContentsMargins(-1, 6, -1, -1)        

        file_label = QtGui.QLabel(self.main)
        file_label.setText('Data Filename:')

        self.file = QtGui.QLineEdit(self.main)
        self.file.setText(plotter.results.data_filename)

        hbox1.addWidget(file_label)
        hbox1.addWidget(self.file)
        info_box.addLayout(hbox1)

        hbox2 = QtGui.QHBoxLayout()
        hbox2.setSpacing(10)
        hbox2.setContentsMargins(-1, 6, -1, 6)

        columns_x_label = QtGui.QLabel(self.main)
        columns_x_label.setMaximumSize(QtCore.QSize(45, 16777215))
        columns_x_label.setText('X Axis:')
        columns_y_label = QtGui.QLabel(self.main)
        columns_y_label.setMaximumSize(QtCore.QSize(45, 16777215))
        columns_y_label.setText('Y Axis:')
        
        self.columns_x = QtGui.QComboBox(self.main)
        self.columns_y = QtGui.QComboBox(self.main)
        columns = plotter.results.procedure.DATA_COLUMNS
        for column in columns:
            self.columns_x.addItem(column)
            self.columns_y.addItem(column)
        self.columns_x.activated.connect(self.update_x_column)
        self.columns_y.activated.connect(self.update_y_column)

        hbox2.addWidget(columns_x_label)
        hbox2.addWidget(self.columns_x)
        hbox2.addWidget(columns_y_label)
        hbox2.addWidget(self.columns_y)
        info_box.addLayout(hbox2)
        vbox.addLayout(info_box)
        
        self.plot_frame = PlotFrame(columns[0], columns[1])
        self.plot = self.plot_frame.plot
        self.columns_x.setCurrentIndex(0)
        self.columns_y.setCurrentIndex(1)

        vbox.addWidget(self.plot_frame)

        self.main.setLayout(vbox)
        self.setCentralWidget(self.main)
        self.main.show()
        self.resize(800, 600)

        self.curve = ResultsCurve(plotter.results, columns[0], columns[1],
            pen=pg.mkPen(color=pg.intColor(0), width=2), antialias=False)
        self.plot.addItem(self.curve)

        self.plot_frame.updated.connect(self.check_stop)

    def quit(self, evt=None):
        log.info("Quitting the Plotter")
        self.close()
        self.plotter.stop()

    def update_x_column(self, index):
        axis = self.columns_x.itemText(index)
        self.plot_frame.change_x_axis(axis)

    def update_y_column(self, index):
        axis = self.columns_y.itemText(index)
        self.plot_frame.change_y_axis(axis)  

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
