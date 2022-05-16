#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from pyvisa.constants import Parity


class TC038(Instrument):
    """
    Communication with the HCP TC038 oven.

    This is the older version with an AC power supply and AC heater.

    It has parity or framing errors from time to time. Handle them in your
    application.
    """

    def __init__(self, resourceName, address=1, timeout=1000,
                 includeSCPI=False):
        """
        Initialize the communication.

        Parameters
        ----------
        resourceName : str
            name COM-Port.
        address : int
            address of the device. Should be between 1 and 99.
        timeout : int
            Timeout in ms.
        """
        super().__init__(resourceName, "TC038", timeout=timeout,
                         write_termination="\r", read_termination="\r",
                         parity=Parity.even,)
        self.address = address

        self.monitorTemperature()  # start to monitor the temperature

    def write(self, command):
        """
        Send "command" to the oven with "commandData".

        Parameters
        ----------
        command : string, optional
            Command to be sent. Three chars indicating the type, and data for
            the command, if necessary.
        """
        super().write(chr(2) + f"{self.address:02}" + "010"
                      + command + chr(3))
        # 010 is CPU (01) and time to wait (0), which are fix

    def ask(self, command):
        """
        Send a command to the oven and read its response.

        Parameters
        ----------
        command : string, optional
            Command to be sent. Three chars indicating the type, and data for
            the command, if necessary.

        Returns
        -------
        string
            response of the system.

        """
        return super().ask(chr(2) + f"{self.address:02}" + "010"
                           + command + chr(3))

    def monitor_temperature(self):
        """Configure the oven to monitor the current temperature."""
        self.ask(command="WRS" + "01" + "D0002")
        # WRS in order to setup to monitor a word
        # monitor 1 word
        # monitor the word in register D0002

    setpoint = Instrument.control(
        "WRD" + "D0120" + ",01",
        "D0120,01,%s",
        """The current setpoint of the temperature controller in °C.""",
        get_process=self._data_to_temp,
        set_process=self._temp_to_data
        )

    temperature = Instrument.measurement(
        "WRD" + "D0002" + ",01",
        """The currently measured temperature in °C.""",
        get_process=self._data_to_temp
        )

    monitored_value = Instrument.measurement(
        "WRM",
        """The currently monitored value. For default it is the current
        temperature in °C.""",
        get_process=self._data_to_temp
        )

    def _data_to_temp(self, data):
        """Convert the returned hex value "data" to a temperature in °C."""
        return int(data[7:11], 16) / 10.
        # get the hex number, convert to int and shift the decimal sign

    def _temp_to_data(self, temp):
        """Convert the temperature `temp` in °C to a command string."""
        return f"{int(round(temp * 10)):04X}"
