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
import time
from typing import TypeVar
from collections.abc import Sequence
from warnings import warn

from .common_base import CommonBase
from ..adapters.adapter import Adapter
from ..adapters.visa import VISAAdapter

_Self = TypeVar("_Self", bound="Instrument")  # typing.Self for Python>3.10

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


AdapterType = Adapter | str | int

class Instrument(CommonBase):
    """The base class for all Instrument definitions.

    It makes use of one of the :py:class:`~pymeasure.adapters.Adapter` classes for communication
    with the connected hardware device. This decouples the instrument/command definition from the
    specific communication interface used.

    When ``adapter`` is a string, this is taken as an appropriate resource name. Depending on your
    installed VISA library, this can be something simple like ``COM1`` or ``ASRL2``, or a more
    complicated
    `VISA resource name <https://pyvisa.readthedocs.io/en/latest/introduction/names.html>`__
    defining the target of your connection.

    When ``adapter`` is an integer, a GPIB resource name is created based on that.
    In either case a :py:class:`~pymeasure.adapters.VISAAdapter` is constructed based on that
    resource name.
    Keyword arguments can be used to further configure the connection.

    Otherwise, the passed :py:class:`~pymeasure.adapters.Adapter` object is used and any keyword
    arguments are discarded.

    :param adapter: A string, integer, or :py:class:`~pymeasure.adapters.Adapter` subclass object
    :param string name: The name of the instrument. Often the model designation by default.

    :param \\**kwargs: In case ``adapter`` is a string or integer, additional arguments passed on
        to :py:class:`~pymeasure.adapters.VISAAdapter` (check there for details).
        Discarded otherwise.
    """
    adapter: Adapter

    # noinspection PyPep8Naming
    def __init__(
        self,
        adapter: AdapterType,
        name: str,
        **kwargs,
    ):
        if "includeSCPI" in kwargs.keys():
            warn("Defining SCPI base functionality with `includeSCPI` is deprecated, inherit "
                 "the `SCPIMixin` class instead if it supports SCPI.", FutureWarning)
            kwargs.pop("includeSCPI")
        # Setup communication before possible children require the adapter.
        if isinstance(adapter, (int, str)):
            try:
                adapter = VISAAdapter(adapter, **kwargs)
            except ImportError:
                raise Exception("Invalid Adapter provided for Instrument since"
                                " PyVISA is not present")
        self.adapter = adapter
        self.isShutdown = False
        self.name = name

        super().__init__()

        log.info(f"Initializing {self.name}.")

    def __enter__(self: _Self) -> _Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool | None:
        self.shutdown()
        return None

    # Wrapper functions for the Adapter object
    def write(self, command: str, **kwargs) -> None:
        """Write a string command to the instrument appending `write_termination`.

        :param command: command string to be sent to the instrument
        :param kwargs: Keyword arguments for the adapter.
        """
        self.adapter.write(command, **kwargs)

    def write_bytes(self, content: bytes, **kwargs) -> None:
        """Write the bytes `content` to the instrument."""
        self.adapter.write_bytes(content, **kwargs)

    def read(self, **kwargs) -> str:
        """Read up to (excluding) `read_termination` or the whole read buffer."""
        return self.adapter.read(**kwargs)

    def read_bytes(self, count: int, **kwargs) -> bytes:
        """Read a certain number of bytes from the instrument.

        :param int count: Number of bytes to read. A value of -1 indicates to
            read the whole read buffer.
        :param kwargs: Keyword arguments for the adapter.
        :returns bytes: Bytes response of the instrument (including termination).
        """
        return self.adapter.read_bytes(count, **kwargs)

    def write_binary_values(
        self, command: str, values: Sequence[int | float], *args, **kwargs
    ) -> None:
        """Write binary values to the device.

        :param command: Command to send.
        :param values: The values to transmit.
        :param \\*args, \\**kwargs: Further arguments to hand to the Adapter.
        """
        self.adapter.write_binary_values(command, values, *args, **kwargs)

    def read_binary_values(self, **kwargs):
        """Read binary values from the device."""
        return self.adapter.read_binary_values(**kwargs)

    # Communication functions
    def wait_for(self, query_delay: float | None = None) -> None:
        """Wait for some time. Used by 'ask' to wait before reading.

        :param query_delay: Delay between writing and reading in seconds. None is default delay.
        """
        if query_delay:
            time.sleep(query_delay)

    def shutdown(self) -> None:
        """Brings the instrument to a safe and stable state"""
        self.isShutdown = True
        log.info(f"Finished shutting down {self.name}")

    def check_get_errors(self) -> list:
        """Check for errors after having gotten a property and log them.

        Called if :code:`check_get_errors=True` is set for that property.

        If you override this method, you may choose to raise an Exception for certain errors.

        :return: List of error entries.
        """
        return self.check_errors()

    def check_set_errors(self) -> list:
        """Check for errors after having set a property and log them.

        Called if :code:`check_set_errors=True` is set for that property.

        If you override this method, you may choose to raise an Exception for certain errors.

        :return: List of error entries.
        """
        return self.check_errors()
