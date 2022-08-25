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

from inspect import signature
from datetime import datetime, timedelta

from ..thread import StoppableQThread
from ..Qt import QtCore, QtGui
from .sequencer_widget import SequenceEvaluationException

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class EstimatorThread(StoppableQThread):
    new_estimates = QtCore.QSignal(list)

    def __init__(self, get_estimates_callable):
        StoppableQThread.__init__(self)

        self._get_estimates = get_estimates_callable

        self.delay = 2

    def __del__(self):
        self.wait()

    def run(self):
        self._should_stop.clear()

        while not self._should_stop.wait(self.delay):
            estimates = self._get_estimates()
            self.new_estimates.emit(estimates)


class EstimatorWidget(QtGui.QWidget):
    """
    Widget that allows to display up-front estimates of the measurement
    procedure.

    This widget relies on a `get_estimates` method of the
    :class:`Procedure<pymeasure.experiment.procedure.Procedure>` class.
    `get_estimates` is expected to return a list of tuples, where each tuple
    contains two strings: a label and the estimate.

    If the :class:`SequencerWidget<pymeasure.display.widgets.sequencer_widget.SequencerWidget>`
    is also used, it is possible to ask for the current sequencer or its length by
    asking for two keyword arguments in the Implementation of the `get_estimates` function:
    `sequence` and `sequence_length`, respectively.

    """
    provide_sequence = False
    provide_sequence_length = False
    number_of_estimates = 0
    sequencer = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent

        self.check_get_estimates_signature()

        self.update_thread = EstimatorThread(self.get_estimates)
        self.update_thread.new_estimates.connect(self.display_estimates)

        self._setup_ui()
        self._layout()

        self.update_estimates()

        self.update_box.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)

    def check_get_estimates_signature(self):
        """ Method that checks the signature of the get_estimates function.
        It checks which input arguments are allowed and, if the output is
        correct for the EstimatorWidget, stores the number of estimates.
        """

        # Check function arguments
        proc = self._parent.make_procedure()
        call_signature = signature(proc.get_estimates)

        if "sequence" in call_signature.parameters:
            self.provide_sequence = True

        if "sequence_length" in call_signature.parameters:
            self.provide_sequence_length = True

        estimates = self.get_estimates()

        # Check if the output of the function is acceptable
        raise_error = True
        if isinstance(estimates, (list, tuple)):
            if all([isinstance(est, (tuple, list)) for est in estimates]):
                if all([len(est) == 2 for est in estimates]):
                    raise_error = False

        if raise_error:
            raise TypeError(
                "If implemented, the get_estimates function is expected to"
                "return an int or float representing the estimated duration,"
                "or a list of tuples of strings, where each tuple  represents"
                "an estimate containing two string: the first is a label for"
                "the estimate, the second is the estimate itself."
            )

        # Store the number of estimates
        self.number_of_estimates = len(estimates)

    def _setup_ui(self):
        self.line_edits = list()
        for idx in range(self.number_of_estimates):
            qlb = QtGui.QLabel(self)

            qle = QtGui.QLineEdit(self)
            qle.setEnabled(False)
            qle.setAlignment(QtCore.Qt.AlignRight)

            self.line_edits.append((qlb, qle))

        # Add a checkbox for continuous updating
        self.update_box = QtGui.QCheckBox(self)
        self.update_box.setTristate(True)
        self.update_box.stateChanged.connect(self._set_continuous_updating)

        # Add a button for instant updating
        self.update_button = QtGui.QPushButton("Update", self)
        self.update_button.clicked.connect(self.update_estimates)

    def _layout(self):
        f_layout = QtGui.QFormLayout(self)
        for row in self.line_edits:
            f_layout.addRow(*row)

        update_hbox = QtGui.QHBoxLayout()
        update_hbox.addWidget(self.update_box)
        update_hbox.addWidget(self.update_button)
        f_layout.addRow("Update continuously", update_hbox)

    def get_estimates(self):
        """ Method that makes a procedure with the currently entered
        parameters and returns the estimates for these parameters.
        """
        # Make a procedure
        procedure = self._parent.make_procedure()

        kwargs = dict()

        sequence = None
        sequence_length = None
        if hasattr(self._parent, "sequencer"):
            try:
                sequence = self._parent.sequencer.get_sequence_from_tree()
            except SequenceEvaluationException:
                sequence_length = 0
            else:
                sequence_length = len(sequence)

        if self.provide_sequence:
            kwargs["sequence"] = sequence

        if self.provide_sequence_length:
            kwargs["sequence_length"] = sequence_length

        estimates = procedure.get_estimates(**kwargs)

        if isinstance(estimates, (int, float)):
            estimates = self._estimates_from_duration(estimates, sequence_length)

        return estimates

    def update_estimates(self):
        """ Method that gets and displays the estimates.
        Implemented for connecting to the 'update'-button.
        """
        estimates = self.get_estimates()
        self.display_estimates(estimates)

    def display_estimates(self, estimates):
        """ Method that updates the shown estimates for the given set of
        estimates.

        :param estimates: The set of estimates to be shown in the form of a
            list of tuples of (2) strings
        """
        if len(estimates) != self.number_of_estimates:
            raise ValueError(
                "Number of estimates changed after initialisation "
                "(from %d to %d)." % (self.number_of_estimates, len(estimates))
            )

        for idx, estimate in enumerate(estimates):
            self.line_edits[idx][0].setText(estimate[0])
            self.line_edits[idx][1].setText(estimate[1])

    def _estimates_from_duration(self, duration, sequence_length):
        estimates = list()

        estimates.append(("Duration", "%d s" % int(duration)))

        if hasattr(self._parent, "sequencer"):
            estimates.append(("Sequence length", str(sequence_length)))
            estimates.append(("Sequence duration", "%d s" % int(sequence_length * duration)))

        estimates.append(('Measurement finished at', str(datetime.now() + timedelta(
            seconds=duration))[:-7]))

        if hasattr(self._parent, "sequencer"):
            estimates.append(('Sequence finished at', str(datetime.now() + timedelta(
                seconds=duration * sequence_length))[:-7]))

        return estimates

    def _set_continuous_updating(self):
        state = self.update_box.checkState()

        self.update_thread.stop()
        self.update_thread.join()

        if state == QtCore.Qt.CheckState.Unchecked:
            pass
        elif state == QtCore.Qt.CheckState.PartiallyChecked:
            self.update_thread.delay = 2
            self.update_thread.start()
        elif state == QtCore.Qt.CheckState.Checked:
            self.update_thread.delay = 0.1
            self.update_thread.start()
