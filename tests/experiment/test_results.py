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

import os
import tempfile
import pickle
from importlib.machinery import SourceFileLoader

from pymeasure.experiment.results import Results, CSVFormatter

# Load the procedure, without it being in a module
#data_path = os.path.join(os.path.dirname(__file__), 'data/procedure_for_testing.py')
#RandomProcedure = SourceFileLoader('procedure', data_path).load_module().RandomProcedure
from data.procedure_for_testing import RandomProcedure


def test_procedure():
    """ Ensure that the loaded test procedure is properly functioning
    """
    p = RandomProcedure()
    assert p.iterations == 100
    assert hasattr(p, 'execute')


def test_csv_formatter_format_header():
    """Tests CSVFormatter.format_header() method."""
    columns = ['t', 'x', 'y', 'z', 'V']
    formatter = CSVFormatter(columns=columns)
    assert formatter.format_header() == 't,x,y,z,V'


def test_csv_formatter_format():
    """Tests CSVFormatter.format() method."""
    columns = ['t', 'x', 'y', 'z', 'V']
    formatter = CSVFormatter(columns=columns)
    data = {'t': 1, 'y': 2, 'z': 3.0, 'x': -1, 'V': 'abc'}
    assert formatter.format(data) == '1,-1,2,3.0,abc'


def test_procedure_wrapper():
    assert RandomProcedure.iterations.value == 100
    procedure = RandomProcedure()
    procedure.iterations = 101
    file = tempfile.mktemp()
    results = Results(procedure, file)

    new_results = pickle.loads(pickle.dumps(results))
    assert hasattr(new_results, 'procedure')
    assert new_results.procedure.iterations == 101
    assert RandomProcedure.iterations.value == 100