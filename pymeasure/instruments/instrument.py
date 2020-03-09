#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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


class Instrument(object):
    """ This provides the base class for all Instruments, which is
    independent of the particular Adapter used to connect for
    communication to the instrument. It provides basic SCPI commands
    by default, but can be toggled with :code:`includeSCPI`.

    :param adapter: An :class:`Adapter<pymeasure.adapters.Adapter>` object
    :param name: A string name
    :param includeSCPI: A boolean, which toggles the inclusion of standard SCPI commands
    """

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
        """ Requests and returns the identification of the instrument. """
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

    @staticmethod
    def control(get_command, set_command, docs,
                validator=lambda v, vs: v, values=(), map_values=False,
                get_process=lambda v: v, set_process=lambda v: v,
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
        :param values: A list, tuple, range, or dictionary of valid values, that can be used
                       as to map values if :code:`map_values` is True.
        :param map_values: A boolean flag that determines if the values should be
                          interpreted as a map
        :param get_process: A function that take a value and allows processing
                            before value mapping, returning the processed value
        :param set_process: A function that takes a value and allows processing
                            before value mapping, returning the processed value
        :param check_set_errors: Toggles checking errors after setting
        :param check_get_errors: Toggles checking errors after getting
        """

        if map_values and isinstance(values, dict):
            # Prepare the inverse values for performance
            inverse = {v: k for k, v in values.items()}

        def fget(self):
            vals = self.values(get_command, **kwargs)
            if check_get_errors:
                self.check_errors()
            if len(vals) == 1:
                value = get_process(vals[0])
                if not map_values:
                    return value
                elif isinstance(values, (list, tuple, range)):
                    return values[int(value)]
                elif isinstance(values, dict):
                    return inverse[value]
                else:
                    raise ValueError(
                        'Values of type `{}` are not allowed '
                        'for Instrument.control'.format(type(values))
                    )
            else:
                vals = get_process(vals)
                return vals

        def fset(self, value):
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

        return property(fget, fset)

    @staticmethod
    def measurement(get_command, docs, values=(), map_values=None,
                    get_process=lambda v: v, command_process=lambda c: c,
                    check_get_errors=False, **kwargs):
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
                            before executing the command, for both getting and setting
        :param check_get_errors: Toggles checking errors after getting
        """

        if map_values and isinstance(values, dict):
            # Prepare the inverse values for performance
            inverse = {v: k for k, v in values.items()}

        def fget(self):
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
                    return inverse[value]
                else:
                    raise ValueError(
                        'Values of type `{}` are not allowed '
                        'for Instrument.measurement'.format(type(values))
                    )
            else:
                return get_process(vals)

        # Add the specified document string to the getter
        fget.__doc__ = docs

        return property(fget)

    @staticmethod
    def setting(set_command, docs,
                validator=lambda x, y: x, values=(), map_values=False,
                set_process=lambda v: v,
                check_set_errors=False,
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
        """

        if map_values and isinstance(values, dict):
            # Prepare the inverse values for performance
            inverse = {v: k for k, v in values.items()}

        def fget(self):
            raise LookupError("Instrument.setting properties can not be read.")

        def fset(self, value):
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

        return property(fget, fset)

    # TODO: Determine case basis for the addition of this method
    def clear(self):
        """ Clears the instrument status byte
        """
        self.write("*CLS")

    # TODO: Determine case basis for the addition of this method
    def reset(self):
        """ Resets the instrument. """
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

    def __init__(self, adapter=None, name=None, includeSCPI=False, **kwargs):
        super().__init__(
            FakeAdapter(),
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
        match = re.search(fmt_spec_pattern, set_command)
        if match:
            format_specifier = match.group(0)
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
