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

import math
from time import time

from pymeasure.instruments import Instrument
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from pyvisa.errors import VisaIOError


def _normalize_inf_input(value):
    """Normalize INF-like setter values."""
    if isinstance(value, str):
        text = value.strip().strip('"').upper()
        if text in {"INF", "INFINITY", "+INF", "+INFINITY"}:
            return float("inf")
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return value
    if math.isinf(numeric):
        return float("inf")
    return numeric


def _normalize_inf_response(value):
    """Normalize INF-like instrument responses."""
    normalized = _normalize_inf_input(value)
    if isinstance(normalized, str):
        return normalized
    if normalized >= 1e20:
        return float("inf")
    return normalized


def _set_inf_or_numeric(value):
    """Format a value for SCPI setters accepting finite values and INF."""
    numeric = _normalize_inf_input(value)
    if isinstance(numeric, str):
        raise ValueError(f"Unsupported value '{value}'.")
    if math.isinf(numeric):
        return "INF"
    return f"{numeric:g}"


def _validate_output_load(value, values):
    """Validate finite output load or INF-like values."""
    normalized = _normalize_inf_input(value)
    if isinstance(normalized, str):
        raise ValueError(f"Output load '{value}' is not numeric and not INF-like.")
    if math.isinf(normalized):
        return float("inf")
    return strict_range(normalized, values)


def _get_output_load(value):
    """Parse output load response to float or infinity."""
    normalized = _normalize_inf_response(value)
    if isinstance(normalized, str):
        raise ValueError(f"Unexpected OUTP:LOAD response '{value}'.")
    if math.isinf(normalized):
        return float("inf")
    return float(normalized)


def _validate_burst_ncycles(value, _values):
    """Validate finite burst cycle count or INF-like values."""
    normalized = _normalize_inf_input(value)
    if isinstance(normalized, str):
        raise ValueError(f"Burst cycles '{value}' is not numeric and not INF-like.")
    if math.isinf(normalized):
        return "INF"
    if not float(normalized).is_integer():
        raise ValueError(f"Burst cycles '{value}' is not an integer.")
    ncycles = int(normalized)
    if not 1 <= ncycles <= 1_000_000:
        raise ValueError("Burst cycles must be in range [1, 1000000] or INF.")
    return ncycles


def _set_burst_ncycles(value):
    """Format burst cycle count for SCPI setter."""
    if isinstance(value, str) and value.upper() == "INF":
        return "INF"
    normalized = _normalize_inf_input(value)
    if isinstance(normalized, str):
        raise ValueError(f"Unsupported burst cycles value '{value}'.")
    if math.isinf(normalized):
        return "INF"
    return str(int(normalized))


def _get_burst_ncycles(value):
    """Parse burst cycle count response to int or INF."""
    normalized = _normalize_inf_response(value)
    if isinstance(normalized, str):
        raise ValueError(f"Unexpected BURS:NCYC response '{value}'.")
    if math.isinf(normalized):
        return "INF"
    return int(float(normalized))


class Agilent33250A(SCPIMixin, Instrument):
    """Represents the Agilent 33250A 80 MHz Function/Arbitrary Waveform Generator."""

    def __init__(self, adapter, name="Agilent 33250A Function/Arbitrary Waveform Generator",
                 **kwargs):
        super().__init__(adapter, name, **kwargs)

    shape = Instrument.control(
        "FUNC?", "FUNC %s",
        """Control the output waveform shape.""",
        validator=strict_discrete_set,
        values=["SIN", "SQU", "RAMP", "PULS", "NOIS", "DC", "USER"],
    )

    frequency = Instrument.control(
        "FREQ?", "FREQ %g",
        """Control the frequency of the output waveform in Hz (float, strict from 1e-6 to
        80e6). Function-dependent limits apply: SIN/SQU 1e-6 to 80e6, RAMP 1e-6 to 1e6,
        PULS 500e-6 to 50e6, USER/ARB 1e-6 to 25e6.""",
        validator=strict_range,
        values=[1e-6, 80e6],
    )

    amplitude = Instrument.control(
        "VOLT?", "VOLT %f",
        """Control the output amplitude.""",
        validator=strict_range,
        values=[1e-3, 10],
    )

    amplitude_unit = Instrument.control(
        "VOLT:UNIT?", "VOLT:UNIT %s",
        """Control the output amplitude unit.""",
        validator=strict_discrete_set,
        values=["VPP", "VRMS", "DBM"],
    )

    offset = Instrument.control(
        "VOLT:OFFS?", "VOLT:OFFS %f",
        """Control the DC offset voltage.""",
        validator=strict_range,
        values=[-5, 5],
    )

    voltage_high = Instrument.control(
        "VOLT:HIGH?", "VOLT:HIGH %f",
        """Control the high voltage level.""",
        validator=strict_range,
        values=[-5, 5],
    )

    voltage_low = Instrument.control(
        "VOLT:LOW?", "VOLT:LOW %f",
        """Control the low voltage level.""",
        validator=strict_range,
        values=[-5, 5],
    )

    square_dutycycle = Instrument.control(
        "FUNC:SQU:DCYC?", "FUNC:SQU:DCYC %g",
        """Control the duty cycle of a square waveform function in percent
        (float, strict from 20 to 80). Additional frequency-dependent limits apply:
        20-80% below 25 MHz, 40-60% from 25 to 50 MHz, and 50% above 50 MHz.""",
        validator=strict_range,
        values=[20, 80],
    )

    ramp_symmetry = Instrument.control(
        "FUNC:RAMP:SYMM?", "FUNC:RAMP:SYMM %f",
        """Control the ramp waveform symmetry in percent.""",
        validator=strict_range,
        values=[0, 100],
    )

    pulse_period = Instrument.control(
        "PULS:PER?", "PULS:PER %g",
        """Control the period of a pulse waveform function in seconds
        (float, strict from 20e-9 to 2000).""",
        validator=strict_range,
        values=[20e-9, 2000],
    )

    pulse_width = Instrument.control(
        "PULS:WIDT?", "PULS:WIDT %g",
        """Control the width of a pulse waveform function in seconds
        (float, strict from 8e-9 to 2000).""",
        validator=strict_range,
        values=[8e-9, 2000],
    )

    pulse_transition = Instrument.control(
        "PULS:TRAN?", "PULS:TRAN %g",
        """Control the edge time in seconds for both the rising and falling edges
        (float, strict from 5e-9 to 1e-3).""",
        validator=strict_range,
        values=[5e-9, 1e-3],
    )

    burst_ncycles = Instrument.control(
        "BURS:NCYC?", "BURS:NCYC %s",
        """Control the number of cycles output when a burst is triggered
        (int, strict from 1 to 1000000, or INF).""",
        validator=_validate_burst_ncycles,
        values=[1, 1_000_000],
        set_process=_set_burst_ncycles,
        get_process=_get_burst_ncycles,
        cast=str,
    )

    output_load = Instrument.control(
        "OUTP:LOAD?", "OUTP:LOAD %s",
        """Control the expected output load resistance in Ohms
        (float, strict from 1 to 10000, or INF).""",
        validator=_validate_output_load,
        values=[1, 10000],
        set_process=_set_inf_or_numeric,
        get_process=_get_output_load,
        cast=str,
    )

    output_enabled = Instrument.control(
        "OUTP?", "OUTP %d",
        """Control whether the main output is enabled (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    output_polarity = Instrument.control(
        "OUTP:POL?", "OUTP:POL %s",
        """Control the output polarity (string, strict from NORM, INV).""",
        validator=strict_discrete_set,
        values=["NORM", "INV"],
    )

    sync_output_enabled = Instrument.control(
        "OUTP:SYNC?", "OUTP:SYNC %d",
        """Control whether the sync output is enabled (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    burst_enabled = Instrument.control(
        "BURS:STAT?", "BURS:STAT %d",
        """Control whether burst mode is enabled (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    burst_mode = Instrument.control(
        "BURS:MODE?", "BURS:MODE %s",
        """Control the burst mode.""",
        validator=strict_discrete_set,
        values=["TRIG", "GAT"],
    )

    burst_period = Instrument.control(
        "BURS:INT:PER?", "BURS:INT:PER %g",
        """Control the period of subsequent bursts in seconds
        (float, strict from 1e-6 to 500).""",
        validator=strict_range,
        values=[1e-6, 500],
    )

    burst_phase = Instrument.control(
        "BURS:PHAS?", "BURS:PHAS %g",
        """Control the start phase for burst mode in degrees
        (float, strict from -360 to 360).""",
        validator=strict_range,
        values=[-360, 360],
    )

    trigger_delay = Instrument.control(
        "TRIG:DEL?", "TRIG:DEL %g",
        """Control the trigger delay in seconds (float, strict from 0 to 85).""",
        validator=strict_range,
        values=[0, 85],
    )

    trigger_slope = Instrument.control(
        "TRIG:SLOP?", "TRIG:SLOP %s",
        """Control the external trigger slope (string, strict from POS, NEG).""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
    )

    trigger_output_enabled = Instrument.control(
        "OUTP:TRIG?", "OUTP:TRIG %d",
        """Control whether trigger output is enabled (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    trigger_output_slope = Instrument.control(
        "OUTP:TRIG:SLOP?", "OUTP:TRIG:SLOP %s",
        """Control the trigger output slope (string, strict from POS, NEG).""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
    )

    trigger_source = Instrument.control(
        "TRIG:SOUR?", "TRIG:SOUR %s",
        """Control the trigger source.""",
        validator=strict_discrete_set,
        values=["IMM", "EXT", "BUS"],
    )

    def trigger(self):
        """Send a trigger signal to the function generator."""
        self.write("*TRG;*WAI")

    def wait_for_trigger(self, timeout=3600, should_stop=lambda: False):
        """Wait until the triggering has finished or timeout is reached."""
        self.write("*OPC?")

        t0 = time()
        while True:
            try:
                ready = bool(self.read())
            except VisaIOError:
                ready = False

            if ready:
                return

            if timeout != 0 and time() - t0 > timeout:
                raise TimeoutError(
                    "Timeout expired while waiting for the Agilent 33250A to finish the "
                    "triggering."
                )

            if should_stop():
                return

    def beep(self):
        """Cause a system beep."""
        self.write("SYST:BEEP")
