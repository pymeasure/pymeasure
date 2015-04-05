"""

This file is part of the PyMeasure package.

Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""


from pymeasure.instruments import Instrument, discreteTruncate

import numpy as np
import time, re


class SR830(Instrument):
    SAMPLE_FREQUENCY_VALUES = [62.5e-3, 125e-3, 250e-3, 500e-3, 1, 2, 4, 8, 16,
                                32, 64, 128, 256, 512]
    TIME_CONSTANT_VALUES = [10e-6, 30e-6, 100e-6, 300e-6, 1e-3, 3e-3, 10e-3, 
                            30e-3, 100e-3, 300e-3, 1, 3, 10, 3, 100, 300, 1e3, 
                            3e3, 10e3, 30e3]
    SENSITIVITY_VALUES = [2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 
                          500e-9, 1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 
                          200e-6, 500e-6, 1e-3, 2e-3, 5e-3, 10e-3, 20e-3,
                          50e-3, 100e-3, 200e-3, 500e-3, 1]
    EXPANSION_VALUES = [0, 10, 100]
    FILTER_SLOPE_VALUES = [6, 12, 18, 24]
    RESERVE_VALUES = ['High Reserve', 'Normal', 'Low Noise']
    CHANNEL1_VALUES = ['X', 'R', 'X Noise', 'Aux In 1', 'Aux In 2']
    CHANNEL2_VALUES = ['Y', 'Theta', 'Y Noise', 'Aux In 3', 'Aux In 4']
    
    def __init__(self, resourceName, **kwargs):
        super(SR830, self).__init__(resourceName, 
           "Stanford Research Systems SR830 Lock-in amplifier", **kwargs)
        
        self.add_control("sine_voltage", "SLVL?", "SLVL%0.3f")
        self.add_control("frequency", "FREQ?", "FREQ%0.3e")
        self.add_control("phase", "PHAS?", "PHAS%0.2f")
        self.add_measurement("x", "OUTP?1")
        self.add_measurement("y", "OUTP?2")
        self.add_measurement("magnitude", "OUTP?3")
        self.add_measurement("theta", "OUTP?4")

    @property
    def channel1(self):
        """ Get the variable for Channel 1 """
        return SR830.CHANNEL1_VALUES[int(self.values("DDEF?1;")[0])]
        
    @channel1.setter
    def channel1(self, value):
        """ Set the variable for Channel 1 """
        if not value in SR830.CHANNEL1_VALUES:
            raise ValueError("Channel 1 selection is invalid for SR830")
        else:
            index = SR830.CHANNEL1_VALUES.index(value)
            self.write("DDEF1,%d,0" % index)

    @property
    def channel2(self):
        """ Get the variable for Channel 2 """
        return SR830.CHANNEL2_VALUES[int(self.values("DDEF?2;")[0])]

    @channel2.setter
    def channel2(self, value):
        """ Set the variable for Channel 2 """
        if not value in SR830.CHANNEL2_VALUES:
            raise ValueError("Channel 2 selection is invalid for SR830")
        else:
            index = SR830.CHANNEL2_VALUES.index(value)
            self.write("DDEF2,%d,0" % index)
        
    def autoGain(self):
        self.write("AGAN")
        
    def autoReserve(self):
        self.write("ARSV")
        
    def autoPhase(self):
        self.write("APHS")

    def autoOffset(self, channel):
        """ Offsets the channel (X=1, Y=2, R=3) to zero """
        self.write("AOFF %i" % channel)

    def autoOffset(self, channel):
        """ Offsets the channel (X=1, Y=2, R=3) to zero """
        self.write("AOFF %i" % channel)
    
    def setOffset(self, channel, precent, expand=0):
        """ Sets the offset of a channel (X=1, Y=2, R=3) to a
        certain precent (-105% to 105%) of the signal with
        an optional expansion term (0, 10=1, 100=2)
        """
        expand = discreteTruncate(expand, self.expansion)
        self.write("OEXP %i,%.2f,%i" % (channel, precent, expand))

    def getOffset(self, channel):
        """ Returns the offset precent and the exapnsion term """
        offset, expand = self.ask("OEXP? %i" % channel).split(',')
        return float(offset), self.expansion[int(expand)] 

    @property
    def sample_frequency(self):
        """ Gets the sample frequency in Hz """
        index = int(self.ask("SRAT?"))
        if index is 14:
            return None # Trigger
        else:
            return SR830.SAMPLE_FREQUENCY_VALUES[index]
        
    @sample_frequency.setter
    def sample_frequency(self, value):
        """Sets the sample frequency in Hz (None is Trigger)"""
        assert type(frequency) in [float, int, type(None)]
        if frequency is None:
            index = 14 # Trigger
        else:
            frequency = discreteTruncate(frequency, SR830.SAMPLE_FREQUENCY_VALUES)
            index = SR830.SAMPLE_FREQUENCY_VALUES.index(frequency)
        self.write("SRAT%f" % index)
        
    @property
    def time_constant(self):
        identifier = re.search(r'^[0-9]+', self.ask("OFLT?"), re.M).group()
        return float(SR830.TIME_CONSTANT_VALUES[int(identifier)])
        
    @time_constant.setter
    def time_constant(self, value):
        assert type(value) in [float, int]
        time = discreteTruncate(value, SR830.TIME_CONSTANT_VALUES)
        self.write("OFLT%d" % SR830.TIME_CONSTANT_VALUES.index(value))
        
    @property
    def sensitivity(self):
        return SR830.SENSITIVITY_VALUES[int(self.ask("SENS?"))]
        
    @sensitivity.setter
    def sensitivity(self, value):
        assert type(value) in [float, int]
        sensitivity = discreteTruncate(value, SR830.SENSITIVITY_VALUES)
        self.write("SENS%d" % SR830.SENSITIVITY_VALUES.index(value))   
        
    @property
    def filter_slope(self):
        return SR830.FILTER_SLOPE_VALUES[int(self.ask("OFSL?"))]   
        
    @filter_slope.setter
    def filter_slope(self, value):
        assert type(value) in [float, int]
        slope = discreteTruncate(value, SR830.FILTER_SLOPE_VALUES)
        self.write("OFSL%d" % SR830.FILTER_SLOPE_VALUES.index(value))       
     
    def aquireOnTrigger(self, enable=True):
        self.write("TSTR%d" % enable)

    @property
    def reserve(self):
        return SR830.RESERVE_VALUES[int(self.ask("RMOD?"))]
        
    @reserve.setter
    def reserve(self, value):
        if not reserve in SR830.RESERVE_VALUES:
            index = 1
        else:
            index = SR830.RESERVE_VALUES.index(reserve)
        self.write("RMOD%d" % index)
    
    def isOutOfRange(self):
        return int(self.ask("LIAS?2")) is 1
        
    def quickRange(self):
        # Go up in range when needed
        while self.isOutOfRange():
            self.write("SENS%d" % (int(self.ask("SENS?"))+1))
            time.sleep(5.0*self.time_constant)
            self.write("*CLS")
        # Set the range as low as possible
        self.sensitivity(1.15*abs(self.R))
        
    @property
    def buffer_count(self):
        query = self.ask("SPTS?")
        if query.count("\n") > 1:
            return int(re.match(r"\d+\n$", query, re.MULTILINE).group(0))
        else:
            return int(query)
    
    def fillBuffer(self, count, abortEvent=None, delay=0.001):
        channel1 = np.empty(count, np.float32)
        channel2 = np.empty(count, np.float32)
        currentCount = self.buffer_count
        index = 0
        while currentCount < count:
            print index, currentCount, count
            if currentCount > index:
                channel1[index:currentCount] = self.buffer_data(1, index, currentCount)
                channel2[index:currentCount] = self.buffer_data(2, index, currentCount)
                index = currentCount
                time.sleep(delay)
            currentCount = self.buffer_count
            if abortEvent is not None and abortEvent.isSet():
                self.pauseBuffer()
                return channel1, channel2
        self.pauseBuffer()
        channel1[index:count+1] = self.buffer_data(1, index, count)
        channel2[index:count+1] = self.buffer_data(2, index, count)
        return channel1, channel2 
    
    def bufferMeasure(self, count, stopRequest=None, delay=1e-3):
        self.write("FAST0;STRD")
        channel1 = np.empty(count, np.float64)
        channel2 = np.empty(count, np.float64)
        currentCount = self.buffer_count
        index = 0
        while currentCount < count:
            if currentCount > index:
                channel1[index:currentCount] = self.buffer_data(1, index, currentCount)
                channel2[index:currentCount] = self.buffer_data(2, index, currentCount)
                index = currentCount
                time.sleep(delay)
            currentCount = self.buffer_count
            if stopRequest is not None and stopRequest.isSet():
                self.pauseBuffer()
                return (0, 0, 0, 0)
        self.pauseBuffer()
        channel1[index:count] = self.buffer_data(1, index, count)
        channel2[index:count] = self.buffer_data(2, index, count)
        return (channel1.mean(), channel1.std(), channel2.mean(), channel2.std())   
    
    def pauseBuffer(self):
        self.write("PAUS")
        
    def startBuffer(self, fast=False):
        if fast:
            self.write("FAST2;STRD")
        else:
            self.write("FAST0;STRD")

    def waitForBuffer(self, count, stopRequest=None, timeout=60, timestep=0.01):
        i = 0
        while not self.buffer_count >= count and i < (timeout / timestep):
            time.sleep(timestep)
            i += 1
            if stopRequest is not None and stopRequest.isSet():
                return False
        self.pauseBuffer()

    def buffer_data(self, channel=1, start=0, end=None):
        """ Aquires the 32 bit floating point data through binary transfer
        """
        if end is None: end = self.buffer_count
        return self.binary_values("TRCB?%d,%d,%d" % (channel, start, end-start))
            
    def resetBuffer(self):
        self.write("REST")
            
    def trigger(self):
        self.write("TRIG")
