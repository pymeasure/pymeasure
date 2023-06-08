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
import time
from warnings import warn

from pymeasure.adapters import VISAAdapter


class NI_GPIB_232(VISAAdapter):
    """ Encapsulates the additional commands necessary
    to communicate over a National Instruments GPIB-232CT Adapter,
    using the :class:`VISAAdapter`.

    Each Adapter is constructed based on a connection to the BI device
    itself and the GPIB address of the instrument to be communicated to.
    Connection sharing is achieved by using the :meth:`.gpib`
    method to spawn new NI_GPIB_232s for different GPIB addresses.

    :param resource_name: A
        `VISA resource string <https://pyvisa.readthedocs.io/en/latest/introduction/names.html>`__
        that identifies the connection to the Prologix device itself, for example
        "ASRL5" for the 5th COM port.
    :param address: Integer GPIB address of the desired instrument.
    :param rw_delay: An optional delay to set between a write and read call for
        slow to respond instruments.

        .. deprecated:: 0.11
            Implement it in the instrument's `wait_for` method instead.

    :param preprocess_reply: optional callable used to preprocess
        strings received from the instrument. The callable returns the
        processed string.

        .. deprecated:: 0.11
            Implement it in the instrument's `read` method instead.

    :param auto: Enable or disable read-after-write and address instrument to listen.
    :param eoi: Enable or disable EOI assertion.
    :param eos: Set command termination string (CR+LF, CR, LF, or "")
    :param kwargs: Key-word arguments if constructing a new serial object

    :ivar address: Integer GPIB address of the desired instrument.

    Usage example:

    .. code::

        adapter = NI_GPIB_232("ASRL5::INSTR", 7)
        sourcemeter = Keithley2400(adapter)  # at GPIB address 7
        # generate another instance with a different GPIB address:
        adapter2 = adapter.gpib(9)
        multimeter = Keithley2000(adapter2)  # at GPIB address 9

#TODO:
    add specifics on the RS232 paramter settings

    """

    def __init__(self, resource_name, address=None, rw_delay=0, serial_timeout=None,
                 preprocess_reply=None, auto=False, eoi=True, eos="\n", **kwargs):
        # for legacy rw_delay: prefer new style over old one.
        if rw_delay:
            warn(("Parameter `rw_delay` is deprecated. "
                  "Implement in Instrument's `wait_for` instead."),
                 FutureWarning)
            kwargs['query_delay'] = rw_delay
        if serial_timeout:
            warn("Parameter `serial_timeout` is deprecated. Use `timeout` in ms instead",
                 FutureWarning)
            kwargs['timeout'] = serial_timeout
        super().__init__(resource_name,
                         asrl={
                             'timeout': 500,
                             'write_termination': "",
                         },
                         preprocess_reply=preprocess_reply,
                         **kwargs)
        self.address = address
        super().write("EOS R 10\r")
        super().write("EOS X 10\r")
        
        # if not isinstance(resource_name, NI_GPIB_232):
            # self.auto = auto
            # self.eoi = eoi
            # self.eos = eos

    # @property
    # def auto(self):
    #     """Control whether to address instruments to talk after sending them a command (bool).

    #     Configure Prologix GPIB controller to automatically address instruments
    #     to talk after sending them a command in order to read their response. The
    #     feature called, Read-After-Write, saves the user from having to issue read commands
    #     repeatedly. This property enables (True) or disables (False) this feature.
    #     """
    #     self.write("++auto")
    #     return bool(int(self.read(prologix=True)))

    # @auto.setter
    # def auto(self, value):
    #     self.write(f"++auto {int(value)}")

    @property
    def eoi(self):
        """Control whether to assert the EOI signal with the last character
        of any command sent over GPIB port (bool).

        Some instruments require EOI signal to be
        asserted in order to properly detect the end of a command.
        """
        super().write("EOT ")
        return bool(int(self.read(prologix=True)))
        self.read(prologix=True)

    @eoi.setter
    def eoi(self, value):
        super().write(f"EOT {int(value)}")

    @property
    def eos(self):
        """Control GPIB termination characters (str).

        possible values:
            - CR+LF
            - CR
            - LF
            - empty string

        When data from host is received, all non-escaped LF, CR and ESC characters are
        removed and GPIB terminators, as specified by this command, are appended before
        sending the data to instruments. This command does not affect data fromMHz
        instruments received over GPIB port.
        """
        values = {0: "\r\n", 1: "\r", 2: "\n", 3: ""}
        super().write("EOS")
        return values[int(self.read(prologix=True))]

    @eos.setter
    def eos(self, value):
        values = {"\r\n": 0, "\r": 1, "\n": 2, "": 3}
        super().write(f"s {values[value]}")

    @property
    def version(self):
        """Get the version string of the Prologix controller.
        """
        super().write('id')
        return self.read(prologix=True)

    # def reset(self):
    #     """Perform a power-on reset of the controller.

    #     The process takes about 5 seconds. All input received during this time
    #     is ignored and the connection is closed.
    #     """
    #     self.write('++rst')

    def ask(self, command):
        """ Ask the Prologix controller.

        .. deprecated:: 0.11
           Call `Instrument.ask` instead.

        :param command: SCPI command string to be sent to instrument
        """
        warn("`Adapter.ask` is deprecated, call `Instrument.ask` instead.", FutureWarning)
        self.write(command)
        return self.read()

    def send_command(self,  data: bytes):
        """
        Write GPIB command bytes on the bus.

        """
        super().write(f"cmd  #{data.length}\n" + data + "\r")

    def pass_control(self, primary_address: int, secondary_address: int):
        """
        Pass control to drevice with primary_address and optional secondary_address

        """
        super().write(f"pct  {primary_address}+{secondary_address}")

    def set_rsc(self):
        """
        set the NI-GPIB232ct to become teh GOIB system controller

        """
        super().write("rsc  1 \n")

    def send_ifc(self):
        """Pulse the interface clear line (IFC) for at least 100 microseconds.

        """
        super().write("sic 0.0002 /n")

    def write(self, command, **kwargs):
        """Write a string command to the instrument appending `write_termination`.

        If the GPIB address in :attr:`.address` is defined, it is sent first.

        :param str command: Command string to be sent to the instrument
            (without termination).
        :param kwargs: Keyword arguments for the connection itself.
        """
        # Overrides write instead of _write in order to ensure proper logging
        # if self.address is not None:
        #     super().write(f"wrt {self.address}  {command} \n", **kwargs)
        super().write(f"wrt {self.address} \n  {command}\n", **kwargs)

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
            address_command = f"wrt { self.address}"
            self.write(address_command)
        super().write_binary_values(command, values, "\n", **kwargs)

    def _read(self, prologix=False, **kwargs):
        """Read up to (excluding) `read_termination` or the whole read buffer.

        :param prologix: Read the prologix adapter itself.
        :param kwargs: Keyword arguments for the connection itself.
        :returns str: ASCII response of the instrument (excluding read_termination).
        """
        if not prologix:
            super().write(f"rd {self.address}\r")
        return super()._read()

    def gpib(self, address, **kwargs):
        """ Return a NI_GPIB_232 object that references the GPIB
        address specified, while sharing the Serial connection with other
        calls of this function

        :param address: Integer GPIB address of the desired instrument
        :param kwargs: Arguments for the initialization
        :returns: NI_GPIB_232 for specific GPIB address
        """
        return NI_GPIB_232(self, address, **kwargs)

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
            return (f"<NI_GPIB_232(resource_name='{self.connection.resource_name}', "
                    f"address={self.address:d})>")
        else:
            return f"<NI_GPIB_232(resource_name='{self.connection.resource_name}')>"
