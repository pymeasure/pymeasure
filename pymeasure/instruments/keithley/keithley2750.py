#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

from collections import Iterable
from pymeasure.instruments import Instrument
import time

SETTLE_DURATION = 0  # seconds. Duration for switch and electrical connection reading to settle.


class Keithley2750(Instrument):
    """
    Instrument class for using the Keithley 2750 multiplexer mainframe. The only multiplexer module card supported at
    this time is the Keithley 7701 card, which is inserted into the mainframe. This class is written to multiplex
    between selected devices under test (DUTs) which are represented by the multiplexer channels associated with them.
    """
    def __init__(self, adapter, dut_channels: dict, **kwargs) -> None:
        """
        :param adapter: most commonly, this is a string containing the NI address of the instrument.
         You can find the address by running `import visa; visa.ResourceManager().list_resources()`. See
         pymeasure.instruments.Instrument's docstring for detailed information.
        :param dict dut_channels: dictionary that maps dut_id to the associated list of channels to
         be closed (connected). Channels are 3-digit numbers: 1st digit is the slot number, 2nd and 3rd digit
         comprise the 2 digit channel number. All 3 of these numbers are 1-indexed (not 0-indexed).
         E.g. {0: [101, 117],
               1: [102, 118],
               2: [103, 119],
               3: [104, 120]}
        """
        super().__init__(adapter, "Keithley 2750 Multiplexer", **kwargs)
        idn = self.ask("*IDN?")
        if 'KEITHLEY INSTRUMENTS INC.,MODEL 2750' not in idn:
            raise ValueError(f'A Keithley 2750 Multiplexer is not connected at address {adapter}.')

        self.dut_channels = dut_channels if dut_channels is not None else {}
        validate_dut_channels(self.dut_channels)

        # Properly keeps track of closed duts, only if close_dut, open_dut, open_all, and setup
        # are the only methods used to handle channels. If _close and _open are used to
        # tamper with DUT channels, self.closed_dut_ids may be inconsistent.
        self.closed_dut_ids = []

    def close_dut(self, dut_id: int) -> None:
        """
        Closes (connects) the channels corresponding to a specified DUT.

        :param int dut_id: ID of specified DUT
        :return: None
        """
        validate_dut_id(dut_id, self.dut_channels)
        if dut_id not in self.closed_dut_ids:
            for channel in self.dut_channels[dut_id]:
                self._close(channel)
            self.closed_dut_ids += [dut_id]
            time.sleep(SETTLE_DURATION)

    def open_dut(self, dut_id: int) -> None:
        """
        Opens (disconnects) the channels corresponding to a specified DUT.

        :param int dut_id: ID of specified DUT
        :return: None
        """
        validate_dut_id(dut_id, self.dut_channels)
        if dut_id in self.closed_dut_ids:
            for channel in self.dut_channels[dut_id]:
                self._open(channel)
            index_dut_id = self.closed_dut_ids.index(dut_id)
            self.closed_dut_ids.pop(index_dut_id)
            time.sleep(SETTLE_DURATION)

    def open_all(self) -> None:
        """
        Opens (disconnects) all the channels on the switch matrix.

        :return: None
        """
        self.write(":ROUTe:OPEN:ALL")
        # Channel 133 is the switch between Mux 1 and Mux 2; we want it to be open. From testing the instrument,
        # it seems that channel 133 exhibits close/open behavior opposite from expected. If switched "closed",
        # the connection will actually be open, and when switched "open" it will actually be shorted.
        self._close(133)  # Open channel 133. Read the above statement to explain this non-intuitive method call.
        self.closed_dut_ids = []
        time.sleep(SETTLE_DURATION)

    def _open(self, channel: int) -> None:
        """
        Opens (disconnects) the specified channel.

        :param int channel: 3-digit number for the channel
        :return: None
        """
        validate_channel(channel)
        self.write(f":ROUTe:MULTiple:OPEN (@{channel})")

    def _close(self, channel: int) -> None:
        """
        Closes (connects) the specified channel.

        :param int channel: 3-digit number for the channel
        :return: None
        """
        validate_channel(channel)
        # Note: if `MULTiple` is omitted, then the specified channel will close, but all other channels will open.
        self.write(f":ROUTe:MULTiple:CLOSe (@{channel})")

    def reset(self):
        """

        :return:
        """
        super().reset()
        self.open_all()


def validate_dut_channels(dut_channels: dict) -> None:
    """
    Ensures all channels are valid in dut_channels. Raises error if invalid, does nothing otherwise.

    :param dict dut_channels: dictionary that maps dut_id to the list of channels to be closed (connected).
    :return: None
    """
    if not isinstance(dut_channels, dict):
        raise ValueError('`dut_channels` must be a dictionary.')

    for channels in dut_channels.values():
        if not isinstance(channels, Iterable):
            raise ValueError('Mapped values in `dut_channels_dict` must be iterables, e.g. lists.')
        for channel in channels:
            validate_channel(channel)


def validate_channel(channel: int) -> None:
    """
    Validates channel by ensuring it is a 3-digit item.

    :param int channel: channel number. Can be a string or a number
    :return: None
    """
    if not isinstance(channel, int):
        raise ValueError('`channel` must an integer.')
    if channel < 101 or 133 < channel:
        raise ValueError('Channel must be an integer between 101 and 133.')


def validate_dut_id(dut_id: int, dut_channels: dict) -> None:
    """
    Checks whether dut_id is valid. Throws error if not.

    :param int dut_id: specified dut_id
    :param dict dut_channels: given dut_channels
    :return: None
    """
    if dut_id not in dut_channels.keys():
        raise ValueError('`dut_id` must be valid. Valid values are {list(self.dut_channels.keys())}.')


