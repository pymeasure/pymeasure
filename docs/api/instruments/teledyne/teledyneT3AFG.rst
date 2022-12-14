##############################################
Teledyne T3AFG Arbitrary Waveform Generator
##############################################

*******************
General Information
*******************

Initial implementation is aimed at T3AFG80 and is very limited even for target device.

Some commands may fail silently or with error on T3AFG5 or T3AFG10. Features avalible on fancier models are not implemented.

Eventually this may be a good use-case for a base class and inheritance for other models.

****************
Instrument Class
****************

.. autoclass:: pymeasure.instruments.teledyne.teledyneT3AFG
    :members:
    :show-inheritance:
    :inherited-members:
