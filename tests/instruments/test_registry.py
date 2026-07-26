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

import warnings
from importlib.metadata import EntryPoint
from unittest import mock

import pytest

from pymeasure.instruments.fakes import FakeInstrument
from pymeasure.instruments.registry import (
    _REGISTRY,
    clear,
    discover,
    get,
    list_plugins,
    register,
    unregister,
)


class FakePlugin(FakeInstrument):
    pass


@pytest.fixture(autouse=True)
def _clean_registry():
    yield
    _REGISTRY.clear()


class TestRegister:
    def test_registers_instrument_subclass(self):
        register(FakePlugin, "acme", "widget")
        assert _REGISTRY[("acme", "widget")] is FakePlugin

    def test_rejects_non_instrument(self):
        with pytest.raises(TypeError, match="not an Instrument subclass"):
            register(int, "acme", "bad")

    def test_rejects_non_type(self):
        with pytest.raises(TypeError, match="not an Instrument subclass"):
            register("not a class", "acme", "bad")

    def test_overwrite_existing(self):
        register(FakePlugin, "acme", "widget")

        class AnotherPlugin(FakeInstrument):
            pass

        register(AnotherPlugin, "acme", "widget")
        assert _REGISTRY[("acme", "widget")] is AnotherPlugin


class TestUnregister:
    def test_removes_entry(self):
        register(FakePlugin, "acme", "widget")
        unregister("acme", "widget")
        assert ("acme", "widget") not in _REGISTRY

    def test_raises_on_missing(self):
        with pytest.raises(KeyError):
            unregister("no", "such")


class TestGet:
    def test_returns_registered_class(self):
        register(FakePlugin, "acme", "widget")
        assert get("acme", "widget") is FakePlugin

    def test_returns_none_for_missing(self):
        assert get("no", "such") is None


class TestListPlugins:
    def test_returns_copy(self):
        register(FakePlugin, "acme", "widget")
        plugins = list_plugins()
        assert plugins == {("acme", "widget"): FakePlugin}
        plugins.clear()
        assert ("acme", "widget") in _REGISTRY

    def test_empty_when_nothing_registered(self):
        assert list_plugins() == {}


class TestClear:
    def test_empties_registry(self):
        register(FakePlugin, "acme", "widget")
        clear()
        assert len(_REGISTRY) == 0


class TestDiscover:
    def test_loads_entry_points(self):
        ep = EntryPoint(
            name="ni.daqmx",
            value="pymeasure.instruments.fakes:FakeInstrument",
            group="pymeasure.instruments",
        )
        with mock.patch(
            "pymeasure.instruments.registry.importlib.metadata.entry_points",
            return_value={"pymeasure.instruments": [ep]},
        ):
            loaded = discover()
        assert loaded == {("ni", "daqmx"): FakeInstrument}
        assert get("ni", "daqmx") is FakeInstrument

    def test_entry_point_without_dot(self):
        ep = EntryPoint(
            name="daqmx",
            value="pymeasure.instruments.fakes:FakeInstrument",
            group="pymeasure.instruments",
        )
        with mock.patch(
            "pymeasure.instruments.registry.importlib.metadata.entry_points",
            return_value={"pymeasure.instruments": [ep]},
        ):
            loaded = discover()
        assert ("unknown", "daqmx") in loaded

    def test_warns_on_broken_plugin(self):
        ep = EntryPoint(
            name="ni.broken",
            value="nonexistent_module:BrokenClass",
            group="pymeasure.instruments",
        )
        with mock.patch(
            "pymeasure.instruments.registry.importlib.metadata.entry_points",
            return_value={"pymeasure.instruments": [ep]},
        ):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                discover()
        assert any("Failed to load plugin" in str(warning.message) for warning in w)

    def test_select_api_for_python312(self):
        ep = EntryPoint(
            name="ni.scope",
            value="pymeasure.instruments.fakes:FakeInstrument",
            group="pymeasure.instruments",
        )

        class _Eps:
            def select(self, *, group):
                return [ep] if group == "pymeasure.instruments" else []

        with mock.patch(
            "pymeasure.instruments.registry.importlib.metadata.entry_points",
            return_value=_Eps(),
        ):
            loaded = discover()
        assert ("ni", "scope") in loaded

    def test_custom_group(self):
        ep = EntryPoint(
            name="custom.inst",
            value="pymeasure.instruments.fakes:FakeInstrument",
            group="custom.group",
        )
        with mock.patch(
            "pymeasure.instruments.registry.importlib.metadata.entry_points",
            return_value={"custom.group": [ep]},
        ):
            loaded = discover(group="custom.group")
        assert ("custom", "inst") in loaded
