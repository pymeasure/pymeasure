#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""
This example demonstrates how to make a graphical interface, and uses
a random number generator to simulate data so that it does not require
an instrument to use.

Run the program by changing to the directory containing this file and calling:

python gui.py

"""

import sys
import random
from time import sleep
from PyQt5.QtCore import QLocale
from pyqtgraph.Qt import QtCore

from pymeasure.experiment import Procedure, IntegerParameter, Parameter, FloatParameter, \
      ListParameter, unique_filename, Metadata, Results
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow

import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())


class TestProcedure(Procedure):

    p_dutId = Parameter('DUT ID', default='NA', save=False)
    iterations = IntegerParameter('Loop Iterations', default=100)
    delay = FloatParameter('Delay Time', units='s', default=0.02)
    seed = Parameter('Random Seed', default='12345')
    param_set = ListParameter('Paramters to set', choices=['None', 'Group 1', 'Group 2'],
                              default='None', save=False)
    # Parameter group 1
    param_1_1 = IntegerParameter('Paramter 1.1', default=1, group_by={'param_set': 'Group 1'})
    # Parameter group 2
    param_2_1 = IntegerParameter('Paramter 2.1', default=2, group_by={'param_set': 'Group 2'})

    # Metadata
    m_dutId = Metadata('DUT_ID', default='')

    # a list defining the order and appearance of columns in our data file
    DATA_COLUMNS = ['Iteration', 'Random Number']

    def startup(self):
        log.info("Setting up random number generator")
        random.seed(self.seed)
        self.m_dutId = self.p_dutId

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
        super().__init__(
            procedure_class=TestProcedure,
            inputs=['p_dutId', 'iterations', 'delay', 'seed',
                    'param_set', 'param_1_1', 'param_2_1'],
            displays=['p_dutId', 'iterations', 'delay', 'seed'],
            x_axis='Iteration',
            y_axis='Random Number',
            enable_file_input=False
        )
        self.setWindowTitle('GUI Example')

    def queue(self):
        procedure = self.make_procedure()
        filename = unique_filename('Result', prefix='rnd_{DUT ID}_{Random Seed}_',
                                   procedure=procedure)
        procedure.data_filename = filename
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)
        self.manager.queue(experiment)


if __name__ == "__main__":
    # Fix for axis scaling (2 lines)
    # https://github.com/pyqtgraph/pyqtgraph/issues/756
    QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
        QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    # Fix to handle numeric fields, decimal dot is used
    # https://github.com/pymeasure/pymeasure/issues/602
    QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
