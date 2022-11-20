.. _adding-instruments:

##################
Adding instruments
##################

You can make a significant contribution to PyMeasure by adding a new instrument to the :code:`pymeasure.instruments` package. Even adding an instrument with a few features can help get the ball rolling, since its likely that others are interested in the same instrument.

Before getting started, become familiar with the :doc:`contributing work-flow <contribute>` for PyMeasure, which steps through the process of adding a new feature (like an instrument) to the development version of the source code. This section will describe how to lay out your instrument code.

File structure
==============

Your new instrument should be placed in the directory corresponding to the manufacturer of the instrument. For example, if you are going to add an "Extreme 5000" instrument you should add the following files assuming "Extreme" is the manufacturer. Use lowercase for all filenames to distinguish packages from CamelCase Python classes.

.. code-block:: none

    pymeasure/pymeasure/instruments/extreme/
        |--> __init__.py
        |--> extreme5000.py

Updating the init file
**********************

The :code:`__init__.py` file in the manufacturer directory should import all of the instruments that correspond to the manufacturer, to allow the files to be easily imported. For a new manufacturer, the manufacturer should also be added to :code:`pymeasure/pymeasure/instruments/__init__.py`.

Add test files
**************

Test files (pytest) for each instrument are highly encouraged, as they help verify the code and implement changes. Testing new code parts with a test (Test Driven Development) is a good way for fast and good programming, as you catch errors early on.

.. code-block:: none

    pymeasure/tests/instruments/extreme/
        |--> test_extreme5000.py


Adding documentation
********************

Documentation for each instrument is required, and helps others understand the features you have implemented. Add a new reStructuredText file to the documentation.

.. code-block:: none

    pymeasure/docs/api/instruments/extreme/
        |--> index.rst
        |--> extreme5000.rst

Copy an existing instrument documentation file, which will automatically generate the documentation for the instrument. The :code:`index.rst` file should link to the :code:`extreme5000` file. For a new manufacturer, the manufacturer should be also linked in :code:`pymeasure/docs/api/instruments/index.rst`.

Instrument file
===============

All standard instruments should be child class of :class:`Instrument <pymeasure.instruments.Instrument>`. This provides the basic functionality for working with :class:`Adapters <pymeasure.adapters.Adapter>`, which perform the actual communication. 

The most basic instrument, for our "Extreme 5000" example starts like this:

.. testcode::

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

    # from pymeasure.instruments import Instrument
    
.. testcode::
    :hide:

    # Behind the scene, replace Instrument with FakeInstrument to enable
    # doctesting all this
    from pymeasure.instruments.fakes import FakeInstrument as Instrument

This is a minimal instrument definition:

.. testcode::
    
    class Extreme5000(Instrument):
        """Control the imaginary Extreme 5000 instrument."""

        def __init__(self, adapter, **kwargs):
            super().__init__(
                adapter,
                "Extreme 5000",
                **kwargs
            )

Make sure to include the PyMeasure license to each file, and add yourself as an author to the :code:`AUTHORS.txt` file.

There is a certain order of elements in an instrument class that is useful to adhere to:

* First, the initializer (the :code:`__init__()` method), this makes it faster to find when browsing the source code.
* Then class attributes/variables, if you need them.
* Then properties (pymeasure-specific or generic Python variants). This will be the bulk of the implementation.
* Finally, any methods.

Your instrument's user interface
================================

Your instrument will have a certain set of properties and methods that are available to a user and discoverable via the documentation or their editor's autocomplete function.

In principle you are free to choose how you do this (with the exception of standard SCPI properties like :code:`id`).
However, there are a couple of practices that have turned out to be useful to follow:

* Naming things is important. Try to choose clear, expressive, unambiguous names for your instrument's elements.
* If there are already similar instruments in the same "family" (like a power supply) in pymeasure, try to follow their lead where applicable. It's better if, e.g., all power supplies have a :code:`current_limit` instead of an assortment of :code:`current_max`, :code:`Ilim`, :code:`max_curr`, etc.
* If there is already an instrument with a similar command set, check if you can inherit from that one and just tweak a couple of things. This massively reduces code duplication and maintenance effort. The section :ref:`instruments_with_similar_features` shows how to achieve that.
* The bulk of your instrument's interface will probably be made up of properties for quantities to set and/or read out. Our custom properties (see :ref:`writing_properties` ff. below) offer some convenience features and are therefore preferable, but plain Python properties are also fine.
* "Actions", commands or verbs should typically be methods, not properties: :code:`recall()`, :code:`trigger_scan()`, :code:`prepare_resistance_measurement()`, etc.
* This separation between properties and methods also naturally helps with observing the `"command-query separation" principle <https://en.wikipedia.org/wiki/Command%E2%80%93query_separation>`__.
* If your instrument has multiple identical channels, see XXX. TODO: write section on channel implementations

In principle, you are free to write any methods that are necessary for interacting with the instrument. When doing so, make sure to use the :code:`self.ask(command)`, :code:`self.write(command)`, and :code:`self.read()` methods to issue commands instead of calling the adapter directly. If the communication requires changes to the commands sent/received, you can override these methods in your instrument, for further information see advanced_communication_protocols_.

In practice, we have developed a number of best practices for making instruments easy to write and maintain. The following sections detail these, which are highly encouraged to follow.

Common instrument types
***********************
There are a number of categories that many instruments fit into.
In the future, pymeasure should gain an abstraction layer based on that, see `this issue <https://github.com/pymeasure/pymeasure/issues/416>`__.
Until that is ready, here are a couple of guidelines towards a more uniform API.
Note that not all already available instruments follow these, but expect this to be harmonized in the future.

Frequent properties
-------------------
If your instrument has an **output** that can be switched on and off, use a :ref:`boolean property <boolean-properties>` called :code:`output_enabled`.

Power supplies
--------------
PSUs typically can measure the *actual* current and voltage, as well as have settings for the voltage level and the current limit.
To keep naming clear and avoid confusion, implement the properties :code:`current`, :code:`voltage`, :code:`voltage_setpoint` and :code:`current_limit`, respectively.

Managing status codes or other indicator values
***********************************************
Often, an instrument features one or more collections of specific values that signal some status, an instrument mode or a number of possible configuration values.
Typically, these are collected in mappings of some sort, as you want to provide a clear and understandable value to the user, while abstracting away the raw data, think :code:`ACQUISITION_MODE` instead of :code:`0x04`.
The mappings normally are kept at module level (i.e. not defined within the instrument class), so that they are available when using the property factories.
This is a small drawback of using Python class attributes.

The easiest way to handle these mappings is a plain :code:`dict`.
However, there is often a better way, the Python :code:`enum.Enum`.
To cite the `Python documentation <https://docs.python.org/3.11/howto/enum.html>`__,

    An Enum is a set of symbolic names bound to unique values. They are similar to global variables, but they offer a more useful :code:`repr()`, grouping, type-safety, and a few other features.

As our signal values are often integers, the most appropriate enum types are :code:`IntEnum` and :code:`IntFlag`.

:code:`IntEnum` is the same as :code:`Enum`, but its members are also integers and can be used anywhere that an integer can be used (so their use for composing commands is transparent), but logic/code they appear in is much more legible.

.. doctest::

    >>> from enum import IntEnum
    >>> class InstrMode(IntEnum):
    ...     WAITING = 0x00
    ...     HEATING = 0x01
    ...     COOLING = 0x05
    ...
    >>> received_from_device = 0x01
    >>> current_mode = InstrMode(received_from_device)
    >>> if current_mode == InstrMode.WAITING:
    ...     print('Idle')
    ... else:
    ...     print(current_mode)
    ...     print(f'Mode value: {current_mode}')
    ...
    InstrMode.HEATING
    Mode value: 1

:code:`IntFlag` has the added benefit that it supports bitwise operators and combinations, and as such is a good fit for status bitmasks or error codes that can represent multiple values:

.. doctest::

    >>> from enum import IntFlag
    >>> class ErrorCode(IntFlag):
    ...     TEMP_OUT_OF_RANGE = 8
    ...     TEMPSENSOR_FAILURE = 4
    ...     COOLER_FAILURE = 2
    ...     HEATER_FAILURE = 1
    ...     OK = 0
    ...
    >>> received_from_device = 7
    >>> print(ErrorCode(received_from_device))
    ErrorCode.TEMPSENSOR_FAILURE|COOLER_FAILURE|HEATER_FAILURE

:code:`IntFlags` are used by many instruments for the purpose just demonstrated.

The status property could look like this:
.. testcode::

    status = Instrument.measurement(
        "STB?", 
        """Measure the status of the device as enum.""",
        get_process=lambda v: ErrorCode(v), 
   )

.. _default_connection_settings:

Defining default connection settings
====================================

When implementing instruments, it's sometimes necessary to define default connection settings.
This might be because an instrument connection requires *specific non-default settings*, or because your instrument actually supports *multiple interfaces*.

The :py:class:`~pymeasure.adapters.VISAAdapter` class offers a flexible way of dealing with connection settings fully within the initializer of your instrument.

Single interface
****************

The simplest version, suitable when the instrument connection needs default settings, just passes all keywords through to the ``Instrument`` initializer, which hands them over to :py:class:`~pymeasure.adapters.VISAAdapter` if ``adapter`` is a string or integer.

.. code-block:: python

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter,
            "Extreme 5000",
            **kwargs
        )

If you want to set defaults that should be prominently visible to the user and may be overridden, place them in the signature.
This is suitable when the instrument has one type of interface, or any defaults are valid for all interface types, see the documentation in :py:class:`~pymeasure.adapters.VISAAdapter` for details.

.. code-block:: python

    def __init__(self, adapter, baud_rate=2400, **kwargs):
        super().__init__(
            adapter,
            "Extreme 5000",
            baud_rate=baud_rate,
            **kwargs
        )

If you want to set defaults, but they don't need to be prominently exposed for replacement, use this pattern, which sets the value only when there is no entry in ``kwargs``, yet.

.. code-block:: python

    def __init__(self, adapter, **kwargs):
        kwargs.setdefault('timeout', 1500)
        super().__init__(
            adapter,
            "Extreme 5000",
            **kwargs
        )

Multiple interfaces
*******************

Now, if you have instruments with multiple interfaces (e.g. serial, TCPI/IP, USB), things get interesting.
You might have settings common to all interfaces (like ``timeout``), but also settings that are only valid for one interface type, but not others.

The trick is to add keyword arguments that name the interface type, like ``asrl`` or ``gpib``, below (see `here <https://pyvisa.readthedocs.io/en/latest/api/constants.html#pyvisa.constants.InterfaceType>`__ for the full list).
These then contain a *dictionary* with the settings specific to the respective interface:

.. code-block:: python

    def __init__(self, adapter, baud_rate=2400, **kwargs):
        kwargs.setdefault('timeout', 1500)
        super().__init__(
            adapter,
            "Extreme 5000",
            gpib=dict(enable_repeat_addressing=False,
                      read_termination='\r'),
            asrl={'baud_rate': baud_rate,
                  'read_termination': '\r\n'},
            **kwargs
        )

When the instrument instance is created, the interface-specific settings for the actual interface being used get merged with ``**kwargs`` before passing them on to PyVISA, the rest is discarded. 
This way, we always pass on a valid set of arguments.
In addition, any entries in ``**kwargs**`` take precedence, so if they need to, it is *still* possible for users to override any defaults you set in the instrument definition.

For many instruments, the simple way presented first is enough, but in case you have a more complex arrangement to implement, see whether advanced_communication_protocols_ fits your bill. If, for some exotic reason, you need a special connection type, which you cannot model with PyVISA, you can write your own Adapter.

.. _writing_properties:

Writing properties
==================

In PyMeasure, `Python properties`_ are the preferred method for dealing with variables that are read or set.

The property factories
**********************
PyMeasure comes with three central convenience factory functions for making properties for classes: :func:`Instrument.control <pymeasure.instruments.Instrument.control>`, :func:`Instrument.measurement <pymeasure.instruments.Instrument.measurement>`, and :func:`Instrument.setting <pymeasure.instruments.Instrument.setting>`.

The :func:`Instrument.measurement <pymeasure.instruments.Instrument.measurement>` function returns a property that can only read values from an instrument.
For example, if our "Extreme 5000" has the :code:`*IDN?` command, we can write the following property to be added after the :code:`def __init__` line in our above example class, or added to the class after the fact as in the code here:

.. _Python properties: https://docs.python.org/3/howto/descriptor.html#properties

.. testcode::

     Extreme5000.cell_temp = Instrument.measurement(
        ":TEMP?",
        """Measure the temperature of the reaction cell.""",
     )

.. testcode::
    :hide:
    
    # We have to fake this silently because the FakeInstrument cannot do
    # a measurement property, it only mirrors values that you sent first.
    Extreme5000.cell_temp = 127.2
    
You will notice that a documentation string is required, see :ref:`docstrings` for details.

When we use this property we will get the temperature of the reaction cell.

.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.cell_temp  # Sends ":TEMP?" to the device
    127.2

The :func:`Instrument.control <pymeasure.instruments.Instrument.control>` function extends this behavior by creating a property that you can read and set. For example, if our "Extreme 5000" has the :code:`:VOLT?` and :code:`:VOLT <float>` commands that are in Volts, we can write the following property.

.. testcode::

    Extreme5000.voltage = Instrument.control(
        ":VOLT?", ":VOLT %g",
        """Control the voltage in Volts (float)."""
    )

You will notice that we use the `Python string format`_ :code:`%g` to format passed-through values as floating point.

.. _Python string format: https://docs.python.org/3/library/string.html#format-specification-mini-language

We can use this property to set the voltage to 100 mV, which will send the appropriate command, and then to request the current voltage:

.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.voltage = 0.1        # Sends ":VOLT 0.1" to set the voltage to 100 mV
    >>> extreme.voltage              # Sends ":VOLT?" to query for the current value
    0.1

Finally, the :func:`Instrument.setting <pymeasure.instruments.Instrument.setting>` function can only set, but not read values.

Using the :func:`Instrument.control <pymeasure.instruments.Instrument.control>`, :func:`Instrument.measurement <pymeasure.instruments.Instrument.measurement>`, and :func:`Instrument.control <pymeasure.instruments.Instrument.control>` functions, you can create a number of properties for basic measurements and controls.

The next sections detail additional features of the property factories.
These allow you to write properties that cover specific ranges, or that have to map between a real value to one used in the command. Furthermore it is shown how to perform more complex processing of return values from your device.

.. _validators:

Restricting values with validators
**********************************
Many GPIB/SCPI commands are more restrictive than our basic examples above. The :func:`Instrument.control <pymeasure.instruments.Instrument.control>` function has the ability to encode these restrictions using :mod:`validators <pymeasure.instruments.validators>`. A validator is a function that takes a value and a set of values, and returns a valid value or raises an exception. There are a number of pre-defined validators in :mod:`pymeasure.instruments.validators` that should cover most situations. We will cover the four basic types here.

In the examples below we assume you have imported the validators.

.. testcode::
    :hide:

    from pymeasure.instruments.validators import strict_discrete_set, strict_range, truncated_range, truncated_discrete_set

In many situations you will also need to process the return string in order to extract the wanted quantity or process a value before sending it to the device. The :func:`Instrument.control <pymeasure.instruments.Instrument.control>`, :func:`Instrument.measurement <pymeasure.instruments.Instrument.measurement>` and :func:`Instrument.setting <pymeasure.instruments.Instrument.setting>` function also provide means to achieve this.

In a restricted range
---------------------

If you have a property with a restricted range, you can use the :func:`strict_range <pymeasure.instruments.validators.strict_range>` and :func:`truncated_range <pymeasure.instruments.validators.strict_range>` functions.

For example, if our "Extreme 5000" can only support voltages from -1 V to 1 V, we can modify our previous example to use a strict validator over this range.

.. testcode::
  
    Extreme5000.voltage = Instrument.control(
        ":VOLT?", ":VOLT %g",
        """Control the voltage in Volts (float strictly from -1 to 1).""",
        validator=strict_range,
        values=[-1, 1]
    )

Now our voltage will raise a ValueError if the value is out of the range.

.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.voltage = 100
    Traceback (most recent call last):
    ...
    ValueError: Value of 100 is not in range [-1,1]

This is useful if you want to alert the programmer that they are using an invalid value. However, sometimes it can be nicer to truncate the value to be within the range.

.. testcode::

    Extreme5000.voltage = Instrument.control(
        ":VOLT?", ":VOLT %g",
        """Control the voltage in Volts (float from -1 to 1).

        Invalid voltages are truncated.
        """,
        validator=truncated_range,
        values=[-1, 1]
    )

Now our voltage will not raise an error, and will truncate the value to the range bounds.

.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.voltage = 100  # Executes ":VOLT 1"
    >>> extreme.voltage
    1.0

In a discrete set
-----------------

Often a control property should only take a few discrete values. You can use the :func:`strict_discrete_set <pymeasure.instruments.validators.strict_discrete_set>` and :func:`truncated_discrete_set <pymeasure.instruments.validators.truncated_discrete_set>` functions to handle these situations. The strict version raises an error if the value is not in the set, as in the range examples above.

For example, if our "Extreme 5000" has a :code:`:RANG <float>` command that sets the voltage range that can take values of 10 mV, 100 mV, and 1 V in Volts, then we can write a control as follows.

.. testcode::

    Extreme5000.voltage = Instrument.control(
        ":RANG?", ":RANG %g",
        """Control the voltage range in Volts (float in 10e-3, 100e-3, 1).""",
        validator=truncated_discrete_set,
        values=[10e-3, 100e-3, 1]
    )

Now we can set the voltage range, which will automatically truncate to an appropriate value.

.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.voltage = 0.08
    >>> extreme.voltage
    0.1


Mapping values
**************

Now that you are familiar with the validators, you can additionally use maps to satisfy instruments which require non-physical values. The :code:`map_values` argument of :func:`Instrument.control <pymeasure.instruments.Instrument.control>` enables this feature.

If your set of values is a list, then the command will use the index of the list. For example, if our "Extreme 5000" instead has a :code:`:RANG <integer>`, where 0, 1, and 2 correspond to 10 mV, 100 mV, and 1 V, then we can use the following control.

.. testcode::

    Extreme5000.voltage = Instrument.control(
        ":RANG?", ":RANG %d",
        """Control the voltage range in Volts (float in 10 mV, 100 mV and 1 V).
        """,
        validator=truncated_discrete_set,
        values=[10e-3, 100e-3, 1],
        map_values=True
    )

Now the actual GPIB/SCIP command is ":RANG 1" for a value of 100 mV, since the index of 100 mV in the values list is 1.

.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.voltage = 100e-3
    >>> extreme.read()
    '1'
    >>> extreme.voltage = 1
    >>> extreme.voltage
    1

Dictionaries provide a more flexible method for mapping between real-values and those required by the instrument. If instead the :code:`:RANG <integer>` took 1, 2, and 3 to correspond to 10 mV, 100 mV, and 1 V, then we can replace our previous control with the following.

.. testcode::

    Extreme5000.voltage = Instrument.control(
        ":RANG?", ":RANG %d",
        """Control the voltage range in Volts (float in 10 mV, 100 mV and 1 V).
        """,
        validator=truncated_discrete_set,
        values={10e-3:1, 100e-3:2, 1:3},
        map_values=True
    )

.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.voltage = 10e-3
    >>> extreme.read()
    '1'
    >>> extreme.voltage = 100e-3
    >>> extreme.voltage
    0.1

The dictionary now maps the keys to specific values. The values and keys can be any type, so this can support properties that use strings:

.. testcode::
  
    Extreme5000.channel = Instrument.control(
        ":CHAN?", ":CHAN %d",
        """Control the measurement channel (string strictly in 'X', 'Y', 'Z').""",
        validator=strict_discrete_set,
        values={'X':1, 'Y':2, 'Z':3},
        map_values=True
    )

.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.channel = 'X'
    >>> extreme.read()
    '1'
    >>> extreme.channel = 'Y'
    >>> extreme.channel
    'Y'

As you have seen, the :func:`Instrument.control <pymeasure.instruments.Instrument.control>` function can be significantly extended by using validators and maps.

.. _boolean-properties:

Boolean properties
******************

The idea of using maps can be leveraged to implement properties where the user-facing values are booleans, so you can interact in a pythonic way using :code:`True` and :code:`False`:

.. testcode::

    Extreme5000.output_enabled = Instrument.control(
        "OUTP?", "OUTP %d",
        """Control the instrument output is enabled (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},  # the dict values could also be "on" and "off", etc. depending on the device
    )


.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.output_enabled = True
    >>> extreme.read()
    '1'
    >>> extreme.output_enabled = False
    >>> extreme.output_enabled
    False
    >>> # Invalid input raises an exception
    >>> extreme.output_enabled = 34
    Traceback (most recent call last):
    ...
    ValueError: Value of 34 is not in the discrete set {True: 1, False: 0}

Good names for boolean properties are chosen such that they could also be a yes/no question: "Is the output enabled?" -> :code:`output_enabled`, :code:`display_active`, etc.

Processing of set values
************************

The :func:`Instrument.control <pymeasure.instruments.Instrument.control>`, and :func:`Instrument.setting <pymeasure.instruments.Instrument.setting>` allow a keyword argument `set_process` which must be a function that takes a value after validation and performs processing before value mapping. This function must return the processed value. This can be typically used for unit conversions as in the following example:


.. testcode::

    Extreme5000.current = Instrument.setting(
        ":CURR %g",
        """Set the measurement current in A (float strictly from 0 to 10).""",
        validator=strict_range,
        values=[0, 10],
        set_process=lambda v: 1e3*v,  # convert current to mA
    )

.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.current = 1  # set current to 1000 mA

Processing of return values
***************************

Similar to `set_process` the :func:`Instrument.control <pymeasure.instruments.Instrument.control>`, and :func:`Instrument.measurement <pymeasure.instruments.Instrument.measurement>` functions allow a `get_process` argument which if specified must be a function that takes a value and performs processing before value mapping. The function must return the processed value. In analogy to the example above this can be used for example for unit conversion:

.. testcode::

    Extreme5000.current = Instrument.control(
        ":CURR?", ":CURR %g",
        """Control the measurement current in A (float strictly from 0 to 10).""",
        validator=strict_range,
        values=[0, 10],
        set_process=lambda v: 1e3*v,  # convert to mA
        get_process=lambda v: 1e-3*v,  # convert to A
    )

.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.current = 3.1
    >>> extreme.current
    3.1

Another use-case of `set-process`, `get-process` is conversion from/to a :code:`pint.Quantity`. Modifying above example to set or return a quantity, we get:

.. testcode::

    from pymeasure.units import ureg

    Extreme5000.current = Instrument.control(
        ":CURR?", ":CURR %g",
        """Control the measurement current (float).""",
        set_process=lambda v: v.m_as(ureg.mA),  # send the value as mA to the device
        get_process=lambda v: ureg.Quantity(v, ureg.mA),  # convert to quantity
    )

.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.current = 3.1 * ureg.A
    >>> extreme.current.m_as(ureg.A)
    3.1

.. note::

    This is, how quantities can be used in pymeasure instruments right now. `Issue 666 <https://github.com/pymeasure/pymeasure/issues/666>`_ develops a more convenient implementation of quantities in the property factories.

`get_process` can also be used to perform string processing. Let's say your instrument returns a value with its unit (e.g. :code:`1.23 nF`), which has to be removed. This could be achieved by the following code:

.. testcode::

    Extreme5000.capacity = Instrument.measurement(
        ":CAP?",
        """Measure the capacity in nF (float).""",
        get_process=lambda v: float(v.replace('nF', ''))
    )

The same can be also achieved by the `preprocess_reply` keyword argument to :func:`Instrument.control <pymeasure.instruments.Instrument.control>` or :func:`Instrument.measurement <pymeasure.instruments.Instrument.measurement>`. This function is forwarded to :func:`Adapter.values <pymeasure.adapters.values>` and runs directly after receiving the reply from the device. One can therefore take advantage of the built in casting abilities and simplify the code accordingly:

.. testcode::

    Extreme5000.capacity = Instrument.measurement(
        ":CAP?",
        """Measure the capacity in nF (float).""",
        preprocess_reply=lambda v: v.replace('nF', '')
        # notice how we don't need to cast to float anymore
    )

Tweaking command strings
************************
If you need to tweak

* the :code:`set_command` string immediately before the value to set is inserted via string formatting (:code:`%g` etc.), or
* the :code:`get_command` string before sending it to the device,

use the :code:`command_process` parameter of :meth:`~pymeasure.instruments.Instrument.control`.

Note that there is only one parameter for both setting and getting, so the utility of this is probably limited.
Note also that for adding e.g. channel identifiers, there are other, more preferable methods.

Checking the instrument for errors
**********************************
If you need to separately ask your instrument about its error state after getting/setting, use the parameters :code:`check_get_errors` and :code:`check_set_errors` of :meth:`~pymeasure.instruments.Instrument.control`, respectively.
If those are enabled, the method :meth:`~pymeasure.instruments.Instrument.check_errors` will be called after device communication has concluded.

Using multiple values
*********************
Seldomly, you might need to send/receive multiple values in one command.
The :func:`Instrument.control <pymeasure.instruments.Instrument.control>` function can be used with multiple values at one time, passed as a tuple. Say, we may set voltages and frequencies in our "Extreme 5000", and the the commands for this are :code:`:VOLTFREQ?` and :code:`:VOLTFREQ <float>,<float>`, we could use the following property:

.. testcode::

    Extreme5000.combination = Instrument.control(
        ":VOLTFREQ?", ":VOLTFREQ %g,%g",
        """Simultaneously control the voltage in Volts and the frequency in Hertz (both float).

        This property is set by a tuple.
        """
    )

In use, we could set the voltage to 200 mV, and the Frequency to 931 Hz, and read both values immediately afterwards. 

.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.combination = (0.2, 931)        # Executes ":VOLTFREQ 0.2,931"
    >>> extreme.combination                     # Reads ":VOLTFREQ?"
    [0.2, 931.0]

This interface is not too convenient, but luckily not often needed.

Dynamic properties
******************

As described in previous sections, Python properties are a very powerful tool to easily code an instrument's programming interface.
One very interesting feature provided in PyMeasure is the ability to adjust properties' behaviour in subclasses or dynamically in instances.
This feature allows accomodating some interesting use cases with a very compact syntax.

Dynamic features of a property are enabled by setting its :code:`dynamic` parameter to :code:`True`.

Afterwards, creating specifically-named attributes (either in class definitions or on instances) allows modifying the parameters used at the time of property definition.
You need to define an attribute whose name is `<property name>_<property_parameter>` and assign to it the desired value.
Pay attention *not* to inadvertently define other class attribute or instance attribute names matching this pattern, since they could unintentionally modify the property behaviour.

.. note::
   To clearly distinguish these special attributes from normal class/instance attributes, they can only be set, not read. 

The mechanism works for all the parameters in properties, except :code:`dynamic` and :code:`docs` -- see :func:`Instrument.control <pymeasure.instruments.Instrument.control>`, :func:`Instrument.measurement <pymeasure.instruments.Instrument.measurement>`, :func:`Instrument.setting <pymeasure.instruments.Instrument.setting>`.

Dynamic validity range
----------------------
Let's assume we have an instrument with a command that accepts a different valid range of values depending on its current state.
The code below shows how this can be accomplished with dynamic properties.

.. testcode::
  
    Extreme5000.voltage = Instrument.control(
        ":VOLT?", ":VOLT %g",
        """Control the voltage in Volts (float).""",
        validator=strict_range,
        values=[-1, 1],
        dynamic = True,
    )
    def set_bipolar_mode(self, enabled = True):
        """Safely switch between bipolar/unipolar mode."""

        # some code to switch off the output first
        # ...

        if enabled:
            self.mode = "BIPOLAR"
            # set valid range of "voltage" property
            self.voltage_values = [-1, 1]
        else:
            self.mode = "UNIPOLAR"
            # note the "propertyname_parametername" form of the attribute
            self.voltage_values = [0, 1]


Now our voltage property has a dynamic validity range, either [-1, 1] or [0, 1].
A side effect of this is that the property's docstring should be less specific, to avoid it containing dynamically changed information (like the admissible value range).
In this example, the property name was :code:`voltage` and the parameter to adjust was :code:`values`, so we used :code:`self.voltage_values` to set our desired values.

.. _instruments_with_similar_features:

Instruments with similar features
=================================

When instruments have a similar set of features, it makes sense to use inheritance to obtain most of the functionality from a parent instrument class, instead of copy-pasting code.

.. note::
    Don't forget to update the instrument's :code:`name` attribute accordingly, by either supplying an appropriate argument (if available) during the :code:`super().__init__()` call, or by setting it anew below that call.

In some cases, one only needs to add additional properties and methods.
In other cases, some of the already present properties/methods need to be completely replaced by defining them again in the derived class.
Often, however, only some details need to be changed.
This can be dealt with efficiently using dynamic properties.

Instrument family with different parameter values
*************************************************

A common case is to have a family of similar instruments with some parameter range different for each family member.
In this case you would update the specific class parameter range without rewriting the entire property:

.. testcode::
    :hide:

    # Behind the scene, load the real Instrument
    from pymeasure.instruments import Instrument
    from pymeasure.test import expected_protocol

.. testcode::

    class FictionalInstrumentFamily(Instrument):
        frequency = Instrument.setting(
            "FREQ %g",
            """Set the frequency (float).""",
            validator=strict_range,
            values=[0, 1e9],
            dynamic=True,
            # ... other possible parameters follow
        )
        #
        # ... complete class implementation here
        #

    class FictionalInstrument_1GHz(FictionalInstrumentFamily):
        pass

    class FictionalInstrument_3GHz(FictionalInstrumentFamily):
        frequency_values = [0, 3e9]

    class FictionalInstrument_9GHz(FictionalInstrumentFamily):
        frequency_values = [0, 9e9]

.. testcode::
    :hide:

    with expected_protocol(FictionalInstrument_9GHz, [("FREQ 5e+09", None)], name="Test") as inst:
        inst.frequency = 5e9

Notice how easily you can derive the different family members from a common class, and the fact that the attribute is now defined at class level and not at instance level.

Instruments with similar command syntax
***************************************

Another use case involves maintaining compatibility between instruments with commands having different syntax, like in the following example.

.. code-block:: python

    class MultimeterA(Instrument):
        voltage = Instrument.measurement(get_command="VOLT?",...)

        # ...full class definition code here

    class MultimeterB(MultimeterA):
        # Same as brand A multimeter, but the command to read voltage 
        # is slightly different
        voltage_get_command = "VOLTAGE?"

In the above example, :code:`MultimeterA` and :code:`MultimeterB` use a different command to read the voltage, but the rest of the behaviour is identical.
:code:`MultimeterB` can be defined subclassing :code:`MultimeterA` and just implementing the difference.


.. _advanced_communication_protocols:

Advanced communication protocols
================================

Some devices require a more advanced communication protocol, e.g. due to checksums or device addresses. In most cases, it is sufficient to subclass :meth:`Instrument.write <pymeasure.instruments.Instrument.write>` and :meth:`Instrument.read <pymeasure.instruments.Instrument.read>`.


Instrument's inner workings
***************************

In order to adjust an instrument for more complicated protocols, it is key to understand the different parts.

The :class:`~pymeasure.adapters.Adapter` exposes :meth:`~pymeasure.adapters.Adapter.write` and :meth:`~pymeasure.adapters.Adapter.read` for strings, :meth:`~pymeasure.adapters.Adapter.write_bytes` and :meth:`~pymeasure.adapters.Adapter.read_bytes` for bytes messages. These are the most basic methods, which log all the traffic going through them. For the actual communication, they call private methods of the Adapter in use, e.g. :meth:`VISAAdapter._read <pymeasure.adapters.VISAAdapter._read>`.
For binary data, like waveforms, the adapter provides also :meth:`~pymeasure.adapters.Adapter.write_binary_values` and :meth:`~pymeasure.adapters.Adapter.read_binary_values`, which use the aforementioned methods.
You do not need to call all these methods directly, instead, you should use the methods of :class:`~pymeasure.instruments.Instrument` with the same name. They call the Adapter for you and keep the code tidy.

Now to :class:`~pymeasure.instruments.Instrument`. The most important methods are :meth:`~pymeasure.instruments.Instrument.write` and :meth:`~pymeasure.instruments.Instrument.read`, as they are the most basic building blocks for the communication. The pymeasure properties (:meth:`Instrument.control <pymeasure.instruments.Instrument.control>` and its derivatives :meth:`Instrument.measurement <pymeasure.instruments.Instrument.measurement>` and :meth:`Instrument.setting <pymeasure.instruments.Instrument.setting>`) and probably most of your methods and properties will call them. In any instrument, :meth:`write` should write a general string command to the device in such a way, that it understands it. Similarly, :meth:`read` should return a string in a general fashion in order to process it further.

The getter of :meth:`Instrument.control <pymeasure.instruments.Instrument.control>` does not call them directly, but via a chain of methods. It calls :meth:`~pymeasure.instruments.Instrument.values` which in turn calls :meth:`~pymeasure.instruments.Instrument.ask` and processes the returned string into understandable values. :meth:`~pymeasure.instruments.Instrument.ask` sends the readout command via :meth:`write`, waits some time if necessary via :meth:`wait_for`, and reads the device response via :meth:`read`.

Similarly, :meth:`Instrument.binary_values <pymeasure.instruments.Instrument.binary_values>` sends a command via :meth:`write`, waits with :meth:`wait_till_read`, but reads the response via :meth:`Adapter.read_binary_values <pymeasure.adapters.Adapter.read_binary_values>`.


Adding a device address and adding delay
****************************************

Let's look at a simple example for a device, which requires its address as the first three characters and returns the same style. This is straightforward, as :meth:`write` just prepends the device address to the command, and :meth:`read` has to strip it again doing some error checking. Similarly, a checksum could be added.
Additionally, the device needs some time after it received a command, before it responds, therefore :meth:`wait_for` waits always a certain time span.

.. testcode::

    class ExtremeCommunication(Instrument):
        """Control the ExtremeCommunication instrument.

        :param address: The device address for the communication.
        :param query_delay: Wait time after writing and before reading in seconds.
        """
        def __init__(self, adapter, address=0, query_delay=0.1):
            super().__init__(adapter, "ExtremeCommunication")
            self.address = f"{address:03}"
            self.query_delay = query_delay
    
        def write(self, command):
            """Add the device address in front of every command before sending it."""
            super().write(self.address + command)
    
        def wait_for(self, query_delay=0):
            """Wait for some time.

            :param query_delay: override the global query_delay.
            """
            super().wait_for(query_delay or self.query_delay)
    
        def read(self):
            """Read from the device and check the response.

            Assert that the response starts with the device address.
            """
            got = super().read()
            if got.startswith(self.address):
                return got[3:]
            else:
                raise ConnectionError(f"Expected message address '{self.address}', but read '{got[3:]}' for wrong address '{got[:3]}'.")
    
        voltage = Instrument.measurement(
            ":VOLT:?", """Measure the voltage in Volts.""")

.. testcode:: :hide:

    with expected_protocol(ExtremeCommunication, [("012:VOLT:?", "01215.5")], address=12
        ) as inst:
        assert inst.voltage == 15.5

If the device is initialized with :code:`address=12`, a request for the voltage would send :code:`"012:VOLT:?"` to the device and expect a response beginning with :code:`"012"`.


Bytes communication
*******************

Some devices do not expect ASCII strings but raw bytes. In those cases, you can call the :meth:`write_bytes` and :meth:`read_bytes` in your :meth:`write` and :meth:`read` methods. The following example shows an instrument, which has registers to be written and read via bytes sent.

.. testcode::

    class ExtremeBytes(Instrument):
        """Control the ExtremeBytes instrument with byte-based communication."""
        def __init__(self, adapter):
            super().__init__(adapter, "ExtremeBytes")
    
        def write(self, command):
            """Write to the device according to the comma separated command.
    
            :param command: R or W for read or write, hexadecimal address, and data.
            """
            function, address, data = command.split(",")
            b = [0x03] if function == "R" else [0x10]
            b.extend(int(address, 16).to_bytes(2, byteorder="big"))
            b.extend(int(data).to_bytes(length=8, byteorder="big", signed=True))
            self.write_bytes(bytes(b))
    
        def read(self):
            """Read the response and return the data as an integer, if applicable."""
            response = self.read_bytes(2)  # return type and payload
            if response[0] == 0x00:
                raise ConnectionError(f"Device error of type {response[1]} occurred.")
            if response[0] == 0x03:
                # read that many bytes and return them as an integer
                data = self.read_bytes(response[1])
                return int.from_bytes(data, byteorder="big", signed=True)
            if response[0] == 0x10 and response[1] != 0x00:
                raise ConnectionError(f"Writing to the device failed with error {response[1]}")
    
        voltage = Instrument.control(
            "R,0x106,1", "W,0x106,%i",
            """Control the output voltage in mV.""",
        )

.. testcode:: :hide:

    with expected_protocol(ExtremeBytes, [(b"\x03\x01\x06\x00\x00\x00\x00\x00\x00\x00\x01", b"\x03\x01\x0f")]) as inst:
        assert inst.voltage == 15


Writing tests
=============

Tests are very useful for writing good code.
We have a number of tests checking the correctness of the pymeasure implementation.
Those tests (located in the :code:`tests` directory) are run automatically on our CI server, but you can also run them locally using :code:`pytest`.

When adding instruments, your primary concern will be tests for the *instrument driver* you implement.
We distinguish two groups of tests for instruments: the first group does not rely on a connected instrument.
These tests verify that the implemented instrument driver exchanges the correct messages with a device (for example according to a device manual).
We call those "protocol tests".
The second group tests the code with a device connected.

Implement device tests by adding files in the :code:`tests/instruments/...` directory tree, mirroring the structure of the instrument implementations.
There are other instrument tests already available that can serve as inspiration.

Protocol tests
**************

In order to verify the expected working of the device code, it is good to test every part of the written code. The :func:`~pymeasure.test.expected_protocol` context manager (using a :class:`~pymeasure.adapters.ProtocolAdapter` internally) simulates the communication with a device and verifies that the sent/received messages triggered by the code inside the :code:`with` statement match the expectation.

.. code-block:: python

    import pytest

    from pymeasure.test import expected_protocol

    from pymeasure.instruments.extreme5000 import Extreme5000

    def test_voltage():
        """Verify the communication of the voltage getter."""
        with expected_protocol(
            Extreme5000,
            [(":VOLT 0.345", None),
             (":VOLT?", "0.3000")],
        ) as inst:
            inst.voltage = 0.345
            assert inst.voltage == 0.3

In the above example, the imports import the pytest package, the expected_protocol and the instrument class to be tested.

The first parameter, Extreme5000, is the class to be tested.

When setting the voltage, the driver sends a message (:code:`":VOLT 0.345"`), but does not expect a response (:code:`None`). Getting the voltage sends a query (:code:`":VOLT?"`) and expects a string response (:code:`"0.3000"`).
Therefore, we expect two pairs of send/receive exchange.
The list of those pairs is the second argument, the expected message protocol.

The context manager returns an instance of the class (:code:`inst`), which is then used to trigger the behaviour corresponding to the message protocol (e.g. by using its properties).

If the communication of the driver does not correspond to the expected messages, an Exception is raised.

.. note::
    The expected messages are **without** the termination characters, as they depend on the connection type and are handled by the normal adapter (e.g. :class:`VISAAdapter`).

Some protocol tests in the test suite can serve as examples:

* Testing a simple instrument: :code:`tests/instruments/keithley/test_keithley2000.py`
* Testing a multi-channel instrument: :code:`tests/instruments/tektronix/test_afg3152.py`
* Testing instruments using frame-based communication: :code:`tests/instruments/hcp/tc038.py`

Device tests
************

It can be useful as well to test the code against an actual device. The necessary device setup instructions (for example: connect a probe to the test output) should be written in the header of the test file or test methods. There should be the connection configuration (for example serial port), too.
In order to distinguish the test module from protocol tests, the filename should be :code:`test_instrumentName_with_device.py`, if the device is called :code:`instrumentName`.

Mark tests that require instrument hardware to be `skipped <https://docs.pytest.org/en/stable/how-to/skipping.html>`_ by default.
If the whole test module requires hardware, add this at module level/after the import statements:

.. code-block:: python

    pytest.skip('Only works with connected hardware', allow_module_level=True)


If only some test functions in a module need hardware, decorate those with

.. code-block:: python

    @pytest.mark.skip(reason='Only works with connected hardware')
    def test_something():
        ...

If you want to run these tests with a connected device, select those tests and ignore the skip marker.
For example, if your tests are in a file called :code:`test_extreme5000.py`, invoke pytest with :code:`pytest -k extreme5000 --no-skip`.
