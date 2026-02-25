#########################################################
Advantest R6245/R6246 DC Voltage/Current Sources/Monitors
#########################################################
.. currentmodule:: pymeasure.instruments.advantest.advantestR624X

**********************************************
Main Classes
**********************************************

.. autoclass:: AdvantestR6245
    :members:
    :show-inheritance:
    :member-order: bysource
.. autoclass:: AdvantestR6246
    :members:
    :show-inheritance:
    :member-order: bysource
.. autoclass:: AdvantestR624X
    :members:
    :show-inheritance:
    :member-order: bysource
.. autoclass:: SMUChannel
    :members:
    :show-inheritance:
    :member-order: bysource

.. automodule:: pymeasure.instruments.advantest.advantestR624X
    :members:
    :exclude-members: AdvantestR6245, AdvantestR6246, AdvantestR624X, SMUChannel
    :show-inheritance:
    :member-order: bysource

.. contents::

**********************************************
General Information
**********************************************

The R6245/6246 Series are DC voltage/current sources and monitors having
source measurement units (SMUs) with 2 isolated channels. The series covers
wide source and measurement ranges. It is ideal for measurement of DC characteristics
of items ranging from separate semiconductors such as bipolar transistors, MOSFETs
and GaAsFETs, to ICs and power devices. Further, due to the increased measuring speed
and synchronized 2-channel measurement function, device I/O characteristics can be
measured with precise timing at high speed which was previously difficult to accomplish.
Due to features such as the trigger link function and the sequence programming function
which automatically performs a series of evaluation tests, the R6245/6246
enable much more efficient evaluation tests.

There is a total of 99 commands, the majority of commands have been implemented. Device
documentation is in Japanese, and the device options are enormous. The implementation is
based on 6245S-GPIB-B-FHJ-8335160E01.pdf, which can be downloaded from the ADCMT website.

**********************************************
Examples
**********************************************

Initialization of the Instrument
====================================

.. code-block:: python

    from pymeasure.instruments.advantest import AdvantestR6246
    from pymeasure.instruments.advantest.advantestR624X import *

    smu = AdvantestR6246("GPIB::1")


Simple dual channel synchronous measurement example
====================================================

Measurement characteristics:
  Channel A (MASTER): DC voltage source + current measurement
  Channel B (SLAVE):  Pulsed voltage source + current measurement

.. note::

    For dual-channel synchronous mode (``PULSED_SYNC``), use ``auto_sampling=False``
    in the ``sample_mode()`` call. With ``auto_sampling=True`` (the default), the
    auto-output data contains the generated/source value, not the measurement result.

.. warning::

    ``CurrentRange.AUTO`` and ``AUTO_*`` (limited auto) ranges cannot be used for
    pulse measurement or pulse sweep — the instrument returns error 00211. Always use
    a fixed range such as ``CurrentRange.FIXED_BEST`` when configuring pulsed modes.

.. code-block:: python

    smu = AdvantestR6246("GPIB::1")
    smu.reset()                                               # Set default parameters

    # Ch A (MASTER): DC voltage source + current measurement
    smu.ch_A.voltage_source(source_range=VoltageRange.FIXED_6V,
                            source_value=5,
                            current_compliance=2)
    smu.ch_A.measure_current(current_range=CurrentRange.FIXED_BEST)

    # Ch B (SLAVE): Pulsed voltage source + current measurement
    smu.ch_B.fast_mode_enabled = True
    smu.ch_B.sample_hold_mode = SampleHold.MODE_1mS
    smu.ch_B.voltage_pulsed_source(source_range=VoltageRange.FIXED_6V,
                                   pulse_value=6, base_value=0,
                                   current_compliance=2)
    smu.ch_B.measure_current(current_range=CurrentRange.FIXED_BEST)
    smu.ch_B.timing_parameters(hold_time=0, measurement_delay=1e-4,
                               pulsed_width=1e-2, pulsed_period=2e-2)

    # PULSED_SYNC with auto_sampling=False (critical for correct readout)
    smu.ch_A.sample_mode(SampleMode.PULSED_SYNC, auto_sampling=False)

    smu.ch_A.enable_source()
    smu.ch_B.enable_source()

    for i in range(10):
        smu.ch_A.select_for_output()                          # Select channel A (FCH 01?)
        smu.ch_A.trigger()                                    # Trigger (XE 1, syncs both)
        Ic_a = smu.read_measurement()                         # Read channel A measurement

        smu.ch_B.select_for_output()                          # Select channel B (FCH 02?)
        Ic_b = smu.read_measurement()                         # Read channel B measurement
        print(f'Ic_a={Ic_a}, Ic_b={Ic_b}')

    smu.standby()                                             # Put channel A & B in standby

Program example for DC measurement
=====================================

Measurement characteristics:
  Function: VSIM - Source voltage and measure current
  Trigger voltage: 10V
  Current compliance: 0.5A
  Measurement delay time: 1ms
  Integration time: 1 PLC
  Response: Fast

After operating, the measurement is repeated 10 times with a trigger command and he prints out the results.

.. code-block:: python

    smu = AdvantestR6246("GPIB::1")
    smu.reset()                                                      # Set default parameters
    smu.ch_A.sample_mode(SampleMode.ASYNC, False)                     # Asynchronous operation and single shot sampling by trigger and command
    smu.ch_A.voltage_source(source_range = VoltageRange.FIXED_BEST,
                            source_value = 10,
                            current_compliance = 0.5)                # compliance of 0.5A
    smu.ch_A.measure_current()                                       # Measure current
    smu.ch_A.timing_parameters(hold_time = 0,                    # 0 sec hold time
                                   measurement_delay = 1E-3,         # 1ms delay between measurements
                                   pulsed_width = 5E-3,              # 5ms pulse width
                                   pulsed_period = 10E-3)            # 10ms pulse period
    smu.ch_A.sample_hold_mode = SampleHold.MODE_1PLC                 # Sample at 1 power line cycle
    smu.ch_A.fast_mode_enabled = True                                # Set channel response to fast
    smu.ch_A.enable_source()                                         # Set channel in operating state
    smu.ch_A.select_for_output()                                     # Select channel for measurement output

    for i in range(1, 10):
        smu.ch_A.trigger()                                           # Trigger a measurement
        measurement = smu.read_measurement()
        print(f"NO {i} {measurement}")

    smu.ch_A.standby()                                               # Put channel A in standby mode

Program example for DC measurement (with external trigger)
==========================================================

Measurement characteristics:
  Function: VSIM - Source voltage and measure current
  Source voltage: 10 V
  Base voltage 1 V
  Current compliance: 0.5 A
  Pulse width: 5 ms
  Pulse period: 10 ms
  Measurement delay time: 1 ms
  Integration time: 1 ms
  Response: Fast

After operating, an external trigger input signal is pulsed to measure the channel operation register.
Reads the fixed end bit, captures the measurement data, and prints out the measurement result.

.. code-block:: python

    smu = AdvantestR6246("GPIB::1")
    smu.reset()                                                      # Set default parameters

    smu.ch_A.auto_zero_enabled = False
    smu.ch_A.sample_mode(SampleMode.ASYNC, False)                     # Asynchronous operation and single shot sampling by trigger and command
    smu.ch_A.voltage_pulsed_source(
          source_range = VoltageRange.FIXED_BEST,
          pulse_value = 10,
          base_value = 1,
          current_compliance = 0.5)
    smu.ch_A.measure_current(current_range=CurrentRange.FIXED_BEST)  # Fixed range required for pulsed
    smu.ch_A.fast_mode_enabled = True                                # Set channel response to fast
    smu.ch_A.sample_hold_mode = SampleHold.MODE_1mS                  # Sample at 1mS
    smu.ch_A.timing_parameters(hold_time = 0,                    # 0 sec hold time
                                   measurement_delay = 1E-3,         # 1ms delay between measurements
                                   pulsed_width = 5E-3,              # 5ms pulse width
                                   pulsed_period = 10E-3)            # 10ms pulse period
    smu.ch_A.trigger_input = TriggerInputType.ALL                    # Mode 1 enables the trigger input signal
    smu.ch_A.output_enable_register = COR.HAS_MEASUREMENT_DATA       # Measurement data available
    smu.service_request_enable_register = SRER.COP                   # COP Set when a bit in the Channel Operations Register is set with the Enable Register set to Enable.
    smu.ch_A.enable_source()                                         # Set channel in operating state
    smu.ch_A.select_for_output()                                     # Select channel for measurement output

    for i in range(1, 10):
        while not smu.ch_A.operation_register & COR.HAS_MEASUREMENT_DATA:
            pass

        measurement = smu.read_measurement()
        print(f"NO {i} {measurement}")

        while not smu.ch_A.operation_register & COR.WAITING_FOR_TRIGGER:
            pass

    smu.ch_A.standby()                                               # Put channel A in standby mode

Program example for pulse measurement
=================================================

Measurement characteristics:
  Function: ISVM - Source current and measure voltage
  Pulse generation current: 100mA
  Base current: 1mA
  Voltage compliance: 5V
  Pulse width: 0
  Pulse period : 0
  Measurement delay time: 0
  Integration time: 1ms
  Response: Fast

After the operation, repeat the measurement 10 times with the trigger command and print out the measurement results.

.. code-block:: python

    smu = AdvantestR6246("GPIB::1")
    smu.reset()                                                         # Set default parameters
    smu.ch_A.sample_mode(SampleMode.ASYNC, auto_sampling = False)
    smu.ch_A.current_pulsed_source(
          source_range = CurrentRange.FIXED_600mA,
          pulse_value = 0.1,                                            # 100mA
          base_value = 1E-3,                                            # 1mA
          voltage_compliance = 5)                                       # 5V
    smu.ch_A.measure_voltage(voltage_range = VoltageRange.FIXED_BEST)
    smu.ch_A.fast_mode_enabled = True                                   # Set channel response to fast
    smu.ch_A.sample_hold_mode = SampleHold.MODE_1mS                     # Sample at 1mS
    smu.ch_A.timing_parameters(hold_time = 0,                       # 0 sec hold time
                                   measurement_delay = 0,               # 0 sec delay between measurements
                                   pulsed_width = 0,                    # 0 sec pulse width
                                   pulsed_period = 0)                   # 0 sec pulse period
    smu.ch_A.enable_source()                                            # Set channel in operating state
    smu.ch_A.select_for_output()                                        # Select channel for measurement output

    for i in range(1, 10):
        smu.ch_A.trigger()                                              # Trigger measurement

        measurement = smu.read_measurement()
        print(f"NO {i} {measurement}")

        while not smu.ch_A.operation_register & COR.WAITING_FOR_TRIGGER:
            pass

    smu.ch_A.standby()                                                  # Put channel A in standby mode

Fixed Level Sweep Program Example
=================================================

Measurement characteristics:
  function: VSVM - Voltage source and voltage measurement
  Level value: 15V
  Bias value: 0V
  Number of measurements: 20 times
  Compliance: 6mA
  Measuring range: Best fixed range (=60V range)
  Integration time: 100us
  Measurement delay time: 0
  Hold time: 1ms
  Sampling mode: automatic sweep
  Measurement data output method: Buffering output (output of specified data)

After operating, make 20 measurements in fixed sweep. Detect the end of sweep
by looking at the Channel Operation Register (COR). After the sweep is finished,
read the measured data from 1 to 2 using the RMM command.

.. code-block:: python

    smu = AdvantestR6246("GPIB::1")

    # First we setup our main parameters
    smu.reset()                                                      # Set default parameters

    smu.ch_A.output_type(output_type = OutputType.BUFFERING_OUTPUT_SPECIFIED,
                         measurement_type = MeasurementType.MEASURE_DATA)

    smu.output_format(delimiter_format = 2,                           # No header, ASCII format
                      block_delimiter = 1,                           # Make it the same as the terminator
                      terminator = 1)                                # CR, LF<EOI>

    smu.ch_A.analog_input = 1                                        # Turn off the analog input.

    smu.lo_common_relay(enable = True)                               # Turns the connection relay on

    smu.ch_A.wire_mode(four_wire = False,                             # disable four wire measurements
                       lo_guard = True)                              # enable the LO-GUARD relay.

    smu.ch_A.auto_zero_enabled = False
    smu.ch_A.trigger_input = TriggerInputType.ALL                    # Mode 1 enables the trigger input signal

    # Now we set measurement specific variables
    smu.ch_A.clear_measurement_buffer()
    smu.ch_A.sample_mode(SampleMode.ASYNC, auto_sampling = True)
    smu.ch_A.voltage_fixed_level_sweep(voltage_range = VoltageRange.FIXED_60V,
                                       voltage_level = 15,
                                       measurement_count = 20,       # 20 measurements
                                       current_compliance = 6E-3,    # compliance at 6mA
                                       bias = 0)
    smu.ch_A.measure_voltage(voltage_range = VoltageRange.FIXED_BEST)
    smu.ch_A.sample_hold_mode = SampleHold.MODE_100uS
    smu.ch_A.timing_parameters(hold_time = 1E-3,                 # 1ms sec hold time
                                   measurement_delay = 0,            # 0 sec delay between measurements
                                   pulsed_width = 0,                 # 0 sec pulse width
                                   pulsed_period = 0)                # 0 sec pulse period

    smu.ch_A.enable_source()                                         # Set channel in operating state
    smu.ch_A.trigger()                                               # Start the sweep

    while not smu.ch_A.operation_register & COR.END_OF_SWEEP:        # Wait until the sweep is done
        pass

    # Read measurements
    for i in range(1, 20):
        measurement = smu.ch_A.read_measurement_from_addr(i)
        print(i, measurement)

    smu.ch_A.standby()                                               # Put channel A in standby mode

