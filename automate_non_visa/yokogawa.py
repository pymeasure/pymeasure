# Yokogawa 7651 (Sourcemeter) Class
#
# Authors: Colin Jermain
# Copyright: 2012 Cornell University
#
from gpib import GPIBInstrument, RangeException

class Yokogawa7651(GPIBInstrument):

    def __init__(self, controller, address):
        GPIBInstrument.__init__(self, controller, address)
        
    def identify(self):
        return self.ask("OS")
        
    def reset(self):
        self.write("++clr")
        
    def enableSource(self):
        self.write("O1;E")
        
    def disableSource(self):
        self.write("O0;E")
        
    def setCurrentSource(self):
        self.write("F5;E")
        
    def setVoltageSource(self):
        self.write("F1;E")

    def setCurrentRange(self, amps):
        if amps <= 1e-3:
            self.write("R4;E")
        elif amps <= 1e-2:
            self.write("R5;E")
        elif amps <= 1e-1:
            self.write("R6;E")
        else:
            raise RangeException("Current can not exceed 100mA")
        
    def setVoltageRange(self, volts):
        if volts <= 1e-2:
            self.write("R2;E")
        elif volts <= 1e-1:
            self.write("R3;E")
        elif volts <= 1e0:
            self.write("R4;E")
        elif volts <= 1e2:
            self.write("R5;E")
        elif volts <= 3e2:
            self.write("R6;E")
        else:
            raise RangeException("Voltage can not exceed 30V")
            
    def setVoltageLimit(self, volts):
        if volts >= 1 and volts <= 30:
            self.write("LV%d;E" % volts)
        else:
            raise RangeException("Voltage limit can not be less than 1V or "
                                 "exceed 30V")
                               
    def setCurrentLimit(self, milliamps):
        if milliamps >= 5 and milliamps <= 120:
            self.write("LA%d;E" % milliamps)
        else:
            raise RangeException("Current limit can not be less than 5mA or "
                                 "exceed 120mA")
            
    def setVoltage(self, volts, autoRange=True):
        if volts <= 3e2:
            if autoRange:
                self.write("SA%G;E" % volts)
            else:
                self.write("S%G;E" % volts)
        else:
            raise RangeException("Voltage can not exceed 30V")
    
    def setCurrent(self, amps, autoRange=True):
        if amps <= 1e-1:
            if autoRange:
                self.write("SA%G;E" % amps)
            else:
                self.write("S%G;E" % amps)
        else:
            raise RangeException("Current can not exceed 100mA")
            
    def getVoltage(self):
        status = self.identify().split("\r\n\n")[1]
        if status[0:2] == 'F1':
            return float(status[5:-1])
        else:
            raise Exception("Voltage is not currently set")
            
    def getCurrent(self):
        status = self.identify().split("\r\n\n")[1]
        if status[0:2] == 'F5':
            return float(status[5:-1])
        else:
            raise Exception("Current is not currently set")    
    

