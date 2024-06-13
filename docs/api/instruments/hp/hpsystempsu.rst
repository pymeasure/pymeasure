################################
HP System Power Supplies HP663XA
################################

Currently supported models are:

=====  ========  =========  =====
Model  Voltage   Current    Power
=====  ========  =========  =====
6632A  0..20 V   0..5.0 A   100 W
6633A  0..50 V   0..2.5 A   100 W
6634A  0..100 V  0..1.0 A   100 W
=====  ========  =========  =====

*Note:*
    * The multi-channel system power supplies HP 6621A, 6622A, 6623A, 6624A, 6625A, 6626A, 6627A & 6628A 
      share some of the command syntax and could probably be incorporated in this implementation
    
    * The B-version of these models (6632B, 6633B & 6634B) are SPCI-compliant and 
      could be implemented in a similar manner
    
    
.. autoclass:: pymeasure.instruments.hp.HP6632A
    :members:
    :show-inheritance:
    
.. autoclass:: pymeasure.instruments.hp.HP6633A
    :members:
    :show-inheritance:
    
.. autoclass:: pymeasure.instruments.hp.HP6634A
    :members:
    :show-inheritance:
