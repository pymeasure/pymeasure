#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
from time import sleep
from enum import IntFlag
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range, truncated_range, strict_discrete_set


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DPSeriesErrors(IntFlag):
    """ IntFlag type to decode error register queries. Error codes are as follows:

        0: no error
        1: Receive Overflow Error: serial communications had a receiving error.
        2: Encoder Error 1: encoder needed to correct the motor position.
        4: Encoder Error 2: encoder could not finish motor position correction.
        8: Command Error: a bad command was sent to the controller.
        16: Motor Error: motor speed profiles are set incorrectly.
        32: Range Overflow Error: go to position has an overflow error.
        64: Range Error: invalid number of commands and characters sent to the controller.
        128: Transmit Error: Too many parameters sent back to the pc.
        256: Mode Error: Controller is in a wrong mode.
        512: Zero Parameters Error: Command sent to the controller that expected to see
                                    parameters follow, but none were given.
        1024: Busy Error: The controller is busy indexing (moving a motor).
        2048: Memory Range Error: Specified address is out of range.
        4096: Memory Command Error: Command pulled from memory is invalid.
        8192: Thumbwheel Read Error: Error reading the thumbwheel, or thumbwheel is not present.
    """
    NO_ERR = 0
    RCV_OVERFLOW_ERR = 1
    ENC_ERR_1 = 2
    ENC_ERR_2 = 4
    CMD_ERR = 8
    MOT_ERR = 16
    RANGE_OVERFLOW_ERR = 32
    RANGE_ERR = 64
    TX_ERR = 128
    MODE_ERR = 256
    ZERO_PARAMS_ERR = 512
    BUSY_ERR = 1024
    MEM_RANGE_ERR = 2048
    MEM_CMD_ERR = 4096
    THBWHEEL_ERR = 8192


class DPSeriesMotorController(Instrument):
    """Base class to interface with Anaheim Automation DP series stepper motor controllers.

    This driver has been tested with the DPY50601 and DPE25601 motor controllers.
    """

    address = Instrument.control(
        "%", "~%i",
        """Integer property representing the address that the motor controller uses for serial
        communications.""",
        validator=strict_range,
        values=[0, 99],
        cast=int,
    )

    basespeed = Instrument.control(
        "VB", "B%i",
        """Integer property that represents the motor controller's starting/homing speed. This
        property can be set.""",
        validator=truncated_range,
        values=[1, 5000],
        cast=int,
    )

    maxspeed = Instrument.control(
        "VM", "M%i",
        """Integer property that represents the motor controller's maximum (running) speed.
        This property can be set.""",
        validator=truncated_range,
        values=[1, 50000],
        cast=int,
    )

    direction = Instrument.control(
        "V+", "%s",
        """A string property that represents the direction in which the stepper motor will rotate
        upon subsequent step commands. This property can be set. 'CW' corresponds to clockwise
        rotation and 'CCW' corresponds to counter-clockwise rotation.""",
        map_values=True,
        validator=strict_discrete_set,
        values={"CW": "+", "CCW": "-"},
        get_process=lambda d: "+" if d == 1.0 else "-",
    )

    encoder_autocorrect = Instrument.control(
        "VEA", "EA%i",
        """A boolean property to enable or disable the encoder auto correct function. This property
        can be set.""",
        map_values=True,
        values={True: 1, False: 0},
        validator=strict_discrete_set,
        cast=int,
    )

    encoder_delay = Instrument.control(
        "VED", "ED%i",
        """An integer property that represents the wait time in ms. after a move is finished before
        the encoder is read for a potential encoder auto-correct action to take place. This
        property can be set.""",
        validator=truncated_range,
        values=[0, 65535],
        cast=int,
    )

    encoder_motor_ratio = Instrument.control(
        "VEM", "EM%i",
        """An integer property that represents the ratio of the number of encoder pulses per motor
        step. This property can be set.""",
        validator=truncated_range,
        values=[1, 255],
        cast=int,
    )

    encoder_retries = Instrument.control(
        "VER", "ER%i",
        """An integer property that represents the number of times the motor controller will try the
        encoder auto correct function before setting an error flag. This property can be set.""",
        validator=truncated_range,
        values=[0, 255],
        cast=int,
    )

    encoder_window = Instrument.control(
        "VEW", "EW%i",
        """An integer property that represents the allowable error in encoder pulses from the
        desired position before the encoder auto-correct function runs. This property can be set.
        """,
        validator=truncated_range,
        values=[0, 255],
        cast=int,
    )

    busy = Instrument.measurement(
        "VF",
        """Query to see if the controller is currently moving a motor."""
    )

    error_reg = Instrument.measurement(
        "!",
        """Reads the current value of the error codes register.""",
        get_process=lambda err: DPSeriesErrors(int(err)),
    )

    def check_errors(self):
        """ Method to read the error codes register and log when an error is detected.

        :return error_code: one byte with the error codes register contents
        """
        current_errors = self.error_reg
        if current_errors != 0:
            logging.error("DP-Series motor controller error detected: %s" % current_errors)
        return current_errors

    def __init__(self, adapter, name="Anaheim Automation Stepper Motor Controller",
                 address=0, encoder_enabled=False, **kwargs):
        """
        Initialize communication with the motor controller with the address given by `address`.

        In addition to the keyword arguments that can be set for the Instrument base class, this
        class has the following kwargs:

        :param address: (int) Address that the motor controller uses for serial communiation.
        :param encoder_enabled: (bool) Flag to indicate if the driver should use an encoder input
            to set its position property.
        """
        self._address = address
        self._encoder_enabled = encoder_enabled
        kwargs.setdefault('write_termination', '\r')
        kwargs.setdefault('read_termination', '\r')
        kwargs.setdefault('timeout', 2000)

        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            asrl={'baud_rate': 38400},
            **kwargs
        )

    @property
    def encoder_enabled(self):
        """ A boolean property to represent whether an external encoder is connected and should be
        used to set the :attr:`step_position` property.
        """
        return self._encoder_enabled

    @encoder_enabled.setter
    def encoder_enabled(self, en):
        self._encoder_enabled = bool(en)

    @property
    def step_position(self):
        """ Integer property representing the value of the motor position measured in steps counted
        by the motor controller or, if :attr:`encoder_enabled` is set, the steps counted by an
        externally connected encoder. Note that in the DP series motor controller instrument
        manuals, this property would be referred to as the 'absolute position' while this
        driver implements a conversion between steps and absolute units for the
        :attr:`absolute_position` property. This property can be set.
        """
        if self._encoder_enabled:
            pos = self.ask("VEP")
        else:
            pos = self.ask("VZ")
        return int(pos)

    @step_position.setter
    def step_position(self, pos):
        strict_range(pos, (-8388607, 8388607))
        self.write("P%i" % pos)
        self.write("G")

    @property
    def absolute_position(self):
        """ Float property representing the value of the motor position measured in absolute units.
        Note that in DP series motor controller instrument manuals, 'absolute position' refers to
        the :attr:`step_position` property rather than this property. Also note that use of this
        property relies on :meth:`steps_to_absolute()` and :meth:`absolute_to_steps()`
        being implemented in a subclass. In this way, the user can define the conversion from a
        motor step position into any desired absolute unit. Absolute units could be the position in
        meters of a linear stage or the angular position of a gimbal mount, etc. This property can
        be set.
        """
        step_pos = self.step_position
        return self.steps_to_absolute(step_pos)

    @absolute_position.setter
    def absolute_position(self, abs_pos):
        steps_pos = self.absolute_to_steps(abs_pos)
        self.step_position = steps_pos

    def absolute_to_steps(self, pos):
        """ Convert an absolute position to a number of steps to move. This must be implemented in
        subclasses.

        :param pos: Absolute position in the units determined by the subclassed
               :meth:`absolute_to_steps()` method.
        """
        raise NotImplementedError("absolute_to_steps() must be implemented in subclasses!")

    def steps_to_absolute(self, steps):
        """ Convert a position measured in steps to an absolute position.

        :param steps: Position in steps to be converted to an absolute position.
        """
        raise NotImplementedError("steps_to_absolute() must be implemented in subclasses!")

    def reset_position(self):
        """
        Reset position as counted by the motor controller and an externally connected encoder to 0.
        """
        # reset encoder recorded position #
        self.write("ET")
        # reset motor recorded position #
        self.write("Z0")

    def stop(self):
        """Method that stops all motion on the motor controller."""
        self.write(".")

    def move(self, direction):
        """ Move the stepper motor continuously in the given direction until a stop command is sent
        or a limit switch is reached. This method corresponds to the 'slew' command in the DP
        series instrument manuals.

        :param direction: value to set on the direction property before moving the motor.
        """
        self.direction = direction
        self.write("S")

    def home(self, home_mode):
        """ Send command to the motor controller to 'home' the motor.

        :param home_mode: ``0`` or ``1`` specifying which homing mode to run.

            0 will perform a homing operation where the controller moves the motor until a soft
            limit is reached, then will ramp down to base speed and continue motion until a home
            limit is reached.

            In mode 1, the controller will move the motor until a limit is reached, then will ramp
            down to base speed, change direction, and run until the limit is released.
        """
        hm = int(home_mode)
        if hm == 0 or hm == 1:
            self.write("H%i" % hm)
        else:
            raise ValueError("Invalid home mode %i specified!" % hm)

    def write(self, command):
        """Override the instrument base write method to add the motor controller's address to the
        command string.

        :param command: command string to be sent to the motor controller.
        """
        # check if @ was already prepended when using say, the SerialAdapter #
        if "@" in command:
            cmd_str = command
        elif "%" in command or "~" in command:
            cmd_str = "@%s" % command
        else:
            cmd_str = "@%i%s" % (self._address, command)
        super().write(cmd_str)

    def wait_for_completion(self, interval=0.5):
        """ Block until the controller is not "busy" (i.e. block until the motor is no longer moving.)

        :param interval: (float) seconds between queries to the "busy" flag.
        :return: None
        """  # noqa: E501
        while self.busy:
            sleep(interval)
