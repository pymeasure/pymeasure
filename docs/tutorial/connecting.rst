###########################
Connecting to an instrument
###########################

.. role:: python(code)
    :language: python

After following the :doc:`Getting Started <../getting_started>` section, you now have a working installation of PyMeasure. This section describes connecting to an instrument, using a Keithley 2400 SourceMeter as an example. To follow the tutorial, open a command prompt, IPython terminal, or Jupyter notebook.

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

Many instruments will work with the VISA library. However, there are others that require a more advanced configuration to connect to them.