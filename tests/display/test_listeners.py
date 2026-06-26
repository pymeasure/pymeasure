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
import logging
from unittest import mock

import pytest

from pymeasure.display import listeners
from pymeasure.display.Qt import QtCore
from pymeasure.display.listeners import Monitor, QListener
from pymeasure.experiment.procedure import Procedure


# ---------------------------------------------------------------------------
# Monitor tests (no zmq dependency)
# ---------------------------------------------------------------------------

def test_monitor_initialization(qtbot):
    queue = mock.MagicMock()
    monitor = Monitor(queue)
    try:
        assert monitor.queue is queue
        assert isinstance(monitor, QtCore.QThread)
    finally:
        monitor.deleteLater()


@pytest.mark.parametrize(
    "status, signal_name",
    [
        (Procedure.RUNNING, "worker_running"),
        (Procedure.FAILED, "worker_failed"),
        (Procedure.FINISHED, "worker_finished"),
        (Procedure.ABORTED, "worker_abort_returned"),
    ],
    ids=["running", "failed", "finished", "aborted"],
)
def test_monitor_emits_status(qtbot, status, signal_name):
    queue = mock.MagicMock()
    queue.get.side_effect = [("status", status), None]
    monitor = Monitor(queue)
    emitted = []
    getattr(monitor, signal_name).connect(lambda: emitted.append(True))
    monitor.status.connect(lambda data: emitted.append(("status", data)))
    try:
        monitor.run()
        assert ("status", status) in emitted
        assert True in emitted
    finally:
        monitor.deleteLater()


def test_monitor_emits_progress(qtbot):
    queue = mock.MagicMock()
    queue.get.side_effect = [("progress", 42.5), None]
    monitor = Monitor(queue)
    received = []
    monitor.progress.connect(lambda value: received.append(value))
    try:
        monitor.run()
        assert received == [42.5]
    finally:
        monitor.deleteLater()


def test_monitor_emits_log(qtbot):
    record = logging.LogRecord(
        "name", logging.INFO, __file__, 1, "message", None, None
    )
    queue = mock.MagicMock()
    queue.get.side_effect = [("log", record), None]
    monitor = Monitor(queue)
    received = []
    monitor.log.connect(lambda value: received.append(value))
    try:
        monitor.run()
        assert received == [record]
    finally:
        monitor.deleteLater()


def test_monitor_stops_on_none(qtbot):
    queue = mock.MagicMock()
    queue.get.side_effect = [None]
    monitor = Monitor(queue)
    try:
        monitor.run()
        assert queue.get.call_count == 1
    finally:
        monitor.deleteLater()


def test_monitor_processes_multiple_messages(qtbot):
    record = logging.LogRecord(
        "name", logging.INFO, __file__, 1, "log message", None, None
    )
    messages = [
        ("status", Procedure.RUNNING),
        ("progress", 10.0),
        ("log", record),
        ("status", Procedure.FINISHED),
        None,
    ]
    queue = mock.MagicMock()
    queue.get.side_effect = messages
    monitor = Monitor(queue)
    statuses = []
    progresses = []
    logs = []
    worker_running_fired = []
    worker_finished_fired = []
    monitor.status.connect(lambda data: statuses.append(data))
    monitor.progress.connect(lambda value: progresses.append(value))
    monitor.log.connect(lambda value: logs.append(value))
    monitor.worker_running.connect(lambda: worker_running_fired.append(True))
    monitor.worker_finished.connect(lambda: worker_finished_fired.append(True))
    try:
        monitor.run()
        assert statuses == [Procedure.RUNNING, Procedure.FINISHED]
        assert progresses == [10.0]
        assert logs == [record]
        assert worker_running_fired == [True]
        assert worker_finished_fired == [True]
    finally:
        monitor.deleteLater()


# ---------------------------------------------------------------------------
# QListener tests (require zmq/cloudpickle; mocked at the module level)
# ---------------------------------------------------------------------------

@pytest.fixture
def mocked_zmq(monkeypatch):
    """Patch the module-level zmq attribute of listeners with a MagicMock."""
    pytest.importorskip("zmq")
    fake_zmq = mock.MagicMock()
    monkeypatch.setattr(listeners, "zmq", fake_zmq)
    return fake_zmq


def test_qlistener_initialization(qtbot, mocked_zmq):
    port = 12345
    topic = "mytopic"
    timeout = 0.5
    listener = QListener(port=port, topic=topic, timeout=timeout)
    try:
        assert listener.port == port
        assert listener.topic == topic
        assert listener.timeout == timeout
        # context and socket created
        assert mocked_zmq.Context.called
        assert listener.context is mocked_zmq.Context.return_value
        assert listener.subscriber is listener.context.socket.return_value
        # connected to tcp://localhost:{port}
        listener.subscriber.connect.assert_called_once_with(
            f"tcp://localhost:{port}"
        )
        # SUBSCRIBE setsockopt called with topic encoded
        listener.subscriber.setsockopt.assert_called_once_with(
            mocked_zmq.SUBSCRIBE, topic.encode()
        )
        # poller registered
        assert listener.poller is mocked_zmq.Poller.return_value
        listener.poller.register.assert_called_once_with(
            listener.subscriber, mocked_zmq.POLLIN
        )
    finally:
        listener.deleteLater()


def test_qlistener_repr(qtbot, mocked_zmq):
    listener = QListener(port=9999, topic="t", timeout=0.1)
    try:
        representation = repr(listener)
        assert "QListener" in representation
        assert "port=9999" in representation
        assert "topic=t" in representation
        assert "should_stop" in representation
    finally:
        listener.deleteLater()


def test_message_waiting_returns_poller_result(qtbot, mocked_zmq):
    listener = QListener(port=1, topic="", timeout=0.02)
    try:
        listener.poller.poll.return_value = ["some_result"]
        assert listener.message_waiting() == ["some_result"]
        listener.poller.poll.assert_called_once_with(0.02)
    finally:
        listener.deleteLater()


def test_receive_returns_topic_and_record(qtbot, mocked_zmq):
    pytest.importorskip("cloudpickle")
    listener = QListener(port=1, topic="", timeout=0.01)
    try:
        payload = {"value": 7}
        # recv_serialized returns the post-deserialize tuple (str, object)
        listener.subscriber.recv_serialized.return_value = ("topic", payload)
        topic, record = listener.receive()
        assert topic == "topic"
        assert record == payload
    finally:
        listener.deleteLater()
