#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure Developers
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
This example demonstrates how to make a graphical interface to preform
IV characteristic measurements. There are a two items that need to be 
changed for your system:

1) Correct the GPIB addresses in IVProcedure.startup for your instruments
2) Correct the directory to save files in MainWindow.queue

Run the program by changing to the directory containing this file and calling:

python iv.py

"""

import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())

import sys
import random
import tempfile
import pyqtgraph as pg
from time import sleep
import numpy as np

from pymeasure.instruments.keithley import Keithley2000
from pymeasure.instruments.yokogawa import Yokogawa7651
from pymeasure.instruments import Instrument
from pymeasure.log import console_log
from pymeasure.experiment import Results
from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Procedure, IntegerParameter, Parameter, FloatParameter
from pymeasure.experiment import unique_filename

class K2000(Keithley2000):
    """ Temporary fix for PyMeasure 0.4.1 """
    measure = Instrument.measurement(":read?", """""")
    voltage = measure
    current = measure

class IVProcedure(Procedure):

    max_current = FloatParameter('Maximum Current', units='mA', default=10)
    min_current = FloatParameter('Minimum Current', units='mA', default=-10)
    current_step = FloatParameter('Current Step', units='mA', default=0.1)
    delay = FloatParameter('Delay Time', units='ms', default=20)
    voltage_range = FloatParameter('Voltage Range', units='V', default=10)

    DATA_COLUMNS = ['Current (A)', 'Voltage (V)', 'Resistance (Ohm)']

    def startup(self):
        log.info("Setting up instruments")
        self.meter = K2000("GPIB::25")
        # Number of power line cycles (NPLC)
        # Medium = 1 NPLC, 20 ms
        self.meter.config_measure_voltage(self.voltage_range, nplc=1)
        
        self.source = Yokogawa7651("GPIB::4")
        self.source.config_current_source(self.max_current*1e-3)
        
        sleep(1)

    def execute(self):
        currents_up = np.arange(self.min_current, self.max_current, self.current_step)
        currents_down = np.arange(self.max_current, self.min_current, -self.current_step)
        currents = np.concatenate((currents_up, currents_down)) # Include the reverse
        currents *= 1e-3 # to mA from A
        steps = len(currents)
        
        log.info("Starting to sweep through current")
        for i, current in enumerate(currents):
            log.debug("Measuring current: %g mA" % current)
            self.source.current = current
            sleep(self.delay*1e-3)
            voltage = self.meter.voltage
            if abs(current) <= 1e-10:
                resistance = np.nan
            else:
                resistance = voltage/current
            data = {
                'Current (A)': current,
                'Voltage (V)': voltage,
                'Resistance (Ohm)': resistance
            }
            self.emit('results', data)
            self.emit('progress', 100.*i/steps)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        self.source.current = 0
        log.info("Finished")


class MainWindow(ManagedWindow):

    def __init__(self):
        super(MainWindow, self).__init__(
            procedure_class=IVProcedure,
            inputs=[
                'max_current', 'min_current', 'current_step',
                'delay', 'voltage_range'
            ],
            displays=[
                'max_current', 'min_current', 'current_step',
                'delay', 'voltage_range'
            ],
            x_axis='Current (A)',
            y_axis='Voltage (V)'
        )
        self.setWindowTitle('IV Measurement')

    def queue(self):
        directory = "./" # Change this to the desired directory
        filename = unique_filename(directory, prefix='IV')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())