#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
from pymeasure.instruments.generic_types import SCPIMixin
from .buffer import KeithleyBuffer


class KeithleyDAQ6510(KeithleyBuffer, SCPIMixin, Instrument):
    """ Represents the Keithley DAQ6510 Data Acquisition Logging Multimeter System
    and provides a high-level interface for interacting with the instrument.

    .. code-block:: python

        keithley = KeithleyDAQ6510("GPIB::1")
        keithley = KeithleyDAQ6510("TCPIP::192.168.1.1::INSTR")

    """

    def __init__(self, adapter, name="Keithley DAQ6510", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    def no_errors(self):
        """
        Check to see if the instrument has any errors returned or not.

        :return: ``True`` if there are no errors, ``False`` if there are errors.
        """
        return len(self.check_errors() == 0)

    def use_mux(self):
        """
        Enables MUX switching. Forces open channels 134 and 135 for isolation and
        closes channel 133 to separate MUX1 and MUX2.

        :return: ``True`` if the channels were opened and closed successfully.
        """
        self.open_channels([134, 135])
        self.close_channels([133])
        return self.ask(":ROUT:CLOS?") == "(@133)\n"

    def open_channel(self, channel):
        """
        Set a single channel to open.

        :param channel: Channel to be set to open.
        """
        self.write(f":ROUT:OPEN (@{channel})")

    def close_channel(self, channel):
        """
        Set a single channel to closed.

        :param channel: Channel to be set to closed.
        """
        self.write(f":ROUT:CLOS (@{channel})")

    def open_channels(self, channel_list):
        """
        Configures multiple channels to be open.

        :param channel_list: List of channels to be set to open.
        """
        for channel in channel_list:
            self.open_channel(channel)

    def close_channels(self, channel_list):
        """
        Configures multiple channels to be closed.

        :param channel_list: List of channels to be set to closed.
        """
        for channel in channel_list:
            self.close_channel(channel)

    def beep(self, frequency, duration):
        """
        Sound a system beep.

        :param frequency: A frequency in Hz from 20 and 8000 Hz
        :param duration: The amount of time to play the tone, between 0.001 s to 100 s
        :return: None
        """
        self.write(f":SYST:BEEP {frequency:g}, {duration:g}")
