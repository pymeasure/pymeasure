##############################
R&S NGPx Power Supply Family
##############################

The :class:`~pymeasure.instruments.rohdeschwarz.ngpx.NGPx` class implements
support for the Rohde & Schwarz NGPx programmable power-supply family
(NGP802, NGP804, NGP812, NGP814).
The model is detected automatically from the ``*IDN?`` response at construction
time, and the correct number of channels is created dynamically.

Basic usage
===========

.. code-block:: python

    from pymeasure.instruments.rohdeschwarz import NGPx

    psu = NGPx("TCPIP0::192.168.1.10::INSTR")

    psu.ch1.voltage_setpoint = 5.0
    psu.ch1.current_limit = 1.0
    psu.ch1.sense = "EXT"          # remote sense
    psu.ch1.output = True

    print(psu.ch1.voltage, psu.ch1.current)

    psu.ch1.output = False
    psu.shutdown()

Shared ResourceManager
=======================

When managing multiple instruments with a specific VISA library (e.g. NI-VISA
vs RS-VISA), create one :class:`pyvisa.ResourceManager` up front and pass it
as the ``adapter`` argument.
The instrument will **not** close the shared manager when it shuts down.

.. code-block:: python

    import pyvisa
    from pymeasure.instruments.rohdeschwarz import NGPx

    rm = pyvisa.ResourceManager("C:/WINDOWS/system32/visa64.dll")

    psu1 = NGPx(rm, "TCPIP0::192.168.1.10::INSTR")
    psu2 = NGPx(rm, "TCPIP0::192.168.1.11::INSTR")

    # ... use instruments ...

    psu1.shutdown()
    psu2.shutdown()
    rm.close()          # close only once, after all instruments

Reconnection after network dropout
===================================

Call :meth:`~pymeasure.instruments.rohdeschwarz.ngpx.NGPx.open` to reopen
the connection without reinstantiating the instrument object.

.. code-block:: python

    psu.close()
    # ... wait for network recovery ...
    psu.open()
    psu.ch1.voltage_setpoint = 5.0

.. admonition:: Migration from the R&S internal fork

    If you previously used the internal R&S fork of pymeasure, the API is
    kept as close as possible to minimize migration effort.

    All property and method names —
    ``ch1`` … ``ch4``, ``sense``, ``output``, ``output_general``,
    ``set2local``, ``set2remote``, ``get_device_info``,
    ``check_is_dev_supported``, ``clear_reset`` — are identical.

PwrChannel
==========

.. autoclass:: pymeasure.instruments.rohdeschwarz.ngpx.PwrChannel
    :members:
    :show-inheritance:

NGPx
====

.. autoclass:: pymeasure.instruments.rohdeschwarz.ngpx.NGPx
    :members:
    :show-inheritance:
