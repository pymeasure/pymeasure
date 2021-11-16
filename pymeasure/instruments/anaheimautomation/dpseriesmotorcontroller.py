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

import asyncio
from pyvisa.errors import VisaIOError
from pymeasure.adapters import VISAAdapter
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set


class DPSeriesMotorController(Instrument):
    """Driver to interface with Anaheim Automation DP series stepper motor controllers. This driver has been tested with the DPY50601 and DPE25601 motor controllers. 
    """

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

    position = Instrument.control(
       "VZ", "Z%i",
       """An integer property that represents the step position as seen by the motor controller. This property can be set.""",
       validator=truncated_range,
       values=[-8388607, 8388607],
    ) 

    encoder_position = Instrument.measurement(
        "VEP", 
        """An integer property that represents the step position as counted by an externally connected encoder. This property cannot be set, but can be 
        reset to 0 using the reset_encoder_position() method.""",
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

    error_reg = Instrument.measurement(
        "!",
        "Reads the current value of the error codes register."
    )

    def __init__(self, resourceName, idn, encoder_enabled=False, **kwargs):
        """
        Initialize communication with the motor controller with id=idn. In addition to the keyword arguments that can be
        set for the Instrument base class, this class has the following kwargs:

        :param idn: (int) Assigned id of the motor controller.
        :param encoder_enabled: (bool) Flag to indicate if an encoder has been connected to the controller. 
        """
        self.idn = idn
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
        
    def reset_encoder_position(self):
        """ Reset the position as counted by an externally connected encoder to 0.
        """
        self.write("ET")

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
        self.write("G")

    def slew(self, direction):
        """Sends the slew command to the motor controller. This tells the controller to clock the stepper motor until a stop command is sent or a limit switch is reached.
        
        :param direction: value to set on the direction property before sending the slew command to the controller.
        """
        self.direction = direction
        self.write("S") 

    async def async_step(self, steps, direction, **kwargs):
        """ Asynchronous implementation of the step() method. This method can be awaited and will not return until the controller completes its step operation.
        """
        # call the normal step method #
        self.step(steps, direction)
        # wait until the step operation completes. # 
        await self.wait_for_completion(**kwargs)

    def write(self, command):
        """Override the instrument base write method to add the motor controller's id to the command string.
        
        :param command: command string to be sent to the motor controller.
        """
        self.adapter.write("@{}".format(self.idn) + command)

    def values(self, command, **kwargs):
        """ Override the instrument base values method to add the motor controller's id to the command string.
        
        :param command: command string to be sent to the motor controller.
        """
        return self.adapter.values("@{}".format(self.idn) + command, **kwargs)
        
    def ask(self, command):
        """ Override the instrument base ask method to add the motor controller's id to the command string.

        :param command: command string to be sent to the instrument
        """
        return self.adapter.ask("@{}".format(self.idn) + command)
   
    async def wait_for_completion(self, interval=0.5, threshold=3):
        """ Query the motor controller's step (or encoder) position and only return when inactivity is detected. Inactivity is 
            defined as when the previous queried position and current queried position match for "threshold" number of times.
        
        :param interval: (float) duration in seconds between controller position queries
        :param threshold: (int) number of times that the previous and current position must match before returning. 
        """
        pos_matches = 0
        prev_pos = None 
        while pos_matches < threshold:
            if self._encoder_enabled:
                pos = self.encoder_position
            else:
                pos = self.position
             
            if pos == prev_pos:
                pos_matches += 1

            prev_pos = pos 
            await asyncio.sleep(interval)


