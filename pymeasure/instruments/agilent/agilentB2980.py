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

from pymeasure.instruments import SCPIMixin, Instrument, Channel

from pymeasure.instruments.validators import (
    strict_discrete_set,
    truncated_range,
    joined_validators
    )

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AgilentB2980SeriesAmmeter(SCPIMixin, Instrument):
    """A class representing the Agilent/Keysight B2980A/B series Femto/Picoammeterss."""
    def __init__(self, adapter,
                 name="Agilent/Keysight B2980A/B series Picoammeter",
                 **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

        self.add_child(AgilentB298xTrigger, attr_name='trigger')

    input_enabled = Instrument.control(
        ":INP?", ":INP %d",
        """Control whether the instrument input is enabled (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
        )

    zero_corrected = Instrument.control(
        ":INP:ZCOR?", ":INP:ZCOR %d",
        """
        Control the zero correct function for current/charge measurement (boolean).

        B2981/B2983 supports current measurement only.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
        )

    measure = Instrument.measurement(
        ":MEAS?",
        """Measure the defined parameter(s) with a spot (one-shot) measurement."""
        )

    current = Instrument.measurement(
        ":MEAS:CURR?",
        """Measure current with a spot (one-shot) measurement."""
        )

    current_range = Instrument.control(
        ":CURR:RANG?", ":CURR:RANG %s",
        """Control the range for current measurement.

        (float strictly from 2E-12 to 20E-3) or
        ('MIN', 'MAX', 'DEF', 'UP', 'DOWN')
        """,
        validator=joined_validators(strict_discrete_set, truncated_range),
        values=[['MIN', 'MAX', 'DEF', 'UP', 'DOWN'], [2E-12, 20E-3]]
        )

    function = Instrument.control(
        ":FUNC?", ":FUNC '%s'",
        """Control the measurement function.

        ('CURR') for ammeters
        ('CURR', 'CHAR', 'VOLT', 'RES') for electrometers
        """,
        validator=strict_discrete_set,
        values=['CURR'],
        dynamic=True
        )


class AgilentB2980SeriesElectrometer(AgilentB2980SeriesAmmeter):
    """A class representing the Agilent/Keysight B2980A/B series Electrometers."""
    def __init__(self, adapter,
                 name="Agilent/Keysight B2980A/B series Electrometer",
                 **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

        self.add_child(AgilentB298xSource, attr_name='source')

    function_values = ['CURR', 'CHAR', 'VOLT', 'RES']

    charge = Instrument.measurement(
        ":MEAS:CHAR?",
        """Measure charge with a spot (one-shot) measurement."""
        )

    charge_range = Instrument.control(
        ":CHAR:RANG?", ":CHAR:RANG %s",
        """Control the range for charge measurement.

        (float strictly from 2E-9 to 2E-6) or
        ('MIN', 'MAX', 'DEF', 'UP', 'DOWN')
        """,
        validator=joined_validators(strict_discrete_set, truncated_range),
        values=[['MIN', 'MAX', 'DEF', 'UP', 'DOWN'], [2E-9, 2E-6]]
        )

    resistance = Instrument.measurement(
        ":MEAS:RES?",
        """Measure resistance with a spot (one-shot) measurement."""
        )

    resistance_range = Instrument.control(
        ":RES:RANG?", ":RES:RANG %s",
        """Control the range for resistance measurement.

        (float strictly from 1E6 to 1E15) or
        ('MIN', 'MAX', 'DEF', 'UP', 'DOWN')
        """,
        validator=joined_validators(strict_discrete_set, truncated_range),
        values=[['MIN', 'MAX', 'DEF', 'UP', 'DOWN'], [1E6, 1E15]]
        )

    voltage = Instrument.measurement(
        ":MEAS:VOLT?",
        """Measure voltage with a spot (one-shot) measurement."""
        )

    voltage_range = Instrument.control(
        ":VOLT:RANG?", ":VOLT:RANG %s",
        """Control the range for voltage measurement.

        (float strictly from 2 to 20) or
        ('MIN', 'MAX', 'DEF', 'UP', 'DOWN')
        """,
        validator=joined_validators(strict_discrete_set, truncated_range),
        values=[['MIN', 'MAX', 'DEF', 'UP', 'DOWN'], [2, 20]]
        )


class AgilentB298xSource(Channel):
    """A class representing the B298x source functions."""

    enabled = Channel.control(
        ":OUTP?", ":OUTP %d",
        """Control the voltage source output (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
        )

    low_state = Channel.control(
        ":OUTP:LOW?", ":OUTP:LOW %s",
        """Control the source low terminal state ('FLO', 'COMM').""",
        validator=strict_discrete_set,
        values=['FLO', 'COMM']
        )

    off_state = Channel.control(
        ":OUTP:OFF:MODE?", ":OUTP:OFF:MODE %s",
        """Control the source condition after output off (ZERO|HIZ|NORM).

        HIGH Z: • Output relay: off (open)
                • The voltage source setting is not changed.
                • This status is available only when the 20 V range is used.
        NORMAL: • Output voltage: 0 V
                • Output relay: off (open)
        ZERO:   • Output voltage: 0 V in the present voltage range
        """,
        validator=strict_discrete_set,
        values=['ZERO', 'HIZ', 'NORM']
        )

    voltage = Channel.control(
        ":SOUR:VOLT?", ":SOUR:VOLT %g",
        """Control the output voltage of the source.""",
        check_set_errors=True
        )

    range = Channel.control(
        ":SOUR:VOLT:RANG?", ":SOUR:VOLT:RANG %s",
        """Control the output voltage range of the source.""",
        validator=joined_validators(strict_discrete_set, truncated_range),
        values=[['MIN', 'MAX', 'DEF'], [-1050, 1050]],
        check_set_errors=True
        )


class AgilentB298xTrigger(Channel):
    """A class representing the B298x trigger functions."""

    def init(self, action='ALL'):
        """Init trigger."""
        strict_discrete_set(action, ['ALL', 'ACQ', 'TRAN'])
        self.write(f":INIT:{action}")


class AgilentB298xBattery(Channel):
    """A class representing the B298x battery functions."""

    def insert_id(self, command):
        return f":SYST:BATT{command}"

    level = Channel.measurement(
        "?",
        """Get the percentage of the remaining battery capacity (int).""",
        get_process=lambda v: int(v),  # convert to integer
    )

    cycles = Channel.measurement(
        ":CYCL?",
        """Get the battery cycle count (int).""",
        get_process=lambda v: int(v),  # convert to integer
    )

    selftest_passed = Channel.measurement(
        ":TEST?",
        """Get the battery self-test result (boolean).""",
        map_values=True,
        values={True: 0, False: 1}  # 0: passed, 1: failed
    )


##########################
# Instrument definitions #
##########################


class AgilentB2981(AgilentB2980SeriesAmmeter):
    """Agilent/Keysight B2981A/B series, Femto/Picoammeter."""
    pass


class AgilentB2983(AgilentB2980SeriesAmmeter):
    """Agilent/Keysight B2983A/B series, Femto/Picoammeter.

    Has battery operation.
    """
    battery = Instrument.ChannelCreator(AgilentB298xBattery, "battery")


class AgilentB2985(AgilentB2980SeriesElectrometer):
    """Agilent/Keysight B2985A/B series Femto/Picoammeter Electrometer/High Resistance Meter."""
    pass


class AgilentB2987(AgilentB2980SeriesElectrometer):
    """Agilent/Keysight B2987A/B series Femto/Picoammeter Electrometer/High Resistance Meter.

    Has battery operation.
    """
    battery = Instrument.ChannelCreator(AgilentB298xBattery, "battery")
