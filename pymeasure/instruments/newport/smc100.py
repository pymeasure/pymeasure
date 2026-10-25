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
from enum import Enum, IntEnum, IntFlag
from itertools import takewhile

from pyvisa.constants import ControlFlow

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

MAX_VALUE = 1e12


class SMC100ControllerState(Enum):
    """Main state of the SMC100 state machine (see section 5.1 of the user manual)."""

    NOT_REFERENCED = "NOT_REFERENCED"
    CONFIGURATION = "CONFIGURATION"
    HOMING = "HOMING"
    MOVING = "MOVING"
    READY = "READY"
    DISABLE = "DISABLE"
    JOGGING = "JOGGING"


class SMC100StateCode(IntEnum):
    """Detailed controller state as reported by the ``TS`` command."""

    NOT_REFERENCED_FROM_RESET = 0x0A
    NOT_REFERENCED_FROM_HOMING = 0x0B
    NOT_REFERENCED_FROM_CONFIGURATION = 0x0C
    NOT_REFERENCED_FROM_DISABLE = 0x0D
    NOT_REFERENCED_FROM_READY = 0x0E
    NOT_REFERENCED_FROM_MOVING = 0x0F
    NOT_REFERENCED_ESP_STAGE_ERROR = 0x10
    NOT_REFERENCED_FROM_JOGGING = 0x11
    CONFIGURATION = 0x14
    HOMING_FROM_RS232 = 0x1E
    HOMING_FROM_KEYPAD = 0x1F
    MOVING = 0x28
    READY_FROM_HOMING = 0x32
    READY_FROM_MOVING = 0x33
    READY_FROM_DISABLE = 0x34
    READY_FROM_JOGGING = 0x35
    DISABLE_FROM_READY = 0x3C
    DISABLE_FROM_MOVING = 0x3D
    DISABLE_FROM_JOGGING = 0x3E
    JOGGING_FROM_READY = 0x46
    JOGGING_FROM_DISABLE = 0x47

    @property
    def controller_state(self) -> SMC100ControllerState:
        """Get the main state of the state machine this detailed state belongs to."""
        return next(s for s in SMC100ControllerState if self.name.startswith(s.value))


class SMC100PositionerError(IntFlag):
    """Positioner error flags as reported by the ``TS`` command."""

    NONE = 0
    NEGATIVE_END_OF_RUN = 1 << 0
    POSITIVE_END_OF_RUN = 1 << 1
    PEAK_CURRENT_LIMIT = 1 << 2
    RMS_CURRENT_LIMIT = 1 << 3
    SHORT_CIRCUIT_DETECTION = 1 << 4
    FOLLOWING_ERROR = 1 << 5
    HOMING_TIME_OUT = 1 << 6
    WRONG_ESP_STAGE = 1 << 7
    DC_VOLTAGE_TOO_LOW = 1 << 8
    OUTPUT_POWER_EXCEEDED = 1 << 9


COMMAND_ERRORS = {
    "A": "Unknown message code or floating point controller address",
    "B": "Controller address not correct",
    "C": "Parameter missing or out of range",
    "D": "Command not allowed",
    "E": "Home sequence already started",
    "F": "ESP stage name unknown",
    "G": "Displacement out of limits",
    "H": "Command not allowed in NOT REFERENCED state",
    "I": "Command not allowed in CONFIGURATION state",
    "J": "Command not allowed in DISABLE state",
    "K": "Command not allowed in READY state",
    "L": "Command not allowed in HOMING state",
    "M": "Command not allowed in MOVING state",
    "N": "Current position out of software limit",
    "S": "Communication time out",
    "U": "Error during EEPROM access",
    "V": "Error during command execution",
    "W": "Command not allowed for PP version",
    "X": "Command not allowed for CC version",
}


class SMC100CommandError(Exception):
    """Raised when the SMC100 refuses to execute a command."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Newport SMC100 command error {code}: {message}")


def _parse_status(reply: str) -> tuple[SMC100PositionerError, SMC100StateCode]:
    return SMC100PositionerError(int(reply[:4], 16)), SMC100StateCode(int(reply[4:6], 16))


class SMC100(Instrument):
    """Represent the Newport SMC100 single-axis motion controller.

    This class implements the commands shared by the stepper motor (:class:`SMC100PP`) and
    DC motor (:class:`SMC100CC`) versions. Prefer these subclasses, which add the
    model-specific parameters.

    The controller is unit agnostic: positions, velocities and accelerations are in the
    preset units of the connected stage (for example mm or degrees).

    Several controllers can share a single RS-232 port via their internal RS-485 link,
    in which case each of them is addressed via its controller ``address``.

    .. code-block:: python

        from pymeasure.instruments.newport import SMC100PP

        stage = SMC100PP("ASRL/dev/ttyUSB0::INSTR")
        stage.home()  # only possible in NOT_REFERENCED state
        stage.wait_until_ready()
        stage.velocity = 8
        stage.position = 45
        stage.wait_until_ready()
        print(stage.position)

    :param adapter: The adapter or resource name of the instrument.
    :param name: The name of the instrument.
    :param address: The controller address on the RS-485 link (int from 1 to 31).
    :param \\**kwargs: Further keyword arguments handed to the adapter.
    """

    def __init__(self, adapter, name="Newport SMC100 motion controller", address=1, **kwargs):
        super().__init__(
            adapter,
            name,
            asrl={
                "baud_rate": 57600,
                "flow_control": ControlFlow.xon_xoff,
                "read_termination": "\r\n",
                "write_termination": "\r\n",
            },
            **kwargs,
        )
        self.address = strict_range(address, (1, 31))
        self._last_mnemonic = ""

    def write(self, command: str, **kwargs) -> None:
        """Write a command prefixed by the controller address.

        :param command: Command string without the controller address.
        :param kwargs: Keyword arguments for the adapter.
        """
        self._last_mnemonic = "".join(takewhile(str.isalpha, command)).upper()
        super().write(f"{self.address}{command}", **kwargs)

    def read(self, **kwargs) -> str:
        """Read a reply and strip the echoed controller address and command.

        :raises ConnectionError: If the reply does not echo the last command.
        """
        reply = super().read(**kwargs)
        prefix = f"{self.address}{self._last_mnemonic}"
        if not reply.startswith(prefix):
            raise ConnectionError(f"Unexpected reply '{reply}', expected prefix '{prefix}'.")
        return reply[len(prefix):].strip()

    def check_errors(self) -> list[tuple[str, str]]:
        """Read the error of the last command and log it.

        :return: List with a ``(code, message)`` tuple, or an empty list if there was no error.
        """
        code = self.ask("TE")
        if code == "@":
            return []
        message = COMMAND_ERRORS.get(code, "Unknown error")
        log.error(f"{self.name}: {code}, {message}")
        return [(code, message)]

    def check_set_errors(self) -> list[tuple[str, str]]:
        """Check the error of the last command.

        :raises SMC100CommandError: If the controller refused to execute the command, e.g.
            because it is not allowed in the current state.
        """
        errors = self.check_errors()
        if errors:
            raise SMC100CommandError(*errors[0])
        return errors

    # Status

    firmware_version = Instrument.measurement(
        "VE",
        """Get the controller model and firmware version (str).""",
        cast=str,
    )

    stage_identifier = Instrument.measurement(
        "ID?",
        """Get the stage identifier (str).""",
        cast=str,
    )

    status = Instrument.measurement(
        "TS",
        """Get the positioner error flags and the detailed controller state
        (tuple of :class:`SMC100PositionerError` and :class:`SMC100StateCode`).""",
        cast=str,
        get_process=_parse_status,
    )

    @property
    def state(self) -> SMC100StateCode:
        """Get the detailed controller state (:class:`SMC100StateCode`)."""
        return self.status[1]

    @property
    def positioner_error(self) -> SMC100PositionerError:
        """Get the positioner error flags (:class:`SMC100PositionerError`)."""
        return self.status[0]

    # Motion

    position = Instrument.control(
        "TP",
        "PA%g",
        """Control the position in preset units (float).

        Setting starts an absolute move, which is only possible in READY state.
        Use :meth:`wait_until_ready` to wait for the end of the move.""",
        check_set_errors=True,
    )

    setpoint = Instrument.measurement(
        "TH",
        """Get the target position of the ongoing (or last) move in preset units (float).""",
    )

    def move_relative(self, displacement: float) -> None:
        """Start a move relative to the current position.

        :param displacement: Displacement in preset units.
        """
        self.write(f"PR{displacement:g}")
        self.check_set_errors()

    def get_motion_time(self, displacement: float) -> float:
        """Get the time the controller needs for a relative move with the current profile.

        :param displacement: Displacement in preset units.
        :return: Motion time in seconds.
        """
        return float(self.ask(f"PT{abs(displacement):g}"))

    def stop(self) -> None:
        """Stop the ongoing motion or home search."""
        self.write("ST")

    def home(self) -> None:
        """Start a home search, which is only possible in NOT_REFERENCED state.

        Use :meth:`wait_until_ready` to wait for the end of the home search.
        """
        self.write("OR")
        self.check_set_errors()

    def wait_until_ready(self, timeout: float = 60, interval: float = 0.1) -> None:
        """Block until the controller reaches the READY state, e.g. after a move or homing.

        :param timeout: Maximum time to wait in seconds.
        :param interval: Polling interval in seconds.
        :raises RuntimeError: If the controller ends up in a state it cannot leave by itself,
            e.g. DISABLE after a following error.
        :raises TimeoutError: If the READY state is not reached within ``timeout``.
        """
        stuck_states = (
            SMC100ControllerState.NOT_REFERENCED,
            SMC100ControllerState.CONFIGURATION,
            SMC100ControllerState.DISABLE,
        )
        deadline = time.monotonic() + timeout
        while True:
            error, state = self.status
            if state.controller_state == SMC100ControllerState.READY:
                return
            if state.controller_state in stuck_states:
                raise RuntimeError(
                    f"{self.name} will not become READY, state: {state.name}, "
                    f"positioner error: {error!r}."
                )
            if time.monotonic() > deadline:
                raise TimeoutError(f"{self.name} not READY after {timeout} s, state: {state.name}.")
            time.sleep(interval)

    def enable(self) -> None:
        """Leave the DISABLE state into the READY state."""
        self.write("MM1")
        self.check_set_errors()

    def disable(self) -> None:
        """Enter the DISABLE state from the READY state, switching off the motor control."""
        self.write("MM0")
        self.check_set_errors()

    def reset(self, wait: bool = True) -> None:
        """Reset the controller, equivalent to a power-up, which leads to NOT_REFERENCED state.

        :param wait: Wait for the controller to finish its startup (about 5 s).
        """
        self.write("RS")
        if wait:
            time.sleep(5)
            # The controller may emit spurious characters while booting.
            self.adapter.flush_read_buffer()

    def enter_configuration(self) -> None:
        """Enter the CONFIGURATION state, which is only possible in NOT_REFERENCED state.

        In this state, parameters are changed in the non-volatile memory and stay effective
        after a reset.
        """
        self.write("PW1")
        self.check_set_errors()

    def exit_configuration(self) -> None:
        """Store the configuration in memory and return to NOT_REFERENCED state.

        Storing takes up to 10 s.
        """
        self.write("PW0")
        deadline = time.monotonic() + 10
        while self.state.controller_state == SMC100ControllerState.CONFIGURATION:
            if time.monotonic() > deadline:
                raise TimeoutError(f"{self.name} did not leave CONFIGURATION state.")
            time.sleep(0.1)

    # Motion profile and limits

    velocity = Instrument.control(
        "VA?",
        "VA%g",
        """Control the velocity in preset units per second (float strictly from 1e-6 to 1e12).""",
        validator=strict_range,
        values=(1e-6, MAX_VALUE),
        check_set_errors=True,
    )

    acceleration = Instrument.control(
        "AC?",
        "AC%g",
        """Control the acceleration in preset units per second squared
        (float strictly from 1e-6 to 1e12).""",
        validator=strict_range,
        values=(1e-6, MAX_VALUE),
        check_set_errors=True,
    )

    jerk_time = Instrument.control(
        "JR?",
        "JR%g",
        """Control the jerk time in seconds, i.e. the time to reach the acceleration
        (float strictly from 0.001 to 1e12).""",
        validator=strict_range,
        values=(0.001, MAX_VALUE),
        check_set_errors=True,
    )

    software_limit_negative = Instrument.control(
        "SL?",
        "SL%g",
        """Control the negative software limit in preset units (float strictly from -1e12 to 0).""",
        validator=strict_range,
        values=(-MAX_VALUE, 0),
        check_set_errors=True,
    )

    software_limit_positive = Instrument.control(
        "SR?",
        "SR%g",
        """Control the positive software limit in preset units (float strictly from 0 to 1e12).""",
        validator=strict_range,
        values=(0, MAX_VALUE),
        check_set_errors=True,
    )

    backlash = Instrument.control(
        "BA?",
        "BA%g",
        """Control the backlash compensation in preset units (float strictly from 0 to 1e12).

        Can only be changed in CONFIGURATION state.""",
        validator=strict_range,
        values=(0, MAX_VALUE),
        check_set_errors=True,
    )

    peak_current_limit = Instrument.control(
        "QIL?",
        "QIL%g",
        """Control the motor peak output current limit in Ampere (float).

        Can only be changed in CONFIGURATION state.""",
        check_set_errors=True,
    )

    # Home search

    home_search_type = Instrument.control(
        "HT?",
        "HT%d",
        """Control the home search type (int strictly in 0 to 4).

        0: use MZ switch and encoder index, 1: use current position as home,
        2: use MZ switch only, 3: use end of run switch and encoder index,
        4: use end of run switch only.
        Can only be changed in CONFIGURATION state.""",
        validator=strict_discrete_set,
        values=range(5),
        cast=int,
        check_set_errors=True,
    )

    home_velocity = Instrument.control(
        "OH?",
        "OH%g",
        """Control the home search velocity in preset units per second
        (float strictly from 1e-6 to 1e12).

        Can only be changed in CONFIGURATION state.""",
        validator=strict_range,
        values=(1e-6, MAX_VALUE),
        check_set_errors=True,
    )

    home_timeout = Instrument.control(
        "OT?",
        "OT%g",
        """Control the home search time-out in seconds (float strictly from 1 to 1000).

        Can only be changed in CONFIGURATION state.""",
        validator=strict_range,
        values=(1, 1000),
        check_set_errors=True,
    )


class SMC100PP(SMC100):
    """Represent the Newport SMC100PP motion controller for stepper motors.

    See :class:`SMC100` for the parameters and an example.
    """

    def __init__(self, adapter, name="Newport SMC100PP motion controller", **kwargs):
        super().__init__(adapter, name, **kwargs)

    base_velocity = Instrument.control(
        "VB?",
        "VB%g",
        """Control the base velocity in preset units per second (float strictly from 0 to 1e12).

        Can only be changed in CONFIGURATION state.""",
        validator=strict_range,
        values=(0, MAX_VALUE),
        check_set_errors=True,
    )

    micro_step_factor = Instrument.control(
        "FRM?",
        "FRM%d",
        """Control the number of micro-steps per full step (int strictly from 1 to 2000).

        Can only be changed in CONFIGURATION state.""",
        validator=strict_range,
        values=(1, 2000),
        cast=int,
        check_set_errors=True,
    )


class SMC100CC(SMC100):
    """Represent the Newport SMC100CC motion controller for DC motors.

    See :class:`SMC100` for the parameters and an example.
    """

    def __init__(self, adapter, name="Newport SMC100CC motion controller", **kwargs):
        super().__init__(adapter, name, **kwargs)

    proportional_gain = Instrument.control(
        "KP?",
        "KP%g",
        """Control the proportional gain Kp of the PID loop (float strictly from 0 to 1e12).""",
        validator=strict_range,
        values=(0, MAX_VALUE),
        check_set_errors=True,
    )

    integral_gain = Instrument.control(
        "KI?",
        "KI%g",
        """Control the integral gain Ki of the PID loop (float strictly from 0 to 1e12).""",
        validator=strict_range,
        values=(0, MAX_VALUE),
        check_set_errors=True,
    )

    derivative_gain = Instrument.control(
        "KD?",
        "KD%g",
        """Control the derivative gain Kd of the PID loop (float strictly from 0 to 1e12).""",
        validator=strict_range,
        values=(0, MAX_VALUE),
        check_set_errors=True,
    )

    friction_compensation = Instrument.control(
        "FF?",
        "FF%g",
        """Control the friction compensation in Volt (float strictly from 0 to 1e12).""",
        validator=strict_range,
        values=(0, MAX_VALUE),
        check_set_errors=True,
    )

    closed_loop_enabled = Instrument.control(
        "SC?",
        "SC%d",
        """Control whether the position control loop is closed (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
        check_set_errors=True,
    )
