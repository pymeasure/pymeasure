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

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, truncated_range

BOOL_MAP = {True: 1, False: 0}


class SMP04(SCPIMixin, Instrument):
    """Control the Rohde & Schwarz SMP04 microwave signal generator (2 GHz to 40 GHz).

    The instrument does not implement the ``FREQuency:MINimum?`` family of
    queries, so the frequency and level ranges below are taken from the manual.
    By default the standard-model limits apply; installed options widen them:

    :param frequency_extension_option: SMP-B11 frequency range extension, lowers
        the frequency limit from 2 GHz to 10 MHz.
    :param step_attenuator_option: SMP-B15/B17 step attenuator, lowers the level
        limit from -20 dBm to -130 dBm.
    """

    def __init__(self, adapter, name="Rohde & Schwarz SMP04",
                 frequency_extension_option=False,
                 step_attenuator_option=False, **kwargs):
        super().__init__(adapter, name, **kwargs)
        if frequency_extension_option:
            self.frequency_values = [10e6, 40e9]
        if step_attenuator_option:
            self.power_values = [-130, 16]

    frequency = Instrument.control(
        "FREQ?", "FREQ %.3f",
        """Control the CW output frequency in Hz (float from 2e9 to 40e9).

        Values outside the range are clipped to the nearest limit. The lower
        limit drops to 10 MHz with the SMP-B11 frequency range extension
        (``frequency_extension_option=True``).""",
        validator=truncated_range,
        values=[2e9, 40e9],
        dynamic=True,
    )

    power = Instrument.control(
        "POW?", "POW %.2f",
        """Control the RF output level in dBm (float from -20 to 16).

        Values outside the range are clipped to the nearest limit. The lower
        limit drops to -130 dBm with the SMP-B15/B17 step attenuator
        (``step_attenuator_option=True``). +13 dBm is the specified level,
        +16 dBm the overrange ceiling.""",
        validator=truncated_range,
        values=[-20, 16],
        dynamic=True,
    )

    output_enabled = Instrument.control(
        "OUTP?", "OUTP %d",
        """Control whether the RF output is enabled (bool).""",
        validator=strict_discrete_set,
        values=BOOL_MAP,
        map_values=True,
    )

    frequency_mode = Instrument.control(
        "FREQ:MODE?", "FREQ:MODE %s",
        """Control the frequency mode ('CW', 'SWEEP' or 'LIST').""",
        validator=strict_discrete_set,
        values=["CW", "SWEEP", "LIST"],
        cast=str,
    )

    power_mode = Instrument.control(
        "POW:MODE?", "POW:MODE %s",
        """Control the level mode ('FIXED', 'SWEEP' or 'LIST').""",
        validator=strict_discrete_set,
        values=["FIXED", "SWEEP", "LIST"],
        cast=str,
    )

    reference_source = Instrument.control(
        "ROSC:SOUR?", "ROSC:SOUR %s",
        """Control the reference oscillator source ('INT' or 'EXT').""",
        validator=strict_discrete_set,
        values=["INT", "EXT"],
        cast=str,
    )

    reference_frequency = Instrument.control(
        "ROSC:EXT:FREQ?", "ROSC:EXT:FREQ %g",
        """Control the expected external reference frequency in Hz
        (float, 1 MHz to 16 MHz in 1 MHz steps).""",
        validator=strict_discrete_set,
        values=[n * 1e6 for n in range(1, 17)],
    )

    alc_enabled = Instrument.control(
        "POW:ALC?", "POW:ALC %d",
        """Control the automatic level control (bool).""",
        validator=strict_discrete_set,
        values=BOOL_MAP,
        map_values=True,
    )

    attenuator_mode = Instrument.control(
        "OUTP:AMOD?", "OUTP:AMOD %s",
        """Control the attenuator mode ('AUTO' or 'FIX'). 'FIX' freezes the step
        attenuator, avoiding level glitches while changing power.""",
        validator=strict_discrete_set,
        values=["AUTO", "FIX"],
        cast=str,
    )

    am_enabled = Instrument.control(
        "AM:STAT?", "AM:STAT %d",
        """Control amplitude modulation (bool).""",
        validator=strict_discrete_set,
        values=BOOL_MAP,
        map_values=True,
    )

    fm_enabled = Instrument.control(
        "FM:STAT?", "FM:STAT %d",
        """Control frequency modulation (bool).""",
        validator=strict_discrete_set,
        values=BOOL_MAP,
        map_values=True,
    )

    pulse_modulation_enabled = Instrument.control(
        "PULM:STAT?", "PULM:STAT %d",
        """Control pulse modulation (bool).""",
        validator=strict_discrete_set,
        values=BOOL_MAP,
        map_values=True,
    )

    questionable_condition = Instrument.measurement(
        "STAT:QUES:COND?",
        """Get the questionable status condition register (int). Bit 5 (value 32)
        flags a frequency problem, such as an unlocked reference.""",
        cast=int,
    )

    frequency_ok = Instrument.measurement(
        "STAT:QUES:COND?",
        """Get whether the frequency status is fine (bool): bit 5 (FREQuency) of
        the questionable condition register is clear. A set bit flags a frequency
        problem such as an unlocked reference.""",
        get_process=lambda v: not (int(v) & 32),
    )
