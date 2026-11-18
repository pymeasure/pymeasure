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
import struct
from typing import cast

from pymeasure.instruments import AdapterType, Channel, Instrument
from pymeasure.instruments.validators import strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def crc16(data: bytes | bytearray) -> bytes:
    """Calculate the Modbus RTU CRC16 of `data`, returned low byte first."""
    crc = 0xFFFF
    for octet in data:
        crc ^= octet
        for _ in range(8):
            lsb = crc & 0x1
            crc >>= 1
            if lsb:
                crc ^= 0xA001
    return crc.to_bytes(2, "little")


READ_REGISTERS = 0x03
WRITE_REGISTERS = 0x10

MODBUS_ERRORS = {
    0x01: "Illegal function.",
    0x02: "Illegal data address.",
    0x03: "Illegal data value.",
    0x04: "Slave device failure.",
}

#: Offset of the IEEE region, where each parameter uses two 16-bit registers.
IEEE_REGION = 0x8000


def int_control(address: int, docs: str, **kwargs) -> property:
    """Create a property for a 16-bit integer parameter at Modbus `address`."""
    return Instrument.control(
        f"I,{address}", f"I,{address},%d", docs, check_set_errors=True, **kwargs
    )


def float_control(address: int, docs: str, **kwargs) -> property:
    """Create a property for a floating point parameter at Modbus `address`."""
    return Instrument.control(
        f"F,{address}", f"F,{address},%s", docs, check_set_errors=True, **kwargs
    )


def time_control(address: int, docs: str, **kwargs) -> property:
    """Create a property for a time parameter (in s) at Modbus `address`."""
    return Instrument.control(
        f"T,{address}", f"T,{address},%s", docs, check_set_errors=True, **kwargs
    )


def enum_control(address: int, docs: str, values: dict, **kwargs) -> property:
    """Create a property for an enumerated 16-bit parameter at Modbus `address`."""
    return int_control(
        address,
        docs,
        validator=strict_discrete_set,
        values=values,
        map_values=True,
        **kwargs,
    )


class OffsetChannel(Channel):
    """Channel whose parameters live at an address offset from the parent ones.

    Commands of children have the form ``"<kind>,<relative address>[,<value>]"``,
    the absolute address is obtained by adding :meth:`offset`.
    """

    @property
    def number(self) -> int:
        """Get the channel number, i.e. its integer id."""
        return cast(int, self.id)

    def offset(self) -> int:
        """Return the address offset of this channel."""
        raise NotImplementedError("Implement it in a subclass.")

    def insert_id(self, command: str) -> str:
        """Shift the register address of `command` by the channel offset."""
        kind, address, *value = command.split(",")
        return ",".join([kind, str(int(address) + self.offset()), *value])


class EurothermBase(Instrument):
    """Base class for Eurotherm controllers communicating via Modbus.

    Eurotherm 2000 and 3000 series controllers expose their parameters as Modbus
    registers. Integer and enumerated parameters are read from the 16-bit registers
    at their documented address. Floating point and time parameters are read from
    the IEEE region (address ``0x8000 + 2 * address``), which gives full resolution
    floats and 32-bit times. Times are exchanged in seconds, regardless of the display
    units set on the controller.

    Modbus RTU is used over serial links, Modbus TCP over Ethernet.

    Commands passed to :meth:`write` have the form ``"<kind>,<address>[,<value>]"``,
    where kind is ``I`` (16-bit integer), ``F`` (float) or ``T`` (time in s).
    Without value, the parameter is read and :meth:`read` returns its value.

    The selection of parameters follows the drivers of the
    `nupylab <https://github.com/hailegroup/nupylab>`__ project, the PID parameters
    follow the `adelaisbruel/pymodaq_plugins_eurotherm
    <https://github.com/adelaisbruel/pymodaq_plugins_eurotherm>`__ plugin.

    :param adapter: The adapter or resource string, e.g. ``"ASRL3::INSTR"`` for a serial
        link or ``"TCPIP::192.168.1.10::502::SOCKET"`` for Modbus TCP.
    :param name: The name of the instrument.
    :param address: The Modbus address (unit identifier) of the controller (1 to 254).
    :param baud_rate: The serial baud rate, as configured on the controller.
    :param timeout: The communication timeout in ms.
    :param tcp: Whether to use Modbus TCP instead of Modbus RTU. By default, Modbus TCP
        is used if `adapter` is a ``TCPIP`` resource string.
    :param \\**kwargs: Keyword arguments passed to the adapter.
    """

    def __init__(
        self,
        adapter: AdapterType,
        name: str = "Eurotherm controller",
        address: int = 1,
        baud_rate: int = 9600,
        timeout: int = 1000,
        tcp: bool | None = None,
        **kwargs,
    ):
        super().__init__(
            adapter,
            name,
            timeout=timeout,
            asrl={"baud_rate": baud_rate},
            **kwargs,
        )
        self.address = address
        if tcp is None:
            tcp = isinstance(adapter, str) and adapter.upper().startswith("TCPIP")
        self.tcp = tcp
        self._kind = "I"
        self._transaction = 0

    def write(self, command: str, **kwargs) -> None:
        """Send a Modbus request for a parameter.

        :param command: ``"<kind>,<address>"`` to read the parameter, or
            ``"<kind>,<address>,<value>"`` to write it.
            Kind is ``I`` (16-bit integer), ``F`` (float) or ``T`` (time in s).
        """
        kind, address, *value = command.split(",")
        if kind not in ("I", "F", "T"):
            raise ValueError(f"Invalid parameter kind '{kind}'.")
        address = int(address)
        count = 1
        if kind != "I":
            address = IEEE_REGION + 2 * address
            count = 2
        self._kind = kind
        pdu = bytearray([WRITE_REGISTERS if value else READ_REGISTERS])
        pdu += address.to_bytes(2, "big")
        pdu += count.to_bytes(2, "big")
        if value:
            if kind == "I":
                data = int(value[0]).to_bytes(2, "big")
            elif kind == "F":
                data = struct.pack(">f", float(value[0]))
            else:
                data = round(float(value[0]) * 1000).to_bytes(4, "big")
            pdu.append(len(data))
            pdu += data
        if self.tcp:
            self._transaction = (self._transaction + 1) % 0x10000
            frame = (self._transaction.to_bytes(2, "big") + b"\x00\x00"
                     + (len(pdu) + 1).to_bytes(2, "big") + bytes([self.address]) + pdu)
        else:
            frame = bytes([self.address]) + pdu
            frame += crc16(frame)
        self.write_bytes(bytes(frame), **kwargs)

    def read(self, **kwargs) -> str:
        """Read and decode the Modbus response.

        :return: The parameter value for a read request, an empty string for a write request.
        :raises ValueError: If the controller answers with a Modbus exception.
        :raises ConnectionError: If the response is corrupted.
        """
        if self.tcp:
            function, data = self._read_tcp(**kwargs)
        else:
            function, data = self._read_rtu(**kwargs)
        if function & 0x80:
            raise ValueError(MODBUS_ERRORS.get(data[0], f"Modbus exception {data[0]}."))
        if function == WRITE_REGISTERS:
            return ""
        if function != READ_REGISTERS:
            raise ConnectionError(f"Unexpected Modbus function code {function}.")
        if self._kind == "F":
            return str(struct.unpack(">f", data)[0])
        elif self._kind == "T":
            return str(int.from_bytes(data, "big") / 1000)
        return str(int.from_bytes(data, "big"))

    def _read_rtu(self, **kwargs) -> tuple[int, bytes]:
        """Read a Modbus RTU response, return its function code and data."""
        header = self.read_bytes(2, **kwargs)
        if header[0] != self.address:
            raise ConnectionError(f"Response from unexpected address {header[0]}.")
        if header[1] & 0x80:
            body = self.read_bytes(3, **kwargs)
        elif header[1] == READ_REGISTERS:
            length = self.read_bytes(1, **kwargs)
            header += length
            body = self.read_bytes(length[0] + 2, **kwargs)
        elif header[1] == WRITE_REGISTERS:
            body = self.read_bytes(6, **kwargs)
        else:
            raise ConnectionError(f"Unexpected Modbus function code {header[1]}.")
        if crc16(header + body[:-2]) != body[-2:]:
            raise ConnectionError("Response CRC does not match.")
        return header[1], body[:-2]

    def _read_tcp(self, **kwargs) -> tuple[int, bytes]:
        """Read a Modbus TCP response, return its function code and data."""
        header = self.read_bytes(7, **kwargs)
        if int.from_bytes(header[:2], "big") != self._transaction:
            raise ConnectionError("Response to an unexpected transaction.")
        if header[6] != self.address:
            raise ConnectionError(f"Response from unexpected address {header[6]}.")
        pdu = self.read_bytes(int.from_bytes(header[4:6], "big") - 1, **kwargs)
        if pdu[0] == READ_REGISTERS:
            return pdu[0], pdu[2:]
        return pdu[0], pdu[1:]

    def check_set_errors(self) -> list:
        """Read the response to a write request, raising an error if the write failed.

        Called if :code:`check_set_errors=True` is set for that property.
        """
        self.read()
        return []

    process_value = Instrument.measurement(
        "F,1",
        """Measure the process value, e.g. the temperature (float).""",
    )

    target_setpoint = float_control(
        2,
        """Control the target setpoint (float).

        Writing it changes the active setpoint (SP1 or SP2), which is stored in
        non-volatile memory with a limited number of write cycles (typically 100,000).
        Do not write continuously changing values to it: use the setpoint rate limit, or
        the remote (communications) setpoint of models which have one.""",
    )

    proportional_band = float_control(
        6,
        """Control the PID proportional band (float).""",
    )

    integral_time = float_control(
        8,
        """Control the PID integral time in s (float).""",
    )

    derivative_time = float_control(
        9,
        """Control the PID derivative time in s (float).""",
    )

    output_level = Instrument.measurement(
        "F,3",
        """Measure the output power level in percent (float).""",
    )

    working_setpoint = Instrument.measurement(
        "F,5",
        """Measure the working setpoint, i.e. the setpoint currently used (float).""",
    )

    active_setpoint = int_control(
        15,
        """Control which setpoint is active (int, 1 for SP1, 2 for SP2).""",
        validator=strict_discrete_set,
        values=[1, 2],
        get_process=lambda v: int(v) + 1,
        set_process=lambda v: v - 1,
    )

    setpoint1 = float_control(
        24,
        """Control the setpoint 1 (float).

        Do not write continuously changing values to it, as it is stored in
        non-volatile memory with a limited number of write cycles (typically 100,000).""",
    )

    setpoint2 = float_control(
        25,
        """Control the setpoint 2 (float).

        Do not write continuously changing values to it, as it is stored in
        non-volatile memory with a limited number of write cycles (typically 100,000).""",
    )

    setpoint_rate_limit = float_control(
        35,
        """Control the setpoint rate limit in units per ramp unit (float, 0 means no limit).""",
    )
