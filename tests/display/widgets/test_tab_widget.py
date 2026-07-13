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

from pymeasure.display.Qt import QtWidgets
from pymeasure.display.widgets.tab_widget import TabWidget


class DelegatingTabWidget(TabWidget, QtWidgets.QWidget):
    """A concrete TabWidget subclass that delegates curve operations to its parent."""

    def new_curve(self, *args, **kwargs):
        return self.parent().new_curve(*args, **kwargs)

    def load(self, curve):
        self.parent().load(curve)

    def remove(self, curve):
        self.parent().remove(curve)

    def set_color(self, curve, color):
        self.parent().set_color(curve, color)

    def preview_widget(self, parent=None):
        widget = QtWidgets.QWidget(parent)
        widget.name = "preview"
        return widget

    def clear_widget(self):
        self._cleared = True


class FakeParent(QtWidgets.QWidget):
    """Fake parent widget recording method calls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.new_curve_calls = []
        self.load_calls = []
        self.remove_calls = []
        self.set_color_calls = []

    def new_curve(self, *args, **kwargs):
        self.new_curve_calls.append((args, kwargs))
        return "curve"

    def load(self, curve):
        self.load_calls.append(curve)

    def remove(self, curve):
        self.remove_calls.append(curve)

    def set_color(self, curve, color):
        self.set_color_calls.append((curve, color))


def test_init_stores_name(qtbot):
    parent = FakeParent()
    qtbot.addWidget(parent)
    wdg = DelegatingTabWidget("my-tab", parent=parent)
    qtbot.addWidget(wdg)
    assert wdg.name == "my-tab"


def test_new_curve_delegates_to_parent(qtbot):
    parent = FakeParent()
    qtbot.addWidget(parent)
    wdg = DelegatingTabWidget("tab", parent=parent)
    qtbot.addWidget(wdg)

    result = wdg.new_curve("results", color="red")

    assert result == "curve"
    assert parent.new_curve_calls == [(("results",), {"color": "red"})]


def test_load_delegates_to_parent(qtbot):
    parent = FakeParent()
    qtbot.addWidget(parent)
    wdg = DelegatingTabWidget("tab", parent=parent)
    qtbot.addWidget(wdg)

    wdg.load("curve1")

    assert parent.load_calls == ["curve1"]


def test_remove_delegates_to_parent(qtbot):
    parent = FakeParent()
    qtbot.addWidget(parent)
    wdg = DelegatingTabWidget("tab", parent=parent)
    qtbot.addWidget(wdg)

    wdg.remove("curve1")

    assert parent.remove_calls == ["curve1"]


def test_set_color_delegates_to_parent(qtbot):
    parent = FakeParent()
    qtbot.addWidget(parent)
    wdg = DelegatingTabWidget("tab", parent=parent)
    qtbot.addWidget(wdg)

    wdg.set_color("curve1", "blue")

    assert parent.set_color_calls == [("curve1", "blue")]


def test_preview_widget_returns_widget(qtbot):
    parent = FakeParent()
    qtbot.addWidget(parent)
    wdg = DelegatingTabWidget("tab", parent=parent)
    qtbot.addWidget(wdg)

    preview = wdg.preview_widget()

    assert isinstance(preview, QtWidgets.QWidget)
    assert preview.name == "preview"


def test_clear_widget_clears(qtbot):
    parent = FakeParent()
    qtbot.addWidget(parent)
    wdg = DelegatingTabWidget("tab", parent=parent)
    qtbot.addWidget(wdg)

    assert not getattr(wdg, "_cleared", False)
    wdg.clear_widget()
    assert wdg._cleared is True


def test_base_tab_widget_defaults():
    """The base TabWidget provides no-op defaults and None returns."""
    class BareTab(TabWidget):
        pass

    obj = BareTab("name")
    assert obj.name == "name"
    assert obj.new_curve() is None
    assert obj.preview_widget() is None
    assert obj.clear_widget() is None
    # load/remove/set_color return None (no-ops)
    assert obj.load("c") is None
    assert obj.remove("c") is None
    assert obj.set_color("c", "red") is None
