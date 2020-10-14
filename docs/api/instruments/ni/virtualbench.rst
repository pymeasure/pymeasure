################
NI Virtual Bench
################

*******************
General Information
*******************

The `armstrap/pyvirtualbench <https://github.com/armstrap/armstrap-pyvirtualbench>`_ 
Python wrapper for the VirtualBench C-API is required.
This Instrument driver only interfaces the pyvirtualbench Python wrapper.

********
Examples
********
To be documented. Check the examples in the pyvirtualbench repository to get an idea.

Simple Example to switch digital lines of the DIO module.

.. code-block:: python

    from pymeasure.instruments.ni import VirtualBench
    
    vb = VirtualBench(device_name='VB8012-3057E1C')
    line = 'dig/2'  # may be list of lines
    # initialize DIO module -> available via vb.dio
    vb.acquire_digital_input_output(line, reset=False)

    vb.dio.write(self.line, {True})
    sleep(1000)
    vb.dio.write(self.line, {False})

    vb.shutdown()

****************
Instrument Class
****************

.. autoclass:: pymeasure.instruments.ni.virtualbench.VirtualBench
    :members:
    :show-inheritance:
    :inherited-members:
    :exclude-members:

.. autoclass:: pymeasure.instruments.ni.virtualbench.VirtualBench_Direct
    :members:
    :show-inheritance:
    :inherited-members:
    :exclude-members:
