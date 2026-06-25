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

import json
from os import path
from unittest import mock

import pandas as pd
from pyqtgraph.dockarea import Dock
from pyqtgraph.dockarea.Dock import DockLabel

from pymeasure.display.curves import ResultsCurve
from pymeasure.display.widgets.dock_widget import DockWidget
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


class TestProcedure(Procedure):
    __test__ = False
    DATA_COLUMNS = ["Time (s)", "Voltage (V)", "Current (A)"]


def _make_widget(qtbot, x_axis_labels=None, y_axis_labels=None, **kwargs):
    if x_axis_labels is None:
        x_axis_labels = ["Time (s)"]
    if y_axis_labels is None:
        y_axis_labels = ["Voltage (V)"]
    wdg = DockWidget(
        "test",
        TestProcedure,
        x_axis_labels=x_axis_labels,
        y_axis_labels=y_axis_labels,
        layout_path="/tmp/",
        layout_filename="test_dock_layout.json",
        **kwargs,
    )
    qtbot.addWidget(wdg)
    return wdg


def test_init_stores_attributes(qtbot):
    wdg = _make_widget(qtbot, linewidth=2)
    assert wdg.name == "test"
    assert wdg.procedure_class is TestProcedure
    assert wdg.x_axis_labels == ["Time (s)"]
    assert wdg.y_axis_labels == ["Voltage (V)"]
    assert wdg.num_plots == 1
    assert wdg.linewidth == 2
    assert wdg.dock_layout_filename == path.join("/tmp/", "test_dock_layout.json")


def test_init_default_filename_from_procedure(qtbot):
    wdg = DockWidget(
        "test",
        TestProcedure,
        x_axis_labels=["Time (s)"],
        y_axis_labels=["Voltage (V)"],
        layout_path="/tmp/",
    )
    qtbot.addWidget(wdg)
    assert wdg.dock_layout_filename == path.join(
        "/tmp/", TestProcedure.__name__ + "_dock_layout.json")


def test_init_multiple_plots(qtbot):
    wdg = _make_widget(
        qtbot,
        x_axis_labels=["Time (s)", "Time (s)"],
        y_axis_labels=["Voltage (V)", "Current (A)"],
    )
    assert wdg.num_plots == 2
    assert len(wdg.docks) == 2
    assert len(wdg.plot_frames) == 2


def test_setup_ui_creates_docks_and_plots(qtbot):
    wdg = _make_widget(qtbot)
    assert len(wdg.docks) == 1
    assert isinstance(wdg.docks[0], Dock)
    assert len(wdg.plot_frames) == 1
    assert isinstance(wdg.plot_frames[0], PlotWidget)


def test_layout_sets_layout(qtbot):
    wdg = _make_widget(qtbot)
    assert wdg.layout() is not None
    # DockArea should be a child of the widget
    assert wdg.dock_area.parent() is not None


def test_new_curve_returns_curves_list(qtbot):
    wdg = _make_widget(qtbot)
    results = FakeResults()
    curves = wdg.new_curve(results)
    assert isinstance(curves, list)
    assert len(curves) == wdg.num_plots
    assert all(isinstance(c, ResultsCurve) for c in curves)
    assert all(c.results is results for c in curves)


def test_new_curve_uses_linewidth(qtbot):
    wdg = _make_widget(qtbot, linewidth=3)
    results = FakeResults()
    curves = wdg.new_curve(results)
    assert curves[0].opts["pen"].width() == 3


def test_clear_removes_curves(qtbot):
    wdg = _make_widget(qtbot)
    results = FakeResults()
    curves = wdg.new_curve(results)
    for i, curve in enumerate(curves):
        wdg.plot_frames[i].load(curve)
        assert curve in wdg.plot_frames[i].plot.items
    wdg.clear()
    for i, curve in enumerate(curves):
        assert curve not in wdg.plot_frames[i].plot.items


def test_save_dock_layout_writes_file(qtbot, tmp_path):
    layout_filename = "test_save_layout.json"
    layout_path = str(tmp_path) + "/"
    wdg = DockWidget(
        "test",
        TestProcedure,
        x_axis_labels=["Time (s)"],
        y_axis_labels=["Voltage (V)"],
        layout_path=layout_path,
        layout_filename=layout_filename,
    )
    qtbot.addWidget(wdg)
    wdg.save_dock_layout()
    assert path.exists(wdg.dock_layout_filename)
    with open(wdg.dock_layout_filename) as f:
        layout = json.loads(f.read())
    assert "docks" in layout
    assert "plots" in layout
    assert len(layout["plots"]) == wdg.num_plots


def test_save_dock_action_returns_action(qtbot):
    wdg = _make_widget(qtbot)
    with mock.patch.object(wdg, "save_dock_layout") as mocked:
        action = wdg.save_dock_action()
        assert action.text() == "Save Dock Layout"
        action.trigger()
        mocked.assert_called_once()


def test_context_menu_event_shows_menu(qtbot):
    wdg = _make_widget(qtbot)
    event = mock.MagicMock()
    # childAt returns a DockLabel-like object to enter the menu branch
    dock_label = mock.MagicMock(spec=DockLabel)
    with mock.patch.object(DockWidget, "childAt", return_value=dock_label), \
         mock.patch.object(DockWidget, "mapToGlobal", return_value=mock.MagicMock()), \
         mock.patch("pymeasure.display.widgets.dock_widget.QtWidgets.QMenu") as MockMenu, \
         mock.patch.object(wdg, "save_dock_action", return_value=mock.MagicMock()):
        menu_instance = MockMenu.return_value
        wdg.contextMenuEvent(event)
        MockMenu.assert_called_once()
        menu_instance.addAction.assert_called_once()
        menu_instance.exec.assert_called_once()


def test_context_menu_event_no_menu_on_empty_area(qtbot):
    wdg = _make_widget(qtbot)
    event = mock.MagicMock()
    # childAt returns None - no menu shown
    with mock.patch.object(DockWidget, "childAt", return_value=None), \
         mock.patch("pymeasure.display.widgets.dock_widget.QtWidgets.QMenu") as MockMenu:
        wdg.contextMenuEvent(event)
        MockMenu.assert_not_called()
