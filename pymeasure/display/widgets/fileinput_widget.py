#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

    def __init__(self, filename_input=True, directory_input=True, parent=None):
        super().__init__(parent)

        self._setup_ui(filename_input, directory_input)
        self._layout()

    def _setup_ui(self, enable_filename, enable_directory):
        if enable_filename:
            self.writefile_toggle = QtWidgets.QCheckBox('Write file', self)
            self.writefile_toggle.setLayoutDirection(QtCore.Qt.RightToLeft)
            self.writefile_toggle.setChecked(True)
            self.writefile_toggle.stateChanged.connect(self.toggle_file_dir_input_active)
            self.writefile_toggle.setToolTip(
                "Control whether the measurement is saved to a file with the filename that is\n"
                "specified in the field below (checked) or not (unchecked; the data is stored\n"
                "in a temporary file)."
            )

            self.filename_input = FilenameLineEdit(self.parent().procedure_class, parent=self)

        if enable_directory:
            self.directory_input = DirectoryLineEdit(parent=self)

    def _layout(self):
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)

        if hasattr(self, 'filename_input'):
            filename_label = QtWidgets.QLabel(self)
            filename_label.setText('Filename')
            filename_label.setToolTip(self.filename_input.toolTip())

            filename_box = QtWidgets.QHBoxLayout()
            filename_box.addWidget(filename_label)
            filename_box.addWidget(self.writefile_toggle)

            vbox.addLayout(filename_box)
            vbox.addWidget(self.filename_input)

        if hasattr(self, 'directory_input'):
            directory_label = QtWidgets.QLabel(self)
            directory_label.setText('Directory')

            vbox.addWidget(directory_label)
            vbox.addWidget(self.directory_input)

        self.setLayout(vbox)

    @property
    def directory(self):
        if not hasattr(self, 'directory_input'):
            raise ValueError("No directory input in the FileInputWidget")
        return self.directory_input.text()

    @directory.setter
    def directory(self, value):
        if not hasattr(self, 'directory_input'):
            raise ValueError("No directory input in the FileInputWidget")
        self.directory_input.setText(str(value))

    @property
    def filename(self):
        if not hasattr(self, 'filename_input'):
            raise ValueError("No filename input in the FileInputWidget")
        return self.filename_input.text()

    @filename.setter
    def filename(self, value):
        if not hasattr(self, 'filename_input'):
            raise ValueError("No filename input in the FileInputWidget")
        self.filename_input.setText(str(value))

    @property
    def store_measurement(self):
        if not hasattr(self, 'writefile_toggle'):
            raise ValueError("No write-file checkbox in the FileInputWidget")
        return self.writefile_toggle.isChecked()

    @store_measurement.setter
    def store_measurement(self, value):
        if not hasattr(self, 'writefile_toggle'):
            raise ValueError("No write-file checkbox in the FileInputWidget")
        self.writefile_toggle.setChecked(bool(value))

    def toggle_file_dir_input_active(self, state):
        if hasattr(self, 'directory_input'):
            self.filename_input.setEnabled(bool(state))
        if hasattr(self, 'filename_input'):
            self.directory_input.setEnabled(bool(state))
