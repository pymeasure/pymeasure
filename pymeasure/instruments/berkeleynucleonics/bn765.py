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



class BN765(Instrument):
    """Represents the Berkeley Nucleonics 765 800 MHz waveform generator.
    Individual devices are represented by subclasses.

    .. code-block:: python

        generator = BN765("GPIB::1")

        generator.shape = 'SIN'                 # Sets the output signal shape to sine
        generator.frequency = 1e3               # Sets the output frequency to 1 kHz
        generator.amplitude = 5                 # Sets the output amplitude to 5 Vpp
        generator.output = 'on'                 # Enables the output

        generator.shape = 'ARB'                 # Set shape to arbitrary
        generator.arb_srate = 1e6               # Set sample rate to 1MSa/s

        generator.data_volatile_clear()         # Clear volatile internal memory
        generator.data_arb(                     # Send data points of arbitrary waveform
            'test',
            range(-10000, 10000, +20),          # In this case a simple ramp
            data_format='DAC'                   # Data format is set to 'DAC'
        )
        generator.arb_file = 'test'             # Select the transmitted waveform 'test'

    """

    id = Instrument.measurement(
        "*IDN?", """ Reads the instrument identification """
    )

    def __init__(self, adapter, **kwargs):
        super(BN765, self).__init__(
            adapter,
            "BN 765 Function/Arbitrary Waveform generator",
            **kwargs
        )



    output1 = Instrument.control(
        "OUTPut1:STATe?", "OUTPut1:STATe %s",
        """ A boolean property that turns on (True, 'on') or off (False, 'off') 
        the output 1 of the function generator. Can be set. """,
        validator=strict_discrete_set,
        values={'ON',  'OFF'},
    )

    output1_pulse_mode = Instrument.control(
        "OUTPut1:PULSe:MODE?", "OUTPut1:PULSe:MODE %s",
        """ A string control that sets how many pulses will be available for output 1.
         Options are SIN (single), DOU (double), TRI (triple), QUAD (quadruple).""",
        validator=strict_discrete_set,
        values=['SIN', 'DOU', 'TRI', 'QUAD'],
    )

    source1_period = Instrument.control(
        "SOURce1:PERiod?", "SOURce1:PERiod %g",
        """ A floating point property that controls the period of the output1
        waveform function in seconds, ranging from 3e-5 s to 8 s. Can be set
        and overwrites the frequency for *all* waveforms. If the period is
        shorter than the pulse width + the edge time, the edge time and pulse
        width will be adjusted accordingly. """,
        validator=strict_range,
        values=[1.25e-9, 8],
    )

    source1_frequency = Instrument.control(
        "SOURce1:FREQuency?", "SOURce1:FREQuency %g",
        """ A floating point property that controls the frequency of the output1
        waveform function in Hz, ranging from 0.125 Hz to 1.25e8 Hz. Can be set
        and overwrites the frequency for *all* waveforms. If the period is
        shorter than the pulse width + the edge time, the edge time and pulse
        width will be adjusted accordingly. """,
        validator=strict_range,
        values=[.125, 1.25e8],
    )

    source1_burst_ncycles = Instrument.control(
        "SOURce1:BURS:NCYC?", "SOURce1:BURS:NCYC %d",
        """ An integer property that sets the number of cycles to be output
        when a burst is triggered. Valid values are 1 to 4294967295. This can be
        set. """,
        validator=strict_range,
        values=[1, 4294967295],
    )

    source1_initdelay = Instrument.control(
        "SOURce1:INITDELay?", "SOURce1:INITDELay %g",
        """ This parameter is the group delay from the Trigger IN signal that all
         the pulses associated to the output N have in common.""",
        validator=strict_range,
        values=[0, 1e6],
    )

    source1_invert = Instrument.control(
        "SOURce1:INV?", "SOURce1:INV %s",
        """ A boolean property that sets inversion on ('ON') or off ('OFF') 
        the output 1 of the function generator. Can be set. """,
        validator=strict_discrete_set,
        values=['ON', 'OFF'],
    )

    source1_amplitude = Instrument.control(
        "SOURce1:VOLT:LEV:IMM:AMPL?", "SOURce1:VOLT:LEV:IMM:AMPL %g",
        """ This control reads and sets the amplitude of the source 1 output. 
        Range is 0.01-5 V""",
        validator=strict_range,
        values=[0, 5],
    )

    source1_offset = Instrument.control(
        "SOURce1:VOLT:LEV:IMM:OFFS?", "SOURce1:VOLT:LEV:IMM:OFFS %g",
        """ This control reads and sets the DC offset of the source 1 output. 
        Range is -2.5 - +2.5 V""",
        validator=strict_range,
        values=[-2.5, 2.55],
    )

    source1_pulse1 = Instrument.control(
        "SOURce1:PULSe1:WIDTh?", "SOURce1:PULSe1:WIDTh %g",
        """ This sets and reads the width of pulse1. Pulse width must be less than the period""",
        validator=strict_range,
        values=[3e-10, 8],
    )

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
        self.write('PULSEGENControl:START')

    def disarm(self):
        """
        Stops and disarms the instrument. Does not modify output state.
        """
        self.write('PULSEGENControl:STOP')