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


from re import sub
from time import sleep

from pyvisa.constants import ControlFlow
from pyvisa.errors import VisaIOError

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class CommandError(Exception):
    """"Command error risen by the controller."""

    MESSAGES = {
        "@": "No error",
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
        "S": "Communication Time Out",
        "U": "Error during EEPROM access",
        "V": "Error during command execution",
        "W": "Command not allowed for PP version",
        "X": "Command not allowed for CC version"
    }

    def __init__(self, address, code):
        self.address = address
        self.code = code
        self.message = self.MESSAGES[self.code]
        super().__init__(f"""Newport SMC100 controller {self.address}
            reported the command error: {self.message}""")


class MotionError(Exception):
    """Motion error risen when unexpectedly changing state during
    motion.
    """

    def __init__(self, address, state):
        self.address = address
        self.state = state
        super().__init__(f"""Newport SMC100 controller {self.address}
            unexpectedly ended up in the state: {self.state}""")


class PositionerError(Exception):
    """Positioner error risen by the controller."""

    MESSAGES = [
        "80 W output power exceeded",
        "DC voltage too low",
        "Wrong ESP stage",
        "Homing time out",
        "Following error",
        "Short circuit detection ",
        "RMS current limit ",
        "Peak current limit ",
        "Positive end of run ",
        "Negative end of run"
    ]

    def __init__(self, address, list):
        self.address = address
        self.list = list
        self.message = ""
        for i, v in enumerate(self.list):
            if v:
                self.message += "* " + self.MESSAGES[i] + "\n"
        super().__init__(f"""Newport SMC100 controller {self.address}
            reported the positioner error(s):\n{self.message}""")


class ControllerState:
    """Controller State."""

    MESSAGES = {
        "0A": "NOT REFERENCED from reset",
        "0B": "NOT REFERENCED from HOMING",
        "0C": "NOT REFERENCED from CONFIGURATION",
        "0D": "NOT REFERENCED from DISABLE",
        "0E": "NOT REFERENCED from READY",
        "0F": "NOT REFERENCED from MOVING",
        "10": "NOT REFERENCED ESP stage error",
        "11": "NOT REFERENCED from JOGGING",
        "14": "CONFIGURATION",
        "1E": "HOMING commanded from RS-232-C",
        "1F": "HOMING commanded by SMC-RC",
        "28": "MOVING",
        "32": "READY from HOMING",
        "33": "READY from MOVING",
        "34": "READY from DISABLE",
        "35": "READY from JOGGING",
        "3C": "DISABLE from READY",
        "3D": "DISABLE from MOVING",
        "3E": "DISABLE from JOGGING",
        "46": "JOGGING from READY",
        "47": "JOGGING from DISABLE"
    }

    def __init__(self, code):
        self.code = code
        self.message = self.MESSAGES[self.code]
        self.ready = self.message.startswith("READY")
        self.disable = self.message.startswith("DISABLE")
        self.not_referenced = self.message.startswith("NOT REFERENCED")

    def __str__(self):
        return self.message


class SMC100(Instrument):
    """Represents the Newport SMC100 Motion Controller and provides a
    high-level interface for interacting with the instrument.

    Each SMC100 controls exactly one stage. The first controller is
    connected to the computer via RS232C, optionally adapted to USB.
    Other SMC100s can be chained to the first one via the internal RS485
    link. In this case, each one must have its own address. Refer to
    User Manual 3.3 for details.

    Refer to the User Manual for details on the functions. One should
    pay attention to the state of the controller when setting a
    parameter. This is especially true in the CONFIGURATION state.

    In the description of the properties, u stands for the preset unit.
    Default is mm and degrees for Newport stages.

    Three commands can be broadcast to all chained controllers:
    - Enter/Leave DISABLE state
    - Execute simultaneous started move
    - Stop motion
    These can be implemented by creating an SMC100 instance with
    address=0. Be careful: error checking is disabled for broadcast
    commands. Broadcasting wrong commands will show delayed errors when
    executing next addressed command.

    Setting address command is not implemented as it is discouraged in
    the User Manual.  Stepper motor, analog and TTL inputs, keypad and
    simultaneous started move related functions are not yet
    implemented.

    Example use:

    .. code-block:: python

        from pymeasure.instruments.newport import SMC100

        with SMC100("ASRL7::INSTR") as smc:
            smc.search_home()
            smc.wait_ready()
            smc.position = 10
            smc.wait_ready()
            smc.position += 5.5
            smc.stop()
        print(smc.state)
        print(smc)
        smc.reset()
    """

    # Class properties
    acceleration = Instrument.control(
        "AC?", "AC%g",
        """Get or set the acceleration.

        Type: Floating point number
        Range: ]1e-6, 1e12[
        Unit: u/s2""",
        validator=strict_range,
        values=(1e-6, 1e12),
        check_get_errors=True,
        check_set_errors=True
    )
    backlash = Instrument.control(
        "BA?", "BA%g",
        """Get or set the backlash compensation.

        Type: Floating point number
        Range: [0, 1e12[
        Unit: u""",
        validator=strict_range,
        values=(0, 1e12),
        check_get_errors=True,
        check_set_errors=True
    )
    control_loop = Instrument.setting(
        "SC%g",
        """Set the state of the control loop to OPEN or CLOSED.

        Type: String
        Range: "OPEN" or "CLOSED"
        Unit: None""",
        validator=strict_discrete_set,
        values=("OPEN", "CLOSED"),
        map_values=True,
        check_set_errors=True
    )
    current_peak = Instrument.control(
        "QIL?", "QIL%g",
        """Get or set the maximum peak current that the controller can
        deliver to the stage.

        Type: Floating point number
        Range: [5e-2, 3]
        Unit: A""",
        validator=strict_range,
        values=(5e-2, 3),
        check_get_errors=True,
        check_set_errors=True
    )
    current_rms = Instrument.control(
        "QIR?", "QIR%g",
        """Get or set the maximum rms current that the controller can
        deliver to the stage.

        Type: Floating point number
        Range: [5e-2, min(1.5, maximum peak current)]
        Unit: A""",
        validator=strict_range,
        values=(5e-2, 1.5),
        check_get_errors=True,
        check_set_errors=True
    )
    current_rms_time = Instrument.control(
        "QIT?", "QIT%g",
        """Get or set the maximum time during which a current greater
        than the maximum rms current can be delivered to the stage.

        Type: Floating point number
        Range: ]1e-2, 1e2]
        Unit: s""",
        validator=strict_range,
        values=(1e-2, 1e2),
        check_get_errors=True,
        check_set_errors=True
    )
    disable = Instrument.setting(
        "MM%g",
        """Change the state of the controller from READY to DISABLE or
        vice versa.

        Type: Boolean
        Range: True or False
        Unit: None""",
        validator=strict_discrete_set,
        values=(True, False),
        map_values=True,
        check_set_errors=True
    )
    configuration = Instrument.setting(
        "PW%g",
        """Change the state of the controller from NOT REFERENCED to
        CONFIGURATION or vice versa.

        Type: Boolean
        Range: True or False
        Unit: None""",
        validator=strict_discrete_set,
        values=(False, True),
        map_values=True,
        check_set_errors=True
    )
    error_command = Instrument.measurement(
        "TE",
        """Get the last command error code.

        "@" means that there is no memorized command error.

        This is the only measurement that doesn't check errors as it
        would cause an infinite loop.""",
        cast=str
    )
    error_following = Instrument.control(
        "FE?", "FE%g",
        """Get or set the limit for the following error.

        Type: Floating point number
        Range: ]1e-6, 1e12[
        Unit: u""",
        validator=strict_range,
        values=(1e-6, 1e12),
        check_get_errors=True,
        check_set_errors=True
    )
    error_positioner = Instrument.measurement(
        "TS",
        """Get the last positioner error.""",
        get_process=lambda v: [bool(int(c)) for c in bin(
            int(v[:4], 16))[2:].zfill(16)[6:]],
        check_get_errors=True,
        cast=str
    )
    filter_frequency = Instrument.control(
        "FD?", "FD%g",
        """Get or set the low-pass filter cut-off frequency.

        Type: Floating point number
        Range: ]1e-6, 2e3[
        Unit: Hz""",
        validator=strict_range,
        values=(1e-6, 2e3),
        check_get_errors=True,
        check_set_errors=True
    )
    friction = Instrument.control(
        "FF?", "FF%g",
        """Get or set the friction compensation.

        Type: Floating point number
        Range: [0, driving voltage[
        Unit: V*s/u""",
        validator=strict_range,
        values=(0, 48),
        check_get_errors=True,
        check_set_errors=True
    )
    home_search_time_out = Instrument.control(
        "OT?", "T%g",
        """Get or set the velocity for home search.

        Type: Floating point number
        Range: ]1, 1e3[
        Unit: s""",
        validator=strict_range,
        values=(1, 1e3),
        check_get_errors=True,
        check_set_errors=True
    )
    home_search_type = Instrument.control(
        "HT?", "HT%g",
        """Get or set the type of home search.

        Type: Interger
        Range: [0, 4]""",
        validator=strict_discrete_set,
        values=range(5),
        check_get_errors=True,
        check_set_errors=True,
        cast=int
    )
    home_search_velocity = Instrument.control(
        "OH?", "OH%g",
        """Get or set the velocity for home search.

        Type: Floating point number
        Range: ]1e-6, 1e12[
        Unit: u/s""",
        validator=strict_range,
        values=(1e-6, 1e12),
        check_get_errors=True,
        check_set_errors=True
    )
    hysteresis = Instrument.control(
        "BH?", "BH%g",
        """Get or set the hysteresis compensation.

        Type: Floating point number
        Range: [0, 1e12[
        Unit: u""",
        validator=strict_range,
        values=(0, 1e12),
        check_get_errors=True,
        check_set_errors=True
    )
    id = Instrument.measurement(
        "ID?",
        """Get the stage identifier.""",
        check_get_errors=True,
        cast=str
    )
    jerk = Instrument.control(
        "JR?", "JR%g",
        """Get or set the jerk time.

        Type: floating point number
        Range: ]1e-3, 1e12[
        Unit: s""",
        validator=strict_range,
        values=(1e-3, 1e12),
        check_get_errors=True,
        check_set_errors=True
    )
    limit_negative = Instrument.control(
        "SL?", "SL%g",
        """Get or set the negative software limit.

        Type: Floating point number
        Range: ]-1e12, 0]
        Unit: u""",
        validator=strict_range,
        values=(-1e12, 0),
        check_get_errors=True,
        check_set_errors=True
    )
    limit_positive = Instrument.control(
        "SR?", "SR%g",
        """Get or set the positive software limit.

        Type: Floating point number
        Range: [0, 1e12[
        Unit: u""",
        validator=strict_range,
        values=(0, 1e12),
        check_get_errors=True,
        check_set_errors=True
    )
    pid_d = Instrument.control(
        "KD?", "KD%g",
        """Get or set the derivative gain of the PID control loop.

        Type: Floating point number
        Range: [0, 1e12[
        Unit: V*s/u""",
        validator=strict_range,
        values=(0, 1e12),
        check_get_errors=True,
        check_set_errors=True
    )
    pid_ff = Instrument.control(
        "KV?", "KV%g",
        """Get or set the feed forward of the PID control loop.

        Type: Floating point number
        Range: [0, 1e12[
        Unit: V*s/u""",
        validator=strict_range,
        values=(0, 1e12),
        check_get_errors=True,
        check_set_errors=True
    )
    pid_i = Instrument.control(
        "KI?", "KI%g",
        """Get or set the integral gain of the PID control loop.

        Type: Floating point number
        Range: [0, 1e12[
        Unit: V*u/s""",
        validator=strict_range,
        values=(0, 1e12),
        check_get_errors=True,
        check_set_errors=True
    )
    pid_p = Instrument.control(
        "KP?", "KP%g",
        """Get or set the proportional gain of the PID control loop.

        Type: Floating point number
        Range: [0, 1e12[
        Unit: V/u""",
        validator=strict_range,
        values=(0, 1e12),
        check_get_errors=True,
        check_set_errors=True
    )
    position = Instrument.control(
        "TP", "PA%g",
        """Get current position or move to set position.

        Type: Floating point number
        Range: [left software limit, right software limit]
        Unit: u

        Example use:

        .. code-block:: python

            smc.position
            smc.position = 10
            smc.position += 1""",
        check_get_errors=True,
        check_set_errors=True
    )
    position_theoretical = Instrument.measurement(
        "TH",
        """Get the theoretical position.

        Type: Floating point number
        Range: [left software limit, right software limit]
        Unit: u""",
        check_get_errors=True
    )
    revision = Instrument.measurement(
        "VE",
        """Get the revision information of the controller.""",
        check_get_errors=True,
        cast=str
    )
    state = Instrument.measurement(
        "TS",
        """Get the controller state.

        Be careful: this command erases the last positioner error, which
        should be checked first if it is of interest.""",
        get_process=lambda v: ControllerState(v[-2:]),
        check_get_errors=True,
        cast=str
    )
    unit = Instrument.control(
        "SU?", "SU%g",
        """Get or set the value for one encoder count in the unit which
        is thus defined.

        Type: Floating point number
        Range: ]1e-6, 1e12[
        Unit: u""",
        validator=strict_range,
        values=(1e-6, 1e12),
        check_get_errors=True,
        check_set_errors=True
    )
    velocity = Instrument.control(
        "VA?", "VA%g",
        """Get or set the velocity.

        Type: Floating point number
        Range: ]1e-6, 1e12[
        Unit: u/s""",
        validator=strict_range,
        values=(1e-6, 1e12),
        check_get_errors=True,
        check_set_errors=True
    )
    voltage = Instrument.control(
        "DV?", "DV%g",
        """Get or set the maximum driver voltage.

        Type: Floating point number
        Range: [12, 48]
        Unit: V""",
        validator=strict_range,
        values=(12, 24),
        check_get_errors=True,
        check_set_errors=True
    )

    # Special methods
    def __init__(self, adapter, address=1, name="SMC100", **kwargs):
        """Set up connection to the controller."""
        self.address = str(address)
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            baud_rate=57600,
            flow_control=ControlFlow.xon_xoff,
            preprocess_reply=lambda v, address=self.address: sub(
                f"^{address}[A-Z]{{2}}[L,R,T]?", "", v),
            **kwargs
        )

    def __str__(self):
        """Return a string describing the controller settings."""
        message = "Newport SMC100 Motion Controller with the following\n"
        message += "settings (u stands for mm or deg by default):\n"
        message += f"* address: {self.address}\n"
        for k, v in self.__class__.__dict__.items():
            if type(v) is property and v.fget.__defaults__[0] is not None:
                unit = ""
                try:
                    unit += v.__doc__.split("Unit:")[1].split("\n")[0]
                except IndexError:
                    pass
                message += f"* {k}: {v.fget(self)}{unit}\n"
        return message[:-1]

    # Implementation or extension of Instrument parent class methods
    def check_errors(self):
        """Check for command error except when broadcasting."""
        if self.address != "0":
            self.check_command_error()

    def ask(self, command):
        return super().ask(self.address + command)

    def shutdown(self):
        """Stop any motion and put the controller in DISABLE state."""
        self.stop()
        self.wait_ready()
        self.disable = True
        super().shutdown()

    def values(self, command, **kwargs):
        return super().values(self.address + command, **kwargs)

    def write(self, command):
        super().write(self.address + command)

    # Other methods
    def check_command_error(self):
        """Check for and raise any command error."""
        error_code = self.error_command
        try:
            assert error_code == '@'
        except AssertionError:
            raise(CommandError(self.address, error_code))

    def check_motion_error(self):
        """Check for and raise any motion error.

        It implements this by verifying that the controller doesn't
        unexpectedly end up in DISABLE or NOT REFERENCED states, which
        indicates that an error happened during homing or moving. Using
        this command may hide positioner errors.
        """
        state = self.state
        try:
            assert not state.disable and not state.not_referenced
        except AssertionError:
            raise(MotionError(self.address, state))

    def check_positioner_error(self):
        """Check for and raise any positioner error."""
        errors = self.error_positioner
        try:
            assert not any(errors)
        except AssertionError:
            raise(PositionerError(self.address, errors))

    def get_motion_time(self, distance):
        """Get an evaluation of the time needed to complete a
        relative move.

        Argument: distance of the move in predefined unit.
        """
        return self.values("PT" + str(abs(distance)))[0]

    def reset(self):
        """Reset the controller."""
        self.write("RS")
        sleep(5)
        # Sequence necessary to avoid error on next command
        try:
            self.check_errors()
        except VisaIOError:
            pass

    def search_home(self, type=None, velocity=None, time_out=None):
        """Execute home search command.

        Keyword arguments:
        * type: type of home search
        * velocity: velocity used for home search in u/s
        * time_out: maximum time allowed to complete home search in s
        """
        if type is not None:
            self.home_search_type = type
            self.check_errors()
        if velocity is not None:
            self.home_search_velocity = velocity
            self.check_errors()
        if time_out is not None:
            self.home_search_time_out = time_out
            self.check_errors()
        self.write("OR")
        self.check_errors()

    def stop(self):
        """Stop the motion of the stage."""
        self.write("ST")
        self.check_errors()

    def wait_ready(self):
        """Wait until the state of the controller changes from HOMING
        or MOVING to READY.

        The command also checks for motion errors to avoid infinite
        loops. Using this command may hide positioner errors.
        """
        while not self.state.ready:
            self.check_motion_error()
            sleep(0.1)
