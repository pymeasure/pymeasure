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
import logging
from pymeasure.instruments import Instrument, SCPIUnknownMixin
from pymeasure.instruments.channel import Channel
from pymeasure.instruments.validators import (strict_discrete_range,
                                              strict_discrete_set,
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


class SPDChannel(Channel):
    """ The channel class for Siglent SPDxxxxX instruments.
    """

    def __init__(self, parent, id,
                 voltage_range: list = [0, 16],
                 current_range: list = [0, 8]):
        super().__init__(parent, id)
        self.voltage_range = voltage_range
        self.current_range = current_range

    voltage = Instrument.measurement(
        "MEAS:VOLT? CH{ch}",
        """Measure the channel output voltage.

        :type: float
        """
    )

    current = Instrument.measurement(
        "MEAS:CURR? CH{ch}",
        """Measure the channel output current.

        :type: float
        """
    )

    power = Instrument.measurement(
        "MEAS:POWE? CH{ch}",
        """Measure the channel output power.

        :type: float
        """
    )

    current_limit = Instrument.control(
        "CH{ch}:CURR?", "CH{ch}:CURR %g",
        """Control the output current configuration of the channel.

        :type : float
        """,
        validator=truncated_range,
        values=[0, 8],
        dynamic=True
    )

    voltage_setpoint = Instrument.control(
        "CH{ch}:VOLT?", "CH{ch}:VOLT %g",
        """Control the output voltage configuration of the channel.

        :type : float
        """,
        validator=truncated_range,
        values=[0, 16],
        dynamic=True
    )

    def enable_output(self, enable: bool = True):
        """Enable the channel output.

        :type: bool
            ``True``: enables the output
            ``False``: disables it
        """
        self.parent.selected_channel = self.id
        self.write('OUTP CH{ch},' + ("ON" if enable else "OFF"))

    def enable_timer(self, enable: bool = True):
        """Enable the channel timer.

        :type: bool
            ``True``: enables the timer
            ``False``: disables it
        """
        self.write('TIME CH{ch},' + ("ON" if enable else "OFF"))

    def configure_timer(self, step, voltage, current, duration):
        """Configure the timer step.

        :param step:
            int: index of the step to save the configuration
        :param voltage:
            float: voltage setpoint of the step
        :param current:
            float: current limit of the step
        :param duration:
            int: duration of the step in seconds
        """
        step = strict_discrete_range(step, [1, 5], 1)
        voltage = truncated_range(voltage, self.voltage_range)
        current = truncated_range(current, self.current_range)
        duration = truncated_range(duration, [0, 10000])
        self.write(f'TIME:SET CH{{ch}},{step:d},{voltage:1.3f},{current:1.3f},{duration:d}')


class SPDBase(SCPIUnknownMixin, Instrument):
    """ The base class for Siglent SPDxxxxX instruments.

    Uses :class:`SPDChannel` for measurement channels.
    """

    def __init__(self, adapter, name="Siglent SPDxxxxX instrument Base Class", **kwargs):
        super().__init__(
            adapter,
            name,
            usb=dict(write_termination='\n',
                     read_termination='\n'),
            tcpip=dict(write_termination='\n',
                       read_termination='\n'),
            **kwargs
        )

    error = Instrument.measurement(
        "SYST:ERR?",
        """Get the error code and information of the instrument.

        :type: string
        """
    )

    fw_version = Instrument.measurement(
        "SYST:VERS?",
        """Get the software version of the instrument.

        :type: string
        """
    )

    system_status_code = Instrument.measurement(
        "SYST:STAT?",
        """Get the system status register.

        :type: :class:`.SystemStatusCode`
        """,
        get_process=lambda v: SystemStatusCode(int(v, base=16)),
    )

    selected_channel = Instrument.control(
        "INST?", "INST %s",
        """Control the selected channel of the instrument.

        :type : int
        """,
        validator=strict_discrete_set,
        values={1: "CH1"},  # This dynamic property should be updated for multi-channel instruments
        map_values=True,
        dynamic=True
    )

    def save_config(self, index):
        """Save the current config to memory.

        :param index:
            int: index of the location to save the configuration
        """
        index = strict_discrete_range(index, [1, 5], 1)
        self.write(f"*SAV {index:d}")

    def recall_config(self, index):
        """Recall a config from memory.

        :param index:
            int: index of the location from which to recall the configuration
        """
        index = strict_discrete_range(index, [1, 5], 1)
        self.write(f"*RCL {index:d}")

    def enable_local_interface(self, enable: bool = True):
        """Configure the availability of the local interface.

        :type: bool
            ``True``: enables the local interface
            ``False``: disables it.
        """
        self.write("*UNLOCK" if enable else "*LOCK")

    def shutdown(self):
        """ Ensure that the voltage is turned to zero
        and disable the output. """
        for ch in self.channels.values():
            ch.voltage_setpoint = 0
            ch.enable_output(False)
        super().shutdown()


class SPDSingleChannelBase(SPDBase):
    def enable_4W_mode(self, enable: bool = True):
        """Enable 4-wire mode.

        :type: bool
            ``True``: enables 4-wire mode
            ``False``: disables it.
        """
        self.write(f'MODE:SET {"4W" if enable else "2W"}')
