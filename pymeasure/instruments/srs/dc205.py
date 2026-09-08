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

from pymeasure.instruments import IEEE4882Mixin, Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

BOOL_MAP = {True: 1, False: 0}

# Range setting -> maximum settable magnitude in V (see the VOLT command in the
# manual; e.g. the 10 V range allows up to 10.1 V).
RANGE_LIMITS = {1: 1.010, 10: 10.10, 100: 101.0}
RANGE_CODES = {1: 0, 10: 1, 100: 2}


class DC205(IEEE4882Mixin, Instrument):
    """Stanford Research Systems DC205 precision DC voltage source.

    The allowed :attr:`voltage` range follows the selected :attr:`voltage_range`:
    the instrument does not auto-range, so a voltage outside the active range is
    rejected until the range is changed. The driver forces numeric response mode
    (``TOKN OFF``) on connection so the mapped properties parse reliably.
    """

    def __init__(self, adapter, name="Stanford Research Systems DC205", **kwargs):
        super().__init__(
            adapter,
            name,
            asrl={"baud_rate": 115200},
            write_termination="\r\n",
            read_termination="\r\n",
            **kwargs,
        )
        # Ensure token-type queries answer with numbers, not text tokens.
        self.write("TOKN 0")
        # Sync the voltage/scan validators with the instrument's active ranges.
        self._read_voltage_range()
        self._read_scan_range()

    voltage = Instrument.control(
        "VOLT?", "VOLT %.6f",
        """Control the output voltage in V (float). The valid range follows
        :attr:`voltage_range` (up to +-1.01, +-10.1 or +-101 V).""",
        validator=strict_range,
        values=[-RANGE_LIMITS[1], RANGE_LIMITS[1]],
        dynamic=True,
    )

    @property
    def voltage_range(self):
        """Control the output range in V (int 1, 10 or 100).

        Setting the range also updates the allowed :attr:`voltage` range, so an
        out-of-range voltage raises a :class:`ValueError` until the range is set.
        The value is read back from the instrument, which may refuse the change
        (for example while a scan is armed or running).
        """
        return self._read_voltage_range()

    @voltage_range.setter
    def voltage_range(self, value):
        value = strict_discrete_set(value, list(RANGE_CODES))
        self.write(f"RNGE {RANGE_CODES[value]}")
        actual = self._read_voltage_range()
        if actual != value:
            raise ValueError(
                f"DC205 did not switch to the {value} V range (now {actual} V); "
                "check that no scan is armed or running."
            )

    def _read_voltage_range(self):
        """Read the active range in V, syncing the :attr:`voltage` validator to it."""
        value = {v: k for k, v in RANGE_CODES.items()}[int(self.ask("RNGE?"))]
        self.voltage_values = [-RANGE_LIMITS[value], RANGE_LIMITS[value]]
        return value

    output_enabled = Instrument.control(
        "SOUT?", "SOUT %d",
        """Control whether the output is switched on (bool).""",
        validator=strict_discrete_set,
        values=BOOL_MAP,
        map_values=True,
    )

    isolation = Instrument.control(
        "ISOL?", "ISOL %d",
        """Control the output common, either 'ground' or 'float' (str).""",
        validator=strict_discrete_set,
        values={"ground": 0, "float": 1},
        map_values=True,
    )

    sensing = Instrument.control(
        "SENS?", "SENS %d",
        """Control the sensing mode, either 'two-wire' or 'four-wire' (str).""",
        validator=strict_discrete_set,
        values={"two-wire": 0, "four-wire": 1},
        map_values=True,
    )

    overloaded = Instrument.measurement(
        "OVLD?",
        """Get whether the output is in current limit (bool).""",
        values=BOOL_MAP,
        map_values=True,
    )

    alarm_enabled = Instrument.control(
        "ALRM?", "ALRM %d",
        """Control the audible alarm (bool).""",
        validator=strict_discrete_set,
        values=BOOL_MAP,
        map_values=True,
    )

    token_mode_enabled = Instrument.control(
        "TOKN?", "TOKN %d",
        """Control whether token-type queries answer with text tokens instead of
        numbers (bool). The driver relies on numeric responses, so only ``False``
        is accepted; setting ``True`` raises a :class:`ValueError`.""",
        validator=strict_discrete_set,
        values={False: 0},
        map_values=True,
    )

    # Scan configuration ---------------------------------------------------------------------------

    @property
    def scan_range(self):
        """Control the scan range in V (int 1, 10 or 100).

        It can be set independently of :attr:`voltage_range` but must match it to
        arm a scan. Setting it also updates the allowed :attr:`scan_begin` and
        :attr:`scan_end` range and, on the instrument, resets both to 0 V. The
        value is read back, which may be refused while a scan is armed or running.
        """
        return self._read_scan_range()

    @scan_range.setter
    def scan_range(self, value):
        value = strict_discrete_set(value, list(RANGE_CODES))
        self.write(f"SCAR {RANGE_CODES[value]}")
        actual = self._read_scan_range()
        if actual != value:
            raise ValueError(
                f"DC205 did not switch to the {value} V scan range (now {actual} V); "
                "check that no scan is armed or running."
            )

    def _read_scan_range(self):
        """Read the scan range in V, syncing the scan endpoint validators to it."""
        value = {v: k for k, v in RANGE_CODES.items()}[int(self.ask("SCAR?"))]
        self.scan_begin_values = [-RANGE_LIMITS[value], RANGE_LIMITS[value]]
        self.scan_end_values = [-RANGE_LIMITS[value], RANGE_LIMITS[value]]
        return value

    scan_begin = Instrument.control(
        "SCAB?", "SCAB %.6f",
        """Control the scan start voltage in V (float, within :attr:`scan_range`).""",
        validator=strict_range,
        values=[-RANGE_LIMITS[1], RANGE_LIMITS[1]],
        dynamic=True,
    )

    scan_end = Instrument.control(
        "SCAE?", "SCAE %.6f",
        """Control the scan stop voltage in V (float, within :attr:`scan_range`).""",
        validator=strict_range,
        values=[-RANGE_LIMITS[1], RANGE_LIMITS[1]],
        dynamic=True,
    )

    scan_time = Instrument.control(
        "SCAT?", "SCAT %.1f",
        """Control the scan duration in s (float from 0.1 to 9999.9).""",
        validator=strict_range,
        values=[0.1, 9999.9],
    )

    scan_shape = Instrument.control(
        "SCAS?", "SCAS %d",
        """Control the scan shape, either 'one-direction' or 'up-down' (str).""",
        validator=strict_discrete_set,
        values={"one-direction": 0, "up-down": 1},
        map_values=True,
    )

    scan_cycle = Instrument.control(
        "SCAC?", "SCAC %d",
        """Control the scan cycling mode, either 'once' or 'repeat' (str).""",
        validator=strict_discrete_set,
        values={"once": 0, "repeat": 1},
        map_values=True,
    )

    scan_display = Instrument.control(
        "SCAD?", "SCAD %d",
        """Control whether the display updates during a scan (bool).""",
        validator=strict_discrete_set,
        values=BOOL_MAP,
        map_values=True,
    )

    scan_state = Instrument.measurement(
        "SCAA?",
        """Get the scan state, one of 'idle', 'armed' or 'scanning' (str).""",
        values={"idle": 0, "armed": 1, "scanning": 2},
        map_values=True,
    )

    def arm_scan(self):
        """Arm the scan.

        Requires the output to be enabled, :attr:`scan_range` to match
        :attr:`voltage_range`, and :attr:`scan_begin` and :attr:`scan_end` to
        differ. Start the armed scan with :meth:`start_scan`.
        """
        self.write("SCAA ARMED")

    def disarm_scan(self):
        """Disarm an armed scan or cancel a running scan."""
        self.write("SCAA IDLE")

    def start_scan(self):
        """Start a previously armed scan (equivalent to a trigger)."""
        self.write("*TRG")

    last_execution_error = Instrument.measurement(
        "LEXE?",
        """Get the last execution error code (int).""",
        cast=int,
    )

    last_command_error = Instrument.measurement(
        "LCME?",
        """Get the last command error code (int).""",
        cast=int,
    )
