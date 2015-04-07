"""

This file is part of the PyMeasure package.

Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from pymeasure.experiment import Procedure

from os.path import basename

from qt_variant import QtCore, QtGui

class BrowserItem(QtGui.QTreeWidgetItem):

    def __init__(self, results, curve, parent=None):
        super(BrowserItem, self).__init__(parent)

        pixelmap = QtGui.QPixmap(24, 24)
        pixelmap.fill(curve.opts['pen'].color())
        self.setIcon(0, QtGui.QIcon(pixelmap))
        self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.setCheckState(0, 2)
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


class Browser(QtGui.QTreeWidget):

    def __init__(self, procedure_class, parameters, parent=None):
        super(Browser, self).__init__(parent)
        self.procedure_parameters = parameters
        self.procedure_class = procedure_class

        header_labels = ["Graph", "Filename", "Progress", "Status"]
        # Get the default parameters
        parameter_objects = procedure_class().parameterObjects()
        for parameter in parameters:
            if parameter in parameter_objects:
                header_labels.append(parameter_objects[parameter].name)
            else:
                raise Exception("Invalid parameter input for a Browser column")

        self.setColumnCount(len(header_labels))
        self.setHeaderLabels(header_labels)

        for i, width in enumerate([80, 140]):
            self.header().resizeSection(i, width)

    def add(self, experiment):
        if not isinstance(experiment.procedure, self.procedure_class):
            raise Exception("This ResultsBrowser only supports '%s' objects")

        item = experiment.browser_item
        parameters = experiment.procedure.parameterObjects()
        for i, column in enumerate(self.procedure_parameters):
            item.setText(i+4, str(parameters[column]))

        self.addTopLevelItem(item)
        self.setItemWidget(item, 2, item.progressbar)
        return item
