#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set


class LD400P(Instrument):
    """Interface for the LD400P electronic DC load from Aim-TTi.

    Note: the LD400 edition doesn't have digital interfacing, only the LD400P does.

    The interface is described by the LD400[P] `manual`_.

    .. _manual: https://resources.aimtti.com/manuals/
                LD400+LD400P_Instruction_Manual_EN_48511-1730_8.pdf
    """

    unit_suffixes = ["A", "V", "W", "OHM", "SIE", "HZ"]

    @classmethod
    def remove_unit_suffix(cls, msg: str) -> str:
        """Remove known unit suffixes from a msg."""
        for suffix in cls.unit_suffixes:
            msg = msg.rstrip(suffix)
        return msg

    def __init__(self, adapter, **kwargs):
        super().__init__(adapter, "LD400", **kwargs)

    id = Instrument.measurement("*IDN?", """Reads the instrument identification (string).""")

    mode = Instrument.control(
        "MODE?",
        "MODE %s",
        """The mode of the digital load. Can be one of: 
        ``("C", "P", "R", "G", "V")`` corresponding to (respectively) constant current, 
        power, resistance, conductance or voltage (string).
        """,
        validator=strict_discrete_set,
        values=["C", "P", "R", "G", "V"],
        get_process=lambda v: v.lstrip("MODE "),
    )

    level_a = Instrument.control(
        "A?",
        "A %g",
        """The A level of the current control mode (float).""",
        preprocess_reply=lambda v: LD400P.remove_unit_suffix(v.lstrip("A")),
    )

    level_b = Instrument.control(
        "B?",
        "B %g",
        """The B level of the current control mode (float).""",
        preprocess_reply=lambda v: LD400P.remove_unit_suffix(v.lstrip("B")),
    )

    level_select = Instrument.control(
        "LVLSEL?",
        "LVLSEL %s",
        """The selected level of the digital load. Can be one of:
        ``("A", "B", "T", "V", "E")``, corresponding to (respectively) Level A, Level B,
        Transient, Ext Voltage and Ext TTL (string).
        """,
        validator=strict_discrete_set,
        values=["A", "B", "T", "V", "E"],
        get_process=lambda v: v.lstrip("LVLSEL "),
    )

    input = Instrument.control(
        "INP?",
        "INP %d",
        """The input state of the digital load, can be 'On' (``True``) or 'Off' 
        (``False``).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    voltage = Instrument.measurement(
        "V?",
        """The measured source input voltage (float).""",
        preprocess_reply=lambda v: v.lstrip("V"),
    )

    current = Instrument.measurement(
        "I?",
        """The measured load current (float).""",
        preprocess_reply=lambda v: v.lstrip("A"),
    )