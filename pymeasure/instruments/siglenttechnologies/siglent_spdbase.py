#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from pymeasure.instruments.instrument import Instrument
from pymeasure.instruments.validators import (strict_discrete_set,
                                              strict_range,
                                              truncated_range
                                              )
from enum import IntFlag

log = logging.getLogger(__name__)  # https://docs.python.org/3/howto/logging.html#library-config
log.addHandler(logging.NullHandler())


class SystemStatusCode(IntFlag):
    """System status enums based on ``IntFlag``

    Used in conjunction with :attr:`~.system_status_code`.

        ======  ======
        Value   Enum
        ======  ======
        256     WAVEFORM_DISPLAY
        64      TIMER_ENABLED
        32      FOUR_WIRE
        16      OUTPUT_ENABLED
        1       CONSTANT_CURRENT
        0       CONSTANT_VOLTAGE
        ======  ======

    """

    WAVEFORM_DISPLAY = 256  # bit 8 -- waveform display enabled
    TIMER_ENABLED = 64  # bit 6 -- timer enabled
    FOUR_WIRE = 32  # bit 5 -- four-wire mode enabled
    OUTPUT_ENABLED = 16  # bit 4 -- output enabled
    CONSTANT_CURRENT = 1   # bit 0 -- constant current mode
    CONSTANT_VOLTAGE = 0   # bit 0 -- constant voltage mode


class SPDBase(Instrument):
    """ The base class for Siglent SPDxxxxX instruments.
    """

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter,
            usb=dict(write_termination='\n',
                     read_termination='\n'),
            tcpip=dict(write_termination='\n',
                       read_termination='\n'),
            **kwargs
        )

    error = Instrument.measurement(
        "SYST:ERR?",
        """Read the error code and information of the instrument.

        :type: string
        """
    )

    fw_version = Instrument.measurement(
        "SYST:VERS?",
        """Read the software version of the instrument.

        :type: string
        """
    )

    system_status_code = Instrument.measurement(
        "SYST:STAT?",
        """Read the system status register.

        :type: :class:`.SystemStatusCode`
        """,
        get_process=lambda v: SystemStatusCode(int(v, base=16)),
    )

    local_lockout = Instrument.setting(
        "%s",
        """Set the local interface lockout.

        :type: bool
            ``True``: disables the local interface
            ``False``: enables it.

        """,
        validator=strict_discrete_set,
        values={True: "*LOCK", False: "*UNLOCK"},
        map_values=True
    )

    save_settings = Instrument.setting(
        "*SAV %d",
        """Save the current configuration in non-volatile memory.

        :type: int
        """,
        validator=strict_range,
        values=[1, 5]
    )

    recall_settings = Instrument.setting(
        "*RCL %d",
        """Recall the saved configuration from non-volatile memory.

        :type: int
        """,
        validator=strict_range,
        values=[1, 5]
    )

    selected_channel = Instrument.control(
        "INST?", "INST %s",
        """Control the selected channel of the instrument.

        :type: int
        """,
        validator=strict_discrete_set,
        values={1: "CH1"},  # This dynamic property should be updated for multi-channel instruments
        map_values=True,
        dynamic=True
    )

    set_4W_mode = Instrument.setting(
        "MODE:SET %s",
        """Configure 4-wire mode.

        :type: bool
            ``True``: enables 4-wire mode
            ``False``: disables it.

        """,
        validator=strict_discrete_set,
        values={False: "2W", True: "4W"},
        map_values=True
    )

    def save_config(self, index):
        """Save the current config to memory.

        :param index:
            string: index of the location to save the configuration
        """
        self.save_settings = index

    def recall_config(self, index):
        """Recall a config from memory.

        :param index:
            string: index of the location from which to recall the configuration
        """
        self.recall_settings = index


class SPDChannel(object):
    """ The channel class for Siglent SPDxxxxX instruments.
    """

    def __init__(self, instrument, channel: int = 1):
        self.instrument = instrument
        self.channel = channel

    voltage = Instrument.measurement(
        "MEAS:VOLT? CH{channel}",
        """Measure the channel output voltage.

        :type: float
        """
    )

    current = Instrument.measurement(
        "MEAS:CURR? CH{channel}",
        """Measure the channel output voltage.

        :type: float
        """
    )

    power = Instrument.measurement(
        "MEAS:POWE? CH{channel}",
        """Measure the channel output voltage.

        :type: float
        """
    )

    set_current = Instrument.control(
        "CH{channel}:CURR?", "CH{channel}:CURR %g",
        """Control the output current configuration of the channel.

        :type: float
        """,
        validator=truncated_range,
        values=[0, 8],
        dynamic=True
    )

    set_voltage = Instrument.control(
        "CH{channel}:VOLT?", "CH{channel}:VOLT %g",
        """Control the output voltage configuration of the channel.

        :type: float
        """,
        validator=truncated_range,
        values=[0, 16],
        dynamic=True
    )

    output = Instrument.setting(
        "OUTP CH{channel},%s",
        """Configure the power supply output.

        :type: bool
            ``True``: enables the output
            ``False``: disables the output

        """,
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True
    )

    enable_timer = Instrument.setting(
        "TIME CH{channel},%s",
        """Enable the channel timer.

        :type: bool
            ``True``: enables the timer
            ``False``: disables it

        """,
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True
    )

    def ask(self, cmd):
        return self.instrument.ask(cmd.format(channel=self.channel))

    def write(self, cmd):
        self.instrument.write(cmd.format(channel=self.channel))

    def values(self, cmd, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values(cmd.format(channel=self.channel), **kwargs)

    def check_errors(self):
        return self.instrument.check_errors()

    def enable(self):
        """Enable the channel output

        :returns: self
        """
        self.instrument.selected_channel = self.channel
        self.output = True
        return self

    def disable(self):
        """Disable the channel output

        :returns: self
        """
        self.instrument.selected_channel = self.channel
        self.output = False
        return self
