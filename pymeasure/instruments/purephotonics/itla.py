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

"""Generic driver for tunable lasers following the OIF-ITLA-MSA register protocol.

The communication follows the OIF Integrable Tunable Laser Assembly Multi Source Agreement
(OIF-ITLA-MSA-01.3): every exchange consists of a 4 byte packet sent to the module and a
4 byte packet returned by the module. Strings and arrays are transferred with the
"automatic extended addressing" (AEA) scheme.
"""

import logging
import threading
import time
from collections.abc import Sequence
from enum import IntEnum, IntFlag

from pymeasure.instruments import AdapterType, Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ITLAStatus(IntEnum):
    """Status field of a packet returned by an ITLA module (bits 25:24)."""

    OK = 0  #: Command executed.
    XE = 1  #: Execution error, the error code is available in the NOP register.
    AEA = 2  #: Automatic extended addressing, the data contain the number of bytes.
    CP = 3  #: Command pending, poll the NOP register until finished.


class ITLAError(IntEnum):
    """Error codes of the NOP register error field (OIF-ITLA-MSA 9.4.1)."""

    OK = 0x00  #: No errors.
    RNI = 0x01  #: Register not implemented.
    RNW = 0x02  #: Register not writeable.
    RVE = 0x03  #: Register value range error.
    CIP = 0x04  #: Command ignored due to pending operation.
    CII = 0x05  #: Command ignored while module is initializing or warming up.
    ERE = 0x06  #: Extended address range error.
    ERO = 0x07  #: Extended address is read only.
    EXF = 0x08  #: Execution general failure.
    CIE = 0x09  #: Command ignored while the optical output is enabled.
    IVC = 0x0A  #: Invalid configuration, command ignored.
    VSE = 0x0F  #: Vendor specific error.


class ITLAExecutionError(Exception):
    """The module answered with an execution error (XE status).

    :param register: Register of the failed command.
    :param error: Error code read from the NOP register.
    """

    def __init__(self, register: int, error: int):
        self.register = register
        try:
            self.error = ITLAError(error)
            text = self.error.name
        except ValueError:
            self.error = error
            text = "reserved error code"
        super().__init__(f"Execution error for register 0x{register:02X}: {text} ({error}).")


class FatalStatus(IntFlag):
    """Flags of the fatal status register StatusF (0x20).

    Bits 15 to 8 show the current condition, bits 7 to 0 are latched.
    """

    FPWRL = 1 << 0  #: Latched fatal output power condition.
    FTHERML = 1 << 1  #: Latched fatal thermal condition.
    FFREQL = 1 << 2  #: Latched fatal frequency condition.
    FVSFL = 1 << 3  #: Latched fatal vendor specific condition.
    CRL = 1 << 4  #: Communication reset occurred.
    MRL = 1 << 5  #: Module reset occurred.
    CEL = 1 << 6  #: Communication error occurred.
    XEL = 1 << 7  #: Execution error occurred.
    FPWR = 1 << 8  #: Fatal output power condition.
    FTHERM = 1 << 9  #: Fatal thermal condition.
    FFREQ = 1 << 10  #: Fatal frequency condition.
    FVSF = 1 << 11  #: Fatal vendor specific condition.
    DIS = 1 << 12  #: Output disabled by hardware pin.
    FATAL = 1 << 13  #: Fatal condition asserted.
    ALM = 1 << 14  #: Alarm asserted.
    SRQ = 1 << 15  #: Service request asserted.


class WarningStatus(IntFlag):
    """Flags of the warning status register StatusW (0x21).

    Bits 15 to 8 show the current condition, bits 7 to 0 are latched.
    """

    WPWRL = 1 << 0  #: Latched output power warning.
    WTHERML = 1 << 1  #: Latched thermal warning.
    WFREQL = 1 << 2  #: Latched frequency warning (not yet on the target frequency).
    WVSFL = 1 << 3  #: Latched vendor specific warning.
    CRL = 1 << 4  #: Communication reset occurred.
    MRL = 1 << 5  #: Module reset occurred.
    CEL = 1 << 6  #: Communication error occurred.
    XEL = 1 << 7  #: Execution error occurred.
    WPWR = 1 << 8  #: Output power warning.
    WTHERM = 1 << 9  #: Thermal warning.
    WFREQ = 1 << 10  #: Frequency warning (not yet on the target frequency).
    WVSF = 1 << 11  #: Vendor specific warning.
    DIS = 1 << 12  #: Output disabled by hardware pin.
    FATAL = 1 << 13  #: Fatal condition asserted.
    ALM = 1 << 14  #: Alarm asserted.
    SRQ = 1 << 15  #: Service request asserted.


def checksum(packet: Sequence[int]) -> int:
    """Calculate the 4 bit BIP-4 checksum of a 4 byte ITLA packet.

    The checksum bits (upper nibble of the first byte) are ignored.
    """
    bip8 = (packet[0] & 0x0F) ^ packet[1] ^ packet[2] ^ packet[3]
    return ((bip8 & 0xF0) >> 4) ^ (bip8 & 0x0F)


def _signed(value: float) -> int:
    """Interpret an unsigned 16 bit register value as signed short."""
    value = int(value)
    return value - 0x10000 if value >= 0x8000 else value


class ITLA(Instrument):
    """Generic tunable laser following the OIF-ITLA-MSA register protocol.

    The protocol is binary. :meth:`write` understands a small command language which is used by
    the properties:

    - ``"R,<register>"`` reads a register. AEA answers are returned as text (up to the first NUL).
    - ``"RA,<register>"`` reads an AEA register as an array of signed shorts.
    - ``"W,<register>,<value>"`` writes a register; negative values are sent as signed short.

    ``<register>`` may be given as decimal or hexadecimal (``0x31``) number. Each command is a
    complete transaction (packet sent and answer received). The answer is buffered and returned by
    :meth:`read`. An execution error of the module raises an :class:`ITLAExecutionError`.

    Many settings (e.g. :attr:`emission_enabled`, :attr:`channel`) start a pending operation in the
    module. Call :meth:`wait_until_ready` before sending further setting commands, otherwise the
    module may refuse them with a :attr:`ITLAError.CIP` error.

    :param adapter: Adapter or resource name, e.g. ``"ASRL/dev/ttyUSB0::INSTR"`` or ``"COM3"``.
    :param name: Name of the instrument.
    :param baud_rate: Baud rate of the serial interface (9600 after power on).
    :param timeout: Communication timeout in ms.
    :param kwargs: Further keyword arguments for the adapter.
    """

    _AEA_REGISTER = 0x0B  # AEA-EAR: read AEA data, two bytes at a time

    def __init__(
        self,
        adapter: AdapterType,
        name: str = "OIF ITLA",
        baud_rate: int = 9600,
        timeout: int = 1000,
        **kwargs,
    ):
        super().__init__(
            adapter,
            name,
            asrl={"baud_rate": baud_rate, **kwargs.pop("asrl", {})},
            timeout=timeout,
            **kwargs,
        )
        self._lock = threading.RLock()
        self._response = ""
        self._last_reply = b""
        self._host_baud_rate = baud_rate

    # Communication
    @staticmethod
    def _packet(register: int, data: int = 0, write: bool = False) -> bytes:
        """Create a 4 byte packet to send to the module."""
        if not -0x8000 <= data <= 0xFFFF:
            raise ValueError(f"Data value {data} does not fit into 16 bits.")
        data &= 0xFFFF
        packet = [int(write), register & 0xFF, data >> 8, data & 0xFF]
        packet[0] |= checksum(packet) << 4
        return bytes(packet)

    def _transceive_once(self, packet: bytes) -> bytes | None:
        """Send a packet and return the answer or None, if the answer is invalid.

        An answer is invalid if it is incomplete, has a wrong checksum or belongs to another
        register (lost framing).
        """
        self.write_bytes(packet)
        try:
            reply = self.read_bytes(4)
        except Exception:  # noqa: BLE001  timeout exceptions depend on the adapter
            reply = b""
        self._last_reply = reply
        if len(reply) != 4 or checksum(reply) != reply[0] >> 4 or reply[1] != packet[1]:
            return None
        if reply[0] & 0x08:
            log.warning(
                "%s: module reports a communication error (CE) of an earlier packet.", self.name
            )
        return reply

    def _resynchronize(self) -> None:
        """Restore the 4 byte framing after a lost or corrupted packet.

        Single zero bytes are sent until the module answers, which completes the packet in the
        module's buffer. Afterwards a NOP read verifies the communication.
        """
        log.info("%s: resynchronizing communication.", self.name)
        self.adapter.flush_read_buffer()
        for _ in range(8):
            self.write_bytes(b"\x00")
            try:
                got = self.read_bytes(1)
            except Exception:  # noqa: BLE001
                got = b""
            if got:
                time.sleep(0.05)
                self.adapter.flush_read_buffer()
                if self._transceive_once(self._packet(0x00)) is not None:
                    return
        raise ConnectionError(f"{self.name}: could not resynchronize communication.")

    def _transceive(self, register: int, data: int = 0, write: bool = False) -> tuple[int, int]:
        """Execute one command and return status and data of the answer.

        A read command is repeated once after resynchronization, if the answer is invalid.
        """
        packet = self._packet(register, data, write)
        reply = self._transceive_once(packet)
        if reply is None:
            self._resynchronize()
            if write:
                raise ConnectionError(
                    f"{self.name}: invalid answer to writing register 0x{register:02X}. "
                    "Communication has been resynchronized, the setting may not have been applied."
                )
            reply = self._transceive_once(packet)
            if reply is None:
                raise ConnectionError(
                    f"{self.name}: no valid answer for register 0x{register:02X}, "
                    f"received {self._last_reply.hex(' ') or 'nothing'}."
                )
        status = reply[0] & 0x03
        value = int.from_bytes(reply[2:4], "big")
        if status == ITLAStatus.XE:
            _, nop = self._transceive(0x00)
            raise ITLAExecutionError(register, nop & 0x0F)
        return status, value

    def _read_aea(self, length: int) -> bytes:
        """Read `length` bytes of extended address data."""
        data = b""
        while len(data) < length:
            _, value = self._transceive(self._AEA_REGISTER)
            data += value.to_bytes(2, "big")
        return data[:length]

    def write(self, command: str, **kwargs) -> None:
        """Execute a command, see the class documentation for the syntax.

        The answer is stored and can be retrieved with :meth:`read`.
        """
        function, register, *values = command.split(",")
        function = function.strip().upper()
        register = int(register, 0)
        with self._lock:
            if function == "W":
                if len(values) != 1:
                    raise ValueError(f"Write command '{command}' needs exactly one value.")
                _, value = self._transceive(register, int(values[0], 0), write=True)
                self._response = str(value)
            elif function in ("R", "RA"):
                status, value = self._transceive(register)
                if status == ITLAStatus.AEA:
                    data = self._read_aea(value)
                    if function == "RA":
                        self._response = ",".join(
                            str(int.from_bytes(data[i:i + 2], "big", signed=True))
                            for i in range(0, len(data) - 1, 2)
                        )
                    else:
                        # strings are null terminated, some contain further data after the NUL
                        text = data.split(b"\x00", 1)[0]
                        self._response = text.decode("ascii", errors="replace")
                else:
                    self._response = str(value)
            else:
                raise ValueError(f"Unknown command '{command}'.")

    def read(self, **kwargs) -> str:
        """Return the answer of the last command."""
        response, self._response = self._response, ""
        return response

    def ask(self, command: str, query_delay: float | None = None) -> str:
        """Execute a command and return the answer (thread safe)."""
        with self._lock:
            return super().ask(command, query_delay)

    def read_register(self, register: int, signed: bool = False) -> int:
        """Read a 16 bit register.

        :param register: Register number.
        :param signed: Interpret the value as signed short.
        """
        value = int(self.ask(f"R,{register}"))
        return _signed(value) if signed else value

    def write_register(self, register: int, value: int) -> int:
        """Write a 16 bit register and return the echoed value."""
        return int(self.ask(f"W,{register},{int(value)}"))

    # Module status
    nop = Instrument.measurement(
        "R,0x00",
        """Get the raw NOP register: pending operations (bits 15:8), module ready (bit 4) and
        error code of the last command (bits 3:0) (int).""",
        cast=int,
    )

    @property
    def pending(self) -> int:
        """Get the pending operation flags (int); 0 if no operation is pending."""
        return self.nop >> 8

    @property
    def module_ready(self) -> bool:
        """Get whether the module is ready to enable its output (bool)."""
        return bool(self.nop & 0x10)

    def wait_until_ready(self, timeout: float = 60, interval: float = 0.1) -> None:
        """Wait until no operation (e.g. tuning or enabling the output) is pending.

        :param timeout: Maximum waiting time in s.
        :param interval: Polling interval in s.
        :raises TimeoutError: if an operation is still pending after `timeout`.
        """
        stop = time.monotonic() + timeout
        while self.pending:
            if time.monotonic() >= stop:
                raise TimeoutError(f"{self.name}: operation still pending after {timeout} s.")
            time.sleep(interval)

    # Baud rate
    BAUD_RATES = (9600, 19200, 38400, 57600, 115200)  #: Baud rates of the MSA (IOCap codes 0-4).

    @property
    def baud_rate(self) -> int:
        """Get the current baud rate of the module (int), see :meth:`set_baud_rate`."""
        return self.BAUD_RATES[(self.read_register(0x0D) >> 4) & 0x0F]

    @property
    def max_baud_rate(self) -> int:
        """Get the maximum baud rate supported by the module (int)."""
        return self.BAUD_RATES[self.read_register(0x0D) & 0x0F]

    def _set_host_baud_rate(self, baud_rate: int) -> None:
        """Change the baud rate of the serial port of the host."""
        connection = self.adapter.connection
        if type(connection).__module__.startswith("serial"):  # pyserial (SerialAdapter)
            connection.baudrate = baud_rate
        else:  # pyvisa (VISAAdapter)
            connection.baud_rate = baud_rate
        self._host_baud_rate = baud_rate

    def set_baud_rate(self, baud_rate: int) -> None:
        """Change the baud rate of the module and of the serial port of the host.

        A higher baud rate reduces the time per command. With FTDI USB-serial converters, the
        latency timer (default 16 ms) also limits the command rate. The baud rate can be changed
        while the output is enabled.
        The setting is volatile: after a power cycle, a hardware reset or (by default) a pulse on
        the MS line, the module communicates at 9600 Bd again. If the module is still set to
        another baud rate when connecting again, pass that value as ``baud_rate`` to the
        constructor.

        :param baud_rate: New baud rate, one of :attr:`BAUD_RATES` up to :attr:`max_baud_rate`.
        :raises ConnectionError: if the communication fails at the new baud rate.
        """
        strict_discrete_set(baud_rate, self.BAUD_RATES)
        code = self.BAUD_RATES.index(baud_rate)
        with self._lock:
            iocap = self.read_register(0x0D)
            if code > iocap & 0x0F:
                raise ValueError(
                    f"Baud rate {baud_rate} exceeds the maximum baud rate "
                    f"{self.BAUD_RATES[iocap & 0x0F]} of the module."
                )
            old_baud_rate = self._host_baud_rate
            # The module answers at the old baud rate and switches afterwards.
            self.write_register(0x0D, (iocap & 0xFF0F) | code << 4)
            time.sleep(0.05)
            self._set_host_baud_rate(baud_rate)
            self.adapter.flush_read_buffer()
            try:
                self.read_register(0x00)
            except ConnectionError:
                self._set_host_baud_rate(old_baud_rate)
                self.adapter.flush_read_buffer()
                try:
                    self.read_register(0x00)
                except ConnectionError:
                    raise ConnectionError(
                        f"{self.name}: communication lost after changing the baud rate to "
                        f"{baud_rate}. Power cycle the module to restore 9600 Bd."
                    ) from None
                raise ConnectionError(
                    f"{self.name}: the module did not change its baud rate to {baud_rate}."
                ) from None

    status_fatal = Instrument.measurement(
        "R,0x20",
        """Get the fatal status flags (:class:`FatalStatus`).""",
        get_process=lambda v: FatalStatus(int(v)),
    )

    status_warning = Instrument.measurement(
        "R,0x21",
        """Get the warning status flags (:class:`WarningStatus`).""",
        get_process=lambda v: WarningStatus(int(v)),
    )

    def clear_status(self) -> None:
        """Clear the latched flags of the fatal and warning status registers."""
        self.write_register(0x20, 0x00FF)
        self.write_register(0x21, 0x00FF)

    # Identification
    device_type = Instrument.measurement(
        "R,0x01", """Get the device type (str).""", cast=str, separator="\n"
    )

    manufacturer = Instrument.measurement(
        "R,0x02", """Get the manufacturer (str).""", cast=str, separator="\n"
    )

    model = Instrument.measurement("R,0x03", """Get the model (str).""", cast=str, separator="\n")

    serial_number = Instrument.measurement(
        "R,0x04", """Get the serial number (str).""", cast=str, separator="\n"
    )

    manufacturing_date = Instrument.measurement(
        "R,0x05", """Get the manufacturing date (str).""", cast=str, separator="\n"
    )

    release = Instrument.measurement(
        "R,0x06",
        """Get the release information, e.g. firmware version (str).""",
        cast=str,
        separator="\n",
    )

    @property
    def id(self) -> str:
        """Get the identification: manufacturer, model, serial number and release (str)."""
        return f"{self.manufacturer},{self.model},{self.serial_number},{self.release}"

    # Laser control
    emission_enabled = Instrument.control(
        "R,0x32",
        "W,0x32,%d",
        """Control whether the optical output is enabled (bool).

        Enabling takes up to a minute; use :meth:`wait_until_ready` afterwards.""",
        validator=strict_discrete_set,
        values=(True, False),
        get_process=lambda v: bool(int(v) & 0x08),
        set_process=lambda v: 0x08 if v else 0,
    )

    def reset(self, hard: bool = False) -> None:
        """Reset the module.

        :param hard: Do a hardware module reset instead of a soft reset of the communication
            interface. A hard reset disables the optical output.
        """
        self.write_register(0x32, 0x01 if hard else 0x02)

    channel = Instrument.control(
        "R,0x30",
        "W,0x30,%d",
        """Control the channel number (int, starting at 1).

        The frequency is
        :attr:`first_channel_frequency` + (channel - 1) * :attr:`grid_spacing`.""",
        validator=strict_range,
        values=(1, 0xFFFF),
        cast=int,
    )

    @property
    def power_setpoint(self) -> float:
        """Control the optical output power setpoint in dBm (float, resolution 0.01 dBm).

        The value is checked against :attr:`power_min` and :attr:`power_max` of the module
        before sending, as some firmware versions accept any value.
        A power change with enabled output does not set a pending flag, so
        :meth:`wait_until_ready` returns immediately; the output power (:attr:`power`) settles
        within a few seconds."""
        return self.read_register(0x31, signed=True) / 100

    @power_setpoint.setter
    def power_setpoint(self, power: float) -> None:
        strict_range(power, (self.power_min, self.power_max))
        self.write_register(0x31, round(power * 100))

    power = Instrument.measurement(
        "R,0x42",
        """Measure the optical output power in dBm (float).

        A disabled output reads about -327.68 dBm.""",
        get_process=lambda v: _signed(v) / 100,
    )

    grid_spacing = Instrument.control(
        "R,0x34",
        "W,0x34,%d",
        """Control the channel grid spacing in Hz (float, resolution 100 MHz).""",
        get_process=lambda v: _signed(v) * 1e8,
        set_process=lambda v: round(v / 1e8),
    )

    def _get_frequency(self, register_thz: int) -> float:
        thz = self.read_register(register_thz)
        ghz_10 = self.read_register(register_thz + 1)
        return thz * 1e12 + ghz_10 * 1e8

    def _set_frequency(self, register_thz: int, frequency: float) -> None:
        ghz_10 = round(frequency / 1e8)
        thz, ghz_10 = divmod(ghz_10, 10_000)
        self.write_register(register_thz, thz)
        self.write_register(register_thz + 1, ghz_10)

    @property
    def first_channel_frequency(self) -> float:
        """Control the frequency of channel 1 in Hz (float, resolution 100 MHz).

        Can be set only with disabled output."""
        return self._get_frequency(0x35)

    @first_channel_frequency.setter
    def first_channel_frequency(self, frequency: float) -> None:
        strict_range(frequency, (self.frequency_min, self.frequency_max))
        self._set_frequency(0x35, frequency)

    @property
    def frequency(self) -> float:
        """Measure the laser frequency in Hz, including fine tuning (float, resolution 100 MHz)."""
        return self._get_frequency(0x40)

    temperature = Instrument.measurement(
        "R,0x43",
        """Measure the laser temperature in °C (float).""",
        get_process=lambda v: _signed(v) / 100,
    )

    @property
    def fine_tune_frequency(self) -> float:
        """Control the fine tuning frequency offset in Hz (float, resolution 1 MHz).

        The value is checked against +/- :attr:`fine_tune_range` of the module before sending.
        Tuning can take several seconds, use :meth:`wait_until_ready`."""
        return self.read_register(0x62, signed=True) * 1e6

    @fine_tune_frequency.setter
    def fine_tune_frequency(self, frequency: float) -> None:
        limit = self.fine_tune_range
        strict_range(frequency, (-limit, limit))
        self.write_register(0x62, round(frequency / 1e6))

    # Module capabilities
    fine_tune_range = Instrument.measurement(
        "R,0x4F",
        """Get the fine tuning range in Hz (float).""",
        get_process=lambda v: v * 1e6,
    )

    power_min = Instrument.measurement(
        "R,0x50",
        """Get the minimum power setpoint in dBm (float).""",
        get_process=lambda v: _signed(v) / 100,
    )

    power_max = Instrument.measurement(
        "R,0x51",
        """Get the maximum power setpoint in dBm (float).""",
        get_process=lambda v: _signed(v) / 100,
    )

    @property
    def frequency_min(self) -> float:
        """Get the lowest laser frequency in Hz (float)."""
        return self._get_frequency(0x52)

    @property
    def frequency_max(self) -> float:
        """Get the highest laser frequency in Hz (float)."""
        return self._get_frequency(0x54)

    grid_spacing_min = Instrument.measurement(
        "R,0x56",
        """Get the minimum grid spacing in Hz (float).""",
        get_process=lambda v: _signed(v) * 1e8,
    )

    # Module monitors
    currents = Instrument.measurement(
        "RA,0x57",
        """Measure the module currents in A (list of floats).

        The first value is usually the TEC current, the second the diode current.""",
        get_process_list=lambda v: [i / 10_000 for i in v],
    )

    temperatures = Instrument.measurement(
        "RA,0x58",
        """Measure the module temperatures in °C (list of floats).

        The first value is usually the diode temperature, the second the case temperature.""",
        get_process_list=lambda v: [i / 100 for i in v],
    )

    age = Instrument.measurement(
        "R,0x61",
        """Get the laser age in percent of its end of life (int).""",
        cast=int,
    )
