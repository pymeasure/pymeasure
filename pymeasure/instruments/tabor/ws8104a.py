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

import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import numpy as np
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from time import time
from pyvisa.errors import VisaIOError

class Channel():
    """ Implementation of a Tabor Electronics WS8104A signal generator channel.
    Implementation modeled on Channel object of Tektronix AFG3152C instrument. """

    BOOLS = {True: 1, False: 0}

    output = Instrument.control(
        "OUTPut?", "OUTPut %d",
        """ A boolean parameter turns the output on or off.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    output_load = Instrument.control(
        "OUTPut:LOAD?", "OUTPut:LOAD %d",
        """ An integer parameter that sets the nominal load so that the output voltage is correct
        at the load. Range is 50 to 1,000,000""",
        validator=strict_range,
        values=[50, 1000000]
    )

    output_filter = Instrument.control(
        "OUTPut:FILTer?", "OUTPut:FILTer %s",
        """ A string parameter that sets the filter on the output channel. Valid values: 
        ["NONE", "25M", "50M", "65M", "120M"]
         From the manual:
        This command will select which filter is connected to the WS8104A-DST output. Observe the following restrictions
when you try to use this command:
1) Filter selection is not available when the instrument is set to output the standard sine waveform. In fact, the
default waveform shape is sine. Therefore, filter selection will be available for use only after you select a
different waveform, or change the output mode to use.
2) Filters are placed before the output amplifier. Therefore, do not expect the filters to remove in-band amplifier
harmonics and spurious.""",
        validator=strict_discrete_set,
        values=['20M', '100M', '200M', 'OFF'],
    )

    frequency = Instrument.control(
        "FREQuency?", "FREQuency %g",
        """ A float parameter that sets the frequency of the standard waveforms. Has no effect
        on arbitrary waveforms. Range is [10e-3,80e6] Hz""",
        validator=strict_range,
        values=[10e-3, 80e6]
    )

    voltage = Instrument.control(
        "VOLTage?", "VOLTage %g",
        """ A float parameter that sets the amplitude of the output waveform. 
         Calibrated for 50 Ohm output impedance. Range is [10e-3,10] Vpp""",
        validator=strict_range,
        values=[10e-3, 10]
    )

    offset = Instrument.control(
        "VOLTage:OFFSet?", "VOLTage:OFFSet %g",
        """ A float parameter that sets the offset of the output waveform. 
         Calibrated for 50 Ohm output impedance. Range is [-4.995,4.995] V""",
        validator=strict_range,
        values=[-4.995, 4.995]
    )

    mode = Instrument.control(
        "FUNCTion:MODE?", "FUNCTion:MODE %s",
        """ A string parameter that sets the output function mode. Options:
        'FIXED: Selects the standard WF's
        'USER': Selects the arbitrary WF's
        'SEQUENCED': Selects sequenced waveform output
        'MODULATED': selects the modulated waveforms
        'COUNTER': selects the counter/timer auxiliary function. This purges ALL channel
        outputs and the signal generator behaves as a counter/timer
        'PULSE': selects the digital pulse generator functions.This purges ALL channel
        outputs and the signal generator behaves as a pulse generator
        'HALFCYCLE': selects the half cycle generator functions.This purges ALL channel
        outputs and the signal generator behaves as a halfcycle generator
         """,
        validator=strict_discrete_set,
        values=['FIXED', 'USER', 'SEQUENCED', 'MODULATED',
                'COUNTER', 'PULSE', 'HALFCYCLE'],
    )

    shape = Instrument.control(
        "FUNCTion:SHAPe?", "FUNCTion:SHAPe %s",
        """ A string parameter that sets the output function mode. Options:
        'SINE: Selects the standard sine waveform
        'TRIANGLE': Selects the standard triangle waveform
        'SQUARE': Selects the square waveform output
        'PULSE': Selects the pulse standard waveform. NOTE: the auxiliary pulse mode may be more suited depending on 
        application. Square may also work if you do not need control over rise times.
        'RAMP': selects the ramp waveform.
        'SINC': selects the sinc waveform
        'EXPONENTIAL': selects the exponential waveform
        'GAUSSIAN': selects the exponential waveform
        'DC': selects the dc waveform
        'NOISE': selects the noise waveform
         """,
        validator=strict_discrete_set,
        values=['SINE', 'TRIANGLE', 'SQUARE', 'PULSE', ' RAMP', 'SINC', 'EXPONENTIAL', 'GAUSSIAN',
                'DC', 'NOISE'],
    )

    sine_phase = Instrument.control(
        "SIN:PHASE?", "SIN:PHASE %g",
        """ A float parameter that specifies the phase of the sine waveform if selected. Units of degrees [0,359.9]""",
        validator=strict_range,
        values=[0, 359.9]
    )

    triangle_phase = Instrument.control(
        "TRI:PHASE?", "TRI:PHASE %g",
        """ A float parameter that specifies the phase of the triangle waveform if selected. Units of degrees [0,359.9]""",
        validator=strict_range,
        values=[0, 359.9]
    )

    square_duty_cycle = Instrument.control(
        "SQUare:DCYCLe?", "SQUare:DCYCLe %g",
        """ A float parameter that sets the square wave duty cycle in units of percent. range = [0, 99.99]""",
        validator=strict_range,
        values=[0, 99.99]
    )

    pulse_delay = Instrument.control(
        "PULSe:DELay?", "PULSe:DELay %g",
        """
        A float parameter that sets the delay of the pulse from the start of the sync transition to go to the pulse high
        level. Range = [0, 99.999] percent""",
        validator=strict_range,
        values=[0, 99.999]
    )

    pulse_width = Instrument.control(
        "PULSe:WIDth?", "PULSe:WIDth %g",
        """A float parameter that sets the width of the pulse in percent. Range = [0, 99.999]""",
        validator=strict_range,
        values=[0, 99.999]
    )

    pulse_transition_rise = Instrument.control(
        "PULSe:TRANsition?", "PULSe:TRANsition %g",
        """ AUXILIARY PULSE FUNCTION: A float parameter that sets the rise time of the pulse in percent. Range = [0, 99.999]""",
        validator=strict_range,
        values=[0, 99.999]
    )

    pulse_transition_fall = Instrument.control(
        "PULSe:TRANsition:TRAiling?", "PULSe:TRANsition:TRAiling %g",
        """ AUXILIARY PULSE FUNCTION: A float parameter that sets the fall time of the pulse in percent. Range = [0, 99.999]""",
        validator=strict_range,
        values=[0, 99.999]
    )

    aux_pulse_delay = Instrument.control(
        "AUXiliary:PULSe:DELay?", "AUXiliary:PULSe:DELay %g",
        """ AUXILIARY PULSE FUNCTION: 
        A float parameter that sets the delay of the pulse from the start of the sync transition to go to the pulse high
        level. Range = [0, 10] seconds""",
        validator=strict_range,
        values=[0, 10]
    )

    aux_pulse_double = Instrument.control(
        "AUXiliary::PULse:DOUBle?", "AUXiliary::PULse:DOUBle %d",
        """ AUXILIARY PULSE FUNCTION: A boolean parameter turns the double pulse on or off""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    aux_pulse_double_delay = Instrument.control(
        "AUXiliary:PULSe:DOUBle:DELay?", "AUXiliary:PULSe:DOUBle:DELay %g",
        """ AUXILIARY PULSE FUNCTION: 
        A float parameter that sets the delay between the two pulse in double pulse mode. Range = [0, 1000] seconds""",
        validator=strict_range,
        values=[0, 1000]
    )

    aux_pulse_hightime = Instrument.control(
        "AUXiliary:PULSe:HIGH?", "AUXiliary:PULSe:HIGH %g",
        """ AUXILIARY PULSE FUNCTION: 
        A float parameter that sets then length of high time of the pulse (does NOT include rise/fall times)
         Range = [0, 1000] seconds""",
        validator=strict_range,
        values=[0, 1000]
    )

    aux_pulse_highlevel = Instrument.control(
        "AUXiliary:PULSe:LEVel:HIGH?", "AUXiliary:PULSe:LEVel:HIGH %g",
        """ AUXILIARY PULSE FUNCTION: 
        A float parameter that sets the pulse high level.
         Range = [-4.990,5] V""",
        validator=strict_range,
        values=[-4.990, 5]
    )

    aux_pulse_lowlevel = Instrument.control(
        "AUXiliary:PULSe:LEVel:LOW?", "AUXiliary:PULSe:LEVel:LOW %g",
        """ AUXILIARY PULSE FUNCTION: 
        A float parameter that sets the pulse low level.
         Range = [-4.990,5] V""",
        validator=strict_range,
        values=[-5, 4.990]
    )


    ramp_delay = Instrument.control(
        "RAMP:DELay?", "RAMP:DELay %g",
        """ A float parameter that sets the delay of the ramp in percent. Range = [0, 99.99]""",
        validator=strict_range,
        values=[0, 99.999]
    )

    ramp_transition_rise = Instrument.control(
        "RAMP:TRANsition?", "RAMP:TRANsition %g",
        """ A float parameter that sets the rise time of the ramp in percent. Range = [0, 99.99]""",
        validator=strict_range,
        values=[0, 99.99]
    )

    ramp_transition_fall = Instrument.control(
        "RAMP:TRANsition:TRAiling?", "RAMP:TRANsition:TRAiling %g",
        """ A float parameter that sets the fall time of the ramp in percent. Range = [0, 99.99]""",
        validator=strict_range,
        values=[0, 99.99]
    )

    ramp_transition_fall = Instrument.control(
        "RAMP:TRANsition:TRAiling?", "RAMP:TRANsition:TRAiling %g",
        """ A float parameter that sets the fall time of the ramp in percent. Range = [0, 99.99]""",
        validator=strict_range,
        values=[0, 99.99]
    )

    ramp_transition_fall = Instrument.control(
        "RAMP:TRANsition:TRAiling?", "RAMP:TRANsition:TRAiling %g",
        """ A float parameter that sets the fall time of the ramp in percent. Range = [0, 99.99]""",
        validator=strict_range,
        values=[0, 99.99]
    )

    arb_trace_select = Instrument.control(
        "TRACe:SELect?", "TRACe:SELect %g",
        """ An integer parameter that sets the arbitrary waveform segment for a given channel. Range = [0, 10000]""",
        validator=strict_range,
        values=[1,10000]
    )

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number

    def values(self, command, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        self.instrument.write(f'Instrument {self.number}')
        return self.instrument.values(command, **kwargs)

    def ask(self, command):
        self.instrument.write(f'Instrument {self.number}')
        self.instrument.ask(command)

    def write(self, command):
        self.instrument.write(f'Instrument {self.number}')
        self.instrument.write(command)


class WS8104A(Instrument):
    """ Represents the Tabor electronics WS8104A signal generator interface for interacting
    with the instrument.
    .. code-block:: python

        awg = WS8104A(resource)
        awg.ch1.shape = 'SQUARE'
    """

    BOOLS = {True: 1, False: 0}

    def __init__(self, adapter, **kwargs):
        super(WS8104A, self).__init__(
            adapter, "Rigol MSO5354 Oscilloscope", **kwargs
        )
        # Account for setup time for timebase_mode, waveform_points_mode
        self.adapter.connection.timeout = 6000
        self.ch1 = Channel(self, 1)
        self.ch2 = Channel(self, 2)
        self.ch3 = Channel(self, 3)
        self.ch4 = Channel(self, 4)

    ##################
    # Timebase Setup #
    ##################

    continuous = Instrument.control(
        "INITiate:CONTinuous?", "INITiate:CONTinuous %s",
        """ A boolean parameter that disables any interrupted modes and forces continuous run mode.""",
        validator=strict_discrete_set,
        values={True: 'ON', False: 'OFF'},
        map_values=True
    )

    burst = Instrument.control(
        "TRIGger:BURSt?", "TRIGger:BURSt %s",
        """ A boolean parameter that toggles the counted burst run mode on and off. self.continuous must be set to
        False for this command to take effect.""",
        validator=strict_discrete_set,
        values={True: 'ON', False: 'OFF'},
        map_values=True
    )

    burst_ncycles = Instrument.control(
        "TRIGger:BURSt:COUNt?", "TRIGger:BURSt:COUNt %d",
        """ Sets the number of cycles when burst mode is on. Range is 1-1,000,000.""",
        validator=strict_range,
        values=[1, 1000000],
    )

    trigger_source = Instrument.control(
        "TRIGger:SOURce:ADVance?", "TRIGger:SOURce:ADVance %s",
        """ "EXT": activates rear panel TRIG IN and the MAN TRIG button as legal sources for trigger
            'BUS': Triggered only by the communication bus (e.g. GPIB, LAN, USB)
            'MIXED': First cycle must be triggered by software bus then TRIG IN and MAN TRIG are allowed""",
        validator=strict_discrete_set,
        values=['EXT', 'BUS', 'MIXED'],
    )

    sample_clock = Instrument.control(
        ":FREQ:RAST?", ":FREQ:RAST %g",
        """ """,
        validator=strict_range,
        values=[1.5, 200e6],
    )

    #TODO implement the rest of the trigger commands

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
                    "Timeout expired while waiting for the WAS8104A" +
                    " to finish the triggering."
                )

            if should_stop:
                return

    ################
    # System Setup #
    ################

    def clear_status(self):
        """ Clear device status. """
        self.write("*CLS")

    def factory_reset(self):
        """ Factory default setup, no user settings remain unchanged. """
        self.write("*RST")

