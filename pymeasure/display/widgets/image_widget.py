#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

import pyqtgraph as pg
from ..curves import ResultsImage
from ..Qt import QtCore, QtGui
from .tab_widget import TabWidget
from .image_frame import ImageFrame

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ImageWidget(TabWidget, QtGui.QWidget):
    """ Extends the :class:`ImageFrame<pymeasure.display.widgets.image_frame.ImageFrame>`
    to allow different columns of the data to be dynamically chosen
    """

    def __init__(self, name, columns, x_axis, y_axis, z_axis=None, refresh_time=0.2,
                 check_status=True, parent=None):
        super().__init__(name, parent)
        self.columns = columns
        self.refresh_time = refresh_time
        self.check_status = check_status
        self.x_axis = x_axis
        self.y_axis = y_axis
        self._setup_ui()
        self._layout()
        if z_axis is not None:
            self.columns_z.setCurrentIndex(self.columns_z.findText(z_axis))
            self.image_frame.change_z_axis(z_axis)

    def _setup_ui(self):
        self.columns_z_label = QtGui.QLabel(self)
        self.columns_z_label.setMaximumSize(QtCore.QSize(45, 16777215))
        self.columns_z_label.setText('Z Axis:')

        self.columns_z = QtGui.QComboBox(self)
        for column in self.columns:
            self.columns_z.addItem(column)
        self.columns_z.activated.connect(self.update_z_column)

        self.image_frame = ImageFrame(
            self.x_axis,
            self.y_axis,
            self.columns[0],
            self.refresh_time,
            self.check_status
        )
        self.updated = self.image_frame.updated
        self.plot = self.image_frame.plot
        self.columns_z.setCurrentIndex(2)

    def _layout(self):
        vbox = QtGui.QVBoxLayout(self)
        vbox.setSpacing(0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        hbox.addWidget(self.columns_z_label)
        hbox.addWidget(self.columns_z)

        vbox.addLayout(hbox)
        vbox.addWidget(self.image_frame)
        self.setLayout(vbox)

    def sizeHint(self):
        return QtCore.QSize(300, 600)

    def new_curve(self, results, color=pg.intColor(0), **kwargs):
        """ Creates a new image """
        image = ResultsImage(results,
                             x=self.image_frame.x_axis,
                             y=self.image_frame.y_axis,
                             z=self.image_frame.z_axis
                             )
        return image

    def update_z_column(self, index):
        axis = self.columns_z.itemText(index)
        self.image_frame.change_z_axis(axis)

    def load(self, curve):
        curve.z = self.columns_z.currentText()
        curve.update_data()
        self.plot.addItem(curve)

    def remove(self, curve):
        self.plot.removeItem(curve)
