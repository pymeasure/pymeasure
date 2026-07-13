#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

from pymeasure.display.Qt import QtCore, QtWidgets
from pymeasure.experiment import Procedure
from pymeasure.display.widgets.estimator_widget import (
    EstimatorThread,
    EstimatorWidget,
)
from pymeasure.display.widgets.sequencer_widget import SequenceEvaluationError


# --- Procedure definitions -------------------------------------------------


class _ListEstimatesProcedure(Procedure):
    """Procedure returning a fixed list of (label, estimate) tuples."""

    DATA_COLUMNS = []

    def get_estimates(self):
        return [
            ("Duration", "100 s"),
            ("Number of lines", "10"),
        ]


class _DurationEstimatesProcedure(Procedure):
    """Procedure returning an int duration."""

    DATA_COLUMNS = []

    def get_estimates(self):
        return 42


class _SeqEstimatesProcedure(Procedure):
    """Procedure accepting sequence/sequence_length kwargs, recording calls."""

    DATA_COLUMNS = []
    calls = []

    def get_estimates(self, sequence=None, sequence_length=None):
        type(self).calls.append(
            dict(sequence=sequence, sequence_length=sequence_length)
        )
        return [("Duration", "1 s")]


class _SeqOnlyProcedure(Procedure):
    """Procedure accepting only the sequence kwarg."""

    DATA_COLUMNS = []

    def get_estimates(self, sequence=None):
        return [("Duration", "1 s")]


class _SeqLengthOnlyProcedure(Procedure):
    """Procedure accepting only the sequence_length kwarg."""

    DATA_COLUMNS = []

    def get_estimates(self, sequence_length=None):
        return [("Duration", "1 s")]


# --- Fake parent and sequencer ---------------------------------------------


class _FakeSequencer:
    """Fake sequencer exposing a configurable get_sequence method."""

    def __init__(self, sequence=None, raise_error=False):
        self._sequence = sequence if sequence is not None else []
        self._raise = raise_error

    def get_sequence(self):
        if self._raise:
            raise SequenceEvaluationError("bad sequence")
        return self._sequence


_SENTINEL = object()


class _FakeParent(QtWidgets.QWidget):
    """Minimal parent exposing make_procedure and an optional sequencer."""

    def __init__(self, procedure_class, sequencer=_SENTINEL, parent=None):
        super().__init__(parent)
        self._procedure_class = procedure_class
        if sequencer is not _SENTINEL:
            self.sequencer = sequencer

    def make_procedure(self):
        return self._procedure_class()


# --- Fixtures --------------------------------------------------------------


@pytest.fixture
def make_widget(qtbot):
    """Construct an EstimatorWidget with a stopped update thread.

    The widget constructor auto-starts the update thread (PartiallyChecked
    state); we stop it immediately for deterministic tests. Tests that need
    a running thread should start it explicitly.
    """
    created = []

    def _make(procedure_class, sequencer=_SENTINEL):
        parent = _FakeParent(procedure_class, sequencer=sequencer)
        qtbot.addWidget(parent)
        wdg = EstimatorWidget(parent=parent)
        qtbot.addWidget(wdg)
        wdg.update_thread.stop()
        wdg.update_thread.wait(2000)
        created.append(wdg)
        return wdg

    yield _make

    for w in created:
        w.update_thread.stop()
        w.update_thread.wait(2000)


@pytest.fixture(autouse=True)
def _reset_seq_calls():
    _SeqEstimatesProcedure.calls = []
    yield
    _SeqEstimatesProcedure.calls = []


# --- EstimatorThread tests -------------------------------------------------


def test_estimator_thread_init_attributes():
    """EstimatorThread stores the callable and a default delay of 2 seconds."""

    def _get_estimates():
        return []

    thread = EstimatorThread(_get_estimates)

    assert thread.delay == 2
    assert thread._get_estimates is _get_estimates
    assert hasattr(thread, "new_estimates")

    # __del__ on a never-started thread should not raise (wait returns early).
    thread.__del__()


def test_estimator_thread_del_after_stop(qtbot):
    """__del__ does not raise after the thread has been stopped and joined."""

    def _get_estimates():
        return []

    thread = EstimatorThread(_get_estimates)
    thread.delay = 0.05
    thread.start()
    qtbot.wait(50)
    thread.stop()
    thread.wait(2000)

    thread.__del__()


def test_estimator_thread_run_emits_estimates(qtbot):
    """The run loop calls the callable and emits the new_estimates signal."""

    emitted = []

    def _get_estimates():
        return [("Duration", "5 s")]

    thread = EstimatorThread(_get_estimates)
    thread.delay = 0.05
    thread.new_estimates.connect(lambda estimates: emitted.append(estimates))

    with qtbot.waitSignal(thread.new_estimates, timeout=2000):
        thread.start()

    thread.stop()
    thread.wait(2000)

    assert len(emitted) >= 1
    assert emitted[0] == [("Duration", "5 s")]


def test_estimator_thread_run_stops_on_stop(qtbot):
    """After stop(), the thread exits its run loop."""

    call_count = {"n": 0}

    def _get_estimates():
        call_count["n"] += 1
        return []

    thread = EstimatorThread(_get_estimates)
    thread.delay = 0.05
    thread.start()
    qtbot.wait(80)
    thread.stop()
    thread.wait(2000)

    assert not thread.isRunning()
    n_after_stop = call_count["n"]
    qtbot.wait(80)
    assert call_count["n"] == n_after_stop


# --- check_get_estimates_signature tests -----------------------------------


def test_check_signature_plain(make_widget):
    """A plain get_estimates(self) sets neither provide_* flag."""
    wdg = make_widget(_ListEstimatesProcedure)

    assert wdg.provide_sequence is False
    assert wdg.provide_sequence_length is False
    assert wdg.number_of_estimates == 2


def test_check_signature_sequence_kwarg(make_widget):
    """A get_estimates(self, sequence=...) sets provide_sequence."""
    wdg = make_widget(_SeqOnlyProcedure)

    assert wdg.provide_sequence is True
    assert wdg.provide_sequence_length is False


def test_check_signature_sequence_length_kwarg(make_widget):
    """A get_estimates(self, sequence_length=...) sets provide_sequence_length."""
    wdg = make_widget(_SeqLengthOnlyProcedure)

    assert wdg.provide_sequence is False
    assert wdg.provide_sequence_length is True


def test_check_signature_both_kwargs(make_widget):
    """A get_estimates(self, sequence=..., sequence_length=...) sets both flags."""
    wdg = make_widget(_SeqEstimatesProcedure)

    assert wdg.provide_sequence is True
    assert wdg.provide_sequence_length is True
    assert wdg.number_of_estimates == 1


@pytest.mark.parametrize(
    "invalid_return", [
        "not a list",
        [("only one element",)],
        [("a", "b", "c")],
        ["not a tuple"],
        {"not": "a list"},
    ],
)
def test_check_signature_rejects_invalid_returns(qtbot, invalid_return):
    """Invalid get_estimates return shapes raise TypeError."""

    class _BadProcedure(Procedure):
        DATA_COLUMNS = []

        def get_estimates(self):
            return invalid_return

    parent = _FakeParent(_BadProcedure)
    qtbot.addWidget(parent)

    with pytest.raises(TypeError):
        EstimatorWidget(parent=parent)


def test_check_signature_stores_number_of_estimates(make_widget):
    """number_of_estimates reflects the length of the returned list."""

    class _ThreeProcedure(Procedure):
        DATA_COLUMNS = []

        def get_estimates(self):
            return [("a", "1"), ("b", "2"), ("c", "3")]

    wdg = make_widget(_ThreeProcedure)

    assert wdg.number_of_estimates == 3
    assert len(wdg.line_edits) == 3


# --- get_estimates / update_estimates / display_estimates ------------------


def test_get_estimates_passes_sequence_kwargs(make_widget):
    """get_estimates forwards sequence/sequence_length to the procedure."""
    seq = _FakeSequencer(sequence=[1, 2, 3])
    make_widget(_SeqEstimatesProcedure, sequencer=seq)

    # Construction already calls get_estimates; verify the recorded kwargs.
    assert _SeqEstimatesProcedure.calls
    last = _SeqEstimatesProcedure.calls[-1]
    assert last["sequence"] == [1, 2, 3]
    assert last["sequence_length"] == 3


def test_get_estimates_without_sequencer_passes_none(make_widget):
    """Without a sequencer, sequence and sequence_length are None."""
    make_widget(_SeqEstimatesProcedure)

    assert _SeqEstimatesProcedure.calls
    last = _SeqEstimatesProcedure.calls[-1]
    assert last["sequence"] is None
    assert last["sequence_length"] is None


def test_get_estimates_sequencer_error_sets_length_zero(make_widget):
    """If get_sequence raises SequenceEvaluationError, sequence_length is 0."""
    seq = _FakeSequencer(raise_error=True)
    make_widget(_SeqEstimatesProcedure, sequencer=seq)

    assert _SeqEstimatesProcedure.calls
    last = _SeqEstimatesProcedure.calls[-1]
    assert last["sequence"] is None
    assert last["sequence_length"] == 0


def test_get_estimates_int_return_uses_duration_conversion(make_widget):
    """An int/float return is converted via _estimates_from_duration."""
    wdg = make_widget(_DurationEstimatesProcedure)

    estimates = wdg.get_estimates()
    assert isinstance(estimates, list)
    assert estimates[0] == ("Duration", "42 s")
    assert estimates[1][0] == "Measurement finished at"
    assert wdg.number_of_estimates == 2


def test_update_estimates_populates_line_edits(make_widget):
    """update_estimates fills the line edits with label and value."""
    wdg = make_widget(_ListEstimatesProcedure)

    wdg.update_estimates()

    labels = [pair[0].text() for pair in wdg.line_edits]
    values = [pair[1].text() for pair in wdg.line_edits]
    assert labels == ["Duration", "Number of lines"]
    assert values == ["100 s", "10"]


def test_display_estimates_populates_line_edits(make_widget):
    """display_estimates sets the text of each line edit pair."""
    wdg = make_widget(_ListEstimatesProcedure)

    wdg.display_estimates([("label1", "val1"), ("label2", "val2")])

    assert wdg.line_edits[0][0].text() == "label1"
    assert wdg.line_edits[0][1].text() == "val1"
    assert wdg.line_edits[1][0].text() == "label2"
    assert wdg.line_edits[1][1].text() == "val2"


def test_display_estimates_wrong_count_raises(make_widget):
    """display_estimates raises ValueError if the number of estimates changes."""
    wdg = make_widget(_ListEstimatesProcedure)

    with pytest.raises(ValueError, match="Number of estimates changed"):
        wdg.display_estimates([("only", "one")])


# --- _estimates_from_duration ---------------------------------------------


def test_estimates_from_duration_without_sequencer(make_widget):
    """Without a sequencer, only Duration and Measurement finished at."""
    wdg = make_widget(_ListEstimatesProcedure)

    estimates = wdg._estimates_from_duration(100, None)

    assert len(estimates) == 2
    assert estimates[0] == ("Duration", "100 s")
    assert estimates[1][0] == "Measurement finished at"


def test_estimates_from_duration_with_sequencer(make_widget):
    """With a sequencer, sequence-related estimates are added."""
    seq = _FakeSequencer(sequence=[1, 2, 3])
    wdg = make_widget(_ListEstimatesProcedure, sequencer=seq)

    estimates = wdg._estimates_from_duration(10, 3)

    assert len(estimates) == 5
    assert estimates[0] == ("Duration", "10 s")
    assert estimates[1] == ("Sequence length", "3")
    assert estimates[2] == ("Sequence duration", "30 s")
    assert estimates[3][0] == "Measurement finished at"
    assert estimates[4][0] == "Sequence finished at"


def test_estimates_from_duration_zero_sequence_length(make_widget):
    """A zero sequence_length produces zero-valued sequence estimates."""
    seq = _FakeSequencer(sequence=[])
    wdg = make_widget(_ListEstimatesProcedure, sequencer=seq)

    estimates = wdg._estimates_from_duration(10, 0)

    assert estimates[1] == ("Sequence length", "0")
    assert estimates[2] == ("Sequence duration", "0 s")


# --- _set_continuous_updating ---------------------------------------------


def test_set_continuous_updating_unchecked_stops_thread(make_widget):
    """Unchecked state stops the update thread."""
    wdg = make_widget(_ListEstimatesProcedure)

    wdg.update_box.setCheckState(QtCore.Qt.CheckState.Unchecked)

    assert not wdg.update_thread.isRunning()


def test_set_continuous_updating_partially_checked_starts_thread(make_widget, qtbot):
    """PartiallyChecked state starts the thread with delay 2."""
    wdg = make_widget(_ListEstimatesProcedure)

    wdg.update_box.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
    qtbot.wait(50)

    assert wdg.update_thread.isRunning()
    assert wdg.update_thread.delay == 2


def test_set_continuous_updating_checked_starts_fast_thread(make_widget, qtbot):
    """Checked state starts the thread with delay 0.1."""
    wdg = make_widget(_ListEstimatesProcedure)

    wdg.update_box.setCheckState(QtCore.Qt.CheckState.Checked)
    qtbot.wait(50)

    assert wdg.update_thread.isRunning()
    assert wdg.update_thread.delay == 0.1
