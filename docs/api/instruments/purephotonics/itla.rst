#####################################
OIF-ITLA-MSA tunable laser base class
#####################################

The :class:`~pymeasure.instruments.purephotonics.itla.ITLA` class implements the register protocol and the standard registers of the OIF Integrable Tunable Laser Assembly Multi Source Agreement (OIF-ITLA-MSA).
It serves as base class for ITLA compliant lasers, e.g. the :class:`~pymeasure.instruments.purephotonics.PPCL300`.

.. autoclass:: pymeasure.instruments.purephotonics.itla.ITLA
    :members:
    :show-inheritance:

Status and errors
=================

.. autoclass:: pymeasure.instruments.purephotonics.itla.FatalStatus
    :members:
    :undoc-members:

.. autoclass:: pymeasure.instruments.purephotonics.itla.WarningStatus
    :members:
    :undoc-members:

.. autoclass:: pymeasure.instruments.purephotonics.itla.ITLAStatus
    :members:
    :undoc-members:

.. autoclass:: pymeasure.instruments.purephotonics.itla.ITLAError
    :members:
    :undoc-members:

.. autoexception:: pymeasure.instruments.purephotonics.itla.ITLAExecutionError
