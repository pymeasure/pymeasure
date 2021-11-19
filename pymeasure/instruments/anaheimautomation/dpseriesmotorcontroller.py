#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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
from pyvisa.errors import VisaIOError
from pymeasure.adapters import VISAAdapter
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
    """Driver to interface with Anaheim Automation DP series stepper motor controllers. This driver has been tested with the DPY50601 and DPE25601 motor controllers. 
    """

    address = Instrument.control(
        "%", "~%i",
        """Integer property representing the address that the motor controller uses for serial communications.""",
        validator=strict_range,
        values=[0, 99],
    )
    
    basespeed = Instrument.control(
        "VB", "B%i", 
        """Integer property that represents the motor controller's starting/homing speed. This property can be set.""",
        validator=truncated_range,
        values=[1, 5000],
    )
    
    maxspeed = Instrument.control(
        "VM", "M%i", 
        """Integer property that represents the motor controller's maximum (running) speed. This property can be set.""",
        validator=truncated_range,
        values=[1, 50000],
    )

    direction = Instrument.control(
        "V+", "%s",
        """A string property that represents the direction in which the stepper motor will rotate upon subsequent step commands. This property can be set. 'CW' corresponds to clockwise rotation and 'CCW' corresponds to counter-clockwise rotation.""",
        map_values=True, 
        validator=strict_discrete_set,
        values={"CW" : "+", "CCW" : "-"},
        get_process=lambda d: "+" if d == 1.0 else "-",
    )    

    steps = Instrument.control(
        "VN", "N%i",
        """An integer property that represents the number of steps the motor controller will run upon the next 'G' (go) command that is sent to the controller. This property can be set.""",
        validator=truncated_range,
        values=[0, 8388607],
    )
    
    encoder_autocorrect = Instrument.control(
        "VEA", "EA%i",
        """A boolean property to enable or disable the encoder auto correct function. This property can be set.""",
        map_values=True, 
        values={True: 1, False: 0},
        validator=strict_discrete_set,
        get_process=lambda ea: int(ea),
    )

    encoder_delay = Instrument.control(
        "VED", "ED%i",
        """An integer property that represents the wait time in ms. after move is finished before
           the encoder is read for a potential encoder auto-correct action to take place. This property can be set.""",
        validator=truncated_range,
        values=[0, 65535], 
    )

    encoder_motor_ratio = Instrument.control(
        "VEM", "EM%i",
        """An integer property that represents the ratio of the number of encoder pulses per motor step. This property can be set.""",
        validator=truncated_range,
        values=[1, 255],
    )

    encoder_retries = Instrument.control(
        "VER", "ER%i",
        """An integer property that represents the number of times the motor controller will try
           the encoder auto correct function before setting an error flag. This property can be set.""",
        validator=truncated_range,
        values=[0, 255],
    )

    encoder_window = Instrument.control(
        "VEW", "EW%i",
        """An integer property that represents the allowable error in encoder pulses from the desired
           position before the encoder auto-correct function runs. This property can be set.""",
        validator=truncated_range,
        values=[0, 255],
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
    
    def __init__(self, resourceName, address=0, encoder_enabled=False, **kwargs):
        """
        Initialize communication with the motor controller with id=idn. In addition to the keyword arguments that can be
        set for the Instrument base class, this class has the following kwargs:

        :param address: (int) Address that the motor controller uses for serial communiations.
        :param encoder_enabled: (bool) Flag to indicate if an encoder has been connected to the controller. 
        """
        self._address = address
        self._encoder_enabled = encoder_enabled 

        super().__init__(
            resourceName,
            "Anaheim Automation Stepper Motor Controller",
            includeSCPI=False,
            write_termination="\r",
            read_termination="\r",
            timeout=2000, 
            **kwargs
        )
        
        if isinstance(self.adapter, VISAAdapter):
            self.adapter.connection.baud_rate = 38400
    
    @property
    def encoder_enabled(self):
        """
        Return the value of the _encoder_enabled flag.
        """
        return self._encoder_enabled

    @encoder_enabled.setter
    def encoder_enabled(self, en):
        """ Set the value of the _encoder_enabled flag. When set, asynchronous coroutine methods like step_async() will query
            the "encoder_position" property instead of the "position" property.

        :param en: (bool) boolean value to set the _encoder_enabled flag with
        """
        self._encoder_enabled = bool(en)
    
    @property
    def step_position(self):
        """
        Return the value of the motor position measured in steps counted by the motor controller or, if encoder_enabled is set, return the
        steps counted by an externally connected encoder.
        """
        if self._encoder_enabled:
            pos = self.ask("VEP")
        else:
            pos = self.ask("VZ")    
        return pos
    
    @step_position.setter
    def step_position(self, pos):
        """ Sends command to the motor controller to move to the desired step position. Note that in DP series controller instrument manuals, this property corresponds to the 'absolute position' command. In this driver, the `absolute_position` property implements a conversion between steps to absolute units whereas the DP series manuals refer to `absolute position` as measured in steps.
        """
        step_pos = int(pos)
        if -8388607 < step_pos < 8388607:
            self.write("P%i" % step_pos)
            self.go()
        else:
            raise ValueError("Provided step position out of valid range!")
    
    @property
    def absolute_position(self):
        """
        Return the absolute position of the motor in units determined by the steps_to_position() method.
        """
        step_pos = self.step_position
        return self.steps_to_absolute(step_pos)
    
    @absolute_position.setter
    def absolute_position(self, abs_pos):
        """ 
        Move the motor to the absolute position provided. Note that the absolute_to_steps()
        method must be implemented in a subclass for this to work.
        
        :param abs_pos: absolute position in units determined by the absolute_to_steps() method.
        """
        steps_pos = self.absolute_to_steps(abs_pos)
        self.step_position = steps_pos
    
    def absolute_to_steps(self, pos):
        """ Convert an absolute position to a number of steps to move. This must be implemented in subclasses.
        
        :param pos: Absolute position in the units determined by the subclassed position_to_steps() method.
        """
        raise NotImplementedError("absolute_to_steps() must be implemented in subclasses!")   
    
    def steps_to_absolute(self, steps):
        """ Convert a position measured in steps to an absolute position.
        
        :param steps: Position in steps to be converted to an absolute position.
        """
        raise NotImplementedError("steps_to_position() must be implemented in subclasses!")
    
    def reset_position(self):
        """ Reset the position as counted by the motor controller and an externally connected encoder to 0.
        """
        # reset encoder recorded position #
        self.write("ET")
        # reset motor recorded position #
        self.write("Z0")

    def stop(self):
        """Method that stops all motion on the motor controller."""
        self.write(".")

    def go(self):
        """Method that sends the G command to the controller to tell the controller to turn the 
           motor the number of steps previously set with the steps property."""
        self.write("G")

    def step(self, steps, direction):
        """Similar to the go() method, but also sets the number of steps and the direction in the same method.
        
        :param steps: Number of steps to clock
        :param direction: Value to set on the direction property before sending the go command to the controller. Valid values of direction are those than can be set on the direction property ("CW" for clockwise or "CCW" for counter-clockwise).
        """
        self.steps = steps 
        self.direction = direction
        self.go()
        
    def slew(self, direction):
        """Sends the slew command to the motor controller. This tells the controller to move the stepper motor until a stop command is sent or a limit switch is reached.
        
        :param direction: value to set on the direction property before sending the slew command to the controller.
        """
        self.direction = direction
        self.write("S") 
    
    def home(self, home_mode):
        """ Send command to the motor controller to 'home' the motor.
        
        :param home_mode: 0 or 1 specifying which homing mode to run.
                          0:
                              DP series controller moves motor until a soft limit is reached, then ramp down to base speed. Motion will continue until a home limit is reached.
                          
                          1: 
                              DP series controller moves until a limit is reached, then ramps down to base speed, changes direction and runs until the limit is released.
        """
        hm = int(home_mode)
        if hm == 0 or hm == 1:
            self.write("H%i" % hm)
        else:
            raise ValueError("Invalid home mode %i specified!" % hm)
    
    def write(self, command):
        """Override the instrument base write method to add the motor controller's id to the command string.
        
        :param command: command string to be sent to the motor controller.
        """
        # check if an address related command was sent. #
        if "%" in command or "~" in command:
            super().write("@%s" % command)
        else:
            super().write("@%i%s" % (self.address, command))

    def values(self, command, **kwargs):
        """ Override the instrument base values method to add the motor controller's id to the command string.
        
        :param command: command string to be sent to the motor controller.
        """
        # check if an address related command was sent. #
        if "%" in command or "~" in command:
            vals = super().values("@%s" % command, **kwargs)
        else:
            vals = super().values("@%i%s" % (self.address, command))

        return vals
    
    def ask(self, command):
        """ Override the instrument base ask method to add the motor controller's id to the command string.

        :param command: command string to be sent to the instrument
        """
        # check if an address related command was sent. #
        if "%" in command or "~" in command:
            val = super().ask("@%s" % command)
        else:
            val = super().ask("@%i%s" % (self.address, command))

        return val



