#########################################
DP-Series Step Motor Controller (DPY50601/DPE25601)
#########################################

The DPSeriesMotorController class implements a base driver class for Anaheim-Automation DP Series stepper motor controllers. There are many controllers sold in this series, all of which implement the same core command set. Some controllers, like the DPY50601 implement additional functionality that is not included in this driver. If these additional features are desired, they should be implemented in a subclass.

.. autoclass:: pymeasure.instruments.anaheimautomation.DPSeriesMotorController
    :members:
    :show-inheritance: