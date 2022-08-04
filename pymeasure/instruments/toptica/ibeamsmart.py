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

    :param port: pyvisa resource name of the instrument
    :param baud_rate: communication speed, defaults to 115200
    :param kwargs: Any valid key-word argument for VISAAdapter
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
        """Read a reply of the instrument and exctract the values.

        Reads a reply of the instrument which consists of at least two
        lines. The initial ones are the reply to the command while the last one
        should be '[OK]' which acknowledges that the device is ready to receive
        more commands.

        Note: '[OK]' is always returned as last message even in case of an
        invalid command, where a message indicating the error is returned
        before the '[OK]'

        Value extraction: extract <value> from 'name = <value> [unit]'.
        If <value> can not be identified the orignal string is returned.

        :returns: string containing the ASCII response of the instrument.
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
                self.adapter.flush_read_buffer()
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

    def write(self, command, check_ack=True):
        """ Writes a command to the instrument. Also reads back a LF+CR which
        is always sent back.

        :param command: command string to be sent to the instrument
        :param check_ack: flag to decide if also an acknowledgement from the
          device is expected. This is the case for set commands.
        """
        self.lastcommand = command
        super().write(command)
        # The following lines are used in order to avoid the need of a
        # complicated Instrument where every property would need to use
        # check_set/get_errors and many Adapter functions would need to be
        # reimplemented in the Instrument. See discussion in PR #352
        if check_ack:
            reply = self.read()
            if reply != "":
                # if any message is returned here this indicates some misuse
                raise ValueError(
                    f"TopticaAdapter.write: Error after command '{command}'"
                    f"with message '{reply}'")

    version = Instrument.measurement(
           "ver", """ Firmware version number """,
    )

    serial = Instrument.measurement(
           "serial", """ Serial number of the laser system """,
    )

    temp = Instrument.measurement(
            "sh temp",
            """ temperature of the laser diode in degree centigrade.""",
    )

    system_temp = Instrument.measurement(
            "sh temp sys",
            """ base plate (heatsink) temperature in degree centigrade.""",
    )

    laser_enabled = Instrument.control(
            "sta la", "la %s",
            """ Status of the laser diode driver.
                This can be True if the laser is on or False otherwise""",
            validator=strict_discrete_set,
            values=[True, False],
            get_process=lambda s: True if s == 'ON' else False,
            set_process=lambda v: "on" if v else "off",
    )

    channel1_enabled = Instrument.control(
            "sta ch 1", "%s",
            """ Status of Channel 1 of the laser.
                This can be True if the laser is on or False otherwise""",
            validator=strict_discrete_set,
            values=[True, False],
            get_process=lambda s: True if s == 'ON' else False,
            set_process=lambda v: "en 1" if v else "di 1",
    )

    channel2_enabled = Instrument.control(
            "sta ch 2", "%s",
            """ Status of Channel 2 of the laser.
                This can be True if the laser is on or False otherwise""",
            validator=strict_discrete_set,
            values=[True, False],
            get_process=lambda s: True if s == 'ON' else False,
            set_process=lambda v: "en 2" if v else "di 2",
    )

    power = Instrument.control(
            "sh pow", "ch pow %f mic",
            """ Actual output power in uW of the laser system. In pulse mode
            this means that the set value might not correspond to the readback
            one.""",
            validator=strict_range,
            values=[0, 200000],
    )

    def enable_continous(self):
        """ enable countinous emmission mode """
        self.write('di ext')
        self.laser_enabled = True
        self.channel2_enabled = True

    def enable_pulsing(self):
        """ enable pulsing mode. The optical output is controlled by a digital
        input signal on a dedicated connnector on the device """
        self.laser_enabled = True
        self.channel2_enabled = True
        self.write('en ext')

    def disable(self):
        """ shutdown all laser operation """
        self.write('di ext')
        self.channel2_enabled = False
        self.laser_enabled = False
