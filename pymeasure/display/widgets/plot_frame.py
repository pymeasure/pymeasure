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

import logging
import re
import weakref
from typing import Any, cast

import pyqtgraph as pg

from ...experiment.procedure import ProcedureStatus
from ..curves import Crosshairs, ResultsCurve
from ..Qt import QtCore, QtGui, QtWidgets

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def _get_attr(obj: object, name: str, default: Any = None) -> Any:
    """Return an attribute of a Qt object, tolerating an already deleted wrapper.

    Accessing an attribute of a Qt object whose C/C++ counterpart has been deleted already
    raises ``RuntimeError``, even for ``getattr`` with a default value.
    Such an attribute is treated as absent.
    """
    try:
        return getattr(obj, name, default)
    except RuntimeError:
        return default


class PlotFrame(QtWidgets.QFrame):
    """Combines a PyQtGraph Plot with Crosshairs.

    Refreshes the plot based on the refresh_time, and allows the axes to be changed on the fly,
    which updates the plotted data.

    Closing the frame is terminal: ``_teardown`` releases the refresh timer, the crosshairs,
    the coordinate label and the plot widget.
    Afterwards the plot and the coordinate label are gone and the frame must not be shown or used
    again.

    Note that a frame destroyed purely as a C/C++ side effect of its parent's destructor,
    without a close event or a deferred delete reaching it or its window, gets no Python
    callback and therefore cannot be torn down.
    The event filter on the ancestor window (see ``showEvent`` and ``event``) covers the regular
    GUI paths, including never-shown frames that are reparented into their window.
    """

    LABEL_STYLE = {'font-size': '10pt', 'font-family': 'Arial', 'color': '#000000'}
    updated = QtCore.Signal()
    ResultsClass = ResultsCurve
    x_axis_changed = QtCore.Signal(str)
    y_axis_changed = QtCore.Signal(str)

    def __init__(
        self,
        x_axis: str,
        y_axis: str,
        refresh_time: float = 0.2,
        check_status: bool = True,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent=parent)
        # Set before _setup_ui, so a partially constructed frame can be torn down.
        self._torn_down = False
        self._filtered_window_ref = None
        self.refresh_time = refresh_time
        self.check_status = check_status
        self._setup_ui()
        self.change_x_axis(x_axis)
        self.change_y_axis(y_axis)

    def _setup_ui(self) -> None:
        self.setAutoFillBackground(False)
        self.setStyleSheet("background: #fff")
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.setMidLineWidth(1)

        vbox = QtWidgets.QVBoxLayout(self)

        self.plot_widget = pg.PlotWidget(self, background='#ffffff')
        vbox.addWidget(self.plot_widget)  # pyright: ignore[reportArgumentType]
        self.setLayout(vbox)

        plot = cast(pg.PlotItem, self.plot_widget.getPlotItem())
        self.plot: pg.PlotItem | None = plot

        style = dict(self.LABEL_STYLE, justify='right')
        if "font-size" in style:  # LabelItem wants the size as 'size' rather than 'font-size'
            style["size"] = style.pop("font-size")
        self.coordinates = pg.LabelItem("", parent=plot, angle=0, **style)
        self.coordinates.anchor(itemPos=(1, 1), parentPos=(1, 1), offset=(0, 3))

        self.crosshairs = Crosshairs(plot,
                                     pen=pg.mkPen(color='#AAAAAA',
                                                  style=QtCore.Qt.PenStyle.DashLine))
        self.crosshairs.coordinates.connect(self.update_coordinates)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_curves)
        self.timer.timeout.connect(self.crosshairs.update)
        self.timer.timeout.connect(self.updated)
        self.timer.start(int(self.refresh_time * 1e3))

    def update_coordinates(self, x: float, y: float) -> None:
        coordinates = _get_attr(self, "coordinates")
        if coordinates is None:
            return
        coordinates.setText(f"({x:g}, {y:g})")

    def update_curves(self) -> None:
        plot = _get_attr(self, "plot")
        if plot is None:
            return
        for item in plot.items:
            if isinstance(item, self.ResultsClass):
                if self.check_status:
                    if item.results.procedure.status == ProcedureStatus.RUNNING:
                        item.update_data()
                else:
                    item.update_data()

    def _teardown(self) -> None:
        """Release timer, crosshairs, coordinate label and plot widget (terminal).

        The method is idempotent and tolerates partially constructed frames as well as frames
        whose C/C++ counterpart was deleted already.
        """
        # Use the instance dict: attribute access on a deleted wrapper raises RuntimeError.
        if self.__dict__.get("_torn_down", False):
            return
        self._torn_down = True

        # Stop the refresh timer first; its timeout must not fire during teardown.
        timer = _get_attr(self, "timer")
        self.timer = None
        if timer is not None:
            try:
                timer.stop()
                timer.timeout.disconnect()
            except (RuntimeError, TypeError, AttributeError):
                pass

        # Take local references, then null the attributes.
        plot = _get_attr(self, "plot")
        crosshairs = _get_attr(self, "crosshairs")
        self.plot = None
        self.crosshairs = None
        if crosshairs is not None:
            try:
                crosshairs.coordinates.disconnect(self.update_coordinates)
            except (RuntimeError, TypeError, AttributeError):
                pass
            try:
                crosshairs.teardown()
            except (RuntimeError, TypeError, AttributeError):
                pass

        # Detach the coordinate label from the scene before the scene is cleared.
        # Removing it hands ownership to this Python wrapper, so it is deleted with the
        # reference instead of being freed under a surviving wrapper by scene.clear().
        coordinates = _get_attr(self, "coordinates")
        self.coordinates = None
        if coordinates is not None and plot is not None:
            try:
                plot.scene().removeItem(coordinates)
            except (RuntimeError, TypeError, AttributeError):
                pass

        # Drop the event filter installed on the ancestor window.
        filtered_window = self._get_filtered_window()
        self._filtered_window_ref = None
        if filtered_window is not None:
            try:
                filtered_window.removeEventFilter(self)
            except (RuntimeError, TypeError, AttributeError):
                pass

        # Close the plot widget last: pyqtgraph's close() empties the scene and nulls the plot
        # item, so it must never be called twice.
        plot_widget = _get_attr(self, "plot_widget")
        self.plot_widget = None
        if plot_widget is not None:
            try:
                plot_widget.close()
            except (RuntimeError, TypeError, AttributeError):
                pass

    def _get_filtered_window(self) -> QtWidgets.QWidget | None:
        """Return the window the event filter is installed on, if it is still alive."""
        window_ref = _get_attr(self, "_filtered_window_ref")
        return window_ref() if window_ref is not None else None

    def _install_window_filter(self) -> None:
        """Install this frame as event filter on its ancestor window.

        A close or deferred delete is only delivered to the widget it applies to, never to its
        children; filtering the ancestor window is therefore the only way a frame notices that
        its window is going away.

        Only a weak reference to the window is kept: a strong reference from a child to its
        ancestor window forms a reference cycle whose collection by Python's garbage collector
        may destroy Qt objects in the middle of event processing.
        """
        window = None
        try:
            window = self.window()
        except (RuntimeError, TypeError, AttributeError):
            pass
        previous = self._get_filtered_window()
        if window is previous:
            return
        if previous is not None:
            try:
                previous.removeEventFilter(self)
            except (RuntimeError, TypeError, AttributeError):
                pass
        self._filtered_window_ref = None
        # An own top-level window is covered by event() and closeEvent(); no filter needed.
        if window is None or window is self:
            return
        try:
            window.installEventFilter(self)
            self._filtered_window_ref = weakref.ref(window)
        except (RuntimeError, TypeError, AttributeError):
            self._filtered_window_ref = None

    def showEvent(self, a0: QtGui.QShowEvent | None) -> None:
        self._install_window_filter()
        super().showEvent(a0)

    def closeEvent(self, a0: QtGui.QCloseEvent | None) -> None:
        self._teardown()
        super().closeEvent(a0)

    def event(self, e: QtCore.QEvent | None) -> bool:
        if e is None:
            return super().event(e)
        if e.type() == QtCore.QEvent.Type.DeferredDelete:
            # The C/C++ object is deleted by the superclass call below, so release the
            # Python-owned resources first.
            self._teardown()
        elif e.type() == QtCore.QEvent.Type.ParentChange:
            # Reparenting changes the ancestor window whose close has to reach this frame.
            self._install_window_filter()
        return super().event(e)

    def eventFilter(self, a0: QtCore.QObject | None, a1: QtCore.QEvent | None) -> bool:
        if a0 is self._get_filtered_window() and a1 is not None and a1.type() in (
            QtCore.QEvent.Type.Close,
            QtCore.QEvent.Type.DeferredDelete,
        ):
            self._teardown()
        return super().eventFilter(a0, a1)

    def parse_axis(self, axis: str) -> tuple[str, str | None]:
        """ Returns the units of an axis by searching the string
        """
        units_pattern = r"\((?P<units>\w+)\)"
        try:
            match = re.search(units_pattern, axis)
        except TypeError:
            match = None

        if match and 'units' in match.groupdict():
                label = re.sub(units_pattern, '', axis)
                return label, cast(str, match.groupdict()['units'])
        return axis, None

    def change_x_axis(self, axis: str) -> None:
        plot = self.plot
        if plot is None:
            return
        for item in plot.items:
            if isinstance(item, self.ResultsClass):
                item.x_label = axis
                item.update_data()
        label, units = self.parse_axis(axis)
        plot.setLabel('bottom', label, units=units, **self.LABEL_STYLE)
        self.x_axis = axis
        self.x_axis_changed.emit(axis)

    def change_y_axis(self, axis: str) -> None:
        plot = self.plot
        if plot is None:
            return
        for item in plot.items:
            if isinstance(item, self.ResultsClass):
                item.y_label = axis
                item.update_data()
        label, units = self.parse_axis(axis)
        plot.setLabel('left', label, units=units, **self.LABEL_STYLE)
        self.y_axis = axis
        self.y_axis_changed.emit(axis)
