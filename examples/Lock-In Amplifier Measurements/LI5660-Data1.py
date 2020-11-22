from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os

import pyvisa
rm = pyvisa.ResourceManager()
instrument = rm.list_resources()
from pymeasure.instruments.nf import LI5660

class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.nf = LI5660(instrument[0])

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        # self.x = list(range(100))  # 100 time points
        # self.y = [randint(0,100) for _ in range(100)]  # 100 data points

        self.fetchData = self.nf.fetch_data

        self.x = [0, 0]
        self.y = [0, self.fetchData[0]]

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 10, 10))
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
        self.graphWidget.setYRange(min=0.324, max=0.335)

        # ... init continued ...
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        self.update_data = self.nf.fetch_data

        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 5e-9)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first 
        self.y.append(self.update_data[0])  # Add a new random value.
        print(self.update_data[0])

        self.data_line.setData(self.x, self.y)  # Update the data.


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())