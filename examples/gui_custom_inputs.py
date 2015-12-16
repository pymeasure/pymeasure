import sys
import random
import tempfile
from time import sleep

import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())

from pymeasure.log import console_log
from pymeasure.experiment import Procedure, IntegerParameter, Parameter, FloatParameter
from pymeasure.experiment import Results
from pymeasure.display.Qt import QtGui, fromUi
from pymeasure.display.windows import ManagedWindow


class TestProcedure(Procedure):

    iterations = IntegerParameter('Loop Iterations', default=100)
    delay = FloatParameter('Delay Time', units='s', default=0.2)
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


class MainWindow(ManagedWindow):

    def __init__(self):
        super(MainWindow, self).__init__(
            procedure_class=TestProcedure,
            displays=['iterations', 'delay', 'seed'],
            x_axis='Iteration',
            y_axis='Random Number'
        )
        self.setWindowTitle('GUI Example')

    def _setup_ui(self):
        super(MainWindow, self)._setup_ui()
        self.inputs.hide()
        self.inputs = fromUi('gui_custom_inputs.ui')

    def queue(self):
        filename = tempfile.mktemp()

        procedure = TestProcedure()
        procedure.seed = str(self.inputs.seed.text())
        procedure.iterations = self.inputs.iterations.value()
        procedure.delay = self.inputs.delay.value()

        results = Results(procedure, filename)

        experiment = self.new_experiment(results)

        self.manager.queue(experiment)


if __name__ == "__main__":
    console_log(log, level=logging.INFO)
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())