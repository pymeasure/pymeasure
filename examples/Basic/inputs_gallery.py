#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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
This is a gallery of all the available inputs in the package.

Run the program by changing to the directory containing this file and calling:

python gui.py

"""
import sys
import numpy as np

from pymeasure.experiment import (
    Procedure,
    IntegerParameter,
    Parameter,
    FloatParameter,
    BooleanParameter,
    ListParameter,
    VectorParameter,
)
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow

import logging

from pymeasure.experiment.parameters import PhysicalParameter, ParameterGroup, Range1DParameterGroup

log = logging.getLogger("")
log.addHandler(logging.NullHandler())

class TestProcedure(Procedure):
    float_param = FloatParameter("Float Parameter", units="s", default=0.2, step=0.01)
    int_param = IntegerParameter("Integer Parameter", units="A", default = 1, step=1)
    param = Parameter("Parameter", default = "text")
    bool_param = BooleanParameter("Boolean Parameter", default=True)
    list_param = ListParameter(
        "List Parameter", choices = ['Choice 1', 'Choice 2', 'Choice 3'], group_name="Test", default="Choice 1",
    )
    vector_param = VectorParameter(
        "Vector Parameter", default = [1,2,3], units = "m", group_name="Test"
    )
    #phys_param = PhysicalParameter("Physical Parameter",group_by="bool_param", default = [20,3])
    param_group = ParameterGroup("Test group",
                                 group_by={"bool_param": True},
                                 test1 = FloatParameter("test1", default=0),
                                 test2 = FloatParameter("test2", default=0)
                                 )
    wl_range = Range1DParameterGroup("Wavelength Range")
    
    
    DATA_COLUMNS = ["wavelength (nm)", "intensity (a.u.)"]

    def startup(self):
        pass
    
    def execute(self):
        for wl in self.wl_range:
            result = {"wavelength (nm)": wl,
                      "intensity (a.u)": np.random.rand()}
            self.emit("results", result)
    
    def shutdown(self):
        pass


class MainWindow(ManagedWindow):
    def __init__(self):
        inputs = ["float_param",
                  "int_param",
                  "param",
                  "bool_param",
                  "list_param",
                  "vector_param",
                  "param_group",
                  "wl_range",
                  ]
        super().__init__(
            procedure_class=TestProcedure,
            inputs= inputs,
            displays=["float_param"],
            x_axis="wavelength (nm)",
            y_axis="intensity (a.u.)",
        )
        self.setWindowTitle("GUI Example")
        self.plot_widget.selectors = ["wl_range"]

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
