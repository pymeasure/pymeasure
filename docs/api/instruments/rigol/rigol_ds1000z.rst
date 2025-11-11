##########################
Rigol DS1000Z oscilloscope
##########################

.. currentmodule:: pymeasure.instruments.rigol.rigol_ds1000z

Quick start
===========

.. code-block:: python

    from pymeasure.instruments.rigol import RigolDS1000Z

    with RigolDS1000Z("TCPIP0::10.0.0.5::INSTR") as scope:
        scope.reset()
        scope.clear_status()

        # Configure analogue channel 1
        scope.channel_1.display_enabled = True
        scope.channel_1.coupling = "DC"
        scope.channel_1.scale = 0.5  # volts/div

        # Pull the waveform
        time_axis, voltage = scope.read_waveform(source=1)

Memory depth handling
=====================

Rigol scopes restrict memory depth to discrete values that depend on the number
of enabled analogue inputs and, on MSO models, digital pod lines. The driver
automatically queries the display state of each analogue channel before
accepting a depth change and raises :class:`ValueError` if the requested value
does not fit the current configuration.

Digital pod usage varies between models, so the driver exposes
:meth:`RigolDS1000Z.set_digital_channel_hint` for callers to provide the number
of active digital lines (0, 8, or 16). This hint is optional—if omitted, the
logic assumes the pod is disabled—but it enables strict validation when logic
channels are in use.

Waveform acquisition
====================

:meth:`RigolDS1000Z.read_waveform` wraps the SCPI ``:WAV`` commands, handling
chunked reads, binary block parsing, and scaling the returned data to physical
units. The method accepts either integer channel indices or the standard Rigol
source names (for example ``"CHAN1"``, ``"MATH"``, or ``"D0"``), and it supports
all Rigol formats via the :class:`WaveformFormat` enum.

Display capture
===============

The :class:`RigolDS1000ZDisplay` helper contains front-panel display controls,
including :meth:`RigolDS1000ZDisplay.grab_image`. Calling ``grab_image`` issues
``:DISP:DATA?`` and returns the raw image bytes (PNG, BMP, JPEG, or TIFF) so you
can save them directly to disk:

.. code-block:: python

    from pathlib import Path

    image = scope.display.grab_image(color=True, image_format="PNG")
    Path("screenshot.png").write_bytes(image)

Optional ``color`` and ``invert`` parameters map to the oscilloscope arguments,
allowing monochrome or inverted captures without halting acquisition.

API reference
=============

.. autoclass:: RigolDS1000Z
    :members:
    :show-inheritance:

.. autoclass:: RigolDS1000ZChannel
    :members:
    :show-inheritance:

.. autoclass:: RigolDS1000ZDisplay
    :members:
    :show-inheritance:

Enumerations
============

The driver ships with enums for common SCPI literals to make interactive use
less error-prone.

.. autoclass:: AcquireType
    :members:

.. autoclass:: WaveformMode
    :members:

.. autoclass:: WaveformFormat
    :members:
