##################################
NI Virtual Bench
##################################

**********************************************
General Information
**********************************************

The `armstrap/pyvirtualbench <https://github.com/armstrap/armstrap-pyvirtualbench>`_ 
Python wrapper for the VirtualBench C-API is required.
This Instrument driver only interfaces the pyvirtualbench Python wrapper.

This wrapper was tested using
this `pyvirtualbench fork <https://github.com/moritzj29/armstrap-pyvirtualbench>`_, which
includes some bug-fixes and a more up-to-date driver. 
A pull request to the original
repository is pending, but it appears to be no longer maintained.

**********************************************
Examples
**********************************************
to be documented. Check the examples in the pyvirtualbench repository to get an idea.

**********************************************
Instrument Class
**********************************************

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
