#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from pymeasure.display.log import LogHandler
from pymeasure.display.Qt import QtCore


def test_emitter_is_qobject():
    """LogHandler.Emitter is a QObject subclass with a record Signal."""
    assert issubclass(LogHandler.Emitter, QtCore.QObject)
    assert hasattr(LogHandler.Emitter, "record")
    assert isinstance(LogHandler.Emitter.record, QtCore.Signal)


def test_connect_delegates_to_emitter():
    """LogHandler.connect() connects to the emitter.record signal."""
    handler = LogHandler()
    received = []

    def callback(message):
        received.append(message)

    handler.connect(callback)

    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="hello", args=None, exc_info=None,
    )
    handler.emit(record)
    assert received == ["hello"]


def test_emit_emits_formatted_record(qtbot):
    """LogHandler.emit() emits the formatted record string on emitter.record."""
    handler = LogHandler()
    received = []

    def callback(message):
        received.append(message)

    handler.connect(callback)

    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="hello world", args=None, exc_info=None,
    )
    with qtbot.waitSignal(handler.emitter.record):
        handler.emit(record)
    assert received == ["hello world"]


def test_emit_uses_formatter():
    """LogHandler.emit() uses its formatter to format the record."""
    handler = LogHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))

    received = []

    def callback(message):
        received.append(message)

    handler.connect(callback)

    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="hello", args=None, exc_info=None,
    )
    handler.emit(record)
    assert received == [handler.formatter.format(record)]
    assert received == ["INFO:test:hello"]


def test_handler_integration_with_logger(qtbot):
    """LogHandler attached to a logger emits formatted log messages."""
    logger = logging.getLogger("pymeasure.test_log_integration")
    logger.setLevel(logging.DEBUG)
    handler = LogHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
    logger.addHandler(handler)

    received = []

    def callback(message):
        received.append(message)

    handler.connect(callback)

    try:
        with qtbot.waitSignal(handler.emitter.record):
            logger.info("integration message")
    finally:
        logger.removeHandler(handler)

    assert received == ["INFO:integration message"]
