#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
from time import sleep
from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AxisError(Exception):
    """
    Raised when a particular axis causes an error for OptoSigma SBIS26.


    """
    MESSAGE_ACK1 = {
        'X': 'Error of command',
        'K': 'Command received normally'
    }

    MESSAGE_ACK2 = {
        'C': 'Stopped by clockwise limit sensor detected',
        'W': 'Stopped by counter-clockwise limit sensor detected',
        'E': 'Stopped by both of limit sensors detected',
        'K': 'Normal stop'
    }

    MESSAGE_ACK3 = {
        'K': 'No alarm',
        'E': 'Alarm on the hardware',
        'C': 'Alarm on the communication',
    }

    MESSAGE_ACK4 = {
        'B': 'Busy',
        'R': 'Ready',
    }

    def __init__(self, code1, code2, code3, code4):
        self.message1 = self.MESSAGE_ACK1[code1]
        self.message2 = self.MESSAGE_ACK2[code2]
        self.message3 = self.MESSAGE_ACK3[code3]
        self.message4 = self.MESSAGE_ACK4[code4]

    def __str__(self):
        return "OptoSigma SBIS26 Error: %s, %s, %s, %s" % (self.message1, self.message2, self.message3, self.message4)


class Axis(Channel):
    """FIXME"""

    position = Instrument.measurement("Q:D,{ch}",
                                      """Reads the current poision""",
                                      get_process=lambda v: v[2]
                                      )
    speed = Instrument.control("?:D,{ch},D",
                               "D:D,{ch},%d,%d,%d",
                               """An integer property that represents the speed of the axis in pulses/s units""",
                               validator=truncated_range,
                               values=((1, 1, 1), (800000, 800000, 1000)),
                               get_process=lambda v: list(map(int, v)),
                               check_set_errors=True,
                               )
    error = Instrument.measurement("SRQ:D,{ch}",
                                   """Get an error code from the stage.""",
                                   )

    def home(self):
        """
        Send the stage to the mechanical home
        """
        self.write("H:{ch}")
        return self.read()

    def move(self, pos):
        """
        Moves to the specified position.

        Parameters:
            pos (int): The position to move to.

        Returns:
            str: The response received from the write operation.

        """
        if pos >= 0:
            self.write("A:D,{ch}," + f"+{pos}")
        else:
            self.write("A:D,{ch}," + f"{pos}")

        return self.read()

    def move_relative(self, pos):
        """
        Moves the position relative to the current position.

        Args:
            pos (int): The relative position to move. Positive values will move in the forward direction,
                       while negative values will move in the backward direction.

        Returns:
            str: The result of the movement.
        """
        if pos >= 0:
            self.write("M:D,{ch}," + f"+{pos}")
        else:
            self.write("M:D,{ch}," + f"{pos}")

        return self.read()

    def stop(self):
        """
        Stop the stage for all the axes immediately
        """
        self.write("LE:A")
        return self.read()

    @property
    def errors(self):
        """

        Get a list of error Exceptions that can be later raised, or used to diagnose the situation.

        Parameters:
            - self: The current instance of the class (implicitly passed).

        Returns:
            - AxisError object: An instance of the `AxisError` class based on the error code retrieved from the device.

        """

        code = self.error
        errors = AxisError(*code[2:])
        return errors


class SBIS26(Instrument):
    """

    SBIS26 Class

    This class is a subclass of the Instrument class and represents the OptoSigma SBIS26 Motorized Stage instrument.

    Attributes:
        connection: A control attribute that represents the instrument's connection status.
        ch_1: A channel creator attribute for channel 1 of the instrument.
        ch_2: A channel creator attribute for channel 2 of the instrument.
        ch_3: A channel creator attribute for channel 3 of the instrument.

    Methods:
        __init__ : Initializes the SBIS26 object.
    """

    def __init__(self,
                 adapter,
                 name="OptoSigma SBIS26 Motorized Stage",
                 baud_rate=38400,
                 **kwargs
                 ):
        self.termination_str = "\r\n"

        super().__init__(
            adapter,
            name,
            baud_rate=baud_rate,
            write_termination=self.termination_str,
            read_termination=self.termination_str,
            **kwargs
        )

        self.initialize()

    ch_1 = Instrument.ChannelCreator(Axis, 1)
    ch_2 = Instrument.ChannelCreator(Axis, 2)
    ch_3 = Instrument.ChannelCreator(Axis, 3)

    def initialize(self):
        """Initializes the SBIS26 object"""
        self.write("#CONNECT")
        return self.read()

    def check_set_errors(self):
        """Check for errors after having set a property and log them.

        Called if :code:`check_set_errors=True` is set for that property.

        :return: error entry.
        """
        try:
            self.read()
        except Exception as exc:
            log.exception("Setting a property failed.", exc_info=exc)
            raise
        else:
            return []

    def read(self):
        msg = super().read()
        if msg[-1] == "NG":
            raise ValueError('SBIS26 Error')
        return msg
