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

import logging

from pymeasure.instruments import Instrument
from pyvisa.constants import Parity


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


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
              "06": "Executed monitor without specifying what to monitor.",
              "08": "Illegal parameter is set.",
              "42": "Sum does not match the expected value.",
              "43": "Data value greater than specified received.",
              "44": "End of data or end of text character is not received.",
              }
    if response[5:7] == "OK":
        return []
    else:  # got[5:7] == "ER"
        """If communication is completed abnormally, TC038 returns a
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

    :param str adapter: Name of the COM-Port.
    :param int address: Address of the device. Should be between 1 and 99.
    :param int timeout: Timeout in ms.
    """

    def __init__(self, adapter, name="TC038", address=1, timeout=1000,
                 **kwargs):
        super().__init__(
            adapter,
            name,
            timeout=timeout,
            write_termination="\r",
            read_termination="\r",
            parity=Parity.even,
            includeSCPI=False,
            **kwargs,
        )
        self.address = address

        self.set_monitored_quantity()  # start to monitor the temperature

    def write(self, command):
        """Send a `command` in its own protocol."""
        # 010 is CPU (01) and time to wait (0), which are fix
        super().write(chr(2) + f"{self.address:02}" + "010" + command + chr(3))

    def read(self):
        """Do error checking on reading."""
        # Response is chr(2) + address:02 + "01" + response + chr(3)
        got = super().read()
        errors = _check_errors(got)
        if errors:
            raise ConnectionError(errors[0])
        return got

    def check_set_errors(self):
        """Check for errors after having set a property.

        Called if :code:`check_set_errors=True` is set for that property.
        """
        try:
            self.read()
        except ConnectionError as exc:
            log.exception("Setting a property failed.", exc_info=exc)
            raise
        else:
            return []

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
        """Control the setpoint of the temperature controller in °C.""",
        get_process=_data_to_temp,
        set_process=lambda temp: f"{int(round(temp * 10)):04X}",
        check_set_errors=True,
    )

    temperature = Instrument.measurement(
        "WRD" + registers['temperature'] + ",01",
        """Measure the current temperature in °C.""",
        get_process=_data_to_temp
    )

    monitored_value = Instrument.measurement(
        "WRM",
        """Measure the currently monitored value. For default it is the current
        temperature in °C.""",
        get_process=_data_to_temp
    )

    information = Instrument.measurement(
        "INF6",
        """Get the information about the device and its capabilities.""",
        get_process=lambda got: got[7:-1],
    )
