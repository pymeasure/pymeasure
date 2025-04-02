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

from pymeasure.instruments import SCPIMixin, Instrument, Channel

from pymeasure.instruments.validators import (
    strict_discrete_set,
    truncated_range,
    joined_validators
    )

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AgilentB298xTrigger(Channel):
    """A class representing the B298x trigger functions."""

    def abor(self, action='ALL'):
        """Aborts the specified device action."""
        strict_discrete_set(action, ['ALL', 'ACQ', 'TRAN'])
        self.write(f":ABOR:{action}")

    def arm(self, action='ALL'):
        """Sends an immediate arm trigger for the specified device action.

        When the status of the specified device action is initiated, the arm trigger
        causes a layer change from arm to trigger.
        """
        strict_discrete_set(action, ['ALL', 'ACQ', 'TRAN'])
        self.write(f":ARM:{action}")

    def init(self, action='ALL'):
        """Init trigger."""
        strict_discrete_set(action, ['ALL', 'ACQ', 'TRAN'])
        self.write(f":INIT:{action}")

    arm_once_bypassed = Channel.control(
        ":ARM:BYP?", ":ARM:BYP %s",
        """Control the bypass for the event detector in the arm layer (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'ONCE', False: 'OFF'}
        )

    arm_count = Channel.control(
        ":ARM:COUN?", ":ARM:COUN %s",
        """Control the arm count for the specified device action""",
        validator=joined_validators(strict_discrete_set, truncated_range),
        values=[['MIN', 'MAX', 'DEF', 'INF', 2147483647], [1, 100000]]
        )

    arm_delay = Channel.control(
        ":ARM:DEL?", ":ARM:DEL %s",
        """Control the arm delay for the specified device action""",
        validator=joined_validators(strict_discrete_set, truncated_range),
        values=[['MIN', 'MAX', 'DEF'], [0, 100000]]
        )

    arm_source_lan_id = Channel.control(
        ":ARM:SOUR:LAN?", ":ARM:SOUR:LAN %s",
        """Control the source for LAN triggers.""",
        validator=strict_discrete_set,
        values=['LAN0', 'LAN1', 'LAN2', 'LAN3', 'LAN4', 'LAN5', 'LAN6', 'LAN7']
        )

    arm_source = Channel.control(
        ":ARM:SOUR?", ":ARM:SOUR %s",
        """Control the arm source for the specified device action.

        AINT: automatically selects the arm source most suitable for the
              present operating mode by using internal algorithms.
        BUS:  selects the remote interface trigger command such as the group
              execute trigger (GET) and the *TRG command.
        TIM:  selects a signal internally generated every interval set by the
              arm_timer command.
        INTn: selects a signal from the internal bus 1 or 2, respectively.
        LAN:  selects the LXI trigger specified by the arm_source_lan_id command.
        EXTn: selects a signal from the GPIO pin n, which is an input port of the
              Digital I/O D-sub connector on the rear panel. n = 1 to 7.
        TIN:  selects the BNC Trigger In.
        """,
        validator=strict_discrete_set,
        values=['AINT', 'BUS', 'TIM', 'INT1', 'INT2', 'LAN', 'TIN',
                'EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7']
        )

    arm_timer = Channel.control(
        ":ARM:TIM?", ":ARM:TIM %s",
        """Control the timer interval of arm source for the specified device action.""",
        validator=joined_validators(strict_discrete_set, truncated_range),
        values=[['MIN', 'MAX', 'DEF'], [1E-5, 1E5]]
        )

    arm_output_signal = Channel.control(
        ":ARM:TOUT:SIGN?", ":ARM:TOUT:SIGN %s",
        """Control the trigger output for the status change between the idle state and the
        arm layer. Multiple trigger output ports can be set.

        INTn: selects the internal bus 1 or 2.
        LAN:  selects a LAN port.
        EXTn: selects the GPIO pin n, which is an output port of the Digital I/O
              D-sub connector on the rear panel. n = 1 to 7.
        TOUT: selects the BNC Trigger Out.""",
        validator=strict_discrete_set,
        values=['INT1', 'INT2', 'LAN', 'TOUT',
                'EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7']
        )

    arm_output_enabled = Channel.control(
        ":ARM:TOUT?", ":ARM:TOUT %s",
        """Control the trigger output for the status change between the idle state
        and the arm layer.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: [1, 'ON'], False: [0, 'OFF']}
        )

    is_idle = Channel.measurement(
        ":IDLE?",
        """Get the status of the specified device action for the specified channel, and
        waits until the status is changed to idle.""",
        map_values=True,
        values={True: 1, False: 0}
        )

    once_bypassed = Channel.control(
        ":TRIG:BYP?", ":TRIG:BYP %s",
        """Control the bypass for the event detector in the trigger layer. (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'ONCE', False: 'OFF'}
        )

    count = Channel.control(
        ":TRIG:COUN?", ":TRIG:COUN %s",
        """Control the trigger count for the specified device action""",
        validator=joined_validators(strict_discrete_set, truncated_range),
        values=[['MIN', 'MAX', 'DEF', 'INF', 2147483647], [1, 100000]]
        )

    delay = Channel.control(
        ":TRIG:DEL?", ":TRIG:DEL %s",
        """Control the trigger delay for the specified device action""",
        validator=joined_validators(strict_discrete_set, truncated_range),
        values=[['MIN', 'MAX', 'DEF'], [0, 100000]]
        )

    source_lan_id = Channel.control(
        ":TRIG:SOUR:LAN?", ":TRIG:SOUR:LAN %s",
        """Control the source for LAN triggers.""",
        validator=strict_discrete_set,
        values=['LAN0', 'LAN1', 'LAN2', 'LAN3', 'LAN4', 'LAN5', 'LAN6', 'LAN7']
        )

    source = Channel.control(
        ":TRIG:SOUR?", ":TRIG:SOUR %s",
        """Control the trigger source for the specified device action.

        AINT: automatically selects the trigger source most suitable for the
              present operating mode by using internal algorithms.
        BUS:  selects the remote interface trigger command such as the group
              execute trigger (GET) and the *TRG command.
        TIM:  selects a signal internally generated every interval set by the
              arm_timer command.
        INTn: selects a signal from the internal bus 1 or 2, respectively.
        LAN:  selects the LXI trigger specified by the arm_source_lan_id command.
        EXTn: selects a signal from the GPIO pin n, which is an input port of the
              Digital I/O D-sub connector on the rear panel. n = 1 to 7.
        TIN:  selects the BNC Trigger In.
        """,
        validator=strict_discrete_set,
        values=['AINT', 'BUS', 'TIM', 'INT1', 'INT2', 'LAN', 'TIN',
                'EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7']
        )

    timer = Channel.control(
        ":TRIG:TIM?", ":TRIG:TIM %s",
        """Control the timer interval of arm source for the specified device action.""",
        validator=joined_validators(strict_discrete_set, truncated_range),
        values=[['MIN', 'MAX', 'DEF'], [1E-5, 1E5]]
        )

    output_signal = Channel.control(
        ":TRIG:TOUT:SIGN?", ":TRIG:TOUT:SIGN %s",
        """Control the trigger output for the status change between the idle state and the
        arm layer. Multiple trigger output ports can be set.

        INTn: selects the internal bus 1 or 2.
        LAN:  selects a LAN port.
        EXTn: selects the GPIO pin n, which is an output port of the Digital I/O
              D-sub connector on the rear panel. n = 1 to 7.
        TOUT: selects the BNC Trigger Out.""",
        validator=strict_discrete_set,
        values=['INT1', 'INT2', 'LAN', 'TOUT',
                'EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7']
        )

    output_enabled = Channel.control(
        ":TRIG:TOUT?", ":TRIG:TOUT %s",
        """Control the trigger output for the status change between the idle state
        and the trigger layer.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: [1, 'ON'], False: [0, 'OFF']}
        )


class AgilentB298xOutput(Channel):
    """A class representing the B298x source functions."""

    enabled = Channel.control(
        ":OUTP?", ":OUTP %d",
        """Control the voltage source output (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
        )

    low_state = Channel.control(
        ":OUTP:LOW?", ":OUTP:LOW %s",
        """Control the source low terminal state ('FLO', 'COMM').""",
        validator=strict_discrete_set,
        values=['FLO', 'COMM']
        )

    off_state = Channel.control(
        ":OUTP:OFF:MODE?", ":OUTP:OFF:MODE %s",
        """Control the source condition after output off (ZERO|HIZ|NORM).

        HIGH Z: • Output relay: off (open)
                • The voltage source setting is not changed.
                • This status is available only when the 20 V range is used.
        NORMAL: • Output voltage: 0 V
                • Output relay: off (open)
        ZERO:   • Output voltage: 0 V in the present voltage range
        """,
        validator=strict_discrete_set,
        values=['ZERO', 'HIZ', 'NORM']
        )

    voltage = Channel.control(
        ":SOUR:VOLT?", ":SOUR:VOLT %g",
        """Control the output voltage of the source.""",
        check_set_errors=False
        )

    range = Channel.control(
        ":SOUR:VOLT:RANG?", ":SOUR:VOLT:RANG %s",
        """Control the output voltage range of the source.""",
        validator=joined_validators(strict_discrete_set, truncated_range),
        values=[['MIN', 'MAX', 'DEF'], [-1000, 1000]],
        check_set_errors=False
        )


class AgilentB298xBattery(Channel):
    """A class representing the B298x battery functions."""

    def insert_id(self, command):
        return f":SYST:BATT{command}"

    level = Channel.measurement(
        "?",
        """Get the percentage of the remaining battery capacity (int).""",
        get_process=lambda v: int(v),  # convert to integer
    )

    cycles = Channel.measurement(
        ":CYCL?",
        """Get the battery cycle count (int).""",
        get_process=lambda v: int(v),  # convert to integer
    )

    selftest_passed = Channel.measurement(
        ":TEST?",
        """Get the battery self-test result (boolean).""",
        map_values=True,
        values={True: 0, False: 1}  # 0: passed, 1: failed
    )


class AgilentB298x(SCPIMixin, Instrument):
    """A class representing the Agilent/Keysight B2980A/B series Picoammeters/Electrometers."""

    HAS_SOURCE = False
    HAS_BATTERY = False

    def __init__(self, adapter,
                 name="Agilent/Keysight B2980A/B series",
                 **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

        if self.HAS_SOURCE:
            self.add_child(AgilentB298xOutput, attr_name='output')

        if self.HAS_BATTERY:
            self.add_child(AgilentB298xBattery, attr_name='battery')

    trigger = Instrument.ChannelCreator(AgilentB298xTrigger, "trigger")

    input_enabled = Instrument.control(
        ":INP?", ":INP %d",
        """Control whether the instrument input is enabled (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
        )

    zero_corrected = Instrument.control(
        ":INP:ZCOR?", ":INP:ZCOR %d",
        """Control the zero correct function for current/charge measurement (boolean).

        B2981/B2983 supports current measurement only.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
        )

    measure = Instrument.measurement(
        ":MEAS?",
        """Measure the defined parameter(s) with a spot (one-shot) measurement."""
        )

    current = Instrument.measurement(
        ":MEAS:CURR?",
        """Measure current with a spot (one-shot) measurement."""
        )

    current_range = Instrument.control(
        ":CURR:RANG?", ":CURR:RANG %s",
        """Control the range for current measurement.

        (float strictly from 2E-12 to 20E-3) or
        ('MIN', 'MAX', 'DEF', 'UP', 'DOWN')
        """,
        validator=joined_validators(strict_discrete_set, truncated_range),
        values=[['MIN', 'MAX', 'DEF', 'UP', 'DOWN'], [2E-12, 20E-3]]
        )

    function = Instrument.control(
        ":FUNC?", ":FUNC '%s'",
        """Control the measurement function.

        ('CURR', 'CHAR', 'VOLT', 'RES') for electrometers
        """,
        validator=strict_discrete_set,
        values=['CURR', 'CHAR', 'VOLT', 'RES'],
        dynamic=True
        )

    charge = Instrument.measurement(
        ":MEAS:CHAR?",
        """Measure charge with a spot (one-shot) measurement."""
        )

    charge_range = Instrument.control(
        ":CHAR:RANG?", ":CHAR:RANG %s",
        """Control the range for charge measurement.

        (float strictly from 2E-9 to 2E-6) or
        ('MIN', 'MAX', 'DEF', 'UP', 'DOWN')
        """,
        validator=joined_validators(strict_discrete_set, truncated_range),
        values=[['MIN', 'MAX', 'DEF', 'UP', 'DOWN'], [2E-9, 2E-6]]
        )

    resistance = Instrument.measurement(
        ":MEAS:RES?",
        """Measure resistance with a spot (one-shot) measurement."""
        )

    resistance_range = Instrument.control(
        ":RES:RANG?", ":RES:RANG %s",
        """Control the range for resistance measurement.

        (float strictly from 1E6 to 1E15) or
        ('MIN', 'MAX', 'DEF', 'UP', 'DOWN')
        """,
        validator=joined_validators(strict_discrete_set, truncated_range),
        values=[['MIN', 'MAX', 'DEF', 'UP', 'DOWN'], [1E6, 1E15]]
        )

    voltage = Instrument.measurement(
        ":MEAS:VOLT?",
        """Measure voltage with a spot (one-shot) measurement."""
        )

    voltage_range = Instrument.control(
        ":VOLT:RANG?", ":VOLT:RANG %s",
        """Control the range for voltage measurement.

        (float strictly from 2 to 20) or
        ('MIN', 'MAX', 'DEF', 'UP', 'DOWN')
        """,
        validator=joined_validators(strict_discrete_set, truncated_range),
        values=[['MIN', 'MAX', 'DEF', 'UP', 'DOWN'], [2, 20]]
        )


class AgilentB298xBattery(Channel):
    """A class representing the B298x battery functions."""

    def insert_id(self, command):
        return f":SYST:BATT{command}"

    level = Channel.measurement(
        "?",
        """Get the percentage of the remaining battery capacity (int).""",
        get_process=lambda v: int(v),  # convert to integer
    )

    cycles = Channel.measurement(
        ":CYCL?",
        """Get the battery cycle count (int).""",
        get_process=lambda v: int(v),  # convert to integer
    )

    selftest_passed = Channel.measurement(
        ":TEST?",
        """Get the battery self-test result (boolean).""",
        map_values=True,
        values={True: 0, False: 1}  # 0: passed, 1: failed
    )


##########################
# Instrument definitions #
##########################


class AgilentB2981(AgilentB298x):
    """Agilent/Keysight B2981A/B series, Femto/Picoammeter."""
    HAS_SOURCE = False
    HAS_BATTERY = False


class AgilentB2983(AgilentB298x):
    """Agilent/Keysight B2983A/B series, Femto/Picoammeter.

    Has battery operation.
    """
    HAS_SOURCE = False
    HAS_BATTERY = True


class AgilentB2985(AgilentB298x):
    """Agilent/Keysight B2985A/B series Femto/Picoammeter Electrometer/High Resistance Meter."""
    HAS_SOURCE = True
    HAS_BATTERY = False


class AgilentB2987(AgilentB298x):
    """Agilent/Keysight B2987A/B series Femto/Picoammeter Electrometer/High Resistance Meter.

    Has battery operation.
    """
    HAS_SOURCE = True
    HAS_BATTERY = True
