#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Hall Probe (GMW HG-302A) class
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from automate.instruments.keithley import Keithley2400
import json

class HallProbe(object):
    """ Represents a Hall probe Gaussmeter using a Keithley
    2400 Sourcemeter and GMW HG-302A Hall probe sensor and 
    provides a high-level interface for interacting with the 
    instrument
    """
    
    def __init__(self, adapter, calibrationFile):
        """ Constructs the HallProbe object given a GPIBAdapter, 
        GPIB address, and calibration file        
        """
        self.loadCalibration(calibrationFile)        
        self.meter = Keithley2400(adapter)
        self.meter.reset()
        self.meter.setCurrentSource(10e-3, 8)
        self.meter.setVoltageMeasure()
        self.meter.setCurrentMeasure(False)
        self.meter.setRemoteSensing()
        self.meter.setRearTerminals()
        self.setFieldDisplay()
        
    def connect(self):
        """ Connect to the underlying Keithley 2400 """
        self.meter.connect()
        
    def isConnected(self):
        """ Return True if the underlying Keithley 2400 is connected """
        return self.meter.isConnected()
        
    def disconnect(self):
        """ Disconnect from the underlying Keithley 2400 """
        self.meter.disconnect()    
        
    def loadCalibration(self, filename):
        """Loads a calibration file based on its filename that should
        contain the cubic fit of calibration data as saved by the
        MagnetCalibrationData object using JSON
        """
        with open(filename, 'r') as handle:
            self.calibration = json.load(handle)
        assert type(self.calibration) in [list, tuple]
    
    def setFieldDisplay(self):
        """ Sets the display of the Keithley Sourcemeter to represent
        the field measurements in terms of Gauss units                
        """
        self.meter.write(":CALC:MATH:UNIT 'G'")
        self.meter.write(":CALC:MATH:EXPR:NAME 'FIELD'")
        self.meter.write(":CALC:STAT ON")
        self.meter.write(":CALC:MATH:EXPR (%.6g*VOLT^3 + %.6g*VOLT^2 + %.6g*VOLT + %.6g)" %
                         tuple(self.calibration[0]))
        
    def enable(self):
        """ Turn on the current source in the Keithley 2400 """
        self.meter.enableSource()
        
    def disable(self):
        """ Turn off the current source in the Keithley 2400 """
        self.meter.disableSource()
        
    def isEnabled(self):
        """ Return True if the Keithley 2400 current source is enabled """
        return self.meter.isSourceEnabled()
    
    def startBuffer(self, points=10):
        """ Sets up and initiates a buffer measurement of the given
        size specified by the number of points
        """
        if not self.isEnabled():
            raise Exception("Hall Probe must be enabled prior to measurement")
        else:
            self.meter.setBuffer(points)
            self.meter.startBuffer()
            
    def waitForBuffer(self, abortEvent=None):
        """ Blocks while waiting for the buffer to fill and optionally
        halts if an abort event is given and triggered
        """
        self.meter.waitForBuffer(abortEvent)
        
    def stopBuffer(self):
        """ Stops the buffer """
        self.meter.stopBuffer()
        
    def getField(self):
        """ Reads the mean and stanard deviation fields from the buffer in Gauss """
        mean = self.meter.getVoltageMean()
        return (self.computeField(mean), 
                 self.computeFieldStd(mean, self.meter.getVoltageStd()))
                 
    def getVoltage(self):
        """ Returns the raw voltage and standard deviation from the buffer in volts """
        return self.meter.getVoltageMean(), self.meter.getVoltageStd()
    
    def measureRaw(self, points=1):
        """ Measures in a blocking fashion and returns the mean and standard
        deviation in volts over the number of points specified to measure
        """
        if not self.isEnabled():
            raise Exception("Hall Probe must be enabled prior to measurement")
        else:
            if points == 1:
                return (float(self.meter.measure().split(',')[0]), 0)
            else:
                self.meter.setBuffer(points)
                self.meter.startBuffer()
                self.meter.waitForBuffer()
                voltageMean = self.meter.getVoltageMean()
                voltageStd = self.meter.getVoltageStd()
                return (voltageMean, voltageStd)        
        
    def measure(self, points=1):
        """ Measures in a blocking fashion and returns the mean and standard
        deviation in Gauss over the number of points specified to measure
        """
        if not self.isEnabled():
            raise Exception("Hall Probe must be enabled prior to measurement")
        else:
            if points == 1:
                field = self.computeField(float(self.meter.measure().split(',')[0]))
                return (field, 0)
            else:
                self.meter.setBuffer(points)
                self.meter.startBuffer()
                self.meter.waitForBuffer()
                voltageMean = self.meter.getVoltageMean()
                voltageStd = self.meter.getVoltageStd()
                fieldMean = self.computeField(voltageMean)
                fieldStd = self.computeFieldStd(voltageMean, voltageStd)
                return (fieldMean, fieldStd)
    
    def computeField(self, voltage):
        """ Returns the field in Gauss from the voltage in volts using the
        cubic fit from the calibration data
        """
        cubic = lambda x, *p: p[0]*x**3+p[1]*x**2+p[2]*x+p[3]
        return cubic(voltage, *self.calibration[0])
        
    def computeFieldStd(self, voltage, voltageStd):
        """ Returns the field standard deviation in Gauss from the voltage
        and its standard deviation in volts using the cubic fit from the
        calibration data
        """
        cubic = lambda x, *p: p[0]*x**3+p[1]*x**2+p[2]*x+p[3]
        fit_variance = lambda x, *p: x**6+p[0]**2+x**4+p[1]**2+x**2+p[2]**2+p[3]**2
        return (fit_variance(voltage, *self.calibration[1]) + 
                 cubic(voltageStd, *self.calibration[0]) )**0.5

