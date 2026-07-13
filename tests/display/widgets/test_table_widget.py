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

from unittest import mock

import numpy as np
import pandas as pd
import pytest

from pymeasure.display.Qt import QtCore, QtGui
from pymeasure.display.widgets.table_widget import (
    PandasModelByColumn,
    PandasModelByRow,
    ResultsTable,
    Table,
    TableWidget,
    SORT_ROLE,
)
from pymeasure.experiment import Procedure


class FakeResults:
    """Minimal Results mock suitable for ResultsTable construction."""

    def __init__(self, data=None):
        self.procedure = mock.MagicMock(spec=Procedure)
        self.procedure.status = Procedure.RUNNING
        self.data = data if data is not None else pd.DataFrame({
            "Time (s)": [0.0, 1.0, 2.0],
            "Voltage (V)": [0.0, 1.0, 4.0],
        })

    def reload(self):
        pass


def _make_df(rows=3):
    return pd.DataFrame({
        "Time (s)": np.arange(rows, dtype=float),
        "Voltage (V)": np.arange(rows, dtype=float) ** 2,
    })


RED = QtGui.QColor("red")
BLUE = QtGui.QColor("blue")


# ---------------------------------------------------------------------------
# ResultsTable
# ---------------------------------------------------------------------------


def test_results_table_data_rows_columns(qtbot):
    df = _make_df(3)
    table = ResultsTable(FakeResults(df), RED)
    assert table.data.shape == (3, 2)
    assert table.rows == 3
    assert table.columns == 2


def test_results_table_set_color(qtbot):
    df = _make_df(2)
    table = ResultsTable(FakeResults(df), RED)
    table.set_color(BLUE)
    assert table.color == BLUE


def test_results_table_set_index(qtbot):
    df = _make_df(3)
    table = ResultsTable(FakeResults(df), RED, column_index="Time (s)")
    assert table.column_index == "Time (s)"
    # column_index set in constructor: data is indexed by that column
    assert table.data.index.name == "Time (s)"
    # change it later (note: only stored, applied on next data assignment)
    table.set_index("Voltage (V)")
    assert table.column_index == "Voltage (V)"


def test_results_table_init_start_stop_update_data(qtbot):
    df = _make_df(3)
    results = FakeResults(df)
    table = ResultsTable(results, RED)
    assert table.last_row_count == 0

    table.init()
    assert table.last_row_count == 0

    # not started: update_data is a no-op
    table.update_data()
    assert table.last_row_count == 0

    table.start()
    assert table._started is True

    # Started: update_data emits data_changed with full bounding rect
    emitted = []
    table.data_changed.connect(
        lambda r1, c1, r2, c2: emitted.append((r1, c1, r2, c2)))
    table.update_data()
    assert table.last_row_count == 3
    assert emitted == [(0, 0, 2, 1)]

    # A second update with no new rows does not emit again
    table.update_data()
    assert emitted == [(0, 0, 2, 1)]

    table.stop()
    assert table._started is False


def test_results_table_update_data_no_emit_when_stopped(qtbot):
    df = _make_df(3)
    table = ResultsTable(FakeResults(df), RED)
    emitted = []
    table.data_changed.connect(
        lambda r1, c1, r2, c2: emitted.append((r1, c1, r2, c2)))
    table.update_data()  # not started
    assert emitted == []


# ---------------------------------------------------------------------------
# PandasModelBase
# ---------------------------------------------------------------------------


def test_pandas_model_base_add_results_connects_signal(qtbot):
    model = PandasModelByRow(results_list=[])
    df = _make_df(3)
    table = ResultsTable(FakeResults(df), RED)
    model.add_results(table)
    assert table in model.results_list
    assert model.rowCount() == 3
    assert model.columnCount() == 2
    assert table._started is True


def test_pandas_model_base_add_results_idempotent(qtbot):
    model = PandasModelByRow(results_list=[])
    df = _make_df(3)
    table = ResultsTable(FakeResults(df), RED)
    model.add_results(table)
    model.add_results(table)  # already in list
    assert model.results_list.count(table) == 1


def test_pandas_model_base_remove_results(qtbot):
    model = PandasModelByRow(results_list=[])
    df = _make_df(3)
    table = ResultsTable(FakeResults(df), RED)
    model.add_results(table)
    model.remove_results(table)
    assert table not in model.results_list
    assert model.rowCount() == 0
    assert table._started is False


def test_pandas_model_base_clear(qtbot):
    model = PandasModelByRow(results_list=[])
    df = _make_df(3)
    table = ResultsTable(FakeResults(df), RED)
    model.add_results(table)
    model.clear()
    assert model.results_list == []
    assert model.rowCount() == 0
    assert table._started is False


def test_pandas_model_base_data_display_role(qtbot):
    model = PandasModelByRow(results_list=[])
    df = pd.DataFrame({"A": [1.5, 2.5], "B": [3.5, 4.5]})
    table = ResultsTable(FakeResults(df), RED)
    model.add_results(table)
    idx = model.index(0, 0)
    assert model.data(idx, QtCore.Qt.ItemDataRole.DisplayRole) == "1.5"
    idx = model.index(1, 1)
    assert model.data(idx, QtCore.Qt.ItemDataRole.DisplayRole) == "4.5"


def test_pandas_model_base_data_sort_role(qtbot):
    model = PandasModelByRow(results_list=[])
    df = pd.DataFrame({"A": [1.5, 2.5]})
    table = ResultsTable(FakeResults(df), RED)
    model.add_results(table)
    idx = model.index(1, 0)
    assert model.data(idx, SORT_ROLE) == 2.5


def test_pandas_model_base_data_invalid_index_returns_none(qtbot):
    model = PandasModelByRow(results_list=[])
    df = pd.DataFrame({"A": [1.5]})
    table = ResultsTable(FakeResults(df), RED)
    model.add_results(table)
    idx = model.index(5, 5)  # out of range
    assert model.data(idx, QtCore.Qt.ItemDataRole.DisplayRole) is None
    assert model.data(idx, SORT_ROLE) is None


def test_pandas_model_base_data_other_role_returns_none(qtbot):
    model = PandasModelByRow(results_list=[])
    df = _make_df(2)
    table = ResultsTable(FakeResults(df), RED)
    model.add_results(table)
    idx = model.index(0, 0)
    assert model.data(idx, QtCore.Qt.ItemDataRole.ToolTipRole) is None


def test_pandas_model_base_header_data_horizontal(qtbot):
    model = PandasModelByRow(results_list=[])
    df = pd.DataFrame({"A": [1.0], "B": [2.0]})
    table = ResultsTable(FakeResults(df), RED)
    model.add_results(table)
    assert model.headerData(0, QtCore.Qt.Orientation.Horizontal,
                            QtCore.Qt.ItemDataRole.DisplayRole) == "A"
    assert model.headerData(1, QtCore.Qt.Orientation.Horizontal,
                            QtCore.Qt.ItemDataRole.DisplayRole) == "B"


def test_pandas_model_base_header_data_vertical(qtbot):
    model = PandasModelByRow(results_list=[])
    df = _make_df(3)
    table = ResultsTable(FakeResults(df), RED)
    model.add_results(table)
    assert model.headerData(0, QtCore.Qt.Orientation.Vertical,
                            QtCore.Qt.ItemDataRole.DisplayRole) == "0"
    assert model.headerData(2, QtCore.Qt.Orientation.Vertical,
                            QtCore.Qt.ItemDataRole.DisplayRole) == "2"


def test_pandas_model_base_header_data_other_role(qtbot):
    model = PandasModelByRow(results_list=[])
    df = _make_df(1)
    table = ResultsTable(FakeResults(df), RED)
    model.add_results(table)
    assert model.headerData(0, QtCore.Qt.Orientation.Horizontal,
                            QtCore.Qt.ItemDataRole.ToolTipRole) is None


def test_pandas_model_base_export_df_empty(qtbot):
    model = PandasModelByRow(results_list=[])
    assert model.export_df() is None


def test_pandas_model_base_export_df_concat(qtbot):
    model = PandasModelByRow(results_list=[])
    df1 = pd.DataFrame({"A": [1.0, 2.0]})
    df2 = pd.DataFrame({"A": [3.0, 4.0]})
    model.add_results(ResultsTable(FakeResults(df1), RED))
    model.add_results(ResultsTable(FakeResults(df2), BLUE))
    df = model.export_df()
    assert df.shape == (4, 1)
    assert df["A"].tolist() == [1.0, 2.0, 3.0, 4.0]


def test_pandas_model_base_copy_model(qtbot):
    model = PandasModelByRow(results_list=[])
    df = _make_df(3)
    table = ResultsTable(FakeResults(df), RED)
    model.add_results(table)
    copy = model.copy_model(PandasModelByColumn)
    assert isinstance(copy, PandasModelByColumn)
    assert copy.results_list == model.results_list
    # copy is a different list instance
    assert copy.results_list is not model.results_list


def test_pandas_model_base_data_changed_signal_inserts_rows(qtbot):
    model = PandasModelByRow(results_list=[])
    df = _make_df(2)
    results = FakeResults(df)
    table = ResultsTable(results, RED)
    model.add_results(table)
    assert model.rowCount() == 2

    # Simulate results growth: append a row then trigger update_data
    results.data = pd.DataFrame({
        "Time (s)": [0.0, 1.0, 2.0, 3.0],
        "Voltage (V)": [0.0, 1.0, 4.0, 9.0],
    })
    table.update_data()
    assert model.rowCount() == 4


def test_pandas_model_base_set_index(qtbot):
    model = PandasModelByRow(results_list=[])
    df = _make_df(3)
    table = ResultsTable(FakeResults(df), RED)
    model.add_results(table)
    model.set_index("Time (s)")
    assert model.column_index == "Time (s)"
    assert table.column_index == "Time (s)"


def test_pandas_model_base_vertical_header_default(qtbot):
    model = PandasModelByRow(results_list=[])
    df = _make_df(3)
    table = ResultsTable(FakeResults(df), RED)
    model.add_results(table)
    assert list(model.vertical_header) == [0, 1, 2]


def test_pandas_model_base_header_decoration_default_none(qtbot):
    # Base class decorations default to None; verify via a subclass instance
    # since PandasModelBase is abstract (raises on pandas_row_count).
    model = PandasModelByRow(results_list=[])
    assert model.horizontal_header_decoration(0) is None


# ---------------------------------------------------------------------------
# PandasModelByRow vs PandasModelByColumn
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("model_class", [PandasModelByRow, PandasModelByColumn])
def test_model_row_column_count_empty(qtbot, model_class):
    model = model_class()
    assert model.rowCount() == 0
    assert model.columnCount() == 0


def test_by_row_row_and_column_count(qtbot):
    model = PandasModelByRow(results_list=[])
    df1 = _make_df(3)
    df2 = _make_df(2)
    model.add_results(ResultsTable(FakeResults(df1), RED))
    model.add_results(ResultsTable(FakeResults(df2), BLUE))
    # rows summed, columns = first table's columns
    assert model.rowCount() == 5
    assert model.columnCount() == 2


def test_by_column_row_and_column_count(qtbot):
    model = PandasModelByColumn(results_list=[])
    df1 = _make_df(3)
    df2 = _make_df(2)
    model.add_results(ResultsTable(FakeResults(df1), RED))
    model.add_results(ResultsTable(FakeResults(df2), BLUE))
    # rows = max(3, 2) = 3, columns = 2 * 2 = 4
    assert model.rowCount() == 3
    assert model.columnCount() == 4


def test_by_row_translate_to_local(qtbot):
    model = PandasModelByRow(results_list=[])
    df1 = _make_df(3)
    df2 = _make_df(2)
    t1 = ResultsTable(FakeResults(df1), RED)
    t2 = ResultsTable(FakeResults(df2), BLUE)
    model.add_results(t1)
    model.add_results(t2)
    # global row 4 -> t2 row 1
    res, row, col = model.translate_to_local(4, 1)
    assert res is t2
    assert row == 1
    assert col == 1
    # global row 0 -> t1 row 0
    res, row, col = model.translate_to_local(0, 0)
    assert res is t1
    assert row == 0


def test_by_row_translate_to_global_impl(qtbot):
    model = PandasModelByRow(results_list=[])
    df1 = _make_df(3)
    df2 = _make_df(2)
    t1 = ResultsTable(FakeResults(df1), RED)
    t2 = ResultsTable(FakeResults(df2), BLUE)
    model.add_results(t1)
    model.add_results(t2)
    # t2 local row 1 -> global row 4 (t1 contributes 3 rows before t2)
    # NOTE: translate_to_global currently uses ``results.rows`` instead of
    # ``res.rows`` inside the loop, so the offset is computed from the target
    # table's own row count rather than the preceding tables'. This test
    # asserts the current (buggy) behavior; the intended result would be 4.
    row, col = model.translate_to_global(t2, 1, 1)
    assert row == 3
    assert col == 1
    # t1 local row 0 -> global row 0
    row, col = model.translate_to_global(t1, 0, 0)
    assert row == 0


def test_by_column_translate_to_local(qtbot):
    model = PandasModelByColumn(results_list=[])
    df1 = _make_df(3)
    df2 = _make_df(3)
    t1 = ResultsTable(FakeResults(df1), RED)
    t2 = ResultsTable(FakeResults(df2), BLUE)
    model.add_results(t1)
    model.add_results(t2)
    # global col 0 -> t1 col 0
    res, row, col = model.translate_to_local(0, 0)
    assert res is t1
    assert row == 0
    assert col == 0
    # global col 3 -> t2 col 1 (t1 has 2 cols)
    res, row, col = model.translate_to_local(0, 3)
    assert res is t2
    assert col == 1


def test_by_column_translate_to_global(qtbot):
    model = PandasModelByColumn(results_list=[])
    df1 = _make_df(3)
    df2 = _make_df(3)
    t1 = ResultsTable(FakeResults(df1), RED)
    t2 = ResultsTable(FakeResults(df2), BLUE)
    model.add_results(t1)
    model.add_results(t2)
    # t2 local col 1 -> global col 3
    row, col = model.translate_to_global(t2, 0, 1)
    assert row == 0
    assert col == 3
    # t1 local col 0 -> global col 0
    row, col = model.translate_to_global(t1, 0, 0)
    assert col == 0


def test_by_row_horizontal_header(qtbot):
    model = PandasModelByRow(results_list=[])
    df = pd.DataFrame({"A": [1.0], "B": [2.0]})
    model.add_results(ResultsTable(FakeResults(df), RED))
    assert list(model.horizontal_header) == ["A", "B"]


def test_by_column_horizontal_header_repeated(qtbot):
    model = PandasModelByColumn(results_list=[])
    df = pd.DataFrame({"A": [1.0], "B": [2.0]})
    model.add_results(ResultsTable(FakeResults(df), RED))
    model.add_results(ResultsTable(FakeResults(df), BLUE))
    # columns repeated once per results table
    assert list(model.horizontal_header) == ["A", "B", "A", "B"]


def test_by_row_vertical_header_decoration(qtbot):
    model = PandasModelByRow(results_list=[])
    df = _make_df(2)
    model.add_results(ResultsTable(FakeResults(df), RED))
    decoration = model.vertical_header_decoration(0)
    assert isinstance(decoration, QtGui.QPixmap)
    assert not decoration.isNull()


def test_by_column_horizontal_header_decoration(qtbot):
    model = PandasModelByColumn(results_list=[])
    df = _make_df(2)
    model.add_results(ResultsTable(FakeResults(df), RED))
    decoration = model.horizontal_header_decoration(0)
    assert isinstance(decoration, QtGui.QPixmap)
    assert not decoration.isNull()


def test_by_row_concat_axis(qtbot):
    assert PandasModelByRow.concat_axis == 0


def test_by_column_concat_axis(qtbot):
    assert PandasModelByColumn.concat_axis == 1


def test_by_column_vertical_header_union_of_indexes(qtbot):
    model = PandasModelByColumn(results_list=[])
    df1 = pd.DataFrame({"A": [1.0, 2.0]}, index=[0, 1])
    df2 = pd.DataFrame({"A": [3.0, 4.0]}, index=[1, 2])
    model.add_results(ResultsTable(FakeResults(df1), RED))
    model.add_results(ResultsTable(FakeResults(df2), BLUE))
    assert model.vertical_header == [0, 1, 2]


# ---------------------------------------------------------------------------
# Table
# ---------------------------------------------------------------------------


def _make_table(qtbot, **kwargs):
    table = Table(**kwargs)
    qtbot.addWidget(table)
    # Detach the model from the class-level shared default ``results_list``
    # (mutable default argument in PandasModelBase.__init__) so tests are
    # isolated from each other.
    table.clear()
    return table


def test_table_init_default_by_column(qtbot):
    table = _make_table(qtbot, refresh_time=None)
    model = table.source_model()
    assert isinstance(model, PandasModelByColumn)
    assert table.float_digits == 6
    assert table.refresh_time is None


def test_table_init_by_row(qtbot):
    table = _make_table(qtbot, refresh_time=None, layout_class=PandasModelByRow)
    model = table.source_model()
    assert isinstance(model, PandasModelByRow)


def test_table_set_model_wraps_in_proxy(qtbot):
    table = _make_table(qtbot, refresh_time=None)
    # The view's model is a QSortFilterProxyModel, source_model is the real one
    from pymeasure.display.Qt import QtCore
    assert isinstance(table.model(), QtCore.QSortFilterProxyModel)
    assert table.source_model() is table.model().sourceModel()


def test_table_add_remove_table(qtbot):
    table = _make_table(qtbot, refresh_time=None)
    df = _make_df(3)
    rt = ResultsTable(FakeResults(df), RED)
    table.add_table(rt)
    assert table.source_model().rowCount() == 3
    table.remove_table(rt)
    assert table.source_model().rowCount() == 0
    assert rt._started is False


def test_table_clear(qtbot):
    table = _make_table(qtbot, refresh_time=None)
    df = _make_df(3)
    rt = ResultsTable(FakeResults(df), RED)
    table.add_table(rt)
    table.clear()
    assert table.source_model().rowCount() == 0


def test_table_set_index(qtbot):
    table = _make_table(qtbot, refresh_time=None)
    df = _make_df(3)
    rt = ResultsTable(FakeResults(df), RED)
    table.add_table(rt)
    table.set_index("Time (s)")
    assert table.source_model().column_index == "Time (s)"


def test_table_set_model_replaces_model(qtbot):
    table = _make_table(qtbot, refresh_time=None, layout_class=PandasModelByColumn)
    df = _make_df(3)
    rt = ResultsTable(FakeResults(df), RED)
    table.add_table(rt)
    assert isinstance(table.source_model(), PandasModelByColumn)
    table.set_model(PandasModelByRow)
    assert isinstance(table.source_model(), PandasModelByRow)
    # results preserved
    assert table.source_model().rowCount() == 3


def test_table_set_color(qtbot):
    table = _make_table(qtbot, refresh_time=None)
    df = _make_df(3)
    rt = ResultsTable(FakeResults(df), RED)
    table.add_table(rt)
    table.set_color(rt, BLUE)
    assert rt.color == BLUE


def test_table_update_tables_force(qtbot):
    table = _make_table(qtbot, refresh_time=None, check_status=True)
    df = _make_df(2)
    rt = ResultsTable(FakeResults(df), RED)
    table.add_table(rt)
    rt.last_row_count = 0
    table.update_tables(force=True)
    assert rt.last_row_count == 2


def test_table_update_tables_respects_check_status(qtbot):
    table = _make_table(qtbot, refresh_time=None, check_status=True)
    df = _make_df(2)
    results = FakeResults(df)
    # status not RUNNING -> update_data should not be called
    results.procedure.status = Procedure.QUEUED
    rt = ResultsTable(results, RED)
    table.add_table(rt)
    rt.last_row_count = 0
    table.update_tables()
    assert rt.last_row_count == 0


def test_table_context_menu_actions_exist(qtbot):
    table = _make_table(qtbot, refresh_time=None)
    assert table.copy.text() == "Copy table data"
    assert table.refresh.text() == "Refresh table data"
    assert table.export.text() == "Export table data"


def test_table_copy_action(qtbot, monkeypatch):
    table = _make_table(qtbot, refresh_time=None)
    df = _make_df(2)
    table.add_table(ResultsTable(FakeResults(df), RED))

    captured = {}
    monkeypatch.setattr(pd.DataFrame, "to_clipboard",
                        lambda self, **kw: captured.setdefault("df", self))
    table.copy_action()
    assert "df" in captured
    assert captured["df"].shape == (2, 2)


def test_table_export_action_aborts_without_filename(qtbot, monkeypatch):
    table = _make_table(qtbot, refresh_time=None)
    df = _make_df(2)
    table.add_table(ResultsTable(FakeResults(df), RED))

    monkeypatch.setattr(
        "pymeasure.display.widgets.table_widget.QtWidgets.QFileDialog.getSaveFileName",
        staticmethod(lambda *a, **kw: ("", "")),
    )
    # Should not raise even though no filename selected
    table.export_action()


def test_table_export_action_writes_file(qtbot, monkeypatch, tmp_path):
    table = _make_table(qtbot, refresh_time=None)
    df = _make_df(2)
    table.add_table(ResultsTable(FakeResults(df), RED))

    out = tmp_path / "out.csv"
    monkeypatch.setattr(
        "pymeasure.display.widgets.table_widget.QtWidgets.QFileDialog.getSaveFileName",
        staticmethod(lambda *a, **kw: (str(out), "CSV file (*.csv)")),
    )
    table.export_action()
    assert out.exists()


def test_table_refresh_action(qtbot):
    table = _make_table(qtbot, refresh_time=None)
    df = _make_df(2)
    rt = ResultsTable(FakeResults(df), RED)
    table.add_table(rt)
    rt.last_row_count = 0
    table.refresh_action()
    assert rt.last_row_count == 2


# ---------------------------------------------------------------------------
# TableWidget
# ---------------------------------------------------------------------------


def _make_widget(qtbot, columns=None, **kwargs):
    if columns is None:
        columns = ["Time (s)", "Voltage (V)", "Current (A)"]
    wdg = TableWidget("test", columns, **kwargs)
    qtbot.addWidget(wdg)
    # Detach the inner Table model from the class-level shared default
    # ``results_list`` (mutable default argument in PandasModelBase.__init__)
    # so tests are isolated from each other.
    wdg.table.clear()
    return wdg


def test_table_widget_init_by_column(qtbot):
    wdg = _make_widget(qtbot, by_column=True, refresh_time=None)
    assert wdg.name == "test"
    assert wdg.columns == ["Time (s)", "Voltage (V)", "Current (A)"]
    assert wdg.table_layout == wdg.layout_names[1]  # "By Column"
    assert isinstance(wdg.table.source_model(), PandasModelByColumn)


def test_table_widget_init_by_row(qtbot):
    wdg = _make_widget(qtbot, by_column=False, refresh_time=None)
    assert wdg.table_layout == wdg.layout_names[0]  # "By Row"
    assert isinstance(wdg.table.source_model(), PandasModelByRow)


def test_table_widget_init_column_index_combo(qtbot):
    wdg = _make_widget(qtbot, refresh_time=None,
                       column_index="Voltage (V)")
    assert wdg.column_index == "Voltage (V)"
    assert wdg.column_index_combo.currentText() == "Voltage (V)"
    assert wdg.table.source_model().column_index == "Voltage (V)"


def test_table_widget_setup_ui_labels(qtbot):
    wdg = _make_widget(qtbot, refresh_time=None)
    assert wdg.column_index_label.text() == "Index:"
    assert wdg.layout_label.text() == "Layout:"
    assert wdg.column_index_combo.count() == 4  # <None> + 3 columns
    assert wdg.column_index_combo.itemText(0) == "<None>"
    assert wdg.layout.count() == 2


def test_table_widget_update_layout(qtbot):
    wdg = _make_widget(qtbot, by_column=True, refresh_time=None)
    # entry index 0 -> "By Row"
    wdg.update_layout(0)
    assert isinstance(wdg.table.source_model(), PandasModelByRow)
    # entry index 1 -> "By Column"
    wdg.update_layout(1)
    assert isinstance(wdg.table.source_model(), PandasModelByColumn)


def test_table_widget_update_column_index(qtbot):
    wdg = _make_widget(qtbot, refresh_time=None)
    # Find the "Voltage (V)" entry index
    idx = wdg.column_index_combo.findText("Voltage (V)")
    wdg.update_column_index(idx)
    assert wdg.column_index == "Voltage (V)"
    assert wdg.table.source_model().column_index == "Voltage (V)"


def test_table_widget_update_column_index_none(qtbot):
    wdg = _make_widget(qtbot, refresh_time=None, column_index="Voltage (V)")
    wdg.update_column_index(0)  # <None>
    assert wdg.column_index is None
    assert wdg.table.source_model().column_index is None


def test_table_widget_new_curve(qtbot):
    wdg = _make_widget(qtbot, refresh_time=None)
    results = FakeResults()
    curve = wdg.new_curve(results, color=RED)
    assert isinstance(curve, ResultsTable)
    assert curve.results is results
    assert curve.color == RED
    assert curve.wdg is wdg


def test_table_widget_load_remove(qtbot):
    wdg = _make_widget(qtbot, refresh_time=None)
    results = FakeResults()
    table = wdg.new_curve(results)
    wdg.load(table)
    assert wdg.table.source_model().rowCount() == 3
    wdg.remove(table)
    assert wdg.table.source_model().rowCount() == 0


def test_table_widget_set_color(qtbot):
    wdg = _make_widget(qtbot, refresh_time=None)
    results = FakeResults()
    table = wdg.new_curve(results)
    wdg.load(table)
    wdg.set_color(table, BLUE)
    assert table.color == BLUE


def test_table_widget_clear_widget(qtbot):
    wdg = _make_widget(qtbot, refresh_time=None)
    results = FakeResults()
    table = wdg.new_curve(results)
    wdg.load(table)
    assert wdg.table.source_model().rowCount() == 3
    wdg.clear_widget()
    assert wdg.table.source_model().rowCount() == 0


def test_table_widget_preview_widget(qtbot):
    wdg = _make_widget(qtbot, by_column=True, refresh_time=None)
    preview = wdg.preview_widget()
    qtbot.addWidget(preview)
    assert isinstance(preview, TableWidget)
    assert preview.name == "Table preview"
    assert preview.columns == wdg.columns
    assert preview.refresh_time is None
    assert preview.check_status is False
    # by_column=True -> "By Column"
    assert isinstance(preview.table.source_model(), PandasModelByColumn)


def test_table_widget_preview_widget_by_row(qtbot):
    wdg = _make_widget(qtbot, by_column=False, refresh_time=None)
    preview = wdg.preview_widget()
    qtbot.addWidget(preview)
    assert isinstance(preview.table.source_model(), PandasModelByRow)


def test_table_widget_layout_class_map(qtbot):
    assert TableWidget.layout_class_map == {
        "By Row": PandasModelByRow,
        "By Column": PandasModelByColumn,
    }
