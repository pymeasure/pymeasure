#######################
Rigol Oscilloscope Base
#######################

The shared Rigol oscilloscope classes collect SCPI commands whose syntax and
semantics are common to the supported Rigol oscilloscope families. Instrument
drivers inherit from these classes and provide model-dependent validators and
value sets through dynamic properties.

.. autoclass:: pymeasure.instruments.rigol.RigolOscilloscope
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_oscilloscope.RigolOscilloscopeChannel
    :members:
    :show-inheritance:
