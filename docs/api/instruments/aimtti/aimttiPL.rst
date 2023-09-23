.. _aimtti-landing-page:

#############################################
Aim-TTI PL Series Power Supplies
#############################################

.. autoclass:: pymeasure.instruments.aimtti.aimttiPL.PLBase
    :members:
    :show-inheritance:

.. autoclass:: pymeasure.instruments.aimtti.aimttiPL.PLChannel
    :members:
    :show-inheritance:

.. For instruments with channels, we explicitly add an autoattribute with no-value
.. to avoid "= <...ChannelCreator object>" in the rendered documentation
.. All explicitly documented members are excluded so that there is no duplication,
.. but we still get docs for all members that are not explicitly enumerated.

.. autoclass:: pymeasure.instruments.aimtti.aimttiPL.PL068P
    :members:
    :exclude-members: ch_1
    :undoc-members:
    :show-inheritance:

    .. autoattribute:: ch_1
       :no-value:

.. autoclass:: pymeasure.instruments.aimtti.aimttiPL.PL155P
    :members:
    :exclude-members: ch_1
    :undoc-members:
    :show-inheritance:

    .. autoattribute:: ch_1
       :no-value:

.. autoclass:: pymeasure.instruments.aimtti.aimttiPL.PL303P
    :members:
    :exclude-members: ch_1
    :undoc-members:
    :show-inheritance:

    .. autoattribute:: ch_1
       :no-value:

.. autoclass:: pymeasure.instruments.aimtti.aimttiPL.PL601P
    :members:
    :exclude-members: ch_1
    :undoc-members:
    :show-inheritance:

    .. autoattribute:: ch_1
       :no-value:

.. autoclass:: pymeasure.instruments.aimtti.aimttiPL.PL303QMDP
    :members:
    :exclude-members: ch_1, ch_2
    :undoc-members:
    :show-inheritance:

    .. autoattribute:: ch_1
       :no-value:

    .. autoattribute:: ch_2
       :no-value:

.. autoclass:: pymeasure.instruments.aimtti.aimttiPL.PL303QMTP
    :members:
    :exclude-members: ch_1, ch_2, ch_3
    :undoc-members:
    :show-inheritance:

    .. autoattribute:: ch_1
       :no-value:

    .. autoattribute:: ch_2
       :no-value:

    .. autoattribute:: ch_3
       :no-value:
