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
from enum import IntFlag, Flag
import time
from pymeasure.adapters import VISAAdapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class NI_GPIB_232(VISAAdapter):
    """Encapsulates the additional commands necessary
       to communicate over a National Instruments GPIB-232CT Adapter,
       using the :class:`VISAAdapter`.

       Each Adapter is constructed based on a connection to the device
       itself and the GPIB address of the instrument to be communicated to.
       Connection sharing is achieved by using the :meth:`.gpib`
       method to spawn new NI_GPIB_232s for different GPIB addresses.

       :param resource_name: A
        `VISA resource string
        <https://pyvisa.readthedocs.io/en/latest/introduction/names.html>`
        that identifies the connection to the  device itself, for example
        "ASRL5" for the 5th COM port.
       :param address: Integer GPIB address of the desired instrument.
       :param eoi: Enable or disable EOI assertion.
       :param kwargs: Key-word arguments if constructing a new serial object

       :ivar address: Integer GPIB address of the desired instrument.

       Usage example:

       .. code::

         adapter = NI_GPIB_232("ASRL5::INSTR", 7)
         sourcemeter = Keithley2400(adapter)  # at GPIB address 7
         # generate another instance with a different GPIB address:
         adapter2 = adapter.gpib(9)
         multimeter = Keithley2000(adapter2)  # at GPIB address 9

       TODO:
         add specifics on the RS232 parameter settings

    """

    def __init__(self, resource_name, address=None, serial_timeout=1000, eoi=True, **kwargs):
        super().__init__(
            resource_name,
            asrl={
                "timeout": serial_timeout,
                "write_termination": "\r",
                "read_termination": "\r\n",
                "flow_control": 2,
                "chunk_size": 256,
            },
            **kwargs,
        )
        self.address = address
        super().write("EOS D")
        super().write("STAT")
        self._check_errors()

        if not isinstance(resource_name, NI_GPIB_232):
            self.eoi = eoi
        super().flush_read_buffer()

    class GPIBStatus(IntFlag):
        """Enum element for GIBP  status bit decoding"""

        ERR = 32768  # Error detected
        TIMO = 16384  # Time out
        END = 8192  # EOI or EOS detected
        SRQI = 4096  # SRQ detected while CIC
        # 2048, 1024,  & 512 are reserved
        CMPL = 256  # Operation completed
        LOK = 128  # Lockout state
        REM = 64  # remote status
        CIC = 32  # CIC (Controller in Charge) status
        ATN = 16  # ATN asserted
        TACS = 8  # Talker active
        LACS = 4  # Listener active
        DTAS = 2  # Device triggeer active state
        SCAS = 1  # Device Clear active status

    class GPIBError(Flag):
        """Enum element for GIBP  error bit decoding"""

        ECMD = 17  # unregcognized command
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

    class SERIALError(Flag):
        """Enum element for serial  error bit decoding"""

        EFRM = 4  # Serial port framing error
        EOFL = 3  # Serial port receive buffer overflow
        EORN = 2  # Serial port overrrun error
        EPAR = 1  # Serial port parity error
        NSER = 0  # No error condition

    def _check_errors(self):
        """
        Method to decode the status data reported from the device.

        """
        super().write("stat n")
        if self.connection.bytes_in_buffer == 0:
            time.sleep(0.125)
        ret_val = super().read_bytes(self.connection.bytes_in_buffer)
        if len(ret_val) <= 3:
            log.warning(f"only {len(ret_val)} bytes received, content: {ret_val}")
            return
        if len(ret_val) < 12:
            log.warning(f"only {len(ret_val)} bytes received, content: {ret_val}")
        ret_val = ret_val.lstrip(b"\x00")
        try:
            [g_s, g_e, s_e, cnt_raw] = ret_val.splitlines()
            gpib_stat = self.GPIBStatus(int(g_s))
            gpib_err = self.GPIBError(int(g_e))
            ser_err = self.SERIALError(int(s_e))
            count = int(cnt_raw)
            log.debug(f"count {count}")
        except ValueError:
            g_s = ret_val[: ret_val.find(b"\r")]
            gpib_stat = self.GPIBStatus(int(g_s))
            log.warning(f" ACHTUNG! {gpib_stat!a}  \r\n")
        # Error handling
        if bool(gpib_stat & self.GPIBStatus.ERR) is True:
            log.critical(f"Error {self.GPIBError(gpib_err)!a} {self.SERIALError(ser_err)!a}")

    def assert_trigger(self):
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

    # TODO: verification needed
    @property
    def time_out(self):
        """Control control the GPIB timeout.
        Valid value range 0.0001 to 3600s
        """
        super().write("tmo")
        ret_val = super().read().split(",")
        return float(ret_val[0])

    @time_out.setter
    def time_out(self, value):
        if value >= 0.0001:
            if value < 1:
                super().write(f"tmo {value:.4f}")
            elif value <= 3600:
                super().write(f"tmo {int(value)}")
            else:
                raise ValueError(f"timeout value out of range! {value}")

    @property
    def version(self):
        """Get the version string of the NI GPIB-232-CT."""
        super().flush_read_buffer()
        super().write("id \r")
        time.sleep(0.02)
        return super().read_bytes(71).decode()

    def clear(self):
        """
        Clear specified device.

        """
        super().write(f"clr  {self.address}")

    def send_command(self, data: bytes):
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
        """Pulse the interface clear line (IFC) for at least 200 microseconds."""
        super().write("sic 0.0002")

    def write(self, command, **kwargs):
        """Write a string to the instrument appending `write_termination`.

        :param str command: Command string to be sent to the instrument
            (without termination).
        :param kwargs: Keyword arguments for the connection itself.
        """
        super().flush_read_buffer()
        super().write(f"wrt {self.address} \n  {command}", **kwargs)
        time.sleep(0.050)
        self._check_errors()
        super().flush_read_buffer()

    def write_bytes(self, content, **kwargs):
        """Write byte to the instrument appending `write_termination`.

        :param str content: string to be sent to the instrument (without termination).
        :param kwargs: Keyword arguments for the connection itself.
        """
        super().flush_read_buffer()
        super().write(f"wrt {self.address} \n  {content}", **kwargs)
        time.sleep(0.050)
        self._check_errors()
        super().flush_read_buffer()

    def read(self, **kwargs):
        """Read up to (excluding) `read_termination` or the whole read buffer.

        :param kwargs: Keyword arguments for the connection itself.
        :returns str: ASCII response of the instrument (excluding read_termination).
        """
        # log.debug("reading")
        super().flush_read_buffer()
        super().write(f"rd #255 {self.address}")
        time.sleep(0.050)
        ret_val = super().read()
        if ret_val != "0":
            ret_len = super().read()
            log.debug(f"length of read {ret_len}")
            self._check_errors()
        return ret_val

    def read_bytes(self, count, **kwargs):
        """Read bytes from the instrument.

        :param count:  number of bytes to be read.
        :param kwargs: Keyword arguments for the connection itself.
        :returns bytes: response of the instrument.
        """
        # log.debug("read bytes..")
        if count == -1:
            count = self.connection.chunk_size - 1
        super().flush_read_buffer()
        super().write(f"rd #{count} {self.address}")
        time.sleep(0.050)
        ret_val = super().read_bytes(count, kwargs)
        time.sleep(0.050)
        ret_len = super().read()
        log.debug(f"length of bytes read {ret_len}")
        self._check_errors()
        return ret_val

    def gpib(self, address, **kwargs):
        """Return a NI_GPIB_232 object that references the GPIB
        address specified, while sharing the Serial connection with other
        calls of this function

        :param address: Integer GPIB address of the desired instrument
        :param kwargs: Arguments for the initialization
        :returns: NI_GPIB_232 for specific GPIB address
        """
        return NI_GPIB_232(self, address, **kwargs)

    def wait_for_srq(self, timeout=20, delay=0.1):
        """Blocks until a SRQ, and leaves the bit high

        :param timeout: Timeout duration in seconds.
        :raises TimeoutError: "Waiting for SRQ timed out."
        """
        stop = time.perf_counter() + timeout
        while time.perf_counter() < stop:
            super().write(f"rsp {self.address}")
            if self.connection.bytes_in_buffer == 0:
                time.sleep(delay)
            if self.connection.bytes_in_buffer >= 1:
                ret_val = super().read_bytes(self.connection.bytes_in_buffer)
                if int(ret_val) > 0:
                    return int(ret_val)
                if int(ret_val) == -1:
                    raise TimeoutError(f"Waiting for SRQ timed out after {timeout}")

    def __repr__(self):
        if self.address is not None:
            return (
                f"<NI_GPIB_232(resource_name='{self.connection.resource_name}', "
                f"address={self.address:d})>"
            )
        return f"<NI_GPIB_232(resource_name='{self.connection.resource_name}')>"
