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

# Parts of this code were copied and adapted from the Agilent33220A class.

import logging
from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from time import time
from pyvisa.errors import VisaIOError

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# Capitalize string arguments to allow for better conformity with other WFG's
# FIXME: Currently not used since it does not combine well with the strict_discrete_set validator
# def capitalize_string(string: str, *args, **kwargs):
#     return string.upper()


# Combine the capitalize function and validator
# FIXME: This validator is not doing anything other then self.capitalize_string
# FIXME: I removed it from this class for now
# string_validator = joined_validators(capitalize_string, strict_discrete_set)


class Agilent33500Channel(Channel):
    """Implementation of a base Agilent 33500 channel"""

    shape = Instrument.control(
        "SOUR{ch}:FUNC?",
        "SOUR{ch}:FUNC %s",
        """ A string property that controls the output waveform. Can be set to:
        SIN<USOID>, SQU<ARE>, TRI<ANGLE>, RAMP, PULS<E>, PRBS,  NOIS<E>, ARB, DC. """,
        validator=strict_discrete_set,
        values=["SIN", "SQU", "TRI", "RAMP", "PULS", "PRBS", "NOIS", "ARB", "DC"],
    )

    frequency = Instrument.control(
        "SOUR{ch}:FREQ?",
        "SOUR{ch}:FREQ %f",
        """ A floating point property that controls the frequency of the output
        waveform in Hz, from 1 uHz to 120 MHz (maximum range, can be lower depending
        on your device), depending on the specified function. """,
        validator=strict_range,
        values=[1e-6, 120e6],
    )

    amplitude = Instrument.control(
        "SOUR{ch}:VOLT?",
        "SOUR{ch}:VOLT %f",
        """ A floating point property that controls the voltage amplitude of the
        output waveform in V, from 10e-3 V to 10 V. Depends on the output
        impedance.""",
        validator=strict_range,
        values=[10e-3, 10],
    )

    amplitude_unit = Instrument.control(
        "SOUR{ch}:VOLT:UNIT?",
        "SOUR{ch}:VOLT:UNIT %s",
        """ A string property that controls the units of the amplitude. Valid
        values are VPP (default), VRMS, and DBM.""",
        validator=strict_discrete_set,
        values=["VPP", "VRMS", "DBM"],
    )

    offset = Instrument.control(
        "SOUR{ch}:VOLT:OFFS?",
        "SOUR{ch}:VOLT:OFFS %f",
        """ A floating point property that controls the voltage offset of the
        output waveform in V, from 0 V to 4.995 V, depending on the set
        voltage amplitude (maximum offset = (Vmax - voltage) / 2).
        """,
        validator=strict_range,
        values=[-4.995, +4.995],
    )

    voltage_high = Instrument.control(
        "SOUR{ch}:VOLT:HIGH?",
        "SOUR{ch}:VOLT:HIGH %f",
        """ A floating point property that controls the upper voltage of the
        output waveform in V, from -4.999 V to 5 V (must be higher than low
        voltage by at least 1 mV).""",
        validator=strict_range,
        values=[-4.999, 5],
    )

    voltage_low = Instrument.control(
        "SOUR{ch}:VOLT:LOW?",
        "SOUR{ch}:VOLT:LOW %f",
        """ A floating point property that controls the lower voltage of the
        output waveform in V, from -5 V to 4.999 V (must be lower than high
        voltage by at least 1 mV).""",
        validator=strict_range,
        values=[-5, 4.999],
    )

    phase = Instrument.control(
        "SOUR{ch}:PHAS?",
        "SOUR{ch}:PHAS %f",
        """ A floating point property that controls the phase of the output
        waveform in degrees, from -360 degrees to 360 degrees. Not available
        for arbitrary waveforms or noise.""",
        validator=strict_range,
        values=[-360, 360],
    )

    square_dutycycle = Instrument.control(
        "SOUR{ch}:FUNC:SQU:DCYC?",
        "SOUR{ch}:FUNC:SQU:DCYC %f",
        """ A floating point property that controls the duty cycle of a square
        waveform function in percent, from 0.01% to 99.98%.
        The duty cycle is limited by the frequency and the minimal pulse width of
        16 ns. See manual for more details.""",
        validator=strict_range,
        values=[0.01, 99.98],
    )

    ramp_symmetry = Instrument.control(
        "SOUR{ch}:FUNC:RAMP:SYMM?",
        "SOUR{ch}:FUNC:RAMP:SYMM %f",
        """ A floating point property that controls the symmetry percentage
        for the ramp waveform, from 0.0% to 100.0%.""",
        validator=strict_range,
        values=[0, 100],
    )

    pulse_period = Instrument.control(
        "SOUR{ch}:FUNC:PULS:PER?",
        "SOUR{ch}:FUNC:PULS:PER %e",
        """ A floating point property that controls the period of a pulse
        waveform function in seconds, ranging from 33 ns to 1 Ms. Can be set
        and overwrites the frequency for *all* waveforms. If the period is
        shorter than the pulse width + the edge time, the edge time and pulse
        width will be adjusted accordingly. """,
        validator=strict_range,
        values=[33e-9, 1e6],
    )

    pulse_hold = Instrument.control(
        "SOUR{ch}:FUNC:PULS:HOLD?",
        "SOUR{ch}:FUNC:PULS:HOLD %s",
        """ A string property that controls if either the pulse width or the
        duty cycle is retained when changing the period or frequency of the
        waveform. Can be set to: WIDT<H> or DCYC<LE>. """,
        validator=strict_discrete_set,
        values=["WIDT", "WIDTH", "DCYC", "DCYCLE"],
    )

    pulse_width = Instrument.control(
        "SOUR{ch}:FUNC:PULS:WIDT?",
        "SOUR{ch}:FUNC:PULS:WIDT %e",
        """ A floating point property that controls the width of a pulse
        waveform function in seconds, ranging from 16 ns to 1e6 s, within a
        set of restrictions depending on the period.""",
        validator=strict_range,
        values=[16e-9, 1e6],
    )

    pulse_dutycycle = Instrument.control(
        "SOUR{ch}:FUNC:PULS:DCYC?",
        "SOUR{ch}:FUNC:PULS:DCYC %f",
        """ A floating point property that controls the duty cycle of a pulse
        waveform function in percent, from 0% to 100%.""",
        validator=strict_range,
        values=[0, 100],
    )

    pulse_transition = Instrument.control(
        "SOUR{ch}:FUNC:PULS:TRAN?",
        "SOUR{ch}:FUNC:PULS:TRAN:BOTH %e",
        """ A floating point property that controls the edge time in
        seconds for both the rising and falling edges. It is defined as the
        time between the 10% and 90% thresholds of the edge.
        Valid values are between 8.4 ns to 1 µs.""",
        validator=strict_range,
        values=[8.4e-9, 1e-6],
    )

    output = Instrument.control(
        "OUTP{ch}?",
        "OUTP{ch} %d",
        """ A boolean property that turns on (True, 'on') or off (False, 'off')
        the output of the function generator.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0},
    )

    output_load = Instrument.control(
        "OUTP{ch}:LOAD?",
        "OUTP{ch}:LOAD %s",
        """ Sets the expected load resistance (should be the load impedance connected
        to the output. The output impedance is always 50 Ohm, this setting can be used
        to correct the displayed voltage for loads unmatched to 50 Ohm.
        Valid values are between 1 and 10 kOhm or INF for high impedance.
        No validator is used since both numeric and string inputs are accepted,
        thus a value outside the range will not return an error.
        """,
    )

    burst_state = Instrument.control(
        "SOUR{ch}:BURS:STAT?",
        "SOUR{ch}:BURS:STAT %d",
        """ A boolean property that controls whether the burst mode is on
        (True) or off (False).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    burst_mode = Instrument.control(
        "SOUR{ch}:BURS:MODE?",
        "SOUR{ch}:BURS:MODE %s",
        """ A string property that controls the burst mode. Valid values
        are: TRIG<GERED>, GAT<ED>.""",
        validator=strict_discrete_set,
        values=["TRIG", "TRIGGERED", "GAT", "GATED"],
    )

    burst_period = Instrument.control(
        "SOUR{ch}:BURS:INT:PER?",
        "SOUR{ch}:BURS:INT:PER %e",
        """ A floating point property that controls the period of subsequent bursts.
        Has to follow the equation burst_period > (burst_ncycles / frequency) + 1 µs.
        Valid values are 1 µs to 8000 s.""",
        validator=strict_range,
        values=[1e-6, 8000],
    )

    burst_ncycles = Instrument.control(
        "SOUR{ch}:BURS:NCYC?",
        "SOUR{ch}:BURS:NCYC %d",
        """ An integer property that sets the number of cycles to be output
        when a burst is triggered. Valid values are 1 to 100000. This can be
        set. """,
        validator=strict_range,
        values=range(1, 100000),
    )

    arb_file = Instrument.control(
        "SOUR{ch}:FUNC:ARB?",
        "SOUR{ch}:FUNC:ARB %s",
        """ A string property that selects the arbitrary signal from the volatile
        memory of the device. String has to match an existing arb signal in volatile
        memory (set by :meth:`data_arb`).""",
    )

    arb_advance = Instrument.control(
        "SOUR{ch}:FUNC:ARB:ADV?",
        "SOUR{ch}:FUNC:ARB:ADV %s",
        """ A string property that selects how the device advances from data point
        to data point. Can be set to 'TRIG<GER>' or 'SRAT<E>' (default). """,
        validator=strict_discrete_set,
        values=["TRIG", "TRIGGER", "SRAT", "SRATE"],
    )

    arb_filter = Instrument.control(
        "SOUR{ch}:FUNC:ARB:FILT?",
        "SOUR{ch}:FUNC:ARB:FILT %s",
        """ A string property that selects the filter setting for arbitrary signals.
        Can be set to 'NORM<AL>', 'STEP' and 'OFF'. """,
        validator=strict_discrete_set,
        values=["NORM", "NORMAL", "STEP", "OFF"],
    )

    arb_srate = Instrument.control(
        "SOUR{ch}:FUNC:ARB:SRAT?",
        "SOUR{ch}:FUNC:ARB:SRAT %f",
        """ An floating point property that sets the sample rate of the currently selected
        arbitrary signal. Valid values are 1 µSa/s to 250 MSa/s (maximum range, can be lower
        depending on your device).""",
        validator=strict_range,
        values=[1e-6, 250e6],
    )

    def data_volatile_clear(self):
        """
        Clear all arbitrary signals from volatile memory for a given channel.

        This should be done if the same name is used continuously to load
        different arbitrary signals into the memory, since an error will occur
        if a trace is loaded which already exists in memory.
        """
        self.write("SOUR{ch}:DATA:VOL:CLE")

    def data_arb(self, arb_name, data_points, data_format="DAC"):
        """
        Uploads an arbitrary trace into the volatile memory of the device for a given channel.

        The data_points can be given as:
        comma separated 16 bit DAC values (ranging from -32767 to +32767),
        as comma separated floating point values (ranging from -1.0 to +1.0),
        or as a binary data stream.
        Check the manual for more information. The storage depends on the device type and ranges
        from 8 Sa to 16 MSa (maximum).

        :param arb_name: The name of the trace in the volatile memory. This is used to access the
                         trace.

        :param data_points: Individual points of the trace. The format depends on the format
                            parameter.

                            format = 'DAC' (default): Accepts list of integer values ranging from
                            -32767 to +32767. Minimum of 8 a maximum of 65536 points.

                            format = 'float': Accepts list of floating point values ranging from
                            -1.0 to +1.0. Minimum of 8 a maximum of 65536 points.

                            format = 'binary': Accepts a binary stream of 8 bit data.
        :param data_format: Defines the format of data_points. Can be 'DAC' (default), 'float' or
                            'binary'. See documentation on parameter data_points above.
        """
        if data_format == "DAC":
            separator = ", "
            data_points_str = [str(item) for item in data_points]  # Turn list entries into strings
            data_string = separator.join(data_points_str)  # Join strings with separator
            self.write(f"SOUR{{ch}}:DATA:ARB:DAC {arb_name}, {data_string}")
            return
        elif data_format == "float":
            separator = ", "
            data_points_str = [str(item) for item in data_points]  # Turn list entries into strings
            data_string = separator.join(data_points_str)  # Join strings with separator
            self.write(f"SOUR{{ch}}:DATA:ARB {arb_name}, {data_string}")
            return
        elif data_format == "binary":  # TODO: *Binary is not yet implemented*
            raise NotImplementedError(
                'The binary format has not yet been implemented. Use "DAC" or "float" instead.'
            )
        else:
            raise ValueError(
                'Undefined format keyword was used. Valid entries are "DAC", "float" and "binary"'
            )


class Agilent33500(Instrument):
    """
    Represents the Agilent 33500 Function/Arbitrary Waveform Generator family.

    Individual devices are represented by subclasses.
    User can specify a channel to control, if no channel specified, a default channel
    is picked based on the device e.g. For Agilent33500B the default channel
    is channel 1. See reference manual for your device

    .. code-block:: python

        generator = Agilent33500("GPIB::1")

        generator.shape = 'SIN'                 # Sets default channel output signal shape to sine
        generator.ch_1.shape = 'SIN'           # Sets channel 1 output signal shape to sine
        generator.frequency = 1e3               # Sets default channel output frequency to 1 kHz
        generator.ch_1.frequency = 1e3         # Sets channel 1 output frequency to 1 kHz
        generator.ch_2.amplitude = 5           # Sets channel 2 output amplitude to 5 Vpp
        generator.ch_2.output = 'on'           # Enables channel 2 output

        generator.ch_1.shape = 'ARB'           # Set channel 1 shape to arbitrary
        generator.ch_1.arb_srate = 1e6         # Set channel 1 sample rate to 1MSa/s

        generator.ch_1.data_volatile_clear()   # Clear channel 1 volatile internal memory
        generator.ch_1.data_arb(               # Send data of arbitrary waveform to channel 1
            'test',
            range(-10000, 10000, +20),          # In this case a simple ramp
            data_format='DAC'                   # Data format is set to 'DAC'
         )
        generator.ch_1.arb_file = 'test'       # Select the transmitted waveform 'test'

    """

    ch_1 = Instrument.ChannelCreator(Agilent33500Channel, 1)

    ch_2 = Instrument.ChannelCreator(Agilent33500Channel, 2)

    def __init__(self, adapter, name="Agilent 33500 Function/Arbitrary Waveform generator family",
                 **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )

    def beep(self):
        """Causes a system beep."""
        self.write("SYST:BEEP")

    shape = Instrument.control(
        "FUNC?",
        "FUNC %s",
        """ A string property that controls the output waveform. Can be set to:
        SIN<USOID>, SQU<ARE>, TRI<ANGLE>, RAMP, PULS<E>, PRBS,  NOIS<E>, ARB, DC. """,
        validator=strict_discrete_set,
        values=["SIN", "SQU", "TRI", "RAMP", "PULS", "PRBS", "NOIS", "ARB", "DC"],
    )

    frequency = Instrument.control(
        "FREQ?",
        "FREQ %f",
        """ A floating point property that controls the frequency of the output
        waveform in Hz, from 1 uHz to 120 MHz (maximum range, can be lower depending
        on your device), depending on the specified function.""",
        validator=strict_range,
        values=[1e-6, 120e6],
    )

    amplitude = Instrument.control(
        "VOLT?",
        "VOLT %f",
        """ A floating point property that controls the voltage amplitude of the
        output waveform in V, from 10e-3 V to 10 V. Depends on the output
        impedance.""",
        validator=strict_range,
        values=[10e-3, 10],
    )

    amplitude_unit = Instrument.control(
        "VOLT:UNIT?",
        "VOLT:UNIT %s",
        """ A string property that controls the units of the amplitude. Valid
        values are VPP (default), VRMS, and DBM.""",
        validator=strict_discrete_set,
        values=["VPP", "VRMS", "DBM"],
    )

    offset = Instrument.control(
        "VOLT:OFFS?",
        "VOLT:OFFS %f",
        """ A floating point property that controls the voltage offset of the
        output waveform in V, from 0 V to 4.995 V, depending on the set
        voltage amplitude (maximum offset = (Vmax - voltage) / 2).
        """,
        validator=strict_range,
        values=[-4.995, +4.995],
    )

    voltage_high = Instrument.control(
        "VOLT:HIGH?",
        "VOLT:HIGH %f",
        """ A floating point property that controls the upper voltage of the
        output waveform in V, from -4.999 V to 5 V (must be higher than low
        voltage by at least 1 mV).""",
        validator=strict_range,
        values=[-4.999, 5],
    )

    voltage_low = Instrument.control(
        "VOLT:LOW?",
        "VOLT:LOW %f",
        """ A floating point property that controls the lower voltage of the
        output waveform in V, from -5 V to 4.999 V (must be lower than high
        voltage by at least 1 mV).""",
        validator=strict_range,
        values=[-5, 4.999],
    )

    phase = Instrument.control(
        "PHAS?",
        "PHAS %f",
        """ A floating point property that controls the phase of the output
        waveform in degrees, from -360 degrees to 360 degrees. Not available
        for arbitrary waveforms or noise.""",
        validator=strict_range,
        values=[-360, 360],
    )

    square_dutycycle = Instrument.control(
        "FUNC:SQU:DCYC?",
        "FUNC:SQU:DCYC %f",
        """ A floating point property that controls the duty cycle of a square
        waveform function in percent, from 0.01% to 99.98%.
        The duty cycle is limited by the frequency and the minimal pulse width of
        16 ns. See manual for more details.""",
        validator=strict_range,
        values=[0.01, 99.98],
    )

    ramp_symmetry = Instrument.control(
        "FUNC:RAMP:SYMM?",
        "FUNC:RAMP:SYMM %f",
        """ A floating point property that controls the symmetry percentage
        for the ramp waveform, from 0.0% to 100.0%.""",
        validator=strict_range,
        values=[0, 100],
    )

    pulse_period = Instrument.control(
        "FUNC:PULS:PER?",
        "FUNC:PULS:PER %e",
        """ A floating point property that controls the period of a pulse
        waveform function in seconds, ranging from 33 ns to 1e6 s. Can be set
        and overwrites the frequency for *all* waveforms. If the period is
        shorter than the pulse width + the edge time, the edge time and pulse
        width will be adjusted accordingly. """,
        validator=strict_range,
        values=[33e-9, 1e6],
    )

    pulse_hold = Instrument.control(
        "FUNC:PULS:HOLD?",
        "FUNC:PULS:HOLD %s",
        """ A string property that controls if either the pulse width or the
        duty cycle is retained when changing the period or frequency of the
        waveform. Can be set to: WIDT<H> or DCYC<LE>. """,
        validator=strict_discrete_set,
        values=["WIDT", "WIDTH", "DCYC", "DCYCLE"],
    )

    pulse_width = Instrument.control(
        "FUNC:PULS:WIDT?",
        "FUNC:PULS:WIDT %e",
        """ A floating point property that controls the width of a pulse
        waveform function in seconds, ranging from 16 ns to 1 Ms, within a
        set of restrictions depending on the period.""",
        validator=strict_range,
        values=[16e-9, 1e6],
    )

    pulse_dutycycle = Instrument.control(
        "FUNC:PULS:DCYC?",
        "FUNC:PULS:DCYC %f",
        """ A floating point property that controls the duty cycle of a pulse
        waveform function in percent, from 0% to 100%.""",
        validator=strict_range,
        values=[0, 100],
    )

    pulse_transition = Instrument.control(
        "FUNC:PULS:TRAN?",
        "FUNC:PULS:TRAN:BOTH %e",
        """ A floating point property that controls the edge time in
        seconds for both the rising and falling edges. It is defined as the
        time between the 10% and 90% thresholds of the edge.
        Valid values are between 8.4 ns to 1 µs.""",
        validator=strict_range,
        values=[8.4e-9, 1e-6],
    )

    output = Instrument.control(
        "OUTP?",
        "OUTP %d",
        """ A boolean property that turns on (True, 'on') or off (False, 'off')
        the output of the function generator.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0},
    )

    output_load = Instrument.control(
        "OUTP:LOAD?",
        "OUTP:LOAD %s",
        """ Sets the expected load resistance (should be the load impedance connected
        to the output. The output impedance is always 50 Ohm, this setting can be used
        to correct the displayed voltage for loads unmatched to 50 Ohm.
        Valid values are between 1 and 10 kOhm or INF for high impedance.
        No validator is used since both numeric and string inputs are accepted,
        thus a value outside the range will not return an error.
        """,
    )

    burst_state = Instrument.control(
        "BURS:STAT?",
        "BURS:STAT %d",
        """ A boolean property that controls whether the burst mode is on
        (True) or off (False).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    burst_mode = Instrument.control(
        "BURS:MODE?",
        "BURS:MODE %s",
        """ A string property that controls the burst mode. Valid values
        are: TRIG<GERED>, GAT<ED>.""",
        validator=strict_discrete_set,
        values=["TRIG", "TRIGGERED", "GAT", "GATED"],
    )

    burst_period = Instrument.control(
        "BURS:INT:PER?",
        "BURS:INT:PER %e",
        """ A floating point property that controls the period of subsequent bursts.
        Has to follow the equation burst_period > (burst_ncycles / frequency) + 1 µs.
        Valid values are 1 µs to 8000 s.""",
        validator=strict_range,
        values=[1e-6, 8000],
    )

    burst_ncycles = Instrument.control(
        "BURS:NCYC?",
        "BURS:NCYC %d",
        """ An integer property that sets the number of cycles to be output
        when a burst is triggered. Valid values are 1 to 100000. This can be
        set. """,
        validator=strict_range,
        values=range(1, 100000),
    )

    arb_file = Instrument.control(
        "FUNC:ARB?",
        "FUNC:ARB %s",
        """ A string property that selects the arbitrary signal from the volatile
        memory of the device. String has to match an existing arb signal in volatile
        memory (set by :meth:`data_arb`).""",
    )

    arb_advance = Instrument.control(
        "FUNC:ARB:ADV?",
        "FUNC:ARB:ADV %s",
        """ A string property that selects how the device advances from data point
        to data point. Can be set to 'TRIG<GER>' or 'SRAT<E>' (default). """,
        validator=strict_discrete_set,
        values=["TRIG", "TRIGGER", "SRAT", "SRATE"],
    )

    arb_filter = Instrument.control(
        "FUNC:ARB:FILT?",
        "FUNC:ARB:FILT %s",
        """ A string property that selects the filter setting for arbitrary signals.
        Can be set to 'NORM<AL>', 'STEP' and 'OFF'. """,
        validator=strict_discrete_set,
        values=["NORM", "NORMAL", "STEP", "OFF"],
    )
    # TODO: This implementation is currently not working. Do not know why.
    # arb_period = Instrument.control(
    #     "FUNC:ARB:PER?", "FUNC:ARB:PER %e",
    #     """ A floating point property that controls the period of the arbitrary signal.
    #     Limited by number of signal points. Check for instrument errors when setting
    #     this property.""",
    #     validator=strict_range,
    #     values=[33e-9, 1e6],
    # )
    #
    # arb_frequency = Instrument.control(
    #     "FUNC:ARB:FREQ?", "FUNC:ARB:FREQ %f",
    #     """ A floating point property that controls the frequency of the arbitrary signal.
    #     Limited by number of signal points. Check for instrument
    #     errors when setting this property.""",
    #     validator=strict_range,
    #     values=[1e-6, 30e+6],
    # )
    #
    # arb_npoints = Instrument.measurement(
    #     "FUNC:ARB:POIN?",
    #     """ Returns the number of points in the currently selected arbitrary trace. """
    # )
    #
    # arb_voltage = Instrument.control(
    #     "FUNC:ARB:PTP?", "FUNC:ARB:PTP %f",
    #     """ An floating point property that sets the peak-to-peak voltage for the
    #     currently selected arbitrary signal. Valid values are 1 mV to 10 V. This can be
    #     set. """,
    #     validator=strict_range,
    #     values=[0.001, 10],
    # )

    arb_srate = Instrument.control(
        "FUNC:ARB:SRAT?",
        "FUNC:ARB:SRAT %f",
        """ An floating point property that sets the sample rate of the currently selected
        arbitrary signal. Valid values are 1 µSa/s to 250 MSa/s (maximum range, can be lower
        depending on your device).""",
        validator=strict_range,
        values=[1e-6, 250e6],
    )

    def data_volatile_clear(self):
        """
        Clear all arbitrary signals from volatile memory.

        This should be done if the same name is used continuously to load
        different arbitrary signals into the memory, since an error
        will occur if a trace is loaded which already exists in the memory.
        """
        self.write("DATA:VOL:CLE")

    def phase_sync(self):
        """ Synchronize the phase of all channels."""
        self.write("PHAS:SYNC")

    def data_arb(self, arb_name, data_points, data_format="DAC"):
        """
        Uploads an arbitrary trace into the volatile memory of the device.

        The data_points can be given as:
        comma separated 16 bit DAC values (ranging from -32767 to +32767),
        as comma separated floating point values (ranging from -1.0 to +1.0)
        or as a binary data stream.
        Check the manual for more information.
        The storage depends on the device type and ranges
        from 8 Sa to 16 MSa (maximum).

        :param arb_name: The name of the trace in the volatile memory. This is used to access the
                         trace.
        :param data_points: Individual points of the trace. The format depends on the format
                            parameter.
                            format = 'DAC' (default): Accepts list of integer values ranging from
                            -32767 to +32767. Minimum of 8 a maximum of 65536 points.
                            format = 'float': Accepts list of floating point values ranging from
                            -1.0 to +1.0. Minimum of 8 a maximum of 65536 points.
                            format = 'binary': Accepts a binary stream of 8 bit data.
        :param data_format: Defines the format of data_points. Can be 'DAC' (default), 'float' or
                            'binary'. See documentation on parameter data_points above.
        """
        if data_format == "DAC":
            separator = ", "
            data_points_str = [str(item) for item in data_points]  # Turn list entries into strings
            data_string = separator.join(data_points_str)  # Join strings with separator
            self.write(f"DATA:ARB:DAC {arb_name}, {data_string}")
            return
        elif data_format == "float":
            separator = ", "
            data_points_str = [str(item) for item in data_points]  # Turn list entries into strings
            data_string = separator.join(data_points_str)  # Join strings with separator
            self.write(f"DATA:ARB {arb_name}, {data_string}")
            return
        elif data_format == "binary":  # TODO: *Binary is not yet implemented*
            raise NotImplementedError(
                'The binary format has not yet been implemented. Use "DAC" or "float" instead.'
            )
        else:
            raise ValueError(
                'Undefined format keyword was used. Valid entries are "DAC", "float" and "binary"'
            )

    display = Instrument.setting(
        "DISP:TEXT '%s'",
        """ A string property which is displayed on the front panel of
        the device.""",
    )

    def clear_display(self):
        """Removes a text message from the display."""
        self.write("DISP:TEXT:CLE")

    def trigger(self):
        """Send a trigger signal to the function generator."""
        self.write("*TRG;*WAI")

    def wait_for_trigger(self, timeout=3600, should_stop=lambda: False):
        """
        Wait until the triggering has finished or timeout is reached.

        :param timeout: The maximum time the waiting is allowed to take. If
                        timeout is exceeded, a TimeoutError is raised. If
                        timeout is set to zero, no timeout will be used.
        :param should_stop: Optional function (returning a bool) to allow the
                            waiting to be stopped before its end.

        """
        self.write("*OPC?")

        t0 = time()
        while True:
            try:
                ready = bool(self.read())
            except VisaIOError:
                ready = False

            if ready:
                return

            if timeout != 0 and time() - t0 > timeout:
                raise TimeoutError(
                    "Timeout expired while waiting for the Agilent 33220A"
                    + " to finish the triggering."
                )

            if should_stop:
                return

    trigger_source = Instrument.control(
        "TRIG:SOUR?",
        "TRIG:SOUR %s",
        """ A string property that controls the trigger source. Valid values
        are: IMM<EDIATE> (internal), EXT<ERNAL> (rear input), BUS (via trigger
        command).""",
        validator=strict_discrete_set,
        values=["IMM", "IMMEDIATE", "EXT", "EXTERNAL", "BUS"],
    )

    ext_trig_out = Instrument.control(
        "OUTP:TRIG?",
        "OUTP:TRIG %d",
        """ A boolean property that controls whether the trigger out signal is
        active (True) or not (False). This signal is output from the Ext Trig
        connector on the rear panel in Burst and Wobbel mode.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )
