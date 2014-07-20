#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Keithley classes -- Sourcemeter, multimeter
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import visa
from automate.instruments import Instrument
import numpy as np
import time
import logging

class Keithley2000(Instrument):
    def __init__(self, resourceName, **kwargs):
        super(Keithley2000, self).__init__(resourceName, "Keithley 2000 Multimeter", **kwargs)
        # Simple measurements go here
        self.add_measurement("voltage", ":read?")
        self.add_measurement("resistance", ":read?")

    def check_errors(self):
        errors = map(int, self.values(":system:error?"))
        for err in errors:
            if err != 0:
                logging.info("Keithley Encountered error: %d\n" % err)

    def configMeasureResistance(self, wires=2, NPLC=2):
        if (wires==2):
            self.write(":configure:resistance")
            self.write(":resistance:nplcycles %g" % NPLC)
        elif (wires==4):
            self.write(":configure:fresistance")
            self.write(":fresistance:nplcycles %g" % NPLC)
        else:
            raise Exception("Incorrect measurement type specified")

    def configMeasureVoltage(self, Vrange=0.5, NPLC=2):
            self.write(":configure:voltage")
            self.write(":voltage:nplcycles %g" % NPLC)
            self.write(":voltage:range %g" % Vrange)


class Keithley2400(Instrument):
    """This is the class for the Keithley 2000-series instruments"""
    def __init__(self, resourceName, **kwargs):
        super(Keithley2400, self).__init__(resourceName, "Keithley 2400 Sourcemeter", **kwargs)

        self.write("format:data ascii")
        self.values_format = visa.ascii
        self.reset()
        self.sourceMode = None

        # Simple control parameters
        self.add_control("source_voltage",  ":sour:volt?",    "sour:volt:lev %g;")
        self.add_control("source_current",  ":sour:curr?",    "sour:curr:lev %g;")
        
        # Simple measurements
        self.add_measurement("voltage",    ":read?")
        self.add_measurement("current",    ":read?")
        self.add_measurement("resistance", ":read?")

        self.add_measurement("buffer_count", ":TRAC:POIN:ACT?")
        self.add_control("voltage_range", ":SOUR:VOLT:RANG?", ":SOUR:VOLT:RANG %0.2f") # TODO: Validate only -+ 210 V
        self.add_control("current_range", ":SOUR:CURR:RANG?", ":SOUR:CURR:RANG %0.2f") # TODO: Validate only -+ 1.05 A
        self.add_control("resistance_range", ":RES:RANG?", ":RES:RANG %e") # TODO: Validate only 0 to 210 MOhm

    def beep(self, freq, dur):
        self.write(":SYST:BEEP %g, %g" % (freq, dur))

    def triad(self, baseFreq, dur):
        import time
        self.beep(baseFreq, dur)
        time.sleep(dur)
        self.beep(baseFreq*5.0/4.0, dur)
        time.sleep(dur)
        self.beep(baseFreq*6.0/4.0, dur)

    def check_errors(self):
        errors = map(int,self.values(":system:error?"))
        for err in errors:
            if err != 0:
                logging.info("Keithley Encountered error: %d\n" % err)

    def reset(self):
        self.write("status:queue:clear;*RST;:stat:pres;:*CLS;")

    def rampToCurrent(self, targetCurrent, numSteps=30, pause=20e-3):
        currents = np.linspace(self.getSourceCurrent(), targetCurrent, numSteps)
        for current in currents:
            self.source_current = current
            time.sleep(pause)

    def rampToVoltage(self, targetVoltage, numSteps=30, pause=20e-3):
        voltages = np.linspace(self.getSourceVoltage(), targetVoltage, numSteps)
        for voltage in voltages:
            self.source_voltage = voltage
            time.sleep(pause)

    def setTriggerBus(self):
        cmd = ":ARM:COUN 1;:ARM:SOUR BUS;:TRIG:SOUR BUS;"
        self.write(cmd)

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
    
    def setContinous(self):
        """ Sets the Keithley to continously read samples
        and turns off any buffer or output triggering
        """
        self.disableBuffer()
        self.disableOutputTrigger()
        self.setImmediateTrigger()
    
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

    def setBuffer(self, numPoints=64, delay=0):
        # TODO: Check if :STAT:PRES is needed (was in Colin's old code
        self.write(":*CLS;*SRE 1;:STAT:MEAS:ENAB 512;")
        self.write(":TRACE:CLEAR;:TRAC:POIN %d;:TRIG:COUN %d;:TRIG:delay %f;" % (numPoints, numPoints, 1.0e-3*delay))
        self.write(":TRAC:FEED SENSE;:TRAC:FEED:CONT NEXT;")
        self.check_errors()

    def isBufferFull(self):
        """ Returns True if the buffer is full of measurements """
        return int(self.ask("*STB?;")) == 65
    
    def waitForBuffer(self, abortEvent=None, timeOut=60, timeStep=0.01):
        """ Blocks waiting for a full buffer or an abort event with timing
        set in units of seconds
        """
        i = 0
        while not self.isBufferFull() and i < (timeOut / timeStep):
            time.sleep(timeStep)
            i += 1
            if abortEvent is not None and abortEvent.isSet():
                return False
        if not self.isBufferFull():
            raise Exception("Timeout waiting for Keithley 2400 buffer to fill")

    def getBuffer(self):
        return np.loadtxt(StringIO(self.ask(":TRAC:DATA?")), dtype=np.float32,
                    delimiter=',')
   
    def startBuffer(self):
        self.write(":INIT")

    def resetBuffer(self):
        self.ask("status:measurement?")
        self.write("trace:clear; feed:control next")

    def stopBuffer(self):
        """ Aborts the arming and triggering sequence and uses
        a Selected Device Clear (SDC) if possible
        """
        if type(self.connection) is PrologixAdapter:
            self.write("++clr")
        else:
            self.write(":ABOR")        

    def disableBuffer(self):
        """ Disables the connection between measurements and the
        buffer, but does not abort the measurement process
        """
        self.write(":TRAC:FEED:CONT NEV")
    
    def waitForBuffer(self):
        self.connection.wait_for_srq()
    
    def getMeans(self):
        """ Returns the calculated means for voltage, current, and resistance
        from the buffer data  as a list
        """
        return self.values(":CALC3:FORM MEAN;:CALC3:DATA?;")
        
    def getMaximums(self):
        """ Returns the calculated maximums for voltage, current, and 
        resistance from the buffer data as a list 
        """
        return self.values(":CALC3:FORM MAX;:CALC3:DATA?;")
        
    def getMinimums(self):
        """ Returns the calculated minimums for voltage, current, and 
        resistance from the buffer data as a list 
        """
        return self.values(":CALC3:FORM MIN;:CALC3:DATA?;")
        
    def getStandardDeviations(self):
        """ Returns the calculated standard deviations for voltage, current, 
        and resistance from the buffer data as a list
        """    
        return self.values(":CALC3:FORM SDEV;:CALC3:DATA?;")
        
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

    @property
    def wires(self):
        val = int(self.values(':system:rsense?'))
        return (4 if val == 1 else 2)
    @wires.setter
    def wires(self, wires):
        if (wires==2):
            self.write(":SYSTem:RSENse 0")
        elif (wires==4):
            self.write(":SYSTem:RSENse 1")

    # One must seemingly configure the measurement before the source to avoid potential range issues
    def measureResistance(self, NPLC=1, rangeR=1000.0, autoRange=True):
        logging.info("<i>%s</i> is measuring resistance." % self.name)
        self.write(":sens:func \"res\";:sens:res:mode man;:sens:res:nplc %f;:form:elem res;" % NPLC)
        if autoRange:
            self.write(":sens:res:rang:auto 1;")
        else:
            self.write(":sens:res:rang:auto 0;:sens:res:rang %g" % rangeR)
        self.check_errors()

    def measureVoltage(self, NPLC=1, rangeV=1000.0, autoRange=True):
        logging.info("<i>%s</i> is measuring voltage." % self.name)
        self.write(":sens:func \"volt\";:sens:volt:nplc %f;:form:elem volt;" % NPLC)
        if autoRange:
            self.write(":sens:volt:rang:auto 1;")
        else:
            self.write(":sens:volt:rang:auto 0;:sens:volt:rang %g" % rangeV)
        self.check_errors()

    def measureCurrent(self, NPLC=1, rangeI=1000.0, autoRange=True):
        logging.info("<i>%s</i> is measuring current." % self.name)
        self.write(":sens:func \"curr\";:sens:curr:nplc %f;:form:elem curr;" % NPLC)
        if autoRange:
            self.write(":sens:curr:rang:auto 1;")
        else:
            self.write(":sens:curr:rang:auto 0;:sens:curr:rang %g" % rangeI)
        self.check_errors()

    def sourceCurrent(self, sourceI=0.01e-3, compV=0.1, rangeI=1.0e-3, autoRange=True):
        logging.info("<i>%s</i> is sourcing current." % self.name)
        self.sourceMode = "Current"
        if autoRange:
            self.write(":sour:func curr;:sour:curr:rang:auto 1;:sour:curr:lev %g;" % sourceI)
        else:
            self.write(":sour:func curr;:sour:curr:rang:auto 0;:sour:curr:rang %g;:sour:curr:lev %g;" % (rangeI, sourceI))
        self.write(":sens:volt:prot %g;" % compV)
        self.check_errors()

    def sourceVoltage(self, sourceV=0.01e-3, compI=0.1, rangeI=2.0, rangeV=2.0, autoRange=True):
        logging.info("<i>%s</i> is sourcing voltage." % self.name)
        self.sourceMode = "Voltage"
        if autoRange:
            self.write("sour:func volt;:sour:volt:rang:auto 1;:sour:volt:lev %g;" % sourceV)
        else:
            self.write("sour:func volt;:sour:volt:rang:auto 0;:sour:volt:rang %g;:sour:volt:lev %g;" % (rangeV, sourceV))
        self.write(":sens:curr:prot %g;" % compI)
        self.check_errors()

    def status(self):
        return self.ask("status:queue?;")

    def getResistanceBuffered(self):
        self.keith.startBuffer()
        self.keith.waitForBuffer()
        return self.keith.getResistanceMean()
        self.keith.resetBuffer()

    def getVoltageBuffered(self):
        self.keith.startBuffer()
        self.keith.waitForBuffer()
        return self.keith.getVoltageMean()
        self.keith.resetBuffer()

    def getCurrentBuffered(self):
        self.keith.startBuffer()
        self.keith.waitForBuffer()
        return self.keith.getCurrentMean()
        self.keith.resetBuffer()

    @property
    def output(self):
        return self.values("output?")==1
    @output.setter
    def output(self, value):
        if value:
            self.write("output on;")
        else:
            self.write("output off;")

    def RvsI(self, startI, stopI, stepI, compliance, delay=10.0e-3, backward=False):
        num = int(float(stopI-startI)/float(stepI)) + 1
        currRange = 1.2*max(abs(stopI),abs(startI))
        # self.write(":SOUR:CURR 0.0")
        self.write(":SENS:VOLT:PROT %g" % compliance)
        self.write(":SOUR:DEL %g" % delay)
        self.write(":SOUR:CURR:RANG %g" % currRange )
        self.write(":SOUR:SWE:RANG FIX")
        self.write(":SOUR:CURR:MODE SWE")
        self.write(":SOUR:SWE:SPAC LIN")
        self.write(":SOUR:CURR:STAR %g" % startI)
        self.write(":SOUR:CURR:STOP %g" % stopI)
        self.write(":SOUR:CURR:STEP %g" % stepI)
        self.write(":TRIG:COUN %d" % num)
        if backward:
            currents = np.linspace(stopI, startI, num)
            self.write(":SOUR:SWE:DIR DOWN")
        else:
            currents = np.linspace(startI, stopI, num)
            self.write(":SOUR:SWE:DIR UP")
        self.connection.timeout = 30.0
        self.outputOn()
        data = self.values(":READ?") 

        self.check_errors()
        return zip(currents,data)

    def RvsIaboutZero(self, minI, maxI, stepI, compliance, delay=10.0e-3):
        data = []
        data.extend(self.RvsI(minI, maxI, stepI, compliance=compliance, delay=delay))
        data.extend(self.RvsI(minI, maxI, stepI, compliance=compliance, delay=delay, backward=True))
        self.outputOff()    
        data.extend(self.RvsI(-minI, -maxI, -stepI, compliance=compliance, delay=delay))
        data.extend(self.RvsI(-minI, -maxI, -stepI, compliance=compliance, delay=delay, backward=True))
        self.outputOff()
        return data   
        
    def setRearTerminals(self):
        """ Sets the rear terminals to be used instead of the front """
        self.write(":ROUT:TERM REAR")
        
    def setFrontTerminals(self):
        """ Sets the front terminals to be used instead of the rear """
        self.write(":ROUT:TERM FRON")    

    def shutdown(self):
        logging.info("Shutting down <i>%s</i>." % self.name)
        if self.sourceMode == "Current":
            self.rampSourceCurrent(0.0)
        else:
            self.rampSourceVoltage(0.0)
        self.wires = 2
        self.stopBuffer()
        self.outputOff()
        
