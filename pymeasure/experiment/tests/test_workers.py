#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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
from pymeasure.experiment.workers import Worker
from pymeasure.experiment.results import Results
import os
import tempfile
from time import sleep
from importlib.machinery import SourceFileLoader

# Load the procedure, without it being in a module
data_path = os.path.join(os.path.dirname(__file__), 'data/procedure_for_testing.py')
procedure = SourceFileLoader('procedure', data_path).load_module()

slow = pytest.mark.skipif(
    not pytest.config.getoption("--runslow"),
    reason="need --runslow option to run"
)


def test_procedure():
    """ Ensure that the loaded test procedure is properly functioning
    """
    p = procedure.TestProcedure()
    assert p.iterations == 100
    assert hasattr(p, 'execute')

def test_worker_stop():
    p = procedure.TestProcedure()
    f = tempfile.mktemp()
    r = Results(p, f)
    w = Worker(r)
    w.start()
    w.stop()
    assert w.should_stop()
    w.join()

@slow
def test_worker_finish():
    p = procedure.TestProcedure()
    f = tempfile.mktemp()
    r = Results(p, f)
    w = Worker(r)
    w.start()
    w.join()
    sleep(2)
    assert w.is_alive() == False