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

from pymeasure.display.curves import ResultsImage
from pymeasure.display.widgets.image_widget import ImageWidget
from pymeasure.display.windows.managed_image_window import ManagedImageWindow


class _FakeProcedure:
    """Procedure stub providing axis range attributes for ResultsImage.

    Attribute names follow the ResultsImage convention: ``<axis>_start`` etc.
    """

    def __init__(self):
        for axis in ("Voltage (V)", "Iterations", "Enabled", "x", "y", "z", "w"):
            setattr(self, f"{axis}_start", 0.0)
            setattr(self, f"{axis}_end", 2.0)
            setattr(self, f"{axis}_step", 1.0)


class _FakeResults:
    """Minimal Results mock suitable for ResultsImage construction."""

    def __init__(self):
        self.procedure = _FakeProcedure()

    def reload(self):
        pass


def _make_window(qtbot, procedure_class, x_axis, y_axis, z_axis=None, **kwargs):
    window = ManagedImageWindow(
        procedure_class, x_axis=x_axis, y_axis=y_axis, z_axis=z_axis, **kwargs,
    )
    qtbot.addWidget(window)
    return window


def test_init_stores_axes(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Iterations",
    )
    assert window.x_axis == "Voltage (V)"
    assert window.y_axis == "Iterations"
    assert window.z_axis is None


def test_init_with_z_axis_stored(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class,
        x_axis="Voltage (V)", y_axis="Iterations", z_axis="Enabled",
    )
    assert window.z_axis == "Enabled"


def test_init_constructs_image_widget(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Iterations",
    )
    assert isinstance(window.image_widget, ImageWidget)
    assert window.image_widget in window.widget_list


def test_init_image_widget_axes(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Iterations",
    )
    assert window.image_widget.x_axis == "Voltage (V)"
    assert window.image_widget.y_axis == "Iterations"


def test_init_z_axis_set_in_image_frame(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class,
        x_axis="Voltage (V)", y_axis="Iterations", z_axis="Enabled",
    )
    assert window.image_widget.columns_z.currentText() == "Enabled"
    assert window.image_widget.image_frame.z_axis == "Enabled"


def test_init_image_widget_added_to_tabs(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Iterations",
    )
    tab_texts = [window.tabs.tabText(i) for i in range(window.tabs.count())]
    assert "Image" in tab_texts


def test_new_curve_returns_results_image(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Iterations",
    )
    results = _FakeResults()

    curve = window.new_curve(window.image_widget, results)
    assert isinstance(curve, ResultsImage)
    assert curve.results is results
    assert curve.wdg is window.image_widget


def test_inherited_queue_button_connected(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Iterations",
    )
    assert window.queue_button.text() == "Queue"
    assert window.abort_button.text() == "Abort"
    assert window.abort_button.isEnabled() is False


def test_inherited_abort_calls_manager_abort(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Iterations",
    )
    with mock.patch.object(window.manager, "abort") as mock_abort:
        window.abort()
        mock_abort.assert_called_once()
    assert window.abort_button.text() == "Resume"


def test_inherited_quit_closes_window(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Iterations",
    )
    with mock.patch.object(window, "close") as mock_close, \
         mock.patch.object(window.manager, "is_running", return_value=False):
        window.quit()
        mock_close.assert_called_once()
