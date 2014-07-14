#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Generic instrument classes
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from __future__ import print_function
import copy

try:
    import visa
    rm = visa.ResourceManager()
    version = 1.5 if hasattr(rm, 'get_instrument') else 1.4
    print("Found pyvisa version {:.1f}".format(version))
    if version == 1.5:
        def getInstrument(resourceName, **kwargs):
            if isinstance( resourceName, ( int, long ) ):
                resourceName = "GPIB0::%d::INSTR" % resourceName
            safeKeywords = ['resource_name', 'timeout', 'term_chars', 'chunk_size', 'lock', 'delay', 'send_end', 'values_format']
            kwargsCopy = copy.deepcopy(kwargs)
            for key in kwargsCopy:
                if key not in safeKeywords:
                    kwargs.pop(key)
            return rm.get_instrument(resourceName, **kwargs)
    elif version == 1.4:
        def getInstrument(resourceName, **kwargs):
            if isinstance( resourceName, ( int, long ) ):
                resourceName = "GPIB0::%d::INSTR" % resourceName
            return visa.instrument(resourceName, **kwargs)
except:
    print("Pyvisa not found, running in fake mode.")
    def getInstrument(resourceName, **kwargs):
        class FakeInstrument(object):
            """Fake instrument class for debugging purposes"""
            def __init__(self):
                super(FakeInstrument,self).__init__()
            def ask(self, string):
                return "Fake string!"
            def write(self, string):
                pass
            def ask_for_values(self, string):
                return [1.0]
        return FakeInstrument()

import numpy as np
import time 

class Instrument(object):
    """The base class for VISA instruments"""
    def __init__(self, resourceName, name, *args, **kwargs):
        super(Instrument, self).__init__()
        self.name = name
        self.instrument = getInstrument(resourceName, **kwargs)

        # Include the global resource manager so that it doesn't go out of scope prematurely...
        self.manager = rm

        if 'logfunc' in kwargs:
            self.logfunc = kwargs['logfunc']
        else:
            self.logfunc = print

        # Basic SCPI commands
        self.add_measurement("id",       "*IDN?")
        self.add_measurement("status",   "*STB?")
        self.add_measurement("complete", "*OPC?")

        self.shutdownCompleted = False
        self.log("Initializing <i>%s</i>." % self.name)

    # More convenient interface communication
    def ask(self, string):
        return self.instrument.ask(string)
    def write(self, string):
        return self.instrument.write(string)
    def values(self, string):
        vals = self.instrument.ask_for_values(string)
        if len(vals) == 1:
            return vals[0]
        else:
            return vals

    def add_control(self, name, get_string, set_string, checkErrorsOnSet=False, checkErrorsOnGet=False):
        """This adds a property to the class based on the supplied SCPI commands. The presumption is
        that this parameter may be set and read from the instrument."""
        def fget(self):
            vals = self.values(get_string)
            if checkErrorsOnGet:
                self.check_errors()
            return vals
        def fset(self, value):
            self.write(set_string.format(value))
            if checkErrorsOnSet:
                self.check_errors()
        # Add the property attribute
        setattr(self.__class__, name, property(fget, fset))
        # Set convenience functions, that we may pass by reference if necessary
        setattr(self.__class__, 'set_'+name, fset)
        setattr(self.__class__, 'get_'+name, fget)

    def add_measurement(self, name, get_string, checkErrorsOnGet=False):
        """This adds a property to the class based on the supplied SCPI commands. The presumption is
        that this is a measurement quantity that may only be read from the instrument, not set."""
        def fget(self):
            return self.values(get_string)
        # Add the property attribute
        setattr(self.__class__, name, property(fget))
        # Set convenience function, that we may pass by reference if necessary
        setattr(self.__class__, 'get_'+name, fget)

    def clear(self):
        self.write("*CLS")
    
    def reset(self):
        self.write("*RST")
    
    def shutdown(self):
        """Bring the instrument to a safe and stable state"""
        self.log("Shutting down <i>%s</i>." % self.name)
    
    def check_errors(self):
        """Return any accumulated errors. Must be reimplemented by subclasses."""
        pass

    def log(self, string):
        self.logfunc(string)
        
def discreteTruncate(number, discreteSet):
    """ Truncates the number to the closest element in the positive discrete set.
    Returns False if the number is larger than the maximum value or negative.    
    """
    if number < 0:
        return False
    discreteSet.sort()
    for item in discreteSet:
        if number <= item:
            return item
    return False
    
class RangeException(Exception): pass
