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

import numpy as np
import pandas as pd
import pytest
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

from pymeasure.display.curves import BufferCurve, Crosshairs, ResultsCurve, ResultsImage


# ---------------------------------------------------------------------------
# BufferCurve
# ---------------------------------------------------------------------------


class TestBufferCurve:
    def test_prepare_creates_buffer(self):
        curve = BufferCurve()
        curve.prepare(size=10)
        assert curve._buffer.shape == (10, 2)
        assert curve._ptr == 0

    def test_prepare_dtype(self):
        curve = BufferCurve()
        curve.prepare(5, dtype=np.float64)
        assert curve._buffer.dtype == np.float64

    def test_append_without_prepare_raises(self):
        curve = BufferCurve()
        with pytest.raises(Exception, match="BufferCurve buffer must be prepared"):
            curve.append(1, 2)

    def test_append_overflow_raises(self):
        curve = BufferCurve()
        curve.prepare(size=2)
        curve.append(1, 2)
        curve.append(3, 4)
        with pytest.raises(Exception, match="BufferCurve overflow"):
            curve.append(5, 6)

    def test_append_sets_data_and_emits(self, qtbot):
        curve = BufferCurve()
        curve.prepare(size=5)
        with qtbot.waitSignal(curve.data_updated, timeout=1000):
            curve.append(1.0, 2.0)
        assert curve._ptr == 1
        x, y = curve.getData()
        # setData is called with the slice [:0], so no points are displayed yet
        # (the just-appended point becomes visible on the *next* append).
        if x is not None:
            assert len(x) == 0
            assert len(y) == 0
        assert curve._buffer[0, 0] == 1.0
        assert curve._buffer[0, 1] == 2.0

    def test_append_sequence(self):
        curve = BufferCurve()
        curve.prepare(size=5)
        curve.append(0.0, 10.0)
        curve.append(1.0, 20.0)
        curve.append(2.0, 30.0)
        x, y = curve.getData()
        # After three appends, the first two points are visible.
        np.testing.assert_allclose(x, [0.0, 1.0])
        np.testing.assert_allclose(y, [10.0, 20.0])
        assert curve._ptr == 3


# ---------------------------------------------------------------------------
# ResultsCurve
# ---------------------------------------------------------------------------


def _make_results_curve(**kwargs):
    pen = pg.mkPen(color='red')
    results = mock.MagicMock()
    return ResultsCurve(results=results, x='x', y='y', pen=pen, **kwargs)


class TestResultsCurve:
    def test_initialization_stores_attrs(self):
        pen = pg.mkPen(color='red')
        results = mock.MagicMock()
        wdg = mock.MagicMock()
        curve = ResultsCurve(results=results, x='x', y='y',
                            force_reload=True, wdg=wdg, pen=pen)
        assert curve.results is results
        assert curve.x == 'x'
        assert curve.y == 'y'
        assert curve.force_reload is True
        assert curve.wdg is wdg
        assert curve.pen is pen
        assert curve.color == QtGui.QColor('red')

    def test_update_data_no_reload(self):
        curve = _make_results_curve(force_reload=False)
        data = pd.DataFrame({'x': [0.0, 1.0, 2.0], 'y': [10.0, 20.0, 30.0]})
        curve.results.data = data
        with mock.patch.object(curve, 'setData') as mock_set:
            curve.update_data()
        curve.results.reload.assert_not_called()
        mock_set.assert_called_once()
        args, _ = mock_set.call_args
        np.testing.assert_allclose(args[0], data['x'].to_numpy())
        np.testing.assert_allclose(args[1], data['y'].to_numpy())

    def test_update_data_force_reload(self):
        curve = _make_results_curve(force_reload=True)
        data = pd.DataFrame({'x': [0.0, 1.0], 'y': [1.0, 2.0]})
        curve.results.data = data
        with mock.patch.object(curve, 'setData'):
            curve.update_data()
        curve.results.reload.assert_called_once()

    def test_set_color_updates_pen(self):
        curve = _make_results_curve()
        new_color = QtGui.QColor('blue')
        curve.set_color(new_color)
        assert curve.pen.color() == new_color
        assert curve.color == new_color


# ---------------------------------------------------------------------------
# ResultsImage
# ---------------------------------------------------------------------------


class _FakeProcedure:
    def __init__(self):
        self.x_start = 0.0
        self.x_end = 2.0
        self.x_step = 1.0
        self.y_start = 0.0
        self.y_end = 2.0
        self.y_step = 1.0


class _FakeResults:
    def __init__(self, data=None):
        self.procedure = _FakeProcedure()
        self.data = data

    def reload(self):
        pass


def _make_results_image(data=None):
    results = _FakeResults(data=data)
    return ResultsImage(results=results, x='x', y='y', z='z')


class TestResultsImage:
    def test_initialization_computes_dimensions(self):
        img = _make_results_image()
        assert img.xsize == 3
        assert img.ysize == 3
        assert img.img_data.shape == (3, 3, 4)
        tr = img.transform()
        assert tr.m11() == 1.0  # x scale
        assert tr.m22() == 1.0  # y scale
        # translate = (int(0/1) - 0.5, int(0/1) - 0.5) = (-0.5, -0.5)
        assert tr.dx() == pytest.approx(-0.5)
        assert tr.dy() == pytest.approx(-0.5)

    @pytest.mark.parametrize(
        "value,expected", [
            (0.4, 0),
            (0.5, 1),
            (0.6, 1),
            (1.4, 1),
            (1.5, 2),
        ]
    )
    def test_round_up(self, value, expected):
        img = _make_results_image()
        assert img.round_up(value) == expected

    @pytest.mark.parametrize(
        "x,y,exp_x,exp_y", [
            (0.0, 0.0, 0, 0),
            (1.0, 1.0, 1, 1),
            (2.0, 2.0, 2, 2),
            (0.5, 1.5, 1, 2),
        ]
    )
    def test_find_img_index_in_range(self, x, y, exp_x, exp_y):
        img = _make_results_image()
        assert img.find_img_index(x, y) == [exp_x, exp_y]

    def test_find_img_index_out_of_range_defaults_to_last(self):
        img = _make_results_image()
        # x below range, y above range
        assert img.find_img_index(-1.0, 3.0) == [img.xsize - 1, img.ysize - 1]
        # x above range, y below range
        assert img.find_img_index(5.0, -2.0) == [img.xsize - 1, img.ysize - 1]

    def test_colormap_returns_rgba_floats(self):
        img = _make_results_image()
        rgba = img.colormap(0.5)
        assert isinstance(rgba, np.ndarray)
        assert rgba.shape == (4,)
        assert rgba.dtype.kind == 'f'
        assert ((rgba >= 0.0) & (rgba <= 1.0)).all()

    def test_update_data_populates_image(self):
        data = pd.DataFrame({
            'x': [0.0, 1.0, 2.0],
            'y': [0.0, 0.0, 0.0],
            'z': [0.0, 0.5, 1.0],
        })
        img = _make_results_image(data=data)
        with mock.patch.object(img, 'setImage') as mock_set:
            img.update_data()
        mock_set.assert_called_once()
        args, _ = mock_set.call_args
        passed = args[0] if args else mock_set.call_args[1]['image']
        # setImage is called with the transposed image data
        np.testing.assert_array_equal(passed, np.transpose(img.img_data, axes=(1, 0, 2)))
        # The first and last rows should differ (z=0 and z=1 map to different colors)
        assert not np.allclose(img.img_data[0, 0, :], img.img_data[0, 2, :])


# ---------------------------------------------------------------------------
# Crosshairs
# ---------------------------------------------------------------------------


class TestCrosshairs:
    def _make_crosshairs(self, qtbot):
        widget = pg.PlotWidget()
        qtbot.addWidget(widget)
        widget.show()
        plot = widget.plotItem
        ch = Crosshairs(plot)
        return widget, plot, ch

    def test_initialization_adds_lines_to_plot(self, qtbot):
        widget, plot, ch = self._make_crosshairs(qtbot)
        assert ch.vertical in plot.items
        assert ch.horizontal in plot.items

    def test_hide_show(self, qtbot):
        widget, plot, ch = self._make_crosshairs(qtbot)
        ch.hide()
        assert not ch.vertical.isVisible()
        assert not ch.horizontal.isVisible()
        ch.show()
        assert ch.vertical.isVisible()
        assert ch.horizontal.isVisible()

    def test_update_emits_coordinates(self, qtbot):
        widget, plot, ch = self._make_crosshairs(qtbot)
        plot.setXRange(0, 10)
        plot.setYRange(0, 10)
        qtbot.waitUntil(lambda: widget.isVisible(), timeout=2000)
        scene_pos = QtCore.QPointF(50.0, 50.0)
        ch.position = scene_pos
        received = []
        ch.coordinates.connect(lambda x, y: received.append((x, y)))
        ch.update()
        assert len(received) == 1
        x, y = received[0]
        assert isinstance(x, float)
        assert isinstance(y, float)
        assert ch.vertical.value() == pytest.approx(x)
        assert ch.horizontal.value() == pytest.approx(y)

    def test_mouseMoved_updates_position(self, qtbot):
        widget, plot, ch = self._make_crosshairs(qtbot)
        scene_pos = QtCore.QPointF(10.0, 20.0)
        with mock.patch.object(ch, 'update') as mock_update:
            ch.mouseMoved([scene_pos])
        assert ch.position == scene_pos
        mock_update.assert_called_once()

    def test_mouseMoved_no_event_raises(self, qtbot):
        widget, plot, ch = self._make_crosshairs(qtbot)
        with pytest.raises(Exception, match="Mouse location not known"):
            ch.mouseMoved(None)
