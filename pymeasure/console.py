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

import numpy as np

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

log.warning('not implemented yet')


class ProgressBar(object):
    """ ProgressBar keeps track of the progress, predicts the
    estimated time of arrival (ETA), and formats the bar for
    display in the console
    """

    def __init__(self):
        self.data = np.empty()
        self.progress_percentage = []
        self.progress_times = []

    def advance(self, progress):
        """ Appends the progress state and the current
        time to the data, so that a more accurate prediction
        for the ETA can be made
        """
        pass

    def __str__(self):
        """ Returns a string representation of the progress bar
        """
        pass


def display(log, port, level=logging.INFO):
    """ Displays the log to the console with a progress bar
    that always remains at the bottom of the screen and refreshes itself
    """
    pass
