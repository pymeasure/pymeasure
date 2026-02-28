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

import logging

import pyqtgraph as pg
import numpy as np
from ..curves import ResultsImage
from ..Qt import QtCore, QtWidgets, QtGui
from .tab_widget import TabWidget
from .image_frame import ImageFrame

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ImageWidget(TabWidget, QtWidgets.QWidget):
    """Extends the :class:`ImageFrame<pymeasure.display.widgets.image_frame.ImageFrame>`
    to allow different columns of the data to be dynamically chosen
    """

    def __init__(
        self,
        name,
        columns,
        x_axis,
        y_axis,
        z_axis=None,
        refresh_time=0.2,
        check_status=True,
        colormap="viridis",
        auto_level = True,
        lower_cmap_bound = -1,
        upper_cmap_bound = 1,
        force_reload=False,
        parent=None,
    ):
        super().__init__(name, parent)
        self.columns = columns
        self.refresh_time = refresh_time
        self.check_status = check_status
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.colormap = colormap
        self.auto_level = auto_level
        self.lower_cmap_bound = lower_cmap_bound
        self.upper_cmap_bound = upper_cmap_bound
        self._setup_ui()
        self._layout()
        if z_axis is not None:
            self.columns_z.setCurrentIndex(self.columns_z.findText(z_axis))
            self.image_frame.change_z_axis(z_axis)
        self.force_reload = force_reload

    def _setup_ui(self):
        self.columns_z_label = QtWidgets.QLabel(self)
        self.columns_z_label.setText("Z Axis:")

        self.columns_z = QtWidgets.QComboBox(self)
        for column in self.columns:
            self.columns_z.addItem(column)
        self.columns_z.currentIndexChanged.connect(self.update_z_column)

        list_of_maps = pg.colormap.listMaps()
        list_of_maps = sorted(list_of_maps, key=lambda x: x.swapcase())
        list_of_icons = [self._cmap_icon(cmap, 64, 16) for cmap in list_of_maps]
        self.colormaps_label = QtWidgets.QLabel(self)
        self.colormaps_label.setText("Colormap:")

        self.colormaps = QtWidgets.QComboBox(self)
        for icon, cmap in zip(list_of_icons, list_of_maps):
            self.colormaps.addItem(icon, cmap)
            self.colormaps.setIconSize(QtCore.QSize(64, 16))

        self.image_frame = ImageFrame(
            self.x_axis, self.y_axis, self.columns[0], self.refresh_time, self.check_status
        )
        self.plot = self.image_frame.plot
        self.colorbar = pg.ColorBarItem(
            colorMap=self.colormap,
            interactive=False,
            colorMapMenu=False,
        )
        self.image_frame.updated.connect(self._update_colorbar)
        self.colormaps.currentIndexChanged.connect(self.set_colormap)
        self.colormaps.setCurrentIndex(self.colormaps.findText(self.colormap))

        self.cmap_bounds_layout = QtWidgets.QHBoxLayout()
        self.lower_cmap_label = QtWidgets.QLabel("Lower bound")
        self.lower_cmap_sbox = QtWidgets.QDoubleSpinBox(
            value=self.lower_cmap_bound,
            minimum=-1000000,
            maximum=1000000
        )
        self.upper_cmap_label = QtWidgets.QLabel("Upper bound")
        self.upper_cmap_sbox = QtWidgets.QDoubleSpinBox(
            value=self.upper_cmap_bound,
            minimum=-1000000,
            maximum=1000000
        )
        
        self.cmap_bounds_layout.addWidget(self.lower_cmap_label)
        self.cmap_bounds_layout.addWidget(self.lower_cmap_sbox)
        self.cmap_bounds_layout.addWidget(self.upper_cmap_label)
        self.cmap_bounds_layout.addWidget(self.upper_cmap_sbox)
        self.cmap_bounds_widget = QtWidgets.QWidget()
        self.cmap_bounds_widget.setLayout(self.cmap_bounds_layout)
        self.cmap_bounds_widget.setVisible(False)
        self.lower_cmap_sbox.valueChanged.connect(self.on_cmap_bounds_change)
        self.upper_cmap_sbox.valueChanged.connect(self.on_cmap_bounds_change)
        
        self.auto_level_cbox = QtWidgets.QCheckBox("Auto level")
        self.auto_level_cbox.setChecked(self.auto_level)
        self.auto_level_cbox.toggled.connect(self.on_auto_level_change)
        

    def _cmap_icon(self, cmap: str, width: int, height: int) -> QtGui.QIcon:
        lut = pg.colormap.get(cmap).getLookupTable(nPts=width, alpha=True)
        gradient = np.tile(lut[np.newaxis, :, :], (height, 1, 1))
        gradient = np.ascontiguousarray(gradient, dtype=np.uint8)
        qimg = QtGui.QImage(
            gradient.data,
            gradient.shape[1],
            gradient.shape[0],
            gradient.strides[0],
            QtGui.QImage.Format.Format_RGBA8888)
        pixmap = QtGui.QPixmap.fromImage(qimg)
        return QtGui.QIcon(pixmap)

    def _layout(self):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(0)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        hbox.addWidget(self.columns_z_label)
        hbox.addWidget(self.columns_z)
        hbox.addWidget(self.colormaps_label)
        hbox.addWidget(self.colormaps)
        hbox.addWidget(self.auto_level_cbox)
        hbox.addWidget(self.cmap_bounds_widget)
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        hbox.addWidget(spacer)
        vbox.addLayout(hbox)
        vbox.addWidget(self.image_frame)
        self.setLayout(vbox)

    def sizeHint(self):
        return QtCore.QSize(300, 600)

    def new_curve(self, results, color=pg.intColor(0), **kwargs):
        """Creates a new image"""
        image = ResultsImage(
            results,
            wdg=self,
            x=self.image_frame.x_axis,
            y=self.image_frame.y_axis,
            z=self.image_frame.z_axis,
            colormap=self.colormap,
            auto_level=self.auto_level,
            lower_cmap_bound=self.lower_cmap_bound,
            upper_cmap_bound=self.upper_cmap_bound,
            force_reload=self.force_reload,
            **kwargs,
        )
        return image

    def on_auto_level_change(self, v: bool):
        self.cmap_bounds_widget.setVisible(not v)
        self.auto_level = v
        self.image_frame.update_curves(
            dynamic=False,
            auto_level = self.auto_level,
            lower_cmap_bound = self.lower_cmap_bound,
            upper_cmap_bound = self.upper_cmap_bound,
        )

    def on_cmap_bounds_change(self):
        self.lower_cmap_bound = self.lower_cmap_sbox.value()
        self.upper_cmap_bound = self.upper_cmap_sbox.value()
        self.image_frame.update_curves(
            dynamic=False,
            auto_level = self.auto_level,
            lower_cmap_bound = self.lower_cmap_bound,
            upper_cmap_bound = self.upper_cmap_bound,
        )

    def update_z_column(self, index):
        axis = self.columns_z.itemText(index)
        self.image_frame.change_z_axis(axis)
        self.colorbar.setLabel("right", text=axis)

    def set_colormap(self, index):
        self.colormap = self.colormaps.itemText(index)
        self.colorbar.setColorMap(self.colormap)

    def load(self, curve):
        curve.z = self.columns_z.currentText()
        curve.update_data()
        self.plot.addItem(curve)

    def remove(self, curve):
        self.plot.removeItem(curve)

    def _update_colorbar(self):
        """Updates the colorbar to match the current image"""
        for item in self.plot.items:
            if isinstance(item, ResultsImage):
                self.colorbar.setImageItem(item, insert_in=self.plot)
