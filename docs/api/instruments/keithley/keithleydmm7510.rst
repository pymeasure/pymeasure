###########################
Keithley DMM7510 Multimeter
###########################

The :class:`~pymeasure.instruments.keithley.KeithleyDMM7510` driver uses the
DMM7510 native SCPI command set.
The instrument must already be in SCPI mode before it is connected.
The constructor does not query, reset, configure, or change the command set.

The independently accepted driver revision used in the 2026-10-27 smoke run
below decodes only complete supported ``:SENS:FUNC?`` replies in its
``function`` getter.
``VOLT`` and ``VOLT:DC`` map to ``DCV``; ``CURR`` and ``CURR:DC`` map to
``DCI``; ``FREQ`` and ``FREQ:VOLT`` map to ``FREQ``; and ``PER`` and
``PER:VOLT`` map to ``PER``.
``RES``, ``FRES``, ``CONT``, and ``DIOD`` map to the same-named functions.
An unsupported or truncated reply raises ``DMM7510MeasurementError`` instead of
accepting an arbitrary function prefix.
Other revisions are outside that validated scope.

.. autoclass:: pymeasure.instruments.keithley.KeithleyDMM7510
    :members:
    :show-inheritance:
    :exclude-members: ask, clear, control, measurement, read, setting, values, write

.. autoclass:: pymeasure.instruments.keithley.DMM7510MeasurementError

.. autoclass:: pymeasure.instruments.keithley.DMM7510SCPIError

Configuration
=============

Use :meth:`~pymeasure.instruments.keithley.KeithleyDMM7510.configure` with
``DCV``, ``DCI``, ``RES``, ``FRES``, ``FREQ``, ``PER``, ``CONT``, or ``DIOD``.
``CONT`` returns a numeric resistance reading and ``DIOD`` returns a numeric
voltage reading.
The driver does not apply a boolean continuity threshold.

The ``voltage_range``, ``current_range``, ``resistance_range``, and
``four_wire_resistance_range`` properties take expected magnitudes in V, A, or Ω.
The DMM7510 selects the next sufficient fixed range, so read-back can differ
from the requested magnitude.
Their corresponding autorange properties are ``voltage_autorange``,
``current_autorange``, ``resistance_autorange``, and
``four_wire_resistance_autorange``.
The frequency and period threshold autorange properties are
``frequency_threshold_autorange`` and ``period_threshold_autorange``.

For ``FREQ`` and ``PER``, ``range_`` and the
``frequency_threshold_range`` and ``period_threshold_range`` properties specify
the expected input voltage from 0.1 V to 700 V.
They do not specify frequency or period.

``voltage_nplc``, ``current_nplc``, ``resistance_nplc``, and
``four_wire_resistance_nplc`` use power-line cycles from 0.0005 to 12 at 50 Hz
or 0.0005 to 15 at 60 Hz.
Values above 12 first query ``SYST:LFR?`` and are accepted only when the reply
identifies 60 Hz.
``voltage_autozero_enabled``, ``current_autozero_enabled``,
``resistance_autozero_enabled``, and ``four_wire_resistance_autozero_enabled``
control automatic reference updates for their named functions.
``configure(..., autozero="ONCE")`` performs a one-shot update and synchronizes
it before applying NPLC.
Fetch or abort a pending acquisition before changing the measurement function.

``four_wire_offset_compensation`` accepts ``OFF``, ``ON``, or ``AUTO``.
``ON`` is limited to ranges through 100 kΩ.
``dry_circuit_enabled`` is available from 1 Ω through 10 kΩ and enables offset
compensation on the instrument.

``terminal_selection`` is read-only because changing terminals requires the
front-panel TERMINALS button.
The 10 A current range requires REAR terminals; FRONT terminals support at most
3 A.
With REAR terminals, current autoranging still tops out at 3 A.
``reading_buffer_count`` and ``reading_buffer_capacity`` report the current
defbuffer1 values without assuming its capacity.
``reading_count`` controls ``SENS:COUN`` and is limited by the current buffer
capacity.
``display_brightness`` accepts ``ON100``, ``ON75``, ``ON50``, ``ON25``, ``OFF``,
and ``BLACKOUT``.

Single and grouped readings
===========================

``measure()`` returns one float.
``acquire(count, timeout=...)`` returns a list, including a one-element list
when ``count`` is 1.
Counts are positive integer samples, limited to 1,000,000 and the instrument's
queried defbuffer1 capacity.
The timeout is in seconds.
Each helper aborts any prior trigger model, disables a previous command
stimulus, selects and clears defbuffer1, and replaces its acquisition settings.
All requested samples are read from the buffer; partial and excess data raise
``DMM7510MeasurementError``.

.. code-block:: python

    from pymeasure.instruments.keithley import KeithleyDMM7510

    meter = KeithleyDMM7510("TCPIP::instrument-host::inst0::INSTR")
    try:
        meter.configure("DCV", range_=10.0, nplc=1.0)
        one_reading = meter.measure()
        group = meter.acquire(8, timeout=5.0)
    finally:
        meter.adapter.close()

SimpleLoop acquisition
======================

``initiate(count, delay=...)`` configures the documented SimpleLoop trigger
model and starts it.
The SimpleLoop count is separate from ``SENS:COUN``; the driver sets one sample
per loop iteration.
Delay is in seconds and must be zero or between 167 ns and 10,000 s.
``fetch(timeout=...)`` waits for the trigger model to reach IDLE and returns the
full list.
It never sends ``INIT`` or ``*TRG``.
Calling ``fetch`` without a pending acquisition raises
``DMM7510MeasurementError`` instead of returning old readings.

.. code-block:: python

    from pymeasure.instruments.keithley import KeithleyDMM7510

    meter = KeithleyDMM7510("TCPIP::instrument-host::inst0::INSTR")
    try:
        meter.configure("DCV")
        meter.initiate(100, delay=0.001)
        samples = meter.fetch(timeout=10.0)
    finally:
        meter.adapter.close()

Command-triggered burst
=======================

``arm(count)`` prepares one command-triggered burst by setting
``DISP:BUFF:ACT``, ``SENS:COUN``, and the ``COMM`` measurement stimulus.
Call ``trigger()`` once for that burst, then call ``fetch(timeout=...)``.
The DMM7510 can latch an additional burst if it receives a second trigger while
the first group is running.
``fetch`` never triggers an acquisition.

.. code-block:: python

    from pymeasure.instruments.keithley import KeithleyDMM7510

    meter = KeithleyDMM7510("TCPIP::instrument-host::inst0::INSTR")
    try:
        meter.configure("DCV")
        meter.arm(4)
        meter.trigger()
        triggered_samples = meter.fetch(timeout=10.0)
    finally:
        meter.adapter.close()

Acquisition helpers own the contents and settings of defbuffer1 while they run.
They do not coordinate with other sessions or unsolicited triggers.
Call ``clear_buffer()`` to abort pending work and explicitly clear defbuffer1.

Timing and validation notes
===========================

The 0.2 s delay after an NPLC write and the autozero-before-NPLC ordering are
inherited device and firmware-specific workarounds from earlier JLDevKit DMM7510 use.
The smoke run below does not independently validate these timing assumptions.

On 2026-10-27, a no-wire, open-input smoke run used that driver revision on a
DMM7510 with firmware 1.7.7b.
It ran on Windows 11 with CPython 3.14.3 through PyVISA and the system VISA
backend.
The flow used FRONT terminals and configured the 10 V DC voltage range at NPLC 1.
It acquired a command-triggered group of three readings and one immediate
scalar reading.
The instrument reported empty SCPI error queues before and after the flow, and
cleanup reported no errors.
The acquisition was aborted after the run.
Finite open-input readings do not establish measurement accuracy, calibration,
external-load behavior, DCI or resistance operation, or operation on other
models.
This result is a smoke test only for that driver revision, model, firmware, and
bounded flow; full upstream Sphinx HTML and doctest CI has not run on the new
PR head and remains pending.
