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
import logging
from enum import IntFlag
from time import sleep
from pymeasure.adapters import VISAAdapter


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())




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
        # if rw_delay:
        #     warn(("Parameter `rw_delay` is deprecated. "
        #           "Implement in Instrument's `wait_for` instead."),
        #          FutureWarning)
        #     kwargs['query_delay'] = rw_delay
        # if serial_timeout:
        #     warn("Parameter `serial_timeout` is deprecated. Use `timeout` in ms instead",
        #          FutureWarning)
        #     kwargs['timeout'] = serial_timeout
        super().__init__(resource_name,
                         asrl={
                             'timeout': 500,
                             'write_termination': "\r",
                             'read_termination': "\r\n",
                             'chunk_size': 256,

                         },
                         preprocess_reply=preprocess_reply,
                         **kwargs)
        self.address = address
        super().write("EOS D")
        super().write("STAT C N")
        # self._check_errors()

        if not isinstance(resource_name, NI_GPIB_232):
            # self.auto = auto
            self.eoi = eoi
        super().flush_read_buffer()

    class GPIB_STATUS(IntFlag):
        """Enum element for GIBP  status bit decoding

        """
        ERR = 32768   # Error detected
        TIMO = 13684  # Time out
        END = 8192  # EOI or EOS detected
        SRQI = 4096  # SRQ detected while CIC
        # 2048, 1024,  & 512 are reserved
        CMPL = 256  # Operation completed
        LOK = 128  # Lockout state
        REM = 64  # remote status
        CIC = 32   # CIC (Controller in Charge) status
        ATN = 16  # ATN asserted
        TACS = 8  # Talker active
        LACS = 4  # Listener active
        DTAS = 2  # Device triggeer active state
        SCAS = 1  # Device Clear active status

    class GPIB_ERR(IntFlag):
        """Enum element for GIBP  error bit decoding

        """
        ECMD = 17   # unregcognized command
        # 15-16 servered
        EBUS = 14  # Command bytes could not be sent
        # 12-13 servered
        ECAP = 11  # No capability for operation
        # 7-10 reserved
        EABO = 6  # IO aborted
        ESAC = 5  # Command requires GPIB-232CT-A to be system controller
        EARG = 4  # invaild argument(s)
        EADR = 3  # GPIBN-232CT-A not adressed correctly
        ENOL = 2  # Write detected, no listeners
        ECIC = 1  # Command requires GPIB-232CT-A to be CIC
        NGER = 0  # No error condition

    class SERIAL_ERR(IntFlag):
        """Enum element for serial  error bit decoding

        """
        EFRM = 4  # Serial port framing error
        EOFL = 3  # Serial port receive buffer overflow
        EORN = 2  # Serial port overrrun error
        EPAR = 1  # Serial port parity error
        NSER = 0  # No error condition

    def _check_errors(self):
        """
        TODO: fine docstring

        """
        if self.connection.bytes_in_buffer == 0:
            sleep(0.5)
            log.debug("Wait 1")
        log.debug(f"buf len: {self.connection.bytes_in_buffer}")
        ret_val = super().read_bytes(self.connection.bytes_in_buffer)
        if len(ret_val) < 12:
            log.debug(f"only {len(ret_val)} bytes received, content: {ret_val}")
        ret_val = ret_val.lstrip(b"\x00")            
        try:
             [g_s, g_e, s_e, c, dummy] = ret_val.split(b'\r\n')
        finally:
            pass
        gpib_stat = self.GPIB_STATUS(int(g_s))
        gpib_err = self.GPIB_ERR(int(g_e))
        ser_err = self.SERIAL_ERR(int(s_e))
        count = int(c)
        log.debug(f"{gpib_stat!a} || {gpib_err!a} || {ser_err!a} || count: {count} \r\n")
        if bool(gpib_stat & self.GPIB_STATUS.ERR) is True:
            log.warning(f"eror detected {self.GPIB_ERR(gpib_err)!a} {self.SERIAL_ERR(ser_err)!a}")
            # TODO: add exception

    def _assert_trigger(self):
        """
        Initiate a GPIB trigger-event
        """
        super().write(f"trg {self.address}")

    @property
    def eoi(self):
        """Control whether to assert the EOI signal with the last character
        of any command sent over GPIB port (bool).

        Some instruments require EOI signal to be
        asserted in order to properly detect the end of a command.
        """
        super().write("EOT")
        return bool(int(super().read()))

    @eoi.setter
    def eoi(self, value):
        super().write(f"EOT {int(value)}")

    @property
    def version(self):
        """Get the version string of the Prologix controller.
        """
        super().flush_read_buffer()
        super().write('id \r')
        sleep(0.02)
        return super().read_bytes(71).decode()

    # TODO: remove?
    def ask(self, command, kwargs):
        """ Ask the Prologix controller.

        .. deprecated:: 0.11
           Call `Instrument.ask` instead.

        :param command: SCPI command string to be sent to instrument
        """
        log.warn("`Adapter.ask` is deprecated, call `Instrument.ask` instead.", FutureWarning)
        super().flush_read_buffer()
        super().write(f"wrt {self.address} \n  {command}", **kwargs)
        sleep(0.0)
        return self.read()

    def clear(self):
        """
        Clear specified device.

        """
        super().write(f"clr  {self.address}")

    def send_command(self,  data: bytes):
        """
        Write GPIB command bytes on the bus.

        """
        super().write(f"cmd  #{len(data)}\n {data}")
        self._check_errors()

    def pass_control(self, primary_address: int, secondary_address: int):
        """
        Pass control to drevice with primary_address and optional secondary_address

        """
        super().write(f"pct  {primary_address}+{secondary_address}")

    def set_rsc(self):
        """
        set the NI-GPIB232ct to become the GPIB system controller

        """
        super().write("rsc  1")

    def send_ifc(self):
        """Pulse the interface clear line (IFC) for at least 200 microseconds.

        """
        super().write("sic 0.0002")

    def write(self, command, **kwargs):
        """Write a string command to the instrument appending `write_termination`.

        If the GPIB address in :attr:`.address` is defined, it is sent first.

        :param str command: Command string to be sent to the instrument
            (without termination).
        :param kwargs: Keyword arguments for the connection itself.
        """
        super().flush_read_buffer()
        super().write(f"wrt {self.address} \n  {command}", **kwargs)
        sleep(0.050)
        # bytes_written = super().read()
        # if bytes_written != len(command):
        #     log.warning("Supicious (bytes)")
        self._check_errors()
        super().flush_read_buffer()


    def write_bytes(self, command, **kwargs):
        """Write a string command to the instrument appending `write_termination`.

        If the GPIB address in :attr:`.address` is defined, it is sent first.

        :param str command: Command string to be sent to the instrument
            (without termination).
        :param kwargs: Keyword arguments for the connection itself.
        """
        super().flush_read_buffer()
        super().write(f"wrt {self.address} \n  {command}", **kwargs)
        sleep(0.050)
        # bytes_written = super().read()
        # if bytes_written != len(command):
        #     log.warning("Supicious (bytes)")
        self._check_errors()
        super().flush_read_buffer()

    def read(self,  **kwargs):
        """Read up to (excluding) `read_termination` or the whole read buffer.

        :param kwargs: Keyword arguments for the connection itself.
        :returns str: ASCII response of the instrument (excluding read_termination).
        """
        log.debug("reading")
        super().flush_read_buffer()
        super().write(f"rd #255 {self.address}")
        # super().write(f"rd {self.address}")
        sleep(0.050)
        ret_val = super().read()
        if ret_val != "0":
            ret_len = super().read()
            self._check_errors()
        return ret_val

    def read_bytes(self, count, **kwargs):
        """
        # TODO:    Fix this docstring

        """
        log.debug("read bytes..")
        if count == -1:
            count = self.chunk_size - 1
        super().flush_read_buffer()
        super().write(f"rd #{count} {self.address}")
        sleep(0.050)
        ret_val = super().read_bytes(count, kwargs)
        ret_len = super().read()
        self._check_errors()
        return ret_val

    def gpib(self, address, **kwargs):
        """ Return a NI_GPIB_232 object that references the GPIB
        address specified, while sharing the Serial connection with other
        calls of this function

        :param address: Integer GPIB address of the desired instrument
        :param kwargs: Arguments for the initialization
        :returns: NI_GPIB_232 for specific GPIB address
        """
        return NI_GPIB_232(self, address, **kwargs)

    # def _check_for_srq(self):
    #     # it was int(self.ask("++srq"))
    #     self.write("++srq")
    #     return int(self.read())

    # def wait_for_srq(self, timeout=25, delay=0.1):
    #     """ Blocks until a SRQ, and leaves the bit high

    #     :param timeout: Timeout duration in seconds.
    #     :param delay: Time delay between checking SRQ in seconds.
    #     :raises TimeoutError: "Waiting for SRQ timed out."
    #     """
    #     stop = time.perf_counter() + timeout
    #     while self._check_for_srq() != 1:
    #         if time.perf_counter() > stop:
    #             raise TimeoutError("Waiting for SRQ timed out.")
    #         time.sleep(delay)

    def __repr__(self):
        if self.address is not None:
            return (f"<NI_GPIB_232(resource_name='{self.connection.resource_name}', "
                    f"address={self.address:d})>")
        else:
            return f"<NI_GPIB_232(resource_name='{self.connection.resource_name}')>"
