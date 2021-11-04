###########################
Connecting to an instrument
###########################

.. role:: python(code)
    :language: python

After following the :doc:`Quick Start <../quick_start>` section, you now have a working installation of PyMeasure. This section describes connecting to an instrument, using a Keithley 2400 SourceMeter as an example. To follow the tutorial, open a command prompt, IPython terminal, or Jupyter notebook.

First import the instrument of interest. ::

    from pymeasure.instruments.keithley import Keithley2400

Then construct an object by passing the GPIB address. For this example we connect to the instrument over GPIB (using VISA) with an address of 4. See the :ref:`adapters <adapters>` section below for more details. ::

    sourcemeter = Keithley2400("GPIB::4")

For instruments with standard SCPI commands, an :code:`id` property will return the results of a :code:`*IDN?` SCPI command, identifying the instrument. ::

    sourcemeter.id

This is equivalent to manually calling the SCPI command. ::

    sourcemeter.ask("*IDN?")

Here the :code:`ask` method writes the SCPI command, reads the result, and returns that result. This is further equivalent to calling the methods below. ::

    sourcemeter.write("*IDN?")
    sourcemeter.read()

This example illustrates that the top-level methods like :code:`id` are really composed of many lower-level methods. Both can be called depending on the operation that is desired. PyMeasure hides the complexity of these lower-level operations, so you can focus on the bigger picture.

.. _adapters:

Using adapters
==============

PyMeasure supports a number of adapters, which are responsible for communicating with the underlying hardware. In the example above, we passed the string "GPIB::4" when constructing the instrument. By default this constructs a VISAAdapter class to connect to the instrument using VISA. Instead of passing a string, we could equally pass an adapter object. ::

    from pymeasure.adapters import VISAAdapter

    adapter = VISAAdapter("GPIB::4")
    sourcemeter = Keithely2400(adapter)

To instead use a Prologix GPIB device connected on :code:`/dev/ttyUSB0` (proper permissions are needed in Linux, see :class:`PrologixAdapter <pymeasure.adapters.PrologixAdapter>`), the adapter is constructed in a similar way. Unlike the VISA adapter which is specific to each instrument, the Prologix adapter can be shared by many instruments. Therefore, they are addressed separately based on the GPIB address number when passing the adapter into the instrument construction. ::

    from pymeasure.adapters import PrologixAdapter

    adapter = PrologixAdapter('/dev/ttyUSB0')
    sourcemeter = Keithley2400(adapter.gpib(4))

For instruments using serial communication that have particular settings that need to be matched, a custom :class:`Adapter <pymeasure.adapters.Adapter>` sub-class can be made. For example, the LakeShore 425 Gaussmeter connects via USB, but uses particular serial communication settings. Therefore, a :class:`LakeShoreUSBAdapter <pymeasure.instruments.lakeshore.LakeShoreUSBAdapter>` class enables these requirements in the background. ::

    from pymeasure.instruments.lakeshore import LakeShore425

    gaussmeter = LakeShore425('/dev/lakeshore425')

Behind the scenes the :code:`/dev/lakeshore425` port is passed to the :class:`LakeShoreUSBAdapter <pymeasure.instruments.lakeshore.LakeShoreUSBAdapter>`.

Some equipment may require the vxi-11 protocol for communication. An example would be a Agilent E5810B ethernet to GPIB bridge.
To use this type equipment the python-vxi11 library has to be installed which is part of the extras package requirements. ::

   from pymeasure.adapters import VXI11Adapter
   from pymeasure.instruments import Instrument

   adapter = VXI11Adapter("TCPIP::192.168.0.100::inst0::INSTR")
   instr = Instrument(adapter, "my_instrument")

The above examples illustrate different methods for communicating with instruments, using adapters to keep instrument code independent from the communication protocols. Next we present the methods for setting up measurements.
