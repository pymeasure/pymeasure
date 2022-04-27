"""
This example demonstrates how to make a graphical interface which contains an
image plotting tab, and uses a random number generator to simulate data so
that it does not require an instrument to use.

Run the program by changing to the directory containing this file and calling:

python image_gui.py
"""
from time import sleep
import sys

import numpy as np

from pymeasure.experiment import Results, unique_filename
from pymeasure.experiment import Procedure
from pymeasure.display.windows import ManagedImageWindow  # new ManagedWindow class
from pymeasure.experiment import FloatParameter
from pymeasure.display.Qt import QtGui

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TestImageProcedure(Procedure):

    # We will be using X and Y as coordinates for our images. We must have
    # parameters called X_start, X_end and X_step and similarly for Y. X and
    # Y can be replaced with other names, but the suffixes must remain.
    X_start = FloatParameter("X Start Position", units="m", default=0.)
    X_end = FloatParameter("X End Position", units="m", default=2.)
    X_step = FloatParameter("X Scan Step Size", units="m", default=0.1)
    Y_start = FloatParameter("Y Start Position", units="m", default=-1.)
    Y_end = FloatParameter("Y End Position", units="m", default=1.)
    Y_step = FloatParameter("Y Scan Step Size", units="m", default=0.1)

    delay = FloatParameter("Delay", units="s", default=0.01)

    # There must be two special data columns which correspond to the two things
    # which will act as coordinates for our image. If X and Y are changed
    # in the parameter names, their names must change in DATA_COLUMNS as well.
    DATA_COLUMNS = ["X", "Y", "pixel_data"]

    def startup(self):
        log.info("starting up...")

    def execute(self):
        xs = np.arange(self.X_start, self.X_end, self.X_step)
        ys = np.arange(self.Y_start, self.Y_end, self.Y_step)

        nprog = xs.size * ys.size
        progit = 0
        for x in xs:
            for y in ys:
                self.emit('progress', int(100 * progit / nprog))
                progit += 1
                self.emit("results", {
                    'X': x,
                    'Y': y,
                    'pixel_data': np.random.rand(1)[0]
                })
                sleep(self.delay)
                if self.should_stop():
                    break
            if self.should_stop():
                break

    def shutdown(self):
        log.info('shutting down')


class TestImageGUI(ManagedImageWindow):

    def __init__(self):
        # Note the new z axis. This can be changed in the GUI. the X and Y axes
        # must be the DATA_COLUMNS corresponding to our special parameters.
        super().__init__(
            procedure_class=TestImageProcedure,
            x_axis='X',
            y_axis='Y',
            z_axis='pixel_data',
            inputs=['X_start', 'X_end', 'X_step', 'Y_start', 'Y_end', 'Y_step',
                    'delay'],
            displays=['X_start', 'X_end', 'Y_start', 'Y_end', 'delay']
        )
        self.setWindowTitle('PyMeasure Image Test')

    def queue(self):
        direc = '.'
        filename = unique_filename(direc, 'test')
        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)
        self.manager.queue(experiment)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = TestImageGUI()
    window.show()
    sys.exit(app.exec_())
