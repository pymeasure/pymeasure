####################
Thorlabs Powermeters
####################

.. contents::

Instrument driver for powermeters from Thorlabs, supported by the `TLPM` driver. 
This is the case for all powermeters compatible with recent versions of the Optical Power Monitor.

Remark: The powermeters work with two different drivers. The `TLPM` driver is newer and used with
the Optical Power Monitor. The older driver supports direct VISA communication and is used for example
in :class:`~pymeasure.instruments.thorlabs.ThorlabsPM100USB`. 

It is possible to communicate with SCPI commands via the methods
:meth:`~pymeasure.instruments.thorlabs.thorlabspm._ThorlabsPowermeterBase.write`,
:meth:`~pymeasure.instruments.thorlabs.thorlabspm._ThorlabsPowermeterBase.read`,
:meth:`~pymeasure.instruments.thorlabs.thorlabspm._ThorlabsPowermeterBase.ask`.
But preparation of appropriate buffers and formatting has to be taken care of.

*******
Example
*******

.. code-block:: python

    from pymeasure.instruments.thorlabs import ThorlabsDLLAdapter, ThorlabsPowermeter

    adapter=ThorlabsDLLAdapter('TLPM')
    # show connected devices
    print(adapter.devices_by_index)

    pm=ThorlabsPowermeter(adapter, adapter.get_resource_name(0), 'PM100USB')

    # print device and sensor information
    print(pm.sensor_info)
    print(pm.id)

    # power measurement
    pm.power.range = 'min'
    pm.dark_adjust(timeout=60)
    pm.power.auto_range = True
    pm.power.measure

*********
Reference
*********

.. autoclass:: pymeasure.instruments.thorlabs.ThorlabsPowermeter
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.thorlabs.thorlabspm._ThorlabsPowermeterBase
    :members:
    :show-inheritance:

==============
Sensor Classes
==============

.. autoclass:: pymeasure.instruments.thorlabs.thorlabspm._ThorlabsPhotosensor
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.thorlabs.thorlabspm._Photodiode
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.thorlabs.thorlabspm._Thermopile
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.thorlabs.thorlabspm._Pyrosensor
    :members:
    :show-inheritance:

===================
Measurement Classes
===================

------------
Base Classes
------------

.. autoclass:: pymeasure.instruments.thorlabs.thorlabspm._ThorlabsPhotosensorMeasurement
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.thorlabs.thorlabspm._ThorlabsPhotosensorMeasurementAutoRange
    :members:
    :show-inheritance:

-------------------
Current Measurement
-------------------

.. autoclass:: pymeasure.instruments.thorlabs.thorlabspm._CurrentMeasurement
    :members:
    :show-inheritance:

-------------------
Voltage Measurement
-------------------

.. autoclass:: pymeasure.instruments.thorlabs.thorlabspm._VoltageMeasurement
    :members:
    :show-inheritance:

-----------------
Power Measurement
-----------------

.. autoclass:: pymeasure.instruments.thorlabs.thorlabspm._PowerMeasurement
    :members:
    :show-inheritance:

------------------
Energy Measurement
------------------

.. autoclass:: pymeasure.instruments.thorlabs.thorlabspm._EnergyMeasurement
    :members:
    :show-inheritance:

------------------
Other Measurements
------------------

.. autoclass:: pymeasure.instruments.thorlabs.thorlabspm._FrequencyMeasurement
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.thorlabs.thorlabspm._ExternalNTC
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.thorlabs.thorlabspm._AuxAD
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.thorlabs.thorlabspm._DigitalIO
    :members:
    :show-inheritance: