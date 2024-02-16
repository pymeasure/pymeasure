.. _connecting-to-an-instrument:

###########################
Connecting to an instrument
###########################

.. role:: python(code)
    :language: python

After following the :doc:`Quick Start <../quick_start>` section, you now have a working installation of PyMeasure. This section describes connecting to an instrument, using a Keithley 2400 SourceMeter as an example. To follow the tutorial, open a command prompt, IPython terminal, or Jupyter notebook.

First import the instrument of interest. ::

    from pymeasure.instruments.keithley import Keithley2400

Then construct an object by passing the VISA address. For this example we connect to the instrument over GPIB (using VISA) with an address of 4::

    sourcemeter = Keithley2400("GPIB::4")


.. note::

    Passing an appropriate resource string is the default method when creating pymeasure instruments.
    See the :ref:`adapters <adapters>` section below for more details.

    If you are not sure about the correct resource string identifying your instrument, you can run the :func:`pymeasure.instruments.list_resources` function to list all available resources::

        from pymeasure.instruments import list_resources
        list_resources()

    If you know the USB properties (vendor id, product id, serial numer) of the serial device, you can query for the VISA resource string::

        from pymeasure.instruments import find_serial_port
        resource_name = find_serial_port(vendor_id=15, product_id=0x12e5, serial_number="sn56X")

For instruments with standard SCPI commands, an :code:`id` property will return the results of a :code:`*IDN?` SCPI command, identifying the instrument. ::

    sourcemeter.id

This is equivalent to manually calling the SCPI command. ::

    sourcemeter.ask("*IDN?")

Here the :code:`ask` method writes the SCPI command, reads the result, and returns that result. This is further equivalent to calling the methods below. ::

    sourcemeter.write("*IDN?")
    sourcemeter.read()

This example illustrates that the top-level methods like :code:`id` are really composed of many lower-level methods. Both can be called depending on the operation that is desired. PyMeasure hides the complexity of these lower-level operations, so you can focus on the bigger picture.

Instruments are also equipped to be used in a :code:`with` statement. ::

    with Keithley2400("GPIB::4") as sourcemeter:
        sourcemeter.id

When the :code:`with`-block is exited, the :code:`shutdown` method of the instrument will be called, turning the system into a safe state. ::

    with Keithley2400("GPIB::4") as sourcemeter:
        sourcemeter.isShutdown == False
    sourcemeter.isShutdown == True

.. _adapters:

Using adapters
==============

PyMeasure supports a number of adapters, which are responsible for communicating with the underlying hardware.
In the example above, we passed the string "GPIB::4" when constructing the instrument.
By default this constructs a VISAAdapter (our most popular, default adapter) to connect to the instrument using VISA.
Passing a string (or integer in case of GPIB) is by far the most typical way to create pymeasure instruments.

Sometimes, you might need to go beyond the usual setup, which is also possible.
Instead of passing a string, you could equally pass an adapter object. ::

    from pymeasure.adapters import VISAAdapter

    adapter = VISAAdapter("GPIB::4")
    sourcemeter = Keithely2400(adapter)

To instead use a Prologix GPIB device connected on :code:`/dev/ttyUSB0` (proper permissions are needed in Linux, see :class:`PrologixAdapter <pymeasure.adapters.PrologixAdapter>`), the adapter is constructed in a similar way.
The Prologix adapter can be shared by many instruments.
Therefore, new :class:`PrologixAdapter <pymeasure.adapters.PrologixAdapter>` instances with different GPIB addresses can be generated from an already existing instance. ::

    from pymeasure.adapters import PrologixAdapter

    adapter = PrologixAdapter('ASRL/dev/ttyUSB0::INSTR', address=7)
    sourcemeter = Keithley2400(adapter)  # at GPIB address 7
    multimeter = Keithley2000(adapter.gpib(9))  # at GPIB address 9

Some equipment may require the vxi-11 protocol for communication. An example would be a Agilent E5810B ethernet to GPIB bridge.
To use this type equipment the python-vxi11 library has to be installed which is part of the extras package requirements. ::

   from pymeasure.adapters import VXI11Adapter
   from pymeasure.instruments import Instrument

   adapter = VXI11Adapter("TCPIP::192.168.0.100::inst0::INSTR")
   instr = Instrument(adapter, "my_instrument")

.. _connection_settings:

Modifying connection settings
=============================

Sometimes you want to tweak the connection settings when talking to a device.
This might be because you have a non-standard device or connection, or are troubleshooting why a device does not reply.

When using a string or integer to connect to an instrument, a :py:class:`~pymeasure.adapters.VISAAdapter` is used internally.
Additional settings need to be passed in as keyword arguments.
For example, to use a fast baud rate on a quick connection when connecting to the Keithely2400 as above, do ::

    sourcemeter = Keithley2400("ASRL2", timeout=500, baud_rate=115200)

This overrides any defaults that may be defined for the instrument, either generally valid ones like ``timeout`` or interface-specific ones like ``baud_rate``.

If you use an invalid argument, either misspelled or not valid for the chosen interface, an exception will be raised.

When using a separately-created Adapter instance, you define any custom settings when creating the adapter. Any keyword arguments passed in are discarded.

----

The above examples illustrate different methods for communicating with instruments, using adapters to keep instrument code independent from the communication protocols. Next we present the methods for setting up measurements.
