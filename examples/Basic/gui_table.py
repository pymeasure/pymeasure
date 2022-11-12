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
from time import sleep
import PyQt5
from pymeasure.experiment import Procedure, IntegerParameter, Parameter, FloatParameter
from pymeasure.experiment import Results, unique_filename
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow
from pymeasure.display.widgets import TableWidget

import logging
log = logging.getLogger('')
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
            self.emit('progress', 100 * i / self.iterations)
            sleep(self.delay)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        log.info("Finished")

class ManagedWindowWithTable(ManagedWindow):
    def __init__(self, procedure_class, x_axis=None, y_axis=None, linewidth=1, **kwargs):
        self.table_widget = TableWidget("Experiment Table", procedure_class.DATA_COLUMNS, float_digits=3)
        if "widget_list" not in kwargs:
            kwargs["widget_list"] = ()
        kwargs["widget_list"] = kwargs["widget_list"] + (self.table_widget, )

        super().__init__(procedure_class, x_axis, y_axis, linewidth, **kwargs)

class MainWindow(ManagedWindowWithTable):

    def __init__(self):
        super().__init__(
            procedure_class=TestProcedure,
            inputs=['iterations', 'delay', 'seed'],
            displays=['iterations', 'delay', 'seed'],
            x_axis='Iteration',
            y_axis='Random Number'
        )
        self.setWindowTitle('GUI Example')

    def queue(self):
        direc = '.'
        filename = unique_filename(direc, 'gui_table')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)


if __name__ == "__main__":
    print (QtWidgets.QApplication)
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
