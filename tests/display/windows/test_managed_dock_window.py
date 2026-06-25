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

import pyqtgraph as pg

from pymeasure.display.widgets.dock_widget import DockWidget
from pymeasure.display.widgets.log_widget import LogWidget
from pymeasure.display.windows.managed_dock_window import ManagedDockWindow


def _make_window(qtbot, procedure_class, **kwargs):
    window = ManagedDockWindow(procedure_class, **kwargs)
    qtbot.addWidget(window)
    return window


def test_init_single_axis(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Enabled",
    )
    assert window.x_axis == "Voltage (V)"
    assert window.y_axis == "Enabled"
    assert window.x_axis_labels == ["Voltage (V)"]
    assert window.y_axis_labels == ["Enabled"]
    assert isinstance(window.dock_widget, DockWidget)
    assert isinstance(window.log_widget, LogWidget)
    assert window.dock_widget in window.widget_list
    assert window.log_widget in window.widget_list


def test_init_list_axes(qtbot, procedure_class):
    window = _make_window(
        qtbot,
        procedure_class,
        x_axis=["Voltage (V)", "Iterations"],
        y_axis=["Enabled", "Iterations"],
    )
    # list is reduced to first element for ResultsDialog
    assert window.x_axis == "Voltage (V)"
    assert window.y_axis == "Enabled"
    assert window.x_axis_labels == ["Voltage (V)", "Iterations"]
    assert window.y_axis_labels == ["Enabled", "Iterations"]
    assert window.dock_widget.num_plots == 2
    assert len(window.dock_widget.docks) == 2
    assert len(window.dock_widget.plot_frames) == 2


def test_init_linewidth_stored(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class,
        x_axis="Voltage (V)", y_axis="Enabled", linewidth=3,
    )
    assert window.dock_widget.linewidth == 3


def test_init_measured_quantities_updated(qtbot, procedure_class):
    window = _make_window(
        qtbot,
        procedure_class,
        x_axis=["Voltage (V)", "Iterations"],
        y_axis="Enabled",
    )
    measured = window.browser_widget.browser.measured_quantities
    assert "Voltage (V)" in measured
    assert "Iterations" in measured
    assert "Enabled" in measured


def test_layout_adds_dock_widgets_to_main_window(qtbot, procedure_class):
    with mock.patch.object(ManagedDockWindow, "addDockWidget") as mock_add:
        window = _make_window(
            qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Enabled",
        )
    # _layout in ManagedWindowBase adds at least one dock (Input Parameters)
    assert mock_add.called
    # verify the dock widget is added to the tab widget
    tab_texts = [window.tabs.tabText(i) for i in range(window.tabs.count())]
    assert "Dock Tab" in tab_texts
    assert "Experiment Log" in tab_texts


def test_dock_layout_persistence_save_load(qtbot, procedure_class, tmp_path):
    # construct window with dock layout in tmp_path
    window = ManagedDockWindow(
        procedure_class,
        x_axis="Voltage (V)",
        y_axis="Enabled",
    )
    qtbot.addWidget(window)
    # point the dock_widget's layout file at tmp_path for the save call
    window.dock_widget.dock_layout_filename = str(tmp_path / "layout.json")

    # Save layout via the dock_widget's save_dock_layout method
    with mock.patch.object(window.dock_widget.dock_area, "saveState",
                          return_value={"saved": True}) as mock_save_state, \
         mock.patch("pymeasure.display.widgets.dock_widget.open",
                    mock.mock_open(), create=True) as mock_open_fn:
        window.dock_widget.save_dock_layout()
        assert mock_save_state.called
        assert mock_open_fn.called

    # Load layout: simulate an existing layout file by patching path.exists
    # one plot frame matches num_plots for the single-axis window
    fake_layout = '{"docks": {}, "plots": [{}]}'
    import pyqtgraph.dockarea
    with mock.patch("pymeasure.display.widgets.dock_widget.path.exists",
                    return_value=True), \
         mock.patch("pymeasure.display.widgets.dock_widget.open",
                    mock.mock_open(read_data=fake_layout), create=True), \
         mock.patch.object(pyqtgraph.dockarea.DockArea, "restoreState") as mock_restore, \
         mock.patch.object(pg.PlotWidget, "restoreState"):
        # Re-trigger _layout by constructing a new widget
        window2 = ManagedDockWindow(
            procedure_class,
            x_axis="Voltage (V)",
            y_axis="Enabled",
        )
        qtbot.addWidget(window2)
        assert mock_restore.called


def test_inherited_queue_button_connected(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Enabled",
    )
    assert window.queue_button.text() == "Queue"
    assert window.abort_button.text() == "Abort"
    assert window.abort_button.isEnabled() is False


def test_inherited_abort_calls_manager_abort(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Enabled",
    )
    with mock.patch.object(window.manager, "abort") as mock_abort:
        window.abort()
        mock_abort.assert_called_once()
    # abort_button is repurposed as Resume
    assert window.abort_button.text() == "Resume"


def test_inherited_quit_closes_window(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Enabled",
    )
    with mock.patch.object(window, "close") as mock_close, \
         mock.patch.object(window.manager, "is_running", return_value=False):
        window.quit()
        mock_close.assert_called_once()


def test_inherited_queue_with_procedure(qtbot, procedure_class, tmp_path):
    window = _make_window(
        qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Enabled",
    )
    # set file_input to use tmp_path
    window.directory = str(tmp_path)
    procedure = procedure_class()
    with mock.patch.object(window.manager, "queue") as mock_queue:
        window.queue(procedure=procedure)
        mock_queue.assert_called_once()
