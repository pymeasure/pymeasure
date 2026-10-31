.. module:: pymeasure.instruments.keysight.keysight34465a

###################
Keysight 34465A DMM
###################

This driver supports the Keysight 34465A Truevolt digital multimeter.
It does not claim support for other Truevolt models.
It uses the manufacturer-authored *Keysight Truevolt Series Operating and Service Guide*,
34460-90901 Edition 7, March 2020.

The constructor accepts a PyMeasure adapter or a VISA resource address and normal PyMeasure
instrument connection keyword arguments.
It does not reset or configure the instrument.

Quick start
===========

Configure DC voltage and take one immediate measurement:

.. code-block:: python

   from pymeasure.instruments.keysight import Keysight34465A

   dmm = Keysight34465A("USB0::0x2A8D::0x0101::SERIAL::INSTR", timeout=5000)
   try:
       dmm.configure("DCV", range_=10.0, nplc=1.0)
       reading = dmm.measure()
   finally:
       dmm.adapter.close()

Take an immediate group of N samples:

.. code-block:: python

   from pymeasure.instruments.keysight import Keysight34465A

   dmm = Keysight34465A("USB0::0x2A8D::0x0101::SERIAL::INSTR", timeout=60000)
   try:
       dmm.configure("DCV", nplc=0.02, autozero_enabled=False)
       readings = dmm.acquire(100)
   finally:
       dmm.adapter.close()

Arm a BUS-triggered acquisition, send its software trigger, and fetch the stored readings:

.. code-block:: python

   from pymeasure.instruments.keysight import Keysight34465A

   dmm = Keysight34465A("USB0::0x2A8D::0x0101::SERIAL::INSTR", timeout=5000)
   try:
       dmm.configure("DCV")
       dmm.arm(sample_count=10, trigger_count=1, trigger_delay=0.0)
       dmm.trigger()
       readings = dmm.fetch()
   finally:
       dmm.adapter.close()

The ``measure`` method returns one ``float``.
The ``acquire`` and ``fetch`` methods return ``list[float]``, including when the requested count
is one.
``fetch`` never starts or retriggers an acquisition.
It raises :class:`~pymeasure.instruments.keysight.keysight34465a.MeasurementError` for an empty,
malformed, or incomplete response.
A nonzero SCPI error-queue entry raises ``RuntimeError`` after the rejected command.
Transport and adapter timeout errors are propagated to the caller.

Functions and range settings
============================

Use ``configure`` with one of ``"DCV"``, ``"DCI"``, ``"RES"``, ``"FRES"``, ``"FREQ"``,
``"PER"``, ``"CONT"``, or ``"DIOD"``.
An optional ``range_`` selects a fixed range or ``"AUTO"`` where the function supports range
selection.
For frequency and period, ``range_`` is the AC input-voltage range in Volts, not a frequency or
period limit.
The ``frequency_input_voltage_range`` and ``frequency_input_voltage_autorange_enabled``
properties control that same shared frequency/period input-voltage range.

The ``voltage_range``, ``current_range``, and ``resistance_range`` properties select fixed ranges.
The corresponding ``*_autorange_enabled`` properties control autoranging.
The 10 A current range is selected with ``configure("DCI", range_=10.0)``; the direct
``current_range`` property covers the 3 A terminals.
Continuity and diode functions use their fixed measurement ranges and reject ``range_``.
Continuity readings are returned as resistance values; the driver does not assign a universal
pass threshold.
Overrange values such as ``9.9E37`` are preserved as returned by the instrument.

NPLC and options
================

The ``voltage_nplc``, ``current_nplc``, and ``resistance_nplc`` properties accept the base NPLC
values ``0.02``, ``0.06``, ``0.2``, ``1``, ``10``, and ``100``.
The ``configure`` method also accepts ``0.001``, ``0.002``, and ``0.006`` after it confirms the
optional DIG feature through ``*OPT?``.
The DIG option is also required by ``set_trigger_source("INT")``.
The ordinary trigger sources IMM, EXT, and BUS do not require DIG.
The constructor does not query or assume installed options.

Autozero properties are available for DC voltage, DC current, and resistance.
The resistance autozero property uses ``RES:ZERO:AUTO``; the manual says that this setting does
not change the always-on autozero behavior of 4-wire resistance measurements.

Acquisition limits and lifecycle
================================

``acquire`` requires an explicit positive integer count and accepts at most 50,000 samples.
This conservative helper limit matches the 34465A reading memory without the optional MEM
feature; the driver does not query or assume MEM is installed.
The hardware sample-count and finite trigger-count properties, and ``arm``, support the documented
integer range from 1 to 1e9.
The reading memory can hold 50,000 readings without MEM or 2,000,000 with MEM.
Using raw hardware counts beyond installed reading memory can overwrite older readings, as
described in the manual.

``arm`` always aborts the prior acquisition, selects BUS, sets sample and trigger counts and delay,
then sends INIT.
It does not send ``*TRG``.
Call ``trigger`` separately to send ``*TRG``, then call ``fetch`` to retrieve existing memory.
An omitted delay restores automatic trigger delay.
The manual documents an approximate trigger-delay range of 0 to 3600 seconds.

The inherited ``shutdown`` method does not close the connection.
Close the adapter explicitly with ``dmm.adapter.close()``, as in the examples.

The protocol tests verify software command exchange and reply handling.
They do not validate measurement accuracy or physical operation.

No-wire smoke validation (2026-10-27)
=====================================

A no-wire, open-input smoke run used the independently accepted driver revision
on a 34465A with firmware A.03.03-03.15-03.03-00.52-05-02.
It ran on Windows 11 with CPython 3.14.3 through PyVISA and the system VISA
backend.
The flow configured the 10 V DC voltage range at NPLC 1 and acquired a
BUS-triggered group of three readings plus one immediate scalar reading.
The instrument reported empty SCPI error queues before and after the flow, and
cleanup reported no errors.
The flow aborted the acquisition and restored the immediate trigger source with
one sample and one trigger.
Cleanup aborted the trigger system again and observed that restored state.
These finite open-input readings do not establish measurement accuracy,
calibration, external-load behavior, operation of other functions, or operation
on other models.
This result is a smoke test only for that driver revision, model, firmware, and
bounded flow.
Full upstream Sphinx HTML and doctest CI is revision-specific; consult the
`PR #1577 checks <https://github.com/pymeasure/pymeasure/pull/1577/checks>`_ for
the current revision.

API
===

.. autoclass:: Keysight34465A
   :members:
   :inherited-members:

.. autoclass:: pymeasure.instruments.keysight.keysight34465a.MeasurementError
