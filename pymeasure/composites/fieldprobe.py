#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Field Probe classes -- Magnetic field sensing
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from __future__ import print_function, division 
        
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

