#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set,\
    strict_range
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


class Agilent33500(Instrument):
    """Represents the Agilent 33500 Function/Arbitrary Waveform Generator family.
    Individual devices are represented by subclasses.

    .. code-block:: python

        generator = Agilent33500("GPIB::1")

        generator.shape = 'SIN'                 # Sets the output signal shape to sine
        generator.frequency = 1e3               # Sets the output frequency to 1 kHz
        generator.amplitude = 5                 # Sets the output amplitude to 5 Vpp
        generator.output = 'on'                 # Enables the output

        generator.shape = 'ARB'                 # Set shape to arbitrary
        generator.arb_srate = 1e6               # Set sample rate to 1MSa/s

        generator.data_volatile_clear()         # Clear volatile internal memory
        generator.data_arb(                     # Send data points of arbitrary waveform
            'test',
            range(-10000, 10000, +20),          # In this case a simple ramp
            data_format='DAC'                   # Data format is set to 'DAC'
        )
        generator.arb_file = 'test'             # Select the transmitted waveform 'test'

    """

    id = Instrument.measurement(
        "*IDN?", """ Reads the instrument identification """
    )

    def __init__(self, adapter, **kwargs):
        super(Agilent33500, self).__init__(
            adapter,
            "Agilent 33500 Function/Arbitrary Waveform generator family",
            **kwargs
        )

    def beep(self):
        """ Causes a system beep. """
        self.write("SYST:BEEP")

    shape = Instrument.control(
        "FUNC?", "FUNC %s",
        """ A string property that controls the output waveform. Can be set to:
        SIN<USOID>, SQU<ARE>, TRI<ANGLE>, RAMP, PULS<E>, PRBS,  NOIS<E>, ARB, DC. """,
        validator=strict_discrete_set,
        values=["SIN", "SQU", "TRI", "RAMP", "PULS", "PRBS", "NOIS", "ARB", "DC"],
    )

    frequency = Instrument.control(
        "FREQ?", "FREQ %f",
        """ A floating point property that controls the frequency of the output
        waveform in Hz, from 1 uHz to 120 MHz (maximum range, can be lower depending
        on your device), depending on the specified function. Can be set. """,
        validator=strict_range,
        values=[1e-6, 120e+6],
    )

    amplitude = Instrument.control(
        "VOLT?", "VOLT %f",
        """ A floating point property that controls the voltage amplitude of the
        output waveform in V, from 10e-3 V to 10 V. Depends on the output
        impedance. Can be set. """,
        validator=strict_range,
        values=[10e-3, 10],
    )

    amplitude_unit = Instrument.control(
        "VOLT:UNIT?", "VOLT:UNIT %s",
        """ A string property that controls the units of the amplitude. Valid
        values are VPP (default), VRMS, and DBM. Can be set. """,
        validator=strict_discrete_set,
        values=["VPP", "VRMS", "DBM"],
    )

    offset = Instrument.control(
        "VOLT:OFFS?", "VOLT:OFFS %f",
        """ A floating point property that controls the voltage offset of the
        output waveform in V, from 0 V to 4.995 V, depending on the set
        voltage amplitude (maximum offset = (Vmax - voltage) / 2). Can be set.
        """,
        validator=strict_range,
        values=[-4.995, +4.995],
    )

    voltage_high = Instrument.control(
        "VOLT:HIGH?", "VOLT:HIGH %f",
        """ A floating point property that controls the upper voltage of the
        output waveform in V, from -4.990 V to 5 V (must be higher than low
        voltage by at least 1 mV). Can be set. """,
        validator=strict_range,
        values=[-4.99, 5],
    )

    voltage_low = Instrument.control(
        "VOLT:LOW?", "VOLT:LOW %f",
        """ A floating point property that controls the lower voltage of the
        output waveform in V, from -5 V to 4.990 V (must be lower than high
        voltage by at least 1 mV). Can be set. """,
        validator=strict_range,
        values=[-5, 4.99],
    )

    square_dutycycle = Instrument.control(
        "FUNC:SQU:DCYC?", "FUNC:SQU:DCYC %f",
        """ A floating point property that controls the duty cycle of a square
        waveform function in percent, from 0.01% to 99.98%.
        The duty cycle is limited by the frequency and the minimal pulse width of
        16 ns. See manual for more details. Can be set. """,
        validator=strict_range,
        values=[0.01, 99.98],
    )

    ramp_symmetry = Instrument.control(
        "FUNC:RAMP:SYMM?", "FUNC:RAMP:SYMM %f",
        """ A floating point property that controls the symmetry percentage
        for the ramp waveform, from 0.0% to 100.0% Can be set. """,
        validator=strict_range,
        values=[0, 100],
    )

    pulse_period = Instrument.control(
        "FUNC:PULS:PER?", "FUNC:PULS:PER %e",
        """ A floating point property that controls the period of a pulse
        waveform function in seconds, ranging from 33 ns to 1e6 s. Can be set
        and overwrites the frequency for *all* waveforms. If the period is
        shorter than the pulse width + the edge time, the edge time and pulse
        width will be adjusted accordingly. """,
        validator=strict_range,
        values=[33e-9, 1e6],
    )

    pulse_hold = Instrument.control(
        "FUNC:PULS:HOLD?", "FUNC:PULS:HOLD %s",
        """ A string property that controls if either the pulse width or the
        duty cycle is retained when changing the period or frequency of the
        waveform. Can be set to: WIDT<H> or DCYC<LE>. """,
        validator=strict_discrete_set,
        values=["WIDT", "WIDTH", "DCYC", "DCYCLE"],
    )

    pulse_width = Instrument.control(
        "FUNC:PULS:WIDT?", "FUNC:PULS:WIDT %e",
        """ A floating point property that controls the width of a pulse
        waveform function in seconds, ranging from 16 ns to 1e6 s, within a
        set of restrictions depending on the period. Can be set. """,
        validator=strict_range,
        values=[16e-9, 1e6],
    )

    pulse_dutycycle = Instrument.control(
        "FUNC:PULS:DCYC?", "FUNC:PULS:DCYC %f",
        """ A floating point property that controls the duty cycle of a pulse
        waveform function in percent, from 0% to 100%. Can be set. """,
        validator=strict_range,
        values=[0, 100],
    )

    pulse_transition = Instrument.control(
        "FUNC:PULS:TRAN?", "FUNC:PULS:TRAN:BOTH %e",
        """ A floating point property that controls the edge time in
        seconds for both the rising and falling edges. It is defined as the
        time between the 10% and 90% thresholds of the edge.
        Valid values are between 8.4 ns to 1 µs. Can be set. """,
        validator=strict_range,
        values=[8.4e-9, 1e-6],
    )

    output = Instrument.control(
        "OUTP?", "OUTP %d",
        """ A boolean property that turns on (True, 'on') or off (False, 'off') 
        the output of the function generator. Can be set. """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, 'on': 1, 'ON': 1, False: 0, 'off': 0, 'OFF': 0},
    )

    output_load = Instrument.control(
        "OUTP:LOAD?", "OUTP:LOAD %s",
        """ Sets the expected load resistance (should be the load impedance connected
        to the output. The output impedance is always 50 Ohm, this setting can be used
        to correct the displayed voltage for loads unmatched to 50 Ohm.
        Valid values are between 1 and 10 kOhm or INF for high impedance.
        No validator is used since both numeric and string inputs are accepted,
        thus a value outside the range will not return an error.
        Can be set. """,
    )

    burst_state = Instrument.control(
        "BURS:STAT?", "BURS:STAT %d",
        """ A boolean property that controls whether the burst mode is on
        (True) or off (False). Can be set. """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    burst_mode = Instrument.control(
        "BURS:MODE?", "BURS:MODE %s",
        """ A string property that controls the burst mode. Valid values
        are: TRIG<GERED>, GAT<ED>. This setting can be set. """,
        validator=strict_discrete_set,
        values=["TRIG", "TRIGGERED", "GAT", "GATED"],
    )

    burst_period = Instrument.control(
        "BURS:INT:PER?", "BURS:INT:PER %e",
        """ A floating point property that controls the period of subsequent bursts.
        Has to follow the equation burst_period > (burst_ncycles / frequency) + 1 µs.
        Valid values are 1 µs to 8000 s. Can be set. """,
        validator=strict_range,
        values=[1e-6, 8000],
    )

    burst_ncycles = Instrument.control(
        "BURS:NCYC?", "BURS:NCYC %d",
        """ An integer property that sets the number of cycles to be output
        when a burst is triggered. Valid values are 1 to 100000. This can be
        set. """,
        validator=strict_range,
        values=range(1, 100000),
    )

    arb_file = Instrument.control(
        "FUNC:ARB?", "FUNC:ARB %s",
        """ A string property that selects the arbitrary signal from the volatile
        memory of the device. String has to match an existing arb signal in volatile
        memore (set by data_arb()). Can be set. """
    )

    arb_advance = Instrument.control(
        "FUNC:ARB:ADV?", "FUNC:ARB:ADV %s",
        """ A string property that selects how the device advances from data point
        to data point. Can be set to 'TRIG<GER>' or 'SRAT<E>' (default). """,
        validator=strict_discrete_set,
        values=["TRIG", "TRIGGER", "SRAT", "SRATE"],
    )

    arb_filter = Instrument.control(
        "FUNC:ARB:FILT?", "FUNC:ARB:FILT %s",
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
    #     this property. Can be set. """,
    #     validator=strict_range,
    #     values=[33e-9, 1e6],
    # )
    #
    # arb_frequency = Instrument.control(
    #     "FUNC:ARB:FREQ?", "FUNC:ARB:FREQ %f",
    #     """ A floating point property that controls the frequency of the arbitrary signal.
    #     Limited by number of signal points. Check for instrument
    #     errors when setting this property. Can be set. """,
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
        "FUNC:ARB:SRAT?", "FUNC:ARB:SRAT %f",
        """ An floating point property that sets the sample rate of the currently selected 
        arbitrary signal. Valid values are 1 µSa/s to 250 MSa/s (maximum range, can be lower
        depending on your device). This can be set. """,
        validator=strict_range,
        values=[1e-6, 250e6],
    )

    def data_volatile_clear(self):
        """
        Clear all arbitrary signals from the volatile memory. This should be done if the same name
        is used continuously to load different arbitrary signals into the memory, since an error
        will occur if a trace is loaded which already exists in the memory.
        """
        self.write("DATA:VOL:CLE")

    def data_arb(self, arb_name, data_points, data_format='DAC'):
        """
        Uploads an arbitrary trace into the volatile memory of the device. The data_points can be given
        as comma separated 16 bit DAC values (ranging from -32767 to +32767), as comma separated floating
        point values (ranging from -1.0 to +1.0) or as a binary data stream. Check the manual for more
        information. The storage depends on the device type and ranges from 8 Sa to 16 MSa (maximum).
        TODO: *Binary is not yet implemented*

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
        if data_format == 'DAC':
            separator = ', '
            data_points_str = [str(item) for item in data_points]  # Turn list entries into strings
            data_string = separator.join(data_points_str)  # Join strings with separator
            print("DATA:ARB:DAC {}, {}".format(arb_name, data_string))
            self.write("DATA:ARB:DAC {}, {}".format(arb_name, data_string))
            return
        elif data_format == 'float':
            separator = ', '
            data_points_str = [str(item) for item in data_points]  # Turn list entries into strings
            data_string = separator.join(data_points_str)  # Join strings with separator
            print("DATA:ARB {}, {}".format(arb_name, data_string))
            self.write("DATA:ARB {}, {}".format(arb_name, data_string))
            return
        elif data_format == 'binary':
            raise NotImplementedError('The binary format has not yet been implemented. Use "DAC" or "float" instead.')
        else:
            raise ValueError('Undefined format keyword was used. Valid entries are "DAC", "float" and "binary"')

    display = Instrument.setting(
        "DISP:TEXT '%s'",
        """ A string property which is displayed on the front panel of
        the device. Can be set. """,
    )

    def clear_display(self):
        """ Removes a text message from the display. """
        self.write("DISP:TEXT:CLE")

    def trigger(self):
        """ Send a trigger signal to the function generator. """
        self.write("*TRG;*WAI")

    def wait_for_trigger(self, timeout=3600, should_stop=lambda: False):
        """ Wait until the triggering has finished or timeout is reached.

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
                    "Timeout expired while waiting for the Agilent 33220A" +
                    " to finish the triggering."
                )

            if should_stop:
                return

    trigger_source = Instrument.control(
        "TRIG:SOUR?", "TRIG:SOUR %s",
        """ A string property that controls the trigger source. Valid values
        are: IMM<EDIATE> (internal), EXT<ERNAL> (rear input), BUS (via trigger
        command). This setting can be set. """,
        validator=strict_discrete_set,
        values=["IMM", "IMMEDIATE", "EXT", "EXTERNAL", "BUS"],
    )

    ext_trig_out = Instrument.control(
        "OUTP:TRIG?", "OUTP:TRIG %d",
        """ A boolean property that controls whether the trigger out signal is
        active (True) or not (False). This signal is output from the Ext Trig
        connector on the rear panel in Burst and Wobbel mode. Can be set. """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    def check_errors(self):
        """ Read all errors from the instrument. """

        errors = []
        while True:
            err = self.values("SYST:ERR?")
            if int(err[0]) != 0:
                errmsg = "Agilent 33521A: %s: %s" % (err[0], err[1])
                log.error(errmsg + '\n')
                errors.append(errmsg)
            else:
                break

        return errors
