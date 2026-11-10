######################################
Rigol DG800 Series Waveform Generators
######################################

The :class:`~pymeasure.instruments.rigol.DG800` driver supports the
DG811, DG812, DG821, DG822, DG831, and DG832 models.
It exposes voltage channels, and selected system and storage functions.

Connection
==========

Connect with any VISA resource supported by the oscilloscope.
For example:

.. code-block:: python

    from pymeasure.instruments.rigol import DG800

    fgen=DG800('USB0::0x1AB1::0x643::DG8A221200686::INSTR')
 
    try:
        print(fgen.id)
        print(fgen.channel_1.waveform)
        print(fgen.load)
    finally:
        fgen.shutdown()

API reference
=============

.. autoclass:: pymeasure.instruments.rigol.DG800
    :members:
    :show-inheritance:
.. autoclass:: pymeasure.instruments.rigol.rigol_dg800.VoltageChannel
    :members:
    :show-inheritance:
