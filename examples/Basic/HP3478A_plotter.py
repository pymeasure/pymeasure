#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example how to use a CLI script to get a plotter window with measurement 
data from the HP3478A.

(Based on script_plotter.py)
Run the program by changing to the directory containing this file and calling:

python HP3478A_plotter.py
"""
import tempfile
from time import sleep
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.log import console_log
from pymeasure.instruments.hp import HP3478A
from pymeasure.experiment import Procedure, IntegerParameter, Parameter, FloatParameter
from pymeasure.experiment import Results, Worker, unique_filename
from pymeasure.display import Plotter

class TestProcedure(Procedure):

    iterations = IntegerParameter('Loop Iterations', default=100)
    delay = FloatParameter('Delay Time', units='s', default=1)
    
    DATA_COLUMNS = ['Iteration', 'Resistance']

    def startup(self):
        log.info("Creating connection to HP3478A")
        self.meter=HP3478A('GPIB0::23')

    def execute(self):
        log.info("Starting to generate data")
        for i in range(self.iterations):
            data = {
                'Iteration': i,
                'Resistance': self.meter.measure(mode="R2W",digits=5)
            }
            log.debug("Produced numbers: %s" % data)
            self.emit('results', data)
            self.emit('progress', 100.*i/self.iterations)
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
    procedure.delay = 1
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
    worker.join(60*20)
    log.info("Waiting for Plotter to close")
    plotter.wait_for_close()
    log.info("Plotter closed")

    log.info("Stopping the logging")
    scribe.stop()



