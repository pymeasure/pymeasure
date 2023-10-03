.. module:: pymeasure.instruments.teledyne

#########
Teledyne
#########

This section contains specific documentation on the Teledyne instruments that are implemented. If you are interested in an instrument not included, please consider :doc:`adding the instrument </dev/adding_instruments/index>`.

If the instrument you are looking for is not here, also check :doc:`LeCroy<../lecroy/index>` for older instruments. 

.. toctree::
   :maxdepth: 1

   teledyneT3AFG


There are shared base classes for Teledyne oscilloscopes.
If your device is missing, the base class might already work well enough.
If adding a new device, these base classes should limit the amount of new code necessary.

.. toctree::
   :maxdepth: 2

   teledyne_bases
