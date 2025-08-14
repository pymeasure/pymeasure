############################################
Thurlby 1905a intelligent digital multimeter
############################################
.. currentmodule:: pymeasure.instruments.tti.thurlby1905a

.. contents::

**********************************************
General Information
**********************************************
This instrument only provides measurement output via an RS-232 serial port.
The serial port can only be read from, not written to.

Earlier models had a Baud rate of 2400, later ones 9600.

Initialization of the Instrument
====================================

.. code-block:: python

    from pymeasure.instruments.tti import Thurlby1905a

    dmm = Thurlby1905a("ASRL/dev/ttyS0::INSTR")
    output = dmm.read_measurement
