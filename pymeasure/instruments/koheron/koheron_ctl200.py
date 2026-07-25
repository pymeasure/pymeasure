#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    strict_discrete_set,
    strict_range,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class KoheronError(IntFlag):
    """IntFlag for CTL200 Error Codes."""

    NONE = 0
    UART_BUFFER_OVERFLOW = 1 << 0
    UART_CMD_BEFORE_PROMPT = 1 << 1
    LASER_UNDERTEMPERATURE = 1 << 2
    LASER_OVERTEMPERATURE = 1 << 3
    CMD_UNKNOWN = 1 << 4
    CMD_INVALID_ARG = 1 << 5
    LASER_ON_WHILE_INTERLOCK = 1 << 6
    INTERLOCK_TRIGGERED = 1 << 7


class CTL200(Instrument):
    """PyMeasure driver for the Koheron CTL200-0 digital
    laser diode controller."""

    _STATUS_KEYS = ["lason", "vlaser", "itec", "vtec", "rtact", "iphd", "ain1",
                    "ain2"]

    def __init__(self, adapter, name="Koheron CTL200", baud_rate=115200, **kwargs):
        super().__init__(
            adapter,
            name,
            baud_rate=baud_rate,
            write_termination="\r\n",
            read_termination="\r\n",
            **kwargs,
        )

    def _read_cleaned_response(self, sent_command):
        """Read the reply of `sent_command`, discarding echo and prompt.

        The device echoes every command before replying with a single value
        line. Its prompt (">>") is not newline terminated, so it arrives
        prepended to the echo of the following command.
        """
        cmd_clean = sent_command.strip()
        while True:
            line = self.read().replace("\x00", "").strip()
            # Skip blank lines, the bare prompt, and the echoed command,
            # each of which may carry a leading prompt.
            if line.removeprefix(">>").strip() in ("", cmd_clean):
                continue
            return line

    def write(self, command, **kwargs):
        """Write a command and consume the echo and the reply.

        The device replies to every command with a single value line, settings
        included. It is discarded here to leave no unread data behind.
        """
        super().write(command, **kwargs)
        self._read_cleaned_response(command)

    def ask(self, command, query_delay=None):
        """Write a command and return its reply without echo and prompt."""
        super().write(command)
        self.wait_for(query_delay)
        return self._read_cleaned_response(command)

    # -- Laser -----------------------------------------------------------

    laser_enabled = Instrument.control(
        "lason",
        "lason %d",
        """Control whether the laser output is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    laser_current_setpoint = Instrument.control(
        "ilaser",
        "ilaser %g",
        """Control the laser current setpoint in A (float).""",
        get_process=lambda v: v * 1e-3,
        set_process=lambda v: v * 1e3,
    )

    laser_current_limit = Instrument.control(
        "ilmax",
        "ilmax %g",
        """Control the laser current software limit in A (float, strict_range
        from 0 to 1).""",
        validator=strict_range,
        values=[0, 1],
        get_process=lambda v: v * 1e-3,
        set_process=lambda v: v * 1e3,
    )

    laser_voltage = Instrument.measurement(
        "vlaser",
        """Get the laser voltage in V (float).""",
    )

    photodiode_current = Instrument.measurement(
        "iphd",
        """Get the photodiode current in A (float).""",
        get_process=lambda v: v * 1e-3,
    )

    laser_delay = Instrument.control(
        "ldelay",
        "ldelay %g",
        """Control the delay time between controller startup and laser
        startup in s (float, strict_range from 0.01 to 100).""",
        validator=strict_range,
        values=[0.01, 100],
        get_process=lambda v: v * 1e-3,
        set_process=lambda v: v * 1e3,
    )

    # -- TEC / temperature -----------------------------------------------

    tec_enabled = Instrument.control(
        "tecon",
        "tecon %d",
        """Control whether the TEC output is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    thermistor_setpoint = Instrument.control(
        "rtset",
        "rtset %g",
        """Control the thermistor resistance setpoint in Ω (float).""",
    )

    tec_current = Instrument.measurement(
        "itec",
        """Get the TEC current in A (float).""",
    )

    tec_voltage = Instrument.measurement(
        "vtec",
        """Get the TEC voltage in V (float).""",
    )

    thermistor_actual = Instrument.measurement(
        "rtact",
        """Get the actual thermistor resistance in Ω (float).""",
    )

    pid_proportional = Instrument.control(
        "pgain",
        "pgain %g",
        """Control the proportional gain of the TEC PID controller (float,
        strict_range from 0 to 0.1).""",
        validator=strict_range,
        values=[0, 0.1],
    )

    pid_integral = Instrument.control(
        "igain",
        "igain %g",
        """Control the integral gain of the TEC PID controller (float,
        strict_range from 0 to 0.1).""",
        validator=strict_range,
        values=[0, 0.1],
    )

    pid_differential = Instrument.control(
        "dgain",
        "dgain %g",
        """Control the differential gain of the TEC PID controller (float,
        strict_range from 0 to 0.1).""",
        validator=strict_range,
        values=[0, 0.1],
    )

    # -- Protection ------------------------------------------------------

    temp_protection_enabled = Instrument.control(
        "tprot",
        "tprot %d",
        """Control whether temperature protection is enabled (bool). If
        temperature protection is enabled, the laser current is automatically
        disabled if the thermistor resistance is outside the set thermistor
        window.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    thermistor_window_min = Instrument.control(
        "rtmin",
        "rtmin %g",
        """Control the minimum thermistor resistance in Ω to trigger
        temperature protection if enabled (float).""",
    )

    thermistor_window_max = Instrument.control(
        "rtmax",
        "rtmax %g",
        """Control the maximum thermistor resistance in Ω to trigger
        temperature protection if enabled (float).""",
    )

    tec_voltage_limit_min = Instrument.control(
        "vtmin",
        "vtmin %g",
        """Control the minimum TEC voltage limit in V (float, strict_range from
        -3 to 0).""",
        validator=strict_range,
        values=[-3.0, 0.0],
    )

    tec_voltage_limit_max = Instrument.control(
        "vtmax",
        "vtmax %g",
        """Control the maximum TEC voltage limit in V (float, strict_range from
        0 to 3).""",
        validator=strict_range,
        values=[0.0, 3.0],
    )

    # -- Interlock -------------------------------------------------------

    interlock_enabled = Instrument.control(
        "lckon",
        "lckon %d",
        """Control whether the hardware interlock is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    # -- Aux Inputs ------------------------------------------------------
    analog_input_1 = Instrument.measurement(
        "ain1",
        """Get the voltage on auxiliary input AI1 in V (float).""",
    )

    analog_input_2 = Instrument.measurement(
        "ain2",
        """Get the voltage on auxiliary input AI2 in V (float).""",
    )

    laser_modulation_gain = Instrument.control(
        "lmodgain",
        "lmodgain %g",
        """Control the laser current modulation gain of auxiliary input 1 in
        A/V (float, strict_range from -100 to 100).""",
        validator=strict_range,
        values=[-100, 100],
        get_process=lambda v: v * 1e-3,
        set_process=lambda v: v * 1e3,
    )

    tec_modulation_gain = Instrument.control(
        "tmodgain",
        "tmodgain %g",
        """Control the temperature modulation gain of auxiliary input 2 in
        Ω/V (float, strict_range from -100000 to 100000).""",
        validator=strict_range,
        values=[-100000, 100000],
    )

    # -- Misc ------------------------------------------------------------
    firmware_version = Instrument.measurement(
        "version",
        """Get the firmware version (str).""",
        cast=str,
    )

    board_version = Instrument.measurement(
        "model",
        """Get the board model version (str).""",
        cast=str,
    )

    serial_number = Instrument.measurement(
        "serial",
        """Get the serial number (str).""",
        cast=str,
    )

    baud_rate_setting = Instrument.control(
        "brate",
        "brate %d",
        """Control the UART baud rate of the device (int, strict_range from 9600
        to 460800). The new baud rate takes effect immediately, which
        desynchronizes the current connection: reconnect with a matching
        :code:`baud_rate` to keep communicating. Use :meth:`save` to persist it
        across power cycles.""",
        validator=strict_range,
        values=[9600, 460800],
        cast=int,
    )

    @staticmethod
    def _parse_status(values):
        keys = CTL200._STATUS_KEYS
        if len(values) != len(keys):
            raise ValueError(
                f"Expected {len(keys)} status fields, got {len(values)}:"
                f" {values}"
            )
        result = dict(zip(keys, (float(v) for v in values)))
        result["iphd"] *= 1e-3
        return result

    status = Instrument.measurement(
        "status",
        """Get a dict with all status values ("lason", "vlaser", "itec",
        "vtec", "rtact", "iphd", "ain1", "ain2").""",
        cast=str,
        get_process=lambda v: CTL200._parse_status(v.split()),
    )

    board_temperature = Instrument.measurement(
        "tboard",
        """Get the current temperature of the driver board in °C (float).""",
    )

    def save(self):
        """Save the current configuration to internal non-volatile memory."""
        self.write("save")

    def clear_error(self):
        """Clear the error code."""
        self.write("errclr")

    error_status = Instrument.measurement(
        "err",
        """Get the current error status (KoheronError). The device returns the
        error code in hexadecimal format.""",
        cast=str,
        get_process=lambda v: KoheronError(int(v, 16)),
    )

    user_data = Instrument.control(
        "userdata",
        "userdata write %s",
        """Control the user data string saved on the device
        (max. 31 chars, str)""",
        cast=str,
        set_process=lambda v: str(v)[:31]
    )

    def check_errors(self):
        """Read the error status flag, log the errors, and clear them.

        :return: List of error entries.
        """
        status = self.error_status
        # Iterating the flag itself requires Python 3.11, so mask the members
        # instead. NONE has value 0 and drops out of the comprehension.
        errors = [error.name for error in KoheronError if error.value & status]
        for error in errors:
            log.error(f"{self.name}: {error}")
        if errors:
            self.clear_error()
        return errors
