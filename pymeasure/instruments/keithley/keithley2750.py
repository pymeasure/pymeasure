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

from pymeasure.instruments import Instrument, SCPIMixin


def clean_closed_channels(output):
    """Cleans up the list returned by command ":ROUTe:CLOSe?", such that each entry is an integer
    denoting the channel number.
    """
    if isinstance(output, str):
        s = output.replace("(", "").replace(")", "").replace("@", "")
        if s == "":
            return []
        else:
            return [int(s)]
    elif isinstance(output, list):
        list_final = []
        for i, entry in enumerate(output):
            if isinstance(entry, float) or isinstance(entry, int):
                list_final += [int(entry)]
            elif isinstance(entry, str):
                list_final += [int(entry.replace("(", "").replace(")", "").replace("@", ""))]
            else:
                raise ValueError("Every entry must be a string, float, or int")
            assert isinstance(list_final[i], int)
        return list_final
    else:
        raise ValueError("`output` must be a string or list.")


class Keithley2750(SCPIMixin, Instrument):
    """ Represents the Keithley2750 multimeter/switch system and provides a high-level interface for
    interacting with the instrument.
    """

    closed_channels = Instrument.measurement(":ROUTe:CLOSe?",
                                             "Reads the list of closed channels",
                                             get_process=clean_closed_channels)

    def __init__(self, adapter, name="Keithley 2750 Multimeter/Switch System", **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )

    def open(self, channel):
        """ Opens (disconnects) the specified channel.

        :param int channel: 3-digit number for the channel
        :return: None
        """
        self.write(f":ROUTe:MULTiple:OPEN (@{channel})")

    def close(self, channel):
        """ Closes (connects) the specified channel.

        :param int channel: 3-digit number for the channel
        :return: None
        """
        # Note: if `MULTiple` is omitted, then the specified channel will close,
        # but all other channels will open.
        self.write(f":ROUTe:MULTiple:CLOSe (@{channel})")

    def open_all(self):
        """ Opens (disconnects) all the channels on the switch matrix.

        :return: None
        """
        self.write(":ROUTe:OPEN:ALL")
