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

from pymeasure.display.curves import ResultsCurve
from pymeasure.display.widgets.plot_widget import PlotWidget
from pymeasure.display.windows.plotter_window import PlotterWindow


class _FakeResults:
    """Minimal Results mock suitable for PlotterWindow construction."""

    def __init__(self, data_filename="data.csv", columns=None):
        self.data_filename = data_filename
        if columns is None:
            columns = ["Time (s)", "Voltage (V)", "Current (A)"]
        self.procedure = mock.MagicMock()
        self.procedure.DATA_COLUMNS = columns


class _FakePlotter:
    """Minimal Plotter mock for PlotterWindow tests."""

    def __init__(self, results=None, should_stop=False):
        if results is None:
            results = _FakeResults()
        self.results = results
        self._should_stop = should_stop
        self.stop_called = False

    def should_stop(self):
        return self._should_stop

    def stop(self):
        self.stop_called = True


def _make_window(qtbot, plotter=None, **kwargs):
    if plotter is None:
        plotter = _FakePlotter()
    window = PlotterWindow(plotter, **kwargs)
    qtbot.addWidget(window)
    return window


def test_init_stores_plotter_and_refresh_time(qtbot):
    plotter = _FakePlotter()
    window = _make_window(qtbot, plotter, refresh_time=0.5, linewidth=2)
    assert window.plotter is plotter
    assert window.refresh_time == 0.5


def test_init_setup_ui_builds_plot_widget(qtbot):
    window = _make_window(qtbot)
    assert isinstance(window.plot_widget, PlotWidget)
    # plot attribute references the PlotItem
    assert window.plot is window.plot_widget.plot
    # file field is populated with the results data_filename
    assert window.file.text() == "data.csv"


def test_init_linewidth_stored_in_plot_widget(qtbot):
    window = _make_window(qtbot, linewidth=4)
    assert window.plot_widget.linewidth == 4


def test_init_curve_added_to_plot(qtbot):
    window = _make_window(qtbot, linewidth=2)
    assert isinstance(window.curve, ResultsCurve)
    assert window.curve in window.plot.items


def test_init_refresh_time_passed_to_plot_widget(qtbot):
    window = _make_window(qtbot, refresh_time=0.7)
    assert window.plot_widget.refresh_time == 0.7


def test_init_plot_widget_check_status_disabled(qtbot):
    window = _make_window(qtbot)
    assert window.plot_widget.check_status is False


def test_check_stop_when_plotter_signals_completion(qtbot):
    plotter = _FakePlotter(should_stop=True)
    window = _make_window(qtbot, plotter)
    with mock.patch.object(pg.QtCore.QCoreApplication.instance(), "quit") as mock_quit:
        window.check_stop()
        mock_quit.assert_called_once()


def test_check_stop_does_not_quit_when_plotter_running(qtbot):
    plotter = _FakePlotter(should_stop=False)
    window = _make_window(qtbot, plotter)
    with mock.patch.object(pg.QtCore.QCoreApplication.instance(), "quit") as mock_quit:
        window.check_stop()
        mock_quit.assert_not_called()


def test_quit_closes_window_and_stops_plotter(qtbot):
    plotter = _FakePlotter()
    window = _make_window(qtbot, plotter)
    with mock.patch.object(window, "close") as mock_close:
        window.quit()
        mock_close.assert_called_once()
        assert plotter.stop_called is True
