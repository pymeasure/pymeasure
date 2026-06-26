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

from qtpy import QtWidgets

from pymeasure.display.Qt import fromUi


# A QDialog with a child QPushButton named "myButton" and a QVBoxLayout
# (a QLayout, not a QWidget) to verify only widgets are exposed as attributes.
UI_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Dialog</class>
 <widget class="QDialog" name="Dialog">
  <layout class="QVBoxLayout" name="verticalLayout">
   <item>
    <widget class="QPushButton" name="myButton">
     <property name="text">
      <string>Click me</string>
     </property>
    </widget>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections/>
</ui>
"""


def _write_ui(tmp_path):
    path = tmp_path / "test_fromUi.ui"
    path.write_text(UI_TEMPLATE)
    return path


def test_fromUi_returns_widget_with_form_children(qtbot, tmp_path):
    path = _write_ui(tmp_path)
    widget = fromUi(str(path))
    assert isinstance(widget, QtWidgets.QDialog)
    assert hasattr(widget, "myButton")
    assert isinstance(widget.myButton, QtWidgets.QPushButton)


def test_fromUi_sets_attributes_for_qwidgets_only(qtbot, tmp_path):
    path = _write_ui(tmp_path)
    widget = fromUi(str(path))
    # The button is a QWidget and is exposed as an attribute.
    assert isinstance(widget.myButton, QtWidgets.QWidget)
    # The layout is a QLayout (not a QWidget) and must not be exposed.
    assert not hasattr(widget, "verticalLayout")


def test_fromUi_calls_setupUi_and_retranslateUi(qtbot, tmp_path):
    path = _write_ui(tmp_path)
    widget = fromUi(str(path))
    # setupUi reparents the button under the dialog, so it is found among children.
    assert widget.findChild(QtWidgets.QPushButton, "myButton") is widget.myButton
    # retranslateUi sets the button text; the widget is usable after being shown.
    with qtbot.waitExposed(widget):
        widget.show()
    assert widget.myButton.text() == "Click me"
