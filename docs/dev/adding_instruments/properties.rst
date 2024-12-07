.. _properties:

Writing properties
==================

In PyMeasure, `Python properties`_ are the preferred method for dealing with variables that are read or set.


.. testsetup::

    # Behind the scene, replace Instrument with FakeInstrument to enable
    # doctesting simple usage cases (default doctest group)
    from pymeasure.instruments.fakes import FakeInstrument as Instrument
    class Extreme5000(Instrument):
        def __init__(self, adapter, name="Test", **kwargs):
            super().__init__(adapter, name, **kwargs)


The property factories
**********************
PyMeasure comes with three central convenience factory functions for making properties for classes: :func:`CommonBase.control <pymeasure.instruments.common_base.CommonBase.control>`, :func:`CommonBase.measurement <pymeasure.instruments.common_base.CommonBase.measurement>`, and :func:`CommonBase.setting <pymeasure.instruments.common_base.CommonBase.setting>`.
You can call them, however, as :code:`Instrument.control`, :code:`Instrument.measurement`, and :code:`Instrument.setting`.

The :func:`Instrument.measurement <pymeasure.instruments.common_base.CommonBase.measurement>` function returns a property that can only read values from an instrument.
For example, if our "Extreme 5000" has the :code:`:TEMP?` command, we can write the following property to be added after the :code:`def __init__` line in our above example class, or added to the class after the fact as in the code here:

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

The :func:`Instrument.control <pymeasure.instruments.common_base.CommonBase.control>` function extends this behavior by creating a property that you can read and set. For example, if our "Extreme 5000" has the :code:`:VOLT?` and :code:`:VOLT <float>` commands that are in Volts, we can write the following property.

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

Finally, the :func:`Instrument.setting <pymeasure.instruments.common_base.CommonBase.setting>` function can only set, but not read values.

Using the :func:`Instrument.control <pymeasure.instruments.common_base.CommonBase.control>`, :func:`Instrument.measurement <pymeasure.instruments.common_base.CommonBase.measurement>`, and :func:`Instrument.control <pymeasure.instruments.common_base.CommonBase.control>` functions, you can create a number of properties for basic measurements and controls.

The next sections detail additional features of the property factories.
These allow you to write properties that cover specific ranges, or that have to map between a real value to one used in the command. Furthermore it is shown how to perform more complex processing of return values from your device.

.. _validators:

Restricting values with validators
**********************************
Many GPIB/SCPI commands are more restrictive than our basic examples above. The :func:`Instrument.control <pymeasure.instruments.common_base.CommonBase.control>` function has the ability to encode these restrictions using :mod:`validators <pymeasure.instruments.validators>`. A validator is a function that takes a value and a set of values, and returns a valid value or raises an exception. There are a number of pre-defined validators in :mod:`pymeasure.instruments.validators` that should cover most situations. We will cover the four basic types here.

In the examples below we assume you have imported the validators.

.. testcode::
    :hide:

    from pymeasure.instruments.validators import strict_discrete_set, strict_range, truncated_range, truncated_discrete_set

In many situations you will also need to process the return string in order to extract the wanted quantity or process a value before sending it to the device. The :func:`Instrument.control <pymeasure.instruments.common_base.CommonBase.control>`, :func:`Instrument.measurement <pymeasure.instruments.common_base.CommonBase.measurement>` and :func:`Instrument.setting <pymeasure.instruments.common_base.CommonBase.setting>` function also provide means to achieve this.

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

Now that you are familiar with the validators, you can additionally use maps to satisfy instruments which require non-physical values. The :code:`map_values` argument of :func:`Instrument.control <pymeasure.instruments.common_base.CommonBase.control>` enables this feature.

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

As you have seen, the :func:`Instrument.control <pymeasure.instruments.common_base.CommonBase.control>` function can be significantly extended by using validators and maps.

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

The :func:`Instrument.control <pymeasure.instruments.common_base.CommonBase.control>`, and :func:`Instrument.setting <pymeasure.instruments.common_base.CommonBase.setting>` allow a keyword argument `set_process` which must be a function that takes a value after validation and performs processing before value mapping. This function must return the processed value. This can be typically used for unit conversions as in the following example:


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

Similar to `set_process` the :func:`Instrument.control <pymeasure.instruments.common_base.CommonBase.control>`, and :func:`Instrument.measurement <pymeasure.instruments.common_base.CommonBase.measurement>` functions allow a `get_process` argument which if specified must be a function that takes a value and performs processing before value mapping. The function must return the processed value. In analogy to the example above this can be used for example for unit conversion:

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

The same can be also achieved by the `preprocess_reply` keyword argument to :func:`Instrument.control <pymeasure.instruments.common_base.CommonBase.control>` or :func:`Instrument.measurement <pymeasure.instruments.common_base.CommonBase.measurement>`. This function is forwarded to :func:`Adapter.values <pymeasure.adapters.values>` and runs directly after receiving the reply from the device. One can therefore take advantage of the built in casting abilities and simplify the code accordingly:

.. testcode::

    Extreme5000.capacity = Instrument.measurement(
        ":CAP?",
        """Measure the capacity in nF (float).""",
        preprocess_reply=lambda v: v.replace('nF', '')
        # notice how we don't need to cast to float anymore
    )

Checking the instrument for errors
**********************************
If you need to separately ask your instrument about its error state after getting/setting, use the parameters :code:`check_get_errors` and :code:`check_set_errors` of :meth:`~pymeasure.instruments.common_base.CommonBase.control`, respectively.
If those are enabled, the methods :meth:`~pymeasure.instruments.Instrument.check_get_errors` and :meth:`~pymeasure.instruments.Instrument.check_set_errors`, respectively, will be called be called after device communication has concluded.
In the default implementation, for simplicity both methods call :meth:`~pymeasure.instruments.Instrument.check_errors`.
To read the automatic response of instruments that respond to every set command with an acknowledgment or error, override :meth:`~pymeasure.instruments.Instrument.check_set_errors` as needed.


Using multiple values
*********************
Seldomly, you might need to send/receive multiple values in one command.
The :func:`Instrument.control <pymeasure.instruments.common_base.CommonBase.control>` function can be used with multiple values at one time, passed as a tuple. Say, we may set voltages and frequencies in our "Extreme 5000", and the commands for this are :code:`:VOLTFREQ?` and :code:`:VOLTFREQ <float>,<float>`, we could use the following property:

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
This feature allows accommodating some interesting use cases with a very compact syntax.

Dynamic features of a property are enabled by setting its :code:`dynamic` parameter to :code:`True`.

Afterwards, creating specifically-named attributes (either in class definitions or on instances) allows modifying the parameters used at the time of property definition.
You need to define an attribute whose name is `<property name>_<property_parameter>` and assign to it the desired value.
Pay attention *not* to inadvertently define other class attribute or instance attribute names matching this pattern, since they could unintentionally modify the property behaviour.

.. note::
   To clearly distinguish these special attributes from normal class/instance attributes, they can only be set, not read. 

The mechanism works for all the parameters in properties, except :code:`dynamic` and :code:`docs` -- see :func:`Instrument.control <pymeasure.instruments.common_base.CommonBase.control>`, :func:`Instrument.measurement <pymeasure.instruments.common_base.CommonBase.measurement>`, :func:`Instrument.setting <pymeasure.instruments.common_base.CommonBase.setting>`.

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
