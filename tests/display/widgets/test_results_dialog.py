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

import pytest

from pymeasure.display.Qt import QtWidgets
from pymeasure.display.widgets import ResultsDialog
from pymeasure.experiment import Parameter, Procedure
from pymeasure.experiment.results import Results


class _DummyProcedure(Procedure):
    """A procedure with two parameters, used for the results dialog tests.

    Defined at module level so that ``Results.load`` can resolve the
    ``Procedure`` class from the stored module path in the file header.
    """

    x = Parameter("X", default="value")
    y = Parameter("Y", default="other")

    DATA_COLUMNS = ["x", "y"]


def _make_results_file(path):
    """Create a results file (header plus a single data row) at ``path``."""
    procedure = _DummyProcedure()
    Results(procedure, str(path))
    # Results writes only the header/labels; append a data row so that
    # ``Results.reload`` (called from ``Results.load``) can parse the file.
    with open(path, "a", encoding=Results.ENCODING) as f:
        f.write("value,other\n")
    return str(path)


def test_init_configures_existing_files_mode(qtbot):
    """ResultsDialog should be configured to select existing files (load mode)."""
    dialog = ResultsDialog(_DummyProcedure)
    qtbot.addWidget(dialog)

    assert (dialog.fileMode()
            == QtWidgets.QFileDialog.FileMode.ExistingFiles)
    assert dialog.testOption(
        QtWidgets.QFileDialog.Option.DontUseNativeDialog)


def test_init_accepts_widget_list(qtbot):
    """An empty widget_list should produce an empty preview_widget_list."""
    dialog = ResultsDialog(_DummyProcedure, widget_list=())
    qtbot.addWidget(dialog)

    assert dialog.preview_widget_list == []


@pytest.mark.parametrize("extension", [".csv", ".txt"])
def test_update_preview_loads_file_contents(qtbot, tmp_path, extension):
    """`update_preview` should load the selected file and populate the parameter
    preview tree regardless of the file extension."""
    data_file = tmp_path / f"data{extension}"
    _make_results_file(data_file)

    dialog = ResultsDialog(_DummyProcedure)
    qtbot.addWidget(dialog)

    dialog.update_preview(str(data_file))

    names = [dialog.preview_param.topLevelItem(i).text(0)
             for i in range(dialog.preview_param.topLevelItemCount())]
    assert "X" in names
    assert "Y" in names


@pytest.mark.parametrize("extension", [".csv", ".txt"])
def test_update_preview_ignores_empty_path(qtbot, tmp_path, extension):
    """`update_preview` should be a no-op for an empty path."""
    dialog = ResultsDialog(_DummyProcedure)
    qtbot.addWidget(dialog)

    dialog.update_preview("")

    assert dialog.preview_param.topLevelItemCount() == 0


def test_update_preview_ignores_directory(qtbot, tmp_path):
    """`update_preview` should ignore directory paths without raising."""
    dialog = ResultsDialog(_DummyProcedure)
    qtbot.addWidget(dialog)

    dialog.update_preview(str(tmp_path))

    assert dialog.preview_param.topLevelItemCount() == 0
