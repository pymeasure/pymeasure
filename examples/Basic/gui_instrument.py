"""
This example demonstrates how to make a graphical interface, and uses
a random number generator to simulate data so that it does not require
an instrument to use. It also demonstrates the use of the sequencer module.

Run the program by changing to the directory containing this file and calling:

python gui_sequencer.py

"""

import sys
import random
import tempfile
from time import sleep

from pymeasure.experiment import Procedure, IntegerParameter, Parameter, \
    FloatParameter
from pymeasure.experiment import Results
from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import InstrumentControlWindow
from pymeasure.instruments.mock import Mock as MockInstrument

import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())




class MockInstrumentControlWindow(InstrumentControlWindow):

    def __init__(self):
        super(MockInstrumentControlWindow,self).__init__(MockInstrument(),
                                    measurements=["wave", "voltage"],
                                    controls=["time", "output_voltage"],
                                    settings=None,
                                    options=None,
                                    functions=["reset_time"])
        self.setWindowTitle('Instrument Control')

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MockInstrumentControlWindow()
    window.show()
    sys.exit(app.exec_())
