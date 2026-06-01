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
import time
from enum import IntFlag
from pymeasure.adapters import SerialAdapter
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


class CTL200Adapter(SerialAdapter):
    """Serial adapter for Koheron CTL200 do deal with echo responses."""

    def __init__(self, port, **kwargs):
        kwargs.setdefault("baudrate", 115200)
        kwargs.setdefault("timeout", 2)
        super().__init__(
            port,
            write_termination="\r\n",
            read_termination="\r\n",
            **kwargs
        )
        self._last_command: str = ""
        self._response_buffer: list[str] = []
        time.sleep(0.05)
        self.connection.reset_input_buffer()

    def _read_until_prompt(self) -> list[str]:
        raw = b""
        total_timeout = max(self.connection.timeout or 0, 2.0)
        deadline = time.monotonic() + total_timeout
        while time.monotonic() < deadline:
            waiting = self.connection.in_waiting
            if waiting:
                raw += self.connection.read(waiting)
                if b">>" in raw:
                    # read trailing chars (\r\n, ...)
                    time.sleep(0.02)
                    trailing = self.connection.in_waiting
                    if trailing:
                        raw += self.connection.read(trailing)
                    break
            else:
                time.sleep(0.005)

        log.debug("raw RX: %r", raw)
        text = raw.decode(errors="replace")
        lines = [line.strip() for line in text.replace("\r", "").split("\n")]
        lines = [line for line in lines if line]  # remove blanks
        if lines and self._last_command and lines[0] == self._last_command:
            lines.pop(0)  # remove echo
        lines = [line for line in lines if line != ">>"]  # remove prompt chars
        log.debug("parsed lines: %r", lines)
        return lines

    def write(self, command: str) -> None:
        self._last_command = command.strip()
        super().write(command)
        self._response_buffer = self._read_until_prompt()
        log.debug("write %r -> buffer: %r", command,
                  self._response_buffer)

    def read(self) -> str:
        if self._response_buffer:
            value = self._response_buffer.pop(0)
            log.debug("read -> %r", value)
            return value
        log.debug("read -> buffer empty, return ''")
        return ""


class CTL200(Instrument):
    """PyMeasure driver for the Koheron CTL200-0 digital
    laser diode controller."""

    def __init__(self, adapter, name="Koheron CTL200", **kwargs):
        if isinstance(adapter, str):
            adapter = CTL200Adapter(adapter, **kwargs)
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            **kwargs
        )

    # -- Laser -----------------------------------------------------------

    laser_enabled = Instrument.control(
        "lason",
        "lason %d",
        """Control whether the laser output is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    laser_current = Instrument.control(
        "ilaser",
        "ilaser %g",
        """Control the laser current setpoint in A (float).""",
        cast=float,
        get_process=lambda v: v * 1e-3,
        set_process=lambda v: v * 1e3,
    )

    laser_current_limit = Instrument.control(
        "ilmax",
        "ilmax %g",
        """Control the laser current software limit in A (float).""",
        cast=float,
        validator=strict_range,
        values=[0, 1],
        get_process=lambda v: v * 1e-3,
        set_process=lambda v: v * 1e3,
    )

    laser_voltage = Instrument.measurement(
        "vlaser",
        """Get the laser voltage in V (float).""",
        cast=float,
    )

    photodiode_current = Instrument.measurement(
        "iphd",
        """Get the photodiode current in A (float).""",
        cast=float,
        get_process=lambda v: v * 1e-3,
    )

    laser_delay = Instrument.control(
        "ldelay",
        "ldelay %g",
        """Control the delay time between controller startup and laser
        startup in s (float).""",
        cast=float,
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
        cast=float,
    )

    tec_current = Instrument.measurement(
        "itec",
        """Get the TEC current in A (float).""",
        cast=float,
    )

    tec_voltage = Instrument.measurement(
        "vtec",
        """Get the TEC voltage in V (float).""",
        cast=float,
    )

    thermistor_actual = Instrument.measurement(
        "rtact",
        """Get the actual thermistor resistance in Ω (float).""",
        cast=float,
    )

    tec_current = Instrument.measurement(
        "itec",
        """Get the TEC current in A (float).""",
        cast=float,
    )

    tec_voltage = Instrument.measurement(
        "vtec",
        """Get the TEC voltage in V (float).""",
        cast=float,
    )

    pid_proportional = Instrument.control(
        "pgain",
        "pgain %g",
        """Control the proportional gain of the TEC PID controller (float).""",
        cast=float,
    )

    pid_integral = Instrument.control(
        "igain",
        "igain %g",
        """Control the integral gain of the TEC PID controller (float).""",
        cast=float,
    )

    pid_differential = Instrument.control(
        "dgain",
        "dgain %g",
        """Control the differential gain of the TEC PID controller (float).""",
        cast=float,
    )

    # -- Protection ------------------------------------------------------

    temp_protection_enabled = Instrument.control(
        "tprot",
        "tprot %d",
        """Control whether temperature protection is enabled (bool). If
        temperature protection is enabled, the laser current is automatically
        disabled id the thermistor resistance is outside the thermistor
        window.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    thermistor_window_min = Instrument.control(
        "rtmin",
        "rtmin %g",
        """Control the minimum thermistor resistance in Ω (float) to trigger
        temperature protection if enabled.""",
        cast=float,
    )

    thermistor_window_max = Instrument.control(
        "rtmax",
        "rtmax %g",
        """Control the maximum thermistor resistance in Ω (float) to trigger
        temperature protection if enabled.""",
        cast=float,
    )

    tec_voltage_limit_min = Instrument.control(
        "vtmin",
        "vtmin %g",
        """Control the minimum TEC voltage limit in V (float).""",
        validator=strict_range,
        values=[-3.3, 0.0],
        cast=float,
    )

    tec_voltage_limit_max = Instrument.control(
        "vtmax",
        "vtmax %g",
        """Control the maximum TEC voltage limit in V (float).""",
        validator=strict_range,
        values=[0.0, 3.3],
        cast=float,
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
        cast=float,
    )

    analog_input_2 = Instrument.measurement(
        "ain2",
        """Get the voltage on auxiliary input AI2 in V (float).""",
        cast=float,
    )

    laser_mod_gain = Instrument.control(
        "lmodgain",
        "lmodgain %g",
        """Control the laser current modulation gain of auxillary input 1 in
        A/V (float).""",
        cast=float,
        validator=strict_range,
        values=[-100, 100],
        get_process=lambda v: v * 1e-3,
        set_process=lambda v: v * 1e3,
    )

    tec_mod_gain = Instrument.control(
        "tmodgain",
        "tmodgain %g",
        """Control the temperature modulation gain of auxillary input 2 in
        Ω/V (float).""",
        cast=float,
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

    @property
    def status(self):
        """Get a dict with all status values ("lason", "vlaser", "itec",
        "vtec", "rtact","iphd", "ain1", "ain2")."""
        raw = self.ask("status").strip().split()
        keys = ["lason", "vlaser", "itec", "vtec", "rtact",
                "iphd", "ain1", "ain2"]
        result = {k: float(v) for k, v in zip(keys, raw)}
        result["iphd"] *= 1e-3
        return result

    board_temperature = Instrument.measurement(
        "tboard",
        """Get the current temperature of the driver board in °C (float).""",
        cast=float)

    def save(self):
        """Save the current configuration to internal non-volatile memory."""
        self.write("save")

    def clear_error(self):
        """Clear the error code."""
        self.write("errclr")

    error_status = Instrument.measurement(
        "err",
        """Get the current error status (IntFlag).""",
        get_process=lambda v: KoheronError(int(v)),
    )

    user_data = Instrument.control(
        "userdata",
        "userdata write %s",
        """Control the user data string saved on the device
        (max. 31 chars, str)""",
        cast=str,
        set_process=lambda v: str(v)[:31]
    )
