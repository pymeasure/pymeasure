#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging

from pymeasure.instruments import SCPIMixin, Instrument

from pymeasure.instruments.validators import (strict_discrete_set,
                                              strict_range,
                                              joined_validators
                                              )

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class BatteryMixin:
    """A class representing the B2983/7 battery functions."""

    battery_level = Instrument.measurement(
        ":SYST:BATT?",
        """Get the percentage of the remaining battery capacity (int).""",
        cast=int,
    )

    battery_cycles = Instrument.measurement(
        ":SYST:BATT:CYCL?",
        """Get the battery cycle count (int).""",
        cast=int,
    )

    battery_selftest_passed = Instrument.measurement(
        ":SYST:BATT:TEST?",
        """Get the battery self-test result (bool).""",
        map_values=True,
        values={True: 0, False: 1}  # 0: passed, 1: failed
    )


class AgilentB2981(SCPIMixin, Instrument):
    """A class representing the Agilent/Keysight B2981A/B.

    The B2981 is a Femto/Picoammeter."""

    def __init__(self, adapter,
                 name="Agilent/Keysight B2980A/B series",
                 **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    input_enabled = Instrument.control(
        ":INP?", ":INP %d",
        """Control the instrument input relay (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
        )

    zero_corrected = Instrument.control(
        ":INP:ZCOR?", ":INP:ZCOR %d",
        """Control the zero correction function (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
        )

    measure = Instrument.measurement(
        ":MEAS?",
        """Measure the defined parameter(s) with a spot measurement.

        :return: float or list of float
        """
        )

    current = Instrument.measurement(
        ":MEAS:CURR?",
        """Measure current with a spot measurement in Amps.

        :return: float
        """
        )

    current_range = Instrument.control(
        ":CURR:RANG?", ":CURR:RANG %s",
        """Control the range for the current measurement in Amps.

        :type: - float, strictly from ``2E-12`` to ``20E-3`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``, ``UP``, ``DOWN``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF', 'UP', 'DOWN'], [2E-12, 20E-3]]
        )

    interlock_enabled = Instrument.measurement(
        ":SYST:INT:TRIP?",
        """Get the interlock status (bool).""",
        map_values=True,
        values={True: 0, False: 1}
        )

    data_buffer_size = Instrument.measurement(
        ":SYST:DATA:QUAN?",
        """Get the data buffer size (int).""",
        cast=int
        )

##################
# Trigger system #
##################

    def abort(self):
        """Abort the all actions."""
        self.write(":ABOR:ALL")

    def arm(self):
        """Send an immediate arm trigger for all actions.

        When the status of all actions is initiated, the arm trigger
        causes a layer change from arm to trigger.
        """
        self.write(":ARM:ALL")

    def init(self):
        """Initiate a trigger for all actions."""
        self.write(":INIT:ALL")

    def abort_acquisition(self):
        """Abort action 'ACQuire'."""
        self.write(":ABOR:ACQ")

    def arm_acquisition(self):
        """Send an immediate arm trigger for action 'ACQuire'.

        When the status of action 'ACQuire' is initiated, the arm trigger
        causes a layer change from arm to trigger.
        """
        self.write(":ARM:ACQ")

    def init_acquisition(self):
        """Initiate a trigger for action 'ACQuire'."""
        self.write(":INIT:ACQ")

###########################################
# Trigger properties for action 'ACQuire' #
###########################################

    arm_acquisition_bypass_once_enabled = Instrument.control(
        ":ARM:ACQ:BYP?", ":ARM:ACQ:BYP %s",
        """Control the bypass for the event detector in the arm layer for action 'ACQuire' (bool).
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'ONCE', False: 'OFF'}
        )

    arm_acquisition_count = Instrument.control(
        ":ARM:ACQ:COUN?", ":ARM:ACQ:COUN %s",
        """Control the arm trigger count for action 'ACQuire'.

        :type: - int, strictly from ``1`` to ``100000`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``, ``INF``

        ``INF`` is equivalent to ``2147483647``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF', 'INF', 2147483647], [1, 100000]]
        )

    arm_acquisition_delay = Instrument.control(
        ":ARM:ACQ:DEL?", ":ARM:ACQ:DEL %s",
        """Control the arm trigger delay for action 'ACQuire' in seconds.

        :type: - float, strictly from ``0`` to ``1E5`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF'], [0, 100000]]
        )

    arm_acquisition_source = Instrument.control(
        ":ARM:ACQ:SOUR?", ":ARM:ACQ:SOUR %s",
        """Control the arm trigger source for action 'ACQuire'.

        :type: str, strictly in ``AINT``, ``BUS``, ``TIM``,
               ``INT1``, ``INT2``, ``LAN``, ``TIN``,
               ``EXT1`` to ``EXT7``

        - ``AINT`` automatically selects the arm source most suitable for the
          present operating mode by using internal algorithms.
        - ``BUS`` selects the remote interface trigger command such as the group
          execute trigger (GET) and the TRG command.
        - ``TIM`` selects a signal internally generated every interval set by the
          arm_timer command.
        - ``INT1`` and ``INT2`` selects a signal from the internal bus 1 or 2.
        - ``LAN`` selects the LXI trigger specified by the arm_source_lan_id command.
        - ``EXT1`` to ``EXT7`` selects a signal from the GPIO pin n, which is an input port of the
          Digital I/O D-sub connector on the rear panel. n = 1 to 7.
        - ``TIN`` selects the BNC Trigger In.
        """,
        validator=strict_discrete_set,
        values=['AINT', 'BUS', 'TIM', 'INT1', 'INT2', 'LAN', 'TIN',
                'EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7']
        )

    arm_acquisition_source_lan_id = Instrument.control(
        ":ARM:ACQ:SOUR:LAN?", ":ARM:ACQ:SOUR:LAN %s",
        """Control the source for LAN arm triggers for action 'ACQuire'.

        :type: str, strictly from ``LAN0`` to ``LAN7``
        """,
        validator=strict_discrete_set,
        values=['LAN0', 'LAN1', 'LAN2', 'LAN3', 'LAN4', 'LAN5', 'LAN6', 'LAN7']
        )

    arm_acquisition_timer = Instrument.control(
        ":ARM:ACQ:TIM?", ":ARM:ACQ:TIM %s",
        """Control the timer interval of the arm trigger source for action 'ACQuire' in seconds.

        :type: - float, strictly from ``1E-5`` to ``1E5``
               - str, strictly in ``MIN``, ``MAX``, ``DEF``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF'], [1E-5, 1E5]]
        )

    arm_acquisition_output_signal = Instrument.control(
        ":ARM:ACQ:TOUT:SIGN?", ":ARM:ACQ:TOUT:SIGN %s",
        """Control the arm trigger output for action 'ACQuire'.

        :type: str, strictly in ``INT1``, ``INT2``, ``LAN``, ``TOUT``,
               ``EXT1`` to ``EXT7``

        - ``INT1`` or ``INT2`` selects the internal bus 1 or 2.
        - ``LAN`` selects a LAN port.
        - ``EXT1`` to ``EXT7`` selects the GPIO pin n, which is an output port of the Digital I/O
          D-sub connector on the rear panel. n = 1 to 7.
        - ``TOUT`` selects the BNC Trigger Out.

        It is for the status change between the idle state and the arm layer.
        """,
        validator=strict_discrete_set,
        values=['INT1', 'INT2', 'LAN', 'TOUT',
                'EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7']
        )

    arm_acquisition_output_enabled = Instrument.control(
        ":ARM:ACQ:TOUT?", ":ARM:ACQ:TOUT %s",
        """Control the arm trigger output for action 'ACQuire' (bool).

        It is for the status change between the idle state and the arm layer.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
        )

    trigger_acquisition_is_idle = Instrument.measurement(
        ":IDLE:ACQ?",
        """Get the idle status of action 'ACQuire' (bool).

        The command waits until the status is changed to idle.
        """,
        map_values=True,
        values={True: 1, False: 0}
        )

    trigger_acquisition_bypass_once_enabled = Instrument.control(
        ":TRIG:ACQ:BYP?", ":TRIG:ACQ:BYP %s",
        """
        Control the bypass for the event detector in the trigger layer for action 'ACQuire' (bool).
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'ONCE', False: 'OFF'}
        )

    trigger_acquisition_count = Instrument.control(
        ":TRIG:ACQ:COUN?", ":TRIG:ACQ:COUN %s",
        """Control the trigger count for action 'ACQuire'.

        :type: - int, strictly from ``1`` to ``100000`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``, ``INF``

        ``INF`` is equivalent to ``2147483647``.
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF', 'INF', 2147483647], [1, 100000]]
        )

    trigger_acquisition_delay = Instrument.control(
        ":TRIG:ACQ:DEL?", ":TRIG:ACQ:DEL %s",
        """Control the trigger delay for action 'ACQuire' in seconds.

        :type: - float, strictly from ``0`` to ``1E5`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF'], [0, 100000]]
        )

    trigger_acquisition_source = Instrument.control(
        ":TRIG:ACQ:SOUR?", ":TRIG:ACQ:SOUR %s",
        """Control the trigger source for action 'ACQuire'.

        :type: str, strictly in ``AINT``, ``BUS``, ``TIM``, ``INT1``, ``INT2``, ``LAN``, ``TIN``,
               ``EXT1`` to ``EXT7``

        - ``AINT`` automatically selects the trigger source most suitable for the
          present operating mode by using internal algorithms.
        - ``BUS`` selects the remote interface trigger command such as the group
          execute trigger (GET) and the TRG command.
        - ``TIM`` selects a signal internally generated every interval set by the
          :attr:`trigger_acquisition_timer`.
        - ``INT1`` and ``INT2`` selects a signal from the internal bus 1 or 2.
        - ``LAN`` selects the LXI trigger specified by :attr:`trigger_acquisition_source_lan_id`.
        - ``EXT1`` to ``EXT7`` selects a signal from the GPIO pin n, which is an input port of the
          Digital I/O D-sub connector on the rear panel. n = 1 to 7.
        - ``TIN`` selects the BNC Trigger In.
        """,
        validator=strict_discrete_set,
        values=['AINT', 'BUS', 'TIM', 'INT1', 'INT2', 'LAN', 'TIN',
                'EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7']
        )

    trigger_acquisition_source_lan_id = Instrument.control(
        ":TRIG:ACQ:SOUR:LAN?", ":TRIG:ACQ:SOUR:LAN %s",
        """Control the source for LAN triggers for action 'ACQuire'.

        :type: str, strictly from ``LAN0`` to ``LAN7``
        """,
        validator=strict_discrete_set,
        values=['LAN0', 'LAN1', 'LAN2', 'LAN3', 'LAN4', 'LAN5', 'LAN6', 'LAN7']
        )

    trigger_acquisition_timer = Instrument.control(
        ":TRIG:ACQ:TIM?", ":TRIG:ACQ:TIM %s",
        """Control the timer interval of the trigger source for action 'ACQuire' in seconds.

        :type: - float, strictly from ``1E-5`` to ``1E5`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF'], [1E-5, 1E5]]
        )

    trigger_acquisition_output_signal = Instrument.control(
        ":TRIG:ACQ:TOUT:SIGN?", ":TRIG:ACQ:TOUT:SIGN %s",
        """Control the trigger signal output for action 'ACQuire'.

        :type: str, strictly in ``INT1``, ``INT2``, ``LAN``, ``TOUT``,
               ``EXT1`` to ``EXT7``

        - ``INT1`` and ``INT2`` selects the internal bus 1 or 2.
        - ``LAN`` selects a LAN port.
        - ``EXT1`` to ``EXT7`` selects the GPIO pin n, which is an output port of the Digital I/O
          D-sub connector on the rear panel. n = 1 to 7.
        - ``TOUT``: selects the BNC Trigger Out.

        It is for the status change between the idle state and the
        trigger layer.
        """,
        validator=strict_discrete_set,
        values=['INT1', 'INT2', 'LAN', 'TOUT',
                'EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7']
        )

    trigger_acquisition_output_enabled = Instrument.control(
        ":TRIG:ACQ:TOUT?", ":TRIG:ACQ:TOUT %s",
        """Control the trigger output for action 'ACQuire' (bool).

        It is for the status change between the idle state
        and the trigger layer.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
        )

####################################
# Trigger setters for action 'ALL' #
####################################

    arm_all_bypass_once_enabled = Instrument.setting(
        ":ARM:ALL:BYP %s",
        """Set the bypass for the event detector in the arm layer for action 'ALL' (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'ONCE', False: 'OFF'}
        )

    arm_all_count = Instrument.setting(
        ":ARM:ALL:COUN %s",
        """Set the arm trigger counter for action 'ALL'.

        :type: - int, strictly from ``1`` to ``100000`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``, ``INF``

        ``INF`` is equivalent to ``2147483647``.
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF', 'INF', 2147483647], [1, 100000]]
        )

    arm_all_delay = Instrument.setting(
        ":ARM:ALL:DEL %s",
        """Set the arm trigger delay for action 'ALL' in seconds.

        :type: - float, strictly from ``0`` to ``1E5`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF'], [0, 100000]]
        )

    arm_all_source = Instrument.setting(
        ":ARM:ALL:SOUR %s",
        """Set the arm trigger source for action 'ALL'.

        :type: str, strictly in ``AINT``, ``BUS``, ``TIM``,
               ``INT1``, ``INT2``, ``LAN``, ``TIN``,
               ``EXT1`` to ``EXT7``

        - ``AINT`` automatically selects the arm source most suitable for the
          present operating mode by using internal algorithms.
        - ``BUS`` selects the remote interface trigger command such as the group
          execute trigger (GET) and the TRG command.
        - ``TIM`` selects a signal internally generated every interval set by
          attr:`arm_all_timer`.
        - ``INT1`` and ``INT2`` selects a signal from the internal bus 1 or 2.
        - ``LAN`` selects the LXI trigger specified by :attr:`arm_all_source_lan_id`.
        - ``EXT1`` to ``EXT7`` selects a signal from the GPIO pin n, which is an input port of the
          Digital I/O D-sub connector on the rear panel. n = 1 to 7.
        - ``TIN`` selects the BNC Trigger In.
        """,
        validator=strict_discrete_set,
        values=['AINT', 'BUS', 'TIM', 'INT1', 'INT2', 'LAN', 'TIN',
                'EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7']
        )

    arm_all_source_lan_id = Instrument.setting(
        ":ARM:ALL:SOUR:LAN %s",
        """Set the source for LAN arm triggers for action 'ALL'.

        :type: str, strictly from ``LAN0`` to ``LAN7``
        """,
        validator=strict_discrete_set,
        values=['LAN0', 'LAN1', 'LAN2', 'LAN3', 'LAN4', 'LAN5', 'LAN6', 'LAN7']
        )

    arm_all_timer = Instrument.setting(
        ":ARM:ALL:TIM %s",
        """Set the timer interval of the arm trigger source for action 'ALL' in seconds.

        :type: - float, strictly from ``1E-5`` to ``1E5`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF'], [1E-5, 1E5]]
        )

    arm_all_output_signal = Instrument.setting(
        ":ARM:ALL:TOUT:SIGN %s",
        """Set the arm trigger output for action 'ALL'.

        :type: str, strictly in ``INT1``, ``INT2``, ``LAN``, ``TOUT``,
                ``EXT1`` to ``EXT7``

        - ``INT1`` and ``INT2`` selects the internal bus 1 or 2.
        - ``LAN`` selects a LAN port.
        - ``EXT1`` to ``EXT7`` selects the GPIO pin n, which is an output port of the Digital I/O
          D-sub connector on the rear panel. n = 1 to 7.
        - ``TOUT`` selects the BNC Trigger Out.

        It is for the status change between the idle state and the arm layer.
        """,
        validator=strict_discrete_set,
        values=['INT1', 'INT2', 'LAN', 'TOUT',
                'EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7']
        )

    arm_all_output_enabled = Instrument.setting(
        ":ARM:ALL:TOUT %s",
        """Set the arm trigger output for action 'ALL' (bool).

        It is for the status change between the idle state
        and the arm layer.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
        )

    trigger_all_is_idle = Instrument.measurement(
        ":IDLE:ALL?",
        """Get the trigger idle status for action 'ALL' (bool).

        The command waits until the status is changed to idle.
        """,
        map_values=True,
        values={True: 1, False: 0}
        )

    trigger_all_bypass_once_enabled = Instrument.setting(
        ":TRIG:ALL:BYP %s",
        """Set the bypass for the event detector in the trigger layer for action 'ALL' (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'ONCE', False: 'OFF'}
        )

    trigger_all_count = Instrument.setting(
        ":TRIG:ALL:COUN %s",
        """Set the trigger count for action 'ALL'.

        :type: - int, strictly from ``1`` to ``100000`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``, ``INF``

        ``INF`` is equivalent to ``2147483647``.
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF', 'INF', 2147483647], [1, 100000]]
        )

    trigger_all_delay = Instrument.setting(
        ":TRIG:ALL:DEL %s",
        """Set the trigger delay for action 'ALL' in seconds.

        :type: - float, strictly from ``0`` to ``1E5`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF'], [0, 100000]]
        )

    trigger_all_source = Instrument.setting(
        ":TRIG:ALL:SOUR %s",
        """Set the trigger source for action 'ALL'.

        :type: str, strictly in ``AINT``, ``BUS``, ``TIM``,
               ``INT1``, ``INT2``, ``LAN``, ``TIN``,
               ``EXT1`` to ``EXT7``

        - ``AINT`` automatically selects the trigger source most suitable for the
          present operating mode by using internal algorithms.
        - ``BUS`` selects the remote interface trigger command such as the group
          execute trigger (GET) and the TRG command.
        - ``TIM`` selects a signal internally generated every interval set by
          :attr:`trigger_all_timer`.
        - ``INT1`` and ``INT2`` selects a signal from the internal bus 1 or 2.
        - ``LAN`` selects the LXI trigger specified by :attr:`trigger_all_source_lan_id`.
        - ``EXT1`` to ``EXT7`` selects a signal from the GPIO pin n, which is an input port of the
          Digital I/O D-sub connector on the rear panel. n = 1 to 7.
        - ``TIN`` selects the BNC Trigger In.
        """,
        validator=strict_discrete_set,
        values=['AINT', 'BUS', 'TIM', 'INT1', 'INT2', 'LAN', 'TIN',
                'EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7']
        )

    trigger_all_source_lan_id = Instrument.setting(
        ":TRIG:ALL:SOUR:LAN %s",
        """Set the source for LAN triggers for action 'ALL'.

        :type: str, strictly from ``LAN0`` to ``LAN7``
        """,
        validator=strict_discrete_set,
        values=['LAN0', 'LAN1', 'LAN2', 'LAN3', 'LAN4', 'LAN5', 'LAN6', 'LAN7']
        )

    trigger_all_timer = Instrument.setting(
        ":TRIG:ALL:TIM %s",
        """Set the timer interval of the trigger source for action 'ALL' in seconds.

        :type: - float, strictly from ``1E-5`` to ``1E5`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF'], [1E-5, 1E5]]
        )

    trigger_all_output_signal = Instrument.setting(
        ":TRIG:ALL:TOUT:SIGN %s",
        """Set the trigger signal output for action 'ALL'.

        :type: str, strictly in ``INT1``, ``INT2``, ``LAN``, ``TOUT``,
                ``EXT1`` to ``EXT7``

        - ``INT1`` and ``INT2`` selects the internal bus 1 or 2.
        - ``LAN`` selects a LAN port.
        - ``EXT1`` to ``EXT7`` selects the GPIO pin n, which is an output port of the Digital I/O
          D-sub connector on the rear panel. n = 1 to 7.
        - ``TOUT`` selects the BNC Trigger Out.

        It is for the status change between the idle state and the
        trigger layer.
        """,
        validator=strict_discrete_set,
        values=['INT1', 'INT2', 'LAN', 'TOUT',
                'EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7']
        )

    trigger_all_output_enabled = Instrument.setting(
        ":TRIG:ALL:TOUT %s",
        """Set the trigger output for action 'ALL' (bool).

        It is for the status change between the idle state
        and the trigger layer.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
        )


class AgilentB2983(AgilentB2981, BatteryMixin):
    """A class representing the Agilent/Keysight B2983A/B.

    The B2983 is a Femto/Picoammeterwith with battery operation.
    """
    pass


class AgilentB2985(AgilentB2981):
    """A class representing the Agilent/Keysight B2985A/B.

    The B2985 is a Femto/Picoammeter and Electrometer/High Resistance Meter.
    """

    function = Instrument.control(
        ":FUNC?", ":FUNC '%s'",
        """Control the measurement function.

        :type: str, strictly in ``CURR``, ``CHAR``, ``VOLT``, ``RES``
        """,
        validator=strict_discrete_set,
        values=['CURR', 'CHAR', 'VOLT', 'RES'],
        get_process=lambda v: v.strip('"'),
        get_process_list=lambda v: [x.strip('"') for x in v],
        )

    charge = Instrument.measurement(
        ":MEAS:CHAR?",
        """Measure charge with a spot measurement in Coulombs.

        :return: float
        """
        )

    charge_range = Instrument.control(
        ":CHAR:RANG?", ":CHAR:RANG %s",
        """Control the range for the charge measurement in Coulombs.

        :type: - float, strictly from ``2E-9`` to ``2E-6`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``, ``UP``, ``DOWN``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF', 'UP', 'DOWN'], [2E-9, 2E-6]]
        )

    resistance = Instrument.measurement(
        ":MEAS:RES?",
        """Measure resistance with a spot measurement in Ohms.

        :return: float
        """
        )

    resistance_range = Instrument.control(
        ":RES:RANG?", ":RES:RANG %s",
        """Control the range for the resistance measurement.

        :type: - float, strictly from ``1E6`` to ``1E15`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``, ``UP``, ``DOWN``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF', 'UP', 'DOWN'], [1E6, 1E15]]
        )

    voltage = Instrument.measurement(
        ":MEAS:VOLT?",
        """Measure voltage with a spot (one-shot) measurement in Volts.

        :return: float
        """
        )

    voltage_range = Instrument.control(
        ":VOLT:RANG?", ":VOLT:RANG %s",
        """Control the range for the voltage measurement in Volts.

        :type: - float, strictly from ``2`` to ``20`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``, ``UP``, ``DOWN``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF', 'UP', 'DOWN'], [2, 20]]
        )

    humidity = Instrument.measurement(
        ":SYST:HUM?",
        """Measure the relative humidity in percent.

        :return: float
        """
        )

    temperature = Instrument.measurement(
        ":SYST:TEMP?",
        """Measure the temperature.

        :return: float

        The unit of temperature is controlled by :attr:`temperature_unit`:
        """
        )

    temperature_sensor = Instrument.control(
        ":SYST:TEMP:SEL?", ":SYST:TEMP:SEL %s",
        """Control the tempertature sensor.

        :type: str, strictly in ``TC``, ``HSEN``

        - ``TC`` selects the thermocouple.
        - ``HSEN`` selects the temperature sensor within the humidity sensor.
        """,
        validator=strict_discrete_set,
        values=['TC', 'HSEN']
        )

    temperature_unit = Instrument.control(
        ":SYST:TEMP:UNIT?", ":SYST:TEMP:UNIT %s",
        """Control the tempertature unit.

        :type: str, strictly in ``C``, ``CEL``,
                                ``F``, ``FAR``,
                                ``K``

        - ``C``, ``CEL`` selects degree Celsius.
        - ``F``, ``FAR`` selects degree Fahrenheit.
        - ``K`` selects Kelvin.
        """,
        validator=strict_discrete_set,
        values=['C', 'CEL', 'F', 'FAR', 'K']
        )

############################################################
# Trigger functions for action 'TRANsient' (voltage source)#
############################################################

    def abort_transient(self):
        """Abort action 'TRANSient'."""
        self.write(":ABOR:TRAN")

    def arm_transient(self):
        """Send an immediate arm trigger for action 'TRANSient'.

        When the status of the specified action is initiated, the arm trigger
        causes a layer change from arm to trigger.
        """
        self.write(":ARM:TRAN")

    def init_transient(self):
        """Initiate a trigger for action 'TRANSient'."""
        self.write(":INIT:TRAN")

##############################################################
# Trigger properties for action 'TRANsient' (voltage source) #
##############################################################

    arm_transient_bypass_once_enabled = Instrument.control(
        ":ARM:TRAN:BYP?", ":ARM:TRAN:BYP %s",
        """
        Control the bypass for the event detector in the arm layer for action 'TRANSient' (bool).
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'ONCE', False: 'OFF'}
        )

    arm_transient_count = Instrument.control(
        ":ARM:TRAN:COUN?", ":ARM:TRAN:COUN %s",
        """Control the arm trigger count for action 'TRANSient'.

        :type: - int, strictly from ``1`` to ``100000`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``, ``INF``

        ``INF`` is equivalent to ``2147483647``.
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF', 'INF', 2147483647], [1, 100000]]
        )

    arm_transient_delay = Instrument.control(
        ":ARM:TRAN:DEL?", ":ARM:TRAN:DEL %s",
        """Control the arm trigger delay for action 'TRANSient' in seconds.

        :type: - float, strictly from ``0`` to ``1E5`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF'], [0, 100000]]
        )

    arm_transient_source = Instrument.control(
        ":ARM:TRAN:SOUR?", ":ARM:TRAN:SOUR %s",
        """Control the arm trigger source for action 'TRANSient'.

        :type: str, strictly in ``AINT``, ``BUS``, ``TIM``, ``INT1``, ``INT2``, ``LAN``, ``TIN``,
               ``EXT1`` to ``EXT7``

        - ``AINT`` automatically selects the arm source most suitable for the
          present operating mode by using internal algorithms.
        - ``BUS`` selects the remote interface trigger command such as the group
          execute trigger (GET) and the TRG command.
        - ``TIM`` selects a signal internally generated every interval set by
          :attr:`arm_transient_timer`.
        - ``INT1`` and ``INT2`` selects a signal from the internal bus 1 or 2.
        - ``LAN`` selects the LXI trigger specified by :attr:`arm_transient_source_lan_id`.
        - ``EXT1`` to ``EXT7`` selects a signal from the GPIO pin n, which is an input port of the
          Digital I/O D-sub connector on the rear panel. n = 1 to 7.
        - ``TIN`` selects the BNC Trigger In.
        """,
        validator=strict_discrete_set,
        values=['AINT', 'BUS', 'TIM', 'INT1', 'INT2', 'LAN', 'TIN',
                'EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7']
        )

    arm_transient_source_lan_id = Instrument.control(
        ":ARM:TRAN:SOUR:LAN?", ":ARM:TRAN:SOUR:LAN %s",
        """Control the source for LAN arm triggers for action 'TRANSient'.

        :type: str, strictly from ``LAN0`` to ``LAN7``
        """,
        validator=strict_discrete_set,
        values=['LAN0', 'LAN1', 'LAN2', 'LAN3', 'LAN4', 'LAN5', 'LAN6', 'LAN7']
        )

    arm_transient_timer = Instrument.control(
        ":ARM:TRAN:TIM?", ":ARM:TRAN:TIM %s",
        """Control the timer interval of the arm trigger source for action 'TRANSient' in seconds.

        :type: - float, strictly from ``1E-5`` to ``1E5``
               - str, strictly in ``MIN``, ``MAX``, ``DEF``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF'], [1E-5, 1E5]]
        )

    arm_transient_output_signal = Instrument.control(
        ":ARM:TRAN:TOUT:SIGN?", ":ARM:TRAN:TOUT:SIGN %s",
        """Control the arm trigger output for action 'TRANSient'.

        :type: str, strictly in ``INT1``, ``INT2``, ``LAN``, ``TOUT``,
               ``EXT1`` to ``EXT7``

        - ``INT1`` and ``INT2`` selects the internal bus 1 or 2.
        - ``LAN`` selects a LAN port.
        - ``EXT1`` to ``EXT7`` selects the GPIO pin n, which is an output port of the Digital I/O
          D-sub connector on the rear panel. n = 1 to 7.
        - ``TOUT`` selects the BNC Trigger Out.

        It is for the status change between the idle state and the arm layer.
        """,
        validator=strict_discrete_set,
        values=['INT1', 'INT2', 'LAN', 'TOUT',
                'EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7']
        )

    arm_transient_output_enabled = Instrument.control(
        ":ARM:TRAN:TOUT?", ":ARM:TRAN:TOUT %s",
        """Control the arm trigger output for action 'TRANSient' (bool).

        It is for the status change between the idle state and the arm layer.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
        )

    trigger_transient_is_idle = Instrument.measurement(
        ":IDLE:TRAN?",
        """Get idle the status of action 'TRANSient'  (bool).

        The command waits until the status is changed to idle.
        """,
        map_values=True,
        values={True: 1, False: 0}
        )

    trigger_transient_bypass_once_enabled = Instrument.control(
        ":TRIG:TRAN:BYP?", ":TRIG:TRAN:BYP %s",
        """
        Control the bypass for the event detector in trigger layer for action 'TRANSient' (bool).
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'ONCE', False: 'OFF'}
        )

    trigger_transient_count = Instrument.control(
        ":TRIG:TRAN:COUN?", ":TRIG:TRAN:COUN %s",
        """Control the trigger count for action 'TRANSient'.

        :type: - int, strictly from ``1`` to ``100000`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``, ``INF``

        ``INF`` is equivalent to ``2147483647``.
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF', 'INF', 2147483647], [1, 100000]]
        )

    trigger_transient_delay = Instrument.control(
        ":TRIG:TRAN:DEL?", ":TRIG:TRAN:DEL %s",
        """Control the trigger delay for action 'TRANSient' in seconds.

        :type: - float, strictly from ``0`` to ``1E5`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF'], [0, 100000]]
        )

    trigger_transient_source = Instrument.control(
        ":TRIG:TRAN:SOUR?", ":TRIG:TRAN:SOUR %s",
        """Control the trigger source for action 'TRANSient'.

        :type: str, strictly in ``AINT``, ``BUS``, ``TIM``,
               ``INT1``, ``INT2``, ``LAN``, ``TIN``,
               ``EXT1`` to ``EXT7``

        - ``AINT`` automatically selects the trigger source most suitable for the
          present operating mode by using internal algorithms.
        - ``BUS`` selects the remote interface trigger command such as the group
          execute trigger (GET) and the TRG command.
        - ``TIM`` selects a signal internally generated every interval set by
          :attr:`trigger_transient_timer`.
        - ``INT1`` and ``INT2`` selects a signal from the internal bus 1 or 2.
        - ``LAN`` selects the LXI trigger specified by :attr:`trigger_transient_source_lan_id`.
        - ``EXT1`` to ``EXT7`` selects a signal from the GPIO pin n, which is an input port of the
          Digital I/O D-sub connector on the rear panel. n = 1 to 7.
        - ``TIN`` selects the BNC Trigger In.
        """,
        validator=strict_discrete_set,
        values=['AINT', 'BUS', 'TIM', 'INT1', 'INT2', 'LAN', 'TIN',
                'EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7']
        )

    trigger_transient_source_lan_id = Instrument.control(
        ":TRIG:TRAN:SOUR:LAN?", ":TRIG:TRAN:SOUR:LAN %s",
        """Control the source for LAN triggers for action 'TRANSient'.

        :type: str, strictly from ``LAN0`` to ``LAN7``
        """,
        validator=strict_discrete_set,
        values=['LAN0', 'LAN1', 'LAN2', 'LAN3', 'LAN4', 'LAN5', 'LAN6', 'LAN7']
        )

    trigger_transient_timer = Instrument.control(
        ":TRIG:TRAN:TIM?", ":TRIG:TRAN:TIM %s",
        """Control the timer interval of the trigger source for action 'TRANSient'.

        :type: - float, strictly from ``1E-5`` to ``1E5`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF'], [1E-5, 1E5]]
        )

    trigger_transient_output_signal = Instrument.control(
        ":TRIG:TRAN:TOUT:SIGN?", ":TRIG:TRAN:TOUT:SIGN %s",
        """Control the trigger signal output for action 'TRANSient'.

        :type: str, strictly in ``INT1``, ``INT2``, ``LAN``, ``TOUT``,
               ``EXT1`` to ``EXT7``

        - ``INT1``, ``INT2`` selects the internal bus 1 or 2.
        - ``LAN`` selects a LAN port.
        - ``EXT1`` to ``EXT7`` selects the GPIO pin n, which is an output port of the Digital I/O
          D-sub connector on the rear panel. n = 1 to 7.
        - ``TOUT`` selects the BNC Trigger Out.

        It is for the status change between the idle state and the trigger layer.
        """,
        validator=strict_discrete_set,
        values=['INT1', 'INT2', 'LAN', 'TOUT',
                'EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7']
        )

    trigger_transient_output_enabled = Instrument.control(
        ":TRIG:TRAN:TOUT?", ":TRIG:TRAN:TOUT %s",
        """Control the trigger output for action 'TRANSient' (bool).

        It is for the status change between the idle state and the trigger layer.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
        )

############################
# Voltage source functions #
############################

    source_enabled = Instrument.control(
        ":OUTP?", ":OUTP %d",
        """Control the voltage source output relay (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
        )

    source_low_state = Instrument.control(
        ":OUTP:LOW?", ":OUTP:LOW %s",
        """Control the voltage source low terminal state.

        :type: str, strictly ``FLO`` or ``COMM``

        - ``FLO``: low terminal is floating.
        - ``COMM``: low terminal is connected to Common.
        """,
        validator=strict_discrete_set,
        values=['FLO', 'COMM']
        )

    source_off_state = Instrument.control(
        ":OUTP:OFF:MODE?", ":OUTP:OFF:MODE %s",
        """Control the voltage source off condition.

        :type: str, strictly in ``ZERO``, ``HIZ``, ``NORM``

        +------------+--------------------------------------------------------------+
        | ``HIGH Z`` | - Output relay: off (open)                                   |
        |            | - The voltage source setting is not changed.                 |
        |            | - This status is available only when the 20 V range is used. |
        +------------+--------------------------------------------------------------+
        | ``NORMAL`` | - Output voltage: 0 V                                        |
        |            | - Output relay: off (open)                                   |
        +------------+--------------------------------------------------------------+
        | ``ZERO``   | - Output voltage: 0 V in the present voltage range           |
        +------------+--------------------------------------------------------------+
        """,
        validator=strict_discrete_set,
        values=['ZERO', 'HIZ', 'NORM']
        )

    source_voltage = Instrument.control(
        ":SOUR:VOLT?", ":SOUR:VOLT %g",
        """Control the source voltage in Volts.

        :type: float, strictly from ``-1050`` to ``1050``

        For voltages > 20V the interlock must be closed.

        +---------+------------+-------------------+-----------------+
        |  Range  | Resolution |   Output voltage  | Maximum current |
        +---------+------------+-------------------+-----------------+
        |   20 V  |   700 µV   | -21 V ≤ V ≤ 21 V  |    +/-20 mA     |
        +---------+------------+-------------------+-----------------+
        |  1000 V |    35 mV   | -1 V ≤ V ≤ 1000 V |    +/-1.0 mA    |
        +---------+------------+-------------------+-----------------+
        | -1000 V |    35 mV   | -1000 V ≤ V ≤ 1 V |    +/-1.0 mA    |
        +---------+------------+-------------------+-----------------+
        """,
        validator=strict_range,
        values=[-1050, 1050]
        )

    source_voltage_range = Instrument.control(
        ":SOUR:VOLT:RANG?", ":SOUR:VOLT:RANG %s",
        """Control the source voltage range.

        :type: - float, strictly from ``-1000`` to ``1000`` or
               - str, strictly in ``MIN``, ``MAX``, ``DEF``
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['MIN', 'MAX', 'DEF'], [-1000, 1000]]
        )


class AgilentB2987(AgilentB2985, BatteryMixin):
    """A class representing the Agilent/Keysight B2987A/B.

    The B2987 is a Femto/Picoammeter and Electrometer/High Resistance Meter
    with battery operation.
    """
    pass
