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

from pymeasure.instruments import Instrument


class Keithley2750(Instrument):
    """ Represents the Keithley2750 multimeter/switch system and provides a high-level interface for interacting
    with the instrument.
    """
    # TODO test closed_channels
    closed_channels = Instrument.measurement(":ROUTe:CLOSe?",
                                             "Reads the list of closed channels")

    def __init__(self, adapter, **kwargs) -> None:
        super().__init__(adapter, "Keithley 2750 Multimeter/Switch System", **kwargs)

    def open(self, channel: int) -> None:
        """ Opens (disconnects) the specified channel.

        :param int channel: 3-digit number for the channel
        :return: None
        """
        self.write(f":ROUTe:MULTiple:OPEN (@{channel})")

    def close(self, channel: int) -> None:
        """ Closes (connects) the specified channel.

        :param int channel: 3-digit number for the channel
        :return: None
        """
        # Note: if `MULTiple` is omitted, then the specified channel will close, but all other channels will open.
        self.write(f":ROUTe:MULTiple:CLOSe (@{channel})")

    def open_all(self) -> None:
        """ Opens (disconnects) all the channels on the switch matrix.

        :return: None
        """
        self.write(":ROUTe:OPEN:ALL")
        # Channel 133 is the switch between Mux 1 and Mux 2; we want it to be open. From testing the instrument,
        # it seems that channel 133 exhibits close/open behavior opposite from expected. If switched "closed",
        # the connection will actually be open, and when switched "open" it will actually be shorted.
        self.close(133)  # Open channel 133. Read the above statement to explain this non-intuitive method call.



