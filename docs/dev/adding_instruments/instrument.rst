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

.. testsetup::

    # Behind the scene, replace Instrument with FakeInstrument to enable
    # doctesting simple usage cases (default doctest group)
    from pymeasure.instruments.fakes import FakeInstrument as Instrument


.. testcode::

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

    # from pymeasure.instruments import Instrument

This is a minimal instrument definition:

.. testcode::
    
    class Extreme5000(Instrument):
        """Control the imaginary Extreme 5000 instrument."""

        def __init__(self, adapter, name="Extreme 5000", **kwargs):
            super().__init__(
                adapter,
                name,
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
* The bulk of your instrument's interface will probably be made up of properties for quantities to set and/or read out. Our custom properties (see :ref:`properties` ff. below) offer some convenience features and are therefore preferable, but plain Python properties are also fine.
* "Actions", commands or verbs should typically be methods, not properties: :code:`recall()`, :code:`trigger_scan()`, :code:`prepare_resistance_measurement()`, etc.
* This separation between properties and methods also naturally helps with observing the `"command-query separation" principle <https://en.wikipedia.org/wiki/Command%E2%80%93query_separation>`__.
* If your instrument has multiple identical channels, see :ref:`channels`.

In principle, you are free to write any methods that are necessary for interacting with the instrument. When doing so, make sure to use the :code:`self.ask(command)`, :code:`self.write(command)`, and :code:`self.read()` methods to issue commands instead of calling the adapter directly. If the communication requires changes to the commands sent/received, you can override these methods in your instrument, for further information see :ref:`advanced_communication_protocols`.

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
Note that starting from Python version 3.11, the printed format of the :code:`IntEnum` and :code:`IntFlag` has been changed to return numeric value; however, the symbolic name can be obtained by printing its :code:`repr` or the :code:`.name` property, or returning the value in a REPL.

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
    ...     current_mode
    ...     print(repr(current_mode))
    ...     print(f'Mode value: {current_mode}')
    ...
    <InstrMode.HEATING: 1>
    <InstrMode.HEATING: 1>
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
    >>> ErrorCode(received_from_device)
    <ErrorCode.TEMPSENSOR_FAILURE|COOLER_FAILURE|HEATER_FAILURE: 7>

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

    def __init__(self, adapter, name="Extreme 5000", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

If you want to set defaults that should be prominently visible to the user and may be overridden, place them in the signature.
This is suitable when the instrument has one type of interface, or any defaults are valid for all interface types, see the documentation in :py:class:`~pymeasure.adapters.VISAAdapter` for details.

.. code-block:: python

    def __init__(self, adapter, name="Extreme 5000", baud_rate=2400, **kwargs):
        super().__init__(
            adapter,
            name,
            baud_rate=baud_rate,
            **kwargs
        )

If you want to set defaults, but they don't need to be prominently exposed for replacement, use this pattern, which sets the value only when there is no entry in ``kwargs``, yet.

.. code-block:: python

    def __init__(self, adapter, name="Extreme 5000", **kwargs):
        kwargs.setdefault('timeout', 1500)
        super().__init__(
            adapter,
            name,
            **kwargs
        )

Multiple interfaces
*******************

Now, if you have instruments with multiple interfaces (e.g. serial, TCPI/IP, USB), things get interesting.
You might have settings common to all interfaces (like ``timeout``), but also settings that are only valid for one interface type, but not others.

The trick is to add keyword arguments that name the interface type, like ``asrl`` or ``gpib``, below (see `here <https://pyvisa.readthedocs.io/en/latest/api/constants.html#pyvisa.constants.InterfaceType>`__ for the full list).
These then contain a *dictionary* with the settings specific to the respective interface:

.. code-block:: python

    def __init__(self, adapter, name="Extreme 5000", baud_rate=2400, **kwargs):
        kwargs.setdefault('timeout', 1500)
        super().__init__(
            adapter,
            name,
            gpib=dict(enable_repeat_addressing=False,
                      read_termination='\r'),
            asrl={'baud_rate': baud_rate,
                  'read_termination': '\r\n'},
            **kwargs
        )

When the instrument instance is created, the interface-specific settings for the actual interface being used get merged with ``**kwargs`` before passing them on to PyVISA, the rest is discarded. 
This way, we always pass on a valid set of arguments.
In addition, any entries in ``**kwargs**`` take precedence, so if they need to, it is *still* possible for users to override any defaults you set in the instrument definition.

For many instruments, the simple way presented first is enough, but in case you have a more complex arrangement to implement, see whether :ref:`advanced_communication_protocols` fits your bill. If, for some exotic reason, you need a special connection type, which you cannot model with PyVISA, you can write your own Adapter.
