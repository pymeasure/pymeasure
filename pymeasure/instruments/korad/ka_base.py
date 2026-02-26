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

import numpy as np
import time
from enum import IntEnum
from dataclasses import dataclass
from pymeasure.adapters.adapter import Adapter
from pymeasure.adapters.serial import SerialAdapter
from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_range, strict_discrete_set


class Mode(IntEnum):
    CC = 0
    CV = 1


class Combination(IntEnum):
    INDEPENDENT = 0
    TRACKING_SERIES = 1
    # ?
    TRACKING_PARALLEL = 3


@dataclass
class State:
    ch_1: Mode
    ch_2: Mode
    combination: Combination
    beep: bool
    lock: bool
    output: bool

    @classmethod
    def from_byte(cls, byte: int):
        ch_1 = Mode((byte >> 0) & 1)
        ch_2 = Mode((byte >> 1) & 1)
        combination = Combination((byte >> 2) & 3)
        beep = bool((byte >> 4) & 1)
        lock = bool((byte >> 5) & 1)
        output = bool((byte >> 6) & 1)
        return cls(ch_1, ch_2, combination, beep, lock, output)
        # 7 N/A


class KoradKAChannel(Channel):
    def __init__(self, parent: "KoradKABase", id: int):
        super().__init__(parent, id)
        assert id in [1, 2], "Channel must be either 1 or 2."

    voltage_setpoint: property = Instrument.control(
        "VSET{ch}?", "VSET{ch}:%g",
        """Control the output voltage setpoint.""",
        validator=lambda v, vs: strict_range(v, vs),
        values=(0, 61.0),
        dynamic=True
    )

    voltage: property = Instrument.measurement(
        "VOUT{ch}?",
        """Measure the actual output voltage."""
    )

    over_voltage_protection: property = Instrument.control(
        "OVP{ch}?", "OVP{ch}:%g",
        """
        Control the over-voltage protection.

        Valid values are ``True`` to turn OVP on and ``False`` to turn OVP off.
        When OVP is on, the PSU will shut down the output
        if the output voltage exceeds the OVP setpoint.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    # KA3005P V2.0 adds "K" suffix
    current_setpoint: property = Instrument.control(
        "ISET{ch}?", "ISET{ch}:%g",
        """Control the output current setpoint.""",
        validator=lambda v, vs: strict_range(v, vs),
        values=(0, 5.1),
        dynamic=True,
        preprocess_reply=lambda s: s.replace("K", "")
    )

    current: property = Instrument.measurement(
        "IOUT{ch}?",
        """Measure the actual output current."""
    )

    over_current_protection: property = Instrument.control(
        "OCP{ch}?", "OCP{ch}:%g",
        """
        Control the over-current protection.

        Valid values are ``True`` to turn OCP on and ``False`` to turn OCP off.
        When OCP is on, the PSU will shut down the output
        if the output current exceeds the OCP setpoint.

        Be aware: OCP may trigger when enabling the output
        due to (internal) output capacity inrush current.
        """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    @property
    def mode(self) -> Mode:
        """Get the current mode of the channel (CC or CV)
        """
        state = self.parent.state
        if self.id == 1:
            return state.ch_1
        else:
            return state.ch_2


class KoradKABase(Instrument):
    """Represents a generic Korad KAxxxxP power supply
    and provides a high-level for interacting with the instrument
    """

    last_write_timestamp: float  # hold timestamp fo the last write for enforcing write_delay
    write_delay: float  # minimum time between writes
    cached_idn: str

    def __init__(self, adapter: Adapter, name: str = "Korad KA base", **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            **kwargs
        )
        if not isinstance(self.adapter, SerialAdapter):
            self.adapter.log.warning(
                "adapter should be instance of SerialAdapter,assuming test environment"
            )
        else:
            self.adapter.connection.timeout = 0.1
            self.adapter.connection.baudrate = 115200
        self.last_write_timestamp = 0.0
        self.write_delay = 0.05
        self.cached_idn = ""

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Properties
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @property
    def id(self) -> str:
        """Get the identity of the instrument"""
        if self.cached_idn:
            return self.cached_idn
        self.cached_idn = self.ask("*IDN?")
        return self.cached_idn

    @property
    def model(self) -> str:
        """Get the model of the instrument"""
        return self.id.split("V")[0].removeprefix("KORAD")

    @property
    def version(self) -> list[int]:
        """Get the firmware version of the instrument"""
        version_str = self.id.split("V")[1]
        version = version_str.split(".")
        assert len(version) == 2
        return [int(v) for v in version]

    output_enabled: property = Instrument.control(
        "OUT?", "OUT%d",
        """Control the output of the power supply.

        Valid values are ``True`` to turn output on and ``False`` to turn output off, shutting down
        any voltage or current.
        """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    # does nothing on KA3005P V2.0
    beep: property = Instrument.control(
        "BEEP?", "BEEP%d",
        """Control the beep of the power supply.

        Valid values are ``True`` to turn beep on and ``False`` to turn beep off.
        """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    # on KA3005P V2.0
    # - works only when the preset is currently selected (caused by recall_preset)
    # - saves values as preset
    store_preset: property = Instrument.setting(
        "SAV%d",
        """Set the current settings into preset slot.""",
        validator=strict_discrete_set,
        values=(1, 2, 3, 4, 5)
    )

    # on KA3005P V2.0
    # - selects the preset slot
    # - reloads values from the slot and overwrites anything unsaved
    recall_preset: property = Instrument.setting(
        "RCL%d",
        """Set the current settings from preset slot.""",
        validator=strict_discrete_set,
        values=(1, 2, 3, 4, 5)
    )

    @property
    def state(self) -> State:
        """Get the current state of the system

    :return State.
        """
        got = self.binary_values("STATUS?", dtype=np.uint8)
        assert len(got) == 1, f"Expected a single byte response for state query, got {got}"
        return State.from_byte(got[0])

    # at least KA3005P V2.0 does not use traditionally delimiters for requests/responses,
    # but relies on timeouts. It was observed that PSU starts sending reply
    # ~18 ms after the end of the command (if the command is query).
    # To make sure all commands are registered by the PSU,
    # 50 ms pause between writes proved to be sufficient.
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Methods
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _wait_before_writing(self):
        actual_write_delay = time.time() - self.last_write_timestamp
        to_sleep = self.write_delay - actual_write_delay
        if to_sleep > 0:
            time.sleep(to_sleep)

    def write(self, command, **kwargs):
        """Overrides Instrument write method for including write_delay time after the parent call.

    :param command: command string to be sent to the instrument
        """
        self._wait_before_writing()
        super().write(command, **kwargs)
        self.last_write_timestamp = time.time()

    def ask(self, command, query_delay=None):
        """Overrides Instrument ask method for including write_delay time after the parent call.

    :param command: command string to be sent to the instrument
    :returns: response from the instrument
        """
        if not isinstance(self.adapter, SerialAdapter):
            self.adapter.log.warning(
                "ask method may not work correctly if adapter"
                " is not instance of SerialAdapter, assuming test environment"
            )
            return super().ask(command, query_delay=query_delay)

        self.write(command)
        if query_delay is not None:
            time.sleep(query_delay)
        # override timeout until first character arrives
        # after that, restore the timeout and read until that
        timeout_backup = self.adapter.connection.timeout
        assert timeout_backup is not None, \
            "Adapter connection timeout must be set to a non-None value."
        self.adapter.connection.timeout = 0.1
        first = self.read_bytes(1, break_on_termchar=False)
        self.adapter.connection.timeout = timeout_backup
        assert len(first) > 0, "No response received from instrument."
        return (first + self.read_bytes(-1, break_on_termchar=False)).decode(errors="ignore")
        # if inter_byte_timeout woudl work, it would be easy
        return self.read_bytes(-1, break_on_termchar=False).decode(errors="ignore")
