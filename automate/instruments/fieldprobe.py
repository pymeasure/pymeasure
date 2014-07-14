#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Field Probe classes -- Magnetic field sensing
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from __future__ import print_function, division 
        
class FieldProbe(object):
    """Field probe base class, essentially performs the inverse role as the magnet class
    in that it converts a signal from the supplied function call to a field in Oe."""
    def __init__(self, readoutMethod, coefficient, offset=0):
        super(FieldProbe, self).__init__()
        self.dataCall    = readoutMethod
        self.coefficient = coefficient
        self.offset      = offset
        self.terminated  = False
    def getField(self):
        return self.coefficient*self.dataCall() + self.offset
    def shutdown(self):
        self.terminated = True
    @property
    def field(self):
        if not self.terminated:
            return self.getField()
    
class ThreeAxisF20(FieldProbe):
    """Senis three axis hall probe"""
    def __init__(self, averages=1000, **kwargs):
        
        if 'logfunc' in kwargs:
            self.logfunc = kwargs['logfunc']
        else:
            self.logfunc = print

        # Take special note: this probe has x reversed...
        self.terminated = False

        from DAQ import DAQ
        self.daq = DAQ("Dev1", logfunc=self.logfunc)  # DAQ Board for Hall Probe Readings and Magnet Control
        self.daq.setupAnalogVoltageIn([0,1,2], averages, sampleRate=20000, scale=1.5) 

        super(ThreeAxisF20, self).__init__(self.daq.acquireAverage, 1.0/0.5e-3)

    @property
    def averages(self):
        return self.daq.numSamples
    @averages.setter
    def averages(self, value):
        self.daq.stop()
        self.daq.setupAnalogVoltageIn([0,1,2], value, sampleRate=20000, scale=1.5) 
    @property
    def field(self):
        return self.getField()
    def getField(self):
        if not self.terminated:
            data = self.dataCall()*self.coefficient
            return [-data[0], data[1], data[2]]
        else:
            return [0,0,0]
    def getFieldDict(self):
        data = self.coefficient*self.dataCall()
        return {'x': -data[0], 'y': data[1], 'z': data[2]}
    def getFieldComponent(self, component):
        return self.getFieldDict()[component]
    @property
    def fieldX(self):
        return self.getFieldDict()['x']
    @property
    def fieldY(self):
        return self.getFieldDict()['y']
    @property
    def fieldZ(self):
        return self.getFieldDict()['z']
    def shutdown(self):
        self.terminated = True
        self.daq.shutdown()

class HallProbe(FieldProbe):
    """Usual hall probe taped to a pole piece somewhere"""
    def __init__(self, *args, **kwargs):
        super(HallProbe, self).__init__(*args, **kwargs)

class Gaussmeter(FieldProbe):
    """Gaussmeter with the most innacurate positioning possible"""
    def __init__(self, *args, **kwargs):
        super(Gaussmeter, self).__init__(*args, **kwargs)
