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
from pymeasure.display.graph import ResultsCurve, Crosshairs, PlotFrame

console_log(log, level=logging.INFO)


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

        self.plot_frame = PlotFrame(self.X_AXIS, self.Y_AXIS)
        vbox.addWidget(self.plot_frame)

        columns = [
            'iterations', 'delay', 'seed'
        ]
        self.browser = Browser(TestProcedure, columns, [self.X_AXIS, self.Y_AXIS], parent=self.main)
        
        self.browser.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.browser.customContextMenuRequested.connect(self.on_curve_context)
        self.browser.itemChanged.connect(self.browser_item_changed)
        vbox.addWidget(self.browser)

        self.manager = Manager(self.plot_frame.plot, self.browser, parent=self)
        self.manager.abort_returned.connect(self.abort_returned)
        self.manager.queued.connect(self.queued)
        self.manager.running.connect(self.running)
        self.manager.finished.connect(self.finished)

        self.main.setLayout(vbox)
        self.setCentralWidget(self.main)
        self.main.show()
        self.resize(800, 600)

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

    def queue(self):
        filename = tempfile.mktemp()

        procedure = TestProcedure()
        procedure.iterations = 200
        procedure.delay = 0.1

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