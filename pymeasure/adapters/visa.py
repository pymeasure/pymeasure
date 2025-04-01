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

import logging
from warnings import warn

import pyvisa
import numpy as np

from .adapter import Adapter
from .protocol import ProtocolAdapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# noinspection PyPep8Naming,PyUnresolvedReferences
class VISAAdapter(Adapter):
    """ Adapter class for the VISA library, using PyVISA to communicate with instruments.

    The workhorse of our library, used by most instruments.

    :param resource_name: A
        `VISA resource string <https://pyvisa.readthedocs.io/en/latest/introduction/names.html>`__
        or GPIB address integer that identifies the target of the connection
    :param visa_library: PyVISA VisaLibrary Instance, path of the VISA library or VisaLibrary spec
        string (``@py`` or ``@ivi``). If not given, the default for the platform will be used.
    :param log: Parent logger of the 'Adapter' logger.
    :param \\**kwargs: Keyword arguments for configuring the PyVISA connection.

    :Kwargs:
        Keyword arguments are used to configure the connection created by PyVISA. This is
        complicated by the fact that *which* arguments are valid depends on the interface (e.g.
        serial, GPIB, TCPI/IP, USB) determined by the current ``resource_name``.

        A flexible process is used to easily define reasonable *default values* for
        different instrument interfaces, but also enable the instrument user to *override any
        setting* if their situation demands it.

        A kwarg that names a pyVISA interface type (most commonly ``asrl``, ``gpib``, ``tcpip``, or
        ``usb``) is a dictionary with keyword arguments defining defaults specific to that
        interface. Example: ``asrl={'baud_rate': 4200}``.

        All other kwargs are either generally valid (e.g. ``timeout=500``) or override any default
        settings from the interface-specific entries above. For example, passing
        ``baud_rate=115200`` when connecting via a resource name ``ASRL1`` would override a
        default of 4200 defined as above.

        See :ref:`connection_settings` for how to tweak settings when *connecting* to an instrument.
        See :ref:`default_connection_settings` for how to best define default settings when
        *implementing an instrument*.
    """

    def __init__(self, resource_name, visa_library='',
                 log=None, **kwargs):
        super().__init__(log=log)
        if isinstance(resource_name, ProtocolAdapter):
            self.connection = resource_name
            self.connection.write_raw = self.connection.write_bytes
            self.read_bytes = self.connection.read_bytes
            return
        elif isinstance(resource_name, VISAAdapter):
            # Allow to reuse the connection.
            self.resource_name = getattr(resource_name, "resource_name", None)
            self.connection = resource_name.connection
            self.manager = resource_name.manager
            return
        elif isinstance(resource_name, int):
            resource_name = "GPIB0::%d::INSTR" % resource_name

        self.resource_name = resource_name
        self.manager = pyvisa.ResourceManager(visa_library)

        # Clean up kwargs considering the interface type matching resource_name
        if_type = self.manager.resource_info(self.resource_name).interface_type
        for key in list(kwargs.keys()):  # iterate over a copy of the keys as we modify kwargs
            # Remove all interface-specific kwargs:
            if key in pyvisa.constants.InterfaceType.__members__:
                if getattr(pyvisa.constants.InterfaceType, key) is if_type:
                    # For the present interface, dump contents into kwargs first if they are not
                    # present already. This way, it is possible to override default values with
                    # kwargs passed to Instrument.__init__()
                    for k, v in kwargs[key].items():
                        kwargs.setdefault(k, v)
                del kwargs[key]

        self.connection = self.manager.open_resource(
            resource_name,
            **kwargs
        )

    def close(self):
        """Close the connection.

        .. note::

            This closes the connection to the resource for all adapters using
            it currently (e.g. different adapters using the same GPIB line).
        """
        super().close()
        try:
            if self.manager.visalib.library_path == "unset":
                # if using the pyvisa-sim library the manager has to be also closed.
                # this works around https://github.com/pyvisa/pyvisa-sim/issues/82
                self.manager.close()
        except AttributeError:
            # AttributeError can occur during __del__ calling close
            pass

    def _write(self, command, **kwargs):
        """Write a string command to the instrument appending `write_termination`.

        :param str command: Command string to be sent to the instrument
            (without termination).
        :param \\**kwargs: Keyword arguments for the connection itself.
        """
        self.connection.write(command, **kwargs)

    def _write_bytes(self, content, **kwargs):
        """Write the bytes `content` to the instrument.

        :param bytes content: The bytes to write to the instrument.
        :param \\**kwargs: Keyword arguments for the connection itself.
        """
        self.connection.write_raw(content, **kwargs)

    def _read(self, **kwargs):
        """Read up to (excluding) `read_termination` or the whole read buffer.

        :param \\**kwargs: Keyword arguments for the connection itself.
        :returns str: ASCII response of the instrument (excluding read_termination).
        """
        return self.connection.read(**kwargs)

    def _read_bytes(self, count, break_on_termchar=False, **kwargs):
        """Read a certain number of bytes from the instrument.

        :param int count: Number of bytes to read. A value of -1 indicates to
            read from the whole read buffer until timeout.
        :param bool break_on_termchar: Stop reading at a termination character.
        :param \\**kwargs: Keyword arguments for the connection itself.
        :returns bytes: Bytes response of the instrument (including termination).
        """
        if count >= 0:
            return self.connection.read_bytes(count, break_on_termchar=break_on_termchar, **kwargs)
        elif break_on_termchar:
            return self.connection.read_raw(None, **kwargs)
        else:
            # pyvisa's `read_raw` reads until newline, if no termination_character defined
            # and if not configured to stop at a termination lane etc.
            # see https://github.com/pyvisa/pyvisa/issues/728
            result = bytearray()
            while True:
                try:
                    result.extend(self.connection.read_bytes(1))
                except pyvisa.errors.VisaIOError as exc:
                    if exc.error_code == pyvisa.constants.StatusCode.error_timeout:
                        return bytes(result)
                    raise

    def wait_for_srq(self, timeout=25, delay=0.1):
        """ Block until a SRQ, and leave the bit high

        :param timeout: Timeout duration in seconds
        :param delay: Time delay between checking SRQ in seconds
        """
        self.connection.wait_for_srq(timeout * 1000)

    def flush_read_buffer(self):
        """ Flush and discard the input buffer

        As detailed by pyvisa, discard the read and receivee buffer contents
        and if data was present in the read buffer and no END-indicator was present,
        read from the device until encountering an END indicator (which causes loss of data).
        """
        try:
            self.connection.flush(pyvisa.constants.BufferOperation.discard_read_buffer)
            self.connection.flush(pyvisa.constants.BufferOperation.discard_receive_buffer)
        except NotImplementedError:
            # NotImplementedError is raised when using resource types other than `asrl`
            # in conjunction with pyvisa-py.
            # Upstream issue: https://github.com/pyvisa/pyvisa-py/issues/348
            # fake discarding the read buffer by reading all available messages.
            timeout = self.connection.timeout
            self.connection.timeout = 0
            try:
                self.read_bytes(-1)
            except pyvisa.errors.VisaIOError:
                pass
            finally:
                self.connection.timeout = timeout

    def __repr__(self):
        return "<VISAAdapter(resource='%s')>" % self.connection.resource_name
