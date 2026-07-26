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

import importlib.metadata
import warnings
from typing import Dict, Optional, Tuple, Type

from .instrument import Instrument

_REGISTRY: Dict[Tuple[str, str], Type[Instrument]] = {}


def register(cls: Type[Instrument], manufacturer: str, name: str) -> None:
    """Register an instrument class in the plugin registry.

    The class must be a subclass of
    :py:class:`~pymeasure.instruments.instrument.Instrument`.

    :param cls: Instrument class to register.
    :param manufacturer: Manufacturer identifier (e.g. ``"ni"``).
    :param name: Instrument name within the manufacturer namespace (e.g. ``"daqmx"``).
    :raises TypeError: If *cls* is not an :py:class:`~pymeasure.instruments.Instrument` subclass.
    """
    if not isinstance(cls, type) or not issubclass(cls, Instrument):
        raise TypeError(f"{cls!r} is not an Instrument subclass")
    _REGISTRY[(manufacturer, name)] = cls


def unregister(manufacturer: str, name: str) -> None:
    """Remove a previously registered instrument from the registry.

    :param manufacturer: Manufacturer identifier.
    :param name: Instrument name.
    :raises KeyError: If the (manufacturer, name) pair is not registered.
    """
    del _REGISTRY[(manufacturer, name)]


def discover(group: str = "pymeasure.instruments") -> Dict[Tuple[str, str], Type[Instrument]]:
    """Auto-discover and load plugin instruments via entry points.

    Third-party packages declare instruments under the
    ``pymeasure.instruments`` entry point group in their ``pyproject.toml``::

        [project.entry-points."pymeasure.instruments"]
        "ni.daqmx" = "pymeasure_ni.daqmx:DAQmxInstrument"

    The entry point name uses the convention ``"<manufacturer>.<name>"``.
    If the dot is absent, the entire name is used as the instrument name
    and the manufacturer is set to ``"unknown"``.

    This function may be called multiple times; already-registered entries
    are silently overwritten.

    :param group: The entry point group to scan.
    :returns: Mapping of ``(manufacturer, name)`` to the loaded instrument classes.
    """
    eps = importlib.metadata.entry_points()
    if isinstance(eps, dict):
        entries = eps.get(group, [])
    else:
        entries = eps.select(group=group)
    loaded: Dict[Tuple[str, str], Type[Instrument]] = {}
    for ep in entries:
        try:
            cls = ep.load()
            parts = ep.name.split(".", 1)
            manufacturer = parts[0] if len(parts) > 1 else "unknown"
            name = parts[-1]
            register(cls, manufacturer, name)
            loaded[(manufacturer, name)] = cls
        except Exception as exc:
            warnings.warn(f"Failed to load plugin {ep.name!r}: {exc}", RuntimeWarning)
    return loaded


def list_plugins() -> Dict[Tuple[str, str], Type[Instrument]]:
    """Return a shallow copy of the current plugin registry.

    :returns: Mapping of ``(manufacturer, name)`` to instrument classes.
    """
    return dict(_REGISTRY)


def get(manufacturer: str, name: str) -> Optional[Type[Instrument]]:
    """Look up a registered instrument class.

    :param manufacturer: Manufacturer identifier.
    :param name: Instrument name.
    :returns: The instrument class, or ``None`` if not registered.
    """
    return _REGISTRY.get((manufacturer, name))


def clear() -> None:
    """Remove all entries from the plugin registry."""
    _REGISTRY.clear()
