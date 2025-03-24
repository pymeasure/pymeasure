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


from pymeasure.instruments import SCPIMixin, Instrument
from pymeasure.instruments.validators import strict_discrete_set


class AgilentB298xAmmeter(SCPIMixin, Instrument):
    """
    Agilent/Keysight B298xA/B series, Femto/Picoammeter functions.
    """
    input_enabled = Instrument.control(
        ":INP?", ":INP %d",
        """Control the instrument input (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
        )

    zero_correction = Instrument.control(
        ":INP:ZCOR?", ":INP:ZCOR %d",
        """
        Control the zero correct function for current or charge measurement (boolean).

        B2981/B2983 supports current measurement only.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
        )

    current = Instrument.measurement(
        ":MEAS:CURR?",
        """Executes a spot (one-shot) current measurement ."""
        )


class AgilentB298xElectrometer(Instrument):
    """
    Agilent/Keysight B298xA/B series, Electrometer/High Resistance Meter functions.
    """
    output_enabled = Instrument.control(
        ":OUTP?", ":OUTP %d",
        """Control the instrument source output (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
        )

    measure = Instrument.measurement(
        ":MEAS?",
        """
        Executes a spot (one-shot) measurement for the parameters specified.

        Measurement conditions must be set before executing this command.
        Each data is separated by a comma.
        """
        )


class AgilentB298xBattery(Instrument):
    """
    Battery functions of the B2983/7 models.
    """
    battery_level = Instrument.measurement(
        ":SYST:BATT?",
        """Get the percentage of the remaining battery capacity.""",
    )

    battery_cycles = Instrument.measurement(
        ":SYST:BATT:CYCL?",
        """Get the battery cycle count.""",
    )

    battery_selftest = Instrument.measurement(
        ":SYST:BATT:TEST?",
        """Self-test off the battery.

            0: passed
            1: failed
        """,
    )

##########################
# Instrument definitions #
##########################


class AgilentB2981(AgilentB298xAmmeter):
    """
    Agilent/Keysight B2981A/B series, Femto/Picoammeter.
    """
    def __init__(self, adapter, name="Agilent/Keysight B2981A/B Femto/Picoammeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )


class AgilentB2983(AgilentB298xAmmeter, AgilentB298xBattery):
    """
    Agilent/Keysight B2983A/B series, Femto/Picoammeter.
    """
    def __init__(self, adapter, name="Agilent/Keysight B2983A/B Femto/Picoammeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )


class AgilentB2985(AgilentB298xAmmeter, AgilentB298xElectrometer):
    """
    Agilent/Keysight B2985A/B series Femto/Picoammeter Electrometer/High Resistance Meter.
    """
    def __init__(self, adapter,
                 name="Agilent/Keysight B2985A/B Electrometer/High Resistance Meter",
                 **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )


class AgilentB2987(AgilentB298xAmmeter, AgilentB298xElectrometer, AgilentB298xBattery):
    """
    Agilent/Keysight B2987A/B series Femto/Picoammeter Electrometer/High Resistance Meter.
    """
    def __init__(self, adapter,
                 name="Agilent/Keysight B2987A/B Electrometer/High Resistance Meter",
                 **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
