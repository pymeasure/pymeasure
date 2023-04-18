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

from inspect import getmembers
import logging
from warnings import warn

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DynamicProperty(property):
    """ Class that allows managing python property behaviour in a "dynamic" fashion

    The class allows passing, in addition to regular property parameters, a list of
    runtime configurable parameters.
    The effect is that the behaviour of fget/fset not only depends on the obj parameter, but
    also on a set of keyword parameters with a default value.
    These extra parameters are read from instance, if available, or left with the default value.
    Dynamic behaviour is achieved by changing class or instance variables with special names
    defined as `<prefix> + <property name> + <param name>`.

    Code has been based on Python equivalent implementation of properties provided in the
    python documentation `here <https://docs.python.org/3/howto/descriptor.html#properties>`_.

    :param fget: class property fget parameter whose signature is expanded with a
                 set of keyword arguments as in fget_params_list
    :param fset: class property fget parameter whose signature is expanded with a
                 set of keyword arguments as in fset_params_list
    :param fdel: class property fdel parameter
    :param doc: class property doc parameter
    :param fget_params_list: List of parameter names that are dynamically configurable
    :param fset_params_list: List of parameter names that are dynamically configurable
    :param prefix: String to be prefixed to get dynamically configurable
                   parameters.
    """

    def __init__(self, fget=None, fset=None, fdel=None, doc=None, fget_params_list=None,
                 fset_params_list=None, prefix=""):
        super().__init__(fget, fset, fdel, doc)
        self.fget_params_list = () if fget_params_list is None else fget_params_list
        self.fset_params_list = () if fset_params_list is None else fset_params_list
        self.name = ""
        self.prefix = prefix

    def __get__(self, obj, objtype=None):
        if obj is None:
            # Property return itself when invoked from a class
            return self
        if self.fget is None:
            raise AttributeError(f"Unreadable attribute {self.name}")

        kwargs = {}
        for attr in self.fget_params_list:
            attr_instance_name = self.prefix + "_".join([self.name, attr])
            if hasattr(obj, attr_instance_name):
                kwargs[attr] = getattr(obj, attr_instance_name)
        return self.fget(obj, **kwargs)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError(f"Can't set attribute {self.name}")
        kwargs = {}
        for attr in self.fset_params_list:
            attr_instance_name = self.prefix + "_".join([self.name, attr])
            if hasattr(obj, attr_instance_name):
                kwargs[attr] = getattr(obj, attr_instance_name)
        self.fset(obj, value, **kwargs)

    def __set_name__(self, owner, name):
        self.name = name


class CommonBase:
    """Base class for instruments and channels.

    This class contains everything needed for pymeasure's property creator
    :meth:`control` and its derivatives :meth:`measurement` and :meth:`setting`.

    :param preprocess_reply: An optional callable used to preprocess
        strings received from the instrument. The callable returns the
        processed string.

        .. deprecated:: 0.11
            Implement it in the instrument's `read` method instead.
    """

    # Variable holding the list of DynamicProperty parameters that are configurable
    # by users
    _fget_params_list = ('get_command',
                         'values',
                         'map_values',
                         'get_process',
                         'command_process',
                         'check_get_errors')

    _fset_params_list = ('set_command',
                         'validator',
                         'values',
                         'map_values',
                         'set_process',
                         'command_process',
                         'check_set_errors')

    # Prefix used to store reserved variables
    __reserved_prefix = "___"

    def __init__(self, preprocess_reply=None, **kwargs):
        self._special_names = self._setup_special_names()
        self._create_channels()
        if preprocess_reply is not None:
            warn(("Parameter `preprocess_reply` is deprecated. "
                 "Implement it in the instrument, e.g. in `read`, instead."),
                 FutureWarning)
        self.preprocess_reply = preprocess_reply
        super().__init__(**kwargs)

    class ChannelCreator:
        """Add channels to the parent class.

        The children will be added to the parent instance at instantiation with
        :func:`CommonBase.add_child`. The variable name (e.g. :code:`channels`) will be
        used as the `collection` of the children. You may define the attribute
        prefix. If there are no other pressing reasons, use :code:`channels` as variable
        and leave the prefix at the default :code:`"ch_"`.

        .. code::

            class SomeInstrument(Instrument):
                # Three channels of the same type: 'ch_A', 'ch_B', 'ch_C' in 'channels'
                channels = Instrument.ChannelCreator(ChildClass, ["A", "B", "C"])
                # Two functions of different types: 'fn_power', 'fn_voltage' in 'functions'
                functions = Instrument.ChannelCreator((PowerChannel, VoltageChannel),
                                                ["power", "voltage"], prefix="fn_")
                # A channel without a prefixed attribute name, simply: 'motor'
                motor = Instrument.ChannelCreator(MotorControl, prefix=None)

        :param cls: Class for all children or tuple/list of classes, one for each child.
        :param id: Single value or tuple/list of ids of the children.
        :param prefix: Collection prefix for the attributes, e.g. `"ch_"`
            creates attribute `self.ch_A`. If prefix evaluates False,
            the child will be added directly under the variable name.
        :param \\**kwargs: Keyword arguments for all children.
        """

        def __init__(self, cls, id=None, prefix="ch_", **kwargs):
            try:
                valid_class = issubclass(cls, CommonBase)
            except TypeError:
                valid_class = False
            if isinstance(id, (list, tuple)) and isinstance(cls, (list, tuple)):
                assert (len(id) == len(cls)), "Lengths of cls and id do not match."
                self.pairs = list(zip(cls, id))
            elif isinstance(id, (list, tuple)) and valid_class:
                self.pairs = list(zip((cls,) * len(id), id))
            elif (isinstance(id, (str, int)) or id is None) and valid_class:
                self.pairs = ((cls, id),)
            else:
                raise ValueError("Invalid definition of classes '{cls}' and ids '{id}'.")
            kwargs.setdefault("prefix", prefix)
            self.kwargs = kwargs

    def _setup_special_names(self):
        """ Return list of class/instance special names.

        Compute the list of special names based on the list of
        class attributes that are a DynamicProperty. Check also for class variables
        with special name and copy them at instance level
        Internal method, not intended to be accessed at user level."""
        special_names = []
        dynamic_params = tuple(set(self._fget_params_list + self._fset_params_list))
        # Check whether class variables of DynamicProperty type are present
        for attr_name, attr in getmembers(self.__class__):
            if isinstance(attr, DynamicProperty):
                special_names += [attr_name + "_" + key for key in dynamic_params]
        # Check if special variables are defined at class level
        for attr, value in getmembers(self.__class__):
            if attr in special_names:
                # Copy class special variable at instance level, prefixing reserved_prefix
                setattr(self, self.__reserved_prefix + attr, value)
        return special_names

    def _create_channels(self):
        """Create channels according to the ChannelCreator objects."""
        for name, creator in getmembers(self.__class__):
            if isinstance(creator, CommonBase.ChannelCreator):
                for cls, id in creator.pairs:
                    child = self.add_child(cls, id, collection=name, **creator.kwargs)
                    child._protected = True

    def __setattr__(self, name, value):
        """ Add reserved_prefix in front of special variables."""
        if hasattr(self, '_special_names'):
            if name in self._special_names:
                name = self.__reserved_prefix + name
        super().__setattr__(name, value)

    def __getattribute__(self, name):
        """ Prevent read access to variables with special names used to
        support dynamic property behaviour."""
        if name in ('_special_names', '__dict__'):
            return super().__getattribute__(name)
        if hasattr(self, '_special_names'):
            if name in self._special_names:
                raise AttributeError(
                    f"{name} is a reserved variable name and it cannot be read")
        return super().__getattribute__(name)

    # Channel management
    def add_child(self, cls, id=None, collection="channels", prefix="ch_", **kwargs):
        """Add a child to this instance and return its index in the children list.

        The newly created child may be accessed either by the id in the
        children dictionary or by the created attribute.
        The fifth channel of `instrument` with id "F" has two access options:
        :code:`instrument.channels["F"] == instrument.ch_F`

        .. note::

            Do not change the default `collection` or `prefix` parameter, unless
            you have to distinguish several collections of different children,
            e.g. different channel types (analog and digital).

        :param cls: Class of the channel.
        :param id: Child id how it is used in communication, e.g. `"A"`.
        :param collection: Name of the collection of children, used for the dictionary.
        :param prefix: Collection prefix for the attributes, e.g. `"ch_"`
            creates attribute `self.ch_A`. If prefix evaluates False,
            the child will be added directly under the collection name.
        :param \\**kwargs: Keyword arguments for the channel creator.
        :returns: Instance of the created child.
        """
        child = cls(self, id, **kwargs)
        collection_data = getattr(self, collection, {})
        if isinstance(collection_data, CommonBase.ChannelCreator):
            collection_data = {}
        if prefix:
            if not collection_data:
                # Add a grouplist to the parent.
                setattr(self, collection, collection_data)
            collection_data[id] = child
            child._collection = collection
            setattr(self, f"{prefix}{id}", child)
            child._name = f"{prefix}{id}"
        else:
            if collection_data:
                raise ValueError(f"An attribute '{collection}' already exists.")
            setattr(self, collection, child)
            child._name = collection
        return child

    def remove_child(self, child):
        """Remove the child from the instrument and the corresponding collection.

        :param child: Instance of the child to delete.
        """
        if hasattr(child, "_protected"):
            raise TypeError("You cannot remove channels defined at class level.")
        if hasattr(child, "_collection"):
            collection = getattr(self, child._collection)
            del collection[child.id]
        delattr(self, child._name)

    # Communication functions
    def wait_for(self, query_delay=0):
        """Wait for some time. Used by 'ask' to wait before reading.

        Implement in subclass!

        :param query_delay: Delay between writing and reading in seconds.
        """
        raise NotImplementedError("Implement in subclass!")

    def ask(self, command, query_delay=0):
        """Write a command to the instrument and return the read response.

        :param command: Command string to be sent to the instrument.
        :param query_delay: Delay between writing and reading in seconds.
        :returns: String returned by the device without read_termination.
        """
        self.write(command)
        self.wait_for(query_delay)
        return self.read()

    def values(self, command, separator=',', cast=float, preprocess_reply=None, maxsplit=-1,
               **kwargs):
        """Write a command to the instrument and return a list of formatted
        values from the result.

        :param command: SCPI command to be sent to the instrument.
        :param preprocess_reply: Optional callable used to preprocess the string
            received from the instrument, before splitting it.
            The callable returns the processed string.
        :param separator: A separator character to split the string returned by
            the device into a list.
        :param maxsplit: The string returned by the device is splitted at most `maxsplit` times.
            -1 (default) indicates no limit.
        :param cast: A type to cast each element of the splitted string.
        :param \\**kwargs: Keyword arguments to be passed to the :meth:`ask` method.
        :returns: A list of the desired type, or strings where the casting fails.
        """
        results = self.ask(command, **kwargs).strip()
        if callable(preprocess_reply):
            results = preprocess_reply(results)
        elif callable(self.preprocess_reply):
            results = self.preprocess_reply(results)
        results = results.split(separator, maxsplit=maxsplit)
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
        """ Write a command to the instrument and return a numpy array of the binary data.

        :param command: Command to be sent to the instrument.
        :param query_delay: Delay between writing and reading in seconds.
        :param kwargs: Arguments for :meth:`~pymeasure.Adapter.read_binary_values`.
        :returns: NumPy array of values.
        """
        self.write(command)
        self.wait_for(query_delay)
        return self.read_binary_values(**kwargs)

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
        command_process=None,
        check_set_errors=False,
        check_get_errors=False,
        dynamic=False,
        preprocess_reply=None,
        separator=',',
        maxsplit=-1,
        cast=float,
        values_kwargs=None,
        **kwargs
    ):
        """Return a property for the class based on the supplied
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

            .. deprecated:: 0.12
                Use a dynamic property instead.

        :param check_set_errors: Toggles checking errors after setting
        :param check_get_errors: Toggles checking errors after getting
        :param dynamic: Specify whether the property parameters are meant to be changed in
            instances or subclasses.
        :param preprocess_reply: Optional callable used to preprocess the string
            received from the instrument, before splitting it.
            The callable returns the processed string.
        :param separator: A separator character to split the string returned by
            the device into a list.
        :param maxsplit: The string returned by the device is splitted at most `maxsplit` times.
            -1 (default) indicates no limit.
        :param cast: A type to cast each element of the splitted string.
        :param dict values_kwargs: Further keyword arguments for :meth:`values`.
        :param \\**kwargs: Keyword arguments for :meth:`values`.

            .. deprecated:: 0.12
                Use `values_kwargs` dictionary parameter instead.

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
        if values_kwargs is None:
            values_kwargs = {}
        if kwargs:
            warn(f"Do not use keyword arguments {kwargs} as `control` parameter "
                 f"for the `values` method, use `values_kwargs` parameter instead. docs:\n{docs}",
                 FutureWarning)
            values_kwargs.update(kwargs)

        if command_process is None:
            command_process = lambda c: c  # noqa: E731
        else:
            warn("Do not use `command_process`, use a dynamic property instead.", FutureWarning)

        def fget(self,
                 get_command=get_command,
                 values=values,
                 map_values=map_values,
                 get_process=get_process,
                 command_process=command_process,
                 check_get_errors=check_get_errors,
                 ):
            if get_command is None:
                raise LookupError("Property can not be read.")
            vals = self.values(command_process(get_command),
                               separator=separator,
                               cast=cast,
                               preprocess_reply=preprocess_reply,
                               maxsplit=maxsplit,
                               **values_kwargs)
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
                raise LookupError("Property can not be set.")

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
                    'for CommonBase.control'.format(type(values))
                )
            self.write(command_process(set_command) % value)
            if check_set_errors:
                self.check_errors()

        # Add the specified document string to the getter
        fget.__doc__ = docs

        if dynamic:
            fget.__doc__ += "(dynamic)"
            return DynamicProperty(fget=fget, fset=fset,
                                   fget_params_list=CommonBase._fget_params_list,
                                   fset_params_list=CommonBase._fset_params_list,
                                   prefix=CommonBase.__reserved_prefix)
        else:
            return property(fget, fset)

    @staticmethod
    def measurement(get_command, docs, values=(), map_values=None,
                    get_process=lambda v: v,
                    command_process=None,
                    check_get_errors=False, dynamic=False,
                    preprocess_reply=None,
                    separator=',',
                    maxsplit=-1,
                    cast=float,
                    values_kwargs=None,
                    **kwargs):
        """ Return a property for the class based on the supplied
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

            .. deprecated:: 0.12
                Use a dynamic property instead.

        :param check_get_errors: Toggles checking errors after getting
        :param dynamic: Specify whether the property parameters are meant to be changed in
            instances or subclasses. See :meth:`control` for an usage example.
        :param preprocess_reply: Optional callable used to preprocess the string
            received from the instrument, before splitting it.
            The callable returns the processed string.
        :param separator: A separator character to split the string returned by
            the device into a list.
        :param maxsplit: The string returned by the device is splitted at most `maxsplit` times.
            -1 (default) indicates no limit.
        :param cast: A type to cast each element of the splitted string.
        :param dict values_kwargs: Further keyword arguments for :meth:`values`.
        :param \\**kwargs: Keyword arguments for :meth:`values`.

            .. deprecated:: 0.12
                Use `values_kwargs` dictionary parameter instead.
        """
        if values_kwargs is None:
            values_kwargs = {}
        if kwargs:
            warn(f"Do not use keyword arguments {kwargs} as `measurement` parameter "
                 f"for the `values` method, use `values_kwargs` parameter instead. docs:\n{docs}",
                 FutureWarning)
            values_kwargs.update(kwargs)

        return CommonBase.control(get_command=get_command,
                                  set_command=None,
                                  docs=docs,
                                  values=values,
                                  map_values=map_values,
                                  get_process=get_process,
                                  command_process=command_process,
                                  check_get_errors=check_get_errors,
                                  dynamic=dynamic,
                                  preprocess_reply=preprocess_reply,
                                  separator=separator,
                                  maxsplit=maxsplit,
                                  cast=cast,
                                  values_kwargs=values_kwargs,
                                  )

    @staticmethod
    def setting(set_command, docs,
                validator=lambda x, y: x, values=(), map_values=False,
                set_process=lambda v: v,
                check_set_errors=False, dynamic=False,
                ):
        """Return a property for the class based on the supplied
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

        return CommonBase.control(get_command=None,
                                  set_command=set_command,
                                  docs=docs,
                                  validator=validator,
                                  values=values,
                                  map_values=map_values,
                                  set_process=set_process,
                                  check_set_errors=check_set_errors,
                                  dynamic=dynamic,
                                  )
