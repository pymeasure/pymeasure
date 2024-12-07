##############################################
Agilent B1500 Semiconductor Parameter Analyzer
##############################################
.. currentmodule:: pymeasure.instruments.agilent.agilentB1500

.. contents::

**********************************************
General Information
**********************************************
This instrument driver does not support all configuration options 
of the B1500 mainframe yet.
So far, it is possible to interface multiple SMU modules and source/measure 
currents and voltages, perform sampling and staircase sweep measurements.
The implementation of further measurement functionalities 
is highly encouraged.
Meanwhile the model is managed by Keysight, 
see the corresponding "Programming Guide"
for details on the control methods and their parameters

Command Translation
===================
Alphabetical list of implemented B1500 commands and their corresponding 
method/attribute names in this instrument driver.

.. |br| raw:: html

    <br>


===========     =============================================
Command         Property/Method
===========     =============================================
``AAD``         :attr:`SMU.adc_type`
``AB``          :meth:`~AgilentB1500.abort`
``AIT``         :meth:`~AgilentB1500.adc_setup`
``AV``          :meth:`~AgilentB1500.adc_averaging`
``AZ``          :attr:`~AgilentB1500.adc_auto_zero`
``BC``          :meth:`~AgilentB1500.clear_buffer`
``CL``          :meth:`SMU.disable`
``CM``          :attr:`~AgilentB1500.auto_calibration`
``CMM``         :attr:`SMU.meas_op_mode`
``CN``          :meth:`SMU.enable`
``DI``          :meth:`SMU.force` mode: ``'CURRENT'``
``DV``          :meth:`SMU.force` mode: ``'VOLTAGE'``
``DZ``          :meth:`~AgilentB1500.force_gnd`, :meth:`SMU.force_gnd`
``ERRX?``       :meth:`~AgilentB1500.check_errors`
``FL``          :attr:`SMU.filter`
``FMT``         :meth:`~AgilentB1500.data_format`
``*IDN?``       :attr:`~AgilentB1500.id`
``*LRN?``       :meth:`~AgilentB1500.query_learn`, |br|
                multiple methods to read/format settings directly
``MI``          :meth:`SMU.sampling_source` mode: ``'CURRENT'``
``ML``          :attr:`~AgilentB1500.sampling_mode`
``MM``          :meth:`~AgilentB1500.meas_mode`
``MSC``         :meth:`~AgilentB1500.sampling_auto_abort`
``MT``          :meth:`~AgilentB1500.sampling_timing`
``MV``          :meth:`SMU.sampling_source` mode: ``'VOLTAGE'``
``*OPC?``       :meth:`~AgilentB1500.check_idle`
``PA``          :meth:`~AgilentB1500.pause`
``PAD``         :attr:`~AgilentB1500.parallel_meas`
``RI``          :attr:`~SMU.meas_range_current`
``RM``          :meth:`SMU.meas_range_current_auto`
``*RST``        :meth:`~AgilentB1500.reset`
``RV``          :attr:`~SMU.meas_range_voltage`
``SSR``         :attr:`~SMU.series_resistor`
``TSC``         :attr:`~AgilentB1500.time_stamp`
``TSR``         :meth:`~AgilentB1500.clear_timer`
``UNT?``        :meth:`~AgilentB1500.query_modules`
``WAT``         :meth:`~AgilentB1500.wait_time`
``WI``          :meth:`SMU.staircase_sweep_source` mode: ``'CURRENT'``
``WM``          :meth:`~AgilentB1500.sweep_auto_abort`
``WSI``         :meth:`SMU.synchronous_sweep_source` mode: ``'CURRENT'``
``WSV``         :meth:`SMU.synchronous_sweep_source` mode: ``'VOLTAGE'``
``WT``          :meth:`~AgilentB1500.sweep_timing`
``WV``          :meth:`SMU.staircase_sweep_source` mode: ``'VOLTAGE'``
``XE``          :meth:`~AgilentB1500.send_trigger`
===========     =============================================

**********************************************
Examples
**********************************************

Initialization of the Instrument
====================================

.. code-block:: python

    from pymeasure.instruments.agilent import AgilentB1500

    # explicitly define r/w terminations; set sufficiently large timeout in milliseconds or None.
    b1500=AgilentB1500("GPIB0::17::INSTR", read_termination='\r\n', write_termination='\r\n', timeout=600000)
    # query SMU config from instrument and initialize all SMU instances
    b1500.initialize_all_smus()
    # set data output format (required!)
    b1500.data_format(21, mode=1) #call after SMUs are initialized to get names for the channels


IV measurement with 4 SMUs
=================================================

.. code-block:: python

    # choose measurement mode
    b1500.meas_mode('STAIRCASE_SWEEP', *b1500.smu_references) #order in smu_references determines order of measurement
    
    # settings for individual SMUs
    for smu in b1500.smu_references:
        smu.enable() #enable SMU
        smu.adc_type = 'HRADC' #set ADC to high-resoultion ADC
        smu.meas_range_current = '1 nA'
        smu.meas_op_mode = 'COMPLIANCE_SIDE' # other choices: Current, Voltage, FORCE_SIDE, COMPLIANCE_AND_FORCE_SIDE

    # General Instrument Settings
    # b1500.adc_averaging = 1
    # b1500.adc_auto_zero = True
    b1500.adc_setup('HRADC','AUTO',6)
    #b1500.adc_setup('HRADC','PLC',1)

    #Sweep Settings
    b1500.sweep_timing(0,5,step_delay=0.1) #hold,delay
    b1500.sweep_auto_abort(False,post='STOP') #disable auto abort, set post measurement output condition to stop value of sweep
    # Sweep Source
    nop = 11
    b1500.smu1.staircase_sweep_source('VOLTAGE','LINEAR_DOUBLE','Auto Ranging',0,1,nop,0.001) #type, mode, range, start, stop, steps, compliance
    # Synchronous Sweep Source
    b1500.smu2.synchronous_sweep_source('VOLTAGE','Auto Ranging',0,1,0.001) #type, range, start, stop, comp
    # Constant Output (could also be done using synchronous sweep source with start=stop, but then the output is not ramped up)
    b1500.smu3.ramp_source('VOLTAGE','Auto Ranging',-1,stepsize=0.1,pause=20e-3) #output starts immediately! (compared to sweeps)
    b1500.smu4.ramp_source('VOLTAGE','Auto Ranging',0,stepsize=0.1,pause=20e-3)
    
    #Start Measurement
    b1500.check_errors()
    b1500.clear_buffer()
    b1500.clear_timer()
    b1500.send_trigger()

    # read measurement data all at once
    b1500.check_idle() #wait until measurement is finished
    data = b1500.read_data(2*nop) #Factor 2 because of double sweep

    #alternatively: read measurement data live
    meas = []
    for i in range(nop*2):
        read_data = b1500.read_channels(4+1) # 4 measurement channels, 1 sweep source (returned due to mode=1 of data_format)
        # process live data for plotting etc.
        # data format for every channel (status code, channel name e.g. 'SMU1', data name e.g 'Current Measurement (A)', value)
        meas.append(read_data)

    #sweep constant sources back to 0V
    b1500.smu3.ramp_source('VOLTAGE','Auto Ranging',0,stepsize=0.1,pause=20e-3)
    b1500.smu4.ramp_source('VOLTAGE','Auto Ranging',0,stepsize=0.1,pause=20e-3) 


Sampling measurement with 4 SMUs
=====================================

.. code-block:: python

    # choose measurement mode
    b1500.meas_mode('SAMPLING', *b1500.smu_references) #order in smu_references determines order of measurement
    number_of_channels = len(b1500.smu_references)

    # settings for individual SMUs
    for smu in b1500.smu_references:
        smu.enable() #enable SMU
        smu.adc_type = 'HSADC' #set ADC to high-speed ADC
        smu.meas_range_current = '1 nA'
        smu.meas_op_mode = 'COMPLIANCE_SIDE' # other choices: Current, Voltage, FORCE_SIDE, COMPLIANCE_AND_FORCE_SIDE

    b1500.sampling_mode = 'LINEAR'
    # b1500.adc_averaging = 1
    # b1500.adc_auto_zero = True
    b1500.adc_setup('HSADC','AUTO',1)
    #b1500.adc_setup('HSADC','PLC',1)
    nop=11
    b1500.sampling_timing(2,0.005,nop) #MT: bias hold time, sampling interval, number of points
    b1500.sampling_auto_abort(False,post='BIAS') #MSC: BASE/BIAS
    b1500.time_stamp = True

    # Sources
    b1500.smu1.sampling_source('VOLTAGE','Auto Ranging',0,1,0.001) #MV/MI: type, range, base, bias, compliance
    b1500.smu2.sampling_source('VOLTAGE','Auto Ranging',0,1,0.001)
    b1500.smu3.ramp_source('VOLTAGE','Auto Ranging',-1,stepsize=0.1,pause=20e-3) #output starts immediately! (compared to sweeps)
    b1500.smu4.ramp_source('VOLTAGE','Auto Ranging',-1,stepsize=0.1,pause=20e-3)

    #Start Measurement
    b1500.check_errors()
    b1500.clear_buffer()
    b1500.clear_timer()
    b1500.send_trigger()

    meas=[]
    for i in range(nop):
        read_data = b1500.read_channels(1+2*number_of_channels) #Sampling Index + (time stamp + measurement value) * number of channels
        # process live data for plotting etc.
        # data format for every channel (status code, channel name e.g. 'SMU1', data name e.g 'Current Measurement (A)', value)
        meas.append(read_data)

    #sweep constant sources back to 0V
    b1500.smu3.ramp_source('VOLTAGE','Auto Ranging',0,stepsize=0.1,pause=20e-3)
    b1500.smu4.ramp_source('VOLTAGE','Auto Ranging',0,stepsize=0.1,pause=20e-3)

**********************************************
Main Classes
**********************************************

Classes to communicate with the instrument:

* :class:`AgilentB1500`: Main instrument class
* :class:`SMU`: Instantiated by main instrument class for every SMU

All `query` commands return a human readable dict of settings. These are intended for debugging/logging/file headers, not for passing to the accompanying setting commands.

.. autoclass:: AgilentB1500
    :members:
    :show-inheritance:
    :member-order: bysource
.. autoclass:: SMU
    :members:
    :show-inheritance:
    :member-order: bysource

.. .. automodule:: pymeasure.instruments.agilent.agilentB1500
..     :members: AgilentB1500, SMU
..     :show-inheritance:

**********************************************
Supporting Classes
**********************************************

Classes that provide additional functionalities:

* :class:`QueryLearn`: Process read out of instrument settings

* :class:`SMUCurrentRanging`, :class:`SMUVoltageRanging`: Allowed 
  ranges for different SMU types and transformation of 
  range names to indices (base: :class:`Ranging`)

.. autoclass:: QueryLearn
    :members:
    :show-inheritance:
.. autoclass:: Ranging
    :members:
    :show-inheritance:
.. autoclass:: SMUCurrentRanging
    :members:
    :show-inheritance:
.. autoclass:: SMUVoltageRanging
    :members:
    :show-inheritance:

.. .. automodule:: pymeasure.instruments.agilent.agilentB1500
..     :members: QueryLearn, Ranging, SMUCurrentRanging, SMUVoltageRanging
..     :show-inheritance:

Enumerations
=========================
Enumerations are used for easy selection of the available 
parameters (where it is applicable). 
Methods accept member name or number as input, 
but name is recommended for readability reasons. 
The member number is passed to the instrument. 
Converting an enumeration member into a string gives a title case, 
whitespace separated string (:meth:`~.CustomIntEnum.__str__`)
which cannot be used to select an enumeration member again. 
It's purpose is only logging or documentation.

.. call automodule with full module path only once to avoid duplicate index warnings
.. autodoc other classes via currentmodule:: and autoclass::

.. automodule:: pymeasure.instruments.agilent.agilentB1500
    :members: 
    :exclude-members: AgilentB1500, SMU, QueryLearn, Ranging, SMUCurrentRanging, SMUVoltageRanging
    :show-inheritance:
    :member-order: bysource
