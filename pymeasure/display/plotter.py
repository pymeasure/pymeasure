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
Qt = QtCore.Qt

from pymeasure.process import StoppableProcess
from .graph import ResultsCurve, Crosshairs

import sys
from time import sleep
import pyqtgraph as pg


class PlotterWindow(QtGui.QMainWindow):

    label_style = {'font-size': '10pt', 'font-family': 'Arial', 'color': '#000000'}

    def __init__(self, plotter, parent=None):
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
        
        frame = QtGui.QFrame(self.main)
        frame.setAutoFillBackground(False)
        frame.setStyleSheet("background: #fff")
        frame.setFrameShape(QtGui.QFrame.StyledPanel)
        frame.setFrameShadow(QtGui.QFrame.Sunken)
        frame.setMidLineWidth(1)
        vbox2 = QtGui.QVBoxLayout(frame)

        self.plot_widget = pg.PlotWidget(frame, background='#ffffff')
        self.coordinates = QtGui.QLabel(frame)
        self.coordinates.setMinimumSize(QtCore.QSize(0, 20))
        self.coordinates.setStyleSheet("background: #fff")
        self.coordinates.setText("")
        self.coordinates.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)

        vbox2.addWidget(self.plot_widget)
        frame.setLayout(vbox2)
        vbox2.addWidget(self.coordinates)
        vbox.addWidget(frame)

        self.plot = self.plot_widget.getPlotItem()

        self.crosshairs = Crosshairs(self.plot, pen=pg.mkPen(color='#AAAAAA', 
                            style=Qt.DashLine))
        self.crosshairs.coordinates.connect(self.update_coordinates)

        self.main.setLayout(vbox)
        self.setCentralWidget(self.main)
        self.main.show()
        self.resize(800, 600)

        self.curve = ResultsCurve(plotter.results, columns[0], columns[1],
            pen=pg.mkPen(color=pg.intColor(0), width=2), antialias=False)
        self.plot.addItem(self.curve)

        self.plot.setLabel('bottom', columns[0], **self.label_style)
        self.plot.setLabel('left', columns[1], **self.label_style)  

        self.columns_x.setCurrentIndex(0)
        self.columns_y.setCurrentIndex(1)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.curve.update)
        self.timer.timeout.connect(self.crosshairs.update)
        self.timer.timeout.connect(self.check_stop)
        self.timer.start(plotter.refresh_time*1e3)

    def quit(self, evt=None):
        log.info("Quitting the Plotter")
        self.timer.stop()
        self.close()
        self.plotter.stop()

    def update_coordinates(self, x, y):
        label = "(%0.3f, %0.3f)"
        self.coordinates.setText(label % (x, y))

    def update_x_column(self, index):
        axis = self.columns_x.itemText(index)
        self.curve.x = axis
        # TODO parse units as: units='Oe'
        self.plot.setLabel('bottom', axis, **self.label_style)

    def update_y_column(self, index):
        axis = self.columns_y.itemText(index)
        self.curve.y = axis
        # TODO parse units as: units='Oe'
        self.plot.setLabel('left', axis, **self.label_style)  

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
        window = PlotterWindow(self)
        app.aboutToQuit.connect(window.quit)
        window.show()
        app.exec_()

    def wait_for_close(self, check_time=0.1):
        while not self.should_stop():
            sleep(check_time)
