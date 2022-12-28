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
from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PSChannel(Channel):
    """ Implementation of a Keithley 2200 channel. """

    VOLTAGE_RANGE = [0, 70]
    CURRENT_RANGE = [0, 45]

    output_enabled = Instrument.control(
        "SOURCE:OUTP:ENAB?", "SOURCE:OUTP:ENAB %d",
        """ A boolean property representing output state.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    voltage = Instrument.control(
        "VOLT?", "VOLT %g",
        """ A floating point property representing the output voltage in Volts.""",
        validator=strict_range,
        values=VOLTAGE_RANGE
    )

    current = Instrument.control(
        "CURR?", "CURR %g",
        """ A floating point property that representing the output current in Amps.""",
        validator=strict_range,
        values=CURRENT_RANGE
    )

    measure_current = Instrument.measurement(
        "MEAS:CURR?",
        """ A measurement property that reads the measured current in Amps.""",
    )

    measure_voltage = Instrument.measurement(
        "MEAS:VOLT?",
        """ A measurement property that reads the measured current in Volts.""",
    )

    measure_power = Instrument.measurement(
        "MEAS:VOLT?",
        """ A measurement property that reads the measured power in watts.""",
    )

    voltage_limit = Instrument.control(
        "VOLT:LIM?", "VOLT:LIM %g",
        """ A property which represents the maximum voltage limit.""",
        validator=strict_range,
        values=VOLTAGE_RANGE
    )

    voltage_limit_enabled = Instrument.control(
        "VOLT:LIM:STAT?", "VOLT:LIM:STAT %d",
        """A boolean property that representing voltage limit.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    def insert_id(self, command):
        return f"INST:SEL CH{self.id};{command}"


class Keithley2200(Instrument):
    """ Represents the Keithley 2230 Power Supply.
    """
    def __init__(self, adapter, name="Keithley2200"):
        super().__init__(adapter, name)

    channels = Instrument.ChannelCreator(PSChannel, ("1", "2", "3"))

    display_enabled = Instrument.control(
        "DISP?", ":DISP %d",
        """ A boolean property that controls whether the display is enabled.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    display_text_data = Instrument.control(
        ":DISP:TEXT:DATA?", ":DISP:TEXT:DATA \"%s\"",
        """ A string property that control text to be displayed(32 characters).""",
        get_process=lambda v: v.replace('"', '')
    )
