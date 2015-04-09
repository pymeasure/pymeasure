#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands
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

import sys
import os

default_variant = 'PyQt4'

env_api = os.environ.get('QT_API', 'pyqt')
if '--pyside' in sys.argv:
    variant = 'PySide'
elif '--pyqt4' in sys.argv:
    variant = 'PyQt4'
elif env_api == 'pyside':
    variant = 'PySide'
elif env_api == 'pyqt':
    variant = 'PyQt4'
else:
    variant = default_variant

if variant == 'PySide':
    from PySide import QtGui, QtCore
    os.environ['QT_API'] = 'pyside'
    QtCore.QSignal = QtCore.Signal

    def QtLoadUI(uifile, custom_widgets=None):
        from PySide import QtUiTools
        loader = QtUiTools.QUiLoader()
        if custom_widgets is not None:
            for widget in custom_widgets:
                loader.registerCustomWidget(widget)
        uif = QtCore.QFile(uifile)
        uif.open(QtCore.QFile.ReadOnly)
        result = loader.load(uif)
        uif.close()
        return result

elif variant == 'PyQt4':
    import sip
    api2_classes = [
            'QData', 'QDateTime', 'QString', 'QTextStream',
            'QTime', 'QUrl', 'QVariant',
            ]
    for cl in api2_classes:
        sip.setapi(cl, 2)
    from PyQt4 import QtGui, QtCore
    QtCore.QSignal = QtCore.pyqtSignal
    QtCore.QString = str
    os.environ['QT_API'] = 'pyqt'

    def QtLoadUI(uifile, custom_widgets=None):
        from PyQt4 import uic
        return uic.loadUi(uifile)
    QtCore.Qt.Checked = 2
else:
    raise ImportError("Python Variant not specified")

__all__ = [QtGui, QtCore, QtLoadUI, variant]