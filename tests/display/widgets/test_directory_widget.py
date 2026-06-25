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

from pymeasure.display.widgets.directory_widget import DirectoryLineEdit


def test_directory_line_edit_init(qtbot):
    """Test that a DirectoryLineEdit can be instantiated."""
    widget = DirectoryLineEdit()
    qtbot.addWidget(widget)
    assert widget.text() == ""
    # A completer is configured
    assert widget.completer() is not None


def test_get_starting_directory_empty(qtbot):
    """Test that an empty text returns the default root path."""
    widget = DirectoryLineEdit()
    qtbot.addWidget(widget)
    assert widget._get_starting_directory() == "/"


def test_get_starting_directory_existing_path(qtbot, tmp_path):
    """Test that a valid existing directory text is returned."""
    widget = DirectoryLineEdit()
    qtbot.addWidget(widget)
    widget.setText(str(tmp_path))
    assert widget._get_starting_directory() == str(tmp_path)


def test_get_starting_directory_nonexistent_path(qtbot):
    """Test that a nonexistent path falls back to the default root."""
    widget = DirectoryLineEdit()
    qtbot.addWidget(widget)
    widget.setText("/nonexistent_path_does_not_exist")
    assert widget._get_starting_directory() == "/"


def test_browse_triggered_opens_dialog(qtbot, tmp_path):
    """Test that browse_triggered opens a QFileDialog and updates the text."""
    widget = DirectoryLineEdit()
    qtbot.addWidget(widget)

    with mock.patch(
        "pymeasure.display.widgets.directory_widget.QtWidgets.QFileDialog"
    ) as mock_filedialog:
        mock_filedialog.getExistingDirectory.return_value = str(tmp_path)
        widget.browse_triggered()

    mock_filedialog.getExistingDirectory.assert_called_once()
    assert widget.text() == str(tmp_path)


def test_browse_triggered_canceled(qtbot):
    """Test that a canceled dialog does not modify the text."""
    widget = DirectoryLineEdit()
    qtbot.addWidget(widget)

    with mock.patch(
        "pymeasure.display.widgets.directory_widget.QtWidgets.QFileDialog"
    ) as mock_filedialog:
        mock_filedialog.getExistingDirectory.return_value = ""
        widget.browse_triggered()

    mock_filedialog.getExistingDirectory.assert_called_once()
    assert widget.text() == ""
