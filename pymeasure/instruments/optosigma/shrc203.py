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
from pymeasure.adapters import Adapter
from enum import StrEnum
from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class D(Exception):
    """
    Exception raised when an invalid axis is specified.

    TODO
    param:
    """

    MESSAGES = {
        '1': 'Normal (S1 to S10 and emergency stop has not occurred)',
        '3': 'Command error',
        '7': 'Scale error (S1)',
        'F': 'Disconnection error (S2)',
        '1F': 'Overflow error (S4)',
        '3F': 'Emergency stop',
        '7F': 'Hunting error (S3)',
        'FF': 'Limit error (S5)',
        '1FF': 'Counter overflow (S6)',
        '3FF': 'Auto config error',
        '7FF': '24V IO overload warning (W1)',
        'FFF': '24V terminal block overload warning (W2)',
        '1FFF': 'System error (S7)',
        '3FFF': 'Motor driver overheat warning (W3)',
        '7FFF': 'Motor driver overheat error (S10)',
        'FFFF': 'Out of in-position range   (after positioning is completed) (READY)',
        '1FFFF': 'Out of in-position range (During positioning operation) (BUSY)',
        '3FFFF': 'Logical origin return is in progress',
        '7FFFF': 'Mechanical origin return is in progress',
        'FFFFF': 'CW limit detection',
        '1FFFFF': 'CCW limit detection',
        '3FFFFF': 'CW software limit stop',
        '7FFFFF': 'CCW software limit stop',
        'FFFFFF': 'NEAR sensor detection',
        '1FFFFFF': 'ORG sensor detection',
    }

    def __init__(self, axis, code):
        """
        :param code: The error code returned by the controller, as a string of comma-separated values  (e.g. "1,1,1,R,B,R") 
        """
        self.axis = axis
        self.code = code.split(",")
        self.error = code[0]
        self.message = self.MESSAGES[self.error]
        self.status = code[1]

    # def __str__(self):
    #     self.error_message = "OptoSigma SHRC-203"
    #     for i in range(len(self.code)):
    #         error = self.code[i]
    #         message = self.MESSAGES[error]
    #         self.error_message += " Axis {} Error: {}\n".format(i + 1, message)
    #     return self.error_message

    def __str__(self):
        return f"OptoSigma SHRC-203 Axis {self.axis} Error: {self.message}"


class Axis:
    """ Represents an axis of OptoSigma SHRC203 Three-Axis Controller,
    which can have independent parameters from the other axes.

    """

    def __init__(self, axis, controller):
        self.axis = str(axis)
        self.controller = controller


class SHRC203(Instrument):
    """
    Represents the OptoSigma SHRC-203 Three-Axis Controller and provides a
    high-level interface for interacting with the instrument.

    By default this instrument is constructed with x, y, and z
    attributes that represent axes 1, 2, and 3. Custom implementations
    can overwrite this depending on the avalible axes. Axes are controlled
    through an :class:`Axis <pymeasure.instruments.optosigma.shrc203.Axis>`
    class.
    
    :param adapter: The VISA resource name of the controller
    :param name: The name of the controller
    :param query_delay: The time delay between successive queries in seconds, default 0.05
    :param kwargs: Any valid key-word argument for VISAAdapter
    """

    # TODO: make command with no axis ->  !:!, RESET, MODE, FMT,



    def __init__(self,
                 adapter,
                 name="OptoSigma SHRC-203 Stage Controller",
                 query_delay=0.05,
                 **kwargs
                 ):
        self.query_delay = query_delay
        self.termination_str = "\r\n"

        self.x = Axis(1, self)
        self.y = Axis(2, self)
        self.z = Axis(3, self)

        super().__init__(
            adapter,
            name,
            write_termination=self.termination_str,
            read_termination=self.termination_str,
            usb={baud_rate: 38400},
            **kwargs
        )

    def home(self):
        """
        Perform mechanical origin return.
        """
        self.write("H")

    def move(self, axis, position):
        """
        Move the stage to the specified position.

        :param axis: The axis to move
        :param position: The position to move to
        """
        self.write(f"{axis}:M {position}")

    def wait_for(self, query_delay=0):
        """

        """

    def speed(self, ):
        """

        """
