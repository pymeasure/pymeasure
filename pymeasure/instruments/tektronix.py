#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Tektronix classes -- Oscilliscope
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from automate.instruments import Instrument, discreteTruncate, RangeException
import numpy as np
import time, re

class TDS2000(Instrument):         
    
    class Measurement(object):
    
        SOURCE_VALUES = ['CH1', 'CH2', 'MATH']
        TYPE_VALUES = ['FREQ', 'MEAN', 'PERI', 'PHA', 'PK2', 'CRM', 
                       'MINI', 'MAXI', 'RIS', 'FALL', 'PWI', 'NWI']
        UNIT_VALUES = ['V', 's', 'Hz']
    
        def __init__(self, parent, preamble="MEASU:IMM:"):
            self.parent = parent
            self.preamble = preamble

        @property
        def value(self):
            return self.parent.values("%sVAL?" % self.preamble)

        @property
        def source(self):
            return self.parent.ask("%sSOU?" % self.preamble).strip()
        @source.setter
        def source(self, value):
            if value in TDS2000.Measurement.SOURCE_VALUES:
                self.parent.write("%sSOU %s" % (self.preamble, value))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                                 self.parent, value))

        @property
        def type(self):
            return self.parent.ask("%sTYP?" % self.preamble).strip()
        @type.setter
        def type(self, value):
            if value in TDS2000.Measurement.TYPE_VALUES:
                self.parent.write("%sTYP %s" % (self.preamble, value))
            else:
                raise ValueError("Invalid type ('%s') provided to %s" % (
                                 self.parent, value))
            
        @property
        def unit(self):
            return self.parent.ask("%sUNI?" % self.preamble).strip()
        @unit.setter
        def unit(self, value):
            if value in TDS2000.Measurement.UNIT_VALUES:
                self.parent.write("%sUNI %s" % (self.preamble, value))
            else:
                raise ValueError("Invalid unit ('%s') provided to %s" % (
                                 self.parent, value))


    def __init__(self, resourceName, **kwargs):
        super(TDS2000, self).__init__(resourceName, "Tektronix TDS 2000 Oscilliscope", **kwargs)
        self.measurement = TDS2000.Measurement(self)
        

        
