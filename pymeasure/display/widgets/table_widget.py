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
from numpy import float64, NaN
from functools import partial
import pyqtgraph as pg
import pandas as pd

from ..Qt import QtCore, QtWidgets, QtGui
from .tab_widget import TabWidget
from ...experiment import Procedure

SORT_ROLE = QtCore.Qt.ItemDataRole.UserRole + 1
SORTING_ENABLED = True

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ResultsTable(QtCore.QObject):
    """ Class representing a panda dataframe """
    data_changed = QtCore.Signal(int, int, int, int)

    def __init__(self, results, color, float_digits, force_reload=False, wdg=None, **kwargs):
        super().__init__()
        self.results = results
        self.color = color
        self.force_reload = force_reload
        self.last_row_count = 0
        self.float_digits = float_digits
        self.wdg = wdg
        self._data = self.results.data
        self._started = False

    @property
    def data(self):
        return self._data

    @property
    def rows(self):
        return self._data.shape[0]

    @property
    def columns(self):
        return self._data.shape[1]

    def init(self):
        self.last_row_count = 0

    def start(self):
        self._started = True

    def stop(self):
        self._started = False

    def update_data(self):
        if not self._started:
            return
        if self.force_reload:
            self.results.reload()
        self._data = self.results.data
        current_row_count, columns = self._data.shape
        if (self.last_row_count < current_row_count):
            # Request cells content update
            self.data_changed.emit(self.last_row_count, 0,
                                   current_row_count - 1, columns - 1)
            self.last_row_count = current_row_count

    def set_color(self, color):
        self.color = color


class PandasModelBase(QtCore.QAbstractTableModel):
    """ This class provided a model to manage multiple panda dataframes and
    display them as a single table.

    The multiple pandas dataframes are provided as ResultTable class instances
    and all of them share the same number of columns.

    There are some assumptions:
    - Series in the dataframe are identical, we call this number k
    - Series length can be different, we call this number l(x), where x=1..n

    The data can be presented as follow:
    - By column: each series in a separate column, in this case table shape
    will be: (k*n) x (max(l(x) x=1..n)
    - By row: column fixed to the number of series, in this case table shape
    will be: k x (sum of l(x) x=1..n)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_data()

    def _init_data(self):
        self.results_list = []
        self.row_count = 0
        self.column_count = 0

    def clear(self):
        self.beginResetModel()
        for results in self.results_list:
            results.stop()
        self._init_data()
        self.endResetModel()

    def add_results(self, results):
        if results not in self.results_list:
            self.results_list.append(results)
            results.data_changed.connect(partial(self._data_changed, results))
            self.layoutChanged.emit()
            results.init()
            results.start()
            results.update_data()

    def remove_results(self, results):
        if results in self.results_list:
            self.results_list.remove(results)
        self.row_count = self.pandas_row_count()
        self.column_count = self.pandas_column_count()
        results.stop()
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self.row_count

    def columnCount(self, parent=None):
        return self.column_count

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if index.isValid() and role in (QtCore.Qt.ItemDataRole.DisplayRole, SORT_ROLE):
            results, row, col = self.translate_to_local(index.row(), index.column())
            try:
                value = results.data.iloc[row][col]
                column_type = results.data.dtypes[col]
                # Cast to column type
                value_render = column_type.type(value)
            except IndexError:
                value = NaN
                value_render = ""
            if isinstance(value_render, float64):
                # limit maximum number of decimal digits displayed
                value_render = f"{value_render:.{results.float_digits:d}f}"

            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                return str(value_render)
            elif role == SORT_ROLE:
                # For numerical sort
                return float(value)

        return None

    def _get_new_rows_columns(self, results, r1, c1, r2, c2):
        new_rows = self.pandas_row_count() - self.row_count
        new_rows_start = self.row_count

        new_columns = self.pandas_column_count() - self.column_count
        new_columns_start = self.column_count

        return new_rows, new_rows_start, new_columns, new_columns_start

    def headerData(self, section, orientation, role):
        """ Return header information

        Override method from QAbstractTableModel
        """
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return str(self.horizontal_header[section])

            if orientation == QtCore.Qt.Orientation.Vertical:
                return str(self.vertical_header[section])
        elif role == QtCore.Qt.ItemDataRole.DecorationRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return self.horizontal_header_decoration(section)

            if orientation == QtCore.Qt.Orientation.Vertical:
                return self.vertical_header_decoration(section)

        return None

    def _data_changed(self, results, r1, c1, r2, c2):
        """ Internal method to handle data changed signal """
        rows, rows_start, columns, columns_start = \
            self._get_new_rows_columns(results, r1, c1, r2, c2)
        if rows or columns:
            if rows > 0:
                # New rows available
                self.beginInsertRows(QtCore.QModelIndex(),
                                     rows_start,
                                     rows_start + rows - 1)
                self.row_count += rows
                self.endInsertRows()

            if columns > 0:
                # New columns available
                self.beginInsertColumns(QtCore.QModelIndex(),
                                        columns_start,
                                        columns_start + columns - 1)
                self.column_count += columns
                self.endInsertColumns()
        else:
            top_bottom = self._get_row_column_set(results, r1, c1, r2, c2)
            for r1, c1, r2, c2 in top_bottom:
                self.dataChanged.emit(self.createIndex(r1, c1),
                                      self.createIndex(r2, c2))

    def pandas_row_count(self):
        """ Return total row count of the panda dataframes

        The value depends on the geometry selected to display dataframes
        """
        raise Exception("Subclass should implement it")

    def pandas_column_count(self):
        """ Return total column count of the panda dataframes

        The value depends on the geometry selected to display dataframes
        """
        raise Exception("Subclass should implement it")

    def _get_row_column_set(self, results, r1, c1, r2, c2):
        """ Return set of top/bottom coordinates for data changed event.

        Depending on the geometry of the table a single top/bottom could be
        translated in multiple tops/bottoms
        """
        raise Exception("Subclass should implement it")

    def translate_to_local(self, row, col):
        """ Translate from full table coordinate to single results coordinates """
        raise Exception("Subclass should implement it")

    def translate_to_global(self, results, row, col):
        """ Translate from single results coordinates to full table coordinates """
        raise Exception("Subclass should implement it")

    @property
    def horizontal_header(self):
        raise Exception("Subclass should implement it")

    @property
    def vertical_header(self):
        return range(self.row_count)

    def horizontal_header_decoration(self, section):
        return None

    def vertical_header_decoration(self, section):
        return None


class PandasModelByRow(PandasModelBase):
    def pandas_row_count(self):
        rows = 0
        for r in self.results_list:
            rows += r.rows
        return rows

    def pandas_column_count(self):
        cols = 0
        if self.results_list:
            cols = self.results_list[0].columns
        return cols

    def _get_row_column_set(self, results, r1, c1, r2, c2):
        top = self.translate_to_global(results, r1, c1)
        bottom = self.translate_to_global(results, r2, c2)
        return (top + bottom),

    def translate_to_local(self, row, col):
        """ Translate from full table coordinate to single results coordinates """
        for index, results in enumerate(self.results_list):
            if row < results.rows:
                break
            row -= results.rows
        return results, row, col

    def translate_to_global(self, results, row, col):
        """ Translate from single results coordinates to full table coordinates """
        rows = 0
        for res in self.results_list:
            if res == results:
                break
            rows += results.rows
        return rows + row, col

    @property
    def horizontal_header(self):
        if self.results_list:
            return self.results_list[0].data.columns
        else:
            return []

    def vertical_header_decoration(self, section):
        results, _, _ = self.translate_to_local(section, 0)
        pixelmap = QtGui.QPixmap(6, 6)
        pixelmap.fill(results.color)
        return pixelmap


class PandasModelByColumn(PandasModelBase):
    def pandas_row_count(self):
        return max([0] + [r.rows for r in self.results_list])

    def pandas_column_count(self):
        cols = 0
        size = len(self.results_list)
        if size > 0:
            cols = self.results_list[0].columns * size
        return cols

    def _get_row_column_set(self, results, r1, c1, r2, c2):
        top_bottoms = []
        for i in range(c1, c2 + 1):
            top = self.translate_to_global(results, r1, i)
            bottom = self.translate_to_global(results, r2, i)
            top_bottoms.append(top + bottom)

        return top_bottoms

    def translate_to_local(self, row, col):
        """ Translate from full table coordinate to single results coordinates """
        columns = 0
        for index, results in enumerate(self.results_list):
            if col < (columns + results.columns):
                break
            columns += results.columns
        return results, row, col - columns

    def translate_to_global(self, results, row, col):
        """ Translate from single results coordinates to full table coordinates """
        columns = 0
        for res in self.results_list:
            if res == results:
                break
            columns += results.columns
        return row, col + columns

    @property
    def horizontal_header(self):
        size = len(self.results_list)
        if size:
            v = list(self.results_list[0].data.columns)
            return v * size
        else:
            return []

    def horizontal_header_decoration(self, section):
        results, _, _ = self.translate_to_local(0, section)
        pixelmap = QtGui.QPixmap(6, 6)
        pixelmap.fill(results.color)
        return pixelmap


class Table(QtWidgets.QTableView):
    """ Table format view of :class:`Experiment<pymeasure.display.manager.Experiment>`
    objects

    """

    supported_formats = {
        "CSV file (*.csv)": 'csv',
        "Excel file (*.xlsx)": 'excel',
        "HTML file (*.html *.htm)": 'html',
        "JSON file (*.json)": 'json',
        "LaTeX file (*.tex)": 'latex',
        "Markdown file (*.md)": 'markdown',
        "XML file (*.xml)": 'xml',
    }

    def __init__(self, refresh_time=0.2, check_status=True,
                 force_reload=False, by_column=True, parent=None):
        super().__init__(parent)
        self.force_reload = force_reload
        if by_column:
            model = PandasModelByColumn()
        else:
            model = PandasModelByRow()

        self.setModel(model)
        self.horizontalHeader().setStyleSheet("font: bold;")
        self.sortByColumn(-1, QtCore.Qt.SortOrder.AscendingOrder)
        self.setSortingEnabled(True)
        self.horizontalHeader().setSectionsMovable(True)
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.ResizeToContents
        )

        self.setup_context_menu()

        self.refresh_time = refresh_time
        self.check_status = check_status
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_tables)
        self.timer.start(int(self.refresh_time * 1e3))

    def setModel(self, model):
        if SORTING_ENABLED:
            proxyModel = QtCore.QSortFilterProxyModel(self)
            proxyModel.setSourceModel(model)
            model = proxyModel

            model.setSortRole(SORT_ROLE)
        super().setModel(model)

    def source_model(self):
        if SORTING_ENABLED:
            model = self.model().sourceModel()
        else:
            model = self.model()
        return model

    def composed_dataframe(self):
        """ Create single pandas dataframe out of the dataframe list """
        model = self.source_model()

        df_list = [results.data for results in model.results_list]
        if not df_list:  # Empty list
            df = None
        elif isinstance(model, PandasModelByRow):
            # Concatenate pandas data frames
            df = pd.concat(df_list, axis=0).replace(to_replace=NaN, value="")
        else:
            # Concatenate pandas data frames
            df = pd.concat(df_list, axis=1).replace(to_replace=NaN, value="")

        return df

    def export_action(self):
        df = self.composed_dataframe()

        if df is not None:
            formats = ";;".join(self.supported_formats.keys())
            filename_and_ext = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                     "Save File",
                                                                     "",
                                                                     formats)
            filename = filename_and_ext[0]
            ext = filename_and_ext[1]
            if filename:
                mode = self.supported_formats[ext]
                prefix = df.style if mode == "latex" else df
                getattr(prefix, 'to_' + mode)(filename)

    def refresh_action(self):
        self.update_tables()

    def copy_action(self):
        df = self.composed_dataframe()
        if df is not None:
            df.to_clipboard()

    def setup_context_menu(self):
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)
        self.copy = QtGui.QAction("Copy table data", self)
        self.copy.triggered.connect(self.copy_action)
        self.refresh = QtGui.QAction("Refresh table data", self)
        self.refresh.triggered.connect(self.refresh_action)
        self.export = QtGui.QAction("Export table data", self)
        self.export.triggered.connect(self.export_action)

    def context_menu(self, point):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.copy)
        menu.addAction(self.refresh)
        menu.addAction(self.export)
        menu.exec(self.mapToGlobal(point))

    def update_tables(self):
        model = self.source_model()
        for item in model.results_list:
            if self.check_status:
                if item.results.procedure.status == Procedure.RUNNING:
                    item.update_data()
            else:
                item.update_data()

    def set_color(self, table, color):
        table.set_color(color)

    def add_table(self, table):
        model = self.source_model()
        model.add_results(table)

    def remove_table(self, table):
        model = self.source_model()
        model.remove_results(table)
        table.stop()

    def clear(self):
        model = self.model().source_model()

        model.clear()


class TableWidget(TabWidget, QtWidgets.QWidget):
    """ Widget to display experiment data in a tabular format
    """
    float_digits = 6

    def __init__(self, name, columns, by_column=True, refresh_time=0.2,
                 check_status=True, parent=None):
        super().__init__(name, parent)
        self.columns = columns
        self.by_column = by_column
        self.refresh_time = refresh_time
        self.check_status = check_status
        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.table = Table(refresh_time=self.refresh_time,
                           check_status=self.check_status,
                           force_reload=False,
                           by_column=self.by_column,
                           parent=self)

    def _layout(self):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(0)

        vbox.addWidget(self.table)
        self.setLayout(vbox)

    def new_curve(self, results, color=pg.intColor(0), **kwargs):
        ret = ResultsTable(results, color, self.float_digits, wdg=self, **kwargs)
        return ret

    def load(self, table):
        self.table.add_table(table)

    def remove(self, table):
        self.table.remove_table(table)

    def set_color(self, table, color):
        """ Change the color of the pen of the curve """
        self.table.set_color(table, color)

    def preview_widget(self, parent=None):
        """ Return a widget suitable for preview during loading """

        return TablePreviewWidget("Table preview",
                                  columns=self.columns,
                                  by_column=self.by_column,
                                  refresh_time=self.refresh_time,
                                  check_status=True,
                                  parent=None)


class TablePreviewWidget(TableWidget):
    """ Class variant intended to be used during preview """

    def preview_update(self, results):
        """ Update the preview widget """
        self.table.clear()
        curve = self.new_curve(results)
        self.load(curve)
