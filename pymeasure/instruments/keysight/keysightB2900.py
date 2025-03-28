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
from pymeasure.instruments.validators import strict_range
import time


class KeysightB2900(Instrument):
    """Interface for the B2900 series Source Measurement Unit (SMU) from Keysight.
    
    Note: This instrument code was tested with a B2910BL SMU. This SMU only has a single channel, therefore this code only supports the use of channel 1.
    """

    def __init__(self, adapter, name="Key sight B2900", **kwargs):
        super().__init__(adapter, name, **kwargs)

    def reset(self):
        self.write("*RST")
        """Reset SMU device"""

    output_enabled = Instrument.control(
        "OUTPut1?",
        "OUTPut1 %d",
        """Control whether channel 1 output is enabled (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    output_mode = Instrument.control(
        ":SOURce1:FUNCtion:MODE?",
        ":SOURce1:FUNCtion:MODE %s",
        """Set SMU channel 1 as voltage or current controlled output.""",
        validator=strict_discrete_set,
        values=["CURR", "CURRent", "VOLT", "VOLTage"],
    )

    voltage_limit = Instrument.control(
        ":SENSe1:VOLTage:DC:PROTection:LEVel?",
        ":SENSe1:VOLTage:DC:PROTection:LEVel %g",
        """Safety limit the output voltage of channel 1, range depends on channel.""",
        validator=strict_range,
        values=[0, 10],  # actual range is up to 210V
        dynamic=True,
    )

    current_limit = Instrument.control(
        ":SENSe1:CURRent:DC:PROTection:LEVel?",
        ":SENSe1:CURRent:DC:PROTection:LEVel %g",
        """Safety limit the output current of channel 1, range depends on channel.""",
        validator=strict_range,
        values=[0, 1],  # actual range is up to 1.5A
        dynamic=True,
    )

    voltage_setpoint = Instrument.control(
        ":SOURce1:VOLTage:LEVel:IMMediate:AMPLitude?",
        ":SOURce1:VOLTage:LEVel:IMMediate:AMPLitude %g",
        """Control the output voltage of channel 1, range depends on channel.""",
        validator=strict_range,
        values=[-10, 10],  # actual range is up to 210V
        dynamic=True,
    )

    current_setpoint = Instrument.control(
        ":SOURce1:CURRent:LEVel:IMMediate:AMPLitude?",
        ":SOURce1:CURRent:LEVel:IMMediate:AMPLitude %g",
        """Control the output current of channel 1, range depends on channel.""",
        validator=strict_range,
        values=[-1, 1],  # actual range is up to 1.5A
        dynamic=True,
    )

    voltage_measure = Instrument.measurement(
        ":MEASure:VOLTage:DC? (@1)",
        """Measure the voltage on channel 1.""",
    )

    current_measure = Instrument.measurement(
        ":MEASure:CURRent:DC? (@1)",
        """Measure the current on channel 1.""",
    )

    output_filter_state = Instrument.control(
        ":OUTPut1:FILTer:LPASs:STATe?",
        ":OUTPut1:FILTer:LPASs:STATe %d",
        """Enables or disables the output filter, default is on""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    output_filter_auto = Instrument.control(
        ":OUTPut1:FILTer:LPASs:AUTO?",
        ":OUTPut1:FILTer:LPASs:AUTO %d",
        """Enables or disables the automatic filter function, default is off""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    output_filter_frequency = Instrument.control(
        ":OUTPut:FILTer:LPASs:FREQuency?",
        ":OUTPut:FILTer:LPASs:FREQuency %g",
        """Sets the cutoff frequency of the output filter.
        This command setting is ignored if the automatic filter function is enabled.
        Value (31.830 Hz to +31.831 kHz)|MINimum|MAXimum|.
        If you specify the value less than MIN or greater than MAX,
        time is automatically set to MIN or MAX.
        The latest command setting is effective for both time_constant and frequency because:
        frequency = 1/(2*pi*time_constant).""",
        validator=strict_range,
        values=[32, 31e3],
        dynamic=True,
    )

    output_filter_time_constant = Instrument.control(
        ":OUTPut1:FILTer:LPASs:TCONstant?",
        ":OUTPut1:FILTer:LPASs:TCONstant %g",
        """Sets the time constant instead of setting the cutoff frequency of the output filter.
        This command setting is ignored if the automatic filter function is enabled.
        Value (5 us to 5 ms)|MINimum|MAXimum|.
        If you specify the value less than MIN or greater than MAX,
        time is automatically set to MIN or MAX.
        The latest command setting is effective for both time_constant and frequency because:
        time_constant= 1/(2*pi*frequency).""",
        validator=strict_range,
        values=[5e-6, 5e-3],
        dynamic=True,
    )

    sense_remote = Instrument.control(
        ":SENSe1:REMote?",
        ":SENSe1:REMote %d",
        """Control whether remote sensing is enabled (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    output_isolation = Instrument.control(
        ":OUTPut1:LOW?",
        ":OUTPut1:LOW %s",
        """Selects the (isolation) state of the low terminal.
        Before executing this command, the source output must be disabled.""",
        validator=strict_discrete_set,
        values=["GRO", "GROund", "FLO", "FLOat"],
    )
