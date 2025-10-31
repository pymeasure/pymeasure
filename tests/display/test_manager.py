#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from pymeasure.display.manager import Experiment, ExperimentQueue, BaseManager, Manager
from pymeasure.experiment.procedure import Procedure
from pymeasure.experiment.results import Results
from pymeasure.display.browser import BrowserItem


class TestExperiment:
    """Test cases for Experiment class"""

    @pytest.fixture
    def mock_results(self):
        """Create a mock Results object for testing."""
        results = mock.MagicMock(spec=Results)
        results.data_filename = "test_data.csv"
        results.procedure = mock.MagicMock(spec=Procedure)
        return results

    def test_experiment_initialization(self, mock_results):
        """Test Experiment initialization with default parameters."""
        # Arrange & Act
        experiment = Experiment(results=mock_results)

        # Assert
        assert experiment.results == mock_results
        assert experiment.data_filename == "test_data.csv"
        assert experiment.procedure == mock_results.procedure
        assert experiment.curve_list is None
        assert experiment.browser_item is None

    def test_experiment_initialization_with_optional_params(self, mock_results):
        """Test Experiment initialization with optional parameters."""
        # Arrange
        curve_list = [mock.MagicMock(), mock.MagicMock()]
        browser_item = mock.MagicMock(spec=BrowserItem)

        # Act
        experiment = Experiment(
            results=mock_results, curve_list=curve_list, browser_item=browser_item
        )

        # Assert
        assert experiment.results == mock_results
        assert experiment.curve_list == curve_list
        assert experiment.browser_item == browser_item


class TestExperimentQueue:
    """Test cases for ExperimentQueue class"""

    @pytest.fixture
    def queue(self):
        """Create an ExperimentQueue instance for testing."""
        return ExperimentQueue()

    @pytest.fixture
    def mock_experiment(self):
        """Create a mock Experiment for testing."""
        experiment = mock.MagicMock(spec=Experiment)
        experiment.procedure = mock.MagicMock(spec=Procedure)
        return experiment

    def test_queue_initialization(self, queue):
        """Test ExperimentQueue initialization."""
        # Assert
        assert queue.queue == []

    def test_queue_append(self, queue, mock_experiment):
        """Test appending an experiment to the queue."""
        # Act
        queue.append(mock_experiment)

        # Assert
        assert len(queue.queue) == 1
        assert queue.queue[0] == mock_experiment

    def test_queue_remove_success(self, queue, mock_experiment):
        """Test removing an experiment from the queue."""
        # Arrange
        queue.append(mock_experiment)
        mock_experiment.procedure.status = Procedure.QUEUED

        # Act
        queue.remove(mock_experiment)

        # Assert
        assert len(queue.queue) == 0

    def test_queue_remove_experiment_not_in_queue(self, queue, mock_experiment):
        """Test removing an experiment that is not in the queue raises exception."""
        # Arrange
        mock_experiment.procedure.status = Procedure.QUEUED

        # Act & Assert
        with pytest.raises(
            Exception, match="Attempting to remove an Experiment that is not in the ExperimentQueue"
        ):
            queue.remove(mock_experiment)

    def test_queue_remove_running_experiment(self, queue, mock_experiment):
        """Test removing a running experiment raises exception."""
        # Arrange
        queue.append(mock_experiment)
        mock_experiment.procedure.status = Procedure.RUNNING

        # Act & Assert
        with pytest.raises(Exception, match="Attempting to remove a running experiment"):
            queue.remove(mock_experiment)

    def test_queue_contains_with_experiment(self, queue, mock_experiment):
        """Test checking if an experiment is in the queue."""
        # Arrange
        queue.append(mock_experiment)

        # Act & Assert
        assert mock_experiment in queue

    def test_queue_contains_with_filename_string(self, queue, mock_experiment):
        """Test checking if a filename string is in the queue."""
        # Arrange
        mock_experiment.data_filename = "/path/to/test_data.csv"
        queue.append(mock_experiment)

        # Act & Assert
        assert "test_data.csv" in queue
        assert "nonexistent.csv" not in queue

    def test_queue_contains_with_other_type(self, queue):
        """Test checking if a non-experiment, non-string is in the queue."""
        # Act & Assert
        assert 123 not in queue

    def test_queue_getitem(self, queue, mock_experiment):
        """Test accessing queue items by index."""
        # Arrange
        queue.append(mock_experiment)

        # Act & Assert
        assert queue[0] == mock_experiment

    def test_queue_next_with_queued_experiment(self, queue, mock_experiment):
        """Test getting the next queued experiment."""
        # Arrange
        mock_experiment.procedure.status = Procedure.QUEUED
        queue.append(mock_experiment)

        # Act
        result = queue.next()

        # Assert
        assert result == mock_experiment

    def test_queue_next_without_queued_experiment(self, queue, mock_experiment):
        """Test getting the next experiment when none are queued."""
        # Arrange
        mock_experiment.procedure.status = Procedure.FINISHED
        queue.append(mock_experiment)

        # Act & Assert
        with pytest.raises(StopIteration, match="There are no queued experiments"):
            queue.next()

    def test_queue_has_next_with_queued_experiment(self, queue, mock_experiment):
        """Test checking if there are queued experiments."""
        # Arrange
        mock_experiment.procedure.status = Procedure.QUEUED
        queue.append(mock_experiment)

        # Act
        result = queue.has_next()

        # Assert
        assert result is True

    def test_queue_has_next_without_queued_experiment(self, queue, mock_experiment):
        """Test checking if there are queued experiments when none are queued."""
        # Arrange
        mock_experiment.procedure.status = Procedure.FINISHED
        queue.append(mock_experiment)

        # Act
        result = queue.has_next()

        # Assert
        assert result is False

    def test_queue_with_browser_item_found(self, queue, mock_experiment):
        """Test finding an experiment by browser item."""
        # Arrange
        browser_item = mock.MagicMock()
        mock_experiment.browser_item = browser_item
        queue.append(mock_experiment)

        # Act
        result = queue.with_browser_item(browser_item)

        # Assert
        assert result == mock_experiment

    def test_queue_with_browser_item_not_found(self, queue, mock_experiment):
        """Test finding an experiment by browser item when not found."""
        # Arrange
        browser_item = mock.MagicMock()
        mock_experiment.browser_item = mock.MagicMock()
        queue.append(mock_experiment)

        # Act
        result = queue.with_browser_item(browser_item)

        # Assert
        assert result is None


class TestBaseManager:
    """Test cases for BaseManager class"""

    @pytest.fixture
    def manager(self):
        """Create a BaseManager instance for testing."""
        return BaseManager()

    @pytest.fixture
    def mock_experiment(self):
        """Create a mock Experiment for testing."""
        experiment = mock.MagicMock(spec=Experiment)
        experiment.procedure = mock.MagicMock(spec=Procedure)
        experiment.procedure.status = Procedure.QUEUED
        experiment.browser_item = mock.MagicMock()
        return experiment

    def test_manager_initialization_default(self):
        """Test BaseManager initialization with default parameters."""
        # Act
        manager = BaseManager()

        # Assert
        assert isinstance(manager.experiments, ExperimentQueue)
        assert manager._worker is None
        assert manager._running_experiment is None
        assert manager._monitor is None
        assert manager.log_level == 20  # logging.INFO
        assert manager.port == 5888
        assert manager._is_continuous is True
        assert manager._start_on_add is True

    def test_manager_initialization_custom(self):
        """Test BaseManager initialization with custom parameters."""
        # Act
        manager = BaseManager(port=1234, log_level=10)

        # Assert
        assert manager.port == 1234
        assert manager.log_level == 10

    def test_is_running_when_no_experiment(self, manager):
        """Test is_running when no experiment is running."""
        # Act
        result = manager.is_running()

        # Assert
        assert result is False

    def test_is_running_when_experiment_running(self, manager, mock_experiment):
        """Test is_running when an experiment is running."""
        # Arrange
        manager._running_experiment = mock_experiment

        # Act
        result = manager.is_running()

        # Assert
        assert result is True

    def test_running_experiment_when_running(self, manager, mock_experiment):
        """Test running_experiment when an experiment is running."""
        # Arrange
        manager._running_experiment = mock_experiment

        # Act
        result = manager.running_experiment()

        # Assert
        assert result == mock_experiment

    def test_running_experiment_when_not_running(self, manager):
        """Test running_experiment when no experiment is running."""
        # Act & Assert
        with pytest.raises(Exception, match="There is no Experiment running"):
            manager.running_experiment()

    def test_load_experiment(self, manager, mock_experiment):
        """Test loading an experiment."""
        # Act
        manager.load(mock_experiment)

        # Assert
        assert mock_experiment in manager.experiments

    def test_queue_experiment(self, manager, mock_experiment, qtbot):
        """Test queuing an experiment."""
        # Arrange
        with mock.patch.object(manager, "next") as mock_next:
            # Act & Assert
            with qtbot.waitSignal(manager.queued, timeout=1000):
                manager.queue(mock_experiment)

            # Additional assertions
            assert mock_experiment in manager.experiments
            mock_next.assert_called_once()

    def test_queue_experiment_start_on_add_false(self, manager, mock_experiment, qtbot):
        """Test queuing an experiment when start_on_add is False."""
        # Arrange
        manager._start_on_add = False
        with mock.patch.object(manager, "next") as mock_next:
            # Act & Assert
            with qtbot.waitSignal(manager.queued, timeout=1000):
                manager.queue(mock_experiment)

            # Additional assertions
            assert mock_experiment in manager.experiments
            mock_next.assert_not_called()

    def test_queue_experiment_already_running(self, manager, mock_experiment, qtbot):
        """Test queuing an experiment when one is already running."""
        # Arrange
        manager._running_experiment = mock.MagicMock()
        with mock.patch.object(manager, "next") as mock_next:
            # Act & Assert
            with qtbot.waitSignal(manager.queued, timeout=1000):
                manager.queue(mock_experiment)

            # Additional assertions
            assert mock_experiment in manager.experiments
            mock_next.assert_not_called()

    def test_remove_experiment(self, manager, mock_experiment):
        """Test removing an experiment."""
        # Arrange
        manager.experiments.append(mock_experiment)

        # Act
        manager.remove(mock_experiment)

        # Assert
        assert mock_experiment not in manager.experiments

    def test_clear_experiments(self, manager, mock_experiment):
        """Test clearing all experiments."""
        # Arrange
        manager.experiments.append(mock_experiment)
        manager.experiments.append(mock.MagicMock())

        # Act
        manager.clear()

        # Assert
        assert len(manager.experiments.queue) == 0

    def test_next_experiment_when_already_running(self, manager, mock_experiment):
        """Test starting next experiment when one is already running."""
        # Arrange
        manager._running_experiment = mock_experiment

        # Act & Assert
        with pytest.raises(Exception, match="Another procedure is already running"):
            manager.next()

    def test_next_experiment_when_no_queued_experiments(self, manager):
        """Test starting next experiment when no experiments are queued."""
        # Act & Assert
        with mock.patch.object(manager.experiments, "has_next", return_value=False):
            # This should not raise an exception and just return silently
            manager.next()

    def test_update_progress_when_running(self, manager, mock_experiment):
        """Test updating progress when an experiment is running."""
        # Arrange
        manager._running_experiment = mock_experiment

        # Act
        manager._update_progress(50)

        # Assert
        mock_experiment.browser_item.setProgress.assert_called_once_with(50)

    def test_update_progress_when_not_running(self, manager):
        """Test updating progress when no experiment is running."""
        # Act
        manager._update_progress(50)

        # Assert
        # Should not raise any exception and should not call setProgress

    def test_update_status_when_running(self, manager, mock_experiment):
        """Test updating status when an experiment is running."""
        # Arrange
        manager._running_experiment = mock_experiment
        mock_experiment.procedure.status = Procedure.QUEUED

        # Act
        manager._update_status(Procedure.RUNNING)

        # Assert
        assert mock_experiment.procedure.status == Procedure.RUNNING
        mock_experiment.browser_item.setStatus.assert_called_once_with(Procedure.RUNNING)

    def test_update_status_when_not_running(self, manager):
        """Test updating status when no experiment is running."""
        # Act
        manager._update_status(Procedure.RUNNING)

        # Assert
        # Should not raise any exception

    def test_update_log(self, manager, qtbot):
        """Test updating log."""
        # Arrange
        record = mock.MagicMock()

        # Act & Assert
        with qtbot.waitSignal(manager.log, timeout=1000):
            manager._update_log(record)

    def test_resume_manager(self, manager):
        """Test resuming the manager."""
        # Arrange
        manager._start_on_add = False
        manager._is_continuous = False
        with mock.patch.object(manager, "next") as mock_next:
            # Act
            manager.resume()

            # Assert
            assert manager._start_on_add is True
            assert manager._is_continuous is True
            mock_next.assert_called_once()

    def test_abort_when_no_experiment_running(self, manager):
        """Test aborting when no experiment is running."""
        # Act & Assert
        with pytest.raises(Exception, match="Attempting to abort when no experiment is running"):
            manager.abort()

    def test_abort_experiment(self, manager, mock_experiment, qtbot):
        """Test aborting a running experiment."""
        # Arrange
        manager._running_experiment = mock_experiment
        manager._worker = mock.MagicMock()

        # Act & Assert
        with qtbot.waitSignal(manager.aborted, timeout=1000):
            manager.abort()

        # Additional assertions
        assert manager._start_on_add is False
        assert manager._is_continuous is False
        manager._worker.stop.assert_called_once()

    def test_clean_up(self, manager, mock_experiment):
        """Test cleaning up resources."""
        # Arrange
        worker_mock = mock.MagicMock()
        monitor_mock = mock.MagicMock()
        manager._worker = worker_mock
        manager._monitor = monitor_mock
        manager._running_experiment = mock_experiment

        # Act
        manager._clean_up()

        # Assert
        worker_mock.join.assert_called_once()
        monitor_mock.wait.assert_called_once()
        assert manager._worker is None
        assert manager._running_experiment is None

    def test_failed_experiment(self, manager, mock_experiment, qtbot):
        """Test handling a failed experiment."""
        # Arrange
        manager._running_experiment = mock_experiment
        manager._worker = mock.MagicMock()
        manager._monitor = mock.MagicMock()

        with mock.patch.object(manager, "_clean_up"):
            # Act & Assert
            with qtbot.waitSignal(manager.failed, timeout=1000):
                manager._failed()

            # Additional assertions
            manager._clean_up.assert_called_once()

    def test_abort_returned(self, manager, mock_experiment, qtbot):
        """Test handling an abort returned."""
        # Arrange
        manager._running_experiment = mock_experiment
        manager._worker = mock.MagicMock()
        manager._monitor = mock.MagicMock()

        with mock.patch.object(manager, "_clean_up"):
            # Act & Assert
            with qtbot.waitSignal(manager.abort_returned, timeout=1000):
                manager._abort_returned()

            # Additional assertions
            manager._clean_up.assert_called_once()

    def test_finish_experiment_continuous(self, manager, mock_experiment, qtbot):
        """Test finishing an experiment with continuous mode enabled."""
        # Arrange
        manager._running_experiment = mock_experiment
        manager._worker = mock.MagicMock()
        manager._monitor = mock.MagicMock()
        manager._is_continuous = True

        with mock.patch.object(manager, "_clean_up"):
            with mock.patch.object(manager, "next") as mock_next:
                # Act & Assert
                with qtbot.waitSignal(manager.finished, timeout=1000):
                    manager._finish()

                # Additional assertions
                manager._clean_up.assert_called_once()
                mock_experiment.browser_item.setProgress.assert_called_once_with(100)
                mock_next.assert_called_once()


class TestManager:
    """Test cases for Manager class"""

    @pytest.fixture
    def mock_widget_list(self):
        """Create a mock widget list for testing."""
        return mock.MagicMock()

    @pytest.fixture
    def mock_browser(self):
        """Create a mock browser for testing."""
        return mock.MagicMock()

    @pytest.fixture
    def manager(self, mock_widget_list, mock_browser):
        """Create a Manager instance for testing."""
        return Manager(widget_list=mock_widget_list, browser=mock_browser)

    @pytest.fixture
    def mock_experiment(self):
        """Create a mock Experiment for testing."""
        experiment = mock.MagicMock(spec=Experiment)
        experiment.procedure = mock.MagicMock(spec=Procedure)
        experiment.procedure.status = Procedure.QUEUED
        experiment.browser_item = mock.MagicMock()
        experiment.curve_list = []
        return experiment

    def test_manager_initialization(self, mock_widget_list, mock_browser):
        """Test Manager initialization."""
        # Act
        manager = Manager(widget_list=mock_widget_list, browser=mock_browser)

        # Assert
        assert isinstance(manager.experiments, ExperimentQueue)
        assert manager._worker is None
        assert manager._running_experiment is None
        assert manager._monitor is None
        assert manager.log_level == 20  # logging.INFO
        assert manager.port == 5888
        assert manager.widget_list == mock_widget_list
        assert manager.browser == mock_browser

    def test_manager_initialization_with_custom_params(self, mock_widget_list, mock_browser):
        """Test Manager initialization with custom parameters."""
        # Act
        manager = Manager(
            widget_list=mock_widget_list, browser=mock_browser, port=1234, log_level=10
        )

        # Assert
        assert manager.port == 1234
        assert manager.log_level == 10

    def test_load_experiment(self, manager, mock_experiment):
        """Test loading an experiment in Manager."""
        # Act
        manager.load(mock_experiment)

        # Assert
        assert mock_experiment in manager.experiments
        manager.browser.add.assert_called_once_with(mock_experiment)

    def test_load_experiment_with_curves(self, manager, mock_experiment):
        """Test loading an experiment with curves in Manager."""
        # Arrange
        curve1 = mock.MagicMock()
        curve1.wdg = mock.MagicMock()
        mock_experiment.curve_list = [curve1, None]

        # Act
        manager.load(mock_experiment)

        # Assert
        curve1.wdg.load.assert_called_once_with(curve1)

    def test_remove_experiment(self, manager, mock_experiment):
        """Test removing an experiment in Manager."""
        # Arrange
        manager.experiments.append(mock_experiment)
        browser_index = 5
        manager.browser.indexOfTopLevelItem.return_value = browser_index

        # Act
        manager.remove(mock_experiment)

        # Assert
        assert mock_experiment not in manager.experiments
        manager.browser.takeTopLevelItem.assert_called_once_with(browser_index)

    def test_remove_experiment_with_curves(self, manager, mock_experiment):
        """Test removing an experiment with curves in Manager."""
        # Arrange
        curve1 = mock.MagicMock()
        curve1.wdg = mock.MagicMock()
        mock_experiment.curve_list = [curve1, None]
        manager.experiments.append(mock_experiment)

        # Act
        manager.remove(mock_experiment)

        # Assert
        curve1.wdg.remove.assert_called_once_with(curve1)

    def test_finish_experiment(self, manager, mock_experiment, qtbot):
        """Test finishing an experiment in Manager."""
        # Arrange
        manager._running_experiment = mock_experiment
        manager._worker = mock.MagicMock()
        manager._monitor = mock.MagicMock()

        # Mock the clean_up method and next method to avoid conflicts
        with mock.patch.object(manager, "_clean_up"):
            with mock.patch.object(manager, "next"):
                # Act & Assert
                with qtbot.waitSignal(manager.finished, timeout=1000):
                    manager._finish()

                # Additional assertions
                mock_experiment.browser_item.setProgress.assert_called_once_with(100)

    def test_finish_experiment_with_curves(self, manager, mock_experiment, qtbot):
        """Test finishing an experiment with curves in Manager."""
        # Arrange
        manager._running_experiment = mock_experiment
        manager._worker = mock.MagicMock()
        manager._monitor = mock.MagicMock()

        curve1 = mock.MagicMock()
        curve1.wdg = mock.MagicMock()
        mock_experiment.curve_list = [curve1, None]

        # Mock the clean_up method and next method to avoid conflicts
        with mock.patch.object(manager, "_clean_up"):
            with mock.patch.object(manager, "next"):
                # Act & Assert
                with qtbot.waitSignal(manager.finished, timeout=1000):
                    manager._finish()

                # Additional assertions
                mock_experiment.browser_item.setProgress.assert_called_once_with(100)
                curve1.wdg.remove.assert_not_called()  # Should not call remove on curves
                curve1.update_data.assert_called_once()
