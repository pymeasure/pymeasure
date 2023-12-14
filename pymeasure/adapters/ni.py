#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

import nidaqmx
import re

import logging
from warnings import warn

from .adapter import Adapter
from .protocol import ProtocolAdapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# noinspection PyPep8Naming,PyUnresolvedReferences
class NIAdapter(Adapter):
    """ Adapter class for the NI-DAQ library, using NI-DAQmx Python to
    communicate with instruments.

    :param name: An NI DAQ device name (e.g. 'Dev1'), model number
        (e.g. 'USB-6212'), or serial number (e.g. 1A3808F).
    :param log: Parent logger of the 'Adapter' logger.
    :param \\**kwargs: Keyword arguments for configuring the NI-DAQmx connection.

    :Kwargs:
        Keyword arguments are used to configure the connection created by
        NI-DAQmx. Which arguments are valid depends on the interface determined by
        the current ``name``.

        See :ref:`connection_settings` for how to tweak settings when *connecting* to an instrument.
        See :ref:`default_connection_settings` for how to best define default settings when
        *implementing an instrument*.
    """

    def __init__(self, name, log=None, **kwargs):
        super().__init__(log=log)

        # Possibly irrelvant to check if isinstance ProtocolAdapter
        if isinstance(name, ProtocolAdapter):
            self.connection = name
            self.connection.write_raw = self.connection.write_bytes
            self.read_bytes = self.connection.read_bytes
            return

        self.name = name
        self.system = nidaqmx.system.System()
        self.dev_name = self.search_for_dev_name()
        self.connection = nidaqmx.system.Device(self.dev_name)

    def search_for_dev_name(self):
        """Search for ``name`` in all connected devices.

        :param name: An NI DAQ device name (e.g. 'Dev1'), model number
        (e.g. 'USB-6212'), or serial number (e.g. 1A3808F). Case insensitive.

        :returns: The NI DAQ device name or raises a ValueError if the resource is not found.
        """
        dev_names = self.system.devices.device_names
        re_pattern = re.compile(self.device_name, re.IGNORECASE)
        for dev_name in dev_names:
            dev = nidaqmx.system.Device(dev_name)
            if re.search(re_pattern, dev.name):
                return dev_name
            elif re.search(re_pattern, dev.product_type):
                return dev_name
            elif re.search(re_pattern, hex(dev.serial_num)):
                return dev_name
            else:
                dev_name = None
        if dev_name is None:
            raise ValueError(f"Device name not found: {self.device_name}")
        return dev_name

    def close(self):
        """Close the connection."""
        # Determine if needed
        raise NotImplementedError

    def _write(self, command, **kwargs):
        """Not implemented."""
        raise NotImplementedError

    def _write_bytes(self, content, **kwargs):
        """Not implemented."""
        raise NotImplementedError

    def _read(self, **kwargs):
        """Not implemented."""
        raise NotImplementedError

    def _read_bytes(self, count, break_on_termchar=False, **kwargs):
        """Not implemented."""
        raise NotImplementedError

    def __repr__(self):
        return f"<NIAdapter(dev_name={self.dev_name})>"
