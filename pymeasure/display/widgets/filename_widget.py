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
import re
import textwrap

from ..Qt import QtCore, QtWidgets, QtGui

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FilenameLineEdit(QtWidgets.QLineEdit):
    """
    Widget that allows to choose a filename.
    A completer is implemented for quick completion of placeholders
    """

    def __init__(self, procedure_class, parent=None):
        super().__init__("DATA", parent=parent)

        self.placeholders = procedure_class.placeholder_names()
        self.placeholders.extend(["date", "time"])

        completer = PlaceholderCompleter(self.placeholders)
        self.setCompleter(completer)

        validator = FilenameValidator(self.placeholders, self)
        self.setValidator(validator)

        self.set_tool_tip()

    def set_tool_tip(self):
        ext = self.parent().extensions[0]
        extensions = ("'." + "', '.".join(self.parent().extensions[:-1]) +
                      f"', or '.{self.parent().extensions[-1]}'")
        placeholders = "'" + "';\n- '".join(self.placeholders) + "'"
        self.setToolTip("\n".join(textwrap.wrap(
            "The filename of the file to which the measurement will be stored. Placeholders (in "
            "standard python format, i.e.: '{variable name:formatspec}') will be replaced by "
            f"the respective value. The extension '.{ext}' will be appended, unless an extension "
            f"(one of {extensions}) is recognized. Additionally, an index number ('_#') is "
            "added to ensure the uniqueness of the filename.", width=100)) +
            f"\nValid placeholders are:\n- {placeholders}."
        )


class PlaceholderCompleter(QtWidgets.QCompleter):
    def __init__(self, placeholders):
        super().__init__()
        self.placeholders = placeholders

        self.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        self.setModelSorting(QtWidgets.QCompleter.ModelSorting.CaseInsensitivelySortedModel)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setFilterMode(QtCore.Qt.MatchContains)

    def splitPath(self, path):
        if path.endswith("{"):
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
                pixmapi = QtWidgets.QStyle.StandardPixmap.SP_MessageBoxCritical
                icon = self.parent.style().standardIcon(pixmapi)
                self.parent.addAction(icon, self.parent.ActionPosition.TrailingPosition)

            # Add tooltip to show which placeholders are not valid
            act = self.parent.actions()[0]

            marked_input = input
            for placeholder in [f"{{{p[0] + p[1]}}}" for p in incorrect_placeholders]:
                marked_input = marked_input.replace(
                    placeholder, f"<b><font color='red'>{placeholder}</font></b>"
                )

            act.setToolTip(
                "<p style='white-space:pre'>"
                "The input filename contains placeholders with<br/>invalid variable names:<br/>"
                " - '" + "',<br/> - '".join([p[0] for p in incorrect_placeholders]) + "'."
                "<br/><br/>Received input:<br/>" + marked_input + "</p>"
            )
        else:
            # Remove action, if it exists
            if self.parent.actions():
                assert len(self.parent.actions()) == 1, (
                    "More than 1 action defined, not sure " "which to remove."
                )
                self.parent.removeAction(self.parent.actions()[0])

        return state, input, pos
