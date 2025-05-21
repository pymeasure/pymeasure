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

import pyqtgraph as pg

from ..curves import ResultsCurve
from ..Qt import QtCore, QtWidgets
from ..widgets import (
    PlotWidget,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PlotterWindow(QtWidgets.QMainWindow):
    """
    A window for plotting experiment results. Should not be
    instantiated directly, but only via the
    :class:`~pymeasure.display.plotter.Plotter` class.

    .. seealso::
        Tutorial :ref:`tutorial-plotterwindow`
        A tutorial and example code for using the Plotter and PlotterWindow.
    .. attribute plot::
        The `pyqtgraph.PlotItem`_ object for this window. Can be
        accessed to further customise the plot view programmatically, e.g.,
        display log-log or semi-log axes by default, change axis range, etc.
    .. pyqtgraph.PlotItem: http://www.pyqtgraph.org/documentation/graphicsItems/plotitem.html
    """

    def __init__(self, plotter, refresh_time=0.1, linewidth=1, parent=None):
        super().__init__(parent)
        self.plotter = plotter
        self.refresh_time = refresh_time
        columns = plotter.results.procedure.DATA_COLUMNS

        self.setWindowTitle('Results Plotter')
        self.main = QtWidgets.QWidget(self)

        vbox = QtWidgets.QVBoxLayout(self.main)
        vbox.setSpacing(0)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(6)
        hbox.setContentsMargins(-1, 6, -1, -1)

        file_label = QtWidgets.QLabel(self.main)
        file_label.setText('Data Filename:')

        self.file = QtWidgets.QLineEdit(self.main)
        self.file.setText(plotter.results.data_filename)

        hbox.addWidget(file_label)
        hbox.addWidget(self.file)
        vbox.addLayout(hbox)

        self.plot_widget = PlotWidget("Plotter", columns, refresh_time=self.refresh_time,
                                      check_status=False, linewidth=linewidth)
        self.plot = self.plot_widget.plot

        vbox.addWidget(self.plot_widget)

        self.main.setLayout(vbox)
        self.setCentralWidget(self.main)
        self.main.show()
        self.resize(800, 600)

        self.curve = ResultsCurve(plotter.results, columns[0], columns[1],
                                  pen=pg.mkPen(color=pg.intColor(0), width=linewidth),
                                  antialias=False)
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
