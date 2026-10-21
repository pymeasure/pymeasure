#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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
from enum import IntEnum

from pymeasure.instruments import AdapterType, Channel, Instrument, SCPIMixin
from pymeasure.instruments.common_base import InstrumentProperty
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class OperatingMode(IntEnum):
    """Operating mode of an output, as reported by the instrument."""

    OFF = 0  #: The output is off or unregulated.
    CONSTANT_CURRENT = 1  #: The output is in constant current mode.
    CONSTANT_VOLTAGE = 2  #: The output is in constant voltage mode.
    HARDWARE_FAILURE = 3  #: The output has a hardware failure.


class EDU36311AChannel(Channel):
    """An output channel of the Keysight EDU36311A power supply.

    Channel 1 is the 6 V output (P6V), channels 2 and 3 are the 30 V outputs (P30V and N30V).
    """

    voltage_setpoint = Channel.control(
        "VOLT? (@{ch})",
        "VOLT %g, (@{ch})",
        """Control the output voltage setpoint in Volts (float strictly from 0 to 6.18 for
        channel 1 and from 0 to 30.9 for channels 2 and 3).""",
        validator=strict_range,
        values=[0, 30.9],
        dynamic=True,
    )

    current_limit = Channel.control(
        "CURR? (@{ch})",
        "CURR %g, (@{ch})",
        """Control the output current limit in Amps (float strictly from 0.002 to 5.15 for
        channel 1 and from 0.001 to 1.03 for channels 2 and 3).""",
        validator=strict_range,
        values=[0.001, 1.03],
        dynamic=True,
    )

    voltage = Channel.measurement(
        "MEAS:VOLT? (@{ch})",
        """Measure the actual output voltage in Volts (float).""",
    )

    current = Channel.measurement(
        "MEAS:CURR? (@{ch})",
        """Measure the actual output current in Amps (float).""",
    )

    output_enabled: InstrumentProperty[bool] = Channel.control(
        "OUTP? (@{ch})",
        "OUTP %d, (@{ch})",
        """Control whether the output is enabled (bool).

        If an output delay is set, the configured state is returned, not the actual state.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    operating_mode: InstrumentProperty[OperatingMode] = Channel.measurement(
        "STAT:QUES:INST:ISUM{ch}:COND?",
        """Get the operating mode of the output (:class:`OperatingMode`).""",
        cast=int,
        get_process=OperatingMode,
    )

    output_on_delay = Channel.control(
        "OUTP:DEL:RISE? (@{ch})",
        "OUTP:DEL:RISE %.10g, (@{ch})",
        """Control the delay in seconds before the output turns on (float strictly from
        0 to 3600).""",
        validator=strict_range,
        values=[0, 3600],
    )

    output_off_delay = Channel.control(
        "OUTP:DEL:FALL? (@{ch})",
        "OUTP:DEL:FALL %.10g, (@{ch})",
        """Control the delay in seconds before the output turns off (float strictly from
        0 to 3600).

        Turning off due to a protection function (like over-voltage) is not delayed.
        """,
        validator=strict_range,
        values=[0, 3600],
    )

    over_voltage_protection_level = Channel.control(
        "VOLT:PROT? (@{ch})",
        "VOLT:PROT %g, (@{ch})",
        """Control the over-voltage protection trip level in Volts (float strictly from 0.5 to
        6.6 for channel 1 and from 1.5 to 33 for channels 2 and 3).

        Over-voltage protection is always enabled.
        """,
        validator=strict_range,
        values=[1.5, 33],
        dynamic=True,
    )

    over_voltage_protection_tripped: InstrumentProperty[bool] = Channel.measurement(
        "VOLT:PROT:TRIP? (@{ch})",
        """Get whether the over-voltage protection has tripped (bool).""",
        cast=int,
        values={True: 1, False: 0},
        map_values=True,
    )

    over_current_protection_enabled: InstrumentProperty[bool] = Channel.control(
        "CURR:PROT:STAT? (@{ch})",
        "CURR:PROT:STAT %d, (@{ch})",
        """Control whether the over-current protection is enabled (bool).

        When enabled, the output turns off if it stays in constant current mode for longer
        than :attr:`over_current_protection_delay`.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    over_current_protection_delay = Channel.control(
        "CURR:PROT:DEL? (@{ch})",
        "CURR:PROT:DEL %.10g, (@{ch})",
        """Control the over-current protection delay in seconds (float strictly from 0 to
        3600).""",
        validator=strict_range,
        values=[0, 3600],
    )

    over_current_protection_delay_start: InstrumentProperty[str] = Channel.control(
        "CURR:PROT:DEL:STAR? (@{ch})",
        "CURR:PROT:DEL:STAR %s, (@{ch})",
        """Control when the over-current protection delay timer starts (str strictly in
        'SCH', 'CCTR').

        'SCH' starts the timer at the end of a settings change in voltage, current or output
        state.
        'CCTR' starts the timer at any transition into constant current mode.
        """,
        validator=strict_discrete_set,
        values=["SCH", "CCTR"],
        cast=str,
    )

    over_current_protection_tripped: InstrumentProperty[bool] = Channel.measurement(
        "CURR:PROT:TRIP? (@{ch})",
        """Get whether the over-current protection has tripped (bool).""",
        cast=int,
        values={True: 1, False: 0},
        map_values=True,
    )

    triggered_voltage = Channel.control(
        "VOLT:TRIG? (@{ch})",
        "VOLT:TRIG %g, (@{ch})",
        """Control the voltage in Volts applied when a trigger occurs (float strictly from 0
        to 6.18 for channel 1 and from 0 to 30.9 for channels 2 and 3).

        It is only applied if :attr:`voltage_mode` is 'STEP'.
        """,
        validator=strict_range,
        values=[0, 30.9],
        dynamic=True,
    )

    triggered_current = Channel.control(
        "CURR:TRIG? (@{ch})",
        "CURR:TRIG %g, (@{ch})",
        """Control the current limit in Amps applied when a trigger occurs (float strictly
        from 0.002 to 5.15 for channel 1 and from 0.001 to 1.03 for channels 2 and 3).

        It is only applied if :attr:`current_mode` is 'STEP'.
        """,
        validator=strict_range,
        values=[0.001, 1.03],
        dynamic=True,
    )

    voltage_mode: InstrumentProperty[str] = Channel.control(
        "VOLT:MODE? (@{ch})",
        "VOLT:MODE %s, (@{ch})",
        """Control what happens to the voltage on a trigger (str strictly in 'FIX', 'STEP').

        'FIX' keeps the voltage setpoint, 'STEP' changes it to :attr:`triggered_voltage`.
        """,
        validator=strict_discrete_set,
        values=["FIX", "STEP"],
        cast=str,
    )

    current_mode: InstrumentProperty[str] = Channel.control(
        "CURR:MODE? (@{ch})",
        "CURR:MODE %s, (@{ch})",
        """Control what happens to the current limit on a trigger (str strictly in 'FIX',
        'STEP').

        'FIX' keeps the current limit, 'STEP' changes it to :attr:`triggered_current`.
        """,
        validator=strict_discrete_set,
        values=["FIX", "STEP"],
        cast=str,
    )

    trigger_source: InstrumentProperty[str] = Channel.control(
        "TRIG:SOUR? (@{ch})",
        "TRIG:SOUR %s, (@{ch})",
        """Control the trigger source (str strictly in 'BUS', 'IMM').

        'BUS' waits for :meth:`~pymeasure.instruments.keysight.KeysightEDU36311A.trigger`,
        'IMM' triggers as soon as the trigger system is initiated.
        """,
        validator=strict_discrete_set,
        values=["BUS", "IMM"],
        cast=str,
    )

    trigger_delay = Channel.control(
        "TRIG:DEL? (@{ch})",
        "TRIG:DEL %.10g, (@{ch})",
        """Control the delay in seconds between a trigger and the output change (float
        strictly from 0 to 3600).""",
        validator=strict_range,
        values=[0, 3600],
    )

    trigger_continuous_enabled: InstrumentProperty[bool] = Channel.control(
        "INIT:CONT? (@{ch})",
        "INIT:CONT %d, (@{ch})",
        """Control whether the trigger system is initiated continuously (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    def initiate(self) -> None:
        """Initiate the trigger system."""
        self.write("INIT (@{ch})")

    def abort(self) -> None:
        """Abort a pending trigger and return the trigger system to idle."""
        self.write("ABOR (@{ch})")

    def clear_protection(self) -> None:
        """Clear a latched over-voltage, over-current or over-temperature protection.

        Remove the condition that caused the protection to trip first.
        """
        self.write("OUTP:PROT:CLE (@{ch})")

    def clear_over_voltage_protection(self) -> None:
        """Clear a latched over-voltage protection."""
        self.write("VOLT:PROT:CLE (@{ch})")

    def clear_over_current_protection(self) -> None:
        """Clear a latched over-current protection."""
        self.write("CURR:PROT:CLE (@{ch})")


class KeysightEDU36311A(SCPIMixin, Instrument):
    """Represent the Keysight EDU36311A triple output DC power supply.

    The outputs are available as the channels :attr:`ch_1` (6 V, 5 A), :attr:`ch_2` and
    :attr:`ch_3` (30 V, 1 A each) of type
    :class:`~pymeasure.instruments.keysight.keysightEDU36311A.EDU36311AChannel`.

    .. code-block:: python

        supply = KeysightEDU36311A("USB0::0x2A8D::0x8F01::CN00000001::0::INSTR")
        supply.ch_1.voltage_setpoint = 5
        supply.ch_1.current_limit = 0.1
        supply.ch_1.output_enabled = True
        print(supply.ch_1.voltage)
    """

    ch_1 = Instrument.ChannelCreator(EDU36311AChannel, 1)

    ch_2 = Instrument.ChannelCreator(EDU36311AChannel, 2)

    ch_3 = Instrument.ChannelCreator(EDU36311AChannel, 3)

    def __init__(self, adapter: AdapterType, name: str = "Keysight EDU36311A", **kwargs):
        super().__init__(
            adapter,
            name,
            tcpip={"read_termination": "\n"},
            **kwargs,
        )
        self.ch_1.voltage_setpoint_values = [0, 6.18]
        self.ch_1.triggered_voltage_values = [0, 6.18]
        self.ch_1.current_limit_values = [0.002, 5.15]
        self.ch_1.triggered_current_values = [0.002, 5.15]
        self.ch_1.over_voltage_protection_level_values = [0.5, 6.6]

    tracking_enabled: InstrumentProperty[bool] = Instrument.control(
        "OUTP:TRAC?",
        "OUTP:TRAC %d",
        """Control whether channels 2 and 3 track each other's voltage setpoint (bool).

        When first enabled, channel 3 takes the voltage setpoint of channel 2.
        Afterwards, a voltage change on either channel is applied to both.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    display_enabled: InstrumentProperty[bool] = Instrument.control(
        "DISP?",
        "DISP %d",
        """Control whether the front panel display is on (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    display_view: InstrumentProperty[str] = Instrument.control(
        "DISP:VIEW?",
        "DISP:VIEW %s",
        """Control the front panel meter view (str strictly in 'METER1', 'METER3').

        'METER1' shows one channel in detail, 'METER3' shows all three channels.
        """,
        validator=strict_discrete_set,
        values=["METER1", "METER3"],
        cast=str,
    )

    beeper_enabled: InstrumentProperty[bool] = Instrument.control(
        "SYST:BEEP:STAT?",
        "SYST:BEEP:STAT %d",
        """Control whether the beeper sounds on errors (bool).

        This setting is stored in non-volatile memory.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    @property
    def options(self):
        """Get the installed options.

        Raises *NotImplementedError* since command ``*OPT?`` is not implemented in EDU36311A.
        """
        raise NotImplementedError("*OPT? is not implemented in EDU36311A.")

    def beep(self) -> None:
        """Issue a single beep."""
        self.write("SYST:BEEP")

    def trigger(self) -> None:
        """Send a bus trigger to all channels waiting for a 'BUS' trigger."""
        self.write("*TRG")

    def save_state(self, location: int) -> None:
        """Save the instrument state to non-volatile memory, overwriting the location.

        :param location: Memory location (int strictly from 0 to 9).
        """
        location = strict_discrete_set(location, range(10))
        self.write(f"*SAV {location}")

    def recall_state(self, location: int) -> None:
        """Recall an instrument state from non-volatile memory.

        :param location: Memory location (int strictly from 0 to 9).
        """
        location = strict_discrete_set(location, range(10))
        self.write(f"*RCL {location}")
