"""
This example demonstrates how to make a graphical interface, and uses
a random number generator to simulate data so that it does not require
an instrument to use. It also demonstrates the use of the additional optional
widgets, including the sequencer-widget and the instrument-widget.

Run the program by changing to the directory containing this file and calling:

python gui_widgets.py

"""

import sys
import random
import tempfile
from time import sleep

import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())

from pymeasure.experiment import Procedure, IntegerParameter, Parameter, \
    FloatParameter
from pymeasure.experiment import Results
from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import ManagedWindow
from pymeasure.instruments.mock import Mock as MockInstrument


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
            self.emit('progress', 100 * i / self.iterations)
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
            inputs=['iterations', 'delay', 'seed'],
            displays=['iterations', 'delay', 'seed'],
            x_axis='Iteration',
            y_axis='Random Number',
            sequencer=True,
            sequencer_inputs=['iterations', 'delay', 'seed'],
            sequence_file="sequencer_example_sequence.txt",
            inputs_in_scrollarea=True
        )
        self.setWindowTitle('GUI Example')

        self.add_instrument_widget(MockInstrument(),
                                   readings=["wave", "voltage"],
                                   settings=["time", "output_voltage"],
                                   )

    def queue(self, *, procedure=None):
        filename = tempfile.mktemp()

        if procedure is None:
            procedure = self.make_procedure()

        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
