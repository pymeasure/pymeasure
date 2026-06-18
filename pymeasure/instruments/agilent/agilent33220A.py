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

from pymeasure.instruments import Instrument, SCPIUnknownMixin
from pymeasure.instruments.validators import strict_discrete_set, \
    strict_range, joined_validators
from time import time
from pyvisa.errors import VisaIOError

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# Capitalize string arguments to allow for better conformity with other WFG's
def capitalize_string(string: str, *args, **kwargs):
    return string.upper()


# Combine the capitalize function and validator
string_validator = joined_validators(capitalize_string, strict_discrete_set)


class Agilent33220A(SCPIUnknownMixin, Instrument):
    """Represents the Agilent 33220A Arbitrary Waveform Generator.

    .. code-block:: python

        # Default channel for the Agilent 33220A
        wfg = Agilent33220A("GPIB::10")

        wfg.shape = "SINUSOID"          # Sets a sine waveform
        wfg.frequency = 4.7e3           # Sets the frequency to 4.7 kHz
        wfg.amplitude = 1               # Set amplitude of 1 V
        wfg.offset = 0                  # Set the amplitude to 0 V

        wfg.burst_state = True          # Enable burst mode
        wfg.burst_ncycles = 10          # A burst will consist of 10 cycles
        wfg.burst_mode = "TRIGGERED"    # A burst will be applied on a trigger
        wfg.trigger_source = "BUS"      # A burst will be triggered on TRG*

        wfg.output = True               # Enable output of waveform generator
        wfg.trigger()                   # Trigger a burst
        wfg.wait_for_trigger()          # Wait until the triggering is finished
        wfg.beep()                      # "beep"

        print(wfg.check_errors())       # Get the error queue

    """

    def __init__(self, adapter, name="Agilent 33220A Arbitrary Waveform generator", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    shape = Instrument.control(
        "FUNC?", "FUNC %s",
        """Control the output waveform (string, strict from SINUSOID, SIN, SQUARE, SQU, RAMP, PULSE,
        PULS, NOISE, NOIS, DC, USER).""",
        validator=joined_validators(
            strict_discrete_set, string_validator
        ),
        values=[["SINUSOID", "SIN", "SQUARE", "SQU", "RAMP",
                "PULSE", "PULS", "NOISE", "NOIS", "DC", "USER"], ],
    )

    frequency = Instrument.control(
        "FREQ?", "FREQ %f",
        """Control the frequency of the output waveform. Depending on the output shape, the
        supported frequency range changes. Supplying out-of-bound values may silently be clipped
        by the device (float, in Hz)"""
    )

    amplitude = Instrument.control(
        "VOLT?", "VOLT %f",
        """Control the amplitude of the output waveform. Depending on amplitude unit, the unit
        is Volt (peak-to-peak), Volt (RMS) or dBm. The limits depend on the configured output
        termination (50 Ohm to High Impedance changes by a factor of 2) and the offset.
        Supplying out-of-bound values may silently be clipped by the device (float, in V or dBm)"""
    )

    amplitude_unit = Instrument.control(
        "VOLT:UNIT?", "VOLT:UNIT %s",
        """Control the units of the amplitude (string, strict from VPP, VRMS, DBM).""",
        validator=joined_validators(
            strict_discrete_set, string_validator
        ),
        values=[["VPP", "VRMS", "DBM"], ],
    )

    offset = Instrument.control(
        "VOLT:OFFS?", "VOLT:OFFS %f",
        """Control the voltage offset of the output waveform. This is limited by the amplitude
        and output termination. Supplying out-of-bound values may silently be clipped by the
        device. (float, in V)"""
    )

    voltage_high = Instrument.control(
        "VOLT:HIGH?", "VOLT:HIGH %f",
        """Control the upper voltage of the output waveform. The limits depend on the output
        termination. Supplying out-of-bound values may silently be clipped by the
        device. (float, in V)"""
    )

    voltage_low = Instrument.control(
        "VOLT:LOW?", "VOLT:LOW %f",
        """Control the lower voltage of the output waveform. The limits depend on the output
        termination. Supplying out-of-bound values may silently be clipped by the
        device. (float, in V)"""
    )

    square_dutycycle = Instrument.control(
        "FUNC:SQU:DCYC?", "FUNC:SQU:DCYC %f",
        """Control the duty cycle of a square waveform function (float, strict from 20 to 80).""",
        validator=strict_range,
        values=[20, 80],
    )

    ramp_symmetry = Instrument.control(
        "FUNC:RAMP:SYMM?", "FUNC:RAMP:SYMM %f",
        """Control the symmetry percentage for the ramp waveform (float, strict from 0 to 100).""",
        validator=strict_range,
        values=[0, 100],
    )

    pulse_period = Instrument.control(
        "PULS:PER?", "PULS:PER %f",
        """Control the period of a pulse waveform function in seconds
        (float, strict from 200e-9 to 2e3). The period overwrites the frequency for all waveforms.
        If the period is shorter than the pulse width + the edge time, the edge time and pulse
        width will be adjusted accordingly.""",
        validator=strict_range,
        values=[200e-9, 2e3],
    )

    pulse_hold = Instrument.control(
        "FUNC:PULS:HOLD?", "FUNC:PULS:HOLD %s",
        """Control if either the pulse width or the duty cycle is retained when changing the period
        or frequency of the waveform (string, strict from WIDT, WIDTH, DCYC, DCYCLE).""",
        validator=joined_validators(
            strict_discrete_set, string_validator
        ),
        values=[["WIDT", "WIDTH", "DCYC", "DCYCLE"], ],
    )

    pulse_width = Instrument.control(
        "FUNC:PULS:WIDT?", "FUNC:PULS:WIDT %f",
        """Control the width of a pulse waveform function in seconds
        (float, strict from 20e-9 to 2e3).""",
        validator=strict_range,
        values=[20e-9, 2e3],
    )

    pulse_dutycycle = Instrument.control(
        "FUNC:PULS:DCYC?", "FUNC:PULS:DCYC %f",
        """Control the duty cycle of a pulse waveform function in percent
        (float, strict from 0 to 100).""",
        validator=strict_range,
        values=[0, 100],
    )

    pulse_transition = Instrument.control(
        "FUNC:PULS:TRAN?", "FUNC:PULS:TRAN %g",
        """Control the edge time in
        seconds for both the rising and falling edges. It is defined as the
        time between 0.1 and 0.9 of the threshold. Valid values are between
        5 ns to 100 ns. The transition time has to be smaller than
        0.625 * the pulse width.""",
        validator=strict_range,
        values=[5e-9, 100e-9],
    )

    output = Instrument.control(
        "OUTP?", "OUTP %d",
        """Control the output of the function generator (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    burst_state = Instrument.control(
        "BURS:STAT?", "BURS:STAT %d",
        """Control whether the burst mode is on (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    burst_mode = Instrument.control(
        "BURS:MODE?", "BURS:MODE %s",
        """Control the burst mode (string, strict from TRIG, TRIGGERED, GAT, GATED).""",
        validator=joined_validators(
            strict_discrete_set, string_validator
        ),
        values=[["TRIG", "TRIGGERED", "GAT", "GATED"], ],
    )

    burst_ncycles = Instrument.control(
        "BURS:NCYC?", "BURS:NCYC %d",
        """Control the number of cycles to be output when a burst is triggered
        (int, strict from 1 to 50000).""",
        validator=strict_discrete_set,
        values=range(1, 50001),
        cast=lambda v: int(float(v))
    )

    def trigger(self):
        """ Send a trigger signal to the function generator. """
        self.write("*TRG;*WAI")

    def wait_for_trigger(self, timeout=3600, should_stop=lambda: False):
        """ Wait until the triggering has finished or timeout is reached.

        :param timeout: The maximum time the waiting is allowed to take. If
                        timeout is exceeded, a TimeoutError is raised. If
                        timeout is set to zero, no timeout will be used.
        :param should_stop: Optional function (returning a bool) to allow the
                            waiting to be stopped before its end.

        """
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
                    "Timeout expired while waiting for the Agilent 33220A to finish the triggering."
                )

            if should_stop():
                return

    trigger_source = Instrument.control(
        "TRIG:SOUR?", "TRIG:SOUR %s",
        """Control the trigger source (string, strict from IMM, IMMEDIATE, EXT, EXTERNAL, BUS).""",
        validator=joined_validators(
            strict_discrete_set, string_validator
        ),
        values=[["IMM", "IMMEDIATE", "EXT", "EXTERNAL", "BUS"], ],
    )

    trigger_state = Instrument.control(
        "OUTP:TRIG?", "OUTP:TRIG %d",
        """Control whether the output is triggered (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    remote_local_state = Instrument.setting(
        "SYST:COMM:RLST %s",
        """Set the remote/local state of the function generator
        (string, strict from LOC, LOCAL, REM, REMOTE, RWL, RWLOCK).""",
        validator=joined_validators(
            strict_discrete_set, string_validator
        ),
        values=[["LOC", "LOCAL", "REM", "REMOTE", "RWL", "RWLOCK"], ],
    )

    beeper_state = Instrument.control(
        "SYST:BEEP:STAT?", "SYST:BEEP:STAT %d",
        """Control the state of the beeper (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    def beep(self):
        """ Causes a system beep. """
        self.write("SYST:BEEP")
