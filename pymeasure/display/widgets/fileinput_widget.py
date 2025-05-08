#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from ..Qt import QtCore, QtWidgets
from .filename_widget import FilenameLineEdit
from .directory_widget import DirectoryLineEdit

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FileInputWidget(QtWidgets.QWidget):
    """
    Widget for controlling where the data of an experiment will be stored.

    The widget consists of a field for the filename
    (:class:`~pymeasure.display.widgets.filename_widget.FilenameLineEdit`), a field for the
    directory (:class:`~pymeasure.display.widgets.directory_widget.DirectoryLineEdit`), and a
    checkbox to control whether the measurement is stored.
    """
    _extensions = ["csv", "txt"]
    _filename_fixed = False

    def __init__(self, parent=None):
        super().__init__(parent)

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.writefile_toggle = QtWidgets.QCheckBox('Save data', self)
        self.writefile_toggle.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.writefile_toggle.setChecked(True)
        self.writefile_toggle.stateChanged.connect(self.set_input_fields_enabled)
        self.writefile_toggle.setToolTip(
            "Control whether the measurement is saved to a file with the filename that is\n"
            "specified in the field below (checked) or not (unchecked; the data is stored\n"
            "in a temporary file)."
        )

        self.filename_input = FilenameLineEdit(self.parent().procedure_class, parent=self)

        self.directory_input = DirectoryLineEdit(parent=self)

    def _layout(self):
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)

        filename_label = QtWidgets.QLabel(self)
        filename_label.setText('Filename')
        filename_label.setToolTip(self.filename_input.toolTip())

        filename_box = QtWidgets.QHBoxLayout()
        filename_box.addWidget(filename_label)
        filename_box.addWidget(self.writefile_toggle)

        vbox.addLayout(filename_box)
        vbox.addWidget(self.filename_input)

        directory_label = QtWidgets.QLabel(self)
        directory_label.setText('Directory')

        vbox.addWidget(directory_label)
        vbox.addWidget(self.directory_input)

        self.setLayout(vbox)

    @property
    def directory(self):
        """String controlling the directory where the file will be stored."""
        return self.directory_input.text()

    @directory.setter
    def directory(self, value):
        self.directory_input.setText(str(value))

    @property
    def filename(self):
        """String controlling the filename that is shown in the filename input field."""
        return self.filename_input.text()

    @filename.setter
    def filename(self, value):
        self.filename_input.setText(str(value))

    @property
    def filename_base(self):
        """String containing the base of the filename with which the file will be stored.
        Can only be read.
        """
        filename_split = self.filename.rsplit('.', 1)

        if len(filename_split) > 1 and filename_split[1] in self.extensions:
            return filename_split[0]
        else:
            return self.filename

    @property
    def filename_extension(self):
        """String containing the file extension with which the file will be stored.

        Can only be read.
        """
        filename_split = self.filename.rsplit('.', 1)

        if len(filename_split) > 1 and filename_split[1] in self.extensions:
            return filename_split[1]
        else:
            return self.extensions[0]

    @property
    def extensions(self):
        """List of extensions that are recognized by the widget.

        The first value of this list will be used as default value in case no extension is provided
        in the filename input field.
        """
        return self._extensions

    @extensions.setter
    def extensions(self, value):
        self._extensions = [ext.lstrip('.') for ext in value]
        self.filename_input.set_tool_tip()

    @property
    def store_measurement(self):
        """Boolean controlling whether the measurement will be stored."""
        return self.writefile_toggle.isChecked()

    @store_measurement.setter
    def store_measurement(self, value):
        self.writefile_toggle.setChecked(bool(value))

    @property
    def filename_fixed(self):
        """Boolean controlling whether the filename input field is frozen.
        If `True`, the filename field will be visible but disabled (i.e., grayed out)."""
        return self._filename_fixed

    @filename_fixed.setter
    def filename_fixed(self, value):
        self._filename_fixed = value

        # Reassess if the input fields should be enabled or disabled
        self.set_input_fields_enabled(self.store_measurement)

    def set_input_fields_enabled(self, state):
        self.filename_input.setEnabled(bool(state) and not self.filename_fixed)
        self.directory_input.setEnabled(bool(state))
