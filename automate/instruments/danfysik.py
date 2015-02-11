#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Danfysik classes -- Current supply
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from automate.instruments import Instrument, SerialAdapter, RangeException
from time import sleep
import numpy as np
import re

class DanfysikAdapter(SerialAdapter):
    
    def __init__(self, port):
        super(DanfysikAdapter, self).__init__(port, baudrate=9600, timeout=0.5)
        
    def write(self, command):
        self.connection.write(command + "\r")
        
    def read(self): # Overwrite to raise exceptions on error messages
        result = "".join(self.connection.readlines())
        result = result.replace("\r", "")
        search = re.search("^\?\\x07\s(?P<name>.*)$", result, re.MULTILINE)
        if search:
            raise Exception("Danfysik 8500 raised the error: %s" % (
                            search.groups()[0]))
        else:
            return result
            
        def __repr__(self):
            return "<DanfysikAdapter(port='%s')>" % self.connection.port        

class Danfysik8500(Instrument):
    """ Represents the Danfysik 8500 Electromanget Current Supply
    and provides a high-level interface for interacting with the
    instrument
    
    To allow user access to the Prolific Technology PL2303 Serial port adapter
    in Linux, create the file:
    /etc/udev/rules.d/50-danfysik.rules, with contents:    
    
    SUBSYSTEMS=="usb",ATTRS{idVendor}=="067b",ATTRS{idProduct}=="2303",MODE="0666",SYMLINK+="danfysik"
        
    Then reload the udev rules with:
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    
    The device will be accessible through /dev/danfysik
      
    """
    
    def __init__(self, port):
        super(Danfysik8500, self).__init__(
            DanfysikAdapter(port), "Danfysik 8500 Current Supply", includeSCPI=False
        )
        self.write("ERRT") # Use text error messages
        self.write("UNLOCK") # Unlock from remote or local mode
        
    @property
    def id(self):
        return self.ask("PRINT")
        
    def local(self):
        self.write("LOC")
        
    def remote(self):
        self.write("REM")
         
    @property
    def polarity(self):
        return 1 if self.ask("PO").strip() == '+' else -1
    
    @polarity.setter
    def polarity(self, value):
        polarity = "+" if value > 0 else "-"
        self.write("PO %s" % polarity)
            
    def resetInterlocks(self):
        self.write("RS")
        
    def enable(self):
        self.write("N")
        
    def disable(self):
        self.write("F")
        
    def isEnabled(self):
        """ Returns True if the supply is enabled """
        return self.status_hex & 0x800000 == 0
        
    @property
    def status_hex(self):
        status = self.ask("S1H")
        match = re.search(r'(?P<hex>[A-Z0-9]{6})', status)
        if match is not None:
            return int(match.groupdict()['hex'], 16)
        else:
            raise Exception("Danfysik status not properly returned. Instead "
                            "got '%s'" % status)
    
    @property    
    def current(self):
        return int(self.ask("AD 8"))*1e-2*self.polarity
    @current.setter
    def current(self, amps):
        if amps > 160 or amps < -160:
            raise RangeException("Danfysik 8500 is only capable of sourcing "
                                  "+/- 160 Amps")
        self.current_ppm = int((1e6/160)*amps)
        
    @property
    def current_ppm(self):
        return int(self.ask("DA 0")[2:])
    @current_ppm.setter
    def current_ppm(self, ppm):
        if abs(ppm) < 0 or abs(ppm) > 1e6:
            raise RangeException("Danfysik 8500 requires parts per million "
                                 "to be an appropriate integer")
        self.write("DA 0,%d" % ppm)
    
    @property
    def current_setpoint(self):
        return self.current_ppm*(160/1e6)
    
    @property
    def slew_rate(self):
        return float(self.ask("R3"))
    
    def waitForCurrent(self, hasAborted=lambda:False, delay=0.01):
        self.waitForReady(hasAborted, delay)
        while not hasAborted() and abs(self.current - self.current_setpoint) > 0.02:
            sleep(delay)
        
    def isReady(self):
        return self.status_hex & 0b10 == 0

    def waitForReady(self, hasAborted=lambda:False, delay=0.01):
        while not hasAborted() and not self.isReady():
            sleep(delay)
         
    @property
    def status(self):
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
        initialCurrent = self.current
        self.clearRampSet()
        self.setRampDelay(delayTime)
        steps = np.linspace(initialCurrent, current, num=points)
        cmds = ["R %.6f" % (step/160.) for step in steps]
        self.write("\r".join(cmds))
        
    def rampToCurrent(self, current, points, delayTime=1):
        initialCurrent = self.current
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
        self.write("MULT %i,%i" % (stack, multiplier))
        
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
