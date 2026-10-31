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

import contextlib
import gc

import pyqtgraph as pg

from pymeasure.display.Qt import QtCore
from pymeasure.display.widgets.plot_frame import PlotFrame


def test_plot_frame_construction(qtbot):
    """PlotFrame must construct with modern pyqtgraph.

    Since pyqtgraph 0.13, :code:`pyqtgraph.PlotItem` is a class rather than
    a module, and :code:`pg.PlotItem.PlotItem` raised an AttributeError.
    """
    frame = PlotFrame("Time (s)", "Voltage (V)")
    qtbot.addWidget(frame)
    assert frame.plot is frame.plot_widget.getPlotItem()


def test_init_with_axes(qtbot):
    frame = PlotFrame(x_axis="Time (s)", y_axis="Voltage (V)")
    qtbot.addWidget(frame)
    assert frame.x_axis == "Time (s)"
    assert frame.y_axis == "Voltage (V)"


def test_setup_ui_creates_plot_and_coordinates(qtbot):
    frame = PlotFrame(x_axis="Time (s)", y_axis="Voltage (V)")
    qtbot.addWidget(frame)
    assert isinstance(frame.plot_widget, pg.PlotWidget)
    assert frame.plot is frame.plot_widget.getPlotItem()
    assert frame.coordinates is not None
    assert frame.crosshairs is not None
    assert frame.timer.isActive()


def test_update_coordinates_updates_label(qtbot):
    frame = PlotFrame(x_axis="Time (s)", y_axis="Voltage (V)")
    qtbot.addWidget(frame)
    frame.update_coordinates(1.5, 2.5)
    # LabelItem stores the text on an internal QGraphicsTextItem
    assert frame.coordinates.item.toPlainText() == "(1.5, 2.5)"


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


def test_change_x_axis_updates_axis_and_emits(qtbot):
    frame = PlotFrame(x_axis="Time (s)", y_axis="Voltage (V)")
    qtbot.addWidget(frame)
    received = []
    frame.x_axis_changed.connect(lambda axis: received.append(axis))

    frame.change_x_axis("Position (m)")

    assert frame.x_axis == "Position (m)"
    assert received == ["Position (m)"]


def test_change_y_axis_updates_axis_and_emits(qtbot):
    frame = PlotFrame(x_axis="Time (s)", y_axis="Voltage (V)")
    qtbot.addWidget(frame)
    received = []
    frame.y_axis_changed.connect(lambda axis: received.append(axis))

    frame.change_y_axis("Current (A)")

    assert frame.y_axis == "Current (A)"
    assert received == ["Current (A)"]


def test_close_tears_down_plot_frame(qtbot):
    """Closing a frame releases the plot, timer and crosshairs."""
    frame = PlotFrame(x_axis="Time (s)", y_axis="Voltage (V)")
    qtbot.addWidget(frame)
    timer = frame.timer
    crosshairs = frame.crosshairs
    assert timer.isActive()

    frame.close()

    assert frame._torn_down is True
    assert not timer.isActive()
    assert crosshairs.proxy.blockSignal is True
    assert crosshairs.proxy.slot is None
    assert frame.timer is None
    assert frame.crosshairs is None
    assert frame.coordinates is None
    assert frame.plot is None
    assert frame.plot_widget is None


def test_teardown_is_idempotent(qtbot):
    """A second teardown or close must be a no-op instead of raising."""
    frame = PlotFrame(x_axis="Time (s)", y_axis="Voltage (V)")
    qtbot.addWidget(frame)

    frame._teardown()
    frame._teardown()
    frame.close()
    frame.close()

    assert frame._torn_down is True
    assert frame.plot is None


def test_teardown_after_cpp_deletion_is_safe(qtbot, qapp):
    """Teardown after the C++ object is gone must not raise."""
    # Deliberately not registered with qtbot: the test deletes the widget itself,
    # and pytest-qt's cleanup calls close() on registered widgets unconditionally.
    frame = PlotFrame(x_axis="Time (s)", y_axis="Voltage (V)")
    frame.close()
    frame.deleteLater()
    QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
    qapp.processEvents()
    gc.collect()

    frame._teardown()


def test_deferred_delete_without_close_tears_down(qapp):
    """A deferred delete alone reaches event() and tears the frame down."""
    # Deliberately not registered with qtbot: the test deletes the widget itself,
    # and pytest-qt's cleanup calls close() on registered widgets unconditionally.
    frame = PlotFrame(x_axis="Time (s)", y_axis="Voltage (V)")
    assert frame._torn_down is False

    frame.deleteLater()
    QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
    qapp.processEvents()

    # The C/C++ object is gone now, but the Python attributes of the wrapper survive.
    assert frame._torn_down is True


def test_repeated_teardown_is_stable(qtbot, qapp):
    """Reproduce the pytest-qt teardown sequence repeatedly without exceptions."""
    capture_exceptions = getattr(qtbot, "capture_exceptions", None)
    if capture_exceptions is None:
        context = contextlib.nullcontext([])
    else:
        context = capture_exceptions()

    with context as exceptions:
        torn_down = []
        for _ in range(10):
            frame = PlotFrame(x_axis="Time (s)", y_axis="Voltage (V)")
            qtbot.addWidget(frame)
            frame.resize(400, 300)
            qtbot.wait(1)
            frame.close()
            torn_down.append(getattr(frame, "_torn_down", False))
            frame.deleteLater()
            QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
            qapp.processEvents()
            del frame
            gc.collect()

        assert all(torn_down)

    assert list(exceptions) == []
