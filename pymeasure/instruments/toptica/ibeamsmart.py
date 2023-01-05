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

import logging
import re
import time

from pyvisa.errors import VisaIOError

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class IBeamSmart(Instrument):
    """ IBeam Smart laser diode

    :param adapter: pyvisa resource name or adapter instance.
    :param baud_rate: communication speed, defaults to 115200.
    :param \\**kwargs: Any valid key-word argument for VISAAdapter.
    """
    _reg_value = re.compile(r"\w+\s+=\s+(\w+)")

    def __init__(self, adapter, name="Toptica IBeam Smart laser diode", **kwargs):
        kwargs.setdefault('read_termination', '\r\n')
        kwargs.setdefault('write_termination', '\r\n')
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            asrl={'baud_rate': 115200},
            **kwargs
        )
        # configure communication mode
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
        """Read a reply of the instrument and exctract the values, if possible.

        Reads a reply of the instrument which consists of at least two
        lines. The initial ones are the reply to the command while the last one
        should be '[OK]' which acknowledges that the device is ready to receive
        more commands.

        Note: '[OK]' is always returned as last message even in case of an
        invalid command, where a message indicating the error is returned
        before the '[OK]'

        Value extraction: extract <value> from 'name = <value> [unit]'.
        If <value> can not be identified the orignal string is returned.

        :return: string containing the ASCII response of the instrument (without '[OK]').
        """
        reply = super().read()  # read back the LF+CR which is always sent back
        if reply != "":
            raise ValueError(
                "TopticaAdapter.read(1): Error after command "
                f"'{self.lastcommand}' with message '{reply}'")
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
                self.adapter.connection.flush_read_buffer()
            except AttributeError:
                log.warning("Adapter does not have 'flush_read_buffer' method.")
            raise ValueError(
                "TopticaAdapter.read(2): Error after command "
                f"'{self.lastcommand}' with message '{reply}'")
        reply = '\n'.join(msg)
        r = self._reg_value.search(reply)
        if r:
            return r.groups()[0]
        else:
            return reply

    def write(self, command):
        self.lastcommand = command
        super().write(command)

    def check_errors(self):
        """Check communication after setting a value.

        Checks if the last reply is only '[OK]', otherwise a ValueError is
        raised and the read buffer is flushed because one has to assume that
        some communication is out of sync.
        """
        reply = self.read()
        if reply:
            # anything else than '[OK]'.
            self.adapter.connection.flush()
            raise ValueError(
                f"IBeamSmart: Error after command '{self.lastcommand}' with "
                f"message '{reply}'")

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

    laser_enabled = Instrument.control(
        "sta la", "la %s",
        """Control emission status of the laser diode driver (bool).""",
        validator=strict_discrete_set,
        values=[True, False],
        get_process=lambda s: True if s == 'ON' else False,
        set_process=lambda v: "on" if v else "off",
        check_set_errors=True,
    )

    channel1_enabled = Instrument.control(
        "sta ch 1", "%s",
        """Control status of Channel 1 of the laser (bool).""",
        validator=strict_discrete_set,
        values=[True, False],
        get_process=lambda s: True if s == 'ON' else False,
        set_process=lambda v: "en 1" if v else "di 1",
        check_set_errors=True,
    )

    channel2_enabled = Instrument.control(
        "sta ch 2", "%s",
        """Control status of Channel 2 of the laser (bool).""",
        validator=strict_discrete_set,
        values=[True, False],
        get_process=lambda s: True if s == 'ON' else False,
        set_process=lambda v: "en 2" if v else "di 2",
        check_set_errors=True,
    )

    power = Instrument.control(
        "sh pow", "ch pow %f mic",
        """Control actual output power in uW of the laser system. In pulse mode
        this means that the set value might not correspond to the readback
        one (float up to 200000).""",
        validator=strict_range,
        values=[0, 200000],
        check_set_errors=True,
    )

    def enable_continous(self):
        """Enable countinous emmission mode."""
        self.write('di ext')
        self.check_errors()
        self.laser_enabled = True
        self.channel2_enabled = True

    def enable_pulsing(self):
        """Enable pulsing mode.

        The optical output is controlled by a digital
        input signal on a dedicated connnector on the device."""
        self.laser_enabled = True
        self.channel2_enabled = True
        self.write('en ext')
        self.check_errors()

    def disable(self):
        """Shutdown all laser operation."""
        self.write('di ext')
        self.check_errors()
        self.channel2_enabled = False
        self.laser_enabled = False
