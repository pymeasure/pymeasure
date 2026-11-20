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
from data.procedure_for_testing import RandomProcedure

from pymeasure.experiment.experiment import (
    Experiment,
    create_filename,
    get_array,
    get_array_steps,
    get_array_zero,
)

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


def test_get_array_zero_queries_max_and_min():
    """get_array_zero sweeps 0 -> maxval -> -maxval -> back towards 0.

    The final segment is ``arange(-maxval, 0, step)``, which stops one step
    before 0, so the LAST element is ``-maxval + step`` (=-1 for ``(5, 1)``):
    the implementation never returns to 0 despite the docstring claiming so.
    """
    arr = get_array_zero(5, 1)
    np.testing.assert_array_equal(
        arr,
        np.concatenate((np.arange(0, 5), np.arange(5, -5, -1), np.arange(-5, 0))),
    )
    assert arr[0] == 0
    assert 5 in arr
    assert -5 in arr
    assert arr[-1] == -1


def test_get_array_zero_shape():
    """Length is the three segments: arange(0, m, s) + arange(m, -m, -s) + arange(-m, 0, s)."""
    arr = get_array_zero(2, 0.5)
    assert arr[0] == 0
    assert arr.max() == 2
    assert arr.min() == -2
    assert len(arr) == 4 + 8 + 4


# ---------------------------------------------------------------------------
# create_filename tests
# ---------------------------------------------------------------------------


def test_create_filename_no_config_section_uses_mktemp(monkeypatch):
    monkeypatch.delenv("CONFIG", raising=False)
    config = configparser.ConfigParser()
    with mock.patch(
        "pymeasure.experiment.experiment.get_config", return_value=config
    ), mock.patch(
        "pymeasure.experiment.experiment.tempfile.mkstemp",
        # Returns a tuple of (open file descriptor int, filename).
        return_value=(3, "/tmp/fake_temp.csv"),
    ) as mock_mktemp:
        filename = create_filename("title")
    mock_mktemp.assert_called_once_with()
    assert filename == (3, "/tmp/fake_temp.csv")


def test_create_filename_with_config_section_uses_unique_filename(monkeypatch):
    monkeypatch.delenv("CONFIG", raising=False)
    config = configparser.ConfigParser()
    config.read_string("[Filename]\ndirectory = /some/dir\nprefix = DATA\n")
    with mock.patch(
        "pymeasure.experiment.experiment.get_config", return_value=config
    ), mock.patch(
        "pymeasure.experiment.experiment.unique_filename",
        return_value="/some/dir/DATA_title.csv",
    ) as mock_unique:
        filename = create_filename("title")
    assert filename == (None, "/some/dir/DATA_title.csv")
    _, kwargs = mock_unique.call_args
    assert kwargs["suffix"] == "_title"
    assert kwargs["directory"] == "/some/dir"
    assert kwargs["prefix"] == "DATA"


def test_create_filename_ignores_default_section(monkeypatch):
    monkeypatch.delenv("CONFIG", raising=False)
    config = configparser.ConfigParser()
    config.read_string("[DEFAULT]\nbad_kwarg = leaked\n[Filename]\ndirectory = /some/dir\n")
    with mock.patch(
        "pymeasure.experiment.experiment.get_config", return_value=config
    ), mock.patch(
        "pymeasure.experiment.experiment.unique_filename",
        return_value="/some/dir/DATA_title.csv",
    ) as mock_unique:
        create_filename("title")
    _, kwargs = mock_unique.call_args
    # Only the Filename section's own items may be passed to unique_filename;
    # [DEFAULT] keys must not leak into the kwargs.
    assert kwargs["directory"] == "/some/dir"
    assert "bad_kwarg" not in kwargs


def test_create_filename_section_overrides_default(monkeypatch):
    monkeypatch.delenv("CONFIG", raising=False)
    config = configparser.ConfigParser()
    config.read_string(
        "[DEFAULT]\ndirectory = /def\nbad_kwarg = leaked\n"
        "[Filename]\ndirectory = /own\n"
    )
    with mock.patch(
        "pymeasure.experiment.experiment.get_config", return_value=config
    ), mock.patch(
        "pymeasure.experiment.experiment.unique_filename",
        return_value="/own/DATA_title.csv",
    ) as mock_unique:
        create_filename("title")
    _, kwargs = mock_unique.call_args
    # The section's own `directory` key must win over the same-named [DEFAULT]
    # key, while the still-inherited `bad_kwarg` must not leak.
    assert kwargs["directory"] == "/own"
    assert "bad_kwarg" not in kwargs


def test_create_filename_includes_title(monkeypatch):
    monkeypatch.delenv("CONFIG", raising=False)
    config = configparser.ConfigParser()
    config.read_string("[Filename]\ndirectory = /some/dir\n")
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


def make_experiment_mocks(monkeypatch, config):
    """Patch Experiment.__init__ dependencies to run against the given config.

    Returns the ``setup_logging`` mock; all other collaborators are MagicMocks.
    """
    monkeypatch.delenv("CONFIG", raising=False)
    monkeypatch.setattr("pymeasure.experiment.experiment.get_config", lambda: config)
    monkeypatch.setattr(
        "pymeasure.experiment.experiment.set_mpl_rcparams", mock.MagicMock()
    )
    mock_setup = mock.MagicMock()
    monkeypatch.setattr("pymeasure.experiment.experiment.setup_logging", mock_setup)
    mock_setup.return_value = mock.MagicMock()
    monkeypatch.setattr(
        "pymeasure.experiment.experiment.Results", mock.MagicMock()
    )
    monkeypatch.setattr(
        "pymeasure.experiment.experiment.Worker", mock.MagicMock()
    )
    return mock_setup


def test_experiment_initialization(mock_dependencies, monkeypatch):
    procedure = RandomProcedure()
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value=(None, "/tmp/data.csv")
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
    config.read_string("[Logging]\nconsole = True\nconsole_level = INFO\n")
    mock_setup = make_experiment_mocks(monkeypatch, config)
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value=(None, "/tmp/data.csv")
    ):
        Experiment("Title", RandomProcedure())

    mock_setup.assert_called_once()
    _args, kwargs = mock_setup.call_args
    # console_log should NOT be called; setup_logging called with Logging section kwargs
    assert "console" in kwargs
    assert kwargs["console"] == "True"
    assert kwargs["console_level"] == "INFO"


def test_experiment_initialization_logging_ignores_default_section(monkeypatch):
    config = configparser.ConfigParser()
    config.read_string("[DEFAULT]\nbad_kwarg = leaked\n[Logging]\nconsole = True\n")
    mock_setup = make_experiment_mocks(monkeypatch, config)
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value=(None, "/tmp/data.csv")
    ):
        Experiment("Title", RandomProcedure())

    mock_setup.assert_called_once()
    _args, kwargs = mock_setup.call_args
    # Only the Logging section's own items may be passed to setup_logging;
    # [DEFAULT] keys must not leak into the kwargs.
    assert kwargs["console"] == "True"
    assert "bad_kwarg" not in kwargs


def test_experiment_initialization_logging_section_overrides_default(monkeypatch):
    config = configparser.ConfigParser()
    config.read_string(
        "[DEFAULT]\nconsole = False\nbad_kwarg = leaked\n"
        "[Logging]\nconsole = True\n"
    )
    mock_setup = make_experiment_mocks(monkeypatch, config)
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value=(None, "/tmp/data.csv")
    ):
        Experiment("Title", RandomProcedure())

    mock_setup.assert_called_once()
    _args, kwargs = mock_setup.call_args
    # The section's own `console` key must win over the same-named [DEFAULT]
    # key, while the still-inherited `bad_kwarg` must not leak.
    assert kwargs["console"] == "True"
    assert "bad_kwarg" not in kwargs


def test_experiment_start_calls_worker_start(mock_dependencies, monkeypatch):
    procedure = RandomProcedure()
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value=(None, "/tmp/data.csv")
    ):
        exp = Experiment("My Experiment", procedure)
    exp.start()
    mock_dependencies["worker"].start.assert_called_once()


def test_data_property_returns_analysed_data(mock_dependencies, monkeypatch):
    df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    mock_dependencies["results"].data = df
    procedure = RandomProcedure()
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value=(None, "/tmp/data.csv")
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
        "pymeasure.experiment.experiment.create_filename", return_value=(None, "/tmp/data.csv")
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
        "pymeasure.experiment.experiment.create_filename", return_value=(None, "/tmp/data.csv")
    ):
        exp = Experiment("Title", procedure)
    assert exp.wait_for_data() is True


def test_wait_for_data_times_out(mock_dependencies, monkeypatch):
    empty_df = pd.DataFrame()
    # data property recomputes analyse(self.results.data.copy()); make results.data always empty
    mock_dependencies["results"].data = empty_df
    procedure = RandomProcedure()
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value=(None, "/tmp/data.csv")
    ):
        exp = Experiment("Title", procedure)
    exp._data_timeout = 0.1
    assert exp.wait_for_data() is False


def test_del_stops_scribe_and_worker(mock_dependencies, monkeypatch):
    procedure = RandomProcedure()
    with mock.patch(
        "pymeasure.experiment.experiment.create_filename", return_value=(None, "/tmp/data.csv")
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
        "pymeasure.experiment.experiment.create_filename", return_value=(None, "/tmp/data.csv")
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
