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
import os

import pytest

from pymeasure.experiment.config import get_config, set_file, set_mpl_rcparams


def test_set_file_sets_env_var(monkeypatch):
    monkeypatch.delenv("CONFIG", raising=False)
    set_file("foo.ini")
    assert os.environ["CONFIG"] == "foo.ini"


def test_get_config_returns_configparser():
    config = get_config("nonexistent_file_for_test.ini")
    assert isinstance(config, configparser.ConfigParser)


def test_get_config_reads_default_file(tmp_path, monkeypatch):
    monkeypatch.delenv("CONFIG", raising=False)
    config_file = tmp_path / "default_config.ini"
    config_file.write_text("[Section1]\nkey = value\n")
    monkeypatch.chdir(tmp_path)
    config = get_config()
    assert config.sections() == ["Section1"]
    assert config["Section1"]["key"] == "value"


def test_get_config_reads_env_file(tmp_path, monkeypatch):
    config_file = tmp_path / "env_config.ini"
    config_file.write_text("[EnvSection]\nfoo = bar\n")
    monkeypatch.setenv("CONFIG", str(config_file))
    config = get_config()
    assert config.sections() == ["EnvSection"]
    assert config["EnvSection"]["foo"] == "bar"


def test_get_config_env_overrides_default(tmp_path, monkeypatch):
    env_file = tmp_path / "env_config.ini"
    env_file.write_text("[EnvSection]\n")
    arg_file = tmp_path / "arg_config.ini"
    arg_file.write_text("[ArgSection]\n")
    monkeypatch.setenv("CONFIG", str(env_file))
    config = get_config(str(arg_file))
    assert config.sections() == ["EnvSection"]


def test_get_config_missing_file_empty(monkeypatch):
    monkeypatch.delenv("CONFIG", raising=False)
    config = get_config("definitely_does_not_exist.ini")
    assert isinstance(config, configparser.ConfigParser)
    assert config.sections() == []


def test_set_mpl_rcparams_no_section_noop():
    pytest.importorskip("matplotlib")
    import matplotlib

    config = configparser.ConfigParser()
    config.add_section("other")
    config["other"]["key"] = "value"
    original = dict(matplotlib.rcParams)
    set_mpl_rcparams(config)
    assert dict(matplotlib.rcParams) == original


def test_set_mpl_rcparams_applies_values():
    matplotlib = pytest.importorskip("matplotlib")
    config = configparser.ConfigParser()
    config.add_section("matplotlib.rcParams")
    config["matplotlib.rcParams"]["figure.dpi"] = "100"
    set_mpl_rcparams(config)
    assert matplotlib.rcParams["figure.dpi"] == 100


def test_set_mpl_rcparams_uses_eval():
    matplotlib = pytest.importorskip("matplotlib")
    config = configparser.ConfigParser()
    config.add_section("matplotlib.rcParams")
    config["matplotlib.rcParams"]["figure.figsize"] = "[6, 4]"
    set_mpl_rcparams(config)
    # The string "[6, 4]" is eval'd into a python list, not kept as a string.
    assert matplotlib.rcParams["figure.figsize"] == [6, 4]
    assert isinstance(matplotlib.rcParams["figure.figsize"], list)
