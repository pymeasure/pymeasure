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
import time

from pyvisa.constants import Parity, StopBits

from pymeasure.instruments import IEEE4882Mixin, Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# Status and error bits (manual sec. 5.1.4.2.2 and 5.1.4.3) -----------------------------------

OPST_COMPLIANCE = 1
OPST_RAMP_DONE = 2
OPST_PSH_STABLE = 4
OPST_DONE_MASK = OPST_RAMP_DONE | OPST_PSH_STABLE

HARDWARE_ERRORS = {
    0: "temperature fault",
    1: "low line voltage",
    2: "output over current",
    3: "output over voltage",
    4: "output control failure",
    5: "DAC processor not responding",
}
OPERATIONAL_ERRORS = {
    0: "calibration error",
    1: "external current program error",
    2: "high line voltage",
    3: "temperature high",
    4: "remote inhibit detected",
    5: "magnet quench detected",
    6: "magnet discharging through crowbar",
}
PSH_ERRORS = {
    0: "PSH open circuit",
    1: "PSH short circuit",
}

#: Bits that abort a ramp. All hardware errors and both PSH errors are fatal.
FATAL_OPERATIONAL_BITS = 0b111_0000  # remote inhibit, quench, crowbar discharge

HEATER_STATES = {"off": 0, "on": 1, "warming": 2, "cooling": 3}


class MagnetFaultError(RuntimeError):
    """Raised when the supply reports a fatal hardware, operational or PSH error."""


def _bits(value, table):
    return [table[b] for b in sorted(table) if value & (1 << b)]


def decode_errors(reply):
    """Decode an ``ERST?`` reply ``"hhh,ooo,ppp"``.

    :returns: ``(hardware, operational, psh, messages)``; the first three are the integer
        registers, ``messages`` lists the set bits (hardware, then operational, then PSH).
    """
    hardware, operational, psh = (int(v) for v in str(reply).split(","))
    messages = (
        _bits(hardware, HARDWARE_ERRORS)
        + _bits(operational, OPERATIONAL_ERRORS)
        + _bits(psh, PSH_ERRORS)
    )
    return hardware, operational, psh, messages


def _is_fatal(hardware, operational, psh):
    return bool(hardware or (operational & FATAL_OPERATIONAL_BITS) or psh)


def heater_interlocked_range(value, values):
    """Validator for the field setpoint: ``values`` is ``None`` while the heater is not on."""
    if values is None:
        raise ValueError(
            "Persistent switch heater interlock: the heater is not on, refusing to "
            "change the field setpoint."
        )
    return strict_range(value, values)


def _settable_heater_state(value, values):
    """Only ``"off"`` and ``"on"`` can be set; warming/cooling are read-only states."""
    return strict_discrete_set(value, ["off", "on"])


class LakeShore625(IEEE4882Mixin, Instrument):
    """Lake Shore Model 625 superconducting magnet power supply.

    :param adapter: PyVISA resource name or adapter instance.
    :param name: Instrument name.
    :param field_limit: Largest absolute field setpoint (T) the driver accepts. Set it to your
        magnet's rating; the default (6 T) is not a property of the supply.
    :param kwargs: Passed to :class:`~pymeasure.instruments.Instrument`. Serial settings
        (9600 baud, 7 data bits, odd parity, 1 stop bit) are applied only to ASRL resources.

    .. code-block:: python

        magnet = LakeShore625("ASRL3::INSTR")
        magnet.persistent_heater = "on"
        magnet.wait_for_heater("on")
        magnet.set_field_blocking(1.0)
    """

    #: Delay (s) between writing ``OPST?`` and reading it during a blocking ramp.
    ramp_status_query_delay = 0.5

    def __init__(
        self, adapter, name="Lake Shore 625 magnet power supply", field_limit=6.0, **kwargs
    ):
        asrl = {"baud_rate": 9600, "data_bits": 7, "parity": Parity.odd, "stop_bits": StopBits.one}
        asrl.update(kwargs.pop("asrl", {}))
        kwargs.setdefault("write_termination", "\r\n")
        kwargs.setdefault("read_termination", "\r\n")
        kwargs.setdefault("timeout", 3000)
        super().__init__(adapter, name, asrl=asrl, **kwargs)
        self._field_range = [-abs(field_limit), abs(field_limit)]
        self._field_setpoint_values = None  # locked until a PSH? query reports "on"
        self._last_error_reply = None

    @property
    def options(self):
        """Get the device options; not supported, the Model 625 has no ``*OPT?`` command."""
        raise NotImplementedError("The LakeShore Model 625 does not implement *OPT?.")

    # Measurements -----------------------------------------------------------------------------

    current = Instrument.measurement("RDGI?", """Measure the output current in A.""")

    voltage = Instrument.measurement("RDGV?", """Measure the output voltage in V.""")

    field = Instrument.measurement(
        "RDGF?", """Measure the output field (field constant times output current)."""
    )

    heater_parameters = Instrument.measurement(
        "PSHS?",
        """Get the persistent switch heater parameters [enabled, current in mA, delay in s].""",
        get_process_list=list,
    )

    error_status = Instrument.measurement(
        "ERST?",
        """Get the raw error registers "hardware,operational,PSH".""",
        cast=int,
        get_process_list=lambda v: ",".join(f"{x:03d}" for x in v),
    )

    operation_status = Instrument.measurement(
        "OPST?",
        """Get the operational status register (4 PSH stable, 2 ramp done,
        1 compliance).""",
        cast=int,
    )

    # Controls ---------------------------------------------------------------------------------

    current_setpoint = Instrument.control(
        "SETI?",
        "SETI %g",
        """Control the output current setpoint in A (no heater interlock).""",
        validator=strict_range,
        values=[-60.1, 60.1],
    )

    ramp_rate = Instrument.control(
        "RATE?",
        "RATE %g",
        """Control the output current ramp rate in A/s.""",
        validator=strict_range,
        values=[0.0001, 99.999],
    )

    current_limit = Instrument.control(
        "LIMIT?",
        "LIMIT %g",
        """Control the output current limit in A.""",
    )

    _field_setpoint = Instrument.control(
        "SETF?",
        "SETF %g",
        """Control the field setpoint without querying the heater; locked by the last known
        heater state.""",
        validator=heater_interlocked_range,
        values=None,
        dynamic=True,
    )

    _persistent_heater = Instrument.control(
        "PSH?",
        "PSH %d",
        """Control the persistent switch heater without updating the interlock.""",
        validator=_settable_heater_state,
        values=HEATER_STATES,
        map_values=True,
    )

    @property
    def persistent_heater(self):
        """Control the persistent switch heater ("off" or "on"; reading can also return
        "warming" or "cooling"). Reading updates the field setpoint interlock; setting "off"
        locks it immediately, setting "on" leaves it locked until a read reports "on"."""
        state = self._persistent_heater
        self._field_setpoint_values = self._field_range if state == "on" else None
        return state

    @persistent_heater.setter
    def persistent_heater(self, state):
        self._persistent_heater = state
        if state == "off":
            self._field_setpoint_values = None

    @property
    def field_setpoint(self):
        """Control the field setpoint in T. Every write first queries the heater (PSH?) and is
        refused unless the heater is on."""
        return self._field_setpoint

    @field_setpoint.setter
    def field_setpoint(self, value):
        self.persistent_heater  # noqa: B018
        self._field_setpoint = value

    # Methods ----------------------------------------------------------------------------------

    def stop_ramp(self):
        """Stop the output ramp; the supply holds the present current within 2 s."""
        self.write("STOP")

    def check_errors(self):
        """Query ``ERST?``; raise :class:`MagnetFaultError` on a fatal error, log the rest.

        Non-fatal errors are logged once per change of the error registers.

        :returns: List of active error messages.
        """
        reply = self.ask("ERST?")
        hardware, operational, psh, messages = decode_errors(reply)
        if _is_fatal(hardware, operational, psh):
            raise MagnetFaultError(f"{self.name}: {', '.join(messages)} (ERST? {reply})")
        if messages and reply != self._last_error_reply:
            log.warning("%s: %s", self.name, ", ".join(messages))
        self._last_error_reply = reply
        return messages

    def wait_for_heater(self, state="on", timeout_s=None, poll_s=1.0):
        """Block until the heater reports ``state`` and the switch is stable (OPST? bit 2).

        :param state: "on" or "off".
        :param timeout_s: Timeout in s; default is twice the heater delay (PSHS?) plus 10 s.
        :param poll_s: Polling interval in s.
        :raises TimeoutError: If the state is not reached in time.
        """
        strict_discrete_set(state, ["off", "on"])
        if timeout_s is None:
            timeout_s = 2 * self.heater_parameters[2] + 10
        start = time.perf_counter()
        while True:
            if self.persistent_heater == state and self.operation_status & OPST_PSH_STABLE:
                return
            if time.perf_counter() - start > timeout_s:
                raise TimeoutError(f"{self.name}: heater not '{state}' after {timeout_s} s")
            time.sleep(poll_s)

    def set_field_blocking(
        self, field, timeout_s=None, stall_s=30.0, min_poll=0.5, max_poll=10.0, tolerance=1e-3
    ):
        """Ramp to ``field`` (T) and block until the ramp is done.

        The ramp is done when OPST? has ramp done and PSH stable set and the measured field is
        within ``tolerance`` of the target. The polling interval is half the estimated time
        to the target, clamped to [``min_poll``, ``max_poll``]; ``min_poll`` is used while the
        ramp rate is unknown.

        :param field: Target field in T.
        :param timeout_s: Overall timeout in s (None: no overall timeout).
        :param stall_s: Stop if the field has not moved by more than ``tolerance`` for this
            long.
        :param min_poll: Shortest polling interval in s.
        :param max_poll: Longest polling interval in s.
        :param tolerance: Field tolerance in T.
        :raises MagnetFaultError: On a fatal error before or during the ramp (no STOP sent).
        :raises TimeoutError: On a stall or timeout (after sending STOP).
        :raises ValueError: If the heater interlock or the field range refuses the setpoint.
        """
        self.check_errors()
        if self.persistent_heater == "warming":
            self.wait_for_heater("on")
        start_field = self.field
        log.info("%s: ramping field from %g T to %g T", self.name, start_field, field)
        self.field_setpoint = field
        start = time.perf_counter()
        last_t, last_b = start, start_field
        progress_t, progress_b = start, start_field
        while True:
            status = int(self.ask("OPST?", query_delay=self.ramp_status_query_delay))
            b = self.field
            t = time.perf_counter()
            self.check_errors()
            if (status & OPST_DONE_MASK) == OPST_DONE_MASK and abs(b - field) <= tolerance:
                log.info("%s: field ramp finished in %.2f s", self.name, t - start)
                return
            if abs(b - progress_b) > tolerance:
                progress_t, progress_b = t, b
            if timeout_s is not None and t - start > timeout_s:
                self.stop_ramp()
                raise TimeoutError(
                    f"{self.name}: field ramp timed out after {t - start:.1f} s "
                    f"at {b} T (target {field} T)"
                )
            if t - progress_t > stall_s:
                self.stop_ramp()
                raise TimeoutError(
                    f"{self.name}: field ramp stalled at {b} T for "
                    f"{t - progress_t:.1f} s (target {field} T)"
                )
            rate = abs(b - last_b) / (t - last_t) if t > last_t else 0.0
            if rate > 0:
                interval = min(max(0.5 * abs(field - b) / rate, min_poll), max_poll)
            else:
                interval = min_poll
            last_t, last_b = t, b
            time.sleep(interval)
