"""
This example demonstrates how to make a graphical interface, and uses
a random number generator to simulate data so that it does not require
an instrument to use.

Run the program by changing to the directory containing this file and calling:

python gui.py

"""

import sys
import random
import tempfile
from time import sleep,time_ns

from datetime import datetime, timedelta

from pymeasure.experiment import Procedure, IntegerParameter, Parameter, FloatParameter, unique_filename
from pymeasure.experiment import Routine
from pymeasure.experiment import Results
from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import ManagedWindow

import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())


class TestProcedure(Procedure):

    iterations = IntegerParameter('Loop Iterations', default=100)
    delay = FloatParameter('Delay Time', units='s', default=0.02)
    seed = Parameter('Random Seed', default='12345')

    DATA_COLUMNS = ['Iteration', 'Random Number']

    def startup(self):
        log.info("Setting up random number generator")
        random.seed(self.seed)

    def execute(self):
        log.info("Starting to generate numbers")
        iss = []
        tands = []
        for i in range(self.iterations):
            iss=i
            tands=random.random()
            log.debug("Produced numbers: %s" % tands)

            self.emit('progress', 100 * i / self.iterations)
            sleep(self.delay)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

            data = {
                'Iteration': iss,
                'Random Number': tands
            }
            self.emit('results', data)

    def get_estimates(self, sequence_length=None, sequence=None):
        """ Function that returns estimates for the EstimatorWidget. If this function
        is implemented (and does not return a NotImplementedError) the widget is
        automatically activated.

        The function is expected to return an int or float, or a list of tuples. If an int or
        float is returned, it should represent the duration in seconds.If a list of
        tuples is returned, each tuple containing two strings, a label and the estimate
        itself:
        estimates = [
            ("label 1", "estimate 1"),
            ("label 2", "estimate 2"),
        ]
        The length of the number of estimates is not limited but has to remain unchanged after
        initialisation. Note that also the label can be altered after initialisation.

        The keyword arguments `sequence_length` and `sequence` are optional and return
        (if asked for) the length of the current sequence (of the `SequencerWidget`) or
        the full sequence.

        """
        duration = self.iterations * self.delay

        """
        A simple implementation of the get_estimates function immediately returns the duration
        in seconds.
        """
        # return duration

        estimates = list()

        estimates.append(("Duration", "%d s" % int(duration)))
        estimates.append(("Number of lines", "%d" % int(self.iterations)))

        estimates.append(("Sequence length", str(sequence_length)))

        estimates.append(('Measurement finished at', str(datetime.now() + timedelta(
            seconds=duration))[:-7]))
        estimates.append(('Sequence finished at', str(datetime.now() + timedelta(
            seconds=duration * sequence_length))[:-7]))

        return estimates

    def shutdown(self):
        log.info("Finished")


class MainWindow(ManagedWindow):

    def __init__(self):
        super().__init__(
            procedure_class=TestProcedure,
            inputs=['iterations', 'delay', 'seed'],
            displays=['iterations', 'delay', 'seed'],
            x_axis='Iteration',
            y_axis='Random Number',
            sequencer=True,
            sequence_file="gui_sequencer_example_sequence.txt",
            analyzer=True,
            port=None
        )
        self.setWindowTitle('GUI Example')

    def queue(self, procedure=None):
        filename = unique_filename(r'G:\Shared drives\Kepler - Main (Internal)\Neal\testlog')

        if procedure is None:
            procedure = self.make_procedure()
        results = Results(procedure, filename, routine=Routine(), output_format='JSON')
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
