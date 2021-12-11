#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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
import re

import numpy as np

from pymeasure.adapters import FakeAdapter
from pymeasure.adapters.visa import VISAAdapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

reserved_prefix = "___" # Prefix used to store reserved variables

class DynamicProperty(property):
    """ Class that allows to manage python property behaviour in a "dynamic" fashion

    The class allows to pass, in addition to regular property parameters, a list of
    runtime configurable parameters.
    The effect is that the behaviour of fget/fset not only depends on the obj parameter, but
    also on a set of keyword parameters with a default value.
    These extra parameters are read from instance, if available, or left with the default value.
    Dynamic behaviour is achieved by changing class or instance variables with special names.

    :param fget_list: List of parameter's names that are dynamically configurable
    :param fset_list: List of parameter's names that are dynamically configurable
    :param fget: class property fget parameter with added parameters as in fget_list
    :param fset: class property fget parameter with added parameters as in fget_list
    :param fdel: class property fdel parameter
    :param doc: class property doc parameter
    """
    def __init__(self, fget_list, fset_list, fget=None, fset=None, fdel=None, doc=None):
        super().__init__(fget, fset, fdel, doc)
        self.fget_list = fget_list
        self.fset_list = fset_list
        self.name = ""

    def __get__(self, obj, objtype=None):
        if obj is None:
            # Property return itself when invoked from a class
            return self 
        if self.fget is None:
            raise AttributeError("unreadable attribute")

        kwargs = {}
        for attr in self.fget_list:
            attr1 = reserved_prefix + "_".join([self.name,attr])
            if hasattr(obj, attr1):
                kwargs[attr]=getattr(obj, attr1)
        return self.fget(obj, **kwargs)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        kwargs = {}
        for attr in self.fset_list:
            attr1 = reserved_prefix + "_".join([self.name,attr])
            if hasattr(obj, attr1):
                kwargs[attr]=getattr(obj, attr1)
        self.fset(obj, value, **kwargs)

    def __set_name__(self, owner, name):
        self.name = name

class Instrument(object):
    """ This provides the base class for all Instruments, which is
    independent of the particular Adapter used to connect for
    communication to the instrument. It provides basic SCPI commands
    by default, but can be toggled with :code:`includeSCPI`.

    :param adapter: An :class:`Adapter<pymeasure.adapters.Adapter>` object
    :param name: A string name
    :param includeSCPI: A boolean, which toggles the inclusion of standard SCPI commands
    """

    # Variable holding the list of DynamicProperty parameters that are configurable
    # by users
    special_keys = ('get_command',
                    'set_command',
                    'validator',
                    'values',
                    'map_values',
                    'get_process',
                    'set_process',
                    'command_process',
                    'check_set_errors',
                    'check_get_errors')


    # noinspection PyPep8Naming
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

        self.isShutdown = False
        self._special_names = self._compute_special_names()

        log.info("Initializing %s." % self.name)

    def _compute_special_names(self):
        """ Return list of class/instance special names

        Compute the list of special names based on the list of 
        class variable names defined as DynamicProperty. Check also for class variables
        with special name and copy them at instance level 
        Internal method, not intended to be accessed at user level."""
        special_names = []
        # Check if class variable of DynamicProperty type are present
        for obj in [self] + self.__class__.mro():
            for attr in obj.__dict__:
                if isinstance(obj.__dict__[attr], DynamicProperty):
                    special_names += [attr + "_" + key for key in Instrument.special_keys]
        # Check if special variables are defined at class level
        for obj in [self] + self.__class__.mro():
            for attr in obj.__dict__:
                if attr in special_names:
                    # Copy class special variable at instance level, prefixing reserved_prefix
                    setattr(self,reserved_prefix + attr, obj.__dict__[attr])
        return special_names

    def __setattr__(self, name, value):
        """ Add reserved_prefix in front of special variables """
        if '_special_names' in self.__dict__:
            if name in self._special_names:
                name = reserved_prefix + name
        super().__setattr__(name, value)

    def __getattribute__(self, name):
        """ Allow to refuse access to variables with special names used to
        support dynamic property behaviour """
        if name in ('_special_names', '__dict__'):
            return super().__getattribute__(name)
        if '_special_names' in self.__dict__:
            if name in self._special_names:
                raise AttributeError("{} is a reserved variable name and it cannot be read".format(name))
        return super().__getattribute__(name)

    @property
    def complete(self):
        """ This property allows synchronization between a controller and a device. The Operation Complete 
        query places an ASCII character 1 into the device's Output Queue when all pending
        selected device operations have been finished.
        """
        if self.SCPI:
            return self.ask("*OPC?").strip()
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    @property
    def status(self):
        """ Requests and returns the status byte and Master Summary Status bit. """
        if self.SCPI:
            return self.ask("*STB?").strip()
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    @property
    def options(self):
        """ Requests and returns the device options installed. """
        if self.SCPI:
            return self.ask("*OPT?").strip()
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    @property
    def id(self):
        """ Requests and returns the identification of the instrument. """
        if self.SCPI:
            return self.ask("*IDN?").strip()
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

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

    @staticmethod
    def control(get_command,
                set_command,
                docs,
                validator=lambda v, vs: v,
                values=(),
                map_values=False,
                get_process=lambda v: v,
                set_process=lambda v: v,
                command_process=lambda c: c,
                check_set_errors=False,
                check_get_errors=False,
                dynamic=False,
                **kwargs):
        """Returns a property for the class based on the supplied
        commands. This property may be set and read from the
        instrument. See also :meth:`measurement` and :meth:`setting`.

        :param get_command: A string command that asks for the value, set to `None`
                            if get is not supported (see also :meth:`setting`).
        :param set_command: A string command that writes the value, set to `None`
                            if set is not supported (see also :meth:`measurement`).
        :param docs: A docstring that will be included in the documentation
        :param validator: A function that takes both a value and a group of valid values
                          and returns a valid value, while it otherwise raises an exception
        :param values: A list, tuple, range, or dictionary of valid values, that can be used
                       as to map values if :code:`map_values` is True.
        :param map_values: A boolean flag that determines if the values should be
                          interpreted as a map
        :param get_process: A function that take a value and allows processing
                            before value mapping, returning the processed value
        :param set_process: A function that takes a value and allows processing
                            before value mapping, returning the processed value
        :param command_process: A function that take a command and allows processing
                            before executing the command, for getting
        :param check_set_errors: Toggles checking errors after setting
        :param check_get_errors: Toggles checking errors after getting
        :param dynamic: Specify whether the property parameters are meant to be changed in instances or subclasses.

        Example of usage of dynamic parameter is as follow:

        .. code-block:: python
        
            class GenericInstrument(Instrument):
                center_frequency = Instrument.control(
                    ":SENS:FREQ:CENT?;", ":SENS:FREQ:CENT %e Hz;",
                    " A floating point property that represents the frequency ... ",
                    validator=strict_range,
                    values=(1, 26.5e9), # Redefine this in subclasses to reflect actual instrument value
                    dynamic=True # declare property dynamic
                )

            class SpecificInstrument(Instrument): # Identical to GenericInstrument, except for frequency range
                center_frequency_values = (1, 13e9) # Redefined at subclass level

            instrument = SpecificInstrument()
            instrument.center_frequency_values = (1, 6e9) # Redefined at instance level

        .. warning:: Unexepected side effects when using dynamic properties

        Users must pay attention when using dynamic properties, since definition of class and/or instance 
        attributes matching specific patterns could have unwanted side effect.
        The attribute name pattern `property_param`, where `property` is the name of the dynamic property (e.g. `center_frequency` in the example)
        and `param` is any of this method parameters name except `dynamic` (e.g. `values` in the example) has to be considered reserved for
        dynamic property control.
        """

        if get_command is None:
            def fget(self):
                raise LookupError("Instrument property can not be read.")
        else:
            def fget(self,
                     get_command=get_command, 
                     values=values,
                     map_values=map_values,
                     get_process = get_process,
                     command_process=command_process,
                     check_get_errors=check_get_errors,
            ):
                vals = self.values(command_process(get_command), **kwargs)
                if check_get_errors:
                    self.check_errors()
                if len(vals) == 1:
                    value = get_process(vals[0])
                    if not map_values:
                        return value
                    elif isinstance(values, (list, tuple, range)):
                        return values[int(value)]
                    elif isinstance(values, dict):
                        for k,v in values.items():
                            if v == value:
                                return k
                        raise KeyError("Value {} not found in mapped values".format(value))
                    else:
                        raise ValueError(
                            'Values of type `{}` are not allowed '
                            'for Instrument.control'.format(type(values))
                        )
                else:
                    vals = get_process(vals)
                    return vals

        if set_command is None:
            def fset(self, value):
                raise LookupError("Instrument property can not be set.")
        else:
            def fset(self,
                     value,
                     set_command=set_command, 
                     validator=validator,
                     values=values, 
                     map_values=map_values,
                     set_process=set_process,
                     check_set_errors=check_set_errors,
            ):

                value = set_process(validator(value, values))
                if not map_values:
                    pass
                elif isinstance(values, (list, tuple, range)):
                    value = values.index(value)
                elif isinstance(values, dict):
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

        if dynamic:
            # Compute list of parameters supporting dynamic value
            fget_list = []
            for var in fget.__code__.co_varnames:
                if var in Instrument.special_keys:
                    fget_list.append(var)

            # Compute list of parameters supporting dynamic value
            fset_list = []
            for var in fset.__code__.co_varnames:
                if var in Instrument.special_keys:
                    fset_list.append(var)

            return DynamicProperty(fget_list, fset_list, fget, fset)
        else:
            return property(fget, fset)

    @staticmethod
    def measurement(get_command, docs, values=(), map_values=None,
                    get_process=lambda v: v, command_process=lambda c: c,
                    check_get_errors=False, dynamic=False, **kwargs):
        """ Returns a property for the class based on the supplied
        commands. This is a measurement quantity that may only be
        read from the instrument, not set.

        :param get_command: A string command that asks for the value
        :param docs: A docstring that will be included in the documentation
        :param values: A list, tuple, range, or dictionary of valid values, that can be used
                       as to map values if :code:`map_values` is True.
        :param map_values: A boolean flag that determines if the values should be
                          interpreted as a map
        :param get_process: A function that take a value and allows processing
                            before value mapping, returning the processed value
        :param command_process: A function that take a command and allows processing
                            before executing the command, for getting
        :param check_get_errors: Toggles checking errors after getting
        :param dynamic: Specify whether the property parameters are meant to be changed in instances or subclasses. See :meth:`control` for an usage example.

        """

        return Instrument.control(get_command=get_command,
                                  set_command=None,
                                  docs=docs,
                                  values=values,
                                  map_values=map_values,
                                  get_process=get_process,
                                  command_process=command_process,
                                  check_get_errors=check_get_errors,
                                  dynamic=dynamic,
                                  **kwargs)

    @staticmethod
    def setting(set_command, docs,
                validator=lambda x, y: x, values=(), map_values=False,
                set_process=lambda v: v,
                check_set_errors=False, dynamic=False,
                **kwargs):
        """Returns a property for the class based on the supplied
        commands. This property may be set, but raises an exception
        when being read from the instrument.

        :param set_command: A string command that writes the value
        :param docs: A docstring that will be included in the documentation
        :param validator: A function that takes both a value and a group of valid values
                          and returns a valid value, while it otherwise raises an exception
        :param values: A list, tuple, range, or dictionary of valid values, that can be used
                       as to map values if :code:`map_values` is True.
        :param map_values: A boolean flag that determines if the values should be
                          interpreted as a map
        :param set_process: A function that takes a value and allows processing
                            before value mapping, returning the processed value
        :param check_set_errors: Toggles checking errors after setting
        :param dynamic: Specify whether the property parameters are meant to be changed in instances or subclasses. See :meth:`control` for an usage example.
        """

        return Instrument.control(get_command=None,
                                  set_command=set_command,
                                  docs=docs,
                                  validator=validator,
                                  values=values,
                                  map_values=map_values,
                                  set_process=set_process,
                                  check_set_errors=check_set_errors,
                                  dynamic=dynamic,
                                  **kwargs)


    def clear(self):
        """ Clears the instrument status byte
        """
        if self.SCPI:
            self.write("*CLS")
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    def reset(self):
        """ Resets the instrument. """
        if self.SCPI:
            self.write("*RST")
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    def shutdown(self):
        """Brings the instrument to a safe and stable state"""
        self.isShutdown = True
        log.info("Shutting down %s" % self.name)

    def check_errors(self):
        """ Read all errors from the instrument.

        :return: list of error entries
        """
        if self.SCPI:
            errors = []
            while True:
                err = self.values("SYST:ERR?")
                if int(err[0]) != 0:
                    log.error("{}: {}, {}".format(self.name, err[0], err[1]))
                    errors.append(err)
                else:
                    break

            return errors
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

class FakeInstrument(Instrument):
    """ Provides a fake implementation of the Instrument class
    for testing purposes.
    """

    def __init__(self, adapter=None, name=None, includeSCPI=False, **kwargs):
        super().__init__(
            FakeAdapter(**kwargs),
            name or "Fake Instrument",
            includeSCPI=includeSCPI,
            **kwargs
        )

    @staticmethod
    def control(get_command, set_command, docs,
                validator=lambda v, vs: v, values=(), map_values=False,
                get_process=lambda v: v, set_process=lambda v: v,
                check_set_errors=False, check_get_errors=False,
                **kwargs):
        """Fake Instrument.control.

        Strip commands and only store and return values indicated by
        format strings to mimic many simple commands.
        This is analogous how the tests in test_instrument are handled.
        """

        # Regex search to find first format specifier in the command
        fmt_spec_pattern = r'(%[\w.#-+ *]*[diouxXeEfFgGcrsa%])'
        match = re.findall(fmt_spec_pattern, set_command)
        if match:
            # format_specifier = match.group(0)
            format_specifier = ','.join(match)
        else:
            format_specifier = ''
        # To preserve as much functionality as possible, call the real
        # control method with modified get_command and set_command.
        return Instrument.control(get_command="",
                                  set_command=format_specifier,
                                  docs=docs,
                                  validator=validator,
                                  values=values,
                                  map_values=map_values,
                                  get_process=get_process,
                                  set_process=set_process,
                                  check_set_errors=check_set_errors,
                                  check_get_errors=check_get_errors,
                                  **kwargs)
