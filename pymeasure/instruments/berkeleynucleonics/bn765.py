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

class Channel():
    """ Implementation of a BN765 fast pulse generator channel.
     """

    BOOLS = {True: 1, False: 0}


    coupling = Instrument.control(
        "COUPling?", "COUPling %s",
        """ A string parameter that determines the coupling ("dc" only).
        The 90000A (Again there are four zeroes there) series oscilloscopes only
        have DC coupling at 50 Ohms impedance.""",
        validator=strict_discrete_set,
        values={"dc": "DC50"},
        map_values=True
    )

    display = Instrument.control(
        "DISPlay?", "DISPlay %d",
        """ A boolean parameter that toggles the display.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    invert = Instrument.control(
        "INVert?", "INVert %d",
        """ A boolean parameter that toggles the inversion of the input signal.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    label = Instrument.control(
        "LABel?", 'LABel "%s"',
        """ A string to label the channel. Labels with more than 10 characters are truncated to 10 
        characters. May contain commonly used ASCII characters. Lower case characters are converted 
        to upper case.""",
        get_process=lambda v: str(v[1:-1])
    )

    offset = Instrument.control(
        "OFFSet?", "OFFSet %f",
        """ A float parameter to set value that is represented at center of screen in 
        Volts. The range of legal values varies depending on range and scale. If the specified value 
        is outside of the legal range, the offset value is automatically set to the nearest legal value. """
    )

    probe_attenuation = Instrument.control(
        "PROBe?", "PROBe %f,RAT",
        """ A float parameter that specifies the probe attenuation as a ratio. The probe attenuation
        may be from 0.1 to 10000.""",
        validator=strict_range,
        values=[0.1, 10000]
    )

    range = Instrument.control(
        "RANGe?", "RANGe %f",
        """ A float parameter that specifies the full-scale vertical axis in Volts. 
        When using 1:1 probe attenuation, legal values for the 91204A range from 8 mV to 800 mV."""
    )

    scale = Instrument.control(
        "SCALe?", "SCALe %f",
        """ A float parameter that specifies the vertical scale, or units per division, in Volts. 
        Limits are [1e-3,1] for the 91204A range"""
    )

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number

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
    def output_enabled(self):
        mapper = {1: True, 0: False}
        out = int(self.instrument.ask("output%d?" % self.number))
        return mapper[out]

    @output_enabled.setter
    def output_enabled(self, state):
        mapper = {True: 'ON', False: 'OFF'}
        self.instrument.write("output%d %s" % (self.number, mapper[state]))


class BN765(Instrument):
    """Represents the Berkeley Nucleonics 765 800 MHz waveform generator.
    Individual devices are represented by subclasses.

    .. code-block:: python

        generator = BN765("GPIB::1")



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

    source1_loadimpedance = Instrument.control(
        'SOURce1:LOAD:IMP?', 'SOURce1:LOAD:IMP %g'
        """A mixed parameter that sets the load impedance. Any float between
        [50, 1e8] are allowed. """
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