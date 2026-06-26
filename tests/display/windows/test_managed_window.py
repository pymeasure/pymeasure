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

import logging
import os
from unittest import mock

import pytest

from pymeasure.display.Qt import QtCore, QtWidgets
from pymeasure.display.widgets import PlotWidget, LogWidget, ResultsDialog
from pymeasure.display.widgets.inputs_widget import InputsWidget
from pymeasure.display.widgets.fileinput_widget import FileInputWidget
from pymeasure.display.windows.managed_window import ManagedWindowBase, ManagedWindow
from pymeasure.experiment import Procedure
from pymeasure.experiment.results import Results


def _make_window(qtbot, procedure_class, **kwargs):
    kwargs.setdefault("x_axis", "Voltage (V)")
    kwargs.setdefault("y_axis", "Iterations")
    window = ManagedWindow(procedure_class, **kwargs)
    qtbot.addWidget(window)
    return window


def _make_base_window(qtbot, procedure_class, widget_list=(), **kwargs):
    window = ManagedWindowBase(procedure_class, widget_list=widget_list, **kwargs)
    qtbot.addWidget(window)
    return window


# ---------------------------------------------------------------------------
# ManagedWindowBase.__init__
# ---------------------------------------------------------------------------


def test_init_stores_procedure_class(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    assert window.procedure_class is procedure_class


def test_init_validates_data_columns(qtbot, procedure_class):
    """DATA_COLUMNS are parsed via Procedure.parse_columns; invalid unit raises."""
    bad_procedure_class = type(
        "BadProcedure",
        (Procedure,),
        {
            "DATA_COLUMNS": ["Voltage (not_a_real_unit_xyz)"],
            "startup": lambda self: None,
            "execute": lambda self: None,
            "shutdown": lambda self: None,
        },
    )
    # ManagedWindowBase (without PlotWidget) validates DATA_COLUMNS in __init__
    with pytest.raises(ValueError):
        ManagedWindowBase(bad_procedure_class)


def test_init_use_estimator_false_when_not_overridden(qtbot, procedure_class):
    """use_estimator is False when get_estimates is not overridden."""
    window = _make_window(qtbot, procedure_class)
    assert window.use_estimator is False


def test_init_use_estimator_true_when_overridden(qtbot, procedure_class):
    """use_estimator is True when get_estimates is overridden."""
    class WithEstimates(procedure_class):
        def get_estimates(self):
            return [("estimate", "value")]

    window = _make_window(qtbot, WithEstimates)
    assert window.use_estimator is True
    assert hasattr(window, "estimator")


def test_init_sets_up_queue_and_abort_buttons(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    assert window.queue_button.text() == "Queue"
    assert window.abort_button.text() == "Abort"
    assert window.abort_button.isEnabled() is False


def test_init_sets_up_browser_widget(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    assert window.browser is window.browser_widget.browser
    # context menu policy is set to CustomContextMenu
    assert (window.browser.contextMenuPolicy()
            == QtCore.Qt.ContextMenuPolicy.CustomContextMenu)


def test_init_inputs_widget_replaces_input_list(qtbot, procedure_class):
    """After _setup_ui, self.inputs is an InputsWidget (not the original tuple)."""
    window = _make_window(qtbot, procedure_class, inputs=("voltage", "iterations"))
    assert isinstance(window.inputs, InputsWidget)


def test_init_file_input_widget_present_when_enabled(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    assert isinstance(window.file_input, FileInputWidget)
    assert window.enable_file_input is True


def test_init_file_input_widget_absent_when_disabled(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class, enable_file_input=False)
    assert window.enable_file_input is False
    assert not hasattr(window, "file_input")


def test_init_manager_created(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    assert window.manager is not None
    # manager has the widget_list and browser wired
    assert window.manager.browser is window.browser


def test_init_sequencer_not_present_by_default(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    assert window.use_sequencer is False
    assert not hasattr(window, "sequencer")


def test_init_sequencer_present_when_requested(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class, sequencer=True)
    assert window.use_sequencer is True
    assert hasattr(window, "sequencer")


def test_init_layout_creates_tab_widget(qtbot, procedure_class):
    """_layout builds the central tab widget with the provided widget_list."""
    log_widget = LogWidget("Experiment Log")
    plot_widget = PlotWidget(
        "Graph", procedure_class.DATA_COLUMNS, "Voltage (V)", "Iterations"
    )
    window = _make_base_window(
        qtbot, procedure_class, widget_list=(log_widget, plot_widget)
    )
    assert isinstance(window.tabs, QtWidgets.QTabWidget)
    tab_texts = [window.tabs.tabText(i) for i in range(window.tabs.count())]
    assert "Experiment Log" in tab_texts
    assert "Graph" in tab_texts


# ---------------------------------------------------------------------------
# queue / experiment management
# ---------------------------------------------------------------------------


def test_queue_uses_inputs_when_no_procedure(qtbot, procedure_class, tmp_path):
    window = _make_window(qtbot, procedure_class)
    window.directory = str(tmp_path)
    with mock.patch.object(window.manager, "queue") as mock_queue, \
         mock.patch.object(window.manager, "is_running", return_value=False):
        window.queue()
    mock_queue.assert_called_once()
    experiment = mock_queue.call_args.args[0]
    assert isinstance(experiment.results, Results)
    assert experiment.results.procedure.__class__ is procedure_class


def test_queue_with_procedure_uses_provided_procedure(qtbot, procedure_class, tmp_path):
    window = _make_window(qtbot, procedure_class)
    window.directory = str(tmp_path)
    procedure = procedure_class()
    procedure.iterations = 42
    with mock.patch.object(window.manager, "queue") as mock_queue:
        window.queue(procedure=procedure)
    mock_queue.assert_called_once()
    experiment = mock_queue.call_args.args[0]
    assert experiment.procedure is procedure


def test_queue_with_invalid_filename_logs_and_returns(qtbot, procedure_class, tmp_path):
    """An invalid placeholder in the filename is logged and the queue is not called."""
    window = _make_window(qtbot, procedure_class)
    window.directory = str(tmp_path)
    window.filename = "{nonexistent_placeholder}"
    with mock.patch.object(window.manager, "queue") as mock_queue:
        window.queue()
    mock_queue.assert_not_called()


def test_queue_temp_file_when_not_storing(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    window.store_measurement = False
    with mock.patch.object(window.manager, "queue") as mock_queue:
        window.queue()
    mock_queue.assert_called_once()
    experiment = mock_queue.call_args.args[0]
    assert "TempFile_" in experiment.results.data_filename


def test_queue_raises_not_implemented_when_file_input_disabled(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class, enable_file_input=False)
    with pytest.raises(NotImplementedError):
        window.queue()


def test_make_procedure_returns_procedure_instance(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class, inputs=("voltage", "iterations"))
    procedure = window.make_procedure()
    assert isinstance(procedure, procedure_class)


def test_make_procedure_raises_without_inputs_widget(qtbot, procedure_class):
    window = _make_base_window(qtbot, procedure_class, widget_list=())
    # Set inputs to a non-InputsWidget value to exercise the error path
    window.inputs = "not a widget"
    with pytest.raises(Exception):
        window.make_procedure()


def test_new_curve_uses_widget_new_curve(qtbot, procedure_class, results_factory):
    window = _make_window(qtbot, procedure_class)
    results = results_factory()
    curve = window.new_curve(window.plot_widget, results)
    assert curve is not None
    assert curve.results is results


def test_new_curve_default_color_cycled(qtbot, procedure_class, results_factory):
    window = _make_window(qtbot, procedure_class)
    results = results_factory()
    curve = window.new_curve(window.plot_widget, results, color=None)
    assert curve.color is not None


def test_new_experiment_creates_experiment_with_curve_list(qtbot, procedure_class,
                                                            results_factory):
    window = _make_window(qtbot, procedure_class)
    results = results_factory()
    experiment = window.new_experiment(results)
    assert experiment.results is results
    assert experiment.procedure is results.procedure
    # widget_list has plot_widget + log_widget -> at least one curve in list
    assert isinstance(experiment.curve_list, list)
    assert experiment.browser_item is not None


def test_new_experiment_uses_provided_curves(qtbot, procedure_class, results_factory):
    window = _make_window(qtbot, procedure_class)
    results = results_factory()
    provided_curve = mock.MagicMock()
    # curve.color must be a valid QColor (used to fill the BrowserItem pixmap)
    from pymeasure.display.Qt import QtGui
    provided_curve.color = QtGui.QColor("blue")
    experiment = window.new_experiment(results, curve=[provided_curve])
    assert experiment.curve_list == [provided_curve]


def test_remove_experiment_calls_manager_remove(qtbot, procedure_class, results_factory):
    window = _make_window(qtbot, procedure_class)
    results = results_factory()
    experiment = window.new_experiment(results)
    with mock.patch.object(window.manager, "remove") as mock_remove, \
         mock.patch("pymeasure.display.windows.managed_window.QtWidgets.QMessageBox.question",
                    return_value=QtWidgets.QMessageBox.StandardButton.Yes):
        window.remove_experiment(experiment)
    mock_remove.assert_called_once_with(experiment)


def test_remove_experiment_list_uses_plural_message(qtbot, procedure_class, results_factory):
    window = _make_window(qtbot, procedure_class)
    results = results_factory()
    exp1 = window.new_experiment(results)
    exp2 = window.new_experiment(results_factory())
    with mock.patch.object(window.manager, "remove") as mock_remove, \
         mock.patch("pymeasure.display.windows.managed_window.QtWidgets.QMessageBox.question",
                    return_value=QtWidgets.QMessageBox.StandardButton.No) as mock_question:
        window.remove_experiment([exp1, exp2])
    # User answered No: nothing removed
    mock_remove.assert_not_called()
    # The message contains the count
    call_args = mock_question.call_args
    assert "2" in call_args.args[2]


def test_delete_experiment_data_removes_file(qtbot, procedure_class, tmp_path):
    window = _make_window(qtbot, procedure_class)
    # Create an experiment with an actual data file on disk
    data_file = tmp_path / "data_to_delete.csv"
    data_file.write_text("some,data\n")
    results = Results(procedure_class(), str(data_file))
    experiment = window.new_experiment(results)
    assert os.path.exists(str(data_file))

    with mock.patch.object(window.manager, "remove") as mock_remove, \
         mock.patch("pymeasure.display.windows.managed_window.QtWidgets.QMessageBox.question",
                    return_value=QtWidgets.QMessageBox.StandardButton.Yes):
        window.delete_experiment_data(experiment)
    mock_remove.assert_called_once_with(experiment)
    assert not os.path.exists(str(data_file))


def test_delete_experiment_data_user_cancels(qtbot, procedure_class, tmp_path):
    window = _make_window(qtbot, procedure_class)
    data_file = tmp_path / "kept.csv"
    data_file.write_text("kept\n")
    results = Results(procedure_class(), str(data_file))
    experiment = window.new_experiment(results)

    with mock.patch.object(window.manager, "remove") as mock_remove, \
         mock.patch("pymeasure.display.windows.managed_window.QtWidgets.QMessageBox.question",
                    return_value=QtWidgets.QMessageBox.StandardButton.No):
        window.delete_experiment_data(experiment)
    mock_remove.assert_not_called()
    assert os.path.exists(str(data_file))


def test_clear_experiments_calls_manager_clear(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    with mock.patch.object(window.manager, "clear") as mock_clear:
        window.clear_experiments()
    mock_clear.assert_called_once()


def test_open_experiment_loads_results(qtbot, procedure_class, tmp_path):
    """open_experiment loads a results file when the dialog accepts."""
    window = _make_window(qtbot, procedure_class)
    # Create a results file backed by an actual procedure
    procedure = procedure_class()
    procedure.iterations = 7
    data_file = tmp_path / "open_exp.csv"
    expected_results = Results(procedure, str(data_file))
    assert os.path.exists(str(data_file))

    dialog = mock.MagicMock(spec=ResultsDialog)
    dialog.exec.return_value = True
    dialog.selectedFiles.return_value = [str(data_file)]
    # Results.load (without procedure_class) cannot rediscover the local test procedure,
    # so mock it to return the Results object built with the correct procedure_class.
    with mock.patch(
        "pymeasure.display.windows.managed_window.ResultsDialog", return_value=dialog
    ), mock.patch.object(window.manager, "load") as mock_load, \
         mock.patch("pymeasure.display.windows.managed_window.Results.load",
                    return_value=expected_results):
        window.open_experiment()
    mock_load.assert_called_once()
    experiment = mock_load.call_args.args[0]
    assert experiment.results.data_filename == str(data_file)


def test_open_experiment_warns_on_duplicate(qtbot, procedure_class, tmp_path):
    """If the file is already loaded, a warning is shown and not re-loaded."""
    window = _make_window(qtbot, procedure_class)
    data_file = tmp_path / "dup.csv"
    # Results writes the file header on construction
    results = Results(procedure_class(), str(data_file))
    assert os.path.exists(str(data_file))

    # Pretend the experiment is already in the queue: __contains__ matches basename
    window.manager.experiments.queue.append(window.new_experiment(results))
    assert str(data_file) in window.manager.experiments

    dialog = mock.MagicMock(spec=ResultsDialog)
    dialog.exec.return_value = True
    dialog.selectedFiles.return_value = [str(data_file)]
    with mock.patch(
        "pymeasure.display.windows.managed_window.ResultsDialog", return_value=dialog
    ), mock.patch.object(window.manager, "load") as mock_load, \
         mock.patch("pymeasure.display.windows.managed_window.QtWidgets.QMessageBox.warning") \
            as mock_warning:
        window.open_experiment()
    mock_load.assert_not_called()
    mock_warning.assert_called_once()


def test_open_experiment_dialog_cancelled(qtbot, procedure_class):
    """When the dialog is cancelled, nothing is loaded."""
    window = _make_window(qtbot, procedure_class)
    dialog = mock.MagicMock(spec=ResultsDialog)
    dialog.exec.return_value = False
    with mock.patch(
        "pymeasure.display.windows.managed_window.ResultsDialog", return_value=dialog
    ), mock.patch.object(window.manager, "load") as mock_load:
        window.open_experiment()
    mock_load.assert_not_called()


def test_save_experiment_copy_copies_file(qtbot, procedure_class, tmp_path):
    window = _make_window(qtbot, procedure_class)
    source = tmp_path / "source.csv"
    source.write_text("a,b\n1,2\n")
    destination = tmp_path / "destination.csv"

    dialog = mock.MagicMock(spec=QtWidgets.QFileDialog)
    dialog.exec.return_value = True
    dialog.selectedFiles.return_value = [str(destination)]
    with mock.patch("pymeasure.display.windows.managed_window.QtWidgets.QFileDialog",
                    return_value=dialog):
        window.save_experiment_copy(str(source))
    assert destination.exists()
    assert destination.read_text() == "a,b\n1,2\n"


def test_save_experiment_copy_dialog_cancelled(qtbot, procedure_class, tmp_path):
    window = _make_window(qtbot, procedure_class)
    source = tmp_path / "src.csv"
    source.write_text("data")
    destination = tmp_path / "dest.csv"

    dialog = mock.MagicMock(spec=QtWidgets.QFileDialog)
    dialog.exec.return_value = False
    with mock.patch("pymeasure.display.windows.managed_window.QtWidgets.QFileDialog",
                    return_value=dialog):
        window.save_experiment_copy(str(source))
    assert not destination.exists()


# ---------------------------------------------------------------------------
# browser callbacks
# ---------------------------------------------------------------------------


def _load_experiment_into_browser(window, results):
    """Manually add an experiment to the manager + browser, like Manager.load would."""
    experiment = window.new_experiment(results)
    window.manager.experiments.append(experiment)
    window.browser.add(experiment)
    return experiment


def test_browser_item_changed_unchecked_removes_curves(qtbot, procedure_class,
                                                         results_factory):
    window = _make_window(qtbot, procedure_class)
    experiment = _load_experiment_into_browser(window, results_factory())
    item = experiment.browser_item

    wdg_mock = mock.MagicMock()
    curve_mock = mock.MagicMock()
    curve_mock.wdg = wdg_mock
    experiment.curve_list = [curve_mock]

    # Disconnect the automatic signal to control the test flow precisely
    window.browser.itemChanged.disconnect()
    item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
    window.browser_item_changed(item, 0)
    wdg_mock.remove.assert_called_once_with(curve_mock)


def test_browser_item_changed_checked_loads_curves(qtbot, procedure_class, results_factory):
    window = _make_window(qtbot, procedure_class)
    experiment = _load_experiment_into_browser(window, results_factory())
    item = experiment.browser_item

    wdg_mock = mock.MagicMock()
    curve_mock = mock.MagicMock()
    curve_mock.wdg = wdg_mock
    experiment.curve_list = [curve_mock]

    window.browser.itemChanged.disconnect()
    item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
    item.setCheckState(0, QtCore.Qt.CheckState.Checked)
    window.browser_item_changed(item, 0)
    wdg_mock.load.assert_called_once_with(curve_mock)


def test_browser_item_menu_builds_actions(qtbot, procedure_class, results_factory):
    window = _make_window(qtbot, procedure_class)
    experiment = _load_experiment_into_browser(window, results_factory())
    # Position the menu at the top-left item
    pos = QtCore.QPoint(0, 0)
    item_at = window.browser.itemAt(pos)
    if item_at is None:
        # Force-select the experiment item so itemAt returns it
        window.browser.setCurrentItem(experiment.browser_item)
        with mock.patch.object(window.browser, "itemAt", return_value=experiment.browser_item):
            with mock.patch.object(QtWidgets.QMenu, "exec") as mock_exec:
                window.browser_item_menu(pos)
    else:
        with mock.patch.object(QtWidgets.QMenu, "exec") as mock_exec:
            window.browser_item_menu(pos)
    assert mock_exec.called


def test_change_color_applies_to_curves(qtbot, procedure_class, results_factory):
    from pymeasure.display.Qt import QtGui
    window = _make_window(qtbot, procedure_class)
    results = results_factory()
    experiment = window.new_experiment(results)
    curve_mock = mock.MagicMock()
    curve_mock.color = None
    experiment.curve_list = [curve_mock]

    color = QtGui.QColor(QtCore.Qt.GlobalColor.red)
    with mock.patch("pymeasure.display.windows.managed_window.QtWidgets.QColorDialog.getColor",
                    return_value=color):
        window.change_color(experiment)
    curve_mock.wdg.set_color.assert_called_once()


def test_open_file_externally_calls_subprocess(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    with mock.patch("pymeasure.display.windows.managed_window.platform.system",
                    return_value="Linux"), \
         mock.patch("pymeasure.display.windows.managed_window.subprocess.Popen") as mock_popen:
        window.open_file_externally("/some/file.csv")
    mock_popen.assert_called_once()
    assert mock_popen.call_args.args[0][0] == "xdg-open"


def test_open_file_externally_unsupported_os(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    with mock.patch("pymeasure.display.windows.managed_window.platform.system",
                    return_value="UnknownOS"):
        with pytest.raises(Exception):
            window.open_file_externally("/some/file.csv")


def test_reveal_in_file_explorer_calls_subprocess(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    with mock.patch("pymeasure.display.windows.managed_window.platform.system",
                    return_value="Linux"), \
         mock.patch("pymeasure.display.windows.managed_window.subprocess.Popen") as mock_popen:
        window.reveal_in_file_explorer("/some/dir/file.csv")
    mock_popen.assert_called_once()
    # On Linux, the dirname is opened
    assert mock_popen.call_args.args[0][0] == "xdg-open"


def test_reveal_in_file_explorer_unsupported_os(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    with mock.patch("pymeasure.display.windows.managed_window.platform.system",
                    return_value="UnknownOS"):
        with pytest.raises(Exception):
            window.reveal_in_file_explorer("/some/file.csv")


# ---------------------------------------------------------------------------
# lifecycle: quit, abort, resume, queued, running, finished, abort_returned
# ---------------------------------------------------------------------------


def test_quit_closes_window_when_not_running(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    with mock.patch.object(window, "close") as mock_close, \
         mock.patch.object(window.manager, "is_running", return_value=False):
        window.quit()
    mock_close.assert_called_once()


def test_quit_aborts_then_closes_when_running(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    with mock.patch.object(window, "abort") as mock_abort, \
         mock.patch.object(window, "close") as mock_close, \
         mock.patch.object(window.manager, "is_running", return_value=True):
        window.quit()
    mock_abort.assert_called_once()
    mock_close.assert_called_once()


def test_abort_calls_manager_abort_and_changes_button(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    with mock.patch.object(window.manager, "abort") as mock_abort:
        window.abort()
    mock_abort.assert_called_once()
    # Button text changes to "Resume"
    assert window.abort_button.text() == "Resume"


def test_abort_handles_manager_failure_gracefully(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    with mock.patch.object(window.manager, "abort", side_effect=RuntimeError("nope")):
        window.abort()
    # On failure, the button reverts to "Abort"
    assert window.abort_button.text() == "Abort"


def test_resume_calls_manager_resume_when_has_next(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    # First put the abort_button into "Resume" mode (mirroring abort)
    with mock.patch.object(window.manager, "abort"):
        window.abort()
    with mock.patch.object(window.manager, "experiments") as experiments_mock, \
         mock.patch.object(window.manager, "resume") as mock_resume:
        experiments_mock.has_next.return_value = True
        window.resume()
    mock_resume.assert_called_once()
    assert window.abort_button.text() == "Abort"


def test_resume_disables_button_when_no_next(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    with mock.patch.object(window.manager, "abort"):
        window.abort()
    with mock.patch.object(window.manager, "experiments") as experiments_mock, \
         mock.patch.object(window.manager, "resume") as mock_resume:
        experiments_mock.has_next.return_value = False
        window.resume()
    mock_resume.assert_not_called()
    assert window.abort_button.isEnabled() is False


def test_queued_enables_buttons(qtbot, procedure_class, results_factory):
    window = _make_window(qtbot, procedure_class)
    # Initially disabled
    assert window.abort_button.isEnabled() is False
    assert window.browser_widget.show_button.isEnabled() is False
    window.queued(results_factory())
    assert window.abort_button.isEnabled() is True
    assert window.browser_widget.show_button.isEnabled() is True
    assert window.browser_widget.hide_button.isEnabled() is True
    assert window.browser_widget.clear_button.isEnabled() is True


def test_running_disables_clear_button(qtbot, procedure_class, results_factory):
    window = _make_window(qtbot, procedure_class)
    window.browser_widget.clear_button.setEnabled(True)
    window.running(results_factory())
    assert window.browser_widget.clear_button.isEnabled() is False


def test_finished_disables_abort_when_no_next(qtbot, procedure_class, results_factory):
    window = _make_window(qtbot, procedure_class)
    window.abort_button.setEnabled(True)
    with mock.patch.object(window.manager.experiments, "has_next", return_value=False):
        window.finished(results_factory())
    assert window.abort_button.isEnabled() is False
    assert window.browser_widget.clear_button.isEnabled() is True


def test_finished_keeps_abort_enabled_when_has_next(qtbot, procedure_class, results_factory):
    window = _make_window(qtbot, procedure_class)
    window.abort_button.setEnabled(True)
    with mock.patch.object(window.manager.experiments, "has_next", return_value=True):
        window.finished(results_factory())
    assert window.abort_button.isEnabled() is True


def test_abort_returned_enables_resume_when_has_next(qtbot, procedure_class,
                                                      results_factory):
    window = _make_window(qtbot, procedure_class)
    with mock.patch.object(window.manager.experiments, "has_next", return_value=True):
        window.abort_returned(results_factory())
    assert window.abort_button.text() == "Resume"
    assert window.abort_button.isEnabled() is True


def test_abort_returned_enables_clear_when_no_next(qtbot, procedure_class,
                                                    results_factory):
    window = _make_window(qtbot, procedure_class)
    with mock.patch.object(window.manager.experiments, "has_next", return_value=False):
        window.abort_returned(results_factory())
    assert window.browser_widget.clear_button.isEnabled() is True


# ---------------------------------------------------------------------------
# properties: directory, filename, store_measurement
# ---------------------------------------------------------------------------


def test_directory_getter_returns_file_input_directory(qtbot, procedure_class, tmp_path):
    window = _make_window(qtbot, procedure_class)
    window.directory = str(tmp_path)
    assert window.directory == str(tmp_path)


def test_directory_setter_updates_file_input(qtbot, procedure_class, tmp_path):
    window = _make_window(qtbot, procedure_class)
    window.directory = str(tmp_path)
    assert window.file_input.directory == str(tmp_path)


def test_filename_getter_returns_file_input_filename(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    window.filename = "my_data.csv"
    assert window.filename == "my_data.csv"


def test_filename_setter_updates_file_input(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    window.filename = "experiment.csv"
    assert window.file_input.filename == "experiment.csv"


def test_store_measurement_getter(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    assert window.store_measurement is True


def test_store_measurement_setter(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class)
    window.store_measurement = False
    assert window.store_measurement is False
    assert window.file_input.store_measurement is False


def test_directory_raises_when_file_input_disabled(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class, enable_file_input=False)
    with pytest.raises(AttributeError):
        _ = window.directory


def test_directory_setter_raises_when_file_input_disabled(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class, enable_file_input=False)
    with pytest.raises(AttributeError):
        window.directory = "/tmp"


def test_filename_raises_when_file_input_disabled(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class, enable_file_input=False)
    with pytest.raises(AttributeError):
        _ = window.filename


def test_store_measurement_raises_when_file_input_disabled(qtbot, procedure_class):
    window = _make_window(qtbot, procedure_class, enable_file_input=False)
    with pytest.raises(AttributeError):
        _ = window.store_measurement


# ---------------------------------------------------------------------------
# ManagedWindow subclass
# ---------------------------------------------------------------------------


def test_managed_window_init_with_axes_and_linewidth(qtbot, procedure_class):
    window = ManagedWindow(
        procedure_class, x_axis="Voltage (V)", y_axis="Iterations", linewidth=3,
    )
    qtbot.addWidget(window)
    assert window.x_axis == "Voltage (V)"
    assert window.y_axis == "Iterations"
    assert window.plot_widget.linewidth == 3


def test_managed_window_builds_plot_widget_in_widget_list(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Iterations"
    )
    assert isinstance(window.plot_widget, PlotWidget)
    assert window.plot_widget in window.widget_list
    assert isinstance(window.log_widget, LogWidget)
    assert window.log_widget in window.widget_list


def test_managed_window_measured_quantities_updated(qtbot, procedure_class):
    window = _make_window(
        qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Iterations"
    )
    measured = window.browser_widget.browser.measured_quantities
    assert "Voltage (V)" in measured
    assert "Iterations" in measured


def test_managed_window_extra_widget_list_extended(qtbot, procedure_class):
    """A user-provided widget_list is prepended to the plot/log widgets."""
    extra = LogWidget("Extra Log")
    window = ManagedWindow(
        procedure_class,
        x_axis="Voltage (V)", y_axis="Iterations",
        widget_list=(extra,),
    )
    qtbot.addWidget(window)
    assert extra in window.widget_list
    assert window.plot_widget in window.widget_list
    assert window.log_widget in window.widget_list
    # widget_list order: user widgets first, then plot, then log
    assert window.widget_list[0] is extra


def test_managed_window_logging_handler_attached(qtbot, procedure_class):
    """ManagedWindow attaches the log_widget handler to the root logger."""
    root_logger = logging.getLogger()
    window = _make_window(
        qtbot, procedure_class, x_axis="Voltage (V)", y_axis="Iterations"
    )
    assert window.log_widget.handler in root_logger.handlers
