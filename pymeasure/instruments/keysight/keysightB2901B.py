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

import logging
from pymeasure.instruments import Instrument, SCPIMixin, Channel
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


OPERATING_MODES = ['VOLT', 'CURR']


class SMUChannel(Channel):
    """A channel of the source-measure unit."""

    output_enabled = Instrument.control(
        'OUTPut{ch}:STATe?', 'OUTPut{ch}:STATe %g',
        """Control the output state (on/off) of the SMU channel (bool)""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
    )

    source_voltage = Instrument.control(
        "SOURce{ch}:VOLTage:LEVel:IMMediate:AMPLitude?",
        "SOURce{ch}:VOLTage:LEVel:IMMediate:AMPLitude %g",
        """Control output voltage in volt."""
    )

    source_voltage_auto_range = Channel.control(
        "SOURce{ch}:VOLTage:RANGe:AUTO?", "SOURce{ch}:VOLTage:RANGe:AUTO %g",
        """Control the automatic output voltage ranging function.""",
        validator=strict_discrete_set,
        map_values=True,
        values={False: 0, True: 1}
    )

    sense_voltage = Instrument.measurement(
        "MEASure:VOLTage? (@{ch})",
        """Measure sense voltage in volt."""
    )

    sense_voltage_limit = Instrument.control(
        "SENSe{ch}:VOLTage:PROTection:LEVel?",
        "SENSe{ch}:VOLTage:PROTection:LEVel %g",
        """Control compliance voltage when operating in current mode."""
    )

    sense_voltage_auto_range = Channel.control(
        "SENSe{ch}:VOLTage:RANGe:AUTO?", "SENSe{ch}:VOLTage:RANGe:AUTO %g",
        """Control the automatic voltage-measurement ranging function.""",
        validator=strict_discrete_set,
        map_values=True,
        values={False: 0, True: 1}
    )

    sense_voltage_averaging_time = Channel.control(
        "SENSe{ch}:VOLTage:APERture?", "SENSe{ch}:VOLTage:APERture %g",
        """Control the voltage-measurement averaging time of the channel in seconds.""",
        validator=strict_range,
        values=[8e-6, 2]
    )

    source_current = Instrument.control(
        "SOURce{ch}:CURRent:LEVel:IMMediate:AMPLitude?",
        "SOURce{ch}:CURRent:LEVel:IMMediate:AMPLitude %g",
        """Control output current in ampere."""
    )

    sense_current = Instrument.measurement(
        "MEASure:CURRent? (@{ch})",
        """Measure sense current in ampere."""
    )

    sense_current_limit = Instrument.control(
        "SENSe{ch}:CURRent:PROTection:LEVel?",
        "SENSe{ch}:CURRent:PROTection:LEVel %g",
        """Control current limit when operating in voltage mode."""
    )

    sense_current_auto_range = Channel.control(
        "SENSe{ch}:CURRent:RANGe:AUTO?", "SENSe{ch}:CURRent:RANGe:AUTO %g",
        """Control the automatic current-measurement ranging function.""",
        validator=strict_discrete_set,
        map_values=True,
        values={False: 0, True: 1}
    )

    sense_current_averaging_time = Channel.control(
        "SENSe{ch}:CURRent:APERture?", "SENSe{ch}:CURRent:APERture %g",
        """Control the current-measurement averaging time of the channel in seconds.""",
        validator=strict_range,
        values=[8e-6, 2]
    )

    operating_mode = Instrument.control(
        "SOURce{ch}:FUNCtion:MODE?", "SOURce{ch}:FUNCtion:MODE %s",
        """Control the operating mode of the SMU.""",
        validator=strict_discrete_set,
        values=OPERATING_MODES
    )


class KeysightB2901B(SCPIMixin, Instrument):
    """
    This represents the Keysight B2901B Source-Measure Unit interface.

    .. code-block:: python

        smu = KeysightB2901B(address)

    """

    def __init__(self, adapter, name="Keysight B2901B Source-Measure Unit", **kwargs):
        super().__init__(
            adapter, name, **kwargs)

    channel_1 = Instrument.ChannelCreator(SMUChannel, 1)

    time = Instrument.control(
        "SYSTem:TIME?", "SYSTem:TIME %g,%g,%g",
        """Control the  the instrument’s internal time."""
    )

    def preset(self):
        """Sets the insrument to its standard settings. The stored settings are deleted."""
        self.write('SYSTem:PRESet')

    def close(self):
        """
        Fully closes the connection to the instrument through the adapter connection.
        """
        self.adapter.close()