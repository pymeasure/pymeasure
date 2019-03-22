#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set,\
    strict_range, joined_validators
from time import time
from pyvisa.errors import VisaIOError


# Capitalize string arguments to allow for better conformity with other WFG's
def capitalize_string(string: str, *args, **kwargs):
    return string.upper()


# Combine the capitalize function and validator
string_validator = joined_validators(capitalize_string, strict_discrete_set)


class Agilent33220A(Instrument):
    """Represents the Agilent 33220A Arbitrary Waveform Generator.

    .. code-block:: python
        # Default channel for the Agilent 33220A
        wfg = Agilent33220A("GPIB::10")

        wfg.shape = "SINUSOID"          # Sets a sine waveform
        wfg.frequency = 4.7e3           # Sets the frequency to 4.7 kHz
        wfg.amplitude = 1               # Set amplitude of 1 V
        wfg.offset = 0                  # Set the amplitude to 0 V

        wfg.burst = True                # Enable burst mode
        wfg.burst_ncycles = 10e3        # A burst will consist of 10 cycles
        wfg.burst_mode = "TRIGGERED"    # A burst will be applied on a trigger
        wfg.trigger_source = "BUS"      # A burst will be triggered on TRG*

        wfg.output = True               # Enable output of waveform generator
        wfg.trigger()                   # Trigger a burst
        wfg.wait_for_trigger()          # Wait until the triggering is finished
        wfg.beep()                      # "beep"

        wfg.check_errors()              # Get the error queue

    """

    def __init__(self, adapter, **kwargs):
        super(Agilent33220A, self).__init__(
            adapter,
            "Agilent 33220A Arbitrary Waveform generator",
            **kwargs
        )

    shape = Instrument.control(
        "FUNC?", "FUNC %s",
        """ A string property that controls the output waveform. Can be set to:
        SIN<USOID>, SQU<ARE>, RAMP, PULS<E>, NOIS<E>, DC, USER. """,
        validator=string_validator,
        values=["SINUSOID", "SIN", "SQUARE", "SQU", "RAMP",
                "PULSE", "PULS", "NOISE", "NOIS", "DC", "USER"],
    )

    frequency = Instrument.control(
        "FREQ?", "FREQ %s",
        """ A floating point property that controls the frequency of the output
        waveform in Hz, from 1e-6 (1 uHz) to 20e+6 (20 MHz), depending on the
        specified function. Can be set. """,
        validator=strict_range,
        values=[1e-6, 5e+6],
    )

    amplitude = Instrument.control(
        "VOLT?", "VOLT %f",
        """ A floating point property that controls the voltage amplitude of the
        output waveform in V, from 10e-3 V to 10 V. Can be set. """,
        validator=strict_range,
        values=[10e-3, 10],
    )

    amplitude_unit = Instrument.control(
        "VOLT:UNIT?", "VOLT:UNIT %s",
        """ A string property that controls the units of the amplitude. Valid
        values are Vpp (default), Vrms, and dBm. Can be set. """,
        validator=string_validator,
        values=["VPP", "VRMS", "DBM"],
    )

    offset = Instrument.control(
        "VOLT:OFFS?", "VOLT:OFFS %f",
        """ A floating point property that controls the voltage offset of the
        output waveform in V, from 0 V to 4.995 V, depending on the set
        voltage amplitude (maximum offset = (10 - voltage) / 2). Can be set.
        """,
        validator=strict_range,
        values=[-4.995, +4.995],
    )

    voltage_high = Instrument.control(
        "VOLT:HIGH?", "VOLT:HIGH %f",
        """ A floating point property that controls the upper voltage of the
        output waveform in V, from -4.990 V to 5 V (must be higher than low
        voltage). Can be set. """,
        validator=strict_range,
        values=[-4.99, 5],
    )

    voltage_low = Instrument.control(
        "VOLT:LOW?", "VOLT:LOW %f",
        """ A floating point property that controls the lower voltage of the
        output waveform in V, from -5 V to 4.990 V (must be lower than high
        voltage). Can be set. """,
        validator=strict_range,
        values=[-5, 4.99],
    )

    square_dutycycle = Instrument.control(
        "FUNC:SQU:DCYC?", "FUNC:SQU:DCYC %f",
        """ A floating point property that controls the duty cycle of a square
        waveform function in percent. Can be set. """,
        validator=strict_range,
        values=[20, 80],
    )

    ramp_symmetry = Instrument.control(
        "FUNC:RAMP:SYMM?", "FUNC:RAMP:SYMM %f",
        """ A floating point property that controls the symmetry percentage
        for the ramp waveform. Can be set. """,
        validator=strict_range,
        values=[0, 100],
    )

    pulse_period = Instrument.control(
        "PULS:PER?", "PULS:PER %f",
        """ A floating point property that controls the period of a pulse
        waveform function in seconds, ranging from 200 ns to 2000 s. Can be set
        and overwrites the frequency for *all* waveforms. If the period is
        shorter than the pulse width + the edge time, the edge time and pulse
        width will be adjusted accordingly. """,
        validator=strict_range,
        values=[200e-9, 2e3],
    )

    pulse_hold = Instrument.control(
        "FUNC:PULS:HOLD?", "FUNC:PULS:HOLD %s",
        """ A string property that controls if either the pulse width or the
        duty cycle is retained when changing the period or frequency of the
        waveform. Can be set to: WIDT<H> or DCYC<LE>. """,
        validator=string_validator,
        values=["WIDT", "WIDTH", "DCYC", "DCYCLE"],
    )

    pulse_width = Instrument.control(
        "FUNC:PULS:WIDT?", "FUNC:PULS:WIDT %f",
        """ A floating point property that controls the width of a pulse
        waveform function in seconds, ranging from 20 ns to 2000 s, within a
        set of restrictions depending on the period. Can be set. """,
        validator=strict_range,
        values=[20e-9, 2e3],
    )

    pulse_dutycycle = Instrument.control(
        "FUNC:PULS:DCYC?", "FUNC:PULS:DCYC %f",
        """ A floating point property that controls the duty cycle of a pulse
        waveform function in percent. Can be set. """,
        validator=strict_range,
        values=[0, 100],
    )

    pulse_transition = Instrument.control(
        "FUNC:PULS:TRAN?", "FUNC:PULS:TRAN %f",
        """ A floating point property that controls the the edge time in
        seconds for both the rising and falling edges. It is defined as the
        time between 0.1 and 0.9 of the threshold. Valid values are between
        5 ns to 100 ns. Can be set. """,
        validator=strict_range,
        values=[5e-9, 100e-9],
    )

    output = Instrument.control(
        "OUTP?", "OUTP %d",
        """ A boolean property that turns on (True) or off (False) the output
        of the function generator. Can be set. """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    burst_state = Instrument.control(
        "BURS:STAT?", "BURS:STAT %d",
        """ A boolean property that controls whether the burst mode is on
        (True) or off (False). Can be set. """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    burst_mode = Instrument.control(
        "BURS:MODE?", "BURS:MODE %s",
        """ A string property that controls the burst mode. Valid values
        are: TRIG<GERED>, GAT<ED>. This setting can be set. """,
        validator=string_validator,
        values=["TRIG", "TRIGGERED", "GAT", "GATED"],
    )

    burst_ncycles = Instrument.control(
        "BURS:NCYC?", "BURS:NCYC %d",
        """ An integer property that sets the number of cycles to be output
        when a burst is triggered. Valid values are 1 to 50000. This can be
        set. """,
        validator=strict_discrete_set,
        values=range(1, 50001),
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
                    "Timeout expired while waiting for the Agilent 33220A" +
                    " to finish the triggering."
                )

            if should_stop:
                return

    trigger_source = Instrument.control(
        "TRIG:SOUR?", "TRIG:SOUR %s",
        """ A string property that controls the trigger source. Valid values
        are: IMM<EDIATE> (internal), EXT<ERNAL> (rear input), BUS (via trigger
        command). This setting can be set. """,
        validator=string_validator,
        values=["IMM", "IMMEDIATE", "EXT", "EXTERNAL", "BUS"],
    )

    trigger_state = Instrument.control(
        "OUTP:TRIG?", "OUTP:TRIG %d",
        """ A boolean property that controls whether the output is triggered
        (True) or not (False). Can be set. """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    remote_local_state = Instrument.setting(
        "SYST:COMM:RLST %s",
        """ A string property that controls the remote/local state of the
        function generator. Valid values are: LOC<AL>, REM<OTE>, RWL<OCK>.
        This setting can only be set. """,
        validator=string_validator,
        values=["LOC", "LOCAL", "REM", "REMOTE", "RWL", "RWLOCK"],
    )

    def check_errors(self):
        """ Read all errors from the instrument. """

        errors = []
        while True:
            err = self.values("SYST:ERR?")
            if int(err[0]) != 0:
                errmsg = "Agilent 33220A: %s: %s" % (err[0], err[1])
                log.error(errmsg + '\n')
                errors.append(errmsg)
            else:
                break

        return errors

    beeper_state = Instrument.control(
        "SYST:BEEP:STAT?", "SYST:BEEP:STAT %d",
        """ A boolean property that controls the state of the beeper. Can
        be set. """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    def beep(self):
        """ Causes a system beep. """
        self.write("SYST:BEEP")
