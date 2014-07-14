# Signal Recovery 7265 (Lock-in) Class
#
# Authors: Colin Jermain
# Copyright: 2013 Cornell University
#
from automate.gpib import GPIBInstrument
from automate import RangeException, discreteTruncate
from time import sleep
from array import array
import numpy as np
import re

class SignalRecovery7265(GPIBInstrument):
    AC_COUPLING, DC_COUPLING = range(2)
    GROUND, FLOAT = range(2)
    sensivitivity = [2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9, 1e-6, 2e-6, 5e-6,
                 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6, 1e-3, 2e-3, 5e-3, 10e-3, 20e-3,
                 50e-3, 100e-3, 200e-3, 500e-3, 1]
    timeConstants = [10e-6, 20e-6, 40e-6, 80e-6, 160e-6, 320e-6, 640e-6, 5e-3, 10e-3, 20e-3,
                 50e-3, 100e-3, 200e-3, 500e-3, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1e3, 2e3,
                 5e3, 10e3, 20e3, 50e3, 100e3]
    filterSlopes = [6, 12, 18, 24]
    
    def __init__(self, adapter, address):
        GPIBInstrument.__init__(self, adapter, address)
    
    def identify(self):
        return self.ask("ID")
        
    def autoOffset(self):
        self.write("AXO")
        
    def getX(self):
        return float(self.ask("X.?"))
        
    def getY(self):
        return float(self.ask("Y.?"))
        
    def getXY(self):
        values = self.ask("XY.?").split(',')
        return float(values[0]), float(values[1])
        
    def setSensitivity(self, sensitivity=100e-6):
        assert type(sensitivity) in [float, int]
        sensitivity = discreteTruncate(sensitivity, self.sensitivity)
        self.write("SEN%d" % self.sensitivity.index(sensitivity))
        
    def getSensitivity(self):
        return self.ask("SEN.?")

    def setTimeConstant(self, time=30e-3):
        assert type(time) in [float, int]
        time = discreteTruncate(time, self.timeConstants)
        self.write("TC%d" % self.timeConstants.index(time))
        
    def getTimeConstant(self):
        return float(self.ask("TC.?"))
        
    def setFilterSlope(self, slope=24):
        assert type(slope) in [float, int]
        slope = discreteTruncate(slope, self.filterSlopes)
        self.write("SLOPE%d" % self.filterSlopes.index(slope))
        
    def getFilterSlope(self):
        return self.filterSlopes[int(self.ask("SLOPE?"))]  
        
    def setOscillatorVoltage(self, voltage):
        self.write("OA.%f" % voltage)
        
    def getOscillatorVoltage(self):
        return float(self.ask("OA.?"))
    
    def setOcillatorFrequency(self, frequency):
        """"Sets the output frequency in Hz"""
        self.write("FRQ.%f" % frequency)
        
    def getOscillatorFrequency(self):
        return float(self.ask("FRQ.?"))
    
    def setInputCoupling(self, coupling):
        if coupling in [self.AC_COUPLING, self.DC_COUPLING]:
            self.write("CP%d" % coupling)
    
    def getInputCoupling(self):
        return int(self.ask("CP?"))
    
    def setInputGrounding(self, grounding):
        if grounding in [self.GOUND, self.FLOAT]:
            self.write("FLOAT%d" % grounding)
            
    def getInputGrounding(self):
        return int(self.ask("FLOAT?"))
        
    def getMagnitude(self):
        return float(self.ask("MAG.?"))
        
    def getPhase(self):
        return float(self.ask("PHA.?"))
        
    def getMagnitudePhase(self):
        values = self.ask("MP.?").split(',')
        return float(values[0]), float(values[1])
        
    def getNoiseOutput(self):
        return float(self.ask("NN.?"))
        
    def setupBuffer(self, points):
        # LEN
        pass
        
    def getBuffer(self, curve, binary=True):
        if binary:
            return self.ask("DCB%d" % curve)
        else:
            return self.ask("DC%d" % curve)
          
    def startBuffer(self):
        # TD, TDC, TDT
        self.write("NC")
            
    def stopBuffer(self):
        self.write("HC")
        
    def getBufferStatus(self):
        # M
        pass
        
    def enableXOffset(self, voltage):
        self.write("XOF1%d" % (-(voltage / float(lockin.ask("SEN.?")))*10000))
        
    def enableXOffsetPrecent(self, precent):
        self.write("XOF1%d", precent)
        
    def disableXOffset(self):
        self.write("XOF0")
        
    def enableYOffset(self, voltage):
        self.write("YOF1%d" % (-(voltage / float(lockin.ask("SEN.?")))*10000))
        
    def enableYOffsetPrecent(self, precent):
        self.write("YOF1%d", precent)
        
    def disableYOffset(self):
        self.write("YOF0")
            
