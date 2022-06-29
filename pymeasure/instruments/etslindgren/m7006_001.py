
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
import re
from datetime import datetime, timezone, timedelta
from turtle import position
import numpy as np
import pandas as pd
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    strict_discrete_set, strict_discrete_range,
    truncated_discrete_set, strict_range
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())



class M7006_001(Instrument):
    """ Position control card of EMCenter modular system.
        Allows for controll and feedback of the positioner card.
        Comunication happes transparently through the EMCenter mainframe.
        devices share the resource name of the mainframe, and 
        are identified by the slot number and the device number(if applicable to the modual).
    """

    def __init__(self,resource_name, slot=1, device='A', **kwargs):

        kwargs.setdefault('write_termination', '\n')
        super().__init__(
            resource_name,
            "test",
            **kwargs
        )
        self._slot = slot
        self._device = device

  
    @property
    def acceleration(self):
        return self.adapter.ask(f'{self._slot}lf._device}ACC?')
    
    @acceleration.setter
    def acceleration(self, value):
        value = strict_range(value, 0.1, 30.0)
        return self.adapter.ask(f'{self._slot}{self._device}ACC {value}')

    @property
    def speed(self):
        return self.adapter.ask(f'{self._slot}{self._device}SPEED?')
    
    @speed.setter
    def speed(self, value):
        value = strict_range(value, 0.0, 100.0)
        return self.adapter.write(f'{self._slot}{self._device}SPEED {value}')
    
    @property
    def aux_output(self, number=1):
        number = strict_discrete_set(number, 1, 2)
        return self.adapter.write(f'{self._slot}{self._device}AUX{number}?')
    
    @aux_output.setter
    def aux_output(self, value, number=1):
        number = strict_discrete_set(number, 1, 2)
        value = strict_discrete_set(value, 'ON', 'OFF')
        return self.adapter.write(f'{self._slot}{self._device}AUX{number} {value}')

    def counter_clockwise(self):
        return self.adapter.write(f'{self._slot}{self._device}CC')
    
    def clockwise(self):
        return self.adapter.write(f'{self._slot}{self._device}CW')

    def down(self):
        return self.adapter.write(f'{self._slot}{self._device}DN')
    
    def up(self):
        return self.adapter.write(f'{self._slot}{self._device}UP')

    def stop(self):
        return self.adapter.write(f'{self._slot}{self._device}ST')
    
    @property
    def polarity(self):
        
        result = self.adapter.write(f'{self._slot}{self._device}P?')
        if result== 1:
            return 'H'
        elif  result == 0:
            return 'V'
        else:
            raise ValueError('Polarity not recognized')
    
    

    
    @polarity.setter
    def polarity(self, value):
        value = strict_discrete_set(value, 'H', 'V')
        value = map()
        return self.adapter.write(f'{self._slot}{self._device}P{value}')


    
    @property
    def position(self):
        """ Returns the current position of the device. """
        return self.adapter.ask(f'{self._slot}{self._device}CP?')
    
    @position.setter
    def position(self, value):
        """ Sets the current position of the device. does not move the device. """
        value = strict_range(value, -999.9, 999.9)
        return self.adapter.write(f'{self._slot}{self._device}CP {value}')
    
    def direction(self):
        return self.adapter.write(f'{self._slot}{self._device}DIR?')

    def seek_position(self, position):
        """ Moves the device to the specified position. by the shortest distance. """
        position = strict_range(position, -999.9, 999.9)
        return self.adapter.write(f'{self._slot}{self._device}SK {position}')
    
    def seek_negative_postion(self, position):
        """ Moves the device to the specified position, in the down or counter clockwise direction. """
        position = strict_range(position, -999.9, 999.9)
        return self.adapter.write(f'{self._slot}{self._device}SKN {position}')
    
    def seek_positive_postion(self, position):
        """ Moves the device to the specified position, in the up or clockwise direction. """
        position = strict_range(position, -999.9, 999.9)
        return self.adapter.write(f'{self._slot}{self._device}SKP {position}')
    
    def seek_relative_postion_rela(self, position):
        """ Moves the device to the specified position relative to the current position. """
        position = strict_range(position, -999.9, 999.9)
        return self.adapter.write(f'{self._slot}{self._device}SKR {position}')


