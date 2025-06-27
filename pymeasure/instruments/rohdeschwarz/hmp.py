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

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import (strict_discrete_set,
                                              truncated_range)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def process_sequence(sequence):
    """
    Check and prepare sequence data.

    :param sequence: Sequence data, in the form [voltage1, current1, time1,
        voltage2, current2, time2, ..., voltage128, current128, time128] with
        voltages in V, currents in A, and times in s. Dwell times are between
        0.06 and 10 s.
    :type sequence: list of float
    :return: Sequence data in the form "Voltage1,Current1,Time1,Voltage2,
        Current2,Time2,...,Voltage128,Current128,Time128"
    :rtype: str
    """
    if not len(sequence) % 3 == 0:
        raise ValueError("Sequence must contain multiple of 3 values.")
    if any(t > 10 or t < 0.06 for t in sequence[2::3]):
        raise ValueError("Dwell times must be between 0.06 and 10 s.")
    # turn sequence data into a string
    sequence = ",".join(str(s) for s in sequence)
    return sequence


class HMP4040(SCPIMixin, Instrument):
    """Represents a Rohde&Schwarz HMP4040 power supply."""

    def __init__(self, adapter, **kwargs):
        kwargs.setdefault("name", "Rohde&Schwarz HMP4040")
        super().__init__(
            adapter,
            **kwargs
        )

    # System Setting Commands -------------------------------------------------

    def beep(self):
        """Emit a single beep from the instrument."""
        self.write("SYST:BEEP")

    control_method = Instrument.setting(
        "SYST:%s",
        """
        Control manual front panel ('LOC'), remote ('REM') or manual/remote
        control('MIX') control or locks the front panel control ('RWL').
        """,
        validator=strict_discrete_set,
        values=["LOC", "REM", "MIX", "RWL"],
    )

    version = Instrument.measurement(
        "SYST:VERS?",
        "Get the SCPI version the instrument's command set complies with.",
    )

    # Channel Selection Commands ----------------------------------------------

    selected_channel = Instrument.control(
        "INST:NSEL?",
        "INST:NSEL %s",
        "Control the selected channel.",
        validator=strict_discrete_set,
        values=[1, 2, 3, 4],
        cast=int
    )

    # Voltage Settings --------------------------------------------------------

    voltage = Instrument.control(
        "VOLT?", "VOLT %s",
        "Control output voltage in V. Increment 0.001 V."
    )

    min_voltage = Instrument.measurement(
        "VOLT? MIN", "Get minimum voltage in V."
    )

    max_voltage = Instrument.measurement(
        "VOLT? MAX", "Get maximum voltage in V."
    )

    def voltage_to_min(self):
        """Set voltage of the selected channel to its minimum value."""
        self.write("VOLT MIN")

    def voltage_to_max(self):
        """Set voltage of the selected channel to its maximum value."""
        self.write("VOLT MAX")

    voltage_step = Instrument.control(
        "VOLT:STEP?",
        "VOLT:STEP %s",
        "Control voltage step in V. Default 1 V.",
        validator=truncated_range,
        values=[0, 32.050],
    )

    def step_voltage_up(self):
        """Increase voltage by one step."""
        self.write("VOLT UP")

    def step_voltage_down(self):
        """Decrease voltage by one step."""
        self.write("VOLT DOWN")

    # Current Settings --------------------------------------------------------

    current = Instrument.control(
        "CURR?",
        "CURR %s",
        "Control output current in A. Range depends on instrument type.",
    )

    min_current = Instrument.measurement(
        "CURR? MIN", "Get minimum current in A."
    )

    max_current = Instrument.measurement(
        "CURR? MAX", "Get maximum current in A."
    )

    def current_to_min(self):
        """Set current of the selected channel to its minimum value."""
        self.write("CURR MIN")

    def current_to_max(self):
        """Set current of the selected channel to its maximum value."""
        self.write("CURR MAX")

    current_step = Instrument.control(
        "CURR:STEP?", "CURR:STEP %s", "Control current step in A."
    )

    def step_current_up(self):
        """Increase current by one step."""
        self.write("CURR UP")

    def step_current_down(self):
        """Decreases current by one step."""
        self.write("CURR DOWN")

    # Combined Voltage And Current Settings -----------------------------------

    voltage_and_current = Instrument.control(
        "APPL?",
        "APPL %s, %s",
        "Control output voltage (V) and current (A).",
    )

    # Output Settings ---------------------------------------------------------

    selected_channel_active = Instrument.control(
        "OUTP:SEL?",
        "OUTPUT:SEL %s",
        "Control the selected channel to active or inactive or check its status.",
        values={True: 1, False: 0},
        map_values=True,
    )

    output_enabled = Instrument.control(
        "OUTP:GEN?",
        "OUTP:GEN %s",
        "Control the output on or off or check the output status.",
        values={True: 1, False: 0},
        map_values=True,
    )

    # The following commands are for making it easier to change the selected
    # channels and activate/deactivate them.

    def set_channel_state(self, channel, state):
        """
        Set the state of the channel to active or inactive.

        :param channel: Channel number to set the state of.
        :type channel: int
        :param state: State of the channel, i.e. True for active, False for
            inactive.
        :type state: bool
        """
        # Save current selected channel before switching.
        selected_channel = self.selected_channel
        self.selected_channel = channel
        self.selected_channel_active = state
        # Restore previously selected channel.
        self.selected_channel = selected_channel

    # Measurement Commands ----------------------------------------------------

    measured_voltage = Instrument.measurement(
        "MEAS:VOLT?", "Get voltage in V."
    )

    measured_current = Instrument.measurement(
        "MEAS:CURR?", "Get current in A."
    )

    # Arbitrary Sequence Commands ---------------------------------------------

    def clear_sequence(self, channel):
        """Clear the sequence of the selected channel."""
        channel = strict_discrete_set(channel, [1, 2, 3, 4])
        self.write(f"ARB:CLEAR {channel}")

    sequence = Instrument.setting(
        "ARB:DATA %s",
        "Set sequence of triplets of voltage (V), current (A) and dwell "
        "time (s).",
        set_process=process_sequence,
    )

    repetitions = Instrument.control(
        "ARB:REP?",
        "ARB:REP %s",
        "Control umber of repetitions (0...255). If 0 is entered, the sequence is"
        "repeated indefinitely.",
        validator=strict_discrete_set,
        values=range(256),
        cast=int,
    )

    def load_sequence(self, slot):
        """Load a saved waveform from internal memory (slot 1, 2 or 3)."""
        slot = strict_discrete_set(slot, [1, 2, 3])
        self.write(f"ARB:REST {slot}")

    def save_sequence(self, slot):
        """
        Save the sequence defined in the sequence property to internal memory
        (slot 1, 2 or 3).
        """
        slot = strict_discrete_set(slot, [1, 2, 3])
        self.write(f"ARB:SAVE {slot}")

    def start_sequence(self, channel):
        """Start the sequence of the selected channel."""
        channel = strict_discrete_set(channel, [1, 2, 3, 4])
        self.write(f"ARB:START {channel}")

    def stop_sequence(self, channel):
        """Stop the sequence defined in the sequence property of the selected
        channel."""
        channel = strict_discrete_set(channel, [1, 2, 3, 4])
        self.write(f"ARB:STOP {channel}")

    def transfer_sequence(self, channel):
        """
        Transfer the sequence defined in the sequence property to the selected
        channel.
        """
        channel = strict_discrete_set(channel, [1, 2, 3, 4])
        self.write(f"ARB:TRAN {channel}")
