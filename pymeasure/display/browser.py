#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

import logging

from os.path import basename

from .Qt import QtCore, QtGui
from ..experiment import Procedure

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class BrowserItem(QtGui.QTreeWidgetItem):
    def __init__(self, results, curve, parent=None):
        super().__init__(parent)

        pixelmap = QtGui.QPixmap(24, 24)
        pixelmap.fill(curve.opts['pen'].color())
        self.setIcon(0, QtGui.QIcon(pixelmap))
        self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.setCheckState(0, QtCore.Qt.Checked)
        self.setText(1, basename(results.data_filename))

        self.setStatus(results.procedure.status)

        self.progressbar = QtGui.QProgressBar()
        self.progressbar.setRange(0, 100)
        self.progressbar.setValue(0)

    def setStatus(self, status):
        status_label = {
            Procedure.QUEUED: 'Queued', Procedure.RUNNING: 'Running',
            Procedure.FAILED: 'Failed', Procedure.ABORTED: 'Aborted',
            Procedure.FINISHED: 'Finished'}
        self.setText(3, status_label[status])

        if status == Procedure.FAILED or status == Procedure.ABORTED:
            # Set progress bar color to red
            return  # Commented this out
            self.progressbar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #AAAAAA;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: red;
            }
            """)

    def setProgress(self, progress):
        self.progressbar.setValue(progress)


class Browser(QtGui.QTreeWidget):
    """Graphical list view of :class:`Experiment<pymeasure.display.manager.Experiment>`
    objects allowing the user to view the status of queued Experiments as well as 
    loading and displaying data from previous runs.

    In order that different Experiments be displayed within the same Browser,
    they must have entries in `DATA_COLUMNS` corresponding to the
    `measured_quantities` of the Browser.
    """

    def __init__(self, procedure_class, display_parameters,
                 measured_quantities, sort_by_filename=False, parent=None):
        super().__init__(parent)
        self.display_parameters = display_parameters
        self.procedure_class = procedure_class
        self.measured_quantities = measured_quantities

        header_labels = ["Graph", "Filename", "Progress", "Status"]
        for parameter in self.display_parameters:
            header_labels.append(getattr(self.procedure_class, parameter).name)

        self.setColumnCount(len(header_labels))
        self.setHeaderLabels(header_labels)
        self.setSortingEnabled(True)
        if sort_by_filename:
            self.sortItems(1, QtCore.Qt.AscendingOrder)

        for i, width in enumerate([80, 140]):
            self.header().resizeSection(i, width)

    def add(self, experiment):
        """Add a :class:`Experiment<pymeasure.display.manager.Experiment>` object
        to the Browser. This function checks to make sure that the Experiment
        measures the appropriate quantities to warrant its inclusion, and then 
        adds a BrowserItem to the Browser, filling all relevant columns with 
        Parameter data.
        """
        experiment_parameters = experiment.procedure.parameter_objects()
        experiment_parameter_names = list(experiment_parameters.keys())

        for measured_quantity in self.measured_quantities:
            if measured_quantity not in experiment.procedure.DATA_COLUMNS:
                raise Exception("Procedure does not measure the"
                                " %s quantity." % measured_quantity)

        # Set the relevant fields within the BrowserItem if
        # that Parameter is implemented
        item = experiment.browser_item
        for i, column in enumerate(self.display_parameters):
            if column in experiment_parameter_names:
                item.setText(i + 4, str(experiment_parameters[column]))

        self.addTopLevelItem(item)
        self.setItemWidget(item, 2, item.progressbar)
        return item
