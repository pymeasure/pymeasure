#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Yokogawa classes -- Power supply
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import math, sys, time
from instrument import Instrument
import numpy as np

class Yokogawa7651(Instrument):
    def __init__(self, resourceName, **kwargs):
        super(Yokogawa7651, self).__init__(resourceName, "Yokogawa 7651 Programmable DC Source", **kwargs)
        
        self.add_measurement("id", "OS")
        
        # Simple control parameters
        self.add_control("source_voltage", "OD;E", "S{:g};E")
        self.add_control("source_current", "OD;E", "S{:g};E")
        self.add_control("voltage", "OD;E", "S{:g};E")
        self.add_control("current", "OD;E", "S{:g};E")

    @property
    def enabled(self):
        """See if 5th bit is set in the OC flag."""
        oc = int(self.ask("OC;E")[5:])
        return True if (oc & 0b10000) else False
    @enabled.setter
    def enabled(self, value):
        if value:
            self.logfunc("Enabling Yokogawa")
            self.write("O1;E")
        else:
            self.write("O0;E")

    def configSourceCurrent(self, maxCurrent, cycle=False):
        """ For current range specified in A, set the device to the proper mode
        the options are 1mA, 10mA, 100mA. This function automatically rounds up
        to the necessary range."""

        intThing = int(math.log10(maxCurrent*0.95e3)+5.0)
        if (intThing < 4):
            intThing = 4
        elif (intThing > 6):
            intThing = 6

        # Turn off output first, then set the source and turn on again
        if cycle: self.enabled = False
        self.write("F5;R%d;E" % intThing)
        if cycle: self.enabled = True

    def configSourceVoltage(self, maxVoltage, cycle=False):
        """ For voltage range specified in V, set the device to the proper mode
        the options are 10mV, 100mV, 1V, 10V, 30V This function automatically rounds up
        to the necessary range."""

        intThing = int(math.log10(maxVoltage*0.95e3)+2.0)
        if (intThing < 2):
            intThing = 2
        elif (intThing > 6):
            intThing = 6

        # Turn off output first, then set the source and turn on again
        if cycle: self.enabled = False
        self.write("F1;R%d;E" % intThing)
        if cycle: self.enabled = True

    def rampToCurrent(self, current, numSteps=25, totalTime=0.5):
        """ For current in A, time in seconds """
        startI = self.source_current
        stopI  = current
        pause  = totalTime/numSteps
        if (startI != stopI):
            currents = np.linspace(startI, stopI, numSteps)
            for current in currents:
                self.source_current = current
                time.sleep(pause)

    def rampToVoltage(self, value, numSteps=25, totalTime=0.5):
        self.rampToCurrent(value, numSteps=numSteps, totalTime=totalTime)

    def shutdown(self):
        self.log("Shutting down <i>%s</i>." % self.name)
        self.rampToCurrent(0.0, numSteps=25)
        self.source_current = 0.0
        self.enabled = False
    

if __name__ == '__main__':
    yoko = Yokogawa7651(2)
    print yoko.source_voltage
    yoko.enabled = True
    yoko.voltage = 0.01
    print yoko.voltage
    yoko.voltage = 0.00
    yoko.enabled = False
