##################
pymeasure.adapters
##################

The adapter classes allow the instruments to be independent of the communication method used. The classes can be directly imported from :code:`pymeasure.adapters` for convenience.

Adapters for specific instruments should be grouped in a :code:`adapters.py` file in the corresponding manufacturer's folder of :class:`pymeasure.instruments`.

==================
Adapter base class
==================

.. autoclass:: pymeasure.adapters.adapter.Adapter
   :members:

============
Fake adapter
============

.. autoclass:: pymeasure.adapters.adapter.FakeAdapter

==============
Serial adapter
==============

.. autoclass:: pymeasure.adapters.serial.SerialAdapter
   :members:

================
Prologix adapter
================

.. autoclass:: pymeasure.adapters.prologix.PrologixAdapter
   :members:

============
VISA adapter
============

.. autoclass:: pymeasure.adapters.visa.VISAAdapter
   :members: