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

from .qt_variant import QtCore, QtGui
Qt = QtCore.Qt
from pymeasure.process import StoppableProcess
from .graph import ResultsCurve, Crosshairs

import sys
import pyqtgraph as pg


class PlotterWindow(QtGui.QMainWindow):

    def __init__(self, plotter, parent=None):
        super(PlotterWindow, self).__init__(parent)
        self.plotter = plotter

        self.setWindowTitle('Results Plotter')
        self.main = QtGui.QWidget(self)
        self.setCentralWidget(self.main)

        self.plot_widget = pg.PlotWidget(self.main, background='#ffffff')

        self.coordinates = QtGui.QLabel(self.main)
        self.coordinates.setMinimumSize(QtCore.QSize(0, 20))

        self.plot = self.plot_widget.getPlotItem()
        label_style = {'font-size': '10pt', 'font-family': 'Arial', 'color': '#000000'}
        self.plot.setLabel('bottom', self.plotter.x, **label_style) # units='Oe'
        self.plot.setLabel('left', self.plotter.y, **label_style)
        self.crosshairs = Crosshairs(self.plot, pen=pg.mkPen(color='#AAAAAA', 
                            style=Qt.DashLine))
        self.crosshairs.coordinates.connect(self.update_coordinates)

        self.vbox = QtGui.QVBoxLayout(self)
        self.vbox.addWidget(self.plot_widget)
        self.vbox.addWidget(self.coordinates)
        self.main.setLayout(self.vbox)
        self.main.show()
        self.resize(800, 600)

        self.curve = ResultsCurve(plotter.results, plotter.x, plotter.y,
            plotter.xerr, plotter.yerr, pen=pg.mkPen(color=pg.intColor(0), width=2), antialias=False)
        self.plot.addItem(self.curve)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.curve.update)
        self.timer.timeout.connect(self.crosshairs.update)
        self.timer.timeout.connect(self.check_stop)
        self.timer.start(plotter.refresh_time*1e3)


    def update_coordinates(self, x, y):
        label = "(%0.3f, %0.3f)"
        self.coordinates.setText(label % (x, y))

    def check_stop(self):
        """ Checks if the Plotter should stop and exits the Qt main loop if so
        """
        if self.plotter.should_stop():
            QtCore.QCoreApplication.instance().quit()



class Plotter(StoppableProcess):
    """ Plotter dynamically plots data from a file through the Results
    object and supports error bars.
    """

    def __init__(self, results, x, y, xerr=None, yerr=None, refresh_time=0.1):
        super(Plotter, self).__init__()
        self.results = results
        self.x, self.y = x, y
        self.xerr, self.yerr = xerr, yerr
        # TODO: parse units from x and y strings
        self.refresh_time = refresh_time

    def run(self):
        app = QtGui.QApplication(sys.argv)
        window = PlotterWindow(self)
        window.show()
        app.exec_()

        
