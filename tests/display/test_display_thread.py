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

from unittest import mock

from pymeasure.display.thread import StoppableQThread


class LoopingThread(StoppableQThread):
    """A StoppableQThread subclass whose run loops until should_stop."""

    def run(self):
        while not self.should_stop():
            pass


def test_initial_should_stop_false(qtbot):
    thread = StoppableQThread()
    try:
        assert thread.should_stop() is False
    finally:
        thread.deleteLater()


def test_stop_sets_should_stop(qtbot):
    thread = StoppableQThread()
    try:
        thread.stop()
        assert thread.should_stop() is True
    finally:
        thread.deleteLater()


def test_repr_contains_should_stop(qtbot):
    thread = StoppableQThread()
    try:
        representation = repr(thread)
        assert "StoppableQThread" in representation
        assert "should_stop" in representation
        assert "False" in representation
        thread.stop()
        assert "True" in repr(thread)
    finally:
        thread.deleteLater()


def test_join_calls_stop_when_not_stopped(qtbot):
    thread = LoopingThread()
    thread.start()
    try:
        assert thread.isRunning()
        with mock.patch.object(thread, "stop", wraps=thread.stop) as spy_stop:
            thread.join(timeout=0.5)
        assert spy_stop.called
        assert thread.should_stop() is True
        assert not thread.isRunning()
    finally:
        if thread.isRunning():
            thread.stop()
            thread.wait()


def test_join_returns_immediately_if_already_stopped(qtbot):
    thread = StoppableQThread()
    thread.stop()
    try:
        with mock.patch.object(thread, "stop", wraps=thread.stop) as spy_stop:
            thread.join(timeout=0)
        assert spy_stop.called is False
    finally:
        thread.deleteLater()


def test_subclass_run_respects_should_stop(qtbot):
    thread = LoopingThread()
    thread.start()
    try:
        assert thread.isRunning()
        thread.stop()
        thread.wait()
        assert not thread.isRunning()
        assert thread.should_stop() is True
    finally:
        if thread.isRunning():
            thread.stop()
            thread.wait()
