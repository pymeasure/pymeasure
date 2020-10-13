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

import time

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


def extract_value(reply):
    """ get_process function for values return in the format 'name = X.YZ unit'

    :param reply: reply string
    :returns: string with only the numerical value
    """
    return reply.split('=')[1].split()[0]


class IBeamSmart(Instrument):
    """ IBeam Smart laser diode

    :param adapter: pyvisa resource name of the instrument
    :param baud_rate: communication speed, defaults to 115200
    :param kwargs: Any valid key-word argument for VISAAdapter
    """
    version = Instrument.measurement(
           "ver", """ Firmware version number """,
           check_get_errors=True
           )

    serial = Instrument.measurement(
           "serial", """ Serial number of the laser system """,
           check_get_errors=True
           )

    temp = Instrument.measurement(
            "sh temp",
            """ temperature of the laser diode in degree centigrade.""",
            get_process=lambda v: float(extract_value(v)),
            check_get_errors=True)

    system_temp = Instrument.measurement(
            "sh temp sys",
            """ base plate (heatsink) temperature in degree centigrade.""",
            get_process=lambda v: float(extract_value(v)),
            check_get_errors=True)

    laser = Instrument.control(
            "sta la", "la %s",
            """ Status of the laser diode driver.
                This can be 'on', or 'off'.""",
            validator=strict_discrete_set,
            values=['on', 'off'],
            get_process=lambda s: s.lower(),
            check_set_errors=True, check_get_errors=True)

    channel1 = Instrument.control(
            "sta ch 1", "%s",
            """ Status of Channel 1 of the laser.
                This can be 'on', or 'off'.""",
            validator=strict_discrete_set,
            values=['on', 'off'],
            get_process=lambda s: s.lower(),
            set_process=lambda v: "en 1" if v == 'on' else "di 1",
            check_set_errors=True, check_get_errors=True)

    channel2 = Instrument.control(
            "sta ch 2", "%s",
            """ Status of Channel 2 of the laser.
                This can be 'on', or 'off'.""",
            validator=strict_discrete_set,
            values=['on', 'off'],
            get_process=lambda s: s.lower(),
            set_process=lambda v: "en 2" if v == 'on' else "di 2",
            check_set_errors=True, check_get_errors=True)

    power = Instrument.control(
            "sh pow", "ch pow %f mic",
            """ Actual output power in uW of the laser system. In pulse mode
            this means that the set value might not correspond to the readback
            one.""",
            validator=strict_range,
            values=[0, 200000],
            get_process=lambda v: float(extract_value(v)),
            check_set_errors=True, check_get_errors=True)

    def __init__(self, adapter, baud_rate=115200, **kwargs):
        super().__init__(
            adapter,
            "toptica IBeam Smart laser diode",
            includeSCPI = False
        )
        # hack to set baud_rate since VISAAdapter would filter it out!
        self.adapter.connection.baud_rate = baud_rate
        # configure communication mode
        self.adapter.write('echo off')
        self.adapter.write('prom off')
        time.sleep(0.04)
        # clear the initial messages from the controller
        self.adapter.flush()
        self.ask('talk usual')

    def check_errors(self):
        """ checks if the last reply is '[OK]', otherwise a ValueError is
        raised and the read buffer is flushed because one has to assume that
        some communication is out of sync.
        """
        if self.lastreply != '[OK]':
            self.adapter.flush()
            raise ValueError(
                f"IBeamSmart: Error after command '{self.lastcommand}' with "
                f"message '{self.lastreply}'")

    def _read_stripped(self):
        """ read a reply from the instrument and stip the termination sequence
        """
        return super().read().strip(self.adapter.connection.read_termination)

    def read(self):
        """ Reads a reply of the instrument which consists of two lines. The
        first one is the reply to the command while the last one should be
        '[OK]' which acknowledges that the device is ready to receive more
        commands. The last line of the reply is saved in self.lastreply for
        potential error checking.

        Note: This command only understands replies with one data line. More
        complicated replies have to be parsed by using the underlying adapter
        methods!

        :returns: String ASCII response of the instrument.
        """
        reply = self._read_stripped()
        self.lastreply = self._read_stripped()
        return reply

    def write(self, command, readAck=True):
        """ Writes a command to the instrument. Also reads back a LF+CR which
        is always sent back.

        :param command: command string to be sent to the instrument
        :param readAck: flag to decide if also an acknowledgement from the
        device is expected. This is the case for set commands.
        """
        self.lastcommand = command
        super().write(command)
        reply = self._read_stripped()
        if reply != '':
            raise ValueError(
                f"IBeamSmart.write: Error after command '{command}' with "
                f"message '{reply}'")
        if readAck:
            self.lastreply = self._read_stripped()

    def ask(self, command):
        """ Writes a command to the instrument and returns the resulting ASCII
        response

        :param command: command string to be sent to the instrument
        :returns: String ASCII response of the instrument
        """
        self.write(command, readAck=False)
        time.sleep(self.adapter.connection.query_delay)
        return self.read()

    def values(self, command, **kwargs):
        """ It seems wrong I have to reimplement this, but my ask method above is
        otherwise bypassed. """
        return self.ask(command)

    def enable_continous(self):
        """ enable countinous emmission mode """
        self.write('di ext')
        self.laser = 'on'
        self.channel2 = 'on'

    def enable_pulsing(self):
        """ enable pulsing mode. The optical output is controlled by a digital
        input signal on a dedicated connnector on the device """
        self.laser = 'on'
        self.channel2 = 'on'
        self.write('en ext')

    def disable(self):
        """ shutdown all laser operation """
        self.write('di ext')
        self.channel2 = 'off'
        self.laser = 'off'
