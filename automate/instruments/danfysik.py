#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Danfysik classes -- Power supply
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from automate import interfaces, Instrument, RangeException
from zope.interface import implementer
from time import sleep
import numpy as np
import re

from serial import Serial
# Ensure that the Serial object gets treated as an IConnection
Serial = implementer(interfaces.IConnection)(Serial)

class Danfysik8500(Instrument):
    """ Represents the Danfysik 8500 Electromanget Current Supply
    and provides a high-level interface for interacting with the
    instrument    
    """
    
    def __init__(self, port):
        Instrument.__init__(self, Serial(port, 9600, timeout=0.5))
        
    def write(self, command):
        """ Write a command ensuring proper line termination """
        self.connection.write(command + "\r")
        
    def setLocal(self):
        self.write("LOC")
        
    def setRemote(self):
        self.write("REM")
         
    def getPolarity(self):
        if self.ask("PO")[0] == '+':
            return 1
        else:
            return -1
            
    def resetInterlocks(self):
        self.write("RS")
        
    def enable(self):
        self.write("N")
        
    def disable(self):
        self.write("F")
        
    def isEnabled(self):
        """ Returns True if the supply is enabled """
        return self.getStatusHex() & 0x800000 == 0
        
    def getStatusHex(self):
        status = self.ask("S1H")
        match = re.search(r'(?P<hex>[A-Z0-9]{6})', status)
        if match is not None:
            return int(match.groupdict()['hex'], 16)
        else:
            raise Exception("Danfysik status not properly returned. Instead "
                            "got '%s'" % status)
        
    def getCurrent(self):
        return int(self.ask("AD 8"))*1e-2*self.getPolarity()
        
    def setCurrent(self, amps, blocking=False, blockDelay=0.01):
        if amps > 160 or amps < -160:
            raise RangeException("Danfysik 8500 is only capable of sourcing "
                                  "+/- 160 Amps")
        else:
            self.setCurrentPPM(int((1e6/160)*amps))
            if blocking: # ensure the program halts until current is met
                self.waitForReady(blockDelay)
                while abs(self.getCurrent() - amps) > 0.02:
                    sleep(blockDelay)
        
    def setCurrentPPM(self, ppm):
        self.write("DA 0,%d" % int(ppm))
        
    def isReady(self):
        return self.getStatusHex() & 0b10 == 0

    def waitForReady(self, blockDelay=0.01): # timestep in seconds
        while not self.isReady():
            sleep(blockDelay)
            
    def getStatus(self):
        status = []
        indicator = self.ask("S1")
        if indicator[0] == "!":
            status.append("Main Power OFF")
        else:
            status.append("Main Power ON")
        # Skipping 5, 6 and 7 (from Appendix Manual on command S1)
        messages = {1:"Polarity Normal", 2:"Polarity Reversed",
                    3:"Regulation Transformer is not equal to zero",
                    7:"Spare Interlock", 8:"One Transistor Fault",
                    9:"Sum - Interlock", 10:"DC Overcurrent (OCP)",
                    11:"DC Overload",12:"Regulation Module Failure",
                    13:"Preregulator Failure", 14:"Phase Failure",
                    15:"MPS Waterflow Failure", 16:"Earth Leakage Failure",
                    17:"Thermal Breaker/Fuses", 18:"MPS Overtemperature",
                    19:"Panic Button/Door Switch", 
                    20:"Magnet Waterflow Failure",
                    21:"Magnet Overtemperature", 22:"MPS Not Ready"}
        for index, message in messages.items():
            if indicator[index] == "!":
                status.append(message)
        return status
        
    def clearRampSet(self):
        self.write("RAMPSET C")
        
    def setRampDelay(self, time):
        self.write("RAMPSET %f" % time)
        
    def startRamp(self):
        self.write("RAMP R")
        
    def addRampStep(self, current):
        self.write("R %.6f" % (current/160.))
        
    def stopRamp(self):
        self.ask("RAMP S")
    
    def setRampToCurrent(self, current, points, delayTime=1):
        initialCurrent = self.getCurrent()
        self.clearRampSet()
        self.setRampDelay(delayTime)
        steps = np.linspace(initialCurrent, current, num=points)
        cmds = ["R %.6f" % (step/160.) for step in steps]
        self.write("\r".join(cmds))
        
    def rampToCurrent(self, current, points, delayTime=1):
        initialCurrent = self.getCurrent()
        self.clearRampSet()
        self.setRampDelay(delayTime)
        steps = np.linspace(initialCurrent, current, num=points)
        cmds = ["R %.6f" % (step/160.) for step in steps]
        self.write("\r".join(cmds))
        self.startRamp()

    # self.setSequence(0, [0, 10], [0.01])
    def setSequence(self, stack, currents, times, multiplier=0):
        """ Sets up an arbitrary ramp profile with a list of currents (Amps)
        and a list of interval times (seconds) on the specified stack number (0-15)
        """
        self.clearSequence(stack)
        if min(times) >= 1 and max(times) <= 65535:
            self.write("SLOW %i" % stack)
        elif min(times) >= 0.1 and max(times) <= 6553.5:
            self.write("FAST %i" % stack)
            times = [0.1*x for x in times]
        else:
            raise Exception("Timing for Danfysik 8500 ramp sequence is out of range")
        for i in range(len(times)):
            self.write("WSA %i,%i,%i,%i" % (stack, int(6250*currents[i]), int(6250*currents[i+1]), times[i]))
        self.write("MULT %i" % multiplier)
        
    def clearSequence(self, stack):
        """ Clears the sequence stack by number 0-15 """
        self.write("CSS %i" % stack)
        
    def syncSequence(self, stack, delay=0):
        self.write("SYNC %i, %i" % (stack, delay))

    def startSequence(self, stack):
        self.write("TS %i" % stack)
        
    def stopSequence(self):
        self.write("STOP")

    def isSequenceRunning(self, stack):
        return re.search("R%i," % stack, self.ask("S2")) is not None
