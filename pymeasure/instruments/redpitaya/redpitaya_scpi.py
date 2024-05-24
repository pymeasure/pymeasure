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


import datetime
import numpy as np

from pymeasure.instruments import Instrument, Channel, SCPIMixin
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

import logging
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
    )

    def get_data(self, npts: int = None, format='ASCII') -> np.ndarray:
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
                 ip_address: str = '169.254.134.87', port: int = 5000, name="Redpitaya SCPI",
                 read_termination='\r\n',
                 write_termination='\r\n',
                 **kwargs):

        if adapter is None:  # if None build it from the usual way as written in the documentation
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

    time = Instrument.control("SYST:TIME?",
                              "SYST:TIME %s",
                              """Control the time on board
                              time should be given as a datetime.time object""",
                              get_process=lambda _tstr:
                              datetime.time(*[int(split) for split in _tstr]),
                              set_process=lambda _time:
                              _time.strftime('%H,%M,%S'),
                              )

    date = Instrument.control("SYST:DATE?",
                              "SYST:DATE %s",
                              """Control the date on board
                              date should be given as a datetime.date object""",
                              get_process=lambda dstr:
                              datetime.date(*[int(split) for split in dstr]),
                              set_process=lambda date: date.strftime('%Y,%m,%d'),
                              )

    board_name = Instrument.measurement("SYST:BRD:Name?",
                                        """Get the RedPitaya board name""")

    def digital_reset(self):
        """Reset the state of all digital lines"""
        self.write("DIG:RST")

    # ANALOG SECTION

    def analog_reset(self):
        """ Reset the voltage of all analog channels """
        self.write("ANALOG:RST")

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
    )

    acq_units = Instrument.control(
        "ACQ:DATA:Units?", "ACQ:DATA:Units %s",
        """Control the output data units (str), either 'RAW', or 'VOLTS' (default)""",
        validator=strict_discrete_set,
        values=['RAW', 'VOLTS'],
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
    )

    acq_trigger_position = Instrument.measurement(
        "ACQ:TPOS?",
        """Get the position within the buffer where the trigger event happened""",
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
