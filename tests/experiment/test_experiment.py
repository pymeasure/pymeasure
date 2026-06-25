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

import configparser
from unittest import mock

import numpy as np
import pandas as pd
import pytest

from pymeasure.experiment.experiment import (
    Experiment,
    create_filename,
    get_array,
    get_array_steps,
    get_array_zero,
)
from data.procedure_for_testing import RandomProcedure


# ---------------------------------------------------------------------------
# get_array tests
# ---------------------------------------------------------------------------


def test_get_array_ascending():
    arr = get_array(0, 10, 2)
    assert np.allclose(arr, [0, 2, 4, 6, 8, 10])


def test_get_array_descending():
    arr = get_array(10, 0, 2)
    assert np.allclose(arr, [10, 8, 6, 4, 2, 0])


def test_get_array_single_step():
    arr = get_array(0, 1, 1)
    assert np.allclose(arr, [0, 1])


def test_get_array_inclusive_endpoint():
    # stop is divisible by step, stop must be included
    arr = get_array(0, 10, 5)
    assert arr[-1] == 10
    assert arr[0] == 0


# ---------------------------------------------------------------------------
# get_array_steps tests
# ---------------------------------------------------------------------------


def test_get_array_steps_even():
    arr = get_array_steps(0, 10, 5)
    assert len(arr) == 6
    assert np.isclose(arr[0], 0)
    assert np.isclose(arr[-1], 10)


def test_get_array_steps_count():
    numsteps = 7
    arr = get_array_steps(0, 10, numsteps)
    assert len(arr) == numsteps + 1


# ---------------------------------------------------------------------------
# get_array_zero tests
# ---------------------------------------------------------------------------


def test_get_array_zero_shape():
    arr = get_array_zero(5, 1)
    # Three segments: 0->5, 5->-5, -5->0 (endpoints 5, -5 excluded)
    # Lengths: 5, 10, 5 -> total 20
    assert arr[0] == 0
    assert np.isclose(arr[-1], 0) or np.isclose(arr[-1], -1)
    assert 5 in arr
    assert -5 in arr


def test_get_array_zero_starts_at_zero_ends_near_zero():
    arr = get_array_zero(5, 1)
    assert arr[0] == 0
    # Last element should be -1 (since np.arange(-5, 0, 1) ends at -1)
    assert np.isclose(arr[-1], -1) or np.isclose(arr[-1], 0)


def test_get_array_zero_visits_max_and_min():
    arr = get_array_zero(5, 1)
    assert 5 in arr
    assert -5 in arr


# ---------------------------------------------------------------------------
# create_filename tests
# ---------------------------------------------------------------------------


def test_create_filename_no_config_section_uses_mktemp(monkeypatch):
    monkeypatch.delenv("CONFIG", raising=False)
    config = configparser.ConfigParser()
    with mock.patch(
        "pymeasure.experiment.experiment.get_config", return_value=config
    ), mock.patch(
        "pymeasure.experiment.experiment.tempfile.mktemp",
        return_value="/tmp/fake_temp.csv",
    ) as mock_mktemp:
        filename = create_filename("title")
    mock_mktemp.assert_called_once_with()
    assert filename == "/tmp/fake_temp.csv"


def test_create_filename_with_config_section_uses_unique_filename(monkeypatch):
    monkeypatch.delenv("CONFIG", raising=False)
    config = configparser.ConfigParser()
    config["Filename"] = {"directory": "/some/dir", "prefix": "DATA"}
    with mock.patch(
        "pymeasure.experiment.experiment.get_config", return_value=config
    ), mock.patch(
        "pymeasure.experiment.experiment.unique_filename",
        return_value="/some/dir/DATA_title.csv",
    ) as mock_unique:
        filename = create_filename("title")
    assert filename == "/some/dir/DATA_title.csv"
    _, kwargs = mock_unique.call_args
    assert kwargs["suffix"] == "_title"
    assert kwargs["directory"] == "/some/dir"
    assert kwargs["prefix"] == "DATA"


def test_create_filename_includes_title(monkeypatch):
    monkeypatch.delenv("CONFIG", raising=False)
    config = configparser.ConfigParser()
    config["Filename"] = {"directory": "/some/dir"}
    with mock.patch(
        "pymeasure.experiment.experiment.get_config", return_value=config
    ), mock.patch(
        "pymeasure.experiment.experiment.unique_filename",
        return_value="/some/dir/DATA_myTitle.csv",
    ) as mock_unique:
        create_filename("myTitle")
    _, kwargs = mock_unique.call_args
    assert kwargs["suffix"] == "_myTitle"


# ---------------------------------------------------------------------------
# Experiment class tests
# ---------------------------------------------------------------------------


@pytest.fixture
def empty_config(monkeypatch):
    monkeypatch.delenv("CONFIG", raising=False)
    config = configparser.ConfigParser()
    return config


@pytest.fixture
def mock_dependencies(monkeypatch, empty_config):
    """Patch the dependencies of Experiment.__init__ for isolation."""
    monkeypatch.setattr(
        "pymeasure.experiment.experiment.get_config", lambda: empty_config
    )
    mock_scribe = mock.MagicMock()
    monkeypatch.setattr(
        "pymeasure.experiment.experiment.console_log", mock.Mock(return_value=mock_scribe)
    )
    mock_setup = mock.MagicMock()
    monkeypatch.setattr("pymeasure.experiment.experiment.setup_logging", mock_setup)
    monkeypatch.setattr(
        "pymeasure.experiment.experiment.set_mpl_rcparams", mock.MagicMock()
    )
    mock_results = mock.MagicMock()
    mock_worker = mock.MagicMock()
    monkeypatch.setattr(
        "pymeasure.experiment.experiment.Results", mock.Mock(return_value=mock_results)
    )
    monkeypatch.setattr(
        "pymeasure.experiment.experiment.Worker", mock.Mock(return_value=mock_worker)
    )
    return {
        "scribe": mock_scribe,
        "setup_logging": mock_setup,
        "results": mock_results,
        "worker": mock_worker,
    }


def test_experiment_initialization(mock_dependencies, monkeypatch):
    procedure = RandomProcedure()
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value="/tmp/data.csv"
    ):
        exp = Experiment("My Experiment", procedure)
    assert exp.title == "My Experiment"
    assert exp.procedure is procedure
    assert exp.measlist == []
    assert exp.port == 5888
    assert exp.plots == []
    assert exp._data_timeout == 10
    mock_dependencies["scribe"].start.assert_called_once()
    assert exp.filename == "/tmp/data.csv"
    assert exp.results is mock_dependencies["results"]
    assert exp.worker is mock_dependencies["worker"]


def test_experiment_initialization_with_logging_section(monkeypatch):
    config = configparser.ConfigParser()
    config["Logging"] = {"console": "True", "console_level": "INFO"}
    monkeypatch.delenv("CONFIG", raising=False)
    monkeypatch.setattr("pymeasure.experiment.experiment.get_config", lambda: config)
    monkeypatch.setattr(
        "pymeasure.experiment.experiment.set_mpl_rcparams", mock.MagicMock()
    )
    mock_setup = mock.MagicMock()
    monkeypatch.setattr("pymeasure.experiment.experiment.setup_logging", mock_setup)
    mock_scribe = mock.MagicMock()
    mock_setup.return_value = mock_scribe
    mock_results = mock.MagicMock()
    mock_worker = mock.MagicMock()
    monkeypatch.setattr(
        "pymeasure.experiment.experiment.Results", mock.Mock(return_value=mock_results)
    )
    monkeypatch.setattr(
        "pymeasure.experiment.experiment.Worker", mock.Mock(return_value=mock_worker)
    )
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value="/tmp/data.csv"
    ):
        procedure = RandomProcedure()
        Experiment("Title", procedure)

    mock_setup.assert_called_once()
    args, kwargs = mock_setup.call_args
    # console_log should NOT be called; setup_logging called with Logging section kwargs
    assert "console" in kwargs
    assert kwargs["console"] == "True"
    assert kwargs["console_level"] == "INFO"


def test_experiment_start_calls_worker_start(mock_dependencies, monkeypatch):
    procedure = RandomProcedure()
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value="/tmp/data.csv"
    ):
        exp = Experiment("My Experiment", procedure)
    exp.start()
    mock_dependencies["worker"].start.assert_called_once()


def test_data_property_returns_analysed_data(mock_dependencies, monkeypatch):
    df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    mock_dependencies["results"].data = df
    procedure = RandomProcedure()
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value="/tmp/data.csv"
    ):
        exp = Experiment("Title", procedure, analyse=lambda df: df + 1)
    data = exp.data
    expected = df + 1
    pd.testing.assert_frame_equal(data, expected)
    # Ensure a copy was returned (mutation doesn't affect results.data)
    assert data is not df


def test_data_property_default_analyse_is_identity(mock_dependencies, monkeypatch):
    df = pd.DataFrame({"x": [1, 2, 3]})
    mock_dependencies["results"].data = df
    procedure = RandomProcedure()
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value="/tmp/data.csv"
    ):
        exp = Experiment("Title", procedure)
    data = exp.data
    pd.testing.assert_frame_equal(data, df)
    assert data is not df  # default analyse returns a copy


def test_wait_for_data_returns_true_when_data_present(mock_dependencies, monkeypatch):
    df = pd.DataFrame({"x": [1, 2, 3]})
    mock_dependencies["results"].data = df
    procedure = RandomProcedure()
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value="/tmp/data.csv"
    ):
        exp = Experiment("Title", procedure)
    assert exp.wait_for_data() is True


def test_wait_for_data_times_out(mock_dependencies, monkeypatch):
    empty_df = pd.DataFrame()
    # data property recomputes analyse(self.results.data.copy()); make results.data always empty
    mock_dependencies["results"].data = empty_df
    procedure = RandomProcedure()
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value="/tmp/data.csv"
    ):
        exp = Experiment("Title", procedure)
    exp._data_timeout = 0.1
    assert exp.wait_for_data() is False


def test_del_stops_scribe_and_worker(mock_dependencies, monkeypatch):
    procedure = RandomProcedure()
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value="/tmp/data.csv"
    ):
        exp = Experiment("Title", procedure)
    mock_dependencies["worker"].is_alive.return_value = True
    recorder_queue = mock.MagicMock()
    monitor_queue = mock.MagicMock()
    mock_dependencies["worker"].recorder_queue = recorder_queue
    mock_dependencies["worker"].monitor_queue = monitor_queue

    exp.__del__()

    mock_dependencies["scribe"].stop.assert_called()
    recorder_queue.put.assert_called_with(None)
    monitor_queue.put.assert_called_with(None)
    mock_dependencies["worker"].stop.assert_called()


# ---------------------------------------------------------------------------
# Plotting tests (require matplotlib and IPython)
# ---------------------------------------------------------------------------


@pytest.fixture
def experiment_with_data(mock_dependencies, monkeypatch):
    matplotlib = pytest.importorskip("matplotlib")
    pytest.importorskip("IPython")
    matplotlib.use("Agg")

    df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    mock_dependencies["results"].data = df
    procedure = RandomProcedure()
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value="/tmp/data.csv"
    ):
        exp = Experiment("Title", procedure)
    return exp


def test_clear_plot_empties_lists(experiment_with_data):
    exp = experiment_with_data
    fig = mock.MagicMock()
    pl = mock.MagicMock()
    exp.figs = [fig]
    exp.plots = [pl]
    exp.clear_plot()
    assert exp.figs == []
    assert exp.plots == []
    fig.clf.assert_called_once()
    pl.close.assert_called_once()


def test_update_line_sets_data(experiment_with_data):
    exp = experiment_with_data
    ax = mock.MagicMock()
    line = mock.MagicMock()
    line._xorig = mock.MagicMock()
    line._yorig = mock.MagicMock()
    exp._data = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    exp.update_line(ax, line, "x", "y")
    line.set_xdata.assert_called_once()
    line.set_ydata.assert_called_once()
    ax.relim.assert_called_once()
    ax.autoscale.assert_called_once()
