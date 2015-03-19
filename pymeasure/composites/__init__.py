#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Generic composite classes
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>class Instrument(object):
from __future__ import print_function
import numpy as np
import time
import logging

class Composite(object):
    """ Base class for combinations of various instruments that act as
    a single unit in practice."""
    def __init__(self, name):
        self.name = name
        self.instruments = []
        self.isShutdown = False
        logging.info("Initializing composite instrument %s" % self.name)
        
    def add_property(self, name, initial_value=0.0):
        """This adds simple setter and getter properties called "name" for the internal variable 
        that will be called _name"""
        # Define the property first
        setattr(self, "_"+name, initial_value)
        def fget(self):
            return getattr(self, "_"+name)
        def fset(self, value):
            setattr(self, "_"+name, value)
        # Add the property attribute
        setattr(self.__class__, name, property(fget, fset))
        # Set convenience functions, that we may pass by reference if necessary
        setattr(self.__class__, 'set_'+name, fset)
        setattr(self.__class__, 'get_'+name, fget)

    # TODO: Determine case basis for the addition of this method
    def clear(self):
        for i in self.instruments:
            i.write("*CLS")

    # TODO: Determine case basis for the addition of this method
    def reset(self):
        for i in self.instruments:
            i.write("*RST")
    
    def shutdown(self):
        logging.info("Shutting down composite instrument %s" % self.name)
        for i in self.instruments:
            i.shutdown()
        time.sleep(0.05)

    def check_errors(self):
        """Return any accumulated errors. Must be reimplemented by subclasses."""
        for i in self.instruments:
            i.check_errors()