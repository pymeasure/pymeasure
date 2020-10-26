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
    # Copyright (c) 2013-2020 PyMeasure Developers
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
    from pymeasure.instruments.instrument import FakeInstrument as Instrument

This is a minimal instrument definition:

.. testcode::
    
    class Extreme5000(Instrument):
        """ Represents the imaginary Extreme 5000 instrument.
        """

        def __init__(self, resourceName, **kwargs):
            super().__init__(
                resourceName,
                "Extreme 5000",
                **kwargs
            )

Make sure to include the PyMeasure license to each file, and add yourself as an author to the :code:`AUTHORS.txt` file.

In principle you are free to write any functions that are necessary for interacting with the instrument. When doing so, make sure to use the :code:`self.ask(command)`, :code:`self.write(command)`, and :code:`self.read()` methods to issue command instead of calling the adapter directly.

In practice, we have developed a number of convenience functions for making instruments easy to write and maintain. The following sections detail these conveniences and are highly encouraged.

Writing properties
==================

In PyMeasure, `Python properties`_ are the preferred method for dealing with variables that are read or set. 
PyMeasure comes with two convenience functions for making properties for classes. 
The :func:`Instrument.measurement <pymeasure.instruments.Instrument.measurement>` function returns a property that issues a GPIB/SCPI requests when the value is used. 
For example, if our "Extreme 5000" has the :code:`*IDN?` command we can write the following property to be added above the :code:`def __init__` line in our above example class, or added to the class after the fact as in the code here:

.. _Python properties: https://docs.python.org/3/howto/descriptor.html#properties

.. testcode::

     Extreme5000.id = Instrument.measurement(
        "*IDN?", """ Reads the instrument identification """
     )

.. testcode::
    :hide:
    
    # We are not mocking this in FakeInstrument, let's override silently
    Extreme5000.id = 'Extreme 5000 identification from instrument'
    
You will notice that a documentation string is required, and should be descriptive and specific.

When we use this property we will get the identification information.

.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.id           # Reads "*IDN?"
    'Extreme 5000 identification from instrument'

The :func:`Instrument.control <pymeasure.instruments.Instrument.control>` function extends this behavior by creating a property that you can read and set. For example, if our "Extreme 5000" has the :code:`:VOLT?` and :code:`:VOLT <float>` commands that are in Volts, we can write the following property.

.. testcode::

    Extreme5000.voltage = Instrument.control(
        ":VOLT?", ":VOLT %g",
        """ A floating point property that controls the voltage
        in Volts. This property can be set.
        """
    )

You will notice that we use the `Python string format`_ :code:`%g` to pass through the floating point.

.. _Python string format: https://docs.python.org/3/library/string.html#format-specification-mini-language

We can use this property to set the voltage to 100 mV, which will execute the command and then request the current voltage.

.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.voltage = 0.1        # Executes ":VOLT 0.1"
    >>> extreme.voltage              # Reads ":VOLT?"
    0.1

Using both of these functions, you can create a number of properties for basic measurements and controls. The next section details additional features of :func:`Instrument.control <pymeasure.instruments.Instrument.control>` that allow you to write properties that cover specific ranges, or have to map between a real value to one used in the command. Furthermore it is shown how to perform more complex processing of return values from your device.

.. _advanced-properties:

Advanced properties
===================

Many GPIB/SCIP commands are more restrictive than our basic examples above. The :func:`Instrument.control <pymeasure.instruments.Instrument.control>` function has the ability to encode these restrictions using :mod:`validators <pymeasure.instruments.validators>`. A validator is a function that takes a value and a set of values, and returns a valid value or raises an exception. There are a number of pre-defined validators in :mod:`pymeasure.instruments.validators` that should cover most situations. We will cover the four basic types here.

In the examples below we assume you have imported the validators.

.. testcode::
    :hide:

    from pymeasure.instruments.validators import strict_discrete_set, strict_range, truncated_range, truncated_discrete_set

In many situations you will also need to process the return string in order to extract the wanted quantity or process a value before sending it to the device. The :func:`Instrument.control <pymeasure.instruments.Instrument.control>`, :func:`Instrument.measurement <pymeasure.instruments.Instrument.measurement>` and :func:`Instrument.setting <pymeasure.instruments.Instrument.setting>` function also provide means to achieve this.

In a restricted range
*********************

If you have a property with a restricted range, you can use the :func:`strict_range <pymeasure.instruments.validators.strict_range>` and :func:`truncated_range <pymeasure.instruments.validators.strict_range>` functions.

For example, if our "Extreme 5000" can only support voltages from -1 V to 1 V, we can modify our previous example to use a strict validator over this range.

.. testcode::
  
    Extreme5000.voltage = Instrument.control(
        ":VOLT?", ":VOLT %g",
        """ A floating point property that controls the voltage
        in Volts, from -1 to 1 V. This property can be set. """,
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
        """ A floating point property that controls the voltage
        in Volts, from -1 to 1 V. Invalid voltages are truncated.
        This property can be set. """,
        validator=truncated_range,
        values=[-1, 1]
    )

Now our voltage will not raise an error, and will truncate the value to the range bounds.

.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.voltage = 100        # Executes ":VOLT 1"  
    >>> extreme.voltage
    1.0

In a discrete set
*****************

Often a control property should only take a few discrete values. You can use the :func:`strict_discrete_set <pymeasure.instruments.validators.strict_discrete_set>` and :func:`truncated_discrete_set <pymeasure.instruments.validators.truncated_discrete_set>` functions to handle these situations. The strict version raises an error if the value is not in the set, as in the range examples above.

For example, if our "Extreme 5000" has a :code:`:RANG <float>` command that sets the voltage range that can take values of 10 mV, 100 mV, and 1 V in Volts, then we can write a control as follows.

.. testcode::

    Extreme5000.voltage = Instrument.control(
        ":RANG?", ":RANG %g",
        """ A floating point property that controls the voltage
        range in Volts. This property can be set.
        """,
        validator=truncated_discrete_set,
        values=[10e-3, 100e-3, 1]
    )

Now we can set the voltage range, which will automatically truncate to an appropriate value.

.. doctest::

    >>> extreme = Extreme5000("GPIB::1")
    >>> extreme.voltage = 0.08
    >>> extreme.voltage
    0.1


Using maps
**********

Now that you are familiar with the validators, you can additionally use maps to satisfy instruments which require non-physical values. The :code:`map_values` argument of :func:`Instrument.control <pymeasure.instruments.Instrument.control>` enables this feature.

If your set of values is a list, then the command will use the index of the list. For example, if our "Extreme 5000" instead has a :code:`:RANG <integer>`, where 0, 1, and 2 correspond to 10 mV, 100 mV, and 1 V, then we can use the following control.

.. testcode::

    Extreme5000.voltage = Instrument.control(
        ":RANG?", ":RANG %d",
        """ A floating point property that controls the voltage
        range in Volts, which takes values of 10 mV, 100 mV and 1 V.
        This property can be set. """,
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
        """ A floating point property that controls the voltage
        range in Volts, which takes values of 10 mV, 100 mV and 1 V.
        This property can be set. """,
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
        """ A string property that controls the measurement channel,
        which can take the values X, Y, or Z.
        """,
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

Processing of set values
************************

The :func:`Instrument.control <pymeasure.instruments.Instrument.control>`, and :func:`Instrument.setting <pymeasure.instruments.Instrument.setting>` allow a keyword argument `set_process` which must be a function that takes a value after validation and performs processing before value mapping. This function must return the processed value. This can be typically used for unit conversions as in the following example:


.. testcode::

    Extreme5000.current = Instrument.setting(
        ":CURR %g",
        """ A floating point property that takes the measurement current in A
        """,
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
        """ A floating point property representing the measurement current in A
        """,
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

`get_process` can also be used to perform string processing. Let's say your instrument returns a value with its unit which has to be removed. This could be achieved by the following code:

.. testcode::

    Extreme5000.capacity = Instrument.measurement(
        ":CAP?",
        """ A measurement returning a capacity in nF in the format '<cap> nF'
        """,
        get_process=lambda v: float(v.replace('nF', ''))
    )

The same can be also achieved by the `preprocess_reply` keyword argument to :func:`Instrument.control <pymeasure.instruments.Instrument.control>` or :func:`Instrument.measurement <pymeasure.instruments.Instrument.measurement>`. This function is forwarded to :func:`Adapter.values <pymeasure.adapters.values>` and runs directly after receiving the reply from the device. One can therefore take advantage of the built in casting abilities and simplify the code accordingly:

.. testcode::

    Extreme5000.capacity = Instrument.measurement(
        ":CAP?",
        """ A measurement returning a capacity in nF in the format '<cap> nF'
        """,
        preprocess_reply=lambda v: v.replace('nF', '')
        # notice how we don't need to cast to float anymore
    )

The real purpose of `preprocess_reply` is, however, for instruments where many/all properties need similar reply processing. `preprocess_reply` can be applied to all :func:`Instrument.control <pymeasure.instruments.Instrument.control>` or :func:`Instrument.measurement <pymeasure.instruments.Instrument.measurement>` properties, for example if all quantities are returned with a unit as in the example above. To avoid running into troubles for other properties this `preprocess_reply` should be clever enough to skip the processing in case it is not appropriate, for example if some identification string is returned. Typically this can be achieved by regular expression matching. In case of no match the reply is returned unchanged:

.. testcode::

    import re
    _reg_value = re.compile(r"([-+]?[0-9]*\.?[0-9]+)\s+\w+")

    def extract_value(reply):
        """ extract numerical value from reply. If none can be found the reply
        is returned unchanged.

        :param reply: reply string
        :returns: string with only the numerical value
        """
        r = _reg_value.search(reply)
        if r:
            return r.groups()[0]
        else:
            return reply

    class Extreme5001(Instrument):
        """ Represents the imaginary Extreme 5001 instrument. This instrument
        sends numerical values including their units in an format "<value>
        <unit>".
        """
        capacity = Instrument.measurement(
            ":CAP?",
            """ A measurement returning a capacity in nF in the format '<cap> nF'
            """
        )

        voltage = Instrument.measurement(
            ":VOLT?",
            """ A measurement returning a voltage in V in the format '<volt> V'
            """
        )

        id = Instrument.measurement(
            "*idn?",
            """ The identification of the instrument.
            """
        )

        def __init__(self, resourceName, **kwargs):
            super().__init__(
                resourceName,
                "Extreme 5000",
                preprocess_reply=extract_value,
                **kwargs,
            )

In cases where the general `preprocess_reply` function should not run it can be also overwritten in the property definition:

.. testcode::

    Extreme5001.channel = Instrument.control(
        ":CHAN?", ":CHAN %d",
        """ A string property that controls the measurement channel,
        which can take the values X, Y, or Z.
        """,
        validator=strict_discrete_set,
        values=[1,2,3],
        preprocess_reply=lambda v: v,
    )

Using a combination of the decribed abilities also complex communication schemes can be achieved.
