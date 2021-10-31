#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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
from collections import OrderedDict as OrderedDictionary

from pymeasure.display.Qt import QtCore, QtGui

modules_enabled=(
#    "rowCount",
#    "index",
#    "data",
#    "parent",
#    "add_node",
#    "remove_node",
#    "headerData",
    "find_index",
)
def print_debug(module, *args):
    if module in modules_enabled:
        print (module, *args)

class TreeModel(QtCore.QAbstractItemModel):
    """ TreeModel is an implementation of PyQt's QAbstractItemModel that overrides default indexing support to use
        python dictionaries mapping a column in the table header supplied to a value for said column. The goal here
        is to simplify indexing by being able to manage the data in a table based on string keys instead of arbitrary
        indexes, eliminating the need to cross-reference a header to find where to put a value.
    """

    def __init__(self, header, data, header_types=None, key_column=0, parent=None):
        """ TreeModel constructor
        :param header: The header to use
        :type header: Iterable
        :param parent: A QWidget that QT will give ownership of this Widget too.
        """
        super().__init__(parent)

        self.header = header
        self.header_types = header_types

        if not self.header_types:
            self.header_types = {}
            for column in self.header:
                self.header_types[column] = 'string'

        self.key_column = self.header[key_column]
        self.root = data

    def find_index(self, pointer):
        print_debug ("find_index", "******** find_index", pointer)
        for index in self.persistentIndexList():
            if index.column() != 0:
                continue

            if index.internalPointer() == pointer:
                return index

    def _connect_node(self, node):
        node.changed.connect(lambda: self._notify_data_changed(node))

    def _notify_data_changed(self, node):
        row = node.row()
        top_left = self.createIndex(row, 0, node)
        bottom_right = self.createIndex(row, len(self.header), node)
        self.dataChanged.emit(top_left, bottom_right)

    def add_node(self, parameter, parent=None):
        """ Add a row in the sequencer """
        print_debug("add_node", parameter, parent)
        if parent is None:
            parent = self.createIndex(-1,-1)

        idx = len(self.root.children(parent))
        print_debug("add_node", " idx", idx)
        parent_seq_item = parent.internalPointer()
            
        self.beginInsertRows(parent, idx, idx)
        self.root.add_node(parameter, parent_seq_item)
        self.endInsertRows()

    def remove_node(self, index):
        """ Remove a row in the sequencer """
        print_debug("remove_node", index, "****", index.internalPointer())
        children = self.rowCount(index)
        print_debug("remove_node", "children", children)
        while (children > 0):
            child = children -1
            print_debug("remove_node", "*", child, index.internalPointer())
            children_seq_item = self.root.get_children(index.internalPointer(), child)
            self.remove_node(self.createIndex(child, 0, children_seq_item))
            children = self.rowCount(index)
            print_debug("remove_node", "children", children)

        self.beginRemoveRows(index.parent(), index.row(), index.row())
        self.root.remove_node(index.internalPointer())
        self.endRemoveRows()

    def flags(self, index):
        """ QAbstractItemModel override method that is used to set the flags for the item at the given QModelIndex.
            Here, we just set all indexes to enabled, and selectable.
        """
        if not index.isValid():
            return_value = QtCore.Qt.NoItemFlags
        else:
            return_value = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
            if index.column() >= 1:
                return_value |= QtCore.Qt.ItemIsEditable
        return return_value

    def data(self, index, role):
        """ Return the data to display for the given index and the given role.
            This method should not be called directly. This method is called implicitly by the QTreeView that is
            displaying us, as the way of finding out what to display where.
        """
        if not index.isValid():
            return

        elif not role == QtCore.Qt.DisplayRole:
            return

        print_debug ("data", index.row(), index.column(), index.internalPointer())
        data = index.internalPointer()[index.column()]

        if not isinstance(data, QtCore.QObject):
            data = str(data)

        print_debug ("data", "ret", data)
        return data

    def index(self, row, col, parent):
        """ Return a QModelIndex instance pointing the row and column underneath the parent given.
            This method should not be called directly. This method is called implicitly by the QTreeView that is
            displaying us, as the way of finding out what to display where.
        """
        print_debug ("index", row, col, parent.row(), parent.column(), parent.internalPointer())
        row_parent, column_parent = parent.row(), parent.column()
        if not parent or not parent.isValid():
            parent_data = None # self.root[0]
        else:
            parent_data = parent.internalPointer()

        if row < 0 or row >= len(self.root.sequences):
            return QtCore.QModelIndex()

        row_data=self.root.get_children(parent_data, row)
        child = row_data
        if child is None:
            return QtCore.QModelIndex()
        index = self.createIndex(row, col, child)
        print_debug ("index", "ret", index.row(), index.column(), index.internalPointer())
        return index

    def parent(self, index=None):
        """ Return the index of the parent of a given index. If index is not supplied, return an invalid
                QModelIndex.
            Optional args: index

        :param index: QModelIndex
        :return:
        """
        
        if index:
            print_debug("parent", index.row(), index.column(), index.internalPointer())
        else:
            print_debug ("parent", index)
            
        if not index:
            return QtCore.QModelIndex()

        elif not index.isValid():
            return QtCore.QModelIndex()

        child = index.internalPointer()
        parent, parent_row = self.root.get_parent(index.internalPointer())

        if parent is None:
            return QtCore.QModelIndex()

        index = self.createIndex(parent_row, 0, parent)
        print_debug ("parent", "ret", parent_row, index.row(), index.column(), index.internalPointer())
        return index

    def rowCount(self, parent):
        """ Return the number of rows a given index has under it. If an invalid QModelIndex is supplied, return the
                number of children under the root.

        :param parent: QModelIndex
        """
        print_debug ("rowCount", parent, parent.internalPointer())
        row, column = parent.row(), parent.column()
        if column > 0:
            return 0

        if not parent.isValid():
            parent = None
        else:
            parent = parent.internalPointer()

        if False and (parent is None):
            rows = 0
        else:
            rows = len(self.root.children(parent))
        print_debug ("rowCount", "ret", rows, parent)
        return rows

    def columnCount(self, parent):
        """ Return the number of columns in the model header. The parent parameter exists only to support the signature
                of QAbstractItemModel.
        """
        return len(self.header)

    def headerData(self, section, orientation, role):
        """ Return the header data for the given section, orientation and role. This method should not be called
            directly. This method is called implicitly by the QTreeView that is displaying us, as the way of finding
            out what to display where.
        """
        print_debug ("headerData", section, orientation, role)
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[section]

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        print_debug ("setData", index, value, role)
        return_value = False
        if role == QtCore.Qt.EditRole:
            return_value =self.root.set_data(index.internalPointer(), index.row(), index.column(), value)
            if return_value:
                self.dataChanged.emit(index, index, value)
        return return_value
        
    def __iter__(self):
        for child in self.root.children.itervalues():
            yield child

    def save(self, filename=None):
        self.root.save(filename)
