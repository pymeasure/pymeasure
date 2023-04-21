##################################
HP 8560A / 8561B Spectrum Analyzer
##################################

Every unit is the base unit so for time it's seconds, frequency in hertz etc...

-------------------------------------
Generic Specific Attributes & Methods
-------------------------------------
.. contents:: Content
    :depth: 3
    :local:

^^^^^^^
General
^^^^^^^
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.preset
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.attenuation
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.amplitude_unit
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.trigger_mode
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.detector_mode
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.coupling
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.auto_couple
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.linear_scale
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.logarithmic_scale
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.threshold
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.title
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.status
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.done
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.service_request
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.errors
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.save_state
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.recall_state
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.request_service_conditions
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.maximum_hold
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.minimum_hold
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.reference_level_calibration
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.reference_offset
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.reference_level
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.display_line
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.protect_state
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.mixer_level
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.frequency_counter_mode
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.frequency_counter_resolution
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.adjust_all
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.adjust_if
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.hold
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.annotation
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.crt_adjustment_pattern
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.display_parameters
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.revision
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.graticule
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.serial_number
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.id
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.elapsed_time


^^^^^^^^^^^^
Demodulation
^^^^^^^^^^^^
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.demodulation_mode
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.demodulation_agc
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.demodulation_time
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.squelch

^^^^^^^^^
Frequency
^^^^^^^^^
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.start_frequency
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.stop_frequency
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.center_frequency
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.frequency_offset
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.frequency_reference
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.span
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.full_span
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.frequency_display

^^^^^^^^^^^^^^^^^^^^
Resolution Bandwidth
^^^^^^^^^^^^^^^^^^^^
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.resolution_bandwidth
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.resolution_bandwidth_to_span_ratio

^^^^^
Video
^^^^^
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.video_trigger_level
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.video_bandwidth_to_resolution_bandwidth
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.video_bandwidth
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.video_average

^^^
FFT & Measurements
^^^
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.fft_trace_window
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.power_bandwidth
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.fft

^^^^^
Trace
^^^^^
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.view_trace
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.trace_data_a
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.trace_data_b
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.trace_data_format
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.save_trace
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.recall_trace
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.clear_write_trace
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.subtract_display_line_from_trace_b
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.exchange_traces
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.blank_trace
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.trace_a_minus_b_plus_dl
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.trace_a_minus_b

^^^^^^
Marker
^^^^^^
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.peak_search
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_amplitude
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_to_center_frequency
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_delta
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_frequency
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_minimum
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_noise_mode
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_off
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_threshold
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.peak_excursion
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_to_reference_level
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_delta_to_span
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_to_center_frequency_step_size
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_time
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_signal_tracking

^^^^^^^^^^^^^^^^^
Diagnostic Values
^^^^^^^^^^^^^^^^^
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.sampling_frequency
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.lo_frequency
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.mroll_frequency
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.oroll_frequency
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.xroll_frequency
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.sampler_harmonic_number

^^^^^
Sweep
^^^^^
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.single_sweep
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.sweep_time
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.sweep_couple
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.sweep_output
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.continuous_sweep
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.trigger_sweep

^^^^^^^^^^^^^
Normalization
^^^^^^^^^^^^^
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.normalize_trace_data
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.normalized_reference_level
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.normalized_reference_position

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Open/Short Calibration (Reflection)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.recall_open_short_average
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.store_open
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.store_short

^^^^^^^^^^^^^^^^
Thru Calibration
^^^^^^^^^^^^^^^^
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.store_thru
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.recall_thru

-------------------------------------
HP8560A Specific Attributes & Methods
-------------------------------------

.. autoclass:: pymeasure.instruments.hp.HP8560A
    :members:
    :show-inheritance:

-------------------------------------
HP8561B Specific Attributes & Methods
-------------------------------------

.. autoclass:: pymeasure.instruments.hp.HP8561B
    :members:
    :show-inheritance:

------------
Enumerations
------------

.. autoclass:: pymeasure.instruments.hp.hp856Xx.AmplitudeUnits
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.hp.hp856Xx.MixerMode
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.hp.hp856Xx.Trace
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.hp.hp856Xx.CouplingMode
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.hp.hp856Xx.DemodulationMode
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.hp.hp856Xx.DetectionModes
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.hp.hp856Xx.ErrorCode
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.hp.hp856Xx.FrequencyReference
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.hp.hp856Xx.PeakSearchMode
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.hp.hp856Xx.SourceLevelingControlMode
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.hp.hp856Xx.StatusRegister
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.hp.hp856Xx.SweepCoupleMode
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.hp.hp856Xx.SweepOut
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.hp.hp856Xx.TriggerMode
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.hp.hp856Xx.WindowType
    :members:
    :show-inheritance:
