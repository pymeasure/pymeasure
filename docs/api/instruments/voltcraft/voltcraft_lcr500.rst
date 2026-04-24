##########################
Voltcraft LCR500 LCR-Meter
##########################

.. warning::

    This instrument uses different write and read terminators. The write and read terminators are each ``\n``. A mismatch can lead to communication issues when sending commands, as responses may not be properly terminated or recognized. If a custom adapter is used, ensure that these are set correctly.

.. autoclass:: pymeasure.instruments.voltcraft.voltcraft_lcr500.LCR500
    :members:
    :show-inheritance:
