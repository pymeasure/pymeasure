#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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

# Parts of this code were copied and adapted from the Agilent33220A class.

import logging
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set,\
    strict_range
from time import time
from pyvisa.errors import VisaIOError


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class Pulse():
    """ Implementation of a BN765 fast pulse on a given generator channel.
     """

    BOOLS = {True: 1, False: 0}

    width = Instrument.control(
        'width?', 'width %.10F',
        """Float parameter that contols the width of the pulse represented by this instance, on this
         instance of channel. Width must be less than pulse period"""
    )

    delay = Instrument.control(
        'delay?', 'delay %.10F',
        """Float paramer which controls the delay for the specified pulse relative
        to the selected output channel"""
    )

    dcycle = Instrument.control(
        'dcyle?', 'dcyle %.4E',
        """Float paramer which controls the duty cycle of the pulse for the given channel.
        Alternative way to set width."""
    )

    phase = Instrument.control(
        'phase?', 'phase %.4E',
        """Float paramer which controls the phase of the pulse for the given channel.
        Alternative way to set the delay."""
    )




    def __init__(self, instrument, pulse_number):
        self.instrument = instrument
        self.pulse_number = pulse_number


    def values(self, command, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values("pulse%d:%s" % (
             self.pulse_number, command), **kwargs)

    def ask(self, command):
        self.instrument.ask("pulse%d:%s" % (
            self.pulse_number, command))

    def write(self, command):
        self.instrument.write("pulse%d:%s" % (
            self.pulse_number, command))

class Channel():
    """ Implementation of a BN765 fast pulse generator channel.
     """

    BOOLS = {True: 1, False: 0}

    load_impedance = Instrument.control(
        'LOAD:IMP?', 'LOAD:IMP %.4E',
        """A mixed parameter that sets the load impedance. Any float between
        [50, 1e4] are allowed as well as 'MIN' and 'MAX'.""",
    )

    period = Instrument.control(
        "PERiod?", "PERiod %.9F",
        """ A floating point property that controls the period of the output1
        waveform function in seconds, ranging from 3e-5 s to 8 s. Can be set
        and overwrites the frequency for *all* waveforms. If the period is
        shorter than the pulse width + the edge time, the edge time and pulse
        width will be adjusted accordingly. """,
        validator=strict_range,
        values=[1.25e-9, 8],
    )

    frequency = Instrument.control(
        "FREQuency?", "FREQuency %g",
        """ A floating point property that controls the frequency of the output1
        waveform function in Hz, ranging from 0.125 Hz to 1.25e8 Hz. Can be set
        and overwrites the frequency for *all* waveforms. If the period is
        shorter than the pulse width + the edge time, the edge time and pulse
        width will be adjusted accordingly. """,
        validator=strict_range,
        values=[.125, 1.25e8],
    )

    burst_ncycles = Instrument.control(
        "BURS:NCYC?", "BURS:NCYC %d",
        """ An integer property that sets the number of cycles to be output
        when a burst is triggered. Valid values are 1 to 4294967295. This can be
        set. """,
        validator=strict_range,
        values=[1, 4294967295],
    )

    init_delay = Instrument.control(
        "INITDELay?", "INITDELay %g",
        """ This parameter is the group delay from the Trigger IN signal that all
         the pulses associated to the output N have in common.""",
        validator=strict_range,
        values=[0, 1e6],
    )

    invert = Instrument.control(
        "INV?", "INV %s",
        """ A boolean property that sets inversion on ('ON') or off ('OFF') 
        the output 1 of the function generator. Can be set. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    amplitude = Instrument.control(
        "VOLT:LEV:IMM:AMPL?", "VOLT:LEV:IMM:AMPL %g",
        """ This control reads and sets the amplitude of the source 1 output. 
        Range is 0.01-5 V""",
        validator=strict_range,
        values=[0, 5],
    )

    offset = Instrument.control(
        "VOLT:LEV:IMM:OFFS?", "VOLT:LEV:IMM:OFFS %g",
        """ This control reads and sets the DC offset of the source 1 output. 
        Range is -2.5 - +2.5 V""",
        validator=strict_range,
        values=[-2.5, 2.55],
    )

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number
        self.pulse1 = Pulse(self, 1)
        self.pulse2 = Pulse(self, 2)
        self.pulse3 = Pulse(self, 3)
        self.pulse4 = Pulse(self, 4)

    def values(self, command, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values(":source%d:%s" % (
            self.number, command), **kwargs)

    def ask(self, command):
        self.instrument.ask("source%d:%s" % (self.number, command))

    def write(self, command):
        self.instrument.write("source%d:%s" % (self.number, command))

    @property
    def output(self):
        mapper = {1: True, 0: False}
        out = int(self.instrument.ask("output%d?" % self.number))
        return mapper[out]

    @output.setter
    def output(self, state):
        mapper = {True: 'ON', False: 'OFF'}
        self.instrument.write("output%d %s" % (self.number, mapper[state]))

    @property
    def pulse_mode(self):
        mapper = {"EXTernalWIDth": 0, 'SINgle': 1, 'DOUble': 2, 'TRIple': 3, 'QUADruple': 4}
        out = self.instrument.ask("output%d:pulse:mode?" % self.number)
        return mapper[out]

    @pulse_mode.setter
    def pulse_mode(self, state):
        mapper = {0: "EXTernalWIDth", 1: 'SINgle', 2: 'DOUble', 3: 'TRIple', 4: 'QUADruple'}
        self.instrument.write("output%d:pulse:mode %s" % (self.number, mapper[state]))

class BN765(Instrument):
    """Represents the Berkeley Nucleonics 765 800 MHz waveform generator.
    Individual devices are represented by subclasses.

    .. code-block:: python

        generator = BN765('TCPIP0::169.254.26.15::inst0::INSTR')

    """

    id = Instrument.measurement(
        "*IDN?", """ Reads the instrument identification """
    )

    run_status = Instrument.measurement(
        "PULSEGENControl:STATus?",
        """Returns the instrument status, 0 if stopped, 1 if running"""
    )

    def __init__(self, adapter, **kwargs):
        super(BN765, self).__init__(
            adapter,
            "BN 765 Function/Arbitrary Waveform generator",
            **kwargs
        )

        nc = 0

        for i in range(0, 4):
            try:
                ret = self.ask("OUTP{:}:PULS:MODE?".format(str(i+1)))
            except VisaIOError:
                break

            if isinstance(ret, str):
                nc += 1
            else:
                break

        self.num_channels = nc

        if nc < 2:
            raise ValueError("PG has insufficient (< 2) channels for operation.")

        for c in range(1, nc+1):
            setattr(self, "ch{:}".format(str(c)), Channel(self, c))

    trigger_mode = Instrument.control(
        "TRIGger:SEQ:MODE?", "TRIGger:SEQ:MODE %s",
        """ Instrument string control to set the trigger mode to 'SIN' (single), 'BURS' (burst), 'GAT' (gated),
        or 'CONT' (continous).""",
        validator=strict_discrete_set,
        values=['SIN', 'BURS', 'GAT', 'CONT'],
    )

    trigger_source = Instrument.control(
        "TRIGger:SEQ:SOUR?", "TRIGger:SEQ:SOUR %s",
        """ Instrument string control to set the trigger source to 'TIM' (timer), 'EXT' (external), 'MAN' (manual).""",
        validator=strict_discrete_set,
        values=['TIM', 'EXT', 'MAN'],
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
                    "Timeout expired while waiting for the BN765" +
                    " to finish the triggering."
                )

            if should_stop:
                return

    def arm(self):
        """
        Arms the instrument to receive a trigger. Does not modify output state.
        """
        if self.run_status != 1:
            self.write('PULSEGENControl:START')

    def disarm(self):
        """
        Stops and disarms the instrument. Does not modify output state.
        """
        if self.run_status != 0:
            self.write('PULSEGENControl:STOP')