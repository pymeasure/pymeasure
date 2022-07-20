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
import importlib
import logging

import pytest
import os
import tempfile
from time import sleep
from importlib.machinery import SourceFileLoader

from pymeasure.experiment import Listener, Procedure
from pymeasure.experiment.workers import Worker
from pymeasure.experiment.results import Results

tcp_libs_available = bool(importlib.util.find_spec('cloudpickle')
                          and importlib.util.find_spec('zmq'))

# Load the procedure, without it being in a module
data_path = os.path.join(os.path.dirname(__file__), 'data/procedure_for_testing.py')
RandomProcedure = SourceFileLoader('procedure', data_path).load_module().RandomProcedure
# from data.procedure_for_testing import RandomProcedure


def test_procedure():
    """ Ensure that the loaded test procedure is properly functioning
    """
    procedure = RandomProcedure()
    assert procedure.iterations == 100
    assert procedure.delay == 0.001
    assert hasattr(procedure, 'execute')


def test_worker_stop():
    procedure = RandomProcedure()
    file = tempfile.mktemp()
    results = Results(procedure, file)
    worker = Worker(results)
    worker.start()
    worker.stop()
    assert worker.should_stop()
    worker.join()


def test_worker_finish():
    procedure = RandomProcedure()
    procedure.iterations = 100
    procedure.delay = 0.001
    file = tempfile.mktemp()
    results = Results(procedure, file)
    worker = Worker(results)
    worker.start()
    worker.join(timeout=20.0)

    assert not worker.is_alive()

    new_results = Results.load(file, procedure_class=RandomProcedure)
    assert new_results.data.shape == (100, 2)


def test_worker_closes_file_after_finishing():
    procedure = RandomProcedure()
    procedure.iterations = 100
    procedure.delay = 0.001
    file = tempfile.mktemp()
    results = Results(procedure, file)
    worker = Worker(results)
    worker.start()
    worker.join(timeout=20.0)

    # Test if the file has been properly closed by removing the file
    os.remove(file)


@pytest.mark.skipif(not tcp_libs_available,
                    reason='TCP communication packages not installed')
def test_zmq_does_not_crash_worker(caplog):
    """Check that a ZMQ serialisation usage error does not cause a crash.

    See https://github.com/ralph-group/pymeasure/issues/168
    """
    procedure = RandomProcedure()
    file = tempfile.mktemp()
    results = Results(procedure, file)
    # If we define a port here we get ZMQ communication
    # if cloudpickle is installed
    worker = Worker(results, port=5888, log_level=logging.DEBUG)
    worker.start()
    worker.join(timeout=20.0)  # give it enough time to finish the procedure
    assert procedure.status == procedure.FINISHED
    del worker  # make sure to clean up, reduce the possibility of test
    # dependencies via left-over sockets


@pytest.mark.skipif(not tcp_libs_available,
                    reason='TCP communication packages not installed')
def test_zmq_topic_filtering_works(caplog):

    class ThreeEmitsProcedure(Procedure):
        def execute(self):
            self.emit('results', 'Data 1')
            self.emit('progress', 33)
            self.emit('results', 'Data 2')
            self.emit('progress', 66)
            self.emit('results', 'Data 3')
            self.emit('progress', 99)

    procedure = ThreeEmitsProcedure()
    file = tempfile.mktemp()
    results = Results(procedure, file)
    received = []
    worker = Worker(results, port=5888, log_level=logging.DEBUG)
    listener = Listener(port=5888, topic='results', timeout=4.0)
    sleep(4.0)  # leave time for subscriber and publisher to establish a connection
    worker.start()
    while True:
        if not listener.message_waiting():
            break
        topic, record = listener.receive()
        received.append((topic, record))
    worker.join(timeout=20.0)  # give it enough time to finish the procedure
    assert procedure.status == procedure.FINISHED
    assert len(received) == 3
    assert all([item[0] == 'results' for item in received])
