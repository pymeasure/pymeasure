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
from enum import IntFlag

from pymeasure.instruments import Instrument, validators
from pyvisa.constants import Parity, StopBits


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def emission_validator(value, values):
    if value is True:
        return "ON"
    elif value is False:
        return "OFF"
    raise ValueError(f"Value is {value}, but a boolean or 'ON' or 'OFF' required.")


def setpoint_validator(value, values):
    if value == 0:
        return value
    else:
        return validators.strict_range(value, values)


def power_get_process_generator(minimum):
    """Generate a get_process for the power property."""
    def get_process(value):
        if isinstance(value, float):
            return value
        elif value == "Off":
            return 0
        elif value == "Low":
            return minimum
        else:
            return value
    return get_process


class YAR(Instrument):
    """Communication with the YAR fiber amplifier series by IPG Photonics.

    This is the RS232 command set. GPIB has different commands.
    """

    def __init__(self, adapter, name="YAR fiber amplifier", **kwargs):
        """Establish communication with the device."""
        kwargs.setdefault("write_termination", "\r")
        kwargs.setdefault("read_termination", "\r")
        super().__init__(adapter,
                         name=name,
                         includeSCPI=False,
                         asrl={'parity': Parity.none, 'stop_bits': StopBits.one},
                         **kwargs)

        # Commands are 3-4 letters, followed by a parameter, a separation
        # by space is option. Commands are case-insensitive.
        # Response is command echoed back, followed by ': ' and the return
        # value.

        # get valid range of power setpoint:
        self.power_setpoint_values = self.power_range
        self.power_get_process = power_get_process_generator(self.minimum_display_power)

    class Status(IntFlag):
        EMISSION = 0x1  # emission is fully on
        STARTUP_DELAY = 0x2  # it is in 3 s startup
        HIGH_TEMPERATURE = 1 << 16
        HIGH_BACKREFLECTION = 1 << 17
        UNEXPECTED_EMISSION = 1 << 19
        SEEDLASER_FAIL = 1 << 20

    def read(self):
        """Read an instrument answer and check whether it is an error."""
        reply = super().read().split(":")
        if reply[0] == "ERR":
            raise ConnectionError(f"Reading error '{reply}'.")
        else:
            return reply[-1].strip()

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

    # COMMUNICATION FUNCTIONS

    @property
    def id(self):
        """Get the model number."""
        return self.values("RMN")[0]

    @property
    def status(self):
        """Get the current status."""
        got = int(self.values("STA")[0])
        return self.Status(got)

    emission_enabled = Instrument.control(
        "STA",
        "EM%s",
        """Control emission of the amplifier (bool).""",
        cast=int,
        values=("ON", "OFF"),
        validator=emission_validator,
        get_process=lambda v: bool(v & YAR.Status.EMISSION),
        check_set_errors=True,
    )

    power = Instrument.measurement(
        "ROP",
        "Measure current output power in W.",
        get_process=power_get_process_generator(0.1),
        dynamic=True,
    )

    @property
    def power_range(self):
        """Get the power limits in W."""
        low = self.values("RNP")[0]
        high = self.values("RMP")[0]
        return [low, high]

    power_setpoint = Instrument.control(
        "RPS", "SPS %g", """Control output power setpoint in W.""",
        values=(1, 2),
        validator=setpoint_validator,
        check_set_errors=True,
        dynamic=True,
    )

    current = Instrument.measurement("RDC", """Measure the diode current in A.""")

    temperature = Instrument.measurement("RCT", """Measure case temperature in °C.""")

    wavelength_temperature = Instrument.control(
        "RWA", "SWA %g", """Control temperature in °C for seed wavelength control.""",
        check_set_errors=True)

    temperature_seed = Instrument.measurement(
        "RST", "Measure current seed temperature in °C")

    firmware = Instrument.measurement("RFV", """Get firmware version""", cast=str)

    maximum_case_temperature = Instrument.measurement(
        "RMT", """Measure the maximum temperature for the optical module in °C.""")

    minimum_display_power = Instrument.measurement(
        "RDPT", """Measure the minimum displayable output power in W.""")

    def clear(self):
        """Reset all errors."""
        return self.ask("RERR")
