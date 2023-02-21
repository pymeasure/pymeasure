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

import serial

from pymeasure.instruments import Instrument


def _parse_channels(channels) -> str:
    """Convert array of channel numbers into mask if needed."""
    if isinstance(channels, list):
        mask = 0x00
        for ch in channels:
            mask |= 1 << (ch - 1)
    else:
        mask = channels

    return hex(mask)


def _get_process_status(items):
    """Process the result of a 0x51 status message."""
    if len(items) < 4 or items[0] != 0x51:
        return None

    return _ints_to_bool_lists(items[1:])


def _ints_to_bool_lists(numbers):
    """Convert 8-bit integers into lists of booleans.

    Also works for a single given integer.

    The least significant bit (#0) will be first
    """
    if isinstance(numbers, int):
        numbers = [numbers]

    bool_lists = [[bool(num & (1 << n)) for n in range(8)] for num in numbers]

    if len(bool_lists) == 1:
        return bool_lists[0]

    return bool_lists


class VellemanK8090(Instrument):
    """For usage with the K8090 relay board, by Velleman.

    The communication is done by serial USB.

    View the "K8090/VM8090 PROTOCOL MANUAL" for the serial command instructions.
    """

    BYTE_STX = 0x04
    BYTE_ETX = 0x0F

    version = Instrument.measurement(
        "0x71",
        """
        Get firmware version, as (year - 2000, week).
        E.g. ``(10, 1)``
        """,
        cast=int,
        get_process=lambda v: (v[2], v[3]) if len(v) > 3 and v[0] == 0x71 else None,
    )

    status = Instrument.measurement(
        "0x18",
        """
        Get current relay status.
        The reply has a different command byte than the request.
        
        Three items (lists of 8 bools) are returned:
        - Previous state: the state of each relay before this event
        - Current state: the state of each relay now
        - Timer state: the state of each relay timer
        """,
        cast=int,
        get_process=_get_process_status,
    )

    switch_on = Instrument.setting(
        "0x11,%s",
        """"
        Switch on a set of channels.
        Other channels are unaffected.
        Pass either a list or set of channel numbers (starting at 1), or pass a bitmask
        """,
        set_process=_parse_channels,
    )

    switch_off = Instrument.setting(
        "0x12,%s",
        """"
        Switch off a set of channels. See :prop:`switch_on`.
        """,
        set_process=_parse_channels,
    )

    id = None  # No identification available

    def __init__(
        self, adapter, name="Velleman K8090", baud_rate=19200, timeout=1000, **kwargs
    ):
        super().__init__(
            adapter, name=name, baud_rate=baud_rate, timeout=timeout, **kwargs
        )

    def _make_checksum(self, command, mask, param1, param2):
        # The formula from the sheet requires twos-complement negation,
        # this works
        return 1 + 0xFF - ((self.BYTE_STX + command + mask + param1 + param2) & 0xFF)

    def switch_on_blocking(self, channels):
        """Switch on a set of channels and wait for the confirmation.

        See :prop:`switch_on`.

        The set command is identical, and the processing part of
        :prop:`status` is called.

        :returns: See :prop:`status`
        """
        mask = _parse_channels(channels)
        self.write(f"0x11,{mask}")
        data = self.read()
        items = [int(it) for it in data.split(",")]
        return _get_process_status(items)

    def switch_off_blocking(self, channels):
        """Switch off a set of channels and wait for the confirmation.

        See :prop:`switch_off`.

        The set command is identical, and the processing part of
        :prop:`status` is called.

        :returns: See :prop:`status`
        """
        mask = _parse_channels(channels)
        self.write(f"0x12,{mask}")
        data = self.read()
        items = [int(it) for it in data.split(",")]
        return _get_process_status(items)

    def write(self, command, **kwargs):
        """The write command specifically for the protocol of the K8090.

        This overrides the method from the ``Instrument`` class.

        Each packet to the device is 7 bytes:

        STX (0x04) - CMD - MASK - PARAM1 - PARAM2 - CHK - ETX (0x0F)

        Where `CHK` is checksum of the package.

        :param command: String like "CMD[, MASK, PARAM1, PARAM2]" - only CMD is mandatory
        :type command: str
        """
        items_str = command.split(",")

        items = [int(it, 16) for it in items_str]

        cmd = items[0]
        mask = items[1] if len(items) > 1 else 0
        param1 = items[2] if len(items) > 2 else 0
        param2 = items[3] if len(items) > 3 else 0

        checksum = self._make_checksum(cmd, mask, param1, param2)

        content = [
            self.BYTE_STX,
            cmd,
            mask,
            param1,
            param2,
            checksum,
            self.BYTE_ETX,
        ]

        self.write_bytes(bytes(content))

    def read(self, **kwargs):
        """The read command specifically for the protocol of the K8090.

        This overrides the method from the ``instrument`` class.

        See :meth:`write`, replies from the machine use the same format.

        A read will return a list of CMD, MASK, PARAM1 and PARAM2.
        """
        num_bytes = 7  # Each packet should always be exactly 7 bytes

        if isinstance(self.adapter.connection, serial.Serial):
            # Because we do not always read the reply to a setting, the buffer
            # might not have been empty. Try to clear it completely but without waiting
            # for more
            num_bytes = max(7, self.adapter.connection.in_waiting)

        response = self.read_bytes(num_bytes)

        if len(response) < 7:
            raise ConnectionError(
                f"Incoming packet was {len(response)} bytes instead of 7"
            )
        elif len(response) > 7:
            response = response[-7:]  # Keep the most recent block only

        stx, command, mask, param1, param2, checksum, etx = list(response)

        if stx != self.BYTE_STX or etx != self.BYTE_ETX:
            raise ConnectionError(
                f"Received invalid start and stop bytes `{stx}` and `{etx}`"
            )

        if command == 0x00:
            raise ConnectionError(f"Received invalid command byte `{command}`")

        real_checksum = self._make_checksum(command, mask, param1, param2)
        if real_checksum != checksum:
            raise ConnectionError(
                f"Packet checksum was not correct, got {hex(checksum)} instead of {hex(real_checksum)}"
            )

        values_str = [str(v) for v in [command, mask, param1, param2]]

        return ",".join(values_str)
