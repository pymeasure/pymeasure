"""
This example demonstrates how to make a command line interface with a
live-plotting interface, and uses a random number generator to simulate
data so that it does not require an instrument to use.

Run the program by changing to the directory containing this file and calling:

python script_plotter.py

"""

import random
import tempfile
from time import sleep

from pymeasure.log import console_log
from pymeasure.experiment import Procedure, IntegerParameter, Parameter, FloatParameter
from pymeasure.experiment import Results, Worker
from pymeasure.display import Plotter

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


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
            self.emit('progress', 100. * i / self.iterations)
            sleep(self.delay)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        log.info("Finished")


if __name__ == "__main__":

    scribe = console_log(log, level=logging.DEBUG)
    scribe.start()

    filename = tempfile.mktemp()
    log.info("Using data file: %s" % filename)

    procedure = TestProcedure()
    procedure.iterations = 200
    procedure.delay = 0.1
    log.info("Set up TestProcedure with %d iterations" % procedure.iterations)

    results = Results(procedure, filename)
    log.info("Set up Results")

    plotter = Plotter(results)
    plotter.start()

    worker = Worker(results, scribe.queue, log_level=logging.DEBUG)
    log.info("Created worker for TestProcedure")
    log.info("Starting worker...")
    worker.start()

    log.info("Joining with the worker in at most 20 min")
    worker.join(60 * 20)
    log.info("Waiting for Plotter to close")
    plotter.wait_for_close()
    log.info("Plotter closed")

    log.info("Stopping the logging")
    scribe.stop()
