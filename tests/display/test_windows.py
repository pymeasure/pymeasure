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

import pytest
from unittest import mock

from pymeasure.display.Qt import QtGui, QtCore
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment.procedure import Procedure

# TODO: Repair this unit test
# class TestManagedWindow:
#     # TODO: More thorough unit (or integration?) tests.
# 
#     # TODO: Could we make this more testable? These patches are a bit ridiculous.
#     @mock.patch('pymeasure.display.windows.Manager')
#     @mock.patch('pymeasure.display.windows.InputsWidget')
#     @mock.patch('pymeasure.display.windows.BrowserWidget')
#     @mock.patch('pymeasure.display.windows.PlotWidget')
#     @mock.patch('pymeasure.display.windows.QtGui')
#     @mock.patch.object(ManagedWindow, 'setCentralWidget')
#     @mock.patch.object(ManagedWindow, 'addDockWidget')
#     @mock.patch.object(ManagedWindow, 'setup_plot')
#     def test_setup_plot_called_on_init(self, mock_sp, mock_a, mock_b,
#             MockQtGui, MockPlotWidget, MockBrowserWidget, MockInputsWidget,
#             MockManager, qtbot):
#         mock_procedure = mock.MagicMock(spec=Procedure)
#         w = ManagedWindow(mock_procedure)
#         qtbot.addWidget(w)
#         mock_sp.assert_called_once_with(w.plot)
