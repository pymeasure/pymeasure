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

import time
from unittest import mock

from pymeasure.process import context
from pymeasure.log import Scribe, setup_logging


# TODO: Add tests for logging convenience functions and TopicQueueHandler

def test_scribe_stop():
    q = context.Queue()
    s = Scribe(q)
    s.start()
    assert s.is_alive() is True
    s.stop()
    assert s.is_alive() is False


def test_scribe_finish():
    q = context.Queue()
    s = Scribe(q)
    s.start()
    assert s.is_alive() is True
    q.put(None)
    time.sleep(0.1)
    assert s.is_alive() is False


def test_setup_file_logging():
    with mock.patch('pymeasure.log.file_log') as mocked_file_log:
        setup_logging()
        mocked_file_log.assert_not_called()
        setup_logging(filename='log.txt')
        mocked_file_log.assert_called_once()
