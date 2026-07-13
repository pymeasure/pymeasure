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

from unittest import mock

import pandas as pd
import pyqtgraph as pg

from pymeasure.display.curves import ResultsCurve
from pymeasure.display.widgets.plot_widget import PlotWidget
from pymeasure.experiment import Procedure


class FakeResults:
    """Minimal Results mock suitable for ResultsCurve construction."""

    def __init__(self, data=None):
        self.procedure = mock.MagicMock(spec=Procedure)
        self.procedure.status = Procedure.RUNNING
        self.data = data if data is not None else pd.DataFrame({
            "Time (s)": [0.0, 1.0, 2.0],
            "Voltage (V)": [0.0, 1.0, 4.0],
        })

    def reload(self):
        pass


def _make_widget(qtbot, columns=None, **kwargs):
    if columns is None:
        columns = ["Time (s)", "Voltage (V)", "Current (A)"]
    wdg = PlotWidget("test", columns, **kwargs)
    qtbot.addWidget(wdg)
    return wdg


def test_init_stores_name_and_columns(qtbot):
    wdg = _make_widget(qtbot, columns=["A", "B"])
    assert wdg.name == "test"
    assert wdg.columns == ["A", "B"]
    assert wdg.refresh_time == 0.2
    assert wdg.check_status is True
    assert wdg.linewidth == 1


def test_init_populates_column_combos(qtbot):
    columns = ["A", "B", "C"]
    wdg = _make_widget(qtbot, columns=columns)
    assert wdg.columns_x.count() == 3
    assert wdg.columns_y.count() == 3
    assert wdg.columns_x.itemText(0) == "A"
    assert wdg.columns_y.itemText(1) == "B"
    assert wdg.columns_x.currentIndex() == 0
    assert wdg.columns_y.currentIndex() == 1


def test_init_with_x_and_y_axis(qtbot):
    wdg = _make_widget(qtbot, x_axis="Voltage (V)", y_axis="Current (A)")
    assert wdg.plot_frame.x_axis == "Voltage (V)"
    assert wdg.plot_frame.y_axis == "Current (A)"


def test_new_curve_returns_results_curve(qtbot):
    wdg = _make_widget(qtbot)
    results = FakeResults()
    curve = wdg.new_curve(results)
    assert isinstance(curve, ResultsCurve)
    assert curve.results is results
    assert curve.x == wdg.plot_frame.x_axis
    assert curve.y == wdg.plot_frame.y_axis


def test_update_x_column_changes_frame_x_axis(qtbot):
    wdg = _make_widget(qtbot)
    index = wdg.columns_x.findText("Voltage (V)")
    wdg.update_x_column(index)
    assert wdg.plot_frame.x_axis == "Voltage (V)"


def test_update_y_column_changes_frame_y_axis(qtbot):
    wdg = _make_widget(qtbot)
    index = wdg.columns_y.findText("Current (A)")
    wdg.update_y_column(index)
    assert wdg.plot_frame.y_axis == "Current (A)"


def test_load_adds_curve_to_plot(qtbot):
    wdg = _make_widget(qtbot)
    results = FakeResults()
    curve = wdg.new_curve(results)
    wdg.load(curve)
    assert curve in wdg.plot.items
    assert curve.x == wdg.columns_x.currentText()
    assert curve.y == wdg.columns_y.currentText()


def test_remove_removes_curve_from_plot(qtbot):
    wdg = _make_widget(qtbot)
    results = FakeResults()
    curve = wdg.new_curve(results)
    wdg.load(curve)
    assert curve in wdg.plot.items
    wdg.remove(curve)
    assert curve not in wdg.plot.items


def test_set_color_updates_curve_color(qtbot):
    wdg = _make_widget(qtbot)
    results = FakeResults()
    curve = wdg.new_curve(results)
    wdg.load(curve)
    new_color = pg.mkColor("blue")
    wdg.set_color(curve, new_color)
    assert curve.color == new_color


def test_clear_widget_removes_items(qtbot):
    wdg = _make_widget(qtbot)
    results = FakeResults()
    curve = wdg.new_curve(results)
    wdg.load(curve)
    assert curve in wdg.plot.items
    wdg.clear_widget()
    assert curve not in wdg.plot.items


def test_preview_widget_returns_plot_widget(qtbot):
    wdg = _make_widget(qtbot)
    preview = wdg.preview_widget()
    qtbot.addWidget(preview)
    assert isinstance(preview, PlotWidget)
    assert preview.name == "Plot preview"
    assert preview.columns == wdg.columns
    assert preview.plot_frame.x_axis == wdg.plot_frame.x_axis
    assert preview.plot_frame.y_axis == wdg.plot_frame.y_axis
