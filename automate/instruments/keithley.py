#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Keithley classes -- Sourcemeter, multimeter
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import visa
from instrument import Instrument
import numpy as np
import time

class Keithley2000(Instrument):
    def __init__(self, resourceName, *args, **kwargs):
        super(Keithley2000, self).__init__(resourceName, "Keithley 2000 Multimeter", *args, **kwargs)
        # Simple measurements go here
        self.add_measurement("voltage", ":read?")
        self.add_measurement("resistance", ":read?")

    def check_errors(self):
        errors = map(int, self.instrument.ask_for_values(":system:error?"))
        for err in errors:
            if err != 0:
                self.log("Keithley Encountered error: %d\n" % err)

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
    def __init__(self, resourceName, *args, **kwargs):
        super(Keithley2400, self).__init__(resourceName, "Keithley 2400 Sourcemeter", *args, **kwargs)

        self.write("format:data ascii")
        self.instrument.values_format = visa.ascii
        self.reset()
        self.sourceMode = None

        # Simple control parameters
        self.add_control("source_voltage",  ":sour:volt?",    "sour:volt:lev {:g};")
        self.add_control("source_current",  ":sour:curr?",    "sour:curr:lev {:g};")
        
        # Simple measurements
        self.add_measurement("voltage",    ":read?")
        self.add_measurement("current",    ":read?")
        self.add_measurement("resistance", ":read?")

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
        errors = map(int,self.instrument.ask_for_values(":system:error?"))
        for err in errors:
            if err != 0:
                self.log("Keithley Encountered error: %d\n" % err)

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

    def setBuffer(self, numPoints=64, delay=0):
        self.write(":*CLS;*SRE 1;:STAT:MEAS:ENAB 512;")
        self.write(":TRACE:CLEAR;:TRAC:POIN %d;:TRIG:COUN %d;:TRIG:delay %f;" % (numPoints, numPoints, 1.0e-3*delay))
        self.write(":TRAC:FEED SENSE;:TRAC:FEED:CONT NEXT;")
        self.check_errors()

    def getBuffer(self):
        return self.instrument.ask_for_values(":TRAC:DATA?;")
   
    def startBuffer(self):
        self.write(":INIT")

    def resetBuffer(self):
        self.instrument.ask("status:measurement?")
        self.write("trace:clear; feed:control next")

    def stopBuffer(self):
        self.write(":TRAC:FEED:CONT NEV;:ABOR")
    
    def waitForBuffer(self):
        self.instrument.wait_for_srq()

    def getMeans(self):
        return self.instrument.ask_for_values(":CALC3:FORM MEAN;:CALC3:DATA?;")

    def getStandardDeviations(self):
        return self.instrument.ask_for_values(":CALC3:FORM SDEV;:CALC3:DATA?;")
      
    def getVoltageMean(self):
        return self.getMeans()[0]

    def getVoltageStd(self):
        return self.getStandardDeviations()[0]

    def getCurrentMean(self):
        return self.getMeans()[1]

    def getCurrentStd(self):
        return self.getStandardDeviations()[1]

    def getResistanceMean(self):
        return self.getMeans()[2]

    def getResistanceStd(self):
        return self.getStandardDeviations()[2]

    @property
    def wires(self):
        val = int(self.ask_for_values(':system:rsense?'))
        return (4 if val == 1 else 2)
    @wires.setter
    def wires(self, wires):
        if (wires==2):
            self.write(":SYSTem:RSENse 0")
        elif (wires==4):
            self.write(":SYSTem:RSENse 1")

    # One must seemingly configure the measurement before the source to avoid potential range issues
    def configMeasureResistance(self, NPLC=1, rangeR=1000.0, autoRange=True):
        self.log("<i>%s</i> is measuring resistance." % self.name)
        self.write(":sens:func \"res\";:sens:res:mode man;:sens:res:nplc %f;:form:elem res;" % NPLC)
        if autoRange:
            self.write(":sens:res:rang:auto 1;")
        else:
            self.write(":sens:res:rang:auto 0;:sens:res:rang %g" % rangeR)
        self.check_errors()

    def configMeasureVoltage(self, NPLC=1, rangeV=1000.0, autoRange=True):
        self.log("<i>%s</i> is measuring voltage." % self.name)
        self.write(":sens:func \"volt\";:sens:volt:nplc %f;:form:elem volt;" % NPLC)
        if autoRange:
            self.write(":sens:volt:rang:auto 1;")
        else:
            self.write(":sens:volt:rang:auto 0;:sens:volt:rang %g" % rangeV)
        self.check_errors()

    def configMeasureCurrent(self, NPLC=1, rangeI=1000.0, autoRange=True):
        self.log("<i>%s</i> is measuring current." % self.name)
        self.write(":sens:func \"curr\";:sens:curr:nplc %f;:form:elem curr;" % NPLC)
        if autoRange:
            self.write(":sens:curr:rang:auto 1;")
        else:
            self.write(":sens:curr:rang:auto 0;:sens:curr:rang %g" % rangeI)
        self.check_errors()

    def configSourceCurrent(self, sourceI=0.01e-3, compV=0.1, rangeI=1.0e-3, autoRange=True):
        self.log("<i>%s</i> is sourcing current." % self.name)
        self.sourceMode = "Current"
        if autoRange:
            self.write(":sour:func curr;:sour:curr:rang:auto 1;:sour:curr:lev %g;" % sourceI)
        else:
            self.write(":sour:func curr;:sour:curr:rang:auto 0;:sour:curr:rang %g;:sour:curr:lev %g;" % (rangeI, sourceI))
        self.write(":sens:volt:prot %g;" % compV)
        self.check_errors()

    def configSourceVoltage(self, sourceV=0.01e-3, compI=0.1, rangeI=2.0, rangeV=2.0, autoRange=True):
        self.log("<i>%s</i> is sourcing voltage." % self.name)
        self.sourceMode = "Voltage"
        if autoRange:
            self.write("sour:func volt;:sour:volt:rang:auto 1;:sour:volt:lev %g;" % sourceV)
        else:
            self.write("sour:func volt;:sour:volt:rang:auto 0;:sour:volt:rang %g;:sour:volt:lev %g;" % (rangeV, sourceV))
        self.write(":sens:curr:prot %g;" % compI)
        self.check_errors()

    def status(self):
        return self.instrument.ask("status:queue?;")

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
        return True if self.ask_for_values("output?")==1 else False
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
        self.instrument.timeout = 30.0
        self.outputOn()
        data = self.instrument.ask_for_values(":READ?") 

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

    def shutdown(self):
        self.log("Shutting down <i>%s</i>." % self.name)
        if self.sourceMode == "Current":
            self.rampSourceCurrent(0.0)
        else:
            self.rampSourceVoltage(0.0)
        self.wires = 2
        self.stopBuffer()
        self.outputOff()
        
