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

import pytest

from pymeasure.display.Qt import QtWidgets
from pymeasure.display.widgets.browser_widget import BrowserWidget
from pymeasure.display.browser import Browser


@pytest.fixture
def mock_procedure_class():
    """A MagicMock procedure class with named parameters for Browser construction."""
    procedure_class = mock.MagicMock()
    param_voltage = mock.MagicMock()
    param_voltage.name = "Voltage"
    param_current = mock.MagicMock()
    param_current.name = "Current"
    procedure_class.voltage_param = param_voltage
    procedure_class.current_param = param_current
    return procedure_class


@pytest.fixture
def browser_widget(mock_procedure_class, qtbot):
    """Create a BrowserWidget with a mocked procedure class."""
    widget = BrowserWidget(
        mock_procedure_class,
        ["voltage_param", "current_param"],
        ["voltage", "current"],
    )
    qtbot.addWidget(widget)
    return widget


class TestBrowserWidgetInit:
    """Tests for BrowserWidget.__init__."""

    def test_init_builds_browser_with_header_labels(
        self, mock_procedure_class, qtbot
    ):
        """BrowserWidget builds a Browser tree with header labels from args."""
        widget = BrowserWidget(
            mock_procedure_class,
            ["voltage_param", "current_param"],
            ["voltage", "current"],
        )
        qtbot.addWidget(widget)

        assert isinstance(widget.browser, Browser)
        assert widget.browser.columnCount() == 6
        header_labels = [
            widget.browser.headerItem().text(i)
            for i in range(widget.browser.columnCount())
        ]
        assert header_labels == [
            "Graph", "Filename", "Progress", "Status", "Voltage", "Current",
        ]

    def test_init_stores_browser_args(self, mock_procedure_class, qtbot):
        """BrowserWidget stores the positional args for the Browser."""
        widget = BrowserWidget(
            mock_procedure_class,
            ["voltage_param"],
            ["voltage"],
        )
        qtbot.addWidget(widget)

        assert widget.browser_args == (
            mock_procedure_class, ["voltage_param"], ["voltage"],
        )

    def test_init_creates_all_buttons(self, browser_widget):
        """BrowserWidget creates the four control buttons."""
        assert isinstance(browser_widget.clear_button, QtWidgets.QPushButton)
        assert isinstance(browser_widget.hide_button, QtWidgets.QPushButton)
        assert isinstance(browser_widget.show_button, QtWidgets.QPushButton)
        assert isinstance(browser_widget.open_button, QtWidgets.QPushButton)

    def test_init_button_labels(self, browser_widget):
        """Buttons are labeled as defined in _setup_ui."""
        assert browser_widget.clear_button.text() == "Clear all"
        assert browser_widget.hide_button.text() == "Hide all"
        assert browser_widget.show_button.text() == "Show all"
        assert browser_widget.open_button.text() == "Open"

    def test_init_button_enabled_states(self, browser_widget):
        """Clear/Hide/Show buttons start disabled; Open button starts enabled."""
        assert browser_widget.clear_button.isEnabled() is False
        assert browser_widget.hide_button.isEnabled() is False
        assert browser_widget.show_button.isEnabled() is False
        assert browser_widget.open_button.isEnabled() is True


class TestBrowserWidgetSetupUi:
    """Tests for BrowserWidget._setup_ui."""

    def test_setup_ui_creates_browser_child(self, browser_widget):
        """_setup_ui instantiates a Browser as a child widget."""
        assert browser_widget.browser.parent() is browser_widget

    def test_setup_ui_creates_clear_button_as_child(self, browser_widget):
        """_setup_ui creates the clear_button as a child widget."""
        assert browser_widget.clear_button.parent() is browser_widget

    def test_setup_ui_creates_hide_button_as_child(self, browser_widget):
        """_setup_ui creates the hide_button as a child widget."""
        assert browser_widget.hide_button.parent() is browser_widget

    def test_setup_ui_creates_show_button_as_child(self, browser_widget):
        """_setup_ui creates the show_button as a child widget."""
        assert browser_widget.show_button.parent() is browser_widget

    def test_setup_ui_creates_open_button_as_child(self, browser_widget):
        """_setup_ui creates the open_button as a child widget."""
        assert browser_widget.open_button.parent() is browser_widget


class TestBrowserWidgetLayout:
    """Tests for BrowserWidget._layout."""

    def test_layout_sets_top_level_layout(self, browser_widget):
        """_layout sets a QVBoxLayout as the top-level layout."""
        layout = browser_widget.layout()
        assert isinstance(layout, QtWidgets.QVBoxLayout)

    def test_layout_vbox_spacing_is_zero(self, browser_widget):
        """The outer vbox layout has zero spacing."""
        assert browser_widget.layout().spacing() == 0

    def test_layout_has_hbox_with_buttons(self, browser_widget):
        """_layout nests an hbox containing show/hide/clear/open buttons."""
        layout = browser_widget.layout()
        hbox = layout.itemAt(0).layout()
        assert isinstance(hbox, QtWidgets.QHBoxLayout)
        assert hbox.spacing() == 10

    def test_layout_hbox_contents_margins(self, browser_widget):
        """The hbox contents margins have top=6 and bottom=6."""
        hbox = browser_widget.layout().itemAt(0).layout()
        margins = hbox.contentsMargins()
        assert margins.top() == 6
        assert margins.bottom() == 6

    def test_layout_hbox_contains_show_hide_clear_open(self, browser_widget):
        """The hbox contains show, hide, clear buttons (in that order), then open."""
        hbox = browser_widget.layout().itemAt(0).layout()
        widgets = [item.widget() for item in [hbox.itemAt(i) for i in range(hbox.count())]
                   if item is not None and item.widget() is not None]
        assert widgets[0] is browser_widget.show_button
        assert widgets[1] is browser_widget.hide_button
        assert widgets[2] is browser_widget.clear_button
        # hbox.itemAt(3) is the stretch (addStretch)
        assert widgets[-1] is browser_widget.open_button

    def test_layout_browser_added_to_vbox(self, browser_widget):
        """The browser tree widget is added to the vbox after the hbox."""
        layout = browser_widget.layout()
        # itemAt(0) is the hbox, itemAt(1) should be the browser widget.
        browser_item = layout.itemAt(1)
        assert browser_item.widget() is browser_widget.browser
