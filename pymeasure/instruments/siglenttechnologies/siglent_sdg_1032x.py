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

# Implementation of a Siglent SDG-1032X Function/Arbitrary Waveform Generator."
# Parts of this code were copied and adapted from the Agilent33500 instrument driver.

import logging
from pymeasure.instruments import Instrument, Channel, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from time import time
from pyvisa.errors import VisaIOError

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# TODO Implement the following:
# -Burst mode
# -Sweep mode
# -Triggers
# -Arbitrary functions


class SiglentSDG1032XChannel(Channel):
    """Implementation of a Siglent SDG-1032X channel"""

    shape = Instrument.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV WVTP,%s",
        """ Control the output waveform shape (str).""",
        validator=strict_discrete_set,
        values=["SINE", "SQUARE", "RAMP", "PULSE", "NOISE", "DC"],
        dynamic=True,
        preprocess_reply=lambda r: r.split("WVTP,")[1].split(",")[0]
    )

    frequency = Instrument.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV FRQ,%g",
        """ Control the waveform frequency in Hz (float). Depends on the specified shape.""",
        validator=strict_range,
        values=[1e-6, 30e6],
        dynamic=True,
        preprocess_reply=lambda r: r.split("FRQ,")[1].split(",")[0]
    )

    amplitude = Instrument.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV AMP,%g",
        """ Control the voltage amplitude in Volts (float).""",
        validator=strict_range,
        values=[2e-3, 20],
        dynamic=True,
        preprocess_reply=lambda r: r.split(",AMP,")[1].split(",")[0]
    )

    amplitude_rms = Instrument.measurement(
        "C{ch}:BSWV?",
        """Read back Vrms from the basic-wave parameters.""",
        preprocess_reply=lambda r: r.split(",AMPVRMS,")[1].split(",")[0]
    )
    amplitude_dbm = Instrument.measurement(
        "C{ch}:BSWV?",
        """Read back Vdbm from the basic-wave parameters.""",
        preprocess_reply=lambda r: r.split(",AMPDBM,")[1].split(",")[0]
    )
    amplitude_max = Instrument.measurement(
        "C{ch}:BSWV?",
        """Read back Vdbm from the basic-wave parameters.""",
        preprocess_reply=lambda r: r.split(",MAX_OUTPUT_AMP,")[1].split(",")[0]
    )

    offset = Instrument.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV OFST,%f",
        """ Control the voltage offset in Volts (float).""",
        validator=strict_range,
        values=[-8, +8],
        dynamic=True,
        preprocess_reply=lambda r: r.split(",OFST,")[1].split(",")[0]
    )

    voltage_high = Instrument.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV HLEV,%f",
        """ Control the upper voltage level in Volts (float).""",
        validator=strict_range,
        values=[-5, 5],
        dynamic=True,
        preprocess_reply=lambda r: r.split(",HLEV,")[1].split(",")[0]
    )

    voltage_low = Instrument.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV LLEV,%f",
        """ Control the lower voltage level in Volts (float).""",
        validator=strict_range,
        values=[-5, 5],
        dynamic=True,
        preprocess_reply=lambda r: r.split(",LLEV,")[1].split(",")[0]
    )

    phase = Instrument.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV PHSE,%f",
        """ Control the waveform phase in degrees (float, from -360 to 360).""",
        validator=strict_range,
        values=[-360, 360],
        preprocess_reply=lambda r: r.split(",PHSE,")[1].split(",")[0]
    )

    dutycycle = Instrument.control(                                                          
        "C{ch}:BSWV?",
        "C{ch}:BSWV DUTY,%f",
        """ Control the duty cycle in percent (float).""",
        validator=strict_range,
        values=[0, 100],
        dynamic=True,
        preprocess_reply=lambda r: r.split(",DUTY,")[1].split(",")[0]
    )

    ramp_symmetry = Instrument.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV SYM,%f",
        """ Control the ramp waveform symmetry in percent (float, from 0 to 100).""",
        validator=strict_range,
        values=[0, 100],
        dynamic=True,
        preprocess_reply=lambda r: r.split(",SYM,")[1].split(",")[0]
    )

    period = Instrument.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV PERI,%g",
        """ Control the pulse period in seconds (float). Overwrites frequency. """,
        validator=strict_range,
        values=[80e-9, 1e6],
        dynamic=True,
        preprocess_reply=lambda r: r.split(",PERI,")[1].split(",")[0]                      
    )


    pulse_width = Instrument.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV WIDTH,%g",
        """ Control the pulse width in seconds (float).""",
        validator=strict_range,
        values=[32.6e-9, 1e6],
        dynamic=True,
        preprocess_reply=lambda r: r.split(",WIDTH,")[1].split(",")[0]  
    )

    pulse_rise_time = Instrument.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV RISE,%g",
        """ Control the pulse rising edge time in seconds (float).""",
        validator=strict_range,
        values=[16.8e-9, 22.4],
        dynamic=True,
        preprocess_reply=lambda r: r.split(",RISE,")[1].split(",")[0]
    )

    pulse_fall_time = Instrument.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV FALL,%g",
        """ Control the pulse falling edge in seconds  (float).""",
        validator=strict_range,
        values=[16.8e-9, 22.4],
        dynamic=True,
        preprocess_reply=lambda r: r.split(",FALL,")[1].split(",")[0]
    )

    pulse_delay = Instrument.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV DLY,%g",
        """ Control the delay between pulses in seconds (float).""",
        validator=strict_range,
        values=[-1e7, 1e7],
        dynamic=True,
        preprocess_reply=lambda r: r.split(",DLY,")[1].split(",")[0]
    )


    output = Instrument.control(
        "C{ch}:OUTP?",
        "C{ch}:OUTP %s",
        """ Control the output state (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", "on": "ON", "On": "ON", "ON": "ON",
                False: "OFF", "off": "OFF", "Off": "OFF", "OFF": "OFF"},
        dynamic=True,
        preprocess_reply=lambda r: r.split(",")[0].split("OUTP ")[1] .strip(),
    )

    output_load = Instrument.control(
        "C{ch}:OUTP?",
        "C{ch}:OUTP LOAD,%s",
        """ Control the expected load resistance in Ohms (str or float). The output impedance           
        is always 50 Ohm, this setting can be used to correct the displayed voltage for
        loads unmatched to 50 Ohm.""",
        validator=strict_discrete_set,
        values=["HZ", 50, "50"],
        dynamic=True,
        preprocess_reply=lambda r: r.split(",LOAD,")[1].split(",")[0]
    )

    output_polarity = Instrument.control(
        "C{ch}:OUTP?",
        "C{ch}:OUTP PLRT,%s",
        """Set the channel polarity (NORmal or INVerTed).""",
        validator=strict_discrete_set,
        values=["NOR", "INVT"],
        dynamic=True,
        preprocess_reply=lambda r: r.split(",PLRT,")[1].split(",")[0]
    )

    noise_standard_deviation = Instrument.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV STDEV,%g",
        """Control the standard deviation for NOISE in Volts (float)""",
        validator=strict_range,
        values=[1e-3, 707e-3],
        dynamic=True,
        preprocess_reply=lambda r: r.split(",STDEV,")[1].split(",")[0]
    )

    noise_mean = Instrument.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV MEAN,%g",
        """Control the mean for NOISE in Volts (float)""",
        validator=strict_range,
        values=[-8, +8],
        dynamic=True,
        preprocess_reply=lambda r: r.split(",MEAN,")[1].split(",")[0]
    )


class SiglentSDG1032X(SCPIMixin, Instrument):
    """
     Driver shell for the **Siglent SDG-1000X** arbitrary/function generators
    (e.g. SDG1032X). Two fully-featured channel objects are exposed as
    ch_1 and ch_2. If not sepcified, driver will default commands to chanel ch_1.

     Basic usage
    -----------
        .. code-block:: python

        gen = SiglentSDG1032X("USB0::0xF4EC::0x11xx::SDGXXXXX::INSTR")

        # ── SHAPE / FREQUENCY / DUTY ETC.  (aliases → channel-1) ─────────
        gen.shape       = "SINE"       # same as gen.ch_1.shape
        gen.frequency   = 1e3          # 1 kHz
        gen.dutycycle   = 25           # 25 % (valid for SQUARE / PULSE)

        # ── AMPLITUDE, OFFSET, PHASE ────────────────────────────────────
        gen.amplitude   = 4            # 4 Vpp  (Hi-Z scale)
        gen.offset      = 0.5          # 0.5 Vdc
        gen.phase       = 90           # 90 °

        # ── NOISE-MODE PARAMETERS ───────────────────────────────────────
        gen.shape = "NOISE"
        gen.noise_standard_deviation = 0.2   # 0.2 Vrms
        gen.noise_mean               = 0.0   # 0 V
        # gen.noise_bandwidth  = 5e6               # Not working yet
        # gen.noise_bandstate  = "ON"              # Not working yet

        # ── PULSE / RAMP SPECIFICS ──────────────────────────────────────
        gen.shape          = "PULSE"
        gen.pulse_width    = 2e-6     # 2 µs high time
        gen.pulse_rise_time = 30e-9   # 30 ns
        gen.pulse_fall_time = 30e-9   # 30 ns
        gen.pulse_delay     = 1e-6    # 1 µs start delay

        gen.shape          = "RAMP"
        gen.ramp_symmetry  = 10       # 10 % fall, 90 % rise

        # ── LEVEL MODE ──────────────────────────────────────────────────
        gen.voltage_high = 1.0        # set high-level directly
        gen.voltage_low  = -1.0       # set low-level directly

        # ── OUTPUT CONTROL ──────────────────────────────────────────────
        gen.output          = True    # ON  (alias to ch_1.output)
        gen.output_load     = "50"    # 50 Ω or "HZ" for Hi-Z
        gen.output_polarity = "INVT"  # NOR / INVT

        # ── CHANNEL-2 EXAMPLE (explicit) ───────────────────────────────
        gen.ch_2.shape     = "SQUARE"
        gen.ch_2.frequency = 2e3
        gen.ch_2.amplitude = 2
        gen.ch_2.output    = True

    """

    ID_PATTERN = "Siglent Technologies,SDG"

    ch_1 = Instrument.ChannelCreator(SiglentSDG1032XChannel, 1)

    ch_2 = Instrument.ChannelCreator(SiglentSDG1032XChannel, 2)

    def __init__(self, adapter, name="Siglent SDG-1032X Function/Arbitrary Waveform Generator",
                 **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )

def _alias(name):
    '''Default to ch_1'''
    return property(
        lambda self, n=name: getattr(self.ch_1, n),
        lambda self, value, n=name: setattr(self.ch_1, n, value),
        doc=f"Shortcut to ch_1.{name}"
    )

for _name in (
        "shape",
        "frequency", 
        "amplitude", 
        "offset",
        "phase",
        "output",           
        "output_load",
        "output_polarity",
        "dutycycle",
        "noise_standard_deviation",
        "noise_mean",
        "pulse_width",
        "period"
        "pulse_rise_time"
        "pulse_fall_time"
        "voltage_high"
        "voltage_low"
        "pulse_delay"
        "ramp_symmetry"
):
    setattr(SiglentSDG1032X, _name, _alias(_name))