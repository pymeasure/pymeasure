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

import logging

from pyqtgraph.Qt import QtGui, QtCore, loadUiType
import sys

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

QtCore.QSignal = QtCore.Signal


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

# creating checkable combo box class
class CheckableComboBox(QtGui.QComboBox):
    def __init__(self):
        super(CheckableComboBox, self).__init__()
        self.view().pressed.connect(self.handle_item_pressed)
        self.setModel(QtGui.QStandardItemModel(self))
  
    # when any item get pressed
    def handle_item_pressed(self, index):
  
        # getting which item is pressed
        item = self.model().itemFromIndex(index)
  
        # make it check if unchecked and vice-versa
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)
  
        # calling method
        self.check_items()
  
    # method called by check_items
    def item_checked(self, index):
  
        # getting item at index
        item = self.model().item(index, 0)
  
        # return true if checked else false
        return item.checkState() == QtCore.Qt.Checked
  
    # calling method
    def check_items(self):
        # blank list
        checkedItems = []
  
        # traversing the items
        for i in range(self.count()):
  
            # if item is checked add it to the list
            if self.item_checked(i):
                checkedItems.append(i)
 
        #call this method
        # self.update_labels(checkedItems)
  
    # method to update the label
    def update_labels(self, item_list):
  
        n = ''
        count = 0
  
        # traversing the list
        for i in item_list:
  
            # if count value is 0 don't add comma
            if count == 0:
                n += ' % s' % i
            # else value is greater then 0
            # add comma
            else:
                n += ', % s' % i
  
            # increment count
            count += 1
  
  
        # loop
        for i in range(self.count()):
  
            # getting label
            text_label = self.model().item(i, 0).text()
  
            # default state
            if text_label.find('-') >= 0:
                text_label = text_label.split('-')[0]
  
            # shows the selected items
            item_new_text_label = text_label + ' - selected index: ' + n
  
           # setting text to combo box
            self.setItemText(i, item_new_text_label)
  
    # flush
    sys.stdout.flush()