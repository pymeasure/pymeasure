import sys
import random
import tempfile
from time import sleep
import pyqtgraph as pg

import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())

from pymeasure.log import console_log
from pymeasure.experiment import Procedure, IntegerParameter, Parameter, FloatParameter
from pymeasure.experiment import Results, Worker, unique_filename
from pymeasure.display.qt_variant import QtCore, QtGui
from pymeasure.display.manager import Manager, Experiment
from pymeasure.display.browser import Browser, BrowserItem
from pymeasure.display.graph import ResultsCurve, Crosshairs

console_log(log, level=logging.DEBUG)


class TestProcedure(Procedure):

    iterations = IntegerParameter('Loop Iterations', default=100)
    delay = FloatParameter('Delay Time', unit='s', default=0.2)
    seed = Parameter('Random Seed', default='12345')

    DATA_COLUMNS = ['Iteration', 'Random Number']

    def startup(self):
        log.info("Setting up random number generator")
        random.seed(self.seed)

    def execute(self):
        log.info("Starting to generate numbers")
        for i in range(self.iterations):
            data = {
                'Iteration': i,
                'Random Number': random.random()
            }
            log.debug("Produced numbers: %s" % data)
            self.emit('results', data)
            self.emit('progress', 100*i/self.iterations)
            sleep(self.delay)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        log.info("Finished")


class MainWindow(QtGui.QMainWindow):

    X_AXIS = 'Iteration'
    Y_AXIS = 'Random Number'

    def __init__(self):
        super(MainWindow, self).__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle('GUI Example')
        self.main = QtGui.QWidget(self)

        vbox = QtGui.QVBoxLayout(self.main)
        vbox.setSpacing(0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        self.queue_button = QtGui.QPushButton('Queue', self)
        self.queue_button.clicked.connect(self.queue)
        self.abort_button = QtGui.QPushButton('Abort', self)
        self.abort_button.setEnabled(False)
        self.abort_button.clicked.connect(self.abort)
        hbox.addWidget(self.queue_button)
        hbox.addWidget(self.abort_button)
        vbox.addLayout(hbox)

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
        label_style = {'font-size': '10pt', 'font-family': 'Arial', 'color': '#000000'}
        self.plot.setLabel('bottom', self.X_AXIS, **label_style)
        self.plot.setLabel('left', self.Y_AXIS, **label_style)

        self.crosshairs = Crosshairs(self.plot, pen=pg.mkPen(color='#AAAAAA', 
                            style=QtCore.Qt.DashLine))
        self.crosshairs.coordinates.connect(self.update_coordinates)

        columns = [
            'iterations', 'delay', 'seed'
        ]
        self.browser = Browser(TestProcedure, columns, [self.X_AXIS, self.Y_AXIS], parent=self.main)
        
        self.browser.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.browser.customContextMenuRequested.connect(self.on_curve_context)
        self.browser.itemChanged.connect(self.browser_item_changed)
        vbox.addWidget(self.browser)

        self.manager = Manager(self.plot, self.browser, parent=self)
        self.manager.abort_returned.connect(self.abort_returned)
        self.manager.queued.connect(self.queued)
        self.manager.running.connect(self.running)
        self.manager.finished.connect(self.finished)

        self.plot_timer = QtCore.QTimer()
        self.plot_timer.timeout.connect(self.update_curves)
        self.plot_timer.timeout.connect(self.crosshairs.update)
        self.plot_timer.start(250) # Update plot every 1/4 sec

        self.main.setLayout(vbox)
        self.setCentralWidget(self.main)
        self.main.show()
        self.resize(800, 600)

    def quit(self, evt=None):
        self.close()

    def update_coordinates(self, x, y):
        label = "(%0.3f, %0.3f)"
        self.coordinates.setText(label % (x, y))

    def update_curves(self):
        for item in self.plot.items:
            if isinstance(item, ResultsCurve):
                item.update()

    def browser_item_changed(self, item, column):
        if column == 0:
            state = item.checkState(0)
            experiment = self.manager.experiments.with_browser_item(item)
            if state == 0:
                self.plot.removeItem(experiment.curve)
            else:
                self.plot.addItem(experiment.curve)

    def queue(self):
        filename = tempfile.mktemp()

        procedure = TestProcedure()
        procedure.iterations = 20
        procedure.delay = 0.2

        results = Results(procedure, filename)

        color = pg.intColor(self.browser.topLevelItemCount() % 8)
        curve = ResultsCurve(results, x=self.X_AXIS, y=self.Y_AXIS, 
            pen=pg.mkPen(color=color, width=2), antialias=False)
        curve.setSymbol(None)
        curve.setSymbolBrush(None)

        browser_item = BrowserItem(results, curve)
        experiment = Experiment(results, curve, browser_item)

        self.manager.queue(experiment)

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


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    app.aboutToQuit.connect(window.quit)
    window.show()
    sys.exit(app.exec_())