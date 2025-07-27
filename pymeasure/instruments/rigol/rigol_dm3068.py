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

from warnings import warn
from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set


class RigolDM3068(SCPIMixin, Instrument):
    """ Represents the Rigol DM3068 Multimeter and
    provides a high-level interface for interacting with the instrument.

    .. code-block:: python

        dmm = RigolDM3068("GPIB::1")

    """
    # Below: stop_bits: 20 comes from
    # https://pyvisa.readthedocs.io/en/latest/api/constants.html#pyvisa.constants.StopBits
    def __init__(self, adapter, name="Rigol DM3068", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    # we keep the function names the same as the HP 34401A
    FUNCTIONS = {
        "DCV"        : "VOLT:DC", 
        "ACV"        : "VOLT:AC", 
        "DCI"        : "CURR:DC", 
        "ACI"        : "CURR:AC",
        "W2R"        : "RES", 
        "W4R"        : "FRES", 
        "FREQ"       : "FREQ",
        "PERIOD"     : "PER", 
        "CONTINUITY" : "CONT", 
        "DIODE"      : "DIOD",
        "CAP"        : "CAP",
    }

    # mapping needed to take care of the inconsistency in the function names returned
    FUNCTIONS_R = {
        "DCV"        : "VOLT:DC", 
        "ACV"        : "VOLT:AC", 
        "DCI"        : "CURR:DC", 
        "ACI"        : "CURR:AC",
        "2WR"        : "RES", 
        "4WR"        : "FRES", 
        "FREQ"       : "FREQ",
        "PERI"       : "PER", 
        "CONT"       : "CONT", 
        "DIODE"      : "DIOD",
        "CAP"        : "CAP",
    }
    
    BOOL_MAPPINGS = {True: 1, False: 0}
    
    function = Instrument.control(
        ":FUNC?", ":FUNC:%s",
        """Confgure the measurement function.

        Allowed values: "DCV", "ACV", "DCI", "ACI",
        "W2R", "W2R", "FREQ", "PERIOD", "CONTINUITY", "DIODE", "CAP".""",
        validator=strict_discrete_set,
        values=FUNCTIONS,
        map_values=True,
        get_process=lambda v: RigolDM3068.FUNCTIONS_R[v]
    )
    
    def beep(self):
        """This command causes the multimeter to beep once."""
        self.write("SYST:BEEP")
    
    beeper_enabled = Instrument.control(
        "SYST:BEEP:STAT?", "SYST:BEEP:STAT %s",
        """Control whether the beeper is enabled.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    scpi_version = Instrument.measurement(
        "SYST:VERS?",
        """The SCPI version of the multimeter.""",
    )
    
    voltage_dc = Instrument.measurement(
        ":MEAS:VOLT:DC?",
        "DC voltage, in Volts",
    )

