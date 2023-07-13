#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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
from pymeasure.instruments.validators import strict_range, strict_discrete_set, joined_validators
from time import time, sleep
import numpy as np
from pyvisa.errors import VisaIOError

# Capitalize string arguments to allow for better conformity with other WFG's
def capitalize_string(string: str, *args, **kwargs):
    return string.upper()

string_validator = joined_validators(capitalize_string, strict_discrete_set)

class Channel():
    """ Implementation of a BN A2255 channel
     """
    BOOLS = {True:1 , False:0}
    shape_vals = ["SINUSOID", "SIN", "SQUARE", "SQU", "RAMP",
                 "PULSE", "PULS", "NOISE", "NOIS", "DC", "EMEM"]
    for val in range(32):
        shape_vals.append(f'USER{val}')

    shape = Instrument.control(
        'FUNC:SHAP?', 'FUNC:SHAP %s',
        """This sets the function shape. SIN, SQU, PULS, RAMP are most commonly used.""",
        validator=string_validator,
        values=shape_vals,
    )

    output_impedance = Instrument.control( # this one is output rather than source for some reason???
        'IMP?', 'IMP %s',
        """This command sets the output load impedance for the specified channel.
        Can be set in [1,1e4] ohm. Default is 50 ohms.
        Also accepts MAX, MIN, or INF (9.9E+37)."""
    )

    period = Instrument.control(
        "PERiod?", "PERiod %.4E",
        """ A floating point property that controls the period of the output1
        waveform function in seconds, ranging from 3e-5 s to 8 s. Can be set
        and overwrites the frequency for *all* waveforms. If the period is
        shorter than the pulse width + the edge time, the edge time and pulse
        width will be adjusted accordingly. """,
        validator=strict_range,
        values=[1.25e-9, 8],
    )

    frequency = Instrument.control(
        "FREQ?", "FREQ %g",
        """ A floating point property that controls the frequency of the output1
        waveform function in Hz, ranging from 0.125 Hz to 1.25e8 Hz. Can be set
        and overwrites the frequency for *all* waveforms. If the period is
        shorter than the pulse width + the edge time, the edge time and pulse
        width will be adjusted accordingly. """,
        validator=strict_range,
        values=[.125, 1.25e8],
    )

    burst_state = Instrument.control(
        "BURS:STAT?", "BURS:STAT %s",
        """Sets the state of burst mode to either ON or OFF.""",
        validator=strict_discrete_set,
        values=['ON','OFF']
    )

    burst_ncycles = Instrument.control(
        "BURS:NCYC?", "BURS:NCYC %d",
        """ An integer property that sets the number of cycles to be output
        when a burst is triggered. Valid values are 1 to 500,000. Also accepts
        MIN, MAX, INF (9.9E+37)""",
        validator=strict_range,
        values=[1, 500000],
    )

    ramp_symmetry = Instrument.control(
        "FUNC:RAMP:SYMM?", "FUNC:RAMP:SYMM %d",
        """The symmetry of the ramp waveform. Takes an int 0 to 100. 50 is default.
        Also will accept MIN, MAX.""",
        validator=strict_range,
        values=[0,100]
    )

    init_delay = Instrument.control(
        "INITDELay?", "INITDELay %g",
        """ This parameter is the group delay from the Trigger IN signal that all
         the pulses associated to the output N have in common.""",
        validator=strict_range,
        values=[0, 1e6],
    )

    invert = Instrument.control(
        "INV?", "INV %s",
        """ A boolean property that sets inversion on ('ON') or off ('OFF') 
        the output 1 of the function generator. Can be set. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    amplitude = Instrument.control(
        "VOLT:LEV:IMM:AMPL?", "VOLT:LEV:IMM:AMPL %g",
        """ This control reads and sets the amplitude of the source 1 output. 
        Range is 0.01-5 V""",
        validator=strict_range,
        values=[0, 10],
    )

    offset = Instrument.control(
        "VOLT:LEV:IMM:OFFS?", "VOLT:LEV:IMM:OFFS %g",
        """ This control reads and sets the DC offset of the source 1 output. 
        Range is -2.5 - +2.5 V""",
        validator=strict_range,
        values=[-5, 5],
    )

    trigger_source = Instrument.control(
        "BURS:SOUR?", "BURS:SOUR %s",
        """ A string parameter to set the whether the trigger is TIMer, EXTernal (BNC),
         or MANual (front panel or software) """,
        validator=strict_discrete_set,
        values=['TIM', 'EXT', 'MAN']
    )

    burst_mode = Instrument.control(
        "BURS:MODE?", "BURS:MODE %s",
        """ A string parameter to set the burst mode to either TRIG or GAT """,
        validator=strict_discrete_set,
        values=['TRIG', 'GAT']
    )

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number

    def values(self, command, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values("SOURce%d:%s" % (
            self.number, command), **kwargs)

    def ask(self, command):
        if "IMP" in command:
            self.instrument.ask("OUTPut%d:%s" % (self.number, command))
        else:
            self.instrument.ask("SOURce%d:%s" % (self.number, command))

    def write(self, command):
        if "IMP" in command:
            self.instrument.write("OUTPut%d:%s" % (self.number, command))
        else:
            self.instrument.write("SOURce%d:%s" % (self.number, command))

    @property
    def output_enabled(self):
        mapper = {1: True, 0: False}
        out = int(self.instrument.ask("output%d?" % self.number))
        return mapper[out]

    @output_enabled.setter
    def output_enabled(self, state):
        mapper = {True: 'ON', False: 'OFF'}
        self.instrument.write("output%d %s" % (self.number, mapper[state]))

    @property
    def output(self):
        mapper = {1: True, 0: False}
        out = int(self.instrument.ask("output%d?" % self.number))
        return mapper[out]

    @output.setter
    def output(self, state):
        mapper = {True: 'ON', False: 'OFF'}
        self.instrument.write("output%d %s" % (self.number, mapper[state]))

class BN_A2255(Instrument):
    """Represents the Berkeley Nucleonics A2255 Arbitrary Waveform Generator."""

    burst_state = Instrument.control(
        "BURS:STAT?", "BURS:STAT %s",
        """Sets the state of burst mode to either ON or OFF.""",
        validator=strict_discrete_set,
        values=['ON', 'OFF']
    )

    burst_n_cycles = Instrument.control(
        "BURS:NCYC?", "BURS:NCYC %d",
        """ Integer parameter setting the number of cycles to burst in burst mode.
        Can be set from 1 to 500,000, or MIN, MAX, INF (9.9E+37)""",
        validator=strict_range,
        values=[1,500000]
    )

    num_channels = 2
    '''
    run_mode = Instrument.control(
        "AWGControl:RMODe?", "AWGControl:RMODe %s",
        """ A string parameter controlling the AWG run mode. Can be:
        CONT: output continously outputs WF
        BURST: burst n after trigger
        TCON: go into continous mode after trigger
        STEP: each trigger event causes the next wf in sequencer to fire
        ADVA: allows conditional hops around sequencer table""",
        validator=strict_discrete_set,
        values=['CONT', 'BURST', 'TCON', 'STEP', 'ADVA'],
    )
    '''
    run_state = Instrument.measurement(
        "AWGC:RSTAT?", """Queries the run state: 0 is stopped
        1 is waiting for trigger, 2 is running"""
    )

    sampling_frequency = Instrument.control(
        "AWGC:SRAT?", "AWGC:SRAT %e",
        """ A floating point property that controls AWG sampling frequency.
        This property can be set.""",
        validator=strict_range,
        values=[10e6, 1.2e9]
    )

    trigger_source = Instrument.control(
        "TRIGger:SEQUENCE:SOURce?", "TRIGger:SEQUENCE:SOURce %s",
        """ A string parameter to set the whether the trigger is TIMer, EXTernal (BNC),
         or MANual (front panel or software) """,
        validator=strict_discrete_set,
        values=['TIM', 'EXT', 'MAN']
    )


    trigger_slope = Instrument.control(
        "TRIGger:SEQUENCE:SLOPe?", "TRIGger:SEQUENCE:SLOPe %s",
        """ A string parameter to set the whether the trigger edge is POSitive or NEGative, or BOTH""",
        validator=strict_discrete_set,
        values={'POS': 'POS', 'NEG': 'NEG', 'BOTH': 'BOTH'},
        map_values=True
    )

    trigger_level = Instrument.control(
        "TRIGger:SEQUENCE:LEVel?", "TRIGger:SEQUENCE:LEVel %g",
        """ A float parameter that sets the trigger input level threshold. Unclear what the range is,
        0.2 V - 1.4 V is a valid range""",
    )

    trigger_impedance = Instrument.control(
        "TRIGger:SEQUENCE:IMPedance?", "TRIGger:SEQUENCE:IMPedance %s",
        """ An integer parameter to set the trigger input impedance to either 50 or 1000 Ohms""",
        validator=strict_discrete_set,
        values={50: '50 Ohm',1000:'1 KOhm'},
        map_values=True
    )

    sequence_len = Instrument.control(
        "SEQ:LENG?", "SEQ:LENG %d",
        """ Integer atrribute to control the length of the sequence table for all channels""",
    )



    @property
    def waveform_list(self):
        return self.ask('WLIST:LIST?')



    def __init__(self, adapter, **kwargs):
        super(BN_A2255, self).__init__(
            adapter,
            "BN A2255 Arbitrary Waveform Generator",
            **kwargs
        )
        self.default_dir = 'C:\\Users\\BN_A2255\\Pictures\\Saved Pictures\\'
        num_chan = int(self.num_channels)
        self.mapper = {}
        for i in range(num_chan):
            setattr(self, f'ch{i+1}', Channel(self, number=i+1))
            self.mapper[i + 1] = getattr(self,f'ch{i+1}')

    def beep(self):
        self.write("system:beep")

    def all_off(self):
        for key, item in self.mapper.items():
            item.output = False

    def set_voltage_format(self, format):
        """
        Sets the way voltages are specified:
        'AMPL': specify voltages as amplitude + offset
        'HIGH': specify voltages as vlow and vhigh #TODO implement these on Channel
        """
        if format not in ['AMPL', 'HIGH']:
            raise ValueError(f'{format} not allowed. Specify AMPL or HIGH')
        self.write('DISP:UNIT:VOLT ' + format)


    def trigger(self):
        """ Send a trigger signal to the function generator. """
        self.write("*TRG")

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

            if should_stop():
                return



    def opc(self):
        return int(self.ask("*OPC?"))


    def start_awg(self, timeout=15000):
        """Starts the AWG to run. This may take some time, so we temporarily
         shift the timeout to be more conservative"""
        old_timeout = self.adapter.connection.timeout
        self.adapter.connection.timeout = timeout
        self.write('STAT ON')
        self.adapter.connection.timeout = old_timeout


    def stop_awg(self):
        self.write('STAT OFF')

    def transfer(self, array, normalized_input=False, wfnumber=None):
        """
        Takes an array and saves it to the Edit Memory (EMEM) of the A2255, then loads it.
        If normalized_input is True, the array is scaled to go from 0 to 2**13 (13 bit DAC).
        """
        array = np.array(array)
        if normalized_input:
            array = (array+1) * 2**13
        array = np.array(array, dtype=int)
        self.adapter.write_binary_values("DATA:DATA EMEM,", array, datatype='H', is_big_endian=True)
        if wfnumber is not None:
            sleep(1)
            if not isinstance(wfnumber, int):
                raise TypeError(f'{type(wfnumber)} not allowed, must be an int')
            else:
                self.write(f"DATA:COPY USER{wfnumber},EMEM")

