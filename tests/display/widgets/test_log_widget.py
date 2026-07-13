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

import pytest

from pymeasure.display.Qt import QtGui, QtWidgets
from pymeasure.display.log import LogHandler
from pymeasure.display.widgets.log_widget import HTMLFormatter, LogWidget


def _make_record(level, msg="hello", name="test"):
    return logging.LogRecord(
        name=name, level=level, pathname="", lineno=0,
        msg=msg, args=None, exc_info=None,
    )


# --- HTMLFormatter ---


def test_html_formatter_prepends_level_comment():
    """HTMLFormatter prepends the level name as an HTML comment."""
    formatter = HTMLFormatter("%(message)s")
    record = _make_record(logging.INFO, "hello")
    assert formatter.format(record) == "<!--INFO-->hello"


def test_html_formatter_info_no_color():
    """INFO level has no color wrapping (not in level_colors)."""
    formatter = HTMLFormatter("%(message)s")
    record = _make_record(logging.INFO, "hello")
    formatted = formatter.format(record)
    assert "<font" not in formatted
    assert formatted.startswith("<!--INFO-->")


def test_html_formatter_warning_color():
    """WARNING level is wrapped in a DarkOrange font tag."""
    formatter = HTMLFormatter("%(message)s")
    record = _make_record(logging.WARNING, "careful")
    formatted = formatter.format(record)
    assert formatted.startswith("<!--WARNING--><font color=\"DarkOrange\">")
    assert formatted.endswith("</font>")
    assert "careful" in formatted


def test_html_formatter_error_color():
    """ERROR level is wrapped in a Red font tag."""
    formatter = HTMLFormatter("%(message)s")
    record = _make_record(logging.ERROR, "broken")
    formatted = formatter.format(record)
    assert formatted.startswith("<!--ERROR--><font color=\"Red\">")
    assert "broken" in formatted


def test_html_formatter_critical_color():
    """CRITICAL level is wrapped in a DarkRed font tag."""
    formatter = HTMLFormatter("%(message)s")
    record = _make_record(logging.CRITICAL, "boom")
    formatted = formatter.format(record)
    assert formatted.startswith("<!--CRITICAL--><font color=\"DarkRed\">")
    assert "boom" in formatted


def test_html_formatter_debug_color():
    """DEBUG level is wrapped in a DarkGray font tag."""
    formatter = HTMLFormatter("%(message)s")
    record = _make_record(logging.DEBUG, "trace")
    formatted = formatter.format(record)
    assert formatted.startswith("<!--DEBUG--><font color=\"DarkGray\">")
    assert "trace" in formatted


def test_html_formatter_newlines_replaced():
    """Newlines are replaced with <br> tags (with indentation)."""
    formatter = HTMLFormatter("%(message)s")
    record = _make_record(logging.INFO, "line1\nline2")
    formatted = formatter.format(record)
    assert "<br>" in formatted
    assert "\n" not in formatted
    assert "line1" in formatted
    assert "line2" in formatted


def test_html_formatter_carriage_return_newline_replaced():
    """CRLF sequences are replaced with <br> tags."""
    formatter = HTMLFormatter("%(message)s")
    record = _make_record(logging.INFO, "line1\r\nline2")
    formatted = formatter.format(record)
    assert "<br>" in formatted
    assert "\r" not in formatted
    assert "\n" not in formatted


def test_html_formatter_tab_replaced():
    """Tabs are replaced with non-breaking spaces."""
    formatter = HTMLFormatter("%(message)s")
    record = _make_record(logging.INFO, "a\tb")
    formatted = formatter.format(record)
    assert "&nbsp;" in formatted
    assert "\t" not in formatted


def test_html_formatter_double_space_replaced():
    """Double spaces are replaced with non-breaking spaces."""
    formatter = HTMLFormatter("%(message)s")
    record = _make_record(logging.INFO, "a  b")
    formatted = formatter.format(record)
    assert "&nbsp;&nbsp;" in formatted


# --- LogWidget.__init__ ---


def test_log_widget_init_stores_name(qtbot):
    """LogWidget.__init__ stores the name attribute."""
    wdg = LogWidget("Experiment Log")
    qtbot.addWidget(wdg)
    assert wdg.name == "Experiment Log"


def test_log_widget_init_default_fmt(qtbot):
    """LogWidget uses the default fmt when none is provided."""
    wdg = LogWidget("log")
    qtbot.addWidget(wdg)
    assert wdg.fmt == '%(asctime)s : %(message)s (%(levelname)s)'
    assert wdg.datefmt == '%m/%d/%Y %I:%M:%S %p'


def test_log_widget_init_custom_fmt(qtbot):
    """LogWidget accepts custom fmt and datefmt."""
    wdg = LogWidget("log", fmt="%(message)s", datefmt="%H:%M:%S")
    qtbot.addWidget(wdg)
    assert wdg.fmt == "%(message)s"
    assert wdg.datefmt == "%H:%M:%S"


# --- _setup_ui ---


def test_log_widget_setup_ui_creates_view(qtbot):
    """_setup_ui creates a read-only QPlainTextEdit as the view."""
    wdg = LogWidget("log")
    qtbot.addWidget(wdg)
    assert isinstance(wdg.view, QtWidgets.QPlainTextEdit)
    assert wdg.view.isReadOnly() is True


def test_log_widget_setup_ui_creates_handler(qtbot):
    """_setup_ui creates a LogHandler with an HTMLFormatter."""
    wdg = LogWidget("log")
    qtbot.addWidget(wdg)
    assert isinstance(wdg.handler, LogHandler)
    assert isinstance(wdg.handler.formatter, HTMLFormatter)


def test_log_widget_setup_ui_handler_fmt(qtbot):
    """The handler's formatter uses the widget's fmt and datefmt."""
    wdg = LogWidget("log", fmt="%(message)s", datefmt="%H:%M:%S")
    qtbot.addWidget(wdg)
    assert wdg.handler.formatter._fmt == "%(message)s"
    assert wdg.handler.formatter.datefmt == "%H:%M:%S"


# --- _layout ---


def test_log_widget_layout_contains_view(qtbot):
    """_layout arranges the view in a vertical box layout."""
    wdg = LogWidget("log")
    qtbot.addWidget(wdg)
    layout = wdg.layout()
    assert layout is not None
    assert layout.count() == 1
    item = layout.itemAt(0)
    assert item.widget() is wdg.view


def test_log_widget_layout_is_vbox(qtbot):
    """The widget's layout is a QVBoxLayout with zero spacing."""
    wdg = LogWidget("log")
    qtbot.addWidget(wdg)
    layout = wdg.layout()
    assert isinstance(layout, QtWidgets.QVBoxLayout)
    assert layout.spacing() == 0


# --- _blink / _blinking_start / _blinking_stop ---


class _TabHost(QtWidgets.QWidget):
    """Host widget containing a QTabWidget, to parent LogWidget correctly.

    Reproducing the structure in ManagedWindowBase: LogWidget is added via
    addTab, which reparents it to the QTabWidget's internal QStackedWidget, so
    log_widget.parent().parent() is the QTabWidget.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tabs = QtWidgets.QTabWidget(self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tabs)


@pytest.fixture
def tab_host(qtbot):
    """Return (host, log_widget) with LogWidget registered as a tab.

    The log tab is made non-current so blinking can start. The shared
    class-level blink state is reset before each test.
    """
    host = _TabHost()
    qtbot.addWidget(host)
    host.show()
    qtbot.waitExposed(host)

    log_widget = LogWidget("Experiment Log")
    host.tabs.addTab(log_widget, log_widget.name)

    # Add a second tab and make it current so the log tab is not active
    other = QtWidgets.QWidget()
    host.tabs.addTab(other, "other")
    host.tabs.setCurrentIndex(1)

    # Reset shared class-level blink state before each test
    LogWidget._blink_qtimer.stop()
    LogWidget._blink_color = None
    LogWidget._blink_state = False

    # Explicitly wire up tab_widget/tab_index (normally done lazily in
    # _blinking_start) so _blink and _blinking_stop can be tested directly.
    log_widget.tab_widget = host.tabs
    log_widget.tab_index = host.tabs.indexOf(log_widget)

    return host, log_widget


def test_blink_toggles_state(tab_host):
    """_blink toggles the _blink_state flag each call."""
    host, log_widget = tab_host
    log_widget._blink_color = "red"
    log_widget._blink_state = False

    log_widget._blink()
    assert log_widget._blink_state is True

    log_widget._blink()
    assert log_widget._blink_state is False


def test_blink_sets_tab_text_color(tab_host):
    """_blink sets the tab text color based on the blink state."""
    host, log_widget = tab_host
    log_widget._blink_color = "darkorange"
    log_widget._blink_state = False

    log_widget._blink()
    # When _blink_state is False, color is _blink_color (darkorange)
    expected = QtGui.QColor("darkorange")
    actual = host.tabs.tabBar().tabTextColor(log_widget.tab_index)
    assert actual.red() == expected.red()
    assert actual.green() == expected.green()
    assert actual.blue() == expected.blue()


def test_blink_sets_black_when_state_true(tab_host):
    """_blink sets black text color when _blink_state is True."""
    host, log_widget = tab_host
    log_widget._blink_color = "red"
    log_widget._blink_state = True

    log_widget._blink()
    expected = QtGui.QColor("black")
    actual = host.tabs.tabBar().tabTextColor(log_widget.tab_index)
    assert actual.red() == expected.red()
    assert actual.green() == expected.green()
    assert actual.blue() == expected.blue()


def test_blinking_start_warning_sets_orange(tab_host):
    """_blinking_start with a WARNING message sets the blink color to darkorange."""
    host, log_widget = tab_host
    assert host.tabs.currentIndex() != log_widget.tab_index

    log_widget._blinking_start("<!--WARNING-->careful")

    assert log_widget._blink_color == "darkorange"
    assert log_widget._blink_qtimer.isActive()


def test_blinking_start_error_sets_red(tab_host):
    """_blinking_start with an ERROR message sets the blink color to red."""
    host, log_widget = tab_host
    assert host.tabs.currentIndex() != log_widget.tab_index

    log_widget._blinking_start("<!--ERROR-->broken")

    assert log_widget._blink_color == "red"
    assert log_widget._blink_qtimer.isActive()


def test_blinking_start_critical_sets_red(tab_host):
    """_blinking_start with a CRITICAL message sets the blink color to red."""
    host, log_widget = tab_host
    assert host.tabs.currentIndex() != log_widget.tab_index

    log_widget._blinking_start("<!--CRITICAL-->boom")

    assert log_widget._blink_color == "red"
    assert log_widget._blink_qtimer.isActive()


def test_blinking_start_info_no_blinking(tab_host):
    """_blinking_start with an INFO message does not start blinking."""
    host, log_widget = tab_host

    log_widget._blinking_start("<!--INFO-->hello")

    assert log_widget._blink_color is None
    assert not log_widget._blink_qtimer.isActive()


def test_blinking_start_when_current_tab_stops(tab_host):
    """_blinking_start stops immediately if the log tab is currently selected."""
    host, log_widget = tab_host
    # Make the log tab the current tab
    host.tabs.setCurrentIndex(log_widget.tab_index)

    log_widget._blink_color = "red"  # pretend blinking was active
    log_widget._blinking_start("<!--ERROR-->broken")

    # _blinking_stop should have been called: color reset, timer stopped
    assert log_widget._blink_color is None
    assert not log_widget._blink_qtimer.isActive()


def test_blinking_stop_resets_state(tab_host):
    """_blinking_stop resets the blink color and stops the timer."""
    host, log_widget = tab_host
    log_widget._blink_color = "red"
    log_widget._blink_qtimer.start(500)
    assert log_widget._blink_qtimer.isActive()

    log_widget._blinking_stop(log_widget.tab_index)

    assert log_widget._blink_color is None
    assert not log_widget._blink_qtimer.isActive()


def test_blinking_stop_ignores_other_index(tab_host):
    """_blinking_stop does nothing if the index is not the log tab index."""
    host, log_widget = tab_host
    log_widget._blink_color = "red"
    log_widget._blink_qtimer.start(500)

    log_widget._blinking_stop(log_widget.tab_index + 999)

    assert log_widget._blink_color == "red"
    assert log_widget._blink_qtimer.isActive()


def test_blinking_start_sets_tab_widget_once(tab_host):
    """_blinking_start lazily discovers the tab_widget on first call."""
    host, log_widget = tab_host
    # Force re-discovery by clearing tab_widget
    log_widget.tab_widget = None

    log_widget._blinking_start("<!--ERROR-->broken")

    assert log_widget.tab_widget is host.tabs
    assert log_widget.tab_index == host.tabs.indexOf(log_widget)


# --- Integration: logger -> handler -> widget ---


def _make_hosted_log_widget(qtbot, name="log", fmt="%(message)s"):
    """Build a LogWidget registered as a tab in a QTabWidget and return both.

    Placing the widget in a QTabWidget gives it the parent chain expected by
    _blinking_start (log_widget.parent().parent() == QTabWidget). The returned
    host must be kept alive for the duration of the test.
    """
    host = _TabHost()
    qtbot.addWidget(host)
    host.show()
    qtbot.waitExposed(host)

    log_widget = LogWidget(name, fmt=fmt)
    host.tabs.addTab(log_widget, log_widget.name)

    LogWidget._blink_qtimer.stop()
    LogWidget._blink_color = None
    LogWidget._blink_state = False
    log_widget.tab_widget = host.tabs
    log_widget.tab_index = host.tabs.indexOf(log_widget)

    return host, log_widget


def test_log_widget_integration_text_appears(qtbot):
    """A record emitted on a logger appears in the widget's view."""
    host, wdg = _make_hosted_log_widget(qtbot)

    logger = logging.getLogger("pymeasure.test_log_widget_integration")
    logger.setLevel(logging.DEBUG)
    # Remove handlers from any prior test runs
    logger.handlers = []
    logger.addHandler(wdg.handler)

    try:
        logger.info("integration message")
    finally:
        logger.removeHandler(wdg.handler)

    text = wdg.view.toPlainText()
    assert "integration message" in text


def test_log_widget_integration_warning_color_emitted(qtbot):
    """A WARNING record is formatted with the DarkOrange color before appending."""
    host, wdg = _make_hosted_log_widget(qtbot)

    received = []
    wdg.handler.connect(received.append)

    logger = logging.getLogger("pymeasure.test_log_widget_warning")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(wdg.handler)

    try:
        logger.warning("careful")
    finally:
        logger.removeHandler(wdg.handler)

    assert any("DarkOrange" in msg for msg in received)
    assert any("careful" in msg for msg in received)


def test_log_widget_integration_multiple_records(qtbot):
    """Multiple records are appended in order to the view."""
    host, wdg = _make_hosted_log_widget(qtbot)

    logger = logging.getLogger("pymeasure.test_log_widget_multi")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(wdg.handler)

    try:
        logger.info("first")
        logger.error("second")
    finally:
        logger.removeHandler(wdg.handler)

    text = wdg.view.toPlainText()
    assert "first" in text
    assert "second" in text
    assert text.index("first") < text.index("second")
