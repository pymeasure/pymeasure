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

from enum import IntFlag
import logging

from pyvisa import VisaIOError
from pymeasure.adapters import SerialAdapter, VISAAdapter
from pymeasure.instruments import Instrument


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class VellemanK8090Switches(IntFlag):
    """Use to identify switch channels."""

    NONE = 0
    CH1 = 1 << 0
    CH2 = 1 << 1
    CH3 = 1 << 2
    CH4 = 1 << 3
    CH5 = 1 << 4
    CH6 = 1 << 5
    CH7 = 1 << 6
    CH8 = 1 << 7
    ALL = CH1 | CH2 | CH3 | CH4 | CH5 | CH6 | CH7 | CH8


def _parse_channels(channels) -> str:
    """Convert array of channel numbers into mask if needed."""
    if isinstance(channels, list):
        mask = VellemanK8090Switches.NONE
        for ch in channels:
            mask |= 1 << (ch - 1)
    else:
        mask = channels

    return hex(mask)


def _get_process_status(items):
    """Process the result of a 0x51 status message.

    :param items: List of 4 integers: [CMD, MASK, Param1, Param2]
    """
    if len(items) < 4 or items[0] != 0x51:
        return None, None, None

    return [VellemanK8090Switches(it) for it in items[1:]]


class VellemanK8090(Instrument):
    """For usage with the K8090 relay board, by Velleman.

    View the "K8090/VM8090 PROTOCOL MANUAL" for the serial command instructions.

    The communication is done by serial USB. The IO settings are fixed:

    ==================  ==================
    Baud rate           19200
    Data bits           8
    Parity              None
    Stop bits           1
    Flow control        None
    ==================  ==================

    A short timeout is recommended, since the device is not consistent in giving status messages
    and serial timeouts will occur also in normal operation.

    Use the class like:

    .. code-block:: python

       from pymeasure.instruments.velleman import VellemanK8090, VellemanK8090Switches as Switches

       instrument = VellemanK8090("ASRL1::INSTR")

       # Get status update from device
       last_on, curr_on, time_on = instrument.status

       # Toggle a selection of channels on
       instrument.switch_on = Switches.CH3 | Switches.CH4 | Switches.CH5

    """

    def __init__(self, adapter, name="Velleman K8090", timeout=100, **kwargs):
        super().__init__(
            adapter,
            name=name,
            asrl={"baud_rate": 19200},
            write_termination="",
            read_termination="",
            timeout=timeout,
            includeSCPI=False,
            **kwargs,
        )

    BYTE_STX = 0x04
    BYTE_ETX = 0x0F

    version = Instrument.measurement(
        "0x71",
        """
        Get firmware version, as (year - 2000, week). E.g. ``(10, 1)``
        """,
        cast=int,
        get_process=lambda v: (v[2], v[3]) if len(v) > 3 and v[0] == 0x71 else None,
    )

    status = Instrument.measurement(
        "0x18",
        """
        Get current relay status.
        The reply has a different command byte than the request.

        Three items (:class:`VellemanK8090Switches` flags) are returned:

        * Previous state: the state of each relay before this event
        * Current state: the state of each relay now
        * Timer state: the state of each relay timer
        """,
        cast=int,
        get_process=_get_process_status,
    )

    switch_on = Instrument.setting(
        "0x11,%s",
        """
        Set channels to on state. Other channels are unaffected.
        Pass either a list or set of channel numbers (starting at 1), or pass a bitmask.

        After switching this waits for a reply from the device. This is only send when
        a relay actually toggles, otherwise expect a blocking time equal to the
        communication timeout
        If speed is important, avoid calling `switch_` unnecessarily.
        """,
        set_process=_parse_channels,
        check_set_errors=True,
    )

    switch_off = Instrument.setting(
        "0x12,%s",
        """
        Set channels to off state. See :attr:`switch_on` for more details.
        """,
        set_process=_parse_channels,
        check_set_errors=True,
    )

    id = None  # No identification available

    def _make_checksum(self, command, mask, param1, param2):
        # The formula from the sheet requires twos-complement negation,
        # this works
        return 1 + 0xFF - ((self.BYTE_STX + command + mask + param1 + param2) & 0xFF)

    def write(self, command, **kwargs):
        """The write command specifically for the protocol of the K8090.

        This overrides the method from the ``Instrument`` class.

        Each packet to the device is 7 bytes:

        STX (0x04) - CMD - MASK - PARAM1 - PARAM2 - CHK - ETX (0x0F)

        Where `CHK` is checksum of the package.

        :param command: String like "CMD[, MASK, PARAM1, PARAM2]" - only CMD is mandatory
        :type command: str
        """

        # The device can give status updates when we don't expect it,
        # drop anything from the buffer first
        if isinstance(self.adapter, VISAAdapter):
            self.adapter.flush_read_buffer()
        elif isinstance(self.adapter, SerialAdapter):
            # The SerialAdapter does not have `flush_read_buffer` implemented
            self.adapter.connection.flush()

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
        # A message is always 7 bytes
        # (there is also a termination char, but since it is not exclusive it cannot be
        # reliably used)
        response = self.read_bytes(7)

        if len(response) < 7:
            raise ConnectionError(f"Incoming packet was {len(response)} bytes instead of 7")

        # Only consider the most recent block
        stx, command, mask, param1, param2, checksum, etx = list(response[-7:])

        if stx != self.BYTE_STX or etx != self.BYTE_ETX:
            raise ConnectionError(f"Received invalid start and stop bytes `{stx}` and `{etx}`")

        if command == 0x00:
            raise ConnectionError(f"Received invalid command byte `{command}`")

        real_checksum = self._make_checksum(command, mask, param1, param2)
        if real_checksum != checksum:
            raise ConnectionError(
                f"Packet checksum was not correct, got {hex(checksum)} "
                f"instead of {hex(real_checksum)}"
            )

        values_str = [str(v) for v in [command, mask, param1, param2]]

        return ",".join(values_str)

    def check_set_errors(self):
        """Check for errors after having set a property and log them.

        Called if :code:`check_set_errors=True` is set for that property.

        The K8090 replies with a status after a switch command, but
        **only** after any switch actually changed. In order to guarantee
        the buffer is empty, we attempt to read it fully here.
        No actual error checking is done here!

        :return: List of error entries.
        """
        try:
            self.read()
        except (VisaIOError, ConnectionError):
            pass  # Ignore a timeout
        except Exception as exc:
            log.exception("Setting a property failed.", exc_info=exc)
            raise
        else:
            return []
