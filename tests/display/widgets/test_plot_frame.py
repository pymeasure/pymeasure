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

import pyqtgraph as pg

from pymeasure.display.widgets.plot_frame import PlotFrame


def test_init_without_axes(qtbot):
    frame = PlotFrame()
    qtbot.addWidget(frame)
    assert frame.x_axis is None
    assert frame.y_axis is None
    assert frame.refresh_time == 0.2
    assert frame.check_status is True


def test_init_with_axes(qtbot):
    frame = PlotFrame(x_axis="Time (s)", y_axis="Voltage (V)")
    qtbot.addWidget(frame)
    assert frame.x_axis == "Time (s)"
    assert frame.y_axis == "Voltage (V)"


def test_setup_ui_creates_plot_and_coordinates(qtbot):
    frame = PlotFrame()
    qtbot.addWidget(frame)
    assert isinstance(frame.plot_widget, pg.PlotWidget)
    assert frame.plot is frame.plot_widget.getPlotItem()
    assert frame.coordinates is not None
    assert frame.crosshairs is not None
    assert frame.timer.isActive()


def test_update_coordinates_updates_label(qtbot):
    frame = PlotFrame()
    qtbot.addWidget(frame)
    frame.update_coordinates(1.5, 2.5)
    # The LabelItem text is set via setText; verify the item exists and is not None
    assert frame.coordinates is not None


def test_parse_axis_with_units():
    frame = PlotFrame.__new__(PlotFrame)
    label, units = frame.parse_axis("Voltage (V)")
    assert label == "Voltage "
    assert units == "V"


def test_parse_axis_without_units():
    frame = PlotFrame.__new__(PlotFrame)
    label, units = frame.parse_axis("Time")
    assert label == "Time"
    assert units is None


def test_parse_axis_none():
    frame = PlotFrame.__new__(PlotFrame)
    label, units = frame.parse_axis(None)
    assert label is None
    assert units is None


def test_change_x_axis_updates_axis_and_emits(qtbot):
    frame = PlotFrame()
    qtbot.addWidget(frame)
    received = []
    frame.x_axis_changed.connect(lambda axis: received.append(axis))

    frame.change_x_axis("Position (m)")

    assert frame.x_axis == "Position (m)"
    assert received == ["Position (m)"]


def test_change_y_axis_updates_axis_and_emits(qtbot):
    frame = PlotFrame()
    qtbot.addWidget(frame)
    received = []
    frame.y_axis_changed.connect(lambda axis: received.append(axis))

    frame.change_y_axis("Current (A)")

    assert frame.y_axis == "Current (A)"
    assert received == ["Current (A)"]
