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

from pymeasure.instruments import Instrument
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set


class LD400P(SCPIMixin, Instrument):
    """Interface for the LD400P electronic DC load from Aim-TTi.

    Note: the LD400 edition doesn't have digital interfacing, only the LD400P does.

    The interface is described by the LD400[P] `manual`_.

    The class :class:`~SCPIMixin` is inherited, however the commands `options`,
    next_error` and `check_errors` do not work for this device.

    .. _manual: https://resources.aimtti.com/manuals/
                LD400+LD400P_Instruction_Manual_EN_48511-1730_8.pdf
    """

    unit_suffixes = ["A", "V", "W", "OHM", "SIE", "HZ"]

    def __init__(self, adapter, name="LD400", **kwargs):
        super().__init__(adapter, name, **kwargs)

    @classmethod
    def remove_unit_suffix(cls, msg: str) -> str:
        """Remove known unit suffixes from a msg.

        The units of some replies depend on the mode of the device, hence all known
        units are removed.
        """
        for suffix in cls.unit_suffixes:
            msg = msg.replace(suffix, "")
        return msg

    mode = Instrument.control(
        "MODE?",
        "MODE %s",
        """Control the mode of the digital load. Can be one of:
        ``("C", "P", "R", "G", "V")``, corresponding to (respectively) constant current,
        power, resistance, conductance, or voltage (string).
        """,
        validator=strict_discrete_set,
        values=["C", "P", "R", "G", "V"],
        get_process=lambda v: v.replace("MODE ", ""),
    )

    level_select = Instrument.control(
        "LVLSEL?",
        "LVLSEL %s",
        """Control the selected level of the digital load. Can be one of:
        ``("A", "B", "T", "V", "E")``, corresponding to (respectively) Level A, Level B,
        Transient, Ext Voltage and Ext TTL (string).
        """,
        validator=strict_discrete_set,
        values=["A", "B", "T", "V", "E"],
        get_process=lambda v: v.replace("LVLSEL ", ""),
    )

    level_a = Instrument.control(
        "A?",
        "A %g",
        """Control the A level of the current control mode (float).""",
        preprocess_reply=lambda v: LD400P.remove_unit_suffix(v.replace("A", "")),
    )

    level_b = Instrument.control(
        "B?",
        "B %g",
        """Control the B level of the current control mode (float).""",
        preprocess_reply=lambda v: LD400P.remove_unit_suffix(v.replace("B", "")),
    )

    input_enabled = Instrument.control(
        "INP?",
        "INP %d",
        """Control the input state of the digital load, can be ``True`` (on) or
        ``False`` (off).
        """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        preprocess_reply=lambda v: v.replace("INP ", ""),
    )

    # Voltage / current replies are _not_ prefixed by the command, but do have a unit:

    voltage = Instrument.measurement(
        "V?",
        """Get the measured source input voltage (float).""",
        preprocess_reply=lambda v: v.replace("V", ""),
    )

    current = Instrument.measurement(
        "I?",
        """Get the measured load current (float).""",
        preprocess_reply=lambda v: v.replace("A", ""),
    )

    # Remove SCP properties that don't work on this device:

    @property
    def options(self):
        """Get options - Not available."""
        raise AttributeError("No attribute 'options' exists")

    @property
    def next_error(self):
        """Get next error - Not available."""
        raise AttributeError("No attribute 'next_error' exists")

    def check_errors(self):
        """Not available."""
        raise NotImplementedError("This method is not available on this device")
