#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

import pandas as pd
import pyqtgraph as pg

from pymeasure.display.curves import ResultsImage
from pymeasure.display.Qt import QtCore, QtWidgets
from pymeasure.display.widgets.image_widget import ImageWidget
from pymeasure.display.widgets.tab_widget import TabWidget


class _FakeProcedure:
    def __init__(self):
        for axis in ("x", "y", "z", "w"):
            setattr(self, f"{axis}_start", 0.0)
            setattr(self, f"{axis}_end", 2.0)
            setattr(self, f"{axis}_step", 1.0)


class _FakeResults:
    def __init__(self, data=None):
        self.procedure = _FakeProcedure()
        if data is None:
            data = pd.DataFrame({
                "x": [0.0, 1.0, 2.0],
                "y": [0.0, 0.0, 0.0],
                "z": [0.0, 0.5, 1.0],
                "w": [1.0, 0.5, 0.0],
            })
        self.data = data

    def reload(self):
        pass


COLUMNS = ["x", "y", "z", "w"]


def _make_widget(qtbot, z_axis=None):
    wdg = ImageWidget(
        "image",
        columns=COLUMNS,
        x_axis="x",
        y_axis="y",
        z_axis=z_axis,
    )
    qtbot.addWidget(wdg)
    return wdg


def test_init_stores_columns_and_axes(qtbot):
    wdg = _make_widget(qtbot)
    assert wdg.name == "image"
    assert wdg.columns == COLUMNS
    assert wdg.x_axis == "x"
    assert wdg.y_axis == "y"
    assert wdg.refresh_time == 0.2
    assert wdg.check_status is True


def test_init_is_tab_widget(qtbot):
    wdg = _make_widget(qtbot)
    assert isinstance(wdg, TabWidget)
    assert isinstance(wdg, QtWidgets.QWidget)


def test_init_with_z_axis_selects_column(qtbot):
    wdg = _make_widget(qtbot, z_axis="w")
    assert wdg.columns_z.currentText() == "w"
    assert wdg.image_frame.z_axis == "w"


def test_setup_ui_creates_components(qtbot):
    wdg = _make_widget(qtbot)
    assert isinstance(wdg.columns_z_label, QtWidgets.QLabel)
    assert wdg.columns_z_label.text() == "Z Axis:"
    assert isinstance(wdg.columns_z, QtWidgets.QComboBox)
    # columns_z is populated with all provided columns
    assert wdg.columns_z.count() == len(COLUMNS)
    for i, column in enumerate(COLUMNS):
        assert wdg.columns_z.itemText(i) == column
    assert isinstance(wdg.image_frame, type(wdg.image_frame))
    assert wdg.plot is wdg.image_frame.plot
    # `updated` attribute is wired to the image_frame's updated signal
    assert hasattr(wdg, "updated")


def test_layout_arranges_widgets(qtbot):
    wdg = _make_widget(qtbot)
    vbox = wdg.layout()
    assert isinstance(vbox, QtWidgets.QVBoxLayout)
    # the layout contains the hbox with label+combobox and the image frame
    assert vbox.count() == 2
    # First item is the horizontal box, second is the image frame widget
    hbox_item = vbox.itemAt(0)
    assert isinstance(hbox_item.layout(), QtWidgets.QHBoxLayout)
    assert vbox.itemAt(1).widget() is wdg.image_frame


def test_size_hint(qtbot):
    wdg = _make_widget(qtbot)
    hint = wdg.sizeHint()
    assert hint == QtCore.QSize(300, 600)


def test_new_curve_returns_results_image(qtbot):
    wdg = _make_widget(qtbot)
    results = _FakeResults()
    image = wdg.new_curve(results)
    assert isinstance(image, ResultsImage)
    assert image.results is results
    assert image.wdg is wdg
    assert image.x == wdg.image_frame.x_axis
    assert image.y == wdg.image_frame.y_axis
    assert image.z == wdg.image_frame.z_axis


def test_new_curve_uses_custom_color(qtbot):
    wdg = _make_widget(qtbot)
    results = _FakeResults()
    image = wdg.new_curve(results, color="#ff0000")
    assert isinstance(image, ResultsImage)


def test_update_z_column_changes_frame_z_axis(qtbot):
    wdg = _make_widget(qtbot)
    # find the index of "w" and trigger update
    index = wdg.columns_z.findText("w")
    received = []
    wdg.image_frame.z_axis_changed.connect(lambda axis: received.append(axis))

    wdg.update_z_column(index)

    assert wdg.image_frame.z_axis == "w"
    assert received == ["w"]


def test_update_z_column_via_combobox(qtbot):
    wdg = _make_widget(qtbot)
    received = []
    wdg.image_frame.z_axis_changed.connect(lambda axis: received.append(axis))

    wdg.columns_z.setCurrentIndex(wdg.columns_z.findText("w"))
    # combobox activated signal fires update_z_column
    wdg.columns_z.activated.emit(wdg.columns_z.currentIndex())

    assert wdg.image_frame.z_axis == "w"
    assert "w" in received


def test_load_adds_curve_to_plot(qtbot):
    wdg = _make_widget(qtbot)
    results = _FakeResults()
    image = wdg.new_curve(results)
    wdg.load(image)
    assert image in wdg.plot.items
    assert image.z == wdg.columns_z.currentText()


def test_remove_removes_curve_from_plot(qtbot):
    wdg = _make_widget(qtbot)
    results = _FakeResults()
    image = wdg.new_curve(results)
    wdg.load(image)
    assert image in wdg.plot.items

    wdg.remove(image)
    assert image not in wdg.plot.items


def test_remove_removes_plain_plot_item(qtbot):
    """remove works on any plot item that was added directly to the plot."""
    wdg = _make_widget(qtbot)
    item = pg.PlotDataItem()
    wdg.plot.addItem(item)
    assert item in wdg.plot.items

    wdg.remove(item)
    assert item not in wdg.plot.items
