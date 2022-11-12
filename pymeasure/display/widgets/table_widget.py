#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
import numpy
from os.path import basename

import pyqtgraph as pg

from ..Qt import QtCore, QtWidgets, QtGui
from .tab_widget import TabWidget
from ...experiment import Procedure

SORT_ROLE = QtCore.Qt.UserRole + 1

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, results, float_digits=12, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.results = results
        self.float_digits = float_digits
        self._data = self.results.data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            value = self._data.iloc[index.row()][index.column()]
            column_type = self._data.dtypes[index.column()]
            # Cast to column type
            value_render = column_type.type(value)
            if isinstance(value_render, numpy.float64):
                value_render = f"{value_render:.{self.float_digits:d}f}"
            if role == QtCore.Qt.DisplayRole:
                return (str(value_render))
            elif role == SORT_ROLE:
                # For numerical sort
                return value
        return None

    def headerData(
        self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.ItemDataRole
    ):
        """Override method from QAbstractTableModel

        Return dataframe index as vertical header data and columns as horizontal header data.
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == QtCore.Qt.Vertical:
                return str(self._data.index[section])

        return None


class Table(QtWidgets.QTableView):
    """Graphical list view of :class:`Experiment<pymeasure.display.manager.Experiment>`
    objects allowing the user to view the status of queued Experiments as well as
    loading and displaying data from previous runs.

    In order that different Experiments be displayed within the same Browser,
    they must have entries in `DATA_COLUMNS` corresponding to the
    `measured_quantities` of the Browser.
    """

    def __init__(self, results, color, force_reload=False, float_digits=6, parent=None):
        super().__init__(parent)
        self.results = results
        self.set_color(color)
        self.force_reload = force_reload
        self.float_digits = float_digits
        self.name = basename(self.results.data_filename)
        model = PandasModel(self.results, float_digits=self.float_digits)
        proxyModel = QtCore.QSortFilterProxyModel()
        proxyModel.setSourceModel(model)
        model = proxyModel
        self.setModel(model)
        self.horizontalHeader().setStyleSheet("font: bold;")
        model.setSortRole(SORT_ROLE)
        self.setSortingEnabled(True)
        self.horizontalHeader().setSectionsMovable(True)

    def update_data(self):
        """Updates the data by polling the results"""
        if self.force_reload:
            self.results.reload()
        model = self.model().sourceModel()
        new_data = self.results.data
        new_rows = len(new_data.values) - model.rowCount()
        if new_rows > 0:
            # New rows available
            model.beginInsertRows(QtCore.QModelIndex(), model.rowCount(),
                                  model.rowCount() + new_rows - 1)
            model._data = new_data
            model.endInsertRows()

    def set_color(self, color):
        self.color = color


class MultiTable(QtWidgets.QTabWidget):
    """ Display a set of experiments in a spreadsheet like fashion
    """

    def __init__(self, refresh_time=0.2, check_status=True, parent=None):
        super().__init__(parent)
        self.refresh_time = refresh_time
        self.check_status = check_status
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_tables)
        self.timer.start(int(self.refresh_time * 1e3))
        self.setTabPosition(QtWidgets.QTabWidget.South)

    def update_tables(self):
        for index in range(self.count()):
            item = self.widget(index)
            if self.check_status:
                if item.results.procedure.status == Procedure.RUNNING:
                    item.update_data()
            else:
                item.update_data()

    def addTable(self, table):
        self.addTab(table, table.name)
        self.set_color(table)
        header = table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

    def removeTable(self, table):
        self.removeTab(self.indexOf(table))

    def set_color(self, table, color=None):
        if color is not None:
            table.set_color(color)
        tab_index = self.indexOf(table)
        pixelmap = QtGui.QPixmap(12, 12)
        pixelmap.fill(table.color)
        self.setTabIcon(tab_index, QtGui.QIcon(pixelmap))


class TableWidget(TabWidget, QtWidgets.QWidget):
    """ Widget to display experiment data in a tabular format
    """

    def __init__(self, name, columns, refresh_time=0.2,
                 check_status=True, float_digits=6, parent=None):
        super().__init__(name, parent)
        self.columns = columns
        self.refresh_time = refresh_time
        self.float_digits = float_digits
        self.check_status = check_status
        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.tables = MultiTable()

    def _layout(self):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(0)

        vbox.addWidget(self.tables)
        self.setLayout(vbox)

    def sizeHint(self):
        return QtCore.QSize(300, 600)

    def new_curve(self, results, color=pg.intColor(0), **kwargs):
        kwargs.setdefault("float_digits", self.float_digits)
        return Table(results, color, **kwargs)

    def load(self, table):
        self.tables.addTable(table)

    def remove(self, table):
        self.tables.removeTable(table)

    def set_color(self, table, color):
        """ Change the color of the pen of the curve """
        self.tables.set_color(table, color)
