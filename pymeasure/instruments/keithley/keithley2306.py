#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley2306Channel(Channel):
    """ Implementation of a Keithley 2306 channel. """

    enabled = Channel.control(
        ":OUTPUT{ch}:STAT?", ":OUTPUT{ch}:STAT %d",
        """A boolean property that controls whether the output is enabled, takes
        values True or False. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    bandwidth = Channel.control(
        ":OUTPUT{ch}:BAND?", ":OUTPUT{ch}:BAND %s",
        """A string property that controls the output bandwidth when the output
        is enabled and the current range is set to 5 A. Takes values 'HIGH' or
        'LOW'. If the output is disabled or the current range is set to 5 mA the
        bandwidth is 'LOW'. """,
        validator=strict_discrete_set,
        values={'low': 'LOW', 'high': 'HIGH'},
        map_values=True,
    )

    sense_mode = Channel.control(
        ":SENS{ch}:FUNC?", ":SENS{ch}:FUNC \"%s\"",
        """A string property that controls the channel sense mode, which can
        take the values 'voltage', 'current', 'dvm', 'pulse_current',
        or 'long_integration'. """,
        validator=strict_discrete_set,
        values={'voltage': 'VOLT', 'current': 'CURR', 'dvm': 'DVM',
                'pulse_current': 'PCUR', 'long_integration': 'LINT'},
        map_values=True,
        get_process=lambda v: v.replace('"', ''),
    )

    nplc = Channel.control(
        ":SENS{ch}:NPLC?", ":SENS{ch}:NPLC %g",
        """A floating point property that controls the number of power line
        cycles (NPLC) for voltage, current, and DVM measurements. Takes
        values from 0.01 to 10. """,
        validator=truncated_range,
        values=[0.01, 10],
    )

    average_count = Channel.control(
        ":SENS{ch}:AVER?", ":SENS{ch}:AVER %d",
        """An integer property that controls the average count for voltage,
        current, and DVM measurements. Takes values from 1 to 10. """,
        validator=truncated_range,
        values=[1, 10],
    )

    current_range = Channel.control(
        ":SENS{ch}:CURR:RANG?", ":SENS{ch}:CURR:RANG %g",
        """A floating point property that controls the current range which
        takes values of 5 mA and 5 A (or 500 mA and 5 A for the 2306-PJ).""",
        validator=strict_discrete_set,
        values=[0.005, 0.5, 5],
    )

    current_range_auto = Channel.control(
        ":SENS{ch}:CURR:RANG:AUTO?", ":SENS{ch}:CURR:RANG:AUTO %d",
        """A boolean point property that controls whether current range
        is in auto mode. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    pulse_current_average_count = Channel.control(
        ":SENS{ch}:PCUR:AVER?", ":SENS{ch}:PCUR:AVER %d",
        """An integer property that controls the average count for pulse
        current measurements. Takes values from 1 to either 100 if
        pulse_current_measure_enabled is set to True, 5000 otherwise. """,
        validator=truncated_range,
        values=[1, 5000],
    )

    pulse_current_measure_enabled = Channel.control(
        ":SENS{ch}:PCUR:SYNC?", ":SENS{ch}:PCUR:SYNC %d",
        """A boolean property that controls whether pulse current
        measurements are enabled (True) or whether the channel is in
        digitization mode (False). """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    pulse_current_trigger_delay = Channel.control(
        ":SENS{ch}:PCUR:SYNC:DEL?", ":SENS{ch}:PCUR:SYNC:DEL %g",
        """A floating point property that controls the pulse current trigger
        delay in seconds. Takes values from 0 to either 0.1 if
        pulse_current_measure_enabled is set to True, 5 otherwise.""",
        validator=truncated_range,
        values=[0, 5],
    )

    pulse_current_trigger_level = Channel.control(
        ":SENS{ch}:PCUR:SYNC:TLEV?", ":SENS{ch}:PCUR:SYNC:TLEV %g",
        """A floating point property that controls the pulse current trigger
        level in amps. Takes values between 0 and 5.""",
        validator=truncated_range,
        values=[0, 5],
    )

    pulse_current_mode = Channel.control(
        ":SENS{ch}:PCUR:MODE?", ":SENS{ch}:PCUR:MODE %s",
        """A string property that controls the pulse current measurement
        mode, which can take the values 'high', 'low', or 'average'. """,
        validator=strict_discrete_set,
        values={'high': 'HIGH', 'low': 'LOW', 'average': 'AVER'},
        map_values=True,
    )

    def pulse_current_time_auto(self):
        """Arranges for the instrument to control integration times. """
        self.write(":SENS{ch}:PCUR:TIME:AUTO")

    pulse_current_time_high = Channel.control(
        ":SENS{ch}:PCUR:TIME:HIGH?", ":SENS{ch}:PCUR:TIME:HIGH %g",
        """A floating point property that controls the integration time (in
        seconds) for high pulse measurements. Takes on values between
        33.33333e-06 and 0.8333. """,
        validator=truncated_range,
        values=[33.33333e-06, 0.8333],
    )

    pulse_current_time_low = Channel.control(
        ":SENS{ch}:PCUR:TIME:LOW?", ":SENS{ch}:PCUR:TIME:LOW %g",
        """A floating point property that controls the integration time (in
        seconds) for low pulse measurements. Takes on values between
        33.33333e-06 and 0.8333. """,
        validator=truncated_range,
        values=[33.33333e-06, 0.8333],
    )

    pulse_current_time_average = Channel.control(
        ":SENS{ch}:PCUR:TIME:AVER?", ":SENS{ch}:PCUR:TIME:AVER %g",
        """A floating point property that controls the integration time (in
        seconds) for average pulse measurements. Takes on values between
        33.33333e-06 and 0.8333. """,
        validator=truncated_range,
        values=[33.33333e-06, 0.8333],
    )

    pulse_current_time_digitize = Channel.control(
        ":SENS{ch}:PCUR:TIME:DIG?", ":SENS{ch}:PCUR:TIME:DIG %g",
        """A floating point property that controls the integration time (in
        seconds) for digitizing or burst pulse measurements. Takes on values
        between 33.33333e-06 and 0.8333. """,
        validator=truncated_range,
        values=[33.33333e-06, 0.8333],
    )

    pulse_current_fast_enabled = Channel.control(
        ":SENS{ch}:PCUR:FAST?", ":SENS{ch}:PCUR:FAST %d",
        """A boolean property that controls whether pulse current fast readings
        are enabled. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    pulse_current_search_enabled = Channel.control(
        ":SENS{ch}:PCUR:SEAR?", ":SENS{ch}:PCUR:SEAR %d",
        """A boolean property that controls whether pulse current search
        is enabled. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    pulse_current_detect_enabled = Channel.control(
        ":SENS{ch}:PCUR:DET?", ":SENS{ch}:PCUR:DET %d",
        """A boolean property that controls whether pulse current detection
        mode is enabled. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    pulse_current_timeout = Channel.control(
        ":SENS{ch}:PCUR:TOUT?", ":SENS{ch}:PCUR:TOUT %g",
        """A floating point property that controls the pulse current timeout
        in seconds, which takes on values between 0.005 and 32. """,
        validator=truncated_range,
        values=[0.005, 32],
    )

    long_integration_trigger_edge = Channel.control(
        ":SENS{ch}:LINT:TEDG?", ":SENS{ch}:LINT:TEDG %s",
        """A string property that controls the long integration trigger edge,
         which can take the values 'rising', 'falling', or 'neither'. """,
        validator=strict_discrete_set,
        values={'rising': 'RISING', 'falling': 'FALLING', 'neither': 'NEITHER'},
        map_values=True,
    )

    long_integration_time = Channel.control(
        ":SENS{ch}:LINT:TIME?", ":SENS{ch}:LINT:TIME %g",
        """A floating point property that controls the long integration time
        in seconds, which takes on values in the range of 0.850 for 60 Hz and
         0.840 for 50 Hz up to 60. """,
        validator=truncated_range,
        values=[0.840, 60],
    )

    def long_integration_time_auto(self):
        """Arranges for the instrument to control integration times. """
        self.write(":SENS{ch}:LINT:TIME:AUTO")

    long_integration_trigger_level = Channel.control(
        ":SENS{ch}:LINT:TLEV?", ":SENS{ch}:LINT:TLEV %g",
        """A floating point property that controls the long integration trigger
        level in amps, which takes values between 0 and 5. """,
        validator=truncated_range,
        values=[0, 5],
    )

    long_integration_timeout = Channel.control(
        ":SENS{ch}:LINT:TOUT?", ":SENS{ch}:LINT:TOUT %g",
        """A floating point property that controls the long integration timeout
        in seconds, which takes values between 1 and 63. """,
        validator=truncated_range,
        values=[1, 63],
    )

    long_integration_fast_enabled = Channel.control(
        ":SENS{ch}:LINT:FAST?", ":SENS{ch}:LINT:FAST %d",
        """A boolean property that controls whether long integration fast
        readings are enabled. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    long_integration_search_enabled = Channel.control(
        ":SENS{ch}:LINT:SEAR?", ":SENS{ch}:LINT:SEAR %d",
        """A boolean property that controls whether long integration search
        is enabled. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    long_integration_detect_enabled = Channel.control(
        ":SENS{ch}:LINT:DET?", ":SENS{ch}:LINT:DET %d",
        """A boolean property that controls whether long integration detection
        mode is enabled. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    source_voltage = Channel.control(
        ":SOUR{ch}:VOLT?", ":SOUR{ch}:VOLT %g",
        """A floating point property that controls the source voltage in volts,
        which takes values between 0 and 15. """,
        validator=truncated_range,
        values=[0, 15],
    )

    source_voltage_protection = Channel.control(
        ":SOUR{ch}:VOLT:PROT?", ":SOUR{ch}:VOLT:PROT %g",
        """A floating point property that controls the source voltage protection
        offset in volts, which takes values between 0 and 8. """,
        validator=truncated_range,
        values=[0, 8],
    )

    source_voltage_protection_enabled = Channel.measurement(
        ":SOUR{ch}:VOLT:PROT:STAT?",
        """A boolean property that returns the source voltage protection state.
        If this property is True, the source has been shut off in accordance
        with the source voltage protection settings. If this property is False,
        the source has not been shut off due to voltage protection. """,
        cast=bool
    )

    source_voltage_protection_clamp_enabled = Channel.control(
        ":SOUR{ch}:VOLT:PROT:CLAM?", ":SOUR{ch}:VOLT:PROT:CLAM %d",
        """A boolean property that controls whether source voltage protection
        clamp is enabled. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    source_current_limit = Channel.control(
        ":SOUR{ch}:CURR?", ":SOUR{ch}:CURR %g",
        """A floating point property that controls the source current limit in
        amps, which takes values between 0.006 and 5. """,
        validator=truncated_range,
        values=[0.006, 5],
    )

    source_current_limit_type = Channel.control(
        ":SOUR{ch}:CURR:TYPE?", ":SOUR{ch}:CURR:TYPE %s",
        """A string property that controls source current limit type, which can
        take the values 'limit' or 'trip'. """,
        validator=strict_discrete_set,
        values={'limit': 'LIM', 'trip': 'TRIP'},
        map_values=True,
    )

    source_current_limit_enabled = Channel.measurement(
        ":SOUR{ch}:CURR:STAT?",
        """A boolean property that returns the source current limit state. If
        this property is True, the source is in either in current limit mode,
        or has tripped (shut off), based on the `source_current_limit_type`
        setting. If this property is False, the source is not being limited and
        has not been tripped. """,
        cast=bool
    )

    last_reading = Channel.measurement(
        ":FETCH{ch}?",
        """A floating point property that returns the last reading. """
    )

    last_readings = Channel.measurement(
        ":FETCH{ch}:ARR?",
        """A floating point array property that returns the last readings. """,
        get_process=lambda v: v if isinstance(v, list) else [v]
    )

    reading = Channel.measurement(
        ":READ{ch}?",
        """A floating point property that triggers and returns a reading
        in accordance with sense_mode. """
    )

    readings = Channel.measurement(
        ":READ{ch}:ARR?",
        """A floating point array property that triggers and returns readings
        in accordance with sense_mode. """,
        get_process=lambda v: v if isinstance(v, list) else [v]
    )

    measured_voltage = Channel.measurement(
        ":MEAS{ch}:VOLT?",
        """A floating point property that triggers and returns a voltage
        reading. """
    )

    measured_voltages = Channel.measurement(
        ":MEAS{ch}:ARR:VOLT?",
        """A floating point array property that triggers and returns
        voltage readings. """,
        get_process=lambda v: v if isinstance(v, list) else [v]
    )

    measured_current = Channel.measurement(
        ":MEAS{ch}:CURR?",
        """A floating point property that triggers and returns a current
        reading. """
    )

    measured_currents = Channel.measurement(
        ":MEAS{ch}:ARR:CURR?",
        """A floating point array property that triggers and returns
        current readings. """,
        get_process=lambda v: v if isinstance(v, list) else [v]
    )

    dvm_voltage = Channel.measurement(
        ":MEAS{ch}:DVM?",
        """A floating point property that triggers and returns a DVM voltage
        reading. """
    )

    dvm_voltages = Channel.measurement(
        ":MEAS{ch}:ARR:DVM?",
        """A floating point array property that triggers and returns
        DVM voltage readings. """,
        get_process=lambda v: v if isinstance(v, list) else [v]
    )

    pulse_current = Channel.measurement(
        ":MEAS{ch}:PCUR?",
        """A floating point property that returns a pulse current reading. """
    )

    pulse_currents = Channel.measurement(
        ":MEAS{ch}:ARR:PCUR?",
        """A floating point array property that triggers and returns
        pulse current readings. """,
        get_process=lambda v: v if isinstance(v, list) else [v]
    )

    long_integration_current = Channel.measurement(
        ":MEAS{ch}:LINT?",
        """A floating point property that returns a long integration current
        reading. """
    )

    long_integration_currents = Channel.measurement(
        ":MEAS{ch}:ARR:LINT?",
        """A floating point array property that triggers and returns
        long integration current readings. """,
        get_process=lambda v: v if isinstance(v, list) else [v]
    )


class BatteryChannel(Keithley2306Channel):
    """ Implementation of a Keithley 2306 battery channel. """

    impedance = Keithley2306Channel.control(
        ":OUTPUT{ch}:IMP?", ":OUTPUT{ch}:IMP %g",
        """A floating point property that controls the output impedance in ohms.
        Takes values from 0 to 1, in 10 milliohm steps.""",
        validator=truncated_range,
        values=[0, 1],
    )

    pulse_current_step_enabled = Keithley2306Channel.control(
        ":SENS{ch}:PCUR:STEP?", ":SENS{ch}:PCUR:STEP %d",
        """A boolean property that controls whether a series of pulse current
        step measurements is enabled.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    pulse_current_step_up_count = Keithley2306Channel.control(
        ":SENS{ch}:PCUR:STEP:UP?", ":SENS{ch}:PCUR:STEP:UP %d",
        """An integer property that controls the number of up steps. Takes
        values from 0 to 20 (max is both up and down combined). """,
        validator=truncated_range,
        values=[0, 20],
    )

    pulse_current_step_down_count = Keithley2306Channel.control(
        ":SENS{ch}:PCUR:STEP:DOWN?", ":SENS{ch}:PCUR:STEP:DOWN %d",
        """An integer property that controls the number of down steps. Takes
        values from 0 to 20 (max is both up and down combined). """,
        validator=truncated_range,
        values=[0, 20],
    )

    pulse_current_step_time = Keithley2306Channel.control(
        ":SENS{ch}:PCUR:STEP:TIME?", ":SENS{ch}:PCUR:STEP:TIME %g",
        """A floating point property that controls the integration time for up
        plus down steps in seconds. Takes values from 33.33333e-06 to 100e-3. """,
        validator=truncated_range,
        values=[33.33333e-06, 100e-3],
    )

    pulse_current_step_timeout = Keithley2306Channel.control(
        ":SENS{ch}:PCUR:STEP:TOUT?", ":SENS{ch}:PCUR:STEP:TOUT %g",
        """A floating point property that controls the integration timeout for
        pulse current steps in seconds (for all but the first step). Takes values
        from 2e-3 to 200e-3. """,
        validator=truncated_range,
        values=[2e-3, 200e-3],
    )

    pulse_current_step_timeout_initial = Keithley2306Channel.control(
        ":SENS{ch}:PCUR:STEP:TOUT:INIT?", ":SENS{ch}:PCUR:STEP:TOUT:INIT %g",
        """A floating point property that controls the integration timeout for
        the initial pulse current step in seconds. Takes values from 10e-3
        to 60. """,
        validator=truncated_range,
        values=[10e-3, 60],
    )

    pulse_current_step_delay = Keithley2306Channel.control(
        ":SENS{ch}:PCUR:STEP:DEL?", ":SENS{ch}:PCUR:STEP:DEL %g",
        """A floating point property that controls the pulse current step delay
        in seconds. Takes values from 0 to 100e-3 in 10e-6 increments. """,
        validator=truncated_range,
        values=[0, 100e-3],
    )

    pulse_current_step_range = Keithley2306Channel.control(
        ":SENS{ch}:PCUR:STEP:RANG?", ":SENS{ch}:PCUR:STEP:RANG %g",
        """A floating point property that controls the pulse current step trigger
        level range in amps. Takes values of 100e-3, 1, or 5. """,
        validator=strict_discrete_set,
        values=[100e-3, 1, 5],
    )

    pulse_current_trigger_level_range = Keithley2306Channel.control(
        ":SENS{ch}:PCUR:SYNC:TLEV:RANG?", ":SENS{ch}:PCUR:SYNC:TLEV:RANG %g",
        """A floating point property that controls the pulse current trigger
        level range in amps. Takes values of 100e-3, 1, or 5. """,
        validator=strict_discrete_set,
        values=[100e-3, 1, 5],
    )

    long_integration_trigger_level_range = Keithley2306Channel.control(
        ":SENS{ch}:LINT:TLEV:RANG?", ":SENS{ch}:LINT:TLEV:RANG %g",
        """A floating point property that controls the long integration trigger
        level range in amps. Takes values of 100e-3, 1, or 5. """,
        validator=strict_discrete_set,
        values=[100e-3, 1, 5],
    )

    def pulse_current_step(self, step_number):
        """Create a new current step point for this instrument.

        :param: step_number:
            int: the number of the step to be created
        :type: :class:`.Step`

        """
        return Step(self.parent, step_number)


class Step(Channel):
    """ Implementation of a Keithley 2306 step. """
    placeholder = 'step'
    trigger_level = Channel.control(
        ":SENS:PCUR:STEP:TLEV{step}?", ":SENS:PCUR:STEP:TLEV{step} %g",
        """A floating point property that controls the pulse current step trigger
        level range in amps. Takes values from 0 up to the range set via
        pulse_current_step_range.""",
        validator=truncated_range,
        values=[0, 5],
    )

    def __init__(self, instrument, number, **kwargs):
        super().__init__(instrument, number, **kwargs)


class Relay(Channel):
    """ Implementation of a Keithley 2306 relay. """

    closed = Channel.control(
        ":OUTP:REL{ch}?", ":OUTP:REL{ch} %s",
        """A boolean property that controls whether the relay is closed (True)
        or open (False). """,
        validator=strict_discrete_set,
        values={True: 'ONE', False: 'ZERO'},
        map_values=True
    )


class Keithley2306(Instrument):
    """ Represents the Keithley 2306 Dual Channel Battery/Charger Simulator.
    """

    def __init__(self, adapter, name="Keithley 2306", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        self.ch1 = BatteryChannel(self, 1)
        self.ch2 = Keithley2306Channel(self, 2)
        self.relay1 = Relay(self, 1)
        self.relay2 = Relay(self, 2)
        self.relay3 = Relay(self, 3)
        self.relay4 = Relay(self, 4)

    display_enabled = Instrument.control(
        ":DISP:ENAB?", ":DISP:ENAB %d",
        """A boolean property that controls whether the display is enabled,
        takes values True or False. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    display_brightness = Instrument.control(
        ":DISP:BRIG?", ":DISP:BRIG %g",
        """A floating point property that controls the display brightness,
        takes values beteween 0.0 and 1.0. A blank display is 0.0,
        1/4 brightness is for values less or equal to 0.25, otherwise 1/2
        brightness for values less than or equal to 0.5, otherwise 3/4
        brightness for values less than or equal to 0.75, otherwise full
        brightness. """,
        validator=truncated_range,
        values=[0, 1],
    )

    display_channel = Instrument.control(
        ":DISP:CHAN?", ":DISP:CHAN %d",
        """An integer property that controls the display channel, takes
        values 1 or 2. """,
        validator=strict_discrete_set,
        values=[1, 2],
    )

    display_text_data = Instrument.control(
        ":DISP:TEXT:DATA?", ":DISP:TEXT:DATA \"%s\"",
        """A string property that control text to be displayed, takes strings
        up to 32 characters. """,
        get_process=lambda v: v.replace('"', '')
    )

    display_text_enabled = Instrument.control(
        ":DISP:TEXT:STAT?", ":DISP:TEXT:STAT %d",
        """A boolean property that controls whether display text is enabled,
        takes values True or False. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    both_channels_enabled = Instrument.setting(
        ":BOTHOUT%s",
        """A boolean setting that controls whether both channel outputs are
        enabled, takes values of True or False. """,
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    def ch(self, channel_number):
        """Get a channel from this instrument.

        :param: channel_number:
            int: the number of the channel to be selected
        :type: :class:`.Keithley2306Channel`

        """
        if channel_number == 1:
            return self.ch1
        elif channel_number == 2:
            return self.ch2
        else:
            raise ValueError("Invalid channel number. Must be 1 or 2.")

    def relay(self, relay_number):
        """Get a relay channel from this instrument.

        :param: relay_number:
            int: the number of the relay to be selected
        :type: :class:`.Relay`

        """
        if relay_number == 1:
            return self.relay1
        elif relay_number == 2:
            return self.relay2
        elif relay_number == 3:
            return self.relay3
        elif relay_number == 4:
            return self.relay4
        else:
            raise ValueError("Invalid relay number. Must be 1, 2, 3, or 4")
