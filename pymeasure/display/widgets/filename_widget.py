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
import re

from ..Qt import QtCore, QtWidgets, QtGui

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

        self.setToolTip(
            "The filename of the file to which the measurement will be stored. Placeholders (in \n"
            "standard python format, i.e.: '{variablename:formatspec}') will be replaced by \n"
            "the respective value. If the filename does not contain an extension, \".csv\" will\n"
            "be append.\n\nValid placeholders are:\n- '" + "';\n- '".join(placeholders) + "'."
        )

        completer = PlaceholderCompleter(placeholders)
        self.setCompleter(completer)

        validator = FilenameValidator(placeholders, self)
        self.setValidator(validator)


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
            options = [path + placeholder + "}" for placeholder in self.placeholders]
            model = QtCore.QStringListModel(options)
            self.setModel(model)
        elif path.count("{") == path.count("}"):
            # Clear the autocomplete options
            self.setModel(QtCore.QStringListModel())

        return [path]


class FilenameValidator(QtGui.QValidator):
    def __init__(self, placeholders, parent):
        self.parent = parent
        self.placeholders = placeholders

        self.full_placeholder = re.compile(r"{([^{}:]*)(:[^{}]*)?}")
        self.half_placeholder = re.compile(r"{([^{}:]*)(:[^{}]*)?$")
        self.valid_filename = re.compile(r"^[^<>:\"/\\|?*{}]*$")
        super().__init__()

    def fixup(self, input):
        half_placeholder = self.half_placeholder.findall(input)

        if half_placeholder:
            input = input + "}"

        return input

    def validate(self, input, pos):
        test_input = input

        full_placeholders = self.full_placeholder.findall(input)
        half_placeholder = self.half_placeholder.findall(input)

        test_input = self.full_placeholder.sub("_plchldr_", test_input)
        test_input = self.half_placeholder.sub("_plchldr", test_input)

        valid_filename = self.valid_filename.fullmatch(test_input)

        # Determine state of input
        if not valid_filename:
            state = QtGui.QValidator.Invalid
        elif half_placeholder:
            state = QtGui.QValidator.Intermediate
        else:
            state = QtGui.QValidator.Acceptable

        # Control the warning for the invalid placeholders
        incorrect_placeholders = [p for p in full_placeholders if p[0] not in self.placeholders]
        if incorrect_placeholders:
            if not self.parent.actions():
                pixmapi = QtWidgets.QStyle.StandardPixmap.SP_MessageBoxWarning
                icon = self.parent.style().standardIcon(pixmapi)
                self.parent.addAction(icon, self.parent.ActionPosition.TrailingPosition)

            # Add tooltip to show which placeholders are not valid
            act = self.parent.actions()[0]

            marked_input = input
            for placeholder in [f"{{{p[0] + p[1]}}}" for p in incorrect_placeholders]:
                marked_input = marked_input.replace(placeholder, f"<b>{placeholder}</b>")

            act.setToolTip(
                "The input filename contains placeholders with invalid variable names:\n"
                " - '" + "', \n - '".join([p[0] for p in incorrect_placeholders]) + "'."
            )
        else:
            # Remove action, if it exists
            if self.parent.actions():
                assert len(self.parent.actions()) == 1, "More than 1 action defined, not sure which to remove."
                self.parent.removeAction(self.parent.actions()[0])

        return state, input, pos
