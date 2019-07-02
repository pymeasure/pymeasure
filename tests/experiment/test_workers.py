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

import pytest
import os
import tempfile
from time import sleep
from importlib.machinery import SourceFileLoader

from pymeasure.experiment.workers import Worker
from pymeasure.experiment.results import Results

# Load the procedure, without it being in a module
data_path = os.path.join(os.path.dirname(__file__), 'data/procedure_for_testing.py')
RandomProcedure = SourceFileLoader('procedure', data_path).load_module().RandomProcedure
#from data.procedure_for_testing import RandomProcedure


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
    worker.join(timeout=5)

    new_results = Results.load(file, procedure_class=RandomProcedure)
    assert new_results.data.shape == (100, 2)
