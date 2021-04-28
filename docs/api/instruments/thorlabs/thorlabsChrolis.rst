###########################
Thorlabs Chrolis LED Source
###########################

.. contents::

Instrument driver for the Thorlabs Chrolis 6-Wavelength High Power LED Source.
This driver wraps the DLL driver provided by Thorlabs for Python.

At the time of writing this wrapper,
the DLL is not yet officially released by Thorlabs, but is
preliminary and experimental.
Features may not work as expected and usage is at your own risk!

*******
Example
*******

.. code-block:: python

    from pymeasure.instruments.thorlabs import ThorlabsDLLAdapter, ThorlabsChrolis

    adapter=ThorlabsDLLAdapter('TL6WL')
    # show connected devices
    print(adapter.devices_by_index)

    instr=ThorlabsChrolis(adapter, adapter.get_resource_name(0), 'Chrolis C1')
    # show LED names
    print(instr.LED_names)

    # set brightness and power state of LEDs
    instr.brightness = (0, 10, 20, 30, 40, 50)
    instr.power_state=(False, False, True, False, False, False)

    # read LED parameters
    print((
        instr.LED405.centroid_wavelength,
        instr.LED405.peak_wavelength,
        instr.LED405.FWHM_wavelength,
        instr.LED405.Ooe2_wavelength,
        instr.LED405.wavelength_range))

    # plot LED spectrum
    instr.LED405.spectrum.plot(x='wavelength', y='power')

*********
Reference
*********

.. autoclass:: pymeasure.instruments.thorlabs.ThorlabsChrolis
    :members:
    :show-inheritance:


==================
Supporting Classes
==================

.. autoclass:: pymeasure.instruments.thorlabs.thorlabsChrolis._ChrolisLED
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.thorlabs.thorlabsChrolis._ChrolisTU
    :members:
    :show-inheritance: