#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Channel():
    """ Implementation of a Keithley 2200 channel. """

    VOLTAGE_RANGE = [0, 70]
    CURRENT_RANGE = [0, 45]

    output_enabled = Instrument.control(
        "SOURCE:OUTP:ENAB?", "SOURCE:OUTP:ENAB %d",
        """A boolean property that controls whether the output is enabled, takes
        values True or False. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    voltage = Instrument.control(
        "VOLT?", "VOLT %g",
        """ A floating point property that represents the output voltage
        setting of the power supply in Volts. This property can be set. """,
        validator=strict_range,
        values=VOLTAGE_RANGE
    )

    current = Instrument.control(
        "CURR?", "CURR %g",
        """ A floating point property that represents the output current of
        the power supply in Amps. This property can be set. """,
        validator=strict_range,
        values=CURRENT_RANGE
    )

    measure_current = Instrument.measurement(
        "MEAS:CURR?",
        """ A measurement property that reads the measured current in Amps.
        This property is readonly. """,
    )

    measure_voltage = Instrument.measurement(
        "MEAS:VOLT?",
        """ A measurement property that reads the measured current in Volts.
        This property is readonly. """,
    )

    measure_power = Instrument.measurement(
        "MEAS:VOLT?",
        """ A measurement property that reads the measured power in watts.
        This property is readonly. """,
    )

    voltage_limit = Instrument.control(
        "VOLT:LIM?", "VOLT:LIM %g",
        """ A property which represents the maximum voltage limit""",
        validator=strict_range,
        values=VOLTAGE_RANGE
    )

    voltage_limit_enabled = Instrument.control(
        "VOLT:LIM:STAT?", "VOLT:LIM:STAT %d",
        """A boolean property that controls whether the voltage limit is enabled,
        takes values True or False. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number

    def values(self, command, **kwargs):
        return self.instrument.values(f"INST:SEL CH{self.number};{command}",
                                      **kwargs)

    def write(self, command):
        self.instrument.write(f"INST:SEL CH{self.number};{command}")


class Keithley2200(Instrument):
    """ Represents the Keithley 2230 Power Supply.
    """

    def __init__(self, adapter, **kwargs):
        super().__init__(adapter, "Keithley 2200", **kwargs)
        self.ch1 = Channel(self, 1)
        self.ch2 = Channel(self, 2)
        self.ch3 = Channel(self, 3)

    display_enabled = Instrument.control(
        "DISP?", ":DISP %d",
        """A boolean property that controls whether the display is enabled,
        takes values True or False. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    display_text_data = Instrument.control(
        ":DISP:TEXT:DATA?", ":DISP:TEXT:DATA \"%s\"",
        """A string property that control text to be displayed, takes strings
        up to 32 characters. """,
        get_process=lambda v: v.replace('"', '')
    )

    def ch(self, channel_number):
        """Get a channel from this instrument.

        :param: channel_number:
            int: the number of the channel to be selected
        :type: :class:`.Channel`

        """
        if channel_number == 1:
            return self.ch1
        elif channel_number == 2:
            return self.ch2
        elif channel_number == 3:
            return self.ch3
        else:
            raise ValueError("Invalid channel number. Must be 1, 2 or 3.")
