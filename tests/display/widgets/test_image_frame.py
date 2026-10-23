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

from pymeasure.display.curves import ResultsImage
from pymeasure.display.widgets.image_frame import ImageFrame
from pymeasure.display.widgets.plot_frame import PlotFrame


def test_image_frame_extends_plot_frame(qtbot):
    frame = ImageFrame("x (V)", "y (A)", z_axis="z (T)")
    qtbot.addWidget(frame)
    assert isinstance(frame, PlotFrame)
    assert frame.ResultsClass is ResultsImage
    assert frame.x_axis == "x (V)"
    assert frame.y_axis == "y (A)"
    assert frame.z_axis == "z (T)"


def test_change_z_axis_updates_title_and_emits(qtbot):
    frame = ImageFrame("x (V)", "y (A)", z_axis="z (T)")
    qtbot.addWidget(frame)
    received = []
    frame.z_axis_changed.connect(lambda axis: received.append(axis))

    frame.change_z_axis("w (m)")

    assert frame.z_axis == "w (m)"
    assert received == ["w (m)"]
    # title reflects the label and units parsed from the axis string
    assert "w" in frame.plot.titleLabel.text
    assert "m" in frame.plot.titleLabel.text


def test_change_z_axis_without_units(qtbot):
    frame = ImageFrame("x (V)", "y (A)", z_axis="z")
    qtbot.addWidget(frame)
    assert frame.z_axis == "z"
    # No units present in axis string, title is just the label
    assert "z" in frame.plot.titleLabel.text
