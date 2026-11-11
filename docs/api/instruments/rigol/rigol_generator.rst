#######################
Rigol Generator Base
#######################

The shared Rigol generator classes collect SCPI commands whose syntax and
semantics are common to the supported Rigol generator families. Instrument
drivers inherit from these classes and provide model-dependent validators and
value sets through dynamic properties.

.. autoclass:: pymeasure.instruments.rigol.RigolGenerator
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.rigol.rigol_generator.RigolGeneratorChannel
    :members:
    :show-inheritance:
    