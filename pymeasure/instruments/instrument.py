#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
import time

from .common_base import CommonBase, DynamicProperty
from ..adapters import VISAAdapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Instrument(CommonBase):
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
    :param preprocess_reply: An optional callable used to preprocess
        strings received from the instrument. The callable returns the
        processed string.

        .. deprecated:: 0.11
            Implement it in the instrument's `read` method instead.
    :param \\**kwargs: In case ``adapter`` is a string or integer, additional arguments passed on
        to :py:class:`~pymeasure.adapters.VISAAdapter` (check there for details).
        Discarded otherwise.
    """

    # noinspection PyPep8Naming
    def __init__(self, adapter, name, includeSCPI=True,
                 preprocess_reply=None,
                 **kwargs):
        # Setup communication before possible children require the adapter.
        if isinstance(adapter, (int, str)):
            try:
                adapter = VISAAdapter(adapter, **kwargs)
            except ImportError:
                raise Exception("Invalid Adapter provided for Instrument since"
                                " PyVISA is not present")
        self.adapter = adapter
        self.SCPI = includeSCPI
        self.isShutdown = False
        self.name = name

        super().__init__(preprocess_reply=preprocess_reply)

        log.info("Initializing %s." % self.name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    # SCPI default properties
    @property
    def complete(self):
        """Get the synchronization bit.

        This property allows synchronization between a controller and a device. The Operation
        Complete query places an ASCII character 1 into the device's Output Queue when all pending
        selected device operations have been finished.
        """
        if self.SCPI:
            return self.ask("*OPC?").strip()
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    @property
    def status(self):
        """ Get the status byte and Master Summary Status bit. """
        if self.SCPI:
            return self.ask("*STB?").strip()
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    @property
    def options(self):
        """ Get the device options installed. """
        if self.SCPI:
            return self.ask("*OPT?").strip()
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    @property
    def id(self):
        """ Get the identification of the instrument. """
        if self.SCPI:
            return self.ask("*IDN?").strip()
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    # Wrapper functions for the Adapter object
    def write(self, command, **kwargs):
        """Write a string command to the instrument appending `write_termination`.

        :param command: command string to be sent to the instrument
        :param kwargs: Keyword arguments for the adapter.
        """
        self.adapter.write(command, **kwargs)

    def write_bytes(self, content, **kwargs):
        """Write the bytes `content` to the instrument."""
        self.adapter.write_bytes(content, **kwargs)

    def read(self, **kwargs):
        """Read up to (excluding) `read_termination` or the whole read buffer."""
        return self.adapter.read(**kwargs)

    def read_bytes(self, count, **kwargs):
        """Read a certain number of bytes from the instrument.

        :param int count: Number of bytes to read. A value of -1 indicates to
            read the whole read buffer.
        :param kwargs: Keyword arguments for the adapter.
        :returns bytes: Bytes response of the instrument (including termination).
        """
        return self.adapter.read_bytes(count, **kwargs)

    def write_binary_values(self, command, values, *args, **kwargs):
        """Write binary values to the device.

        :param command: Command to send.
        :param values: The values to transmit.
        :param \\*args, \\**kwargs: Further arguments to hand to the Adapter.
        """
        self.adapter.write_binary_values(command, values, *args, **kwargs)

    def read_binary_values(self, **kwargs):
        """Read binary values from the device."""
        return self.adapter.read_binary_values(**kwargs)

    # Communication functions
    def wait_for(self, query_delay=0):
        """Wait for some time. Used by 'ask' to wait before reading.

        :param query_delay: Delay between writing and reading in seconds.
        """
        if query_delay:
            time.sleep(query_delay)

    def ask(self, command, query_delay=0):
        """ Writes the command to the instrument through the adapter
        and returns the read response.

        :param command: Command string to be sent to the instrument.
        :param query_delay: Delay between writing and reading in seconds.
        :returns: String returned by the device without read_termination.
        """
        self.write(command)
        self.wait_for(query_delay)
        return self.read()

    def values(self, command, separator=',', cast=float, preprocess_reply=None):
        """ Writes a command to the instrument and returns a list of formatted
        values from the result.

        :param command: SCPI command to be sent to the instrument
        :param separator: A separator character to split the string into a list
        :param cast: A type to cast the result
        :param preprocess_reply: optional callable used to preprocess values
            received from the instrument. The callable returns the processed
            string.
        :returns: A list of the desired type, or strings where the casting fails
        """
        results = str(self.ask(command)).strip()
        if callable(preprocess_reply):
            results = preprocess_reply(results)
        results = results.split(separator)
        for i, result in enumerate(results):
            try:
                if cast == bool:
                    # Need to cast to float first since results are usually
                    # strings and bool of a non-empty string is always True
                    results[i] = bool(float(result))
                else:
                    results[i] = cast(result)
            except Exception:
                pass  # Keep as string
        return results

    def binary_values(self, command, query_delay=0, **kwargs):
        """ Returns a numpy array from a query for binary data.

        :param command: Command to be sent to the instrument.
        :param query_delay: Delay between writing and reading in seconds.
        :param kwargs: Arguments for :meth:`Adapter.read_binary_values`.
        :returns: NumPy array of values
        """
        self.write(command)
        self.wait_for(query_delay)
        return self.adapter.read_binary_values(**kwargs)

    # Property creators
    @staticmethod
    def control(  # noqa: C901 accept that this is a complex method
        get_command,
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
        **kwargs
    ):
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
        :param command_process: A function that takes a command and allows processing
            before executing the command
        :param check_set_errors: Toggles checking errors after setting
        :param check_get_errors: Toggles checking errors after getting
        :param dynamic: Specify whether the property parameters are meant to be changed in
            instances or subclasses.

        Example of usage of dynamic parameter is as follows:

        .. code-block:: python

            class GenericInstrument(Instrument):
                center_frequency = Instrument.control(
                    ":SENS:FREQ:CENT?;", ":SENS:FREQ:CENT %e GHz;",
                    " A floating point property that represents the frequency ... ",
                    validator=strict_range,
                    # Redefine this in subclasses to reflect actual instrument value:
                    values=(1, 20),
                    dynamic=True  # enable changing property parameters on-the-fly
                )

            class SpecificInstrument(GenericInstrument):
                # Identical to GenericInstrument, except for frequency range
                # Override the "values" parameter of the "center_frequency" property
                center_frequency_values = (1, 10) # Redefined at subclass level

            instrument = SpecificInstrument()
            instrument.center_frequency_values = (1, 6e9) # Redefined at instance level
        .. warning:: Unexpected side effects when using dynamic properties

        Users must pay attention when using dynamic properties, since definition of class and/or
        instance attributes matching specific patterns could have unwanted side effect.
        The attribute name pattern `property_param`, where `property` is the name of the dynamic
        property (e.g. `center_frequency` in the example) and `param` is any of this method
        parameters name except `dynamic` and `docs` (e.g. `values` in the example) has to be
        considered reserved for dynamic property control.
        """

        def fget(self,
                 get_command=get_command,
                 values=values,
                 map_values=map_values,
                 get_process=get_process,
                 command_process=command_process,
                 check_get_errors=check_get_errors,
                 ):
            if get_command is None:
                raise LookupError("Instrument property can not be read.")
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
                    for k, v in values.items():
                        if v == value:
                            return k
                    raise KeyError(f"Value {value} not found in mapped values")
                else:
                    raise ValueError(
                        'Values of type `{}` are not allowed '
                        'for Instrument.control'.format(type(values))
                    )
            else:
                vals = get_process(vals)
                return vals

        def fset(self,
                 value,
                 set_command=set_command,
                 validator=validator,
                 values=values,
                 map_values=map_values,
                 set_process=set_process,
                 command_process=command_process,
                 check_set_errors=check_set_errors,
                 ):

            if set_command is None:
                raise LookupError("Instrument property can not be set.")

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
            self.write(command_process(set_command) % value)
            if check_set_errors:
                self.check_errors()

        # Add the specified document string to the getter
        fget.__doc__ = docs

        if dynamic:
            fget.__doc__ += "(dynamic)"
            return DynamicProperty(fget=fget, fset=fset,
                                   fget_params_list=Instrument._fget_params_list,
                                   fset_params_list=Instrument._fset_params_list,
                                   prefix=Instrument.__reserved_prefix)
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
        :param dynamic: Specify whether the property parameters are meant to be changed in
            instances or subclasses. See :meth:`control` for an usage example.
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
        :param dynamic: Specify whether the property parameters are meant to be changed in
            instances or subclasses. See :meth:`control` for an usage example.
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
        log.info(f"Finished shutting down {self.name}")

    def check_errors(self):
        """ Read all errors from the instrument.

        :return: list of error entries
        """
        if self.SCPI:
            errors = []
            while True:
                err = self.values("SYST:ERR?")
                if int(err[0]) != 0:
                    log.error(f"{self.name}: {err[0]}, {err[1]}")
                    errors.append(err)
                else:
                    break
            return errors
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")
