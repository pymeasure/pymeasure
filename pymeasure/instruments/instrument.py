"""

This file is part of the PyMeasure package.

Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from pymeasure.adapters import VISAAdapter

import numpy as np
import logging


class Instrument(object):
    """ Base class for Instruments, independent of the particular Adapter used
    to connect for communication
    """
    def __init__(self, adapter, name, includeSCPI=True, **kwargs):
        try:
            if isinstance(adapter, (int, long, str)):
                adapter = VISAAdapter(adapter, **kwargs)
        except ImportError:
            raise Exception("Invalid Adapter provided for Instrument since "
                            "PyVISA is not present")

        self.name = name
        self.adapter = adapter

        # TODO: Determine case basis for the addition of these methods
        if includeSCPI:
            # Basic SCPI commands
            self.add_measurement("id",       "*IDN?")
            self.add_measurement("status",   "*STB?")
            self.add_measurement("complete", "*OPC?")

        self.isShutdown = False
        logging.info("Initializing %s" % self.name)

    # Wrapper functions for the Adapter object
    def ask(self, command): return self.adapter.ask(command)

    def write(self, command): self.adapter.write(command)

    def read(self): return self.adapter.read()

    def values(self, command):
        values = self.adapter.values(command)
        if len(values) == 1:
            return values[0]
        else:
            return values

    def binary_values(self, command, header_bytes=0, dtype=np.float32):
        return self.adapter.binary_values(command, header_bytes, dtype)

    def add_property(self, name, initial_value=0.0):
        """This adds simple setter and getter properties called "name"
        for the internal variable that will be called _name
        """
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

    def add_control(self, name, get_string, set_string,
                    check_errors_on_set=False,
                    check_errors_on_get=False,
                    docs=None
                    ):
        """This adds a property to the class based on the supplied
        SCPI commands. The presumption is that this parameter may
        be set and read from the instrument."""

        def fget(self):
            vals = self.values(get_string)
            if check_errors_on_get:
                self.check_errors()
            return vals

        def fset(self, value):
            self.write(set_string % value)
            if check_errors_on_set:
                self.check_errors()

        # Add the specified document string to the getter
        fget.__doc__ = docs

        # Add the property attribute
        setattr(self.__class__, name, property(fget, fset))

    def add_measurement(self, name, get_string, checkErrorsOnGet=False):
        """This adds a property to the class based on the supplied
        SCPI commands. The presumption is that this is a measurement
        quantity that may only be read from the instrument, not set.
        """

        def fget(self):
            return self.values(get_string)

        # Add the specified document string to the getter
        fget.__doc__ = docs

        # Add the property attribute
        setattr(self.__class__, name, property(fget))

    # TODO: Determine case basis for the addition of this method
    def clear(self):
        self.write("*CLS")

    # TODO: Determine case basis for the addition of this method
    def reset(self):
        self.write("*RST")

    def shutdown(self):
        """Bring the instrument to a safe and stable state"""
        logging.info("Shutting down %s" % self.name)

    def check_errors(self):
        """Return any accumulated errors. Must be reimplemented by subclasses.
        """
        pass
