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
from functools import partial
import pyqtgraph as pg

from ..Qt import QtCore, QtWidgets, QtGui
from .tab_widget import TabWidget
from ...experiment import Procedure

SORT_ROLE = QtCore.Qt.UserRole + 1
SORTING_ENABLED = False

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class ResultsTable(QtCore.QObject):
    data_changed = QtCore.Signal(int, int, int, int)

    def __init__(self, results, color, force_reload=False, **kwargs):
        super().__init__()
        self.results = results
        self.color = color
        self.force_reload = force_reload
        self.last_row_count = 0
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
    """ This class provided a model to manage multiple panda dataframes and display them
    as a single table.

    The multiple pandas dataframes are provided as ResultTable class instances and all of the share the
    same number of columns.
    The pandas dataframes can be arranged with different modes in a global table, e.g.
    - By row:
    - By column:
    
    Model to present multiple pandas dataframe in a single table view

    There are some assumptions:
    - Series in the dataframe are identical, we call this number k
    - Series length can be different, we call this number l(x), where x=1..n

    The data can be presented as follow:
    - By column: each series in a separate column, in this case table shape
    will be: (k*n) x (max(l(x) x=1..n)
    - By row: column fixed to the number of series, in this case table shape
    will be: k x (sum of l(x) x=1..n)
    """
    def __init__(self, by_column=True, parent=None):
        super().__init__(parent)
        self.float_digits = 6
        self.results_list = []
        self.row_count = 0
        self.column_count = 0

    def add_results(self, results):
        if not results in self.results_list:
            self.results_list.append(results)
            results.data_changed.connect(partial(self._data_changed, results))
            self.layoutChanged.emit()
            results.init()
            results.start()
            results.update_data()

    def remove_results(self, results):
        self.results_list.remove(results)
        self.row_count = self.pandas_row_count()
        self.column_count = self.pandas_column_count()
        results.stop()
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self.row_count

    def columnCount(self, parent=None):
        return self.column_count

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid() and role in (QtCore.Qt.DisplayRole, SORT_ROLE):
            result, row, col = self.translate_to_local(index.row(), index.column())
            try:
                value = result.data.iloc[row][col]
                column_type = result.data.dtypes[col]
                # Cast to column type
                value_render = column_type.type(value)
            except IndexError:
                value_render = ""
            if isinstance(value_render, numpy.float64):
                # limit maximum number of decimal digits displayed
                value_render = f"{value_render:.{self.float_digits:d}f}"

            if role == QtCore.Qt.DisplayRole:
                return (str(value_render))
            elif role == SORT_ROLE:
                # For numerical sort
                return float(value)

        return None

    def headerData(
        self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.ItemDataRole
    ):
        """ Return header information

        Override method from QAbstractTableModel
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self.horizontal_header[section])

            if orientation == QtCore.Qt.Vertical:
                return str(self.vertical_header[section])
        elif role == QtCore.Qt.DecorationRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.horizontal_header_decoration(section)

            if orientation == QtCore.Qt.Vertical:
                return self.vertical_header_decoration(section)

        return None
    
    def _data_changed(self, results, r1, c1, r2, c2):
        """ Internal method to handle data changed signal """
        index = self.results_list.index(results)
        new_rows, new_rows_start, new_columns, new_columns_start = self._get_new_row_columns(results, r1, c1, r2, c2)
        if new_rows or new_columns:
            if new_rows > 0:
                # New rows available
                self.beginInsertRows(QtCore.QModelIndex(),
                                     new_rows_start,
                                     new_rows_start + new_rows - 1)
                self.row_count += new_rows
                self.endInsertRows()

            if new_columns > 0:
                # New columns available
                self.beginInsertColumns(QtCore.QModelIndex(),
                                     new_columns_start,
                                        new_columns_start + new_columns - 1)
                self.column_count += new_columns
                self.endInsertColumns()
        else:
            top_bottom = self._get_row_column_set(results, r1, c1, r2, c2)
            for r1,c1, r2,c2 in top_bottom:
                self.dataChanged.emit(self.createIndex(r1, c1),
                                      self.createIndex(r2, c2))

    def pandas_row_count(self):
        """ Return total row count of the panda dataframes

        The value depends on the geometry selected to display dataframes
        """
        raise Exception ("Subclass should implement it")

    def pandas_column_count(self):
        """ Return total column count of the panda dataframes

        The value depends on the geometry selected to display dataframes
        """
        raise Exception ("Subclass should implement it")

    def _get_row_column_set (self, result, r1, c1, r2, c2):
        """ Return set of top/bottom for data changed event.

        Depending on the geometry of the table a single top/bottom could be
        translated in multiple tops/bottoms
        """
        raise Exception ("Subclass should implement it")
 
    def _get_new_row_columns(self, result, r1, c1, r2, c2):
        """ Return new row and column to be added, if any

        Upon request of adding the box top=(r1,c1), bottom=(r2,c2) to panda dataframe result,
        it computes the new now and columns to be added to the global table.
        """
        raise Exception ("Subclass should implement it")

        # return new_rows, new_rows_start, new_columns, new_columns_start
    
    def translate_to_local(self, row, col):
        """ Translate from full table coordinate to single result coordinates """
        raise Exception ("Subclass should implement it")
            
    def translate_to_full(self, result, row, col):
        """ Translate from single result coordinates to full table coordinates """
            
    @property
    def horizontal_header(self):
        raise Exception ("Subclass should implement it")
    
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

    def _get_row_column_set (self, result, r1, c1, r2, c2):
        """ Return set of top/bottom for data changed event.

        Depending on the geometry of the table a single top/bottom could be
        translated in multiple tops/bottoms
        """
        top = self.translate_to_global(result, r1, c1)
        bottom = self.translate_to_global(result, r2, c2)
        return ((top + bottom),)
 
    def _get_new_row_columns(self, result, r1, c1, r2, c2):
        """ Return new row and column to be added, if any """
        new_rows = new_rows_start = new_columns = new_columns_start = 0
        current_rows = self.pandas_row_count()
        current_columns = self.pandas_column_count()
        if current_rows > self.row_count:
            new_rows = current_rows - self.row_count
            new_rows_start = 0
            for r in self.results_list:
                new_rows_start += r.rows
                if r == result:
                    break

        if current_columns > self.column_count:
            new_columns = current_columns - self.column_count
            new_columns_start = self.column_count

        return new_rows, new_rows_start, new_columns, new_columns_start
    
    def translate_to_local(self, row, col):
        """ Translate from full table coordinate to single result coordinates """
        for index, result in enumerate(self.results_list):
            if row < result.rows:
                break
            row -= result.rows
        return result, row, col
            
    def translate_to_global(self, result, row, col):
        """ Translate from single result coordinates to full table coordinates """
        rows = 0
        for res in self.results_list:
            if  res == result:
                break
            rows += result.rows
        return rows+row, col
            
    @property
    def horizontal_header(self):
        if self.results_list:
            return self.results_list[0].data.columns
        else:
            return []
    
    def vertical_header_decoration(self, section):
        result, _,_ = self.translate_to_local(section, 0)
        pixelmap = QtGui.QPixmap(6, 6)
        pixelmap.fill(result.color)
        return pixelmap

class PandasModelByColumn(PandasModelBase):
    def pandas_row_count(self):
        rows = 0
        for r in self.results_list:
            rows = max(rows, r.rows)
        return rows

    def pandas_column_count(self):
        cols = 0
        if (len(self.results_list) > 0):
            cols = self.results_list[0].columns * len(self.results_list)
        return cols

    def _get_row_column_set (self, result, r1, c1, r2, c2):
        """ Return set of top/bottom for data changed event.

        Depending on the geometry of the table a single top/bottom could be
        translated in multiple tops/bottoms
        """
        top = self.translate_to_global(result, r1, c1)
        bottom = self.translate_to_global(result, r2, c2)
        top_bottoms = []
        for i in range(c1, c2 + 1):
            top = self.translate_to_global(result, r1, i)
            bottom = self.translate_to_global(result, r2, i)
            top_bottoms.append(top + bottom)
            
        return top_bottoms
 
    def _get_new_row_columns(self, result, r1, c1, r2, c2):
        """ Return new row and column to be added, if any """
        new_rows = new_rows_start = new_columns = new_columns_start = 0
        current_rows = self.pandas_row_count()
        current_columns = self.pandas_column_count()
        if current_rows > self.row_count:
            new_rows = current_rows - self.row_count
            new_rows_start = 0
            for r in self.results_list:
                new_rows_start += r.rows
                if r == result:
                    break

        if current_columns > self.column_count:
            new_columns = current_columns - self.column_count
            new_columns_start = self.column_count
        return new_rows, new_rows_start, new_columns, new_columns_start
    
    def translate_to_local(self, row, col):
        """ Translate from full table coordinate to single result coordinates """
        columns = 0
        for index, result in enumerate(self.results_list):
            if col < (columns + result.columns):
                break
            columns += result.columns
        return result, row, col - columns
            
    def translate_to_global(self, result, row, col):
        """ Translate from single result coordinates to full table coordinates """
        columns = 0
        for res in self.results_list:
            if  res == result:
                break
            columns += result.columns
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
        result, _, _ = self.translate_to_local(0,section)
        pixelmap = QtGui.QPixmap(6, 6)
        pixelmap.fill(result.color)
        return pixelmap
        
class Header(QtWidgets.QHeaderView):
    def __init__(self, header, parent=None):
        super().__init__(QtCore.Qt.Horizontal, header)
        self.mainHeader = header

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.ctxMenu)
        self.hello = QtGui.QAction("Hello", self)
        self.hello.triggered.connect(self.printHello)
        self.currentSection = None
        self.resizeSection(0, self.getSectionSizes(0,1))
        self.hideSection(1)
        self.sectionResized.connect(self.updateSizes)

    def getSectionSizes(self, *args):
        return sum(map(lambda x : self.mainHeader.sectionSize(x), args))

    def updateSizes (self):
        print ("updateSizes", self.mainHeader.count())
        self.setOffset(self.mainHeader.offset())
        self.mainHeader.resizeSection(1, self.mainHeader.sectionSize(1) + (self.sectionSize(0) + self.getSectionSizes(0,1)))
        # TBD
        #pass

    def updateOffset(self):
        self.setOffset(self.mainHeader.offset())


    def eventFilter(self, obj, event):
        if obj == self.mainHeader:
            if event.type() == QtCore.QEvent.Resize:
                self.setOffset(self.mainHeader.offset())
                self.setGeometry(0, 0, self.mainHeader.width(), self.mainHeader.height())
            return False
        else:
            # standard event processing
            return super().eventFilter(obj, event)

    def printHello(self):
        data = self.model().headerData(self.currentSection, QtCore.Qt.Horizontal)
        print (data)

    def ctxMenu(self, point):
        menu = QtWidgets.QMenu(self)
        self.currentSection = self.logicalIndexAt(point)
        menu.addAction(self.hello)
        menu.exec(self.mapToGlobal(point))

class Table(QtWidgets.QTableView):
    """Graphical list view of :class:`Experiment<pymeasure.display.manager.Experiment>`
    objects allowing the user to view the status of queued Experiments as well as
    loading and displaying data from previous runs.

    In order that different Experiments be displayed within the same Browser,
    they must have entries in `DATA_COLUMNS` corresponding to the
    `measured_quantities` of the Browser.
    """

    def __init__(self, refresh_time=0.2, check_status=True, force_reload=False, float_digits=6, parent=None):
        super().__init__(parent)
        self.force_reload = force_reload
        self.float_digits = float_digits
        model = PandasModelByColumn()
        if SORTING_ENABLED:
            proxyModel = QtCore.QSortFilterProxyModel(self)
            proxyModel.setSourceModel(model)
            model = proxyModel

            model.setSortRole(SORT_ROLE)
        self.setModel(model)
        self.horizontalHeader().setStyleSheet("font: bold;")
        self.setSortingEnabled(True)
        self.sortByColumn(-1, QtCore.Qt.AscendingOrder)
        self.horizontalHeader().setSectionsMovable(True)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.refresh_time = refresh_time
        self.check_status = check_status
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_curves)
        self.timer.start(int(self.refresh_time * 1e3))

    def update_curves(self):
        if SORTING_ENABLED:
            model = self.model().sourceModel()
        else:
            model = self.model()
        for item in model.results_list:
            if self.check_status:
                if item.results.procedure.status == Procedure.RUNNING:
                    item.update_data()
            else:
                item.update_data()

    def set_color(self, table, color):
        table.set_color(color)

    def addTable(self, table):
        if SORTING_ENABLED:
            model = self.model().sourceModel()
        else:
            model = self.model()
        model.add_results(table)

    def removeTable(self, table):
        if SORTING_ENABLED:
            model = self.model().sourceModel()
        else:
            model = self.model()
        model.remove_results(table)
        table.stop()


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
        self.tables = Table(refresh_time= self.refresh_time,
                            check_status=True,
                            force_reload=False,
                            float_digits=self.float_digits,
                            parent=None)

    def _layout(self):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(0)

        vbox.addWidget(self.tables)
        self.setLayout(vbox)

    def sizeHint(self):
        return QtCore.QSize(300, 600)

    def new_curve(self, results, color=pg.intColor(0), **kwargs):
        kwargs.setdefault("float_digits", self.float_digits)
        ret = ResultsTable(results, color, **kwargs)
        return ret

    def load(self, table):
        self.tables.addTable(table)

    def remove(self, table):
        self.tables.removeTable(table)

    def set_color(self, table, color):
        """ Change the color of the pen of the curve """
        self.tables.set_color(table, color)
