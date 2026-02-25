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

from pymeasure.display.browser import BaseBrowserItem, BrowserItem, Browser
from pymeasure.experiment.procedure import Procedure
from pymeasure.experiment.results import Results
from pymeasure.display.Qt import QtGui, QtCore, QtWidgets


class TestBaseBrowserItem:
    """Test cases for BaseBrowserItem class"""

    def test_status_label_mapping(self):
        """Test that status_label mapping contains all expected statuses"""
        # Assert
        assert BaseBrowserItem.status_label[Procedure.QUEUED] == "Queued"
        assert BaseBrowserItem.status_label[Procedure.RUNNING] == "Running"
        assert BaseBrowserItem.status_label[Procedure.FAILED] == "Failed"
        assert BaseBrowserItem.status_label[Procedure.ABORTED] == "Aborted"
        assert BaseBrowserItem.status_label[Procedure.FINISHED] == "Finished"

    def test_set_status_abstract_method(self):
        """Test that setStatus is an abstract method that raises NotImplementedError"""
        # Arrange
        item = BaseBrowserItem()

        # Act & Assert
        with pytest.raises(NotImplementedError, match="Must be reimplemented by subclasses"):
            item.setStatus(Procedure.QUEUED)

    def test_set_progress_abstract_method(self):
        """Test that setProgress is an abstract method that raises NotImplementedError"""
        # Arrange
        item = BaseBrowserItem()

        # Act & Assert
        with pytest.raises(NotImplementedError, match="Must be reimplemented by subclasses"):
            item.setProgress(50)


class TestBrowserItem:
    """Test cases for BrowserItem class"""

    @pytest.fixture
    def mock_results(self):
        """Create a mock Results object for testing."""
        results = mock.MagicMock(spec=Results)
        results.data_filename = "/path/to/test_data.csv"
        results.procedure = mock.MagicMock(spec=Procedure)
        results.procedure.status = Procedure.QUEUED
        return results

    # Remove the browser_item fixture and create BrowserItem instances directly in tests

    def test_browser_item_initialization(self, mock_results, qtbot):
        """Test BrowserItem initialization with experiment objects."""
        # Arrange
        color = QtGui.QColor(255, 255, 255)  # White color
        tree = QtWidgets.QTreeWidget()
        qtbot.addWidget(tree)

        # Act
        browser_item = BrowserItem(results=mock_results, color=color)
        tree.addTopLevelItem(browser_item)

        # Assert
        assert isinstance(browser_item, QtWidgets.QTreeWidgetItem)
        assert isinstance(browser_item, BaseBrowserItem)
        assert browser_item.text(1) == "test_data.csv"  # Basename of data_filename
        assert browser_item.checkState(0) == QtCore.Qt.CheckState.Checked
        # Status is displayed in column 3, initially set to 'Queued'
        assert browser_item.text(3) == "Queued"

    def test_browser_item_icon_creation(self, mock_results, qtbot):
        """Test that BrowserItem creates icon with correct color."""
        # Arrange
        color = QtGui.QColor(255, 255, 255)  # White color
        tree = QtWidgets.QTreeWidget()
        qtbot.addWidget(tree)

        # Act
        browser_item = BrowserItem(results=mock_results, color=color)
        tree.addTopLevelItem(browser_item)
        icon = browser_item.icon(0)

        # Assert
        assert not icon.isNull()

    def test_browser_item_flags(self, mock_results, qtbot):
        """Test that BrowserItem has correct flags set."""
        # Arrange
        color = QtGui.QColor(255, 255, 255)  # White color
        tree = QtWidgets.QTreeWidget()
        qtbot.addWidget(tree)

        # Act
        browser_item = BrowserItem(results=mock_results, color=color)
        tree.addTopLevelItem(browser_item)
        flags = browser_item.flags()

        # Assert
        assert bool(flags & QtCore.Qt.ItemFlag.ItemIsUserCheckable)
        assert bool(flags & QtCore.Qt.ItemFlag.ItemIsSelectable)
        assert bool(flags & QtCore.Qt.ItemFlag.ItemIsEnabled)

    def test_set_status_updates_text(self, mock_results, qtbot):
        """Test setStatus updates status text correctly."""
        # Arrange
        color = QtGui.QColor(255, 255, 255)  # White color
        tree = QtWidgets.QTreeWidget()
        qtbot.addWidget(tree)
        browser_item = BrowserItem(results=mock_results, color=color)
        tree.addTopLevelItem(browser_item)

        # Act
        browser_item.setStatus(Procedure.RUNNING)

        # Assert
        assert browser_item.text(3) == "Running"

    def test_set_status_failed_updates_text(self, mock_results, qtbot):
        """Test setStatus with FAILED updates status text correctly."""
        # Arrange
        color = QtGui.QColor(255, 255, 255)  # White color
        tree = QtWidgets.QTreeWidget()
        qtbot.addWidget(tree)
        browser_item = BrowserItem(results=mock_results, color=color)
        tree.addTopLevelItem(browser_item)

        # Act
        browser_item.setStatus(Procedure.FAILED)

        # Assert
        assert browser_item.text(3) == "Failed"

    def test_set_status_aborted_updates_text(self, mock_results, qtbot):
        """Test setStatus with ABORTED updates status text correctly."""
        # Arrange
        color = QtGui.QColor(255, 255, 255)  # White color
        tree = QtWidgets.QTreeWidget()
        qtbot.addWidget(tree)
        browser_item = BrowserItem(results=mock_results, color=color)
        tree.addTopLevelItem(browser_item)

        # Act
        browser_item.setStatus(Procedure.ABORTED)

        # Assert
        assert browser_item.text(3) == "Aborted"

    def test_set_status_finished_updates_text(self, mock_results, qtbot):
        """Test setStatus with FINISHED updates status text correctly."""
        # Arrange
        color = QtGui.QColor(255, 255, 255)  # White color
        tree = QtWidgets.QTreeWidget()
        qtbot.addWidget(tree)
        browser_item = BrowserItem(results=mock_results, color=color)
        tree.addTopLevelItem(browser_item)

        # Act
        browser_item.setStatus(Procedure.FINISHED)

        # Assert
        assert browser_item.text(3) == "Finished"

    def test_set_progress_updates_progressbar(self, mock_results, qtbot):
        """Test setProgress updates progress bar value."""
        # Arrange
        color = QtGui.QColor(255, 255, 255)  # White color
        tree = QtWidgets.QTreeWidget()
        qtbot.addWidget(tree)
        browser_item = BrowserItem(results=mock_results, color=color)
        tree.addTopLevelItem(browser_item)

        # Act
        browser_item.setProgress(75)

        # Assert
        assert browser_item.progressbar.value() == 75

    def test_set_progress_with_float_value(self, mock_results, qtbot):
        """Test setProgress handles float values correctly."""
        # Arrange
        color = QtGui.QColor(255, 255, 255)  # White color
        tree = QtWidgets.QTreeWidget()
        qtbot.addWidget(tree)
        browser_item = BrowserItem(results=mock_results, color=color)
        tree.addTopLevelItem(browser_item)

        # Act
        browser_item.setProgress(45.5)

        # Assert
        assert browser_item.progressbar.value() == 45  # Should be converted to int

    def test_progressbar_properties(self, mock_results, qtbot):
        """Test that progressbar has correct initial properties."""
        # Arrange
        color = QtGui.QColor(255, 255, 255)  # White color
        tree = QtWidgets.QTreeWidget()
        qtbot.addWidget(tree)
        browser_item = BrowserItem(results=mock_results, color=color)
        tree.addTopLevelItem(browser_item)

        # Assert
        assert browser_item.progressbar.minimum() == 0
        assert browser_item.progressbar.maximum() == 100
        assert browser_item.progressbar.value() == 0


class TestBrowser:
    """Test cases for Browser class"""

    @pytest.fixture
    def mock_procedure_class(self):
        """Create a mock procedure class for testing."""
        procedure_class = mock.MagicMock()
        # Mock parameter objects
        param1 = mock.MagicMock()
        param1.name = "Voltage"
        param2 = mock.MagicMock()
        param2.name = "Current"

        # Set up the class attributes
        procedure_class.voltage_param = param1
        procedure_class.current_param = param2

        return procedure_class

    @pytest.fixture
    def browser(self, mock_procedure_class, qtbot):
        """Create a Browser instance for testing."""
        display_parameters = ["voltage_param", "current_param"]
        measured_quantities = ["voltage", "current"]
        browser = Browser(
            procedure_class=mock_procedure_class,
            display_parameters=display_parameters,
            measured_quantities=measured_quantities,
        )
        qtbot.addWidget(browser)
        return browser

    def test_browser_initialization(self, browser, mock_procedure_class):
        """Test Browser initialization and setup."""
        # Assert
        assert isinstance(browser, QtWidgets.QTreeWidget)
        assert browser.procedure_class == mock_procedure_class
        assert browser.display_parameters == ["voltage_param", "current_param"]
        assert browser.measured_quantities == {"voltage", "current"}
        assert browser.columnCount() == 6  # Graph, Filename, Progress, Status + 2 parameters
        assert browser.isSortingEnabled() is True

    def test_browser_header_labels(self, browser):
        """Test Browser header labels are set correctly."""
        # Act
        header_labels = [browser.headerItem().text(i) for i in range(browser.columnCount())]

        # Assert
        assert header_labels == ["Graph", "Filename", "Progress", "Status", "Voltage", "Current"]

    def test_browser_section_widths(self, browser):
        """Test Browser section widths are set correctly."""
        # Act
        width_col_0 = browser.header().sectionSize(0)
        width_col_1 = browser.header().sectionSize(1)

        # Assert
        assert width_col_0 == 80
        assert width_col_1 == 140

    def test_add_experiment_success(self, browser, qtbot):
        """Test adding an experiment to the Browser successfully."""
        # Arrange
        mock_experiment = mock.MagicMock()
        mock_experiment.procedure.DATA_COLUMNS = ["voltage", "current"]
        mock_experiment.procedure.parameter_objects.return_value = {
            "voltage_param": "5.0 V",
            "current_param": "1.0 A",
        }

        # Create a real BrowserItem instead of a mock
        mock_results = mock.MagicMock(spec=Results)
        mock_results.data_filename = "/path/to/test_data.csv"
        mock_results.procedure = mock.MagicMock(spec=Procedure)
        mock_results.procedure.status = Procedure.QUEUED
        color = QtGui.QColor(255, 255, 255)  # White color
        browser_item = BrowserItem(results=mock_results, color=color)
        # Add the item to a temporary tree widget to ensure proper initialization
        temp_tree = QtWidgets.QTreeWidget()
        qtbot.addWidget(temp_tree)
        temp_tree.addTopLevelItem(browser_item)

        mock_experiment.browser_item = browser_item

        # Act
        item = browser.add(mock_experiment)

        # Assert
        assert item == mock_experiment.browser_item

    def test_add_experiment_missing_quantity_raises_exception(self, browser):
        """Test adding an experiment missing required measured quantities raises exception."""
        # Arrange
        mock_experiment = mock.MagicMock()
        mock_experiment.procedure.DATA_COLUMNS = ["voltage"]  # Missing 'current'

        # Act & Assert
        with pytest.raises(Exception, match="Procedure does not measure the current quantity."):
            browser.add(mock_experiment)

    def test_add_experiment_sets_parameter_values(self, browser, qtbot):
        """Test that add method sets parameter values in the browser item."""
        # Arrange
        mock_experiment = mock.MagicMock()
        mock_experiment.procedure.DATA_COLUMNS = ["voltage", "current"]
        mock_parameters = {"voltage_param": mock.MagicMock(), "current_param": mock.MagicMock()}
        mock_parameters["voltage_param"].__str__ = mock.Mock(return_value="5.0 V")
        mock_parameters["current_param"].__str__ = mock.Mock(return_value="1.0 A")

        mock_experiment.procedure.parameter_objects.return_value = mock_parameters

        # Create a real BrowserItem instead of a mock
        mock_results = mock.MagicMock(spec=Results)
        mock_results.data_filename = "/path/to/test_data.csv"
        mock_results.procedure = mock.MagicMock(spec=Procedure)
        mock_results.procedure.status = Procedure.QUEUED
        color = QtGui.QColor(255, 255, 255)  # White color
        browser_item = BrowserItem(results=mock_results, color=color)
        # Add the item to a temporary tree widget to ensure proper initialization
        temp_tree = QtWidgets.QTreeWidget()
        qtbot.addWidget(temp_tree)
        temp_tree.addTopLevelItem(browser_item)

        mock_experiment.browser_item = browser_item

        # Act
        item = browser.add(mock_experiment)

        # Assert
        # Check that text was set for parameter columns (index 4 and 5)
        assert item.text(4) == "5.0 V"  # voltage_param
        assert item.text(5) == "1.0 A"  # current_param

    def test_add_experiment_with_unimplemented_parameter(self, browser, qtbot):
        """Test adding experiment with parameter not implemented in procedure."""
        # Arrange
        mock_experiment = mock.MagicMock()
        mock_experiment.procedure.DATA_COLUMNS = ["voltage", "current"]
        # Return empty dict to simulate parameter not implemented
        mock_experiment.procedure.parameter_objects.return_value = {}

        # Create a real BrowserItem instead of a mock
        mock_results = mock.MagicMock(spec=Results)
        mock_results.data_filename = "/path/to/test_data.csv"
        mock_results.procedure = mock.MagicMock(spec=Procedure)
        mock_results.procedure.status = Procedure.QUEUED
        color = QtGui.QColor(255, 255, 255)  # White color
        browser_item = BrowserItem(results=mock_results, color=color)
        # Add the item to a temporary tree widget to ensure proper initialization
        temp_tree = QtWidgets.QTreeWidget()
        qtbot.addWidget(temp_tree)
        temp_tree.addTopLevelItem(browser_item)

        mock_experiment.browser_item = browser_item

        # Act
        item = browser.add(mock_experiment)

        # Assert
        # Text should be empty for parameter columns since parameters don't exist
        assert item.text(4) == ""  # voltage_param column should be empty
        assert item.text(5) == ""  # current_param column should be empty

    def test_sort_by_filename_option(self, mock_procedure_class):
        """Test Browser initialization with sort_by_filename option."""
        # Act
        browser = Browser(
            procedure_class=mock_procedure_class,
            display_parameters=["voltage_param"],
            measured_quantities=["voltage"],
            sort_by_filename=True,
        )

        # Assert
        assert browser.isSortingEnabled() is True
        # Note: We can't easily verify the sort order without a full Qt application context

    def test_measured_quantities_validation(self, mock_procedure_class):
        """Test that measured_quantities are stored as a set."""
        # Act
        browser = Browser(
            procedure_class=mock_procedure_class,
            display_parameters=[],
            measured_quantities=["voltage", "current", "resistance"],
        )

        # Assert
        assert isinstance(browser.measured_quantities, set)
        assert len(browser.measured_quantities) == 3
        assert "voltage" in browser.measured_quantities
        assert "current" in browser.measured_quantities
        assert "resistance" in browser.measured_quantities
