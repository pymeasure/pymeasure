.. _channels:

Instruments with channels
=========================

Some instruments, like oscilloscopes and voltage sources, have channels whose commands differ only in the channel name.
For this case, we have :class:`~pymeasure.instruments.Channel`, which is similar to :class:`~pymeasure.instruments.Instrument` and its property factories, but does expect an :class:`~pymeasure.instruments.Instrument` instance (i.e., a parent instrument) instead of an :class:`~pymeasure.adapters.Adapter` as parameter.
All the channel communication is routed through the instrument's methods (`write`, `read`, etc.).
However, :meth:`Channel.insert_id <pymeasure.instruments.Channel.insert_id>` uses `str.format` to insert the channel's id at any occurence of the class attribute :attr:`Channel.placeholder`, which defaults to :code:`"ch"`, in the written commands.
For example :code:`"Ch{ch}:VOLT?"` will be sent as :code:`"Ch3:VOLT?"` to the device, if the channel's id is "3".

In order to add a channel to an instrument or to another channel (nesting channels is possible), create the channels with the class :class:`~pymeasure.instruments.common_base.CommonBase.ChannelCreator` as class attributes.
Its constructor accepts a single channel class or list of classes and a list of corresponding ids.
Instead of lists, you may also use tuples.
If you give a single class and a list of ids, all channels will be of the same class.

At instrument instantiation, the instrument will add the channels accordingly with the attribute names as a composition of the prefix (default :code:`"ch_"`) and channel id, e.g. the channel with id "A" will be added as attribute :code:`ch_A`.
Additionally, the channels will be collected in a dictionary with the same name as you used for the `ChannelCreator`.
Without pressing reasons, call the dictionary :code:`channels` and do not change the default prefix in order to keep the code base homogeneous.

In order to add or remove programatically channels, use the parent's :meth:`~pymeasure.instruments.common_base.CommonBase.add_child`, :meth:`~pymeasure.instruments.common_base.CommonBase.remove_child` methods.

.. testcode:: with-protocol-tests

    class VoltageChannel(Channel):
        """A channel of the voltage source."""

        voltage = Channel.control(
            "SOURce{ch}:VOLT?", "SOURce{ch}:VOLT %g",
            """Control the output voltage of this channel.""",
        )

    class InstrumentWithChannels(Instrument):
        """An instrument with channels."""
        channels = Instrument.ChannelCreator(VoltageChannel, ("A", "B"))

.. testcode:: with-protocol-tests
    :hide:

    with expected_protocol(InstrumentWithChannels,
        [("SOURceA:VOLT 1.23", None), ("SOURceB:VOLT?", "4.56")],
        name="Instrument with Channels",
    ) as inst:
        inst.ch_A.voltage = 1.23
        assert inst.ch_B.voltage == 4.56

If you set the voltage of the first channel of above :class:`ExtremeChannel` instrument with :code:`inst.chA.voltage = 1.23`, the driver sends :code:`"SOURceA:VOLT 1.23"` to the device, supplying the "A" of the channel name.
The same channel could be addressed with :code:`inst.channels["A"].voltage = 1.23` as well.


Channels with fixed prefix
**************************

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
        channels = Instrument.ChannelCreator(VoltageChannelPrefix, "A")

    with expected_protocol(InstrumentWithChannelsPrefix,
        [("SOURceA:VOLT 1.23", None), ("SOURceA:VOLT?", "1.23")],
        name="Test",
    ) as inst:
        inst.ch_A.voltage = 1.23
        assert inst.ch_A.voltage == 1.23

This channel class implements the same communication as the previous example, but implements the channel prefix in the :meth:`insert_id` method and not in the individual property (created by :meth:`control`).


Collections of different channel types
**************************************

Some devices have different types of channels. In this case, you can specify a different `collection` and `prefix` parameter.

.. testcode:: with-protocol-tests

    class PowerChannel(Channel):
        """A channel controlling the power."""

        power = Channel.measurement(
            "POWER?", """Measure the currently consumed power.""")

    class MultiChannelTypeInstrument(Instrument):
        """An instrument with two different channel types."""
        analog = Instrument.ChannelCreator(
            (VoltageChannel, VoltageChannelPrefix),
            ("A", "B"),
            prefix="an_")
        digital = Instrument.ChannelCreator(VoltageChannel, (0, 1, 2), prefix="di_")
        power = Instrument.ChannelCreator(PowerChannel, prefix=None)


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
