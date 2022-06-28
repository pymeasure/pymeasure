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

import logging
import socket
from typing import List

from pymeasure.instruments.instrument import BaseChannel, Instrument
from pymeasure.instruments.keithley.keithley2600 import Keithley2600
from pymeasure.instruments.validators import strict_discrete_set, truncated_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley2602B(Keithley2600):
    """Represents the Keithley 2602B SourceMeter. This class adds digital I/O
    functionality to the Keithley2600 series driver. Note that this driver can
    be used to control any of the other 2600 series models that support digital
    I/O (2601B, 2611B, 2612B, 2635B, 2636B).

    Manual:
    https://drive.google.com/file/d/19_jllFNPkVmcRw9TuJlywFlwgmDTnIuu/view?usp=sharing
    """

    number_of_pins = 14
    _event_descriptions = []

    for channel in ["a", "b"]:
        _event_descriptions += [
            f"smu{channel}.trigger.SOURCE_COMPLETE_EVENT_ID",
            f"smu{channel}.trigger.MEASURE_COMPLETE_EVENT_ID",
            f"smu{channel}.trigger.PULSE_COMPLETE_EVENT_ID",
            f"smu{channel}.trigger.SWEEP_COMPLETE_EVENT_ID",
            f"smu{channel}.trigger.IDLE_EVENT_ID",
        ]

    def __init__(self, hostname: str, port: int = 5025, **kwargs) -> None:
        """Initializes LAN communication with the device.
        Flushes the error queue and logs the system identification info.
        If ID info cannot be retrieved, or communication was not successfully
        initialized, the results are logged.

        Args:
            hostname (str): Hostname of the system (initial expected value is a concatenation of
                product number and serial number. Note that the hostname can be overwritten.
            port (int): Port used to communicate with the system
        """
        self.hostname = hostname
        self.port = port
        adapter = f"TCPIP::{self.hostname}::{self.port}::SOCKET"
        self.dio_pins = [
            Keithley2600DigitalIOPin(self, i + 1) for i in range(self.number_of_pins)
        ]

        try:
            super().__init__(adapter, **kwargs)

        except ValueError or socket.error:
            log.exception(f"Could not connect to {self.hostname}")
            super().communication_success = False

        # Override valid voltage ranges (as requested)
        # to avoid potential damage to diodes
        for channel_name in [self.ChA, self.ChB]:
            channel_name.source_voltage_values = [-0.7, 0.7]
            channel_name.compliance_voltage_values = [-0.7, 0.7]

    @staticmethod
    def get_trigger_event_description_strings() -> List[str]:
        """Returns a list of the valid event IDs that can be used to select the event that
        causes a trigger to be asserted on the digital output line. The list can be indexed
        to set a digitial I/O line to assert a trigger given the described conditions. E.g.
        to set digital line 4 to assert a trigger when the SMU completes a source
        action on channel A, use the following:

        .. code-block:: python

            #Assume a Keithley2602B object called "smu" has been successully instaniated
            trigger_event_lists = smu.get_trigger_event_description_strings()
            smu.dio_pins[3].stimulus = trigger_event_lists[0]

        See page 9-61 of the Reference Manual for more details about the various event
        descriptions.
        """

        return Keithley2602B._event_descriptions


class Keithley2600DigitalIOPin(BaseChannel):
    def __init__(self, instrument: Keithley2602B, pin_number: int) -> None:
        self.instrument = instrument
        self.pin_number = pin_number

    def ask(self, cmd: str) -> str:
        return self.instrument.ask(f"print(digio.trigger[{self.pin_number}].{cmd})")

    def write(self, cmd: str) -> None:
        self.instrument.write(f"digio.trigger.[{self.pin_number}].{cmd}")

    def check_errors(self) -> None:
        self.instrument.check_errors()

    def assert_trigger(self) -> None:
        """This method asserts a trigger pulse on one of the digital I/O lines."""

        log.info(f"Asserting a trigger pulse on pin number {self.pin_number}.")
        self.write("assert()")

    def clear_trigger(self) -> None:
        """This method clears the trigger event detector on a digital I/O line."""

        log.info(f"Clearing trigger on pin number {self.pin_number}.")
        self.write("clear()")

    def get_event_id(self) -> int:
        """This method returns the mode in which the trigger event detector and
        the output trigger generator operate on the given trigger line. See description
        of all the possible EVENT_IDs on page 9-57 of the Series 2600B Reference Manual.
        """

        id = self.ask("EVENT_ID")
        return int(id)

    def get_overrun_status(self) -> bool:
        """This method returns the event detector overrun status. If this is
        true, an event was ignored because the event detector was already in the
        detected state when the event occurred. This is an indication of the
        state of the event detector built into the line itself. It does not
        indicate if an overrun occurred in any other part of the trigger model
        or in any other detector that is monitoring the event."""

        response_status = self.ask("overrun")

        if response_status == "false":
            status = False
        elif response_status == "true":
            status = True
        else:
            status = None

        return status

    def release_trigger(self) -> None:
        """This method releases an indefinite length or latched trigger."""

        log.info(f"Releasing trigger on pin number {self.pin_number}.")
        self.write("release()")

    def reset_trigger_values(self) -> None:
        """This method resets trigger values to their factory defaults. It
        sets the mode, pulsewidth, stimulus, and overrun status to factory
        default settings.
        """

        log.info(
            f"Resetting trigger values (to factory defaults) on pin number {self.pin_number}."
        )
        self.write("reset()")

    def wait_for_trigger(self, timeout: float) -> None:
        """This method waits for a trigger for up to a maximum of the timeout value (in seconds).
        Returns True if a trigger was detected, false if the timout was reached and no trigger was
        detected.

        Args:
            timeout: The amount of time to wait in seconds.
        """

        log.info(f"Waiting for trigger for {timeout} on pin number {self.pin_number}.")
        self.write(f"wait({timeout})")

    trigger_mode = Instrument.control(
        "mode",
        "mode=%d",
        """Property controlling the mode in which the trigger event detector and
        the output trigger generator operate on the given trigger line.
        """,
        validator=strict_discrete_set,
        values={
            "TRIG_BYPASS": 0,
            "TRIG_FALLING": 1,
            "TRIG_RISING": 2,
            "TRIG_EITHER": 3,
            "TRIG_SYNCHRONOUSA": 4,
            "TRIG_SYNCHRONOUS": 5,
            "TRIG_SYNCHRONOUSM": 6,
            "TRIG_RISINGA": 7,
            "TRIG_RISINGM": 8,
        },
        map_values=True,
    )

    pulse_width = Instrument.control(
        "pulsewidth",
        "pulsewidth=%f",
        """Property controlling the length of time (in seconds) that the trigger line is asserted
        for output triggers. Setting the pulse width to zero (0) seconds asserts
        the trigger indefinitely. To release the trigger line, use release_trigger().
        """,
        validator=truncated_range,
        values=[0, 10],
        map_values=False,
    )

    stimulus = Instrument.control(
        "stimulus",
        "stimulus=%s",
        """Property controlling the event that causes a trigger to be asserted on the digital output
        line.When setting this property, get the valid event descriptions using the
        get_trigger_event_description_strings method in the Keithley2602B class.
        """,
        validator=strict_discrete_set,
        values=Keithley2602B.get_trigger_event_description_strings(),
        map_values=False,
    )
