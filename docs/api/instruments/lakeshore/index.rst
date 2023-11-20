.. module:: pymeasure.instruments.lakeshore

#####################
Lake Shore Cryogenics
#####################

This section contains specific documentation on the Lake Shore Cryogenics instruments that are implemented. If you are interested in an instrument not included, please consider :doc:`adding the instrument </dev/adding_instruments/index>`.

.. toctree::
   :maxdepth: 2

   lakeshore211
   lakeshore224
   lakeshore331
   lakeshore421
   lakeshore425

.. _LakeShoreChannels:

LakeShore Channel Classes
--------------------------

Several Lakeshore instruments are channel based and make use of the :ref:`Channel Interface <channels>`. For temperature monitoring and controller instruments the
following common :class:`Channel Classes <pymeasure.instruments.Channel>` are utilized:

.. autoclass:: pymeasure.instruments.lakeshore.lakeshore_base.LakeShoreTemperatureChannel
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.lakeshore.lakeshore_base.LakeShoreHeaterChannel
    :members:
    :show-inheritance:
