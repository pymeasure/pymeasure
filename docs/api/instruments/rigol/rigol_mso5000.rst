##################################
Rigol MSO5000 Series Oscilloscopes
##################################

The :class:`~pymeasure.instruments.rigol.MSO5000` driver supports the
MSO5072, MSO5074, MSO5102, MSO5104, MSO5204, and MSO5354 models.
It exposes analog and digital channels, acquisition, automatic measurement, timebase,
advanced analysis, bus decoding, protocol triggers, waveform transfer, and selected system and
storage functions.

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

Automatic measurements
======================

Use :attr:`~pymeasure.instruments.rigol.MSO5000.measurements` to configure automatic
measurement sources, thresholds, modes, statistics, and regions.
Measurement item and statistic type arguments accept the documented SCPI short-to-long forms.

.. code-block:: python

    scope.measurements.source = "CHAN1"
    scope.measurements.mode = "PREC"
    frequency = scope.measurements.item("FREQ")

    scope.measurements.enable_item("RRDELAY", "CHAN1", "CHAN2")
    delay = scope.measurements.item("RRDELAY", "CHAN1", "CHAN2")

The :meth:`~pymeasure.instruments.rigol.MSO5000.measure` convenience method queries an
automatic measurement on an analog channel.
For example, ``scope.measure("VPP", 2)`` measures peak-to-peak voltage on channel 2.
Use the measurement child directly for math, digital, or dual-source measurements.

Advanced scope functions
========================

Dedicated child interfaces group cursor, display, histogram, mask-test, recording,
reference-waveform, and search configuration.
The four math waveforms use :attr:`~pymeasure.instruments.rigol.MSO5000.math_1` through
:attr:`~pymeasure.instruments.rigol.MSO5000.math_4` so their channel selector is explicit.

.. code-block:: python

    scope.cursor.mode = "MAN"
    scope.cursor.manual_source = "CHAN1"
    delta_t = scope.cursor.manual_x_delta

    scope.math_1.operator = "FFT"
    scope.math_1.fft_source = "CHAN1"
    scope.math_1.fft_window = "HANN"

    scope.search.mode = "EDGE"
    scope.search.edge_source = "CHAN1"

Per-slot reference settings use methods on
:attr:`~pymeasure.instruments.rigol.MSO5000.references` because the SCPI commands carry a
reference number argument.

Mixed-signal and protocol functions
===================================

Four decoding buses are exposed as :attr:`~pymeasure.instruments.rigol.MSO5000.bus_1` through
:attr:`~pymeasure.instruments.rigol.MSO5000.bus_4`. Digital inputs ``D0`` through ``D15`` are
available as ``d_0`` through ``d_15`` and in the
:attr:`~pymeasure.instruments.rigol.MSO5000.digital_channels` collection. The two logic pods use
:attr:`~pymeasure.instruments.rigol.MSO5000.pod_1` and
:attr:`~pymeasure.instruments.rigol.MSO5000.pod_2`.

.. code-block:: python

    scope.bus_1.mode = "RS232"
    scope.bus_1.rs232_rx = "CHAN2"
    scope.bus_1.rs232_baud = 9600

    scope.protocol_trigger.rs232_source = "CHAN2"
    scope.protocol_trigger.rs232_when = "DATA"

Decoder and trigger availability depends on the installed instrument options. Digital-channel and
logic-pod operation additionally requires the appropriate active logic probe. The
:attr:`~pymeasure.instruments.rigol.rigol_mso5000.LogicAnalyzerSubsystem.time_calibration`
property is read-only because changing it alters calibration state.

Integrated functions
====================

Dedicated child interfaces expose Bode plot, counter, DVM, and power-analysis settings. Optional
waveform-generator channels use :attr:`~pymeasure.instruments.rigol.MSO5000.awg_1` and
:attr:`~pymeasure.instruments.rigol.MSO5000.awg_2`.

.. code-block:: python

    frequency = scope.counter.current
    voltage = scope.dvm.current
    scope.awg_1.apply_sine(1000, 0.5, 0, 0)

Generator and Bode-plot availability depends on the installed AWG option and suitable wiring.
``upload_waveform`` accepts raw DAC16 bytes so the driver does not impose an undocumented byte
order.

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

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.MeasurementSubsystem
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.CursorSubsystem
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.DisplaySubsystem
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.HistogramSubsystem
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.MaskSubsystem
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.MathChannel
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.RecordingSubsystem
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.ReferenceSubsystem
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.SearchSubsystem
    :members:
    :show-inheritance:


.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.BodePlotSubsystem
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.CounterSubsystem
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.DVMSubsystem
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.PowerAnalysisSubsystem
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.AWGChannel
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.QuickSubsystem
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.DigitalChannel
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.LogicPod
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.LogicAnalyzerSubsystem
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.BusChannel
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.TriggerSubsystem
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_mso5000.MSO5000Channel
    :members:
    :show-inheritance:
