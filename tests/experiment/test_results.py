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


class TestPandas3Numpy2Compat:
    """Tests verifying compatibility with pandas 3.0 and numpy 2.0."""

    @staticmethod
    def _write_rows(result, rows):
        """Append data rows directly to the results file."""
        with open(result.data_filename, 'a', encoding=Results.ENCODING) as f:
            for row in rows:
                f.write(result.format(row) + Results.LINE_BREAK)

    def test_results_numeric_dtype_preserved_after_reload(self, tmpdir):
        """Numeric dtypes must be preserved after writing and reloading a Results file."""
        class DummyProcedure(Procedure):
            DATA_COLUMNS = ['x', 'y']

        procedure = DummyProcedure()
        filename = os.path.join(str(tmpdir), 'dtype_test.csv')
        result = Results(procedure, filename)

        self._write_rows(result, [{'x': float(i), 'y': float(i) * 2.5} for i in range(5)])
        result.reload()

        assert result.data['x'].dtype == np.float64
        assert result.data['y'].dtype == np.float64

    def test_results_numeric_dtype_preserved_after_incremental_read(self, tmpdir):
        """Numeric dtypes must not become object/str when reading new rows incrementally."""
        class DummyProcedure(Procedure):
            DATA_COLUMNS = ['x', 'y']

        procedure = DummyProcedure()
        filename = os.path.join(str(tmpdir), 'incremental_dtype_test.csv')
        result = Results(procedure, filename)

        self._write_rows(result, [{'x': float(i), 'y': float(i) * 1.5} for i in range(5)])
        first_data = result.data
        first_dtype = first_data['x'].dtype

        self._write_rows(result, [{'x': float(i), 'y': float(i) * 1.5} for i in range(5, 10)])
        second_data = result.data

        assert second_data['x'].dtype == first_dtype
        assert second_data['y'].dtype == first_dtype
        assert len(second_data) == 10

    def test_results_concat_sort_false_preserves_column_order(self, tmpdir):
        """pd.concat with sort=False must preserve column order from DATA_COLUMNS."""
        class DummyProcedure(Procedure):
            DATA_COLUMNS = ['z', 'a', 'b']

        procedure = DummyProcedure()
        filename = os.path.join(str(tmpdir), 'column_order_test.csv')
        result = Results(procedure, filename)

        self._write_rows(result, [
            {'z': float(i), 'a': float(i + 1), 'b': float(i + 2)} for i in range(3)
        ])
        result.reload()

        assert list(result.data.columns) == ['z', 'a', 'b']

    def test_boolean_parameter_numpy_bool_(self):
        """BooleanParameter must accept np.bool_ values (numpy 2.0 replacement for np.bool)."""
        from pymeasure.experiment import BooleanParameter
        p = BooleanParameter('Test')
        p.value = np.bool_(True)
        assert p.value is True
        p.value = np.bool_(False)
        assert p.value is False

    def test_results_empty_file_returns_empty_dataframe(self, tmpdir):
        """An empty Results file must return an empty DataFrame without dtype errors."""
        class DummyProcedure(Procedure):
            DATA_COLUMNS = ['x', 'y']

        procedure = DummyProcedure()
        filename = os.path.join(str(tmpdir), 'empty_test.csv')
        result = Results(procedure, filename)

        data = result.data
        assert isinstance(data, pd.DataFrame)
        assert list(data.columns) == ['x', 'y']
        assert len(data) == 0


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
