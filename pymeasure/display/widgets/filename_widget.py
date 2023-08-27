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

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FilenameLineEdit(QtWidgets.QLineEdit):
    """
    Widget that allows to choose a filename.
    A completer is implemented for quick completion of placeholders
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        placeholders = parent.procedure_class.placeholder_names()
        completer = PlaceholderCompleter(placeholders)
        self.setCompleter(completer)


class PlaceholderCompleter(QtWidgets.QCompleter):

    def __init__(self, placeholders):
        super().__init__()
        self.placeholders = placeholders

        self.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        self.setModelSorting(QtWidgets.QCompleter.ModelSorting.CaseInsensitivelySortedModel)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setFilterMode(QtCore.Qt.MatchContains)

    def splitPath(self, path):
        if path.endswith('{'):
            options = [path + placeholder for placeholder in self.placeholders]
            model = QtCore.QStringListModel(options)
            self.setModel(model)
        elif path.count("{") == path.count("}"):
            # Clear the autocomplete options
            self.setModel(QtCore.QStringListModel())

        return [path]
