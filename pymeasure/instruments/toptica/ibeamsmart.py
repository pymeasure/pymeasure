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
import re
import time
from warnings import warn

from pyvisa.errors import VisaIOError

from pymeasure.instruments import Channel, Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def _deprecation_warning(text):
    def func(x):
        warn(text, FutureWarning)
        return x

    return func


def _deprecation_warning_channels(property_name):
    def func(x):
        warn(f'Deprecated property name "{property_name}", use the channels '
             '"enabled" property instead.', FutureWarning)
        return x

    return func


def deprecated_strict_discrete_set(value, values):
    warn("This property is deprecated, use channels instead.", FutureWarning)
    return strict_discrete_set(value, values)


class DriverChannel(Channel):
    """A laser diode driver channel for the IBeam Smart laser."""

    power = Channel.setting(
        "ch {ch} pow %f mic",
        """Set the output power in µW (float up to 200000).""",
        check_set_errors=True,
        validator=strict_range,
        values=[0, 200000],
    )

    enabled = Channel.control(
        "sta ch {ch}",
        "%s {ch}",
        """Control the enabled state of the driver channel.""",
        validator=strict_discrete_set,
        values=[True, False],
        get_process=lambda s: True if s == 'ON' else False,
        set_process=lambda v: "en" if v else "di",
        check_set_errors=True,
    )


class IBeamSmart(Instrument):
    """ IBeam Smart laser diode

    For the usage of the different diode driver channels, see the manual

    .. code::

        laser = IBeamSmart("SomeResourceString")
        laser.emission = True
        laser.ch_2.power = 1000  # µW
        laser.ch_2.enabled = True
        laser.shutdown()

    :param adapter: pyvisa resource name or adapter instance.
    :param baud_rate: The baud rate you have set in the instrument.
    :param \\**kwargs: Any valid key-word argument for VISAAdapter.
    """
    _reg_value = re.compile(r"\w+\s+=\s+(\w+)")

    ch_1 = Instrument.ChannelCreator(DriverChannel, 1)

    ch_2 = Instrument.ChannelCreator(DriverChannel, 2)

    ch_3 = Instrument.ChannelCreator(DriverChannel, 3)

    ch_4 = Instrument.ChannelCreator(DriverChannel, 4)

    ch_5 = Instrument.ChannelCreator(DriverChannel, 5)

    def __init__(self, adapter, name="Toptica IBeam Smart laser diode",
                 baud_rate=115200,
                 **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            read_termination='\r\n',
            write_termination='\r\n',
            asrl={'baud_rate': baud_rate},
            **kwargs
        )
        # configure communication mode: no repeating and no command prompt
        self.write('echo off')
        self.write('prom off')
        time.sleep(0.04)
        # clear the initial messages from the controller
        try:
            self.adapter.flush_read_buffer()
        except AttributeError:
            log.warning("Adapter does not have 'flush_read_buffer' method.")
        self.ask('talk usual')

    def read(self):
        """Read a reply of the instrument and extract the values, if possible.

        Reads a reply of the instrument which consists of at least two
        lines. The initial ones are the reply to the command while the last one
        should be '[OK]' which acknowledges that the device is ready to receive
        more commands.

        Note: '[OK]' is always returned as last message even in case of an
        invalid command, where a message indicating the error is returned
        before the '[OK]'

        Value extraction: extract <value> from 'name = <value> [unit]'.
        If <value> can not be identified the original string is returned.

        :return: string containing the ASCII response of the instrument (without '[OK]').
        """
        reply = super().read()  # read back the LF+CR which is always sent back
        if reply != "":
            raise ValueError(
                f"Error, no empty line at begin of message, instead '{reply}'")
        msg = []
        try:
            while True:
                line = super().read()
                if line == '[OK]':
                    break
                msg.append(line)
        except VisaIOError:
            reply = '\n'.join(msg)
            try:
                self.adapter.flush_read_buffer()
            except AttributeError:
                log.warning("Adapter does not have 'flush_read_buffer' method.")
            raise ValueError(f"Flush buffer failed after '{reply}'")
        reply = '\n'.join(msg)
        r = self._reg_value.search(reply)
        if r:
            return r.groups()[0]
        else:
            return reply

    def check_set_errors(self):
        """Check for errors after having gotten a property and log them.

        Checks if the last reply is only '[OK]', otherwise a ValueError is
        raised and the read buffer is flushed because one has to assume that
        some communication is out of sync.
        """
        reply = self.read()
        if reply:
            # anything else than '[OK]'.
            self.adapter.flush_read_buffer()
            log.error(f"Setting a property failed with reply '{reply}'.")
            raise ValueError(f"Setting a property failed with reply '{reply}'.")
        return []

    version = Instrument.measurement(
        "ver", """Get Firmware version number.""",
    )

    serial = Instrument.measurement(
        "serial", """Get Serial number of the laser system.""",
    )

    temp = Instrument.measurement(
        "sh temp",
        """Measure the temperature of the laser diode in degree centigrade.""",
    )

    system_temp = Instrument.measurement(
        "sh temp sys",
        """Measure base plate (heatsink) temperature in degree centigrade.""",
    )

    current = Instrument.measurement(
        "sh cur",
        """Measure the laser diode current in mA.""",
    )

    emission = Instrument.control(
        "sta la", "la %s",
        """Control emission status of the laser diode driver (bool).""",
        validator=strict_discrete_set,
        values=[True, False],
        get_process=lambda s: True if s == 'ON' else False,
        set_process=lambda v: "on" if v else "off",
        check_set_errors=True,
    )

    laser_enabled = Instrument.control(
        "sta la", "la %s",
        """Control emission status of the laser diode driver (bool).

        .. deprecated:: 0.12 Use attr:`emission` instead.
        """,
        validator=deprecated_strict_discrete_set,
        values=[True, False],
        get_process=lambda s: True if s == 'ON' else False,
        set_process=lambda v: "on" if v else "off",
        check_set_errors=True,
        preprocess_reply=_deprecation_warning(
            "Property `laser_enabled` is deprecated, use `emission` instead."),
    )

    channel1_enabled = Instrument.control(
        "sta ch 1", "%s",
        """Control status of Channel 1 of the laser (bool).

        .. deprecated:: 0.12 Use :attr:`ch_1.enabled` instead.
        """,
        validator=deprecated_strict_discrete_set,
        values=[True, False],
        get_process=lambda s: True if s == 'ON' else False,
        set_process=lambda v: "en 1" if v else "di 1",
        check_set_errors=True,
        preprocess_reply=_deprecation_warning_channels("channel1_enabled"),
    )

    channel2_enabled = Instrument.control(
        "sta ch 2", "%s",
        """Control status of Channel 2 of the laser (bool).

        .. deprecated:: 0.12 Use :attr:`ch_2.enabled` instead.""",
        validator=deprecated_strict_discrete_set,
        values=[True, False],
        get_process=lambda s: True if s == 'ON' else False,
        set_process=lambda v: "en 2" if v else "di 2",
        check_set_errors=True,
        preprocess_reply=_deprecation_warning_channels("channel2_enabled"),
    )

    power = Instrument.control(
        "sh pow", "ch pow %f mic",
        """Control actual output power in µW of the laser system. In pulse mode
        this means that the set value might not correspond to the readback
        one (float up to 200000).""",
        validator=strict_range,
        values=[0, 200000],
        check_set_errors=True,
    )

    def enable_continous(self):
        """Enable countinous emmission mode."""
        self.write('di ext')
        self.check_set_errors()
        self.emission = True
        self.ch_2.enabled = True

    def enable_pulsing(self):
        """Enable pulsing mode.

        The optical output is controlled by a digital
        input signal on a dedicated connnector on the device."""
        self.emission = True
        self.ch_2.enabled = True
        self.write('en ext')
        self.check_set_errors()

    def disable(self):
        """Shutdown all laser operation."""
        self.write('di 0')
        self.check_set_errors()
        self.emission = False

    def shutdown(self):
        """Brings the instrument to a safe and stable state."""
        self.disable()
        super().shutdown()
