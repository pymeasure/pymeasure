##################################
Rigol MSO5000 Series Oscilloscopes
##################################

The :class:`~pymeasure.instruments.rigol.MSO5000` driver supports the
MSO5072, MSO5074, MSO5102, MSO5104, MSO5204, and MSO5354 models.
It exposes analog channels, acquisition and timebase settings, common trigger
modes, waveform transfer, and selected system and storage functions.

Connection
==========

Connect with any VISA resource supported by the oscilloscope.
For example:

.. code-block:: python

    from pymeasure.instruments.rigol import MSO5000

    scope = MSO5000("TCPIP::192.0.2.1::INSTR")
    try:
        print(scope.id)
        print(scope.ch_1.scale)
        print(scope.sample_rate)
    finally:
        scope.shutdown()

Waveform transfer
=================

Configure the waveform source, mode, format, and point range before calling
:meth:`~pymeasure.instruments.rigol.MSO5000.waveform_data`.
BYTE and WORD transfers return unsigned sample codes and require the preamble
values to convert them to physical units.
ASC transfers return physical values directly.

.. code-block:: python

    import numpy as np

    scope.waveform_source = "CHAN1"
    scope.waveform_mode = "NORM"
    scope.waveform_format = "BYTE"
    scope.waveform_start = 1
    scope.waveform_stop = 1000

    preamble = scope.get_waveform_preamble()
    samples = scope.waveform_data()
    voltage = (
        samples.astype(float)
        - preamble["y_origin"]
        - preamble["y_reference"]
    ) * preamble["y_increment"]
    time = (
        np.arange(samples.size) - preamble["x_reference"]
    ) * preamble["x_increment"] + preamble["x_origin"]

Some firmware versions return malformed WORD blocks.
In that case, use BYTE or ASC format as indicated by the raised error.

API reference
=============

.. autoclass:: pymeasure.instruments.rigol.MSO5000
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.MSO5000Channel
    :members:
    :show-inheritance:
