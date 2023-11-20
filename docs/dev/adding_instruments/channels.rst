.. _channels:

Instruments with channels
=========================


.. testsetup::

    # Behind the scene, replace Instrument with FakeInstrument to enable
    # doctesting simple usage cases (default doctest group)
    from pymeasure.instruments.fakes import FakeInstrument as Instrument

.. testsetup:: with-protocol-tests

    # If we want to run protocol tests on doctest code, we need to use a
    # separate doctest "group" and a different set of imports.
    # See https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html
    from pymeasure.instruments import Instrument, Channel
    from pymeasure.test import expected_protocol


Some instruments, like oscilloscopes and voltage sources, have channels whose commands differ only in the channel name.
For this case, we have :class:`~pymeasure.instruments.Channel`, which is similar to :class:`~pymeasure.instruments.Instrument` and its property factories, but does expect an :class:`~pymeasure.instruments.Instrument` instance (i.e., a parent instrument) instead of an :class:`~pymeasure.adapters.Adapter` as parameter.
All the channel communication is routed through the instrument's methods (`write`, `read`, etc.).
However, :meth:`Channel.insert_id <pymeasure.instruments.Channel.insert_id>` uses ``str.format`` to insert the channel's id at any occurrence of the class attribute :attr:`Channel.placeholder`, which defaults to :code:`"ch"`, in the written commands.
For example :code:`"Ch{ch}:VOLT?"` will be sent as :code:`"Ch3:VOLT?"` to the device, if the channel's id is "3".

Please add any created channel classes to the documentation. In the instrument's documentation file, you may add

.. code::

    .. autoclass:: pymeasure.instruments.MANUFACTURER.INSTRUMENT.CHANNEL
        :members:
        :show-inheritance:

`MANUFACTURER` is the folder name of the manufacturer and `INSTRUMENT` the file name of the instrument definition, which contains the `CHANNEL` class.
You may link in the instrument's docstring to the channel with :code:`:class:`CHANNEL``

To simplify and standardize the creation of channels in an ``Instrument`` class, there are two classes that can be used.
For instruments with fewer than 16 channels, :class:`~pymeasure.instruments.common_base.CommonBase.ChannelCreator` should be used
to explicitly declare each individual channel. For instruments with more than 16 channels, the
:class:`~pymeasure.instruments.common_base.CommonBase.MultiChannelCreator` can create multiple channels in a single declaration.

Adding a channel with :class:`~pymeasure.instruments.common_base.CommonBase.ChannelCreator`
*******************************************************************************************

For instruments with fewer than 16 channels the class :class:`~pymeasure.instruments.common_base.CommonBase.ChannelCreator` should be used to assign each channel interface to a class attribute.
:class:`~pymeasure.instruments.common_base.CommonBase.ChannelCreator` constructor accepts two parameters, the channel class for this channel interface, and the instrument's channel id for the channel interface.

In this example, we are defining a channel class and an instrument driver class. The ``VoltageChannel`` channel class will be used for controlling two channels in our ``ExtremeVoltage5000`` instrument.
In the ``ExtremeVoltage5000`` class we declare two class attributes with :class:`~pymeasure.instruments.common_base.CommonBase.ChannelCreator`, ``output_A`` and ``output_B``, which will become our channel interfaces.

.. testcode:: with-protocol-tests

    class VoltageChannel(Channel):
        """A channel of the voltage source."""

        voltage = Channel.control(
            "SOURce{ch}:VOLT?", "SOURce{ch}:VOLT %g",
            """Control the output voltage of this channel.""",
        )

    class ExtremeVoltage5000(Instrument):
        """An instrument with channels."""
        output_A = Instrument.ChannelCreator(VoltageChannel, "A")
        output_B = Instrument.ChannelCreator(VoltageChannel, "B")

.. testcode:: with-protocol-tests
    :hide:

    with expected_protocol(ExtremeVoltage5000,
        [("SOURceA:VOLT 1.25", None), ("SOURceB:VOLT?", "4.56")],
        name="Instrument with Channels",
    ) as inst:
        inst.output_A.voltage = 1.25
        assert inst.channels['B'].voltage == 4.56

At instrument class instantiation, the instrument class will create an instance of the channel class and assign it to the class attribute name.
Additionally the channels will be collected in a dictionary, by default named :code:`channels`.
We can access the channel interface through that class name:

.. code-block:: python

    extreme_inst = ExtremeVoltage5000('COM3')
    # Set channel A voltage
    extreme_inst.output_A.voltage = 50
    # Read channel B voltage
    chan_b_voltage = extreme_inst.output_B.voltage

.. testcode:: with-protocol-tests
    :hide:

    with expected_protocol(ExtremeVoltage5000,
        [("SOURceA:VOLT 50", None), ("SOURceB:VOLT?", "4.56")],
        name="Instrument with Channels",
    ) as inst:
        inst.output_A.voltage = 50
        assert inst.output_B.voltage == 4.56

Or we can access the channel interfaces through the :code:`channels` collection:

.. code-block:: python

    # Set channel A voltage
    extreme_inst.channels['A'].voltage = 50
    # Read channel B voltage
    chan_b_voltage = extreme_inst.channels['B'].voltage

.. testcode:: with-protocol-tests
    :hide:

    with expected_protocol(ExtremeVoltage5000,
        [("SOURceA:VOLT 50", None), ("SOURceB:VOLT?", "4.56")],
        name="Instrument with Channels",
    ) as inst:
        inst.channels['A'].voltage = 50
        assert inst.channels['B'].voltage == 4.56

Adding multiple channels with :class:`~pymeasure.instruments.common_base.CommonBase.MultiChannelCreator`
********************************************************************************************************

For instruments greater than 16 channels the class :class:`~pymeasure.instruments.common_base.CommonBase.MultiChannelCreator` can be used to easily generate a list of channels from one class attribute declaration.

The :class:`~pymeasure.instruments.common_base.CommonBase.MultiChannelCreator` constructor accepts a single channel class or list of channel classes, and a list of corresponding channel ids. Instead of lists, you may also use tuples.
If you give a single class and a list of ids, all channels will be of the same class.

At instrument instantiation, the instrument will generate channel interfaces as class attribute names composing of the prefix (default :code:`"ch_"`) and channel id, e.g. the channel with id "A" will be added as attribute :code:`ch_A`.
While :class:`~pymeasure.instruments.common_base.CommonBase.ChannelCreator` creates a channel interface for each class attribute, :class:`~pymeasure.instruments.common_base.CommonBase.MultiChannelCreator` creates a channel collection for the assigned class attribute.
It is recommended you use the class attribute name ``channels`` to keep the codebase homogenous.

To modify our example, we will use :class:`~pymeasure.instruments.common_base.CommonBase.MultiChannelCreator` to generate 24 channels of the ``VoltageChannel`` class.

.. testcode:: with-protocol-tests

    class VoltageChannel(Channel):
        """A channel of the voltage source."""

        voltage = Channel.control(
            "SOURce{ch}:VOLT?", "SOURce{ch}:VOLT %g",
            """Control the output voltage of this channel.""",
        )

    class MultiExtremeVoltage5000(Instrument):
        """An instrument with channels."""
        channels = Instrument.MultiChannelCreator(VoltageChannel, list(range(1,25)))


.. testcode:: with-protocol-tests
    :hide:

    with expected_protocol(MultiExtremeVoltage5000,
        [("SOURce5:VOLT 1.23", None), ("SOURce16:VOLT?", "4.56")],
        name="Instrument with Channels",
    ) as inst:
        inst.ch_5.voltage = 1.23
        assert inst.channels[16].voltage == 4.56

We can now access the channel interfaces through the generated class attributes:

.. code-block:: python

    extreme_inst = MultiExtremeVoltage5000('COM3')
    # Set channel 5 voltage
    extreme_inst.ch_5.voltage = 50
    # Read channel 16 voltage
    chan_16_voltage = extreme_inst.ch_16.voltage

.. testcode:: with-protocol-tests
    :hide:

    with expected_protocol(MultiExtremeVoltage5000,
        [("SOURce5:VOLT 50", None), ("SOURce16:VOLT?", "4.56")],
        name="Instrument with Channels",
    ) as inst:
        inst.ch_5.voltage = 50
        assert inst.ch_16.voltage == 4.56

Because we use `channels` as the class attribute for ``MultiChannelCreator``, we can access the channel interfaces through the :code:`channels` collection:

.. code-block:: python

    # Set channel 10 voltage
    extreme_inst.channels[10].voltage = 50
    # Read channel 22 voltage
    chan_b_voltage = extreme_inst.channels[22].voltage

.. testcode:: with-protocol-tests
    :hide:

    with expected_protocol(MultiExtremeVoltage5000,
        [("SOURce10:VOLT 50", None), ("SOURce22:VOLT?", "4.56")],
        name="Instrument with Channels",
    ) as inst:
        inst.channels[10].voltage = 50
        assert inst.channels[22].voltage == 4.56

Advanced channel management
***************************

Adding / removing channels
--------------------------

In order to add or remove programmatically channels, use the parent's :meth:`~pymeasure.instruments.common_base.CommonBase.add_child`, :meth:`~pymeasure.instruments.common_base.CommonBase.remove_child` methods.

Channels with fixed prefix
--------------------------

If all channel communication is prefixed by a specific command, e.g. :code:`"SOURceA:"` for channel A, you can override the channel's :meth:`insert_id` method.
That is especially useful, if you have only one channel of that type, e.g. because it defines one function of the instrument vs. another one.

.. testcode:: with-protocol-tests

    class VoltageChannelPrefix(Channel):
        """A channel of a voltage source, every command has the same prefix."""

        def insert_id(self, command):
            return f"SOURce{self.id}:{command}"

        voltage = Channel.control(
            "VOLT?", "VOLT %g",
            """Control the output voltage of this channel.""",
        )

.. testcode:: with-protocol-tests
    :hide:

    class InstrumentWithChannelsPrefix(Instrument):
        """An instrument with a channel, just for the test."""
        ch_A = Instrument.ChannelCreator(VoltageChannelPrefix, "A")

    with expected_protocol(InstrumentWithChannelsPrefix,
        [("SOURceA:VOLT 1.23", None), ("SOURceA:VOLT?", "1.23")],
        name="Test",
    ) as inst:
        inst.ch_A.voltage = 1.23
        assert inst.ch_A.voltage == 1.23

This channel class implements the same communication as the previous example, but implements the channel prefix in the :meth:`insert_id` method and not in the individual property (created by :meth:`control`).

Collections of different channel types
--------------------------------------

Some devices have different types of channels. In this case, you can specify a different ``collection`` and ``prefix`` parameter.

.. testcode:: with-protocol-tests

    class PowerChannel(Channel):
        """A channel controlling the power."""
        power = Channel.measurement(
            "POWER?", """Measure the currently consumed power.""")

    class MultiChannelTypeInstrument(Instrument):
        """An instrument with two different channel types."""
        analog = Instrument.MultiChannelCreator(
            (VoltageChannel, VoltageChannelPrefix),
            ("A", "B"),
            prefix="an_")
        digital = Instrument.MultiChannelCreator(VoltageChannel, (0, 1, 2), prefix="di_")
        power = Instrument.ChannelCreator(PowerChannel)


.. testcode:: with-protocol-tests
    :hide:

    with expected_protocol(MultiChannelTypeInstrument,
        [("SOURceB:VOLT 1.23", None), ("SOURce2:VOLT?", "4.56")],
        name="MultiChannelTypeInstrument",
    ) as inst:
        inst.an_B.voltage = 1.23
        assert inst.di_2.voltage == 4.56

This instrument has two collections of channels and one single channel.
The first collection in the dictionary :code:`analog` contains an instance of :class:`VoltageChannel` with the name :code:`an_A` and an instance of :class:`VoltageChannelPrefix` with the name :code:`an_B`.
The second collection contains three channels of type :class:`VoltageChannel` with the names :code:`di_0, di_1, di_2` in the dictionary :code:`digital`.
You can address the first channel of the second group either with :code:`inst.di_0` or with :code:`inst.digital[0]`.
Finally, the instrument has a single channel with the name :code:`power`, as it does not have a prefix.

If you have a single channel category, do not change the default parameters of :class:`~pymeasure.instruments.common_base.CommonBase.ChannelCreator` or :meth:`~pymeasure.instruments.common_base.CommonBase.add_child`, in order to keep the code base homogeneous.
We expect the default behaviour to be sufficient for most use cases.
