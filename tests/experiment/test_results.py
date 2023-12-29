#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
import pickle
import tempfile
from unittest import mock

import pandas as pd
import pytest
import numpy as np

from pymeasure.units import ureg
from pymeasure.experiment.results import Results, CSVFormatter
from pymeasure.experiment.procedure import Procedure, Parameter
from pymeasure.experiment import BooleanParameter
from data.procedure_for_testing import RandomProcedure


def test_procedure():
    """ Ensure that the loaded test procedure is properly functioning
    """
    procedure = RandomProcedure()
    assert procedure.iterations == 100
    assert procedure.delay == 0.001
    assert hasattr(procedure, 'execute')


def test_csv_formatter_format_header():
    """Tests CSVFormatter.format_header() method."""
    columns = ['t', 'x', 'y', 'z', 'V']
    formatter = CSVFormatter(columns=columns)
    assert formatter.format_header() == 't,x,y,z,V'


class Test_csv_formatter_format:
    def test_csv_formatter_format(self):
        """Tests CSVFormatter.format() method."""
        columns = ['t', 'x', 'y', 'z', 'V']
        formatter = CSVFormatter(columns=columns)
        data = {'t': 1, 'y': 2, 'z': 3.0, 'x': -1, 'V': 'abc'}
        assert formatter.format(data) == '1,-1,2,3.0,abc'

    @pytest.mark.parametrize("head, value, result",
                             (('index', 10, "10"),
                              ('length (m)', "50 cm", "0.5"),
                              ('voltage (V)', ureg.Quantity(-7, ureg.kV), "-7000.0"),
                              ('speed (m/s)', 15 * ureg.cm / ureg.s, "0.15"),
                              ('magnetic (T)', 7, "7"),
                              ('string', "abcdef", "abcdef"),
                              ('count', 9 * ureg.dimensionless, "9"),
                              ('boolean', True, "True"),
                              ('numpy (V)', np.float64(1.1), "1.1"),
                              ('boolean nan (V)', True, "nan"),
                              ))
    def test_unitful(self, head, value, result):
        """Test, whether units are appended correctly"""
        formatter = CSVFormatter(columns=[head])
        assert formatter.format({head: value}) == result

    def test_newly_unitful(self):
        formatter = CSVFormatter(columns=["count"])
        assert formatter.format({'count': 5 * ureg.km}) == "5000.0"
        assert formatter.units['count'] == ureg.m

    def test_no_newly_unitful(self):
        formatter = CSVFormatter(columns=["count"])
        assert formatter.format({'count': 5 * ureg.dimensionless}) == "5"
        assert formatter.units.get('count') is None

    def test_unitful_erroneous(self):
        """Test, whether wrong units are rejected"""
        columns = ['index', 'length (m)', 'voltage (V)']
        formatter = CSVFormatter(columns=columns)
        formatter.units['index'] = ureg.km
        data = {'index': "10 stupid", 'length (m)': "50 cV", 'voltage (V)': True}
        assert formatter.format(data) == "nan,nan,nan"


def test_procedure_filestorage():
    assert RandomProcedure.iterations.value == 100
    procedure = RandomProcedure()
    procedure.iterations = 101
    resultfile = tempfile.mktemp()
    results = Results(procedure, resultfile)

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
                                                                      read_csv_mock,
                                                                      path_exists_mock):
        procedure_mock = mock.MagicMock(spec=Procedure)
        result = Results(procedure_mock, 'test.csv')

        read_csv_mock.return_value = [pd.DataFrame(data={
            'A': [1, 2, 3, 4, 5, 6, 7],
            'B': [2, 3, 4, 5, 6, 7, 8]
        })]
        first_data = result.data

        # if no updates, read_csv returns a zero-row dataframe
        read_csv_mock.return_value = [pd.DataFrame(data={
            'A': [], 'B': []
        }, dtype=object)]
        second_data = result.data

        assert second_data.iloc[:, 0].dtype is not object
        assert first_data.iloc[:, 0].dtype is second_data.iloc[:, 0].dtype

    def test_regression_param_str_should_not_include_newlines(self, tmpdir):
        class DummyProcedure(Procedure):
            par = Parameter('Generic Parameter with newline chars')
            DATA_COLUMNS = ['Foo', 'Bar', 'Baz']
        procedure = DummyProcedure()
        procedure.par = np.linspace(1, 100, 17)
        filename = os.path.join(str(tmpdir), 'header_linebreak_test.csv')
        result = Results(procedure, filename)
        result.reload()  # assert no error
        pd.read_csv(filename, comment="#")  # assert no error
        assert (result.parameters['par'].value == np.linspace(1, 100, 17)).all()


def test_parameter_reading():
    data_path = os.path.join(os.path.dirname(__file__), "data/results_for_testing_parameters.csv")
    test_string = "/test directory with space/test_filename.csv"
    iterations = 101
    delay = 0.0005
    seed = '54321'

    class DummyProcedure(RandomProcedure):
        check_false = BooleanParameter('checkbox False')
        check_true = BooleanParameter('checkbox True')
        check_dir = Parameter('Directory string')

    results = Results.load(data_path, procedure_class=DummyProcedure)

    # Check if all parameters are correctly read from file
    assert results.parameters["iterations"].value == iterations
    assert results.parameters["delay"].value == delay
    assert results.parameters["seed"].value == seed

    assert results.parameters["check_true"].value is True
    assert results.parameters["check_false"].value is False
    assert results.parameters["check_dir"].value == test_string
