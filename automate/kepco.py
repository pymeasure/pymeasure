# Kepco BOP (Bipolar Operational Power Supply/Amplifier) Class
#
# Authors: Colin Jermain
# Copyright: 2012 Cornell University
#
from gpib import RangeException, linearInverse
from yokogawa7651 import Yokogawa7651
from time import sleep

class KepcoBOP(object):

    # Fitting from calibration: magnet current as a function of 
    # programming voltage
    fitSlope = -1.952
    fitIntercept = 0.222

    def __init__(self, controller, address):
        self.meter = Yokogawa7651(controller, address)
        self.meter.setVoltageSource()
        self.meter.setVoltage(0)
    
    def connect(self):
        self.meter.connect()
        
    def isConnected(self):
        return self.meter.isConnected()
        
    def disconnect(self):
        self.meter.disconnect()
    
    def enableProgramming(self):
        self.meter.enableSource()
        
    def disableProgramming(self):
        self.meter.disableSource()
            
    def setCurrent(self, amps):
        voltage = linearInverse(amps, self.fitSlope, self.fitIntercept)
        self.meter.setVoltage(voltage)
        
    # rate in amps per second
    def rampCurrent(self, endCurrent, rate=1, steps=50):
        initialCurrent = (self.fitSlope*self.meter.getVoltage() + 
                          self.fitIntercept)
        delta = endCurrent - initialCurrent
        totalTime = abs(delta)/float(rate)
        stepTime = totalTime/float(steps)
        stepSize = delta/steps
        currents = [(x+1)*stepSize + initialCurrent for x in range(steps)]
        for current in currents:
            self.setCurrent(current)
            sleep(stepTime)
