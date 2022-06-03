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


def _data_to_temp(data):
    """Convert the returned hex value "data" to a temperature in °C."""
    return int(data[7:11], 16) / 10.
    # get the hex number, convert to int and shift the decimal sign


registers = {'temperature': "D0002",
             'setpoint': "D0120",
             }


def _check_errors(response):
    errors = {"02": "Command does not exist or is not executable.",
              "03": "Register number does not exist.",
              "04": "Out of setpoint range.",
              "05": "Out of data number range.",
              "06": "Executed monitor without specifying what do monitor.",
              "08": "Illegal parameter is set.",
              "42": "Sum does not match the expected value.",
              "43": "Data value greater than specified received.",
              "44": "End of data or end of text character is not received.",
              }
    if response[5:7] == "OK":
        return []
    else:  # got[5:7] == "ER"
        """If communication is complete abnormally, TC038 return a
        character string “ER” and error code (EC1 and EC2)"""
        EC1 = response[7:9]
        if EC1 in ("03", "04", "05", "08"):
            EC2 = response[9:11]
            return [errors[EC1] + f" Wrong parameter has number {EC2}."]
        return [errors[EC1]]


class TC038(Instrument):
    """
    Communication with the HCP TC038 oven.

    This is the older version with an AC power supply and AC heater.

    It has parity or framing errors from time to time. Handle them in your
    application.

    The oven always responds with an "OK" to all valid requests or commands.
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

        self.set_monitored_quantity()  # start to monitor the temperature

    def _adjust_command(self, command):
        """
        Return an adjusted command string for the oven protocol.

        :param str command: Three chars indicating the type, and data for
            the command, if necessary.
        """
        # 010 is CPU (01) and time to wait (0), which are fix
        return chr(2) + f"{self.address:02}" + "010" + command + chr(3)
        # Response is chr(2) + address:02 + "01" + response + chr(3)

    def write(self, command):
        """Send a `command` in its own protocol."""
        super().write(self._adjust_command(command))

    def ask(self, command):
        """Send a `command` to the oven and read its string response."""
        got = super().ask(self._adjust_command(command))
        errors = _check_errors(got)
        if errors:
            raise ConnectionError(errors[0])
        return got

    def values(self, command, **kwargs):
        """Read the values of the oven in its own protocol."""
        got = super().values(self._adjust_command(command), **kwargs)
        errors = _check_errors(got[0])
        if errors:
            raise ConnectionError(errors[0])
        return got

    def check_errors(self):
        """Read the error from the instrument and return a list of errors."""
        errors = _check_errors(super().read())
        if errors:
            raise ConnectionError(errors[0])
        return errors

    def set_monitored_quantity(self, quantity='temperature'):
        """
        Configure the oven to monitor a certain `quantity`.

        `quantity` may be any key of `registers`. Default is the current
        temperature in °C.
        """
        # WRS in order to setup to monitor a word
        # monitor 1 word
        # monitor the word in register D0002
        self.ask(command="WRS" + "01" + registers[quantity])

    setpoint = Instrument.control(
        "WRD" + registers['setpoint'] + ",01",
        "WWR" + registers['setpoint'] + ",01,%s",
        """The current setpoint of the temperature controller in °C.""",
        get_process=_data_to_temp,
        set_process=lambda temp: f"{int(round(temp * 10)):04X}",
        check_set_errors=True,
        )

    temperature = Instrument.measurement(
        "WRD" + registers['temperature'] + ",01",
        """The currently measured temperature in °C.""",
        get_process=_data_to_temp
        )

    monitored_value = Instrument.measurement(
        "WRM",
        """The currently monitored value. For default it is the current
        temperature in °C.""",
        get_process=_data_to_temp
        )

    information = Instrument.measurement(
        "INF6",
        """The information about the device and its capabilites.""",
        get_process=lambda got: got[7:-1],
        )
