##################
pymeasure.adapters
##################

The adapter classes allow the instruments to be independent of the communication method used.
The instrument implementation takes care of any potential quirks in its communication protocol (see :ref:`advanced_communication_protocols`), and the adapter takes care of the details of the over-the-wire communication with the hardware device.
In the vast majority of cases, it will be sufficient to pass a connection string or integer to the instrument (see :ref:`connecting-to-an-instrument`), which uses the :class:`pymeasure.adapters.VISAAdapter` in the background.

==================
Adapter base class
==================

All adapters expose a :attr:`~pymeasure.adapters.Adapter.timeout` property.
Its value is in the unit native to the adapter's connection: milliseconds for VISA adapters and
seconds for serial adapters.

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

Driver code that uses PyVISA-specific connection members types the connection with the
:func:`~pymeasure.adapters.visa.visa_resource` helper.
It is a typing-only cast and performs no runtime check.

.. autofunction:: pymeasure.adapters.visa.visa_resource

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

=============
Test adapters
=============

These pieces are useful when writing tests.

.. automodule:: pymeasure.test
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pymeasure.adapters.ProtocolAdapter
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pymeasure.adapters.FakeAdapter
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

.. autoclass:: pymeasure.generator.Generator
    :members:
