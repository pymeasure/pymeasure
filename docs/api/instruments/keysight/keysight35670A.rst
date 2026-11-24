##########################################
Keysight 35670A Dynamic Signal Analyzer
##########################################

.. code-block:: python

    from pymeasure.instruments.keysight import Keysight35670A

The Keysight/Agilent/HP 35670A driver provides a dynamic signal analyzer API for
measurement and configuration workflows.
It supports 2 or 4 input channels depending on option AY6, trace boxes 1..4,
source-output control, and block transfer helpers for binary/definite-block
data paths.
Destructive memory, system, and program operations require explicit
confirmation arguments.

.. autoclass:: pymeasure.instruments.keysight.Keysight35670A
    :members:
    :show-inheritance:
    :inherited-members:

.. autoclass:: pymeasure.instruments.keysight.keysight35670A.Keysight35670AInputChannel
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.keysight.keysight35670A.Keysight35670ASenseWindow
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.keysight.keysight35670A.Keysight35670ADisplayWindow
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.keysight.keysight35670A.Keysight35670AWindow
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.keysight.keysight35670A.Keysight35670AOrderTrack
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.keysight.keysight35670A.Keysight35670ATrace
    :members:
    :show-inheritance:
