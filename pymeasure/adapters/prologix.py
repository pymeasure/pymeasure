#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
import time
from warnings import warn

from pymeasure.adapters import VISAAdapter


class PrologixAdapter(VISAAdapter):
    """ Encapsulates the additional commands necessary
    to communicate over a Prologix GPIB-USB Adapter,
    using the :class:`VISAAdapter`.

    Each PrologixAdapter is constructed based on a serial port or
    connection and the GPIB address to be communicated to.
    Serial connection sharing is achieved by using the :meth:`.gpib`
    method to spawn new PrologixAdapters for different GPIB addresses.

    :param port: The Serial port name or a connection object
    :param address: Integer GPIB address of the desired instrument
    :param rw_delay: An optional delay to set between a write and read call for
        slow to respond instruments.

        .. deprecated:: 0.11
            Implement it in the instrument's `wait_until_read` method instead.

    :param preprocess_reply: optional callable used to preprocess
        strings received from the instrument. The callable returns the
        processed string.

        .. deprecated:: 0.11
            Implement it in the instrument's `read` method instead.

    :param kwargs: Key-word arguments if constructing a new serial object

    :ivar address: Integer GPIB address of the desired instrument

    To allow user access to the Prologix adapter in Linux, create the file:
    :code:`/etc/udev/rules.d/51-prologix.rules`, with contents:

    .. code-block:: bash

        SUBSYSTEMS=="usb",ATTRS{idVendor}=="0403",ATTRS{idProduct}=="6001",MODE="0666"

    Then reload the udev rules with:

    .. code-block:: bash

        sudo udevadm control --reload-rules
        sudo udevadm trigger

    """

    def __init__(self, resource_name, address=None, rw_delay=0, serial_timeout=None,
                 preprocess_reply=None, **kwargs):
        # for legacy rw_delay: prefer new style over old one.
        if rw_delay:
            warn("Implement in Instrument's 'wait_until_read' instead.", FutureWarning)
            kwargs['query_delay'] = rw_delay
        if serial_timeout:
            warn("Use 'timeout' in ms instead", FutureWarning)
            kwargs['timeout'] = serial_timeout
        super().__init__(resource_name,
                         asrl={
                             'timeout': 500,
                             'write_termination': "\n",
                         },
                         preprocess_reply=preprocess_reply,
                         **kwargs)
        self.address = address
        if not isinstance(resource_name, PrologixAdapter):
            self.set_defaults()

    def set_defaults(self):
        """ Set up the default behavior of the Prologix-GPIB
        adapter
        """
        self.write("++auto 0")  # Turn off auto read-after-write
        self.write("++eoi 1")  # Append end-of-line to commands
        self.write("++eos 2")  # Append line-feed to commands

    def ask(self, command):
        """ Ask the Prologix controller.

        .. deprecated:: 0.11
           Call `Instrument.ask` instead.

        :param command: SCPI command string to be sent to instrument
        """
        warn("Do not call `Adapter.ask`, but `Instrument.ask` instead.",
             FutureWarning)
        self.write(command)
        return self.read()

    def write(self, command, **kwargs):
        """Write a string command to the instrument appending `write_termination`.

        If the GPIB address in :attr:`.address` is defined, it is sent first.

        :param str command: Command string to be sent to the instrument
            (without termination).
        :param kwargs: Keyword arguments for the connection itself.
        """
        # Overrides write instead of _write in order to ensure proper logging
        if self.address is not None and not command.startswith("++"):
            super().write("++addr %d" % self.address, **kwargs)
        super().write(command, **kwargs)

    def _format_binary_values(self, values, datatype='f', is_big_endian=False, header_fmt="ieee"):
        """Format values in binary format, used internally in :meth:`.write_binary_values`.

        :param values: data to be writen to the device.
        :param datatype: the format string for a single element. See struct module.
        :param is_big_endian: boolean indicating endianess.
        :param header_fmt: Format of the header prefixing the data ("ieee", "hp", "empty").
        :return: binary string.
        :rtype: bytes
        """
        block = super()._format_binary_values(values, datatype, is_big_endian, header_fmt)
        # Prologix needs certian characters to be escaped.
        # Special care must be taken when sending binary data to instruments. If any of the
        # following characters occur in the binary data -- CR (ASCII 13), LF (ASCII 10), ESC
        # (ASCII 27), '+' (ASCII 43) - they must be escaped by preceding them with an ESC
        # character.
        special_chars = b'\x0d\x0a\x1b\x2b'
        new_block = b''
        for b in block:
            escape = b''
            if b in special_chars:
                escape = b'\x1b'
            new_block += (escape + bytes((b,)))

        return new_block

    def write_binary_values(self, command, values, **kwargs):
        """ Write binary data to the instrument, e.g. waveform for signal generators.

        values are encoded in a binary format according to
        IEEE 488.2 Definite Length Arbitrary Block Response Data block.

        :param command: SCPI command to be sent to the instrument
        :param values: iterable representing the binary values
        :param kwargs: Key-word arguments to pass onto :meth:`._format_binary_values`
        :returns: number of bytes written
        """
        if self.address is not None:
            address_command = "++addr %d\n" % self.address
            self.write(address_command)
        super().write_binary_values(command, values, "\n", **kwargs)

    def _read(self, **kwargs):
        """Read up to (excluding) `read_termination` or the whole read buffer.

        :param kwargs: Keyword arguments for the connection itself.
        :returns str: ASCII response of the instrument (excluding read_termination).
        """
        self.write("++read eoi")
        return super()._read()

    def gpib(self, address, **kwargs):
        """ Return a PrologixAdapter object that references the GPIB
        address specified, while sharing the Serial connection with other
        calls of this function

        :param address: Integer GPIB address of the desired instrument
        :param kwargs: Arguments for the initialization
        :returns: PrologixAdapter for specific GPIB address
        """
        return PrologixAdapter(self, address, **kwargs)

    def _check_for_srq(self):
        # it was int(self.ask("++srq"))
        self.write("++srq")
        return int(self.read())

    def wait_for_srq(self, timeout=25, delay=0.1):
        """ Blocks until a SRQ, and leaves the bit high

        :param timeout: Timeout duration in seconds.
        :param delay: Time delay between checking SRQ in seconds.
        :raises TimeoutError: "Waiting for SRQ timed out."
        """
        stop = time.perf_counter() + timeout
        while self._check_for_srq() != 1:
            if time.perf_counter() > stop:
                raise TimeoutError("Waiting for SRQ timed out.")
            time.sleep(delay)

    def __repr__(self):
        if self.address is not None:
            return (f"<PrologixAdapter(resource_name='{self.connection.resource_name}', "
                    f"address={self.address:d})>")
        else:
            return f"<PrologixAdapter(resource_name='{self.connection.resource_name}')>"
