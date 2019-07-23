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
from unittest import mock

import os
import tempfile
import pickle
from importlib.machinery import SourceFileLoader
import pandas as pd
import numpy as np
from pymeasure.experiment.results import Results, CSVFormatter
from pymeasure.experiment.procedure import Procedure, Parameter

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


class TestResults:
    # TODO: add a full set of Results tests

    @mock.patch('pymeasure.experiment.results.open', mock.mock_open(), create=True)
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('pymeasure.experiment.results.pd.read_csv')
    def test_regression_attr_data_when_up_to_date_should_retain_dtype(self,
            read_csv_mock, path_exists_mock):
        procedure_mock = mock.MagicMock(spec=Procedure)
        result = Results(procedure_mock, 'test.csv')

        read_csv_mock.return_value = [pd.DataFrame(data={
                'A': [1,2,3,4,5,6,7],
                'B': [2,3,4,5,6,7,8]
            })]
        first_data = result.data

        # if no updates, read_csv returns a zero-row dataframe
        read_csv_mock.return_value = [pd.DataFrame(data={
            'A': [], 'B': []
            }, dtype=object)]
        second_data = result.data

        assert second_data.iloc[:,0].dtype is not object
        assert first_data.iloc[:,0].dtype is second_data.iloc[:,0].dtype
        
    def test_regression_param_str_should_not_include_newlines(self, tmpdir):
        class DummyProcedure(Procedure):
            par = Parameter('Generic Parameter with newline chars')           
            DATA_COLUMNS = ['Foo', 'Bar', 'Baz'] 
        procedure = DummyProcedure()
        procedure.par = np.linspace(1,100,17)
        filename = os.path.join(str(tmpdir), 'header_linebreak_test.csv')
        result = Results(procedure, filename)
        result.reload() # assert no error
        pd.read_csv(filename, comment="#") # assert no error
        assert (result.parameters['par'].value == np.linspace(1,100,17)).all()
