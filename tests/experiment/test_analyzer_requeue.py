"""Analyses queued while another analysis of the same routine runs.

Every analysis queued for one experiment shares that experiment's routine,
and the AnalyzerManager runs whichever row's routine is QUEUED. These tests
pin down that a row queued mid-run still gets a pass after the procedure has
ended (finished or aborted), that rows a finished pass already covered are
dropped rather than stranded, and that a new row never shows another row's
'Running' status.
"""
from queue import Queue
from types import SimpleNamespace

import pytest

from pymeasure.experiment import Procedure
from pymeasure.experiment.routine import Routine
from pymeasure.experiment.workers import Analyzer, request_analysis
from pymeasure.thread import StoppableThread


class _Analyzer(Analyzer):
    """An Analyzer around a bare routine, without results or ZMQ."""

    def __init__(self, routine, stop=False):
        StoppableThread.__init__(self)
        self.port = None
        self.routine = routine
        self.monitor_queue = Queue()
        self.context = None
        self.publisher = None
        if stop:
            self.stop()

    def statuses(self):
        out = []
        while True:
            item = self.monitor_queue.get_nowait()
            if item is None:
                return out
            topic, record = item
            if topic == 'status':
                out.append(record)


def _routine(procedure_status):
    routine = Routine()
    routine.procedure = SimpleNamespace(status=procedure_status)
    routine.status = Procedure.RUNNING  # an analysis of it is in flight
    return routine


def _shutdown(routine, stop=False):
    analyzer = _Analyzer(routine, stop=stop)
    analyzer.shutdown()
    return analyzer.statuses()


@pytest.mark.parametrize('ended', [Procedure.ABORTED, Procedure.FINISHED,
                                   Procedure.FAILED])
def test_request_after_procedure_ends_requeues(ended):
    # The abort/finish analysis is queued (after the worker is done) while
    # the last progress analysis still runs.
    routine = _routine(ended)
    request_analysis(routine)

    assert _shutdown(routine) == [Procedure.FINISHED, Procedure.QUEUED]
    assert routine.status == Procedure.QUEUED
    assert not routine.rerun_pending


@pytest.mark.parametrize('ended', [Procedure.ABORTED, Procedure.FINISHED,
                                   Procedure.FAILED])
def test_progress_request_does_not_rerun_once_procedure_ends(ended):
    # A progress update queued mid-pass, then the procedure ends before the
    # pass does. The Worker marks it ended before its recorder has finished
    # writing, so re-running now would read a half-written file; the end
    # signal's own request covers the final data instead.
    routine = _routine(Procedure.RUNNING)
    request_analysis(routine)
    routine.procedure.status = ended

    assert _shutdown(routine) == [Procedure.FINISHED]
    assert routine.status == Procedure.FINISHED


def test_no_request_after_procedure_ends_finishes():
    routine = _routine(Procedure.ABORTED)
    assert _shutdown(routine) == [Procedure.FINISHED]
    assert routine.status == Procedure.FINISHED


def test_procedure_still_running_requeues_as_before():
    routine = _routine(Procedure.RUNNING)
    assert _shutdown(routine) == [Procedure.FINISHED, Procedure.QUEUED]


def test_user_abort_wins_over_pending_rerun():
    routine = _routine(Procedure.ABORTED)
    request_analysis(routine)
    assert _shutdown(routine, stop=True) == [Procedure.ABORTED]
    assert not routine.rerun_pending


def test_request_after_finished_pass_requeues():
    routine = Routine()
    routine.status = Procedure.FINISHED
    request_analysis(routine)
    assert routine.status == Procedure.QUEUED


@pytest.mark.parametrize('status', [Procedure.FAILED, Procedure.ABORTED])
def test_request_leaves_failed_and_aborted_for_restart(status):
    routine = Routine()
    routine.status = status
    request_analysis(routine)
    assert routine.status == status
    assert not getattr(routine, 'rerun_pending', False)


# --- AnalyzerManager ------------------------------------------------------

class _Browser:
    def __init__(self):
        self.items = []

    def add(self, analysis):
        self.items.append(analysis.browser_item)

    def indexOfTopLevelItem(self, item):
        return self.items.index(item)

    def takeTopLevelItem(self, index):
        return self.items.pop(index)


class _Item:
    def __init__(self):
        self.status = None
        self.progress = None

    def setStatus(self, status):
        self.status = status

    def setProgress(self, progress):
        self.progress = progress


def _analysis(routine):
    return SimpleNamespace(analysis=routine, browser_item=_Item(),
                           data_filename='x', experiment=None)


@pytest.fixture
def manager():
    from pymeasure.display.manager import AnalyzerManager
    m = AnalyzerManager(_Browser())
    m._start_on_add = False  # no threads: drive the queue by hand
    return m


def test_finished_pass_drops_rows_it_covered(manager):
    old, new = Routine(), Routine()
    old.status = Procedure.FINISHED
    finished, covered = _analysis(old), _analysis(old)
    other = _analysis(new)
    for a in (finished, covered, other):
        manager.load(a)

    manager._drop_covered(finished)

    assert covered not in manager.analyses.queue
    assert covered.browser_item not in manager.browser.items
    assert other in manager.analyses.queue
    assert finished in manager.analyses.queue  # the widget removes this one


def test_requeued_pass_keeps_rows(manager):
    routine = Routine()
    routine.status = Procedure.QUEUED
    finished, waiting = _analysis(routine), _analysis(routine)
    manager.load(finished)
    manager.load(waiting)

    manager._drop_covered(finished)

    assert waiting in manager.analyses.queue


def test_queue_while_running_marks_rerun(manager):
    routine = Routine()
    routine.status = Procedure.RUNNING
    routine.procedure = SimpleNamespace(status=Procedure.ABORTED)
    manager.queue(_analysis(routine))
    assert routine.rerun_pending


def test_status_only_updates_row_not_procedure(manager):
    routine = Routine()
    running = _analysis(routine)
    running.procedure = SimpleNamespace(status=Procedure.ABORTED)
    manager._running_analysis = running
    manager._monitor = object()
    manager.sender = lambda: manager._monitor

    manager._update_status(Procedure.RUNNING)

    assert running.browser_item.status == Procedure.RUNNING
    assert running.procedure.status == Procedure.ABORTED


def test_stale_monitor_signal_is_ignored(manager):
    running = _analysis(Routine())
    manager._running_analysis = running
    manager._monitor = object()
    manager.sender = lambda: object()  # the previous analysis's monitor

    manager._update_status(Procedure.QUEUED)
    manager._update_progress(100.)

    assert running.browser_item.status is None
    assert running.browser_item.progress is None
