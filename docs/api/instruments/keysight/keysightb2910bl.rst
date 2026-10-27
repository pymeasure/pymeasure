###############
KeysightB2910BL
###############

This driver supports channel 1 of the Keysight B2910BL only.
It does not claim support for other B2900 models.

The initial property-command implementation reuses the MIT-licensed source from
`PyMeasure PR #1254 <https://github.com/pymeasure/pymeasure/pull/1254>`_, head
``c639b61f0deeaa52055bb5ffa665167ccaec025f``.
That pull request is open and unmerged, so it is not released upstream support.
This driver adds a B2910BL-specific channel API, deterministic fixed DC setup,
paired readings, host-stepped scans, and B2910BL envelope checks.

The driver is based on the Keysight
`B2900B/BL SCPI Command Reference, Edition 2
<https://www.keysight.com/pr/en/assets/9921-01285/programming-guides/B2900B-BL-Series-Precision-Source-Measure-Unit-SCPI-Command-Reference.pdf>`_.
The voltage and current output envelope follows Figure 2-6 on page 73.
The source ranges follow Tables 2-5 and 2-8 on pages 69 and 71.
The B2910BL sense ranges follow Tables 2-9 and 2-10 on page 74.

Install and use the driver through the normal PyMeasure instrument package::

    from pymeasure.instruments.keysight import KeysightB2910BL

    smu = KeysightB2910BL("TCPIP0::192.0.2.10::inst0::INSTR")
    try:
        smu.ch1.configure_voltage(1.0, current_limit=0.01)
        smu.ch1.output_enabled = True
        reading = smu.ch1.read_point()
        print(reading.voltage_V, reading.current_A, reading.compliance)
    finally:
        try:
            smu.ch1.output_enabled = False
        finally:
            smu.adapter.close()

Construction performs no ID, reset, output, language, or discovery commands.
The adapter remains open until the caller closes ``smu.adapter``.

Constant voltage and current
============================

``configure_voltage`` and ``configure_current`` validate every argument before
writing, abort old activity, request output off, select a fixed DC source, and
set both voltage and current sensing.
They set compliance, the measurement ranges, and a shared NPLC integration time.
They disable automatic output-on and output-off, then set single arm and trigger
counts with AINT sources.
Configuration does not enable output.
Enable it explicitly when a constant source is wanted.

The independently accepted driver revision used in the 2026-10-27 smoke run
below enables both source autoranges before writing the immediate and triggered
source levels in either source mode.
This ordering lets the instrument select source ranges before applying the
requested level.
Other revisions are outside that validated scope.

The current-source setup uses the voltage compliance limit instead::

    try:
        smu.ch1.configure_current(0.01, voltage_limit=5.0)
        smu.ch1.output_enabled = True
        reading = smu.ch1.read_point()
    finally:
        try:
            smu.ch1.output_enabled = False
        finally:
            smu.adapter.close()

Always place caller-owned output control in a ``finally`` block and close the
adapter when finished.

The convenience API accepts NPLC from 0.01 to 100 PLC.
This is the conservative range shared by 50 Hz and 60 Hz operation.
The native instrument limits are 0.0004 to 100 PLC at 50 Hz and 0.00048 to 120
PLC at 60 Hz.
The raw ``nplc`` property accepts those combined native bounds and checks the
selected line frequency before setting a value.
Setting it disables automatic aperture and automatic NPLC first.
NPLC is common to voltage and current sensing, so the setup disables both
automatic aperture and automatic NPLC before applying fixed NPLC.

The native source ranges are 0.2, 2, 20, and 200 V, and 10 nA, 100 nA, 1 uA,
10 uA, 100 uA, 1 mA, 10 mA, 100 mA, 1 A, and 1.5 A.
The B2910BL voltage measurement ranges are 0.2, 2, 20, and 200 V.
Its DC current measurement ranges are 10 nA through 1.5 A using the ranges
listed above.
No 3 A or 10 A sense range is exposed.

The DC envelope allows up to 1.515 A for voltage magnitudes through 21 V.
Above 21 V and through 210 V, it allows up to 0.105 A.
The envelope is symmetric for positive and negative values.
The driver rejects setpoint and compliance combinations outside this envelope.
It does not infer a 315 W rating from 210 V and 1.5 A.

Before commands that allow more than 42 V, including current-source voltage
compliance, the driver requires ``SYST:INT:TRIP?`` to report a closed interlock.
This software query does not verify physical interlock operation.
Setting ``output_enabled`` requests the instrument output switch state.
It does not confirm that a physical voltage is present.

Paired measurements and scans
=============================

Before each ``read_point``, the driver aborts stale activity, selects fixed DC
source operation, enables voltage and current sensing, and selects one AINT
acquisition.
It disables automatic output-on and output-off so the read does not silently
change the caller's output state.
It matches the triggered source level to the current immediate source setting
without changing that immediate setpoint.
``read_point`` fixes ASCII output and requests voltage, current, and source data
in one ``READ? (@1)`` acquisition.
The manual fixes the response order as voltage, current, resistance, time, status,
then source, regardless of the order in the format command.
The returned ``voltage_V`` and ``current_A`` are from that acquisition.
``source_setting`` is the instrument-reported programmed source setting, not a
measured voltage or current.
``compliance`` comes from the active source function's documented protection
trip query.
No compliance state is inferred from measurement values or status bits.

Malformed, non-finite, empty, or incorrectly sized ASCII responses raise an
exception.
The ``+9.91e37`` missing-reading sentinel raises ``ValueError``.
The documented ``+9.90e37`` and ``-9.90e37`` infinity sentinels raise
``OverflowError``.
These are not returned as physical measurements, and an overload value is not
treated as a compliance indication.

``sweep_voltage`` and ``sweep_current`` run host-stepped scans.
They preserve input order, including descending, cross-zero, repeated, and
single-point sequences.
They validate the full finite iterable, its envelope, and all options before
the first write, and reject more than 100,000 points.
The host applies each setpoint, waits for the optional ``settle`` delay, and
reads one paired point.
This is not a deterministic hardware-timed sweep.
The native output protection setting is inherited from the instrument and is
not disabled or automatically re-enabled by a scan.
The instrument can turn output off when compliance is reached (SCPI reference,
Edition 2, page 220).
Before each point and after each acquisition, the scan strictly checks the
reported output state.
If output is off, the scan aborts and runs its output-off cleanup without
applying another setpoint or acquiring another point.
A compliance trip while output remains on is a valid measurement and does not
by itself stop the scan.
Each scan requests output off in cleanup and verifies the reported output flag
before returning normally.
If communication is lost, the output state is reported as unknown through an
exception rather than inferred from the attempted write.
The caller owns output state outside scans.
Each scan manages and verifies its own output state, then returns records with
the requested setpoint and paired reading::

    voltage_points = smu.ch1.sweep_voltage(
        [-1.0, 0.0, 1.0], current_limit=0.01, settle=0.02
    )
    current_points = smu.ch1.sweep_current(
        [-0.01, 0.0, 0.01], voltage_limit=5.0, settle=0.02
    )

Direct ``voltage`` and ``current`` properties use the instrument's native one-shot
DC measurement commands.
The B2910BL is described as a multimeter, but an output-off ``HIGHZ`` or
``NORM`` mode opens the output relay, and ``READ`` or ``INIT`` can enable output
when automatic output-on is enabled.
The 2026-10-27 smoke run used voltage sourcing and did not exercise passive
output-off readings, relay state, circuit loading, or current burden.
Those behaviors remain ``NOT_RUN``, and the measurement properties do not
promise passive output-off readings or replace an isolated DMM for arbitrary
circuits.

No-wire smoke validation (2026-10-27)
=====================================

A no-wire, no-load smoke run used that driver revision on a B2910BL with firmware
5.0.2029.1911.
It ran on Windows 11 with CPython 3.14.3 through PyVISA and the system VISA
backend.
The constant-voltage flow used a 100 µA current limit and NPLC 0.1.
It took single points at requested 0 V, 0.1 V, and 0 V, then ran a host-stepped
0 V, 0.1 V, 0 V sweep with a 0.1 s settle delay.
The instrument returned finite voltage and current readings, and no point
reported a compliance trip.
These no-load readings do not establish measurement accuracy, calibration,
external-load behavior, current-source operation, physical protection or
interlock action, terminal voltage, or deterministic sweep timing.
The flow requested output off and the instrument finally reported ``OFF``; this
does not establish physical zero volts at the terminals.
The SCPI error queues were empty before and after the flow, and cleanup reported
no errors.
Only that driver revision, the B2910BL, and these bounded constant-voltage
flows were exercised.
The full upstream Sphinx HTML and doctest CI has not run on the new PR head and
remains pending.

API reference
=============

.. autoclass:: pymeasure.instruments.keysight.keysightb2910bl.KeysightB2910BL
   :members:
   :show-inheritance:

.. autoclass:: pymeasure.instruments.keysight.keysightb2910bl.B2910BLChannel
   :members:

.. autoclass:: pymeasure.instruments.keysight.keysightb2910bl.B2910BLReading
   :members:

.. autoclass:: pymeasure.instruments.keysight.keysightb2910bl.B2910BLSweepPoint
   :members:
