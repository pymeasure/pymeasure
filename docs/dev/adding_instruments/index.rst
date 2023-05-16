.. _adding-instruments:

##################
Adding instruments
##################

You can make a significant contribution to PyMeasure by adding a new instrument to the :code:`pymeasure.instruments` package.
Even adding an instrument with a few features can help get the ball rolling, since its likely that others are interested in the same instrument.

Before getting started, become familiar with the :doc:`contributing work-flow <../contribute>` for PyMeasure, which steps through the process of adding a new feature (like an instrument) to the development version of the source code.

Pymeasure instruments communicate with the devices via transfer of bytes or ASCII characters encoded as bytes.
For ease of use, we have :ref:`property creators <properties>` to easily create python properties. Similarly, we have creators to easily implement :ref:`channels <channels>`. Finally, for a smoother implementation process and better maintenance, we have :ref:`tests <tests>`.

The following sections will describe how to lay out your instrument code.



.. toctree::
   :maxdepth: 2

   instrument
   properties
   channels
   advanced_communication
   tests
   solutions
