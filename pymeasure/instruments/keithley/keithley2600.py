#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure Developers
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
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


import visa
import numpy as np
import time
from io import BytesIO


class Keithley2600(Instrument):
    """This is the class for the Keithley 2600-series instruments"""

    def __init__(self, resourceName, **kwargs):
        super(Keithley2600, self).__init__(
            resourceName,
            "Keithley 2600 Sourcemeter",
            includeSCPI=False,
            **kwargs
        )
        self.adapter.connection.read_termination = '\n'

    def get_currentA(self):
        '''Get the current reading for channel A.'''
        return float(self.ask('print(smua.measure.i())'))

    @property
    def currentA(self):
        '''Get the current reading for channel A.'''
        return float(self.ask('print(smua.measure.i())'))
    @property
    def currentB(self):
        '''Get the current reading for channel B.'''
        return float(self.ask('print(smub.measure.i())'))
    @currentA.setter
    def currentA(self, value):
        '''Set the source current for channel A.'''
        self.write('smua.source.func=smua.OUTPUT_DCAMPS;smua.source.leveli=%s' % value)
    @currentB.setter
    def currentB(self, value):
        '''Set the source current for channel B.'''
        self.write('smub.source.func=smub.OUTPUT_DCAMPS;smub.source.leveli=%s' % value)

    @property
    def voltageA(self):
        '''Get the voltage reading for channel A'''
        return float(self.ask('print(smua.measure.v())'))
    @property
    def voltageB(self):
        '''Get the voltage reading for channel B'''
        return float(self.ask('print(smub.measure.v())'))
    @voltageA.setter
    def voltageA(self, value):
        '''Set the source voltage for channel A.'''
        self.write('smua.source.func=smua.OUTPUT_DCVOLTS;smua.source.levelv=%s' % value)
    @voltageB.setter
    def voltageB(self, value):
        '''Set the source voltage for channel B.'''
        self.write('smub.source.func=smub.OUTPUT_DCVOLTS;smub.source.levelv=%s' % value)

    @property
    def modeA(self):
        '''Get the source function for channel A.'''
        return self.ask('print(smuA.source.func())')
    @property
    def modeB(self):
        '''Get the source function for channel B.'''
        return self.ask('print(smuB.source.func())')
    @modeA.setter
    def modeA(self, value):
        '''Set the source function ('voltage' or 'current') for channel A'''
        value={'voltage':'OUTPUT_DCVOLTS','current':'OUTPUT_DCAMPS'}[value]
        self.write('smua.source.func=smua.%s' % value)
    @modeB.setter
    def modeB(self, value):
        '''Set the source function ('voltage' or 'current') for channel B'''
        value={'voltage':'OUTPUT_DCVOLTS','current':'OUTPUT_DCAMPS'}[value]
        self.write('smub.source.func=smub.%s' % value)


    @property
    def outputA(self):
        '''Gets the source output ('on'/'off'/'highz') for channel A'''
        return {0: 'off', 1:'on', 2: 'highz'}[int(float(self.ask('print(smua.source.output)')))]
    @property
    def outputB(self):
        '''Gets the source output ('on'/'off'/'highz')  for channel B'''
        return {0: 'off', 1:'on', 2: 'highz'}[int(float(self.ask('print(smub.source.output)')))]
    @outputA.setter
    def outputA(self, value):
        '''Sets the source output ('on'/'off'/'highz') for channel A'''
        status = 'ON' if ((value==True) or (value==1) or (value=='on')) else 'OFF'
        self.write('smua.source.output= smua.OUTPUT_%s' %status)
    @outputB.setter
    def outputB(self, value):
        '''Sets the source output ('on'/'off'/'highz') for channel B'''
        status = 'ON' if ((value==True) or (value==1) or (value=='on')) else 'OFF'
        self.write('smub.source.output= smub.OUTPUT_%s' %status)

    @property
    def voltagelimitA(self,value):
        '''Get the output voltage compliance limit for channel A'''
        return float(self.ask('print(smua.source.limitv'))
    @property
    def voltagelimitB(self,value):
        '''Get the output voltage compliance limit for channel B'''
        return float(self.ask('print(smub.source.limitv'))
    @voltagelimitA.setter
    def voltagelimitA(self,value):
        '''Get the output voltage compliance limit for channel A'''
        return self.write('smua.source.limitv=%s' %value)
    @voltagelimitB.setter
    def voltagelimitB(self,value):
        '''Get the output voltage compliance limit for channel B'''
        return self.write('smub.source.limitv=%s' %value)


    @property
    def currentlimitA(self,value):
        '''Get the output current compliance limit for channel A'''
        return float(self.ask('print(smua.source.limiti'))
    @property
    def currentlimitB(self,value):
        '''Get the output current compliance limit for channel B'''
        return float(self.ask('print(smub.source.limiti'))
    @currentlimitA.setter
    def currentlimitA(self,value):
        '''Get the output current compliance limit for channel A'''
        return self.write('smua.source.limiti=%s' %value)
    @currentlimitB.setter
    def currentlimitB(self,value):
        '''Get the output current compliance limit for channel B'''
        return self.write('smub.source.limiti=%s' %value)

    def resetA(self):
        '''Resets the A channel'''
        self.write('smua.reset()')
    def resetB(self):
        '''Resets the B channel'''
        self.write('smub.reset()')
