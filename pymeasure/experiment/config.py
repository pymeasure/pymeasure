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


def set_file(filename: str) -> None:
    os.environ["CONFIG"] = filename


def get_config(filename: str = "default_config.ini") -> configparser.ConfigParser:
    if "CONFIG" in os.environ:
        filename = os.environ["CONFIG"]
    config = configparser.ConfigParser()
    config.read(filename)
    return config


def section_items(config: configparser.ConfigParser, section: str) -> dict[str, str]:
    """Return a section's own items, excluding keys inherited from ``[DEFAULT]``.

    Keys explicitly overridden in ``section`` (same-named as a ``[DEFAULT]``
    key) are included; only keys genuinely inherited from ``[DEFAULT]``
    without a section-local definition are excluded.

    :param config: The config parser to read from.
    :param section: The section name; it must exist in ``config``.
    :returns: A dict of the section's own raw ``(key, value)`` pairs.
    """
    # ``config.items()`` merges ``[DEFAULT]`` items into every section, so it
    # cannot distinguish an inherited key from a same-named section override.
    # ``_sections`` holds the section's own raw items (what configparser
    # ``read*`` stored for this section), which is used here to keep overrides.
    # It is not part of the public stubs, hence the ignore below.
    return dict(config._sections[section])  # pyright: ignore[reportAttributeAccessIssue]


# noinspection PyProtectedMember
def set_mpl_rcparams(config: configparser.ConfigParser) -> None:
    if config.has_section("matplotlib.rcParams"):
        import matplotlib

        for key, value in section_items(config, "matplotlib.rcParams").items():
            matplotlib.rcParams[key] = eval(value)  # pyright: ignore[reportArgumentType]
