# Keithley Classes
#
# Authors: Colin Jermain
# Copyright: 2012 Cornell University
#

from automate import RangeException
from automate.gpib import GPIBInstrument, PrologixAdapter
from time import sleep
from StringIO import StringIO
import numpy as np

class Keithley2400(GPIBInstrument):
    """ Represents the Keithley 2400 Sourcemeter and
    provides a high-level interface for interacting with
    the instrument    
    """
    
    def __init__(self, adapter, address):
        super(Keithley2400, self).__init__(adapter, address)
        
    def enableSource(self):
        """ Turns on the source voltage or current depending
        on which source type has been set up
        """
        self.write(":OUTP:STAT 1")
        
    def disableSource(self):
        """ Turns off the source voltage or current depending
        on which source type has been set up
        """
        self.write(":OUTP:STAT 0")
        
    def isSourceEnabled(self):
        """ Returns True if the source voltage or current is enabled
        depending on which source type has been set up 
        """
        return int(self.ask(":OUTP:STAT?;")) == 1
        
    def measure(self):
        """ Initializes and returns a measurement """
        return self.ask(":READ?")

    def start(self):
        """ Initializes the arming and triggering sequence
        """
        self.write(":INIT")

    def stop(self):
        """ Aborts the arming and triggering sequence and uses
        a Selected Device Clear (SDC) if possible
        """
        if type(self.connection) is PrologixAdapter:
            self.write("++clr")
        else:
            self.write(":ABOR")

    def setContinous(self):
        """ Sets the Keithley to continously read samples
        and turns off any buffer or output triggering
        """
        self.disableBuffer()
        self.disableOutputTrigger()
        self.setImmediateTrigger()
        
    def setBuffer(self, dataPoints):
        """ Sets up the buffer for a specified number of points """
        cmd = ":STAT:PRES;:*CLS;*SRE 1;:STAT:MEAS:ENAB 512;"
        cmd += ":TRACE:CLEAR;:TRAC:POIN %d;" % dataPoints
        cmd += ":TRAC:FEED SENSE;:TRAC:FEED:CONT NEXT;"
        self.write(cmd)

    def disableBuffer(self):
        """ Disables the connection between measurements and the
        buffer, but does not abort the measurement process
        """
        self.write(":TRAC:FEED:CONT NEV")

    def setTriggerCounts(self, arm, trigger):
        """ Sets the number of counts for both the sweeps (arm) and the
        points in those sweeps (trigger), where the total number of
        points can not exceed 2500
        """
        if arm * trigger > 2500 or arm * trigger < 0:
            raise RangeException("Keithley 2400 has a combined maximum of 2500 counts")
        if arm < trigger:
            self.write(":ARM:COUN %d;:TRIG:COUN %d" % (arm, trigger))
        else:
            self.write(":TRIG:COUN %d;:ARM:COUN %d" % (trigger, arm))
    
    def setImmediateTrigger(self):
        """ Sets up the measurement to be taken with the internal
        trigger at the maximum sampling rate
        """
        self.write(":ARM:SOUR IMM;:TRIG:SOUR IMM;")

    def setTimedArm(self, interval):
        """ Sets up the measurement to be taken with the internal
        trigger at a variable sampling rate defined by the interval
        in seconds between sampling points
        """
        if interval > 99999.99 or interval < 0.001:
            raise RangeException("Keithley 2400 can only be time triggered between 1 mS and 1 Ms")
        self.write(":ARM:SOUR TIM;:ARM:TIM %.3f" % interval)
    
    def setExternalTrigger(self, line=1):
        """ Sets up the measurments to be taken on the specified
        line of an external trigger
        """
        cmd = ":ARM:SOUR TLIN;:TRIG:SOUR TLIN;"
        cmd += ":ARM:ILIN %d;:TRIG:ILIN %d;" % (line, line)
        self.write(cmd)
    
    def setOutputTrigger(self, line=1, after='DEL'):
        """ Sets up an output trigger on the specified trigger link
        line number, with the option of supplyiny the part of the
        measurement after which the trigger should be generated
        (default to Delay, which is right before the measurement)
        """
        self.write(":TRIG:OUTP %s;:TRIG:OLIN %d;" % (after, line))

    def disableOutputTrigger(self):
        """ Disables the output trigger for the Trigger layer
        """
        self.write(":TRIG:OUTP NONE")
      
    def isBufferFull(self):
        """ Returns True if the buffer is full of measurements """
        return int(self.ask("*STB?;")) == 65
        
    def waitForBuffer(self, abortEvent=None, timeOut=60, timeStep=0.01):
        """ Blocks waiting for a full buffer or an abort event with timing
        set in units of seconds
        """
        i = 0
        while not self.isBufferFull() and i < (timeOut / timeStep):
            sleep(timeStep)
            i += 1
            if abortEvent is not None and abortEvent.isSet():
                return False
        if not self.isBufferFull():
            raise Exception("Timeout waiting for Keithley 2400 buffer to fill")
    
    def getBuffer(self):
        """ Returns the full contents of the buffer as a string """
        return np.loadtxt(StringIO(self.ask(":TRAC:DATA?")), dtype=np.float32,
                    delimiter=',')
        
    def getBufferCount(self):
        """ Returns the number of data points in the buffer """
        return int(self.ask(":TRAC:POIN:ACT?"))
    
    def getMeans(self):
        """ Returns the calculated means for voltage, current, and resistance
        from the buffer data  as a list
        """
        return [float(x) for x in self.ask(":CALC3:FORM MEAN;:CALC3:DATA?;").split(',')]
        
    def getMaximums(self):
        """ Returns the calculated maximums for voltage, current, and 
        resistance from the buffer data as a list 
        """
        return [float(x) for x in self.ask(":CALC3:FORM MAX;:CALC3:DATA?;").split(',')]
        
    def getMinimums(self):
        """ Returns the calculated minimums for voltage, current, and 
        resistance from the buffer data as a list 
        """
        return [float(x) for x in self.ask(":CALC3:FORM MIN;:CALC3:DATA?;").split(',')]
        
    def getStandardDeviations(self):
        """ Returns the calculated standard deviations for voltage, current, 
        and resistance from the buffer data as a list
        """    
        return [float(x) for x in self.ask(":CALC3:FORM SDEV;:CALC3:DATA?;").split(',')]
        
    def getVoltageMean(self):
        """ Returns the mean voltage from the buffer """
        return self.getMeans()[0]
        
    def getVoltageMax(self):
        """ Returns the maximum voltage from the buffer """
        return self.getMaximums()[0]
        
    def getVoltageMin(self):
        """ Returns the minimum voltage from the buffer """
        return self.getMinimums()[0]

    def getVoltageStd(self):
        """ Returns the voltage standard deviation from the buffer """
        return self.getStandardDeviations()[0]

    def getCurrentMean(self):
        """ Returns the mean current from the buffer """
        return self.getMeans()[1]
        
    def getCurrentMax(self):
        """ Returns the maximum current from the buffer """
        return self.getMaximums()[1]
        
    def getCurrentMin(self):
        """ Returns the minimum current from the buffer """
        return self.getMinimums()[1]

    def getCurrentStd(self):
        """ Returns the current standard deviation from the buffer """
        return self.getStandardDeviations()[1]

    def getResistanceMean(self):
        """ Returns the mean resistance from the buffer """
        return self.getMeans()[2]
        
    def getResistanceMax(self):
        """ Returns the maximum resistance from the buffer """
        return self.getMaximums()[2]
        
    def getResistanceMin(self):
        """ Returns the minimum resistance from the buffer """
        return self.getMinimums()[2]

    def getResistanceStd(self):
        """ Returns the resistance standard deviation from the buffer """
        return self.getStandardDeviations()[2]
              
    def setCurrentMeasure(self, enable=True):
        """ Enables (True) or disables (False) the measurement of current """
        if enable:
            self.write(":SENS:FUNC \"CURR:DC\"")
        else:
            self.write(":SENS:FUNC:OFF \"CURR:DC\"")
    
    def setCurrentSource(self, amps, complianceVolts):
        """ Sets the current as the source based on the value in
        Ampere and a voltage compliance in Volts
        """
        cmd = ":SOUR:FUNC:MODE CURR;:VOLT:PROT %e;" % complianceVolts
        cmd += ":SOUR:CURR:LEV:IMM:AMPL %e;" % amps
        self.write(cmd)
       
    def setCurrentRange(self, amps):
        """ Sets the current range in ampere which must be between
        -1.05 and positive 1.05 A
        """
        if float(amps) < -1.05 or float(amps) > 1.05:
            raise RangeException("Current range can not exceed +-1.05 Amps")
        else:
            self.write(":SOUR:CURR:RANG %0.2f" % amps)

    def getCurrentRange(self):
        """ Returns the current range in ampere """
        return self.ask(":SOUR:CURR:RANG?")

    def setCurrentAutoRange(self, enable=True):
        """ Enables the auto-range function for the current source """
        if enable:
            self.write(":SOUR:CURR:RANG:AUTO 1")
        else:
            self.write(":SOUR:CURR:RANG:AUTO 0")

    def setVoltageMeasure(self, enable=True):
        """ Enables (True) or disables (False) the measurement of voltage """
        if enable:
            self.write(":SENS:FUNC \"VOLT:DC\"")
        else:
            self.write(":SENS:FUNC:OFF \"VOLT:DC\"")

    def setVoltageSource(self, volts, complianceAmps):
        """ Sets the voltage as the source based on the value in Volts
        and the compliance current in Ampere
        """
        cmd = ":SOUR:FUNC:MODE VOLT;:CURR:PROT %e;" % complianceAmps
        cmd += ":SOUR:VOLT:LEV:IMM:AMPL %e;" % volts
        self.write(cmd)
    
    def setVoltageRange(self, volts):
        """ Sets the voltage range in Volts which must be between -210
        and 210 V
        """
        if float(volts) < -210 or float(volts) > 210:
            raise RangeException("Voltage range can not exceed +-210 Volts")
        else:
            self.write(":SOUR:VOLT:RANG %0.2f" % volts)
            
    def getVoltageRange(self):
        """ Returns the voltage range in volts """
        return self.ask(":SOUR:VOLT:RANG?")
        
    def setResistanceMode(self):
        """ Sets the measurement to be in resistance mode """
        self.write("FUNC \"RES\";:RES:MODE AUTO;:SYST:RSEN ON;:FORM:ELEM RES;")
        
    def setResistanceRange(self, ohms):
        """ Sets the range of the resistance measurement in Ohms which
        can not exeed 210 MOhm or be negative
        """
        if float(ohms) < 0 or float(ohms) > 2.1e8:
            raise RangeException("Resistance range can not exceed 210 MOhm or "
                                  "be negative")
        else:
            self.write(":RES:RANG %e" % ohms)
    
    def getResistanceRange(self):
        """ Returns the resistance range in Ohms """
        return self.ask(":RES:RANG?")
        
    def setRemoteSensing(self, enable=True):
        """ Enables (True) or disables (False) the 4 wire
        setting which uses the remote sensing (of the 
        second channel)
        """
        if enable:
            self.write(":SYST:RSEN 1")
        else:
            self.write(":SYST:RSEN 0")
    
    def getRemoteSensing(self):
        """ Returns the state of remote sensing """
        return self.ask(":SYST:RSEN?")
        
    def setRearTerminals(self):
        """ Sets the rear terminals to be used instead of the front """
        self.write(":ROUT:TERM REAR")
        
    def setFrontTerminals(self):
        """ Sets the front terminals to be used instead of the rear """
        self.write(":ROUT:TERM FRON")
        
