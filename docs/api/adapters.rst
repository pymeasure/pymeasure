##################
pymeasure.adapters
##################

The adapter classes allow the instruments to be independent of the communication method used.

Adapters for specific instruments should be grouped in an :code:`adapters.py` file in the corresponding manufacturer's folder of :mod:`pymeasure.instruments </api/instruments/index>`. For example, the adapter for communicating with LakeShore instruments over USB, :class:`LakeShoreUSBAdapter <pymeasure.instruments.lakeshore.LakeShoreUSBAdapter>`, is found in :mod:`pymeasure.instruments.lakeshore.adapters`.

==================
Adapter base class
==================

.. autoclass:: pymeasure.adapters.Adapter
    :members:
    :undoc-members:

============
VISA adapter
============

.. autoclass:: pymeasure.adapters.VISAAdapter
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

==============
Serial adapter
==============

.. autoclass:: pymeasure.adapters.SerialAdapter
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:
    :private-members: _format_binary_values

================
Prologix adapter
================

.. autoclass:: pymeasure.adapters.PrologixAdapter
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:
    :private-members: _format_binary_values

==============
VXI-11 adapter
==============

.. autoclass:: pymeasure.adapters.VXI11Adapter
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance: 

==============
Telnet adapter
==============

.. autoclass:: pymeasure.adapters.TelnetAdapter
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

============
Fake adapter
============

.. autoclass:: pymeasure.adapters.FakeAdapter
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:
