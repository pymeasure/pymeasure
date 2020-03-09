#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

from pyqtgraph.Qt import QtGui, QtCore, loadUiType

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

QtCore.QSignal = QtCore.pyqtSignal


def fromUi(*args, **kwargs):
    """ Returns a Qt object constructed using loadUiType
    based on its arguments. All QWidget objects in the
    form class are set in the returned object for easy
    accessability.
    """
    form_class, base_class = loadUiType(*args, **kwargs)
    widget = base_class()
    form = form_class()
    form.setupUi(widget)
    form.retranslateUi(widget)
    for name in dir(form):
        element = getattr(form, name)
        if isinstance(element, QtGui.QWidget):
            setattr(widget, name, element)
    return widget

def qt_min_version(major, minor=0):
    """
    Check for a minimum Qt version. For example, to check for version 4.11
    or later, call ``check_qt_version(4, 11)``.

    :return bool: True if PyQt version >= min_version
    """
    return (QtCore.QT_VERSION >= ((major << 16) + (minor << 8)))

