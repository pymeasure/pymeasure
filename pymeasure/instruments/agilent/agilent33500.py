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

# Parts of this code were copied and adapted from the Agilent33220A class.

import logging
from pymeasure.instruments import Instrument, Channel, SCPIMixin
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
        """ Control the output waveform shape (str).""",
        validator=strict_discrete_set,
        values=["SIN", "SQU", "TRI", "RAMP", "PULS", "PRBS", "NOIS", "ARB", "DC"],
        dynamic=True,
    )

    frequency = Instrument.control(
        "SOUR{ch}:FREQ?",
        "SOUR{ch}:FREQ %f",
        """ Control the waveform frequency in Hz (float). Depends on the specified shape.""",
        validator=strict_range,
        values=[1e-6, 120e6],
        dynamic=True,
    )

    amplitude = Instrument.control(
        "SOUR{ch}:VOLT?",
        "SOUR{ch}:VOLT %f",
        """ Control the voltage amplitude in Volts (float).""",
        validator=strict_range,
        values=[10e-3, 10],
        dynamic=True,
    )

    amplitude_unit = Instrument.control(
        "SOUR{ch}:VOLT:UNIT?",
        "SOUR{ch}:VOLT:UNIT %s",
        """ Control the amplitude units (string, strictly 'VPP', 'VRMS', or 'DBM').""",
        validator=strict_discrete_set,
        values=["VPP", "VRMS", "DBM"],
        dynamic=True,
    )

    offset = Instrument.control(
        "SOUR{ch}:VOLT:OFFS?",
        "SOUR{ch}:VOLT:OFFS %f",
        """ Control the voltage offset in Volts (float).""",
        validator=strict_range,
        values=[-4.995, +4.995],
        dynamic=True,
    )

    voltage_high = Instrument.control(
        "SOUR{ch}:VOLT:HIGH?",
        "SOUR{ch}:VOLT:HIGH %f",
        """ Control the upper voltage level in Volts (float).""",
        validator=strict_range,
        values=[-4.999, 5],
        dynamic=True,
    )

    voltage_low = Instrument.control(
        "SOUR{ch}:VOLT:LOW?",
        "SOUR{ch}:VOLT:LOW %f",
        """ Control the lower voltage level in Volts (float).""",
        validator=strict_range,
        values=[-5, 4.999],
        dynamic=True,
    )

    phase = Instrument.control(
        "SOUR{ch}:PHAS?",
        "SOUR{ch}:PHAS %f",
        """ Control the waveform phase in degrees (float, truncated from -360 to 360).""",
        validator=strict_range,
        values=[-360, 360],
    )

    square_dutycycle = Instrument.control(
        "SOUR{ch}:FUNC:SQU:DCYC?",
        "SOUR{ch}:FUNC:SQU:DCYC %f",
        """ Control the square wave duty cycle in percent (float).""",
        validator=strict_range,
        values=[0.01, 99.98],
        dynamic=True,
    )

    ramp_symmetry = Instrument.control(
        "SOUR{ch}:FUNC:RAMP:SYMM?",
        "SOUR{ch}:FUNC:RAMP:SYMM %f",
        """ Control the ramp waveform symmetry in percent (float, truncated from 0 to 100).""",
        validator=strict_range,
        values=[0, 100],
        dynamic=True,
    )

    pulse_period = Instrument.control(
        "SOUR{ch}:FUNC:PULS:PER?",
        "SOUR{ch}:FUNC:PULS:PER %e",
        """ Control the pulse period in seconds (float). Overwrites frequency.
        If the period is shorter than the pulse width + the edge time, the edge
        time and pulse width are adjusted.""",
        validator=strict_range,
        values=[33e-9, 1e6],
        dynamic=True,
    )

    pulse_hold = Instrument.control(
        "SOUR{ch}:FUNC:PULS:HOLD?",
        "SOUR{ch}:FUNC:PULS:HOLD %s",
        """ Control whether pulse width or duty cycle is maintained when the
        period or frequency of the waveform is changed (str).""",
        validator=strict_discrete_set,
        values=["WIDT", "WIDTH", "DCYC", "DCYCLE"],
        dynamic=True,
    )

    pulse_width = Instrument.control(
        "SOUR{ch}:FUNC:PULS:WIDT?",
        "SOUR{ch}:FUNC:PULS:WIDT %e",
        """ Control the pulse width in seconds (float).""",
        validator=strict_range,
        values=[16e-9, 1e6],
        dynamic=True,
    )

    pulse_dutycycle = Instrument.control(
        "SOUR{ch}:FUNC:PULS:DCYC?",
        "SOUR{ch}:FUNC:PULS:DCYC %f",
        """ Control the pulse duty cycle in percent (float, truncated from 0 to 100).""",
        validator=strict_range,
        values=[0, 100],
        dynamic=True,
    )

    pulse_transition = Instrument.control(
        "SOUR{ch}:FUNC:PULS:TRAN?",
        "SOUR{ch}:FUNC:PULS:TRAN:BOTH %e",
        """ Control the pulse edge time (both rising and falling) in seconds (float).""",
        validator=strict_range,
        values=[8.4e-9, 1e-6],
        dynamic=True,
    )

    output = Instrument.control(
        "OUTP{ch}?",
        "OUTP{ch} %d",
        """ Control the output state (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0},
        dynamic=True,
    )

    output_load = Instrument.control(
        "OUTP{ch}:LOAD?",
        "OUTP{ch}:LOAD %s",
        """ Control the expected load resistance in Ohms (str or float). The output impedance
        is always 50 Ohm, this setting can be used to correct the displayed voltage for
        loads unmatched to 50 Ohm.""",
        dynamic=True,
    )

    burst_state = Instrument.control(
        "SOUR{ch}:BURS:STAT?",
        "SOUR{ch}:BURS:STAT %d",
        """ Control the burst mode state (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
        dynamic=True,
    )

    burst_mode = Instrument.control(
        "SOUR{ch}:BURS:MODE?",
        "SOUR{ch}:BURS:MODE %s",
        """ Control the burst mode type (str, strictly 'TRIG<GERED>' or 'GAT<ED>').""",
        validator=strict_discrete_set,
        values=["TRIG", "TRIGGERED", "GAT", "GATED"],
        dynamic=True,
    )

    burst_period = Instrument.control(
        "SOUR{ch}:BURS:INT:PER?",
        "SOUR{ch}:BURS:INT:PER %e",
        """ Control the period of subsequent bursts in seconds (float).""",
        validator=strict_range,
        values=[1e-6, 8000],
        dynamic=True,
    )

    burst_ncycles = Instrument.control(
        "SOUR{ch}:BURS:NCYC?",
        "SOUR{ch}:BURS:NCYC %d",
        """ Control the number of cycles to be output when a burst is triggered (int).""",
        validator=strict_range,
        values=range(1, 100000),
        dynamic=True,
    )

    arb_file = Instrument.control(
        "SOUR{ch}:FUNC:ARB?",
        "SOUR{ch}:FUNC:ARB %s",
        """ Control the arbitrary signal to use from the volatile memory of the device.""",
        dynamic=True,
    )

    arb_advance = Instrument.control(
        "SOUR{ch}:FUNC:ARB:ADV?",
        "SOUR{ch}:FUNC:ARB:ADV %s",
        """ Control how the device advances from data point to data point (str).
        Can be set to 'TRIG<GER>' or 'SRAT<E>' (default).""",
        validator=strict_discrete_set,
        values=["TRIG", "TRIGGER", "SRAT", "SRATE"],
    )

    arb_filter = Instrument.control(
        "SOUR{ch}:FUNC:ARB:FILT?",
        "SOUR{ch}:FUNC:ARB:FILT %s",
        """ Control the filter setting for arbitrary signals (str).
        Can be set to 'NORM<AL>', 'STEP' and 'OFF'.""",
        validator=strict_discrete_set,
        values=["NORM", "NORMAL", "STEP", "OFF"],
    )

    arb_srate = Instrument.control(
        "SOUR{ch}:FUNC:ARB:SRAT?",
        "SOUR{ch}:FUNC:ARB:SRAT %f",
        """ Control the sample rate of the currently selected arbitrary signal in Sa/s (float).
        Valid values range from 1 µSa/s to 250 MSa/s (maximum range, device-dependent).""",
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


class Agilent33500(SCPIMixin, Instrument):
    """
    Represents the Agilent 33500 Function/Arbitrary Waveform Generator family.

    Individual devices are represented by subclasses.
    User can specify a channel to control, if no channel specified, a default channel
    is picked based on the device e.g. For Agilent33500B the default channel
    is channel 1. See reference manual for your device

    .. code-block:: python

        generator = Agilent33500("GPIB::1")

        generator.shape = 'SIN'                 # Sets default channel output signal shape to sine
        generator.channels[1].shape = 'SIN'           # Sets channel 1 output signal shape to sine
        generator.frequency = 1e3               # Sets default channel output frequency to 1 kHz
        generator.channels[1].frequency = 1e3         # Sets channel 1 output frequency to 1 kHz
        generator.channels[2].amplitude = 5           # Sets channel 2 output amplitude to 5 Vpp
        generator.channels[2].output = 'on'           # Enables channel 2 output

        generator.channels[1].shape = 'ARB'           # Set channel 1 shape to arbitrary
        generator.channels[1].arb_srate = 1e6         # Set channel 1 sample rate to 1MSa/s

        generator.channels[1].data_volatile_clear()   # Clear channel 1 volatile internal memory
        generator.channels[1].data_arb(               # Send data of arbitrary waveform to channel 1
            'test',
            range(-10000, 10000, +20),          # In this case a simple ramp
            data_format='DAC'                   # Data format is set to 'DAC'
         )
        generator.channels[1].arb_file = 'test'       # Select the transmitted waveform 'test'

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
        """ Control the output waveform shape (str).""",
        validator=strict_discrete_set,
        values=["SIN", "SQU", "TRI", "RAMP", "PULS", "PRBS", "NOIS", "ARB", "DC"],
        dynamic=True,
    )

    frequency = Instrument.control(
        "FREQ?",
        "FREQ %f",
        """ Control the waveform frequency in Hz (float). Depends on the specified shape.""",
        validator=strict_range,
        values=[1e-6, 120e6],
        dynamic=True,
    )

    amplitude = Instrument.control(
        "VOLT?",
        "VOLT %f",
        """ Control the voltage amplitude in Volts (float).""",
        validator=strict_range,
        values=[10e-3, 10],
        dynamic=True,
    )

    amplitude_unit = Instrument.control(
        "VOLT:UNIT?",
        "VOLT:UNIT %s",
        """ Control the amplitude units (string, strictly 'VPP', 'VRMS', or 'DBM').""",
        validator=strict_discrete_set,
        values=["VPP", "VRMS", "DBM"],
        dynamic=True,
    )

    offset = Instrument.control(
        "VOLT:OFFS?",
        "VOLT:OFFS %f",
        """ Control the voltage offset in Volts (float).""",
        validator=strict_range,
        values=[-4.995, +4.995],
        dynamic=True,
    )

    voltage_high = Instrument.control(
        "VOLT:HIGH?",
        "VOLT:HIGH %f",
        """ Control the upper voltage level in Volts (float).""",
        validator=strict_range,
        values=[-4.999, 5],
        dynamic=True,
    )

    voltage_low = Instrument.control(
        "VOLT:LOW?",
        "VOLT:LOW %f",
        """ Control the lower voltage level in Volts (float).""",
        validator=strict_range,
        values=[-5, 4.999],
        dynamic=True,
    )

    phase = Instrument.control(
        "PHAS?",
        "PHAS %f",
        """ Control the waveform phase in degrees (float, truncated from -360 to 360).""",
        validator=strict_range,
        values=[-360, 360],
    )

    square_dutycycle = Instrument.control(
        "FUNC:SQU:DCYC?",
        "FUNC:SQU:DCYC %f",
        """ Control the square wave duty cycle in percent (float).""",
        validator=strict_range,
        values=[0.01, 99.98],
        dynamic=True,
    )

    ramp_symmetry = Instrument.control(
        "FUNC:RAMP:SYMM?",
        "FUNC:RAMP:SYMM %f",
        """ Control the ramp waveform symmetry in percent (float, truncated from 0 to 100).""",
        validator=strict_range,
        values=[0, 100],
        dynamic=True,
    )

    pulse_period = Instrument.control(
        "FUNC:PULS:PER?",
        "FUNC:PULS:PER %e",
        """ Control the pulse period in seconds (float). Overwrites frequency.
        If the period is shorter than the pulse width + the edge time, the edge
        time and pulse width are adjusted.""",
        validator=strict_range,
        values=[33e-9, 1e6],
        dynamic=True,
    )

    pulse_hold = Instrument.control(
        "FUNC:PULS:HOLD?",
        "FUNC:PULS:HOLD %s",
        """ Control whether pulse width or duty cycle is maintained when the
        period or frequency of the waveform is changed (str).""",
        validator=strict_discrete_set,
        values=["WIDT", "WIDTH", "DCYC", "DCYCLE"],
        dynamic=True,
    )

    pulse_width = Instrument.control(
        "FUNC:PULS:WIDT?",
        "FUNC:PULS:WIDT %e",
        """ Control the pulse width in seconds (float).""",
        validator=strict_range,
        values=[16e-9, 1e6],
        dynamic=True,
    )

    pulse_dutycycle = Instrument.control(
        "FUNC:PULS:DCYC?",
        "FUNC:PULS:DCYC %f",
        """ Control the pulse duty cycle in percent (float, truncated from 0 to 100).""",
        validator=strict_range,
        values=[0, 100],
        dynamic=True,
    )

    pulse_transition = Instrument.control(
        "FUNC:PULS:TRAN?",
        "FUNC:PULS:TRAN:BOTH %e",
        """ Control the pulse edge time (both rising and falling) in seconds (float).""",
        validator=strict_range,
        values=[8.4e-9, 1e-6],
        dynamic=True,
    )

    output = Instrument.control(
        "OUTP?",
        "OUTP %d",
        """ Control the output state (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0},
        dynamic=True,
    )

    output_load = Instrument.control(
        "OUTP:LOAD?",
        "OUTP:LOAD %s",
        """ Control the expected load resistance in Ohms (str or float). The output impedance
        is always 50 Ohm, this setting can be used to correct the displayed voltage for
        loads unmatched to 50 Ohm.""",
        dynamic=True,
    )

    burst_state = Instrument.control(
        "BURS:STAT?",
        "BURS:STAT %d",
        """ Control the burst mode state (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
        dynamic=True,
    )

    burst_mode = Instrument.control(
        "BURS:MODE?",
        "BURS:MODE %s",
        """ Control the burst mode type (str, strictly 'TRIG<GERED>' or 'GAT<ED>').""",
        validator=strict_discrete_set,
        values=["TRIG", "TRIGGERED", "GAT", "GATED"],
        dynamic=True,
    )

    burst_period = Instrument.control(
        "BURS:INT:PER?",
        "BURS:INT:PER %e",
        """ Control the period of subsequent bursts in seconds (float).""",
        validator=strict_range,
        values=[1e-6, 8000],
        dynamic=True,
    )

    burst_ncycles = Instrument.control(
        "BURS:NCYC?",
        "BURS:NCYC %d",
        """ Control the number of cycles to be output when a burst is triggered (int).""",
        validator=strict_range,
        values=range(1, 100000),
        dynamic=True,
    )

    arb_file = Instrument.control(
        "FUNC:ARB?",
        "FUNC:ARB %s",
        """ Control the arbitrary signal to use from the volatile memory of the device.""",
        dynamic=True,
    )

    arb_advance = Instrument.control(
        "FUNC:ARB:ADV?",
        "FUNC:ARB:ADV %s",
        """ Control how the device advances from data point to data point (str).
        Can be set to 'TRIG<GER>' or 'SRAT<E>' (default).""",
        validator=strict_discrete_set,
        values=["TRIG", "TRIGGER", "SRAT", "SRATE"],
    )

    arb_filter = Instrument.control(
        "FUNC:ARB:FILT?",
        "FUNC:ARB:FILT %s",
        """ Control the filter setting for arbitrary signals (str).
        Can be set to 'NORM<AL>', 'STEP' and 'OFF'.""",
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
        """ Control the sample rate of the currently selected arbitrary signal in Sa/s (float).
        Valid values range from 1 µSa/s to 250 MSa/s (maximum range, device-dependent).""",
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
        """ Control the trigger source (str).""",
        validator=strict_discrete_set,
        values=["IMM", "IMMEDIATE", "EXT", "EXTERNAL", "BUS"],
    )

    ext_trig_out = Instrument.control(
        "OUTP:TRIG?",
        "OUTP:TRIG %d",
        """ Control whether the trigger out signal is active (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )
