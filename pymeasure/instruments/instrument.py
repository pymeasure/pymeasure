#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
    """ The base class for all Instrument definitions.

    It makes use of one of the :py:class:`~pymeasure.adapters.Adapter` classes for communication
    with the connected hardware device. This decouples the instrument/command definition from the
    specific communication interface used.

    When ``adapter`` is a string, this is taken as an appropriate resource name. Depending on your
    installed VISA library, this can be something simple like ``COM1`` or ``ASRL2``, or a more
    complicated
    `VISA resource name <https://pyvisa.readthedocs.io/en/latest/introduction/names.html>`__
    defining the target of your connection.

    When ``adapter`` is an integer, a GPIB resource name is created based on that.
    In either case a :py:class:`~pymeasure.adapters.VISAAdapter` is constructed based on that
    resource name.
    Keyword arguments can be used to further configure the connection.

    Otherwise, the passed :py:class:`~pymeasure.adapters.Adapter` object is used and any keyword
    arguments are discarded.

    This class defines basic SCPI commands by default. This can be disabled with
    :code:`includeSCPI` for instruments not compatible with the standard SCPI commands.

    :param adapter: A string, integer, or :py:class:`~pymeasure.adapters.Adapter` subclass object
    :param string name: The name of the instrument. Often the model designation by default.
    :param includeSCPI: A boolean, which toggles the inclusion of standard SCPI commands
    :param \\**kwargs: In case ``adapter`` is a string or
        integer, additional arguments passed on to
        :py:class:`~pymeasure.adapters.VISAAdapter` (check there for details). Discarded otherwise.
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

        self.isShutdown = False
        log.info("Initializing %s." % self.name)

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
