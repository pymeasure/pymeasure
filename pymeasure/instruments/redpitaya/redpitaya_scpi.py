#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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


import datetime
import logging

import numpy as np

from pymeasure.instruments import Channel, Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range, truncated_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DigitalChannelP(Channel):
    """ A digital line of the P type"""

    direction_in = Channel.control(
        "DIG:PIN:DIR? DIO{ch}_P", "DIG:PIN:DIR %s,DIO{ch}_P",
        """ Control a digital line to the given direction (True for 'IN' or False for 'OUT')""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'IN', False: 'OUT'},
        cast=str,
    )

    enabled = Channel.control(
        "DIG:PIN? DIO{ch}_P", "DIG:PIN DIO{ch}_P,%d",
        """ Control the enabled state of the line (bool)""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )


class DigitalChannelN(Channel):
    """ A digital line of the N type"""

    direction_in = Channel.control(
        "DIG:PIN:DIR? DIO{ch}_N", "DIG:PIN:DIR %s,DIO{ch}_N",
        """ Control a digital line to the given direction (True for 'IN' or False for 'OUT')""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'IN', False: 'OUT'},
        cast=str,
    )

    enabled = Channel.control(
        "DIG:PIN? DIO{ch}_N", "DIG:PIN DIO{ch}_N,%d",
        """ Control the enabled state of the line (bool)""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )


class DigitalChannelLed(Channel):
    """ A LED digital line (Output only)"""

    enabled = Channel.control(
        "DIG:PIN? LED{ch}", "DIG:PIN LED{ch},%d",
        """ Control the enabled state of the led (bool)""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )


class AnalogInputSlowChannel(Channel):
    """ A slow analog input channel"""

    voltage = Channel.measurement(
        "ANALOG:PIN? AIN{ch}",
        """ Measure the voltage on the corresponding analog input channel, range is [0, 3.3]V""",
    )


class AnalogOutputSlowChannel(Channel):
    """ A slow analog output channel"""

    voltage = Channel.setting(
        "ANALOG:PIN AOUT{ch}, %f",
        """ Set the voltage on the corresponding analog input channel, range is [0, 1.8]V""",
        validator=truncated_range,
        values=[0, 1.8],
    )


class AnalogInputFastChannel(Channel):

    gain = Instrument.control(
        "ACQ:SOUR{ch}:GAIN?", "ACQ:SOUR{ch}:GAIN %s",
        """Control the gain of the selected fast analog input either 'LV' or 'HV'
        (see jumpers on boards)

        'LV' set the returned values in the range [-1, 1]V and 'HV' in the range [-20, 20]V
        """,
        validator=strict_discrete_set,
        values=['LV', 'HV'],
        cast=str,
    )

    def get_data_from(self, start: int, npts: int) -> np.ndarray:
        self.write(f"ACQ:SOUR{'{ch}'}:DATA:STArt:N? {start:.0f}, {npts:.0f}")
        return self._read_from_ascii()

    def get_data(self, npts: int | None = None, format='ASCII') -> np.ndarray:
        """ Read data from the buffer

        :param npts: number of points to be read
        :param format: either 'ASCII' or 'BIN', see :meth:acq_format
        """
        if npts is not None:
            self.write(f"ACQ:SOUR{'{ch}'}:DATA:Old:N? {npts:.0f}")
        else:
            self.write("ACQ:SOUR{ch}:DATA?")

        if format == 'ASCII':
            data = self._read_from_ascii()
        else:
            data = self._read_from_binary()
        return data

    def _read_from_ascii(self) -> np.ndarray:
        """ Read data from the buffer from ascii format, see :meth:acq_format
        """
        data_str = self.read()
        return np.fromstring(data_str.strip('{}').encode(), sep=',')

    def _read_from_binary(self) -> np.ndarray:
        """ Read data from the buffer from binary format, see :meth:acq_format
        """
        self.read_bytes(1)
        nint = int(self.read_bytes(1).decode())
        length = int(self.read_bytes(nint).decode())
        data = np.frombuffer(self.read_bytes(length), dtype=int)
        self.read_bytes(2)
        if self.gain == 'LV':
            max_range = 2 * RedPitayaScpi.LV_MAX
        else:
            max_range = 2 * RedPitayaScpi.HV_MAX

        return max_range * data / (2**16 - 1) - max_range / 2


class AnalogOutputFastChannel(Channel):
    """A fast analog output"""

    SHAPES = ("SINE", "SQUARE", "TRIANGLE", "SAWU", "SAWD", "PWM", "ARBITRARY", "DC", "DC_NEG")
    shape = Instrument.control(
        "SOUR{ch}:FUNC?",
        "SOUR{ch}:FUNC %s",
        """Control the output waveform (str). Can be set to:
        SINE, SQUARE, TRIANGLE, SAWU, SAWD, PWM, ARBITRARY, DC, DC_NEG. """,
        validator=strict_discrete_set,
        values=SHAPES,
    )

    FREQUENCIES = [1e-6, 50e6] #in Hz
    frequency = Instrument.control(
        "SOUR{ch}:FREQ:FIX?",
        "SOUR{ch}:FREQ:FIX %f",
        """ Control the frequency of the output
        waveform in Hz, from 1 uHz to 50 MHz.
        For the ARBITRARY waveform, this is the frequency of one signal period
        (a buffer of 16384 samples).""",
        validator=strict_range,
        values= FREQUENCIES,
    )

    AMPLITUDES = [0, +1] #in V
    amplitude = Instrument.control(
        "SOUR{ch}:VOLT?",
        "SOUR{ch}:VOLT %f",
        """ Control the voltage amplitude of the
        output waveform in V, from 0 V to 1 V.""",
        validator=strict_range,
        values= AMPLITUDES,
    )

    OFFSETS = [-0.995, +0.995] #in V
    offset = Instrument.control(
        "SOUR{ch}:VOLT:OFFS?",
        "SOUR{ch}:VOLT:OFFS %f",
        """ Control the voltage offset of the
        output waveform in V, from -1 V to 1 V, depending on the set
        voltage amplitude (maximum offset = (Vmax - amplitude) / 2).
        """,
        validator=strict_range,
        values= OFFSETS,
    )

    PHASES = (-360, 360) #in degrees
    phase = Instrument.control(
        "SOUR{ch}:PHAS?",
        "SOUR{ch}:PHAS %f",
        """ Control the phase of the output
        waveform in degrees, from -360 degrees to 360 degrees.
        Not available for arbitrary waveforms.""",
        validator=strict_range,
        values= PHASES,
    )

    CYCLES = (0, 1)
    dutycycle = Instrument.control(
        "SOUR{ch}:DCYC?",
        "SOUR{ch}:DCYC %f",
        """Control the duty cycle of a PWM
        waveform function as a fraction - 1 = 100% (float strictly between 0 and 1).""",
        validator=strict_range,
        values= CYCLES,
    )


    # Generation Trigger

    GEN_TRIGGER_SOURCES = ("EXT_PE", "EXT_NE", "INT", "GATED")
    gen_trigger_source = Instrument.control(
        "SOUR{ch}:TRig:SOUR?",
        "SOUR{ch}:TRig:SOUR %s",
        """ Control the generator output trigger source (str), one of
        RedPitayaScpi.GEN_TRIGGER_SOURCES.
        PE and NE means respectively Positive and Negative edge.
        Is important to note that it appears that the trigger can only be done internally.
        """,
        validator=strict_discrete_set,
        values=GEN_TRIGGER_SOURCES,
    )

    def run(self):
        """Trigger the generation of the specified fast analog output immediately internally."""
        self.write("SOUR{ch}:TRig:INT")

    enable = Instrument.control(
        "OUTPUT{ch}:STATE?",
        "OUTPUT{ch}:STATE %d",
        """Control the enabled state of the specified fast analog output.
        When enabled, the signal does not start generating, until triggered""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )


    # Sweep mode

    SWEEP_MODES = ('LINEAR', 'LOG')
    sweep_mode = Instrument.control(
        "SOUR{ch}:SWeep:MODE?",
        "SOUR{ch}:SWeep:MODE %s",
        """ Control the mode of the sweep. Can be set to:
        LINEAR or LOG""",
        validator=strict_discrete_set,
        values=SWEEP_MODES,
    )

    #START_FREQUENCY_SWEEP= [1e-6, 50e6]
    sweep_start_frequency = Instrument.control(
        "SOUR{ch}:SWeep:FREQ:START?",
        "SOUR{ch}:SWeep:FREQ:START %f",
        """ Control the start frequency for the sweep,
         from 1 uHz to 50 MHz.""",
        validator=strict_range,
        values=FREQUENCIES,
    )

    sweep_stop_frequency = Instrument.control(
        "SOUR{ch}:SWeep:FREQ:STOP?",
        "SOUR{ch}:SWeep:FREQ:STOP %f",
        """ Control the stop frequency for the sweep,
         from 1 uHz to 50 MHz.""",
        validator=strict_range,
        values=FREQUENCIES,
    )

    TIME = [1, 60e6] #in microseconds
    sweep_time = Instrument.control(
        "SOUR{ch}:SWeep:TIME?",
        "SOUR{ch}:SWeep:TIME %d",
        """ Control the generation time.
        How long it takes to transition from the starting frequency to the final frequency,
        from 1 us to 10 s.""",
        validator=strict_range,
        values=TIME,
    )

    sweep_state = Instrument.control(
        "SOUR{ch}:SWeep:STATE?",
        "SOUR{ch}:SWeep:STATE %s",
        """Control the enabled state of the sweep on the specified channel,
        for this to work we have to enable the output channel too""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'ON', False: 'OFF'}
    )

    DIRECTION = ('NORMAL', 'UP_DOWN')
    sweep_direction = Instrument.control(
        "SOUR{ch}:SWeep:DIR?",
        "SOUR{ch}:SWeep:DIR %s",
        """Control the direction of the sweep. Can be set to:
        NORMAl (up) or UP_DOWN """,
        validator=strict_discrete_set,
        values=DIRECTION,
    )


    # Burst mode
    #Not working at the moment to be further tested !!!

    # BURST_MODES = ('CONTINUOUS', 'BURST')
    # burst_mode = Instrument.control(
    #     "SOUR{ch}:BURS:STAT?",
    #     "SOUR{ch}:BURS:STAT %s",
    #     """ A string property that controls the generation mode.
    #     Can be set to: CONTINUOUS or BURST
    #     Red Pitaya will generate R bursts with N signal periods.
    #     P is the time between the start of one and the start of the next burst.""",
    #     validator=strict_discrete_set,
    #     values=BURST_MODES,
    # )
    #
    # burst_initial_voltage = Instrument.control(
    #     "SOUR{ch}:BURS:INITValue?",
    #     "SOUR{ch}:BURS:INITValue %f",
    #     """ A floating point property that controls the initial voltage value,
    #     from 0 V to 1V, that appears on the fast analog output once it is enabled
    #     but before the signal is generated.""",
    #     validator=strict_range,
    #     values=AMPLITUDES,
    # )
    #
    # burst_last_voltage = Instrument.control(
    #     "SOUR{ch}:BURS:LASTValue?",
    #     "SOUR{ch}:BURS:LASTValue %f",
    #     """ A floating point property that controls the end value of the
    #     generated burst signal, from 0 V to 1V.
    #     The output will stay on this value until a new signal is generated.""",
    #     validator=strict_range,
    #     values=AMPLITUDES,
    # )
    #
    # NUM = [1, 65536]
    # burst_num_cycles= Instrument.control(
    #     "SOUR{ch}:BURS:NCYC?",
    #     "SOUR{ch}:BURS:NCYC %d",
    #     """ An integer point property that controls the number of cycles in one burst (N),
    #     the number of generated waveforms in a burst.""",
    #     validator=strict_range,
    #     values=NUM,
    # )
    #
    # burst_num_repetitions = Instrument.control(
    #     "SOUR{ch}:BURS:NOR?",
    #     "SOUR{ch}:BURS:NOR %d",
    #     """ An integer point property that controls the number of repeated bursts (R),
    #     (65536 == INF repetitions).""",
    #     validator=strict_range,
    #     values=NUM,
    # )
    #
    # PERIOD = [1, 5e8] #in microseconds
    # burst_period = Instrument.control(
    #     "SOUR{ch}:BURS:INT:PER?",
    #     "SOUR{ch}:BURS:INT:PER %d",
    #     """ An integer point property that controls the duration of a single burst (P).
    #     This specifies the time between the start of one and the start of the next burst.
    #     The bursts will always have at least 1 microsecond between them:
    #     If the period is shorter than the burst, the software will default to 1 us
    #     between bursts.""",
    #     validator=strict_range,
    #     values=PERIOD,
    # )


class RedPitayaScpi(SCPIMixin, Instrument):
    """This is the class for the Redpitaya reconfigurable board

    The instrument is accessed using a TCP/IP Socket communication, that is an adapter in the form:
    "TCPIP::x.y.z.k::port::SOCKET" where x.y.z.k is the IP address of the SCPI server
    (that should be activated on the board) and port is the TCP/IP port number, usually 5000

    To activate the SCPI server, you have to connect first the redpitaya to your computer/network
    and enter the url address written on the network plug (on the redpitaya). It should be something
    like "RP-F06432.LOCAL/" then browse the menu, open the Development application and activate the
    SCPI server. When activating the server, you'll be notified with the IP/port address to use
    with this Instrument.

    :param ip_address: IP address to use, if `adapter` is None.
    :param port: Port number to use, if `adapter` is None.
    """

    TRIGGER_SOURCES = ('DISABLED', 'NOW', 'CH1_PE', 'CH1_NE', 'CH2_PE', 'CH2_NE',
                       'EXT_PE', 'EXT_NE', 'AWG_PE', 'AWG_NE')


    LV_MAX = 1
    HV_MAX = 20
    CLOCK = 125e6  # Hz
    DELAY_NS = tuple(np.array(np.array(range(-2**13, 2**13+1)) * 1 / CLOCK * 1e9, dtype=int))

    def __init__(self,
                 adapter=None,
                 ip_address: str | None = None,
                 port: int = 5000,
                 name="Redpitaya SCPI",
                 read_termination='\r\n',
                 write_termination='\r\n',
                 **kwargs):

        if adapter is None:  # if None build it from the usual way as written in the documentation
            if ip_address is None:
                raise ValueError("Provide either adapter or ip_address.")
            adapter = f"TCPIP::{ip_address}::{port}::SOCKET"

        super().__init__(
            adapter,
            name,
            read_termination=read_termination,
            write_termination=write_termination,
            **kwargs)

    dioN = Instrument.MultiChannelCreator(DigitalChannelN, list(range(7)), prefix='dioN')
    dioP = Instrument.MultiChannelCreator(DigitalChannelP, list(range(7)), prefix='dioP')
    led = Instrument.MultiChannelCreator(DigitalChannelLed, list(range(8)), prefix='led')

    analog_in_slow = Instrument.MultiChannelCreator(AnalogInputSlowChannel, list(range(4)),
                                                    prefix='ainslow')
    analog_out_slow = Instrument.MultiChannelCreator(AnalogOutputSlowChannel, list(range(4)),
                                                     prefix='aoutslow')

    analog_in = Instrument.MultiChannelCreator(AnalogInputFastChannel, (1, 2), prefix='ain')

    analog_out = Instrument.MultiChannelCreator(AnalogOutputFastChannel, (1, 2), prefix='aout')

    time = Instrument.control("SYST:TIME?",
                              "SYST:TIME %s",
                              """Control the time on board
                              time should be given as a datetime.time object""",
                              cast=str,
                              get_process=lambda _tstr:
                              datetime.time.fromisoformat(_tstr),
                              set_process=lambda _time:
                              _time.strftime('"%H:%M:%S"'),
                              )

    date = Instrument.control("SYST:DATE?",
                              "SYST:DATE %s",
                              """Control the date on board
                              date should be given as a datetime.date object""",
                              cast=str,
                              get_process=lambda dstr:
                              datetime.date.fromisoformat(dstr),
                              set_process=lambda date: date.strftime('"%Y-%m-%d"'),
                              )

    board_name = Instrument.measurement(
        "SYST:BRD:Name?",
        """Get the RedPitaya board name""",
        cast=str,
    )

    def digital_reset(self):
        """Reset the state of all digital lines"""
        self.write("DIG:RST")

    # ANALOG SECTION

    def analog_reset(self):
        """ Reset the voltage of all analog channels """
        self.write("ANALOG:RST")

    def output_reset(self):
        """ Reset the Analog Output generation channels. """
        self.write("GEN:RST")

    # ACQUISITION SECTION

    def acquisition_start(self):
        self.write("ACQ:START")

    def acquisition_stop(self):
        self.write("ACQ:STOP")

    def acquisition_reset(self):
        self.write("ACQ:RST")

    # Acquisition Settings

    decimation = Instrument.control(
        "ACQ:DEC?", "ACQ:DEC %d",
        """Control the decimation (int) as 2**n with n in range [0, 16]
        The sampling rate is given as 125MS/s / decimation
        """,
        validator=strict_discrete_set,
        values=[2**n for n in range(17)],
        cast=int,
    )

    average_skipped_samples = Instrument.control(
        "ACQ:AVG?", "ACQ:AVG %s",
        """Control the use of skipped samples (if decimation > 1) to average the returned
        acquisition array (bool)""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'ON', False: 'OFF'},
        cast=str,
    )

    acq_units = Instrument.control(
        "ACQ:DATA:Units?", "ACQ:DATA:Units %s",
        """Control the output data units (str), either 'RAW', or 'VOLTS' (default)""",
        validator=strict_discrete_set,
        values=['RAW', 'VOLTS'],
        cast=str,
    )

    buffer_length = Instrument.measurement(
        "ACQ:BUF:SIZE?",
        """Measure the size of the buffer, that is the number of points of the acquisition""",
        cast=int,
    )

    acq_format = Instrument.setting(
        "ACQ:DATA:FORMAT %s",
        """Set the format of the retrieved buffer data (str), either 'BIN', or 'ASCII' (default)""",
        validator=strict_discrete_set,
        values=['BIN', 'ASCII'],
    )

    # Acquisition Trigger

    acq_trigger_source = Instrument.setting(
        "ACQ:TRig %s",
        """Set the trigger source (str), one of RedPitayaScpi.TRIGGER_SOURCES.
        PE and NE means respectively Positive and Negative edge
        """,
        validator=strict_discrete_set,
        values=TRIGGER_SOURCES,
    )

    acq_trigger_status = Instrument.measurement(
        "ACQ:TRig:STAT?",
        """Get the trigger status (bool), if True the trigger as been fired (or is disabled)""",
        map_values=True,
        values={True: 'TD', False: 'WAIT'},
        cast=str,
    )

    acq_trigger_position = Instrument.measurement(
        "ACQ:TPOS?",
        """Get the position within the buffer where the trigger event happened""",
        cast=int,
    )

    acq_last_position = Instrument.measurement(
        "ACQ:WPOS?",
        """Get the current position of the write pointer, i.e the index of the most recent
        sample in the buffer""",
        cast=int,
    )

    acq_buffer_filled = Instrument.measurement(
        "ACQ:TRig:FILL?",
        """Get the status of the buffer(bool), if True the buffer is full""",
        map_values=True,
        values={True: 1, False: 0},
    )

    acq_trigger_delay_samples = Instrument.control(
        "ACQ:TRig:DLY?", "ACQ:TRig:DLY %d",
        """Control the trigger delay in number of samples (int) in the range [-8192, 8192]""",
        validator=truncated_range,
        cast=int,
        values=[-2**13, 2**13],
    )

    # direct call to the SCPI command "ACQ:TRig:DLY:NS?" seems not to be working...
    @property
    def acq_trigger_delay_ns(self):
        """Control the trigger delay in nanoseconds (int) in the range [-8192, 8192] / CLOCK"""
        return int(self.acq_trigger_delay_samples * 1 / self.CLOCK * 1e9)

    @acq_trigger_delay_ns.setter
    def acq_trigger_delay_ns(self, delay_ns: int):
        delay_sample = int(delay_ns * self.CLOCK / 1e9)
        self.acq_trigger_delay_samples = delay_sample

    # not working
    # acq_trigger_delay_ns = Instrument.control(
    #     "ACQ:TRig:DLY:NS?", "ACQ:TRig:DLY:NS %d",
    #     """Control the trigger delay in nanoseconds (int) multiple of the board clock period
    #     (1/RedPitayaSCPI.CLOCK)""",
    #     validator=truncated_discrete_set,
    #     values=DELAY_NS,
    #     cast=int,
    # )

    acq_trigger_level = Instrument.control(
        "ACQ:TRig:LEV?", "ACQ:TRig:LEV %f",
        """Control the level of the trigger in volts
        The allowed range should be dynamically set depending on the gain settings either +-LV_MAX
        or +- HV_MAX
        """,
        validator=truncated_range,
        values=[-LV_MAX, LV_MAX],
        dynamic=True,
    )
