"""
This example demonstrates how to use an instrument from another library, here
InstrumentKit, in the pymeasure graphical interface.
It is a modification of the `gui.py` example: The `MainWindow` is the
same, the `TestProcedure` was adjusted to use an instrumentKit instrument
instead of a random number generator.

Run the program by changing to the directory containing this file and calling:

python gui_foreign_instrument.py
"""

import sys
import random
import tempfile
from time import sleep

from pymeasure.experiment import Procedure, IntegerParameter, FloatParameter
from pymeasure.experiment import Results
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow

# Import the InstrumentKit package
from instruments.thorlabs.pm100usb import PM100USB
import instruments.units as u

# For simulating communication
from io import BytesIO

import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())


class TestProcedure(Procedure):

    iterations = IntegerParameter('Loop Iterations', default=10, maximum=100)
    delay = FloatParameter('Delay Time', units='s', default=0.2)

    DATA_COLUMNS = ['Iteration', 'Power (W)']

    def startup(self):
        log.info("Setting up the power meter")
        # Open the test connection to the powermeter with some sample responses
        responses = ["POW"]
        responses.extend(f"{random.random()}" for i in range(100))
        communication = b"\n".join(item.encode() for item in responses)
        self.powermeter = PM100USB.open_test(BytesIO(communication))
        self.powermeter.cache_units = True
        # In order to connect to an actual device at COM Port 5, use instead:
        # self.powermeter = PM100USB.open_serial("COM5")

    def execute(self):
        log.info("Starting to measure the laser power")
        for i in range(self.iterations):
            data = {
                'Iteration': i,
                # Read the powermeter and store the sensor reading in Watts.
                'Power (W)': self.powermeter.read().m_as(u.W),
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
        super().__init__(
            procedure_class=TestProcedure,
            inputs=['iterations', 'delay'],
            displays=['iterations', 'delay'],
            x_axis='Iteration',
            y_axis='Power (W)',
        )
        self.setWindowTitle('GUI Example for Foreign Instrument')

    def queue(self):
        filename = tempfile.mktemp()

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
