# Stanford Research Systems SR830 (Lock-in) Class
#
# Authors: Colin Jermain
# Copyright: 2012 Cornell University
#
from automate import RangeException, discreteTruncate
from automate.gpib import GPIBInstrument
from time import sleep
from array import array
from StringIO import StringIO
import numpy as np
import re

class SR830(GPIBInstrument):
    sampleFrequencies = [62.5e-3, 125e-3, 250e-3, 500e-3, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    timeConstants = [10e-6, 30e-6, 100e-6, 300e-6, 1e-3, 3e-3, 10e-3, 30e-3, 100e-3, 300e-3, 1,
                     3, 10, 3, 100, 300, 1e3, 3e3, 10e3, 30e3]
    sensitivity = [2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9, 1e-6, 2e-6, 5e-6,
                   10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6, 1e-3, 2e-3, 5e-3, 10e-3, 20e-3,
                   50e-3, 100e-3, 200e-3, 500e-3, 1]
    expansion = [0, 10, 100]
    filterSlopes = [6, 12, 18, 24]
    reserves = ['High Reserve', 'Normal', 'Low Noise']
    channel1 = ['X', 'R', 'X Noise', 'Aux In 1', 'Aux In 2']
    channel2 = ['Y', 'Theta', 'Y Noise', 'Aux In 3', 'Aux In 4']
    
    def __init__(self, adapter, address):
        super(SR830, self).__init__(adapter, address)
    
    def setChannel1(self, variable='X'):
        if not variable in self.channel1:
            index = 0
        else:
            index = self.channel1.index(variable)
        self.write("DDEF1,%d,0" % index)
    
    def setChannel2(self, variable='Y'):
        if not variable in self.channel2:
            index = 0
        else:
            index = self.channel2.index(variable)
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

    def setSampleFrequency(self, frequency=1):
        """Sets the Sample frequency in Hz (None is Trigger)"""
        assert type(frequency) in [float, int, type(None)]
        if frequency is None:
            index = 14
        else:
            frequency = discreteTruncate(frequency, self.sampleFrequencies)
            index = self.sampleFrequencies.index(frequency)
        self.write("SRAT%d" % index)
        
    def getSampleFrequency(self):
        index = int(self.ask("SRAT?"))
        if index is 14:
            return None
        else:
            return self.sampleFrequencies[index]
            
    def setTimeConstant(self, time=30e-3):
        assert type(time) in [float, int]
        time = discreteTruncate(time, self.timeConstants)
        self.write("OFLT%d" % self.timeConstants.index(time))
        
    def getTimeConstant(self):
        identifier = re.search(r'^[0-9]+', self.ask("OFLT?"), re.M).group()
        return float(self.timeConstants[int(identifier)])
        
    def setSensitivity(self, sensitivity=100e-6):
        assert type(sensitivity) in [float, int]
        sensitivity = discreteTruncate(sensitivity, self.sensitivity)
        self.write("SENS%d" % self.sensitivity.index(sensitivity))
        
    def getSensitivity(self):
        return self.sensitivity[int(self.ask("SENS?"))]
        
    def setFilterSlope(self, slope=24):
        assert type(slope) in [float, int]
        slope = discreteTruncate(slope, self.filterSlopes)
        self.write("OFSL%d" % self.filterSlopes.index(slope))
        
    def getFilterSlope(self):
        return self.filterSlopes[int(self.ask("OFSL?"))]        
        
    def setAquireOnTrigger(self, enable=True):
        self.write("TSTR%d" % enable)
        
    def setReserve(self, reserve='Low Noise'):
        if not reserve in self.reserves:
            index = 1
        else:
            index = self.reserves.index(reserve)
        self.write("RMOD%d" % index)
        
    def getReserve(self):
        return self.reserves[int(self.ask("RMOD?"))]
        
    def getX(self):
        return float(self.ask("OUTP?1"))
        
    def getY(self):
        return float(self.ask("OUTP?2"))
        
    def getR(self):
        return float(self.ask("OUTP?3"))
        
    def getTheta(self):
        return float(self.ask("OUTP?3"))
        
    def isOutOfRange(self):
        return int(self.ask("LIAS?2")) is 1
        
    def quickRange(self):
        # Go up in range when needed
        while self.isOutOfRange():
            self.write("SENS%d" % (int(self.ask("SENS?"))+1))
            sleep(5.0*self.getTimeConstant())
            self.write("*CLS")
        # Set the range as low as possible
        self.setSensitivity(1.15*abs(self.getR()))
        
    def getBufferCount(self):
        query = self.ask("SPTS?")
        if query.count("\n") > 1:
            return int(re.match(r"\d+\n$", query, re.MULTILINE).group(0))
        else:
            return int(query)
    
    def fillBuffer(self, count, abortEvent=None, delay=0.001):
        channel1 = np.empty(count, np.float32)
        channel2 = np.empty(count, np.float32)
        currentCount = self.getBufferCount()
        index = 0
        while currentCount < count:
            print index, currentCount, count
            if currentCount > index:
                channel1[index:currentCount] = self.getBuffer(1, index, currentCount)
                channel2[index:currentCount] = self.getBuffer(2, index, currentCount)
                index = currentCount
                sleep(delay)
            currentCount = self.getBufferCount()
            if abortEvent is not None and abortEvent.isSet():
                self.pauseBuffer()
                return channel1, channel2
        self.pauseBuffer()
        channel1[index:count+1] = self.getBuffer(1, index, count)
        channel2[index:count+1] = self.getBuffer(2, index, count)
        return channel1, channel2 
    
    def bufferMeasure(self, count, stopRequest=None, delay=1e-3):
        self.write("FAST0;STRD")
        channel1 = np.empty(count, np.float64)
        channel2 = np.empty(count, np.float64)
        currentCount = self.getBufferCount()
        index = 0
        while currentCount < count:
            if currentCount > index:
                channel1[index:currentCount] = self.getBuffer(1, index, currentCount)
                channel2[index:currentCount] = self.getBuffer(2, index, currentCount)
                index = currentCount
                sleep(delay)
            currentCount = self.getBufferCount()
            if stopRequest is not None and stopRequest.isSet():
                self.pauseBuffer()
                return (0, 0, 0, 0)
        self.pauseBuffer()
        channel1[index:count] = self.getBuffer(1, index, count)
        channel2[index:count] = self.getBuffer(2, index, count)
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
        while not self.getBufferCount() >= count and i < (timeout / timestep):
            sleep(timestep)
            i += 1
            if stopRequest is not None and stopRequest.isSet():
                return False
        self.pauseBuffer()
        
    def getBuffer(self, channel=1, start=0, end=None):
        """ Aquires the 32 bit floating point data through binary transfer
        """
        if end is None: end = self.getBufferCount()
        self.connection.flush()
        self.write("TRCB?%d,%d,%d" % (channel, start, end-start))
        binary = ''.join(self.readlines())
        return np.fromstring(binary, dtype=np.float32)
        
    def resetBuffer(self):
        self.write("REST")
        
    def trigger(self):
        self.write("TRIG")
        
    def setSineVoltage(self, voltage):
        if voltage <= 5.0 and voltage >= 0.004:
            self.write("SLVL%0.3f" % voltage)
        else:
            raise RangeException("The SR830 sine voltage must be between 0.004 and 5 V")
        
    def getSineVoltage(self):
        return float(self.ask("SLVL?"))
