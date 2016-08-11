#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.adapters.visa import VISAAdapter
from pymeasure.adapters import FakeAdapter

import numpy as np


class Instrument(object):
    """ This provides the base class for all Instruments, which is 
    independent of the particular Adapter used to connect for 
    communication to the instrument. It provides basic SCPI commands
    by default, but can be toggled with :code:`includeSCPI`.

    :param adapter: An :class:`Adapter<pymeasure.adapters.Adapter>` object
    :param name: A string name
    :param includeSCPI: A boolean, which toggles the inclusion of standard SCPI commands
    """
    def __init__(self, adapter, name, includeSCPI=True, **kwargs):
        try:
            if isinstance(adapter, (int, str)):
                adapter = VISAAdapter(adapter, **kwargs)
        except ImportError:
            raise Exception("Invalid Adapter provided for Instrument since "
                            "PyVISA is not present")

        self.name = name
        self.SCPI = includeSCPI
        self.adapter = adapter
        class Object(object):
            pass
        self.get = Object()

        # TODO: Determine case basis for the addition of these methods
        if includeSCPI:
            # Basic SCPI commands
            self.status = self.measurement("*STB?", 
                """ Returns the status of the instrument """)
            self.complete = self.measurement("*OPC?",
                """ TODO: Add this doc """)

        self.isShutdown = False
        log.info("Initializing %s." % self.name)
        
    @property
    def id(self):
        """ Requests and returns the identification of the instrument.
        """
        if self.SCPI:
            return self.adapter.ask("*IDN?").strip()
        else:
            return "Warning: Property not implemented."
            
    # Wrapper functions for the Adapter object
    def ask(self, command):
        """ Writes the command to the instrument through the adapter
        and returns the read response.

        :param command: command string to be sent to the instrument
        """
        return self.adapter.ask(command)

    def write(self, command):
        """ Writes the command to the instrument through the adapter.

        :param command: command string to be sent to the instrument
        """
        self.adapter.write(command)

    def read(self): 
        """ Reads from the instrument through the adapter and returns the
        response.
        """
        return self.adapter.read()

    def values(self, command, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.adapter.values(command, **kwargs)

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

    @staticmethod
    def control(get_command, set_command, docs,
                validator=lambda x, y: x, values=[], map_values=False,
                check_set_errors=False, check_get_errors=False,
                **kwargs):
        """Returns a property for the class based on the supplied
        commands. This property may be set and read from the 
        instrument.

        :param get_command: A string command that asks for the value
        :param set_command: A string command that writes the value
        :param docs: A docstring that will be included in the documentation
        :param validator: A function that takes both a value and a group of valid values
                          and returns a valid value, while it otherwise raises an exception
        :param values: A list, range, or dictionary of valid values, that can be used
                       as to map values if :code:`map_values` is True.
        :param map_values: A boolean flag that determines if the values should be 
                          interpreted as a map
        :param check_set_errors: Toggles checking errors after setting
        :param check_get_errors: Toggles checking errors after getting        
        """

        if map_values and type(values) is dict:
            # Prepare the inverse values for performance
            inverse = {v: k for k, v in values.items()}

        def fget(self):
            vals = self.values(get_command, **kwargs)
            if check_get_errors:
                self.check_errors()
            if len(vals) == 1:
                if not map_values:
                    return vals[0]
                elif type(values) in (list, range):
                    return values[int(vals[0])]
                elif type(values) is dict:
                    return inverse[vals[0]]
                else:
                    raise ValueError(
                        'Values of type `{}` are not allowed '
                        'for Instrument.control'.format(type(values))
                    )
            else:
                return vals

        def fset(self, value):
            value = validator(value, values)
            if not map_values:
                pass
            elif type(values) in (list, range):
                value = values.index(value)
            elif type(values) is dict:
                value = values[value]
            else:
                raise ValueError(
                    'Values of type `{}` are not allowed '
                    'for Instrument.control'.format(type(values))
                )
            self.write(set_command % value)
            if check_set_errors:
                self.check_errors()

        # Add the specified document string to the getter
        fget.__doc__ = docs

        return property(fget, fset)
    
    @staticmethod
    def measurement(get_command, docs, values=[], map_values=None, 
                    check_get_errors=False, **kwargs):
        """ Returns a property for the class based on the supplied
        commands. This is a measurement quantity that may only be 
        read from the instrument, not set.

        :param get_command: A string command that asks for the value
        :param docs: A docstring that will be included in the documentation
        :param values: A list, range, or dictionary of valid values, that can be used
                       as to map values if :code:`map_values` is True.
        :param map_values: A boolean flag that determines if the values should be 
                          interpreted as a map
        :param check_get_errors: Toggles checking errors after getting 
        """

        if map_values and type(values) is dict:
            # Prepare the inverse values for performance
            inverse = {v: k for k, v in values.items()}

        def fget(self):
            vals = self.values(get_command, **kwargs)
            if check_get_errors:
                self.check_errors()
            if len(vals) == 1:
                if not map_values:
                    return vals[0]
                elif type(values) in (list, range):
                    return values[int(vals[0])]
                elif type(values) is dict:
                    return inverse[vals[0]]
                else:
                    raise ValueError(
                        'Values of type `{}` are not allowed '
                        'for Instrument.measurement'.format(type(values))
                    )
            else:
                return vals

        # Add the specified document string to the getter
        fget.__doc__ = docs

        return property(fget)

    # TODO: Determine case basis for the addition of this method
    def clear(self):
        """ Clears the instrument status byte
        """
        self.write("*CLS")

    # TODO: Determine case basis for the addition of this method
    def reset(self):
        """ Resets the instrument
        """
        self.write("*RST")

    def shutdown(self):
        """Brings the instrument to a safe and stable state"""
        self.isShutdown = True
        log.info("Shutting down %s" % self.name)

    def check_errors(self):
        """Return any accumulated errors. Must be reimplemented by subclasses.
        """
        pass


class FakeInstrument(Instrument):
    """ Provides a fake implementation of the Instrument class
    for testing purposes.
    """

    def __init__(self, **kwargs):
        super(FakeInstrument, self).__init__(
            FakeAdapter(),
            "Fake Instrument",
            includeSCPI=False,
            **kwargs
        )
