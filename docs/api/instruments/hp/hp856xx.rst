##################################
HP 8560A / 8561B Spectrum Analyzer
##################################

Every unit is used in the base unit, so for time it is s (Seconds), frequency in Hz (Hertz) etc...

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
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.set_auto_couple
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.set_linear_scale
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.logarithmic_scale
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.threshold
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.set_title
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.status
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.check_done
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.request_service
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.errors
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.save_state
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.recall_state
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.request_service_conditions
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.set_maximum_hold
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.set_minimum_hold
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.reference_level_calibration
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.reference_offset
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.reference_level
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.display_line
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.protect_state_enabled
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.mixer_level
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.frequency_counter_mode_enabled
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.frequency_counter_resolution
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.adjust_all
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.adjust_if
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.hold
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.annotation_enabled
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.set_crt_adjustment_pattern
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.display_parameters
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.firmware_revision
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.graticule_enabled
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.serial_number
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.id
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.elapsed_time


^^^^^^^^^^^^
Demodulation
^^^^^^^^^^^^
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.demodulation_mode
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.demodulation_agc_enabled
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.demodulation_time
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.squelch

^^^^^^^^^
Frequency
^^^^^^^^^
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.start_frequency
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.stop_frequency
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.center_frequency
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.frequency_offset
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.frequency_reference_source
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.span
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.set_full_span
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.frequency_display_enabled

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

^^^^^^^^^^^^^^^^^^
FFT & Measurements
^^^^^^^^^^^^^^^^^^
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.create_fft_trace_window
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.get_power_bandwidth
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.do_fft

^^^^^
Trace
^^^^^
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.view_trace
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.get_trace_data_a
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.get_trace_data_b
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.set_trace_data_a
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.set_trace_data_b
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.trace_data_format
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.save_trace
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.recall_trace
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.clear_write_trace
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.subtract_display_line_from_trace_b
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.exchange_traces
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.blank_trace
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.trace_a_minus_b_plus_dl_enabled
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.trace_a_minus_b_enabled

^^^^^^
Marker
^^^^^^
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.search_peak
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_amplitude
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.set_marker_to_center_frequency
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_delta
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_frequency
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.set_marker_minimum
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_noise_mode_enabled
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.deactivate_marker
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_threshold
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.peak_excursion
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.set_marker_to_reference_level
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.set_marker_delta_to_span
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.set_marker_to_center_frequency_step_size
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_time
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.marker_signal_tracking_enabled

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
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.sweep_single
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.sweep_time
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.sweep_couple
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.sweep_output
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.set_continuous_sweep
.. automethod:: pymeasure.instruments.hp.hp856Xx.HP856Xx.trigger_sweep

^^^^^^^^^^^^^
Normalization
^^^^^^^^^^^^^
.. autoattribute:: pymeasure.instruments.hp.hp856Xx.HP856Xx.normalize_trace_data_enabled
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
