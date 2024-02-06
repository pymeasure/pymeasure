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
from time import sleep
from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AxisError(Exception):
    """
    Raised when a particular axis causes an error for OptoSigma SHRC-203.

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

    def __init__(self, code):
        self.message = self.MESSAGES[code]

    def __str__(self):
        return f"OptoSigma SHRC-203 Error: {self.message}"


class Axis(Channel):
    """ Represents an axis of OptoSigma SHRC203 Three-Axis Controller,
    which can have independent parameters from the other axes.
    """

    open_loop = Instrument.control("?:F{ch}", "F:{ch}%d",
                                   """Query or set the open loop mode. 0: Close loop, 1: Open loop""",
                                   validator=strict_discrete_set,
                                   values=[1, 0],
                                   check_set_errors=True
                                   )

    speed = Instrument.control("?:D{ch}", "D:{ch}S%dF%dR%d",
                               """An integer property that controls the speed""",
                               validator=truncated_range,
                               values=((1, 1, 1), (1000000, 1000000, 1000)),
                               get_process=lambda v: list(map(int, v)),
                               check_set_errors=True,
                               )

    motion_done = Instrument.measurement("!:{ch}S",
                                         """Query to see if the axis is currently moving. "R": ready, "B": busy""")

    zero = Instrument.setting("R:{ch}",
                              """ Resets the axis position to be zero at the current poisiton.""",
                              check_set_errors=True
                              )

    stop = Instrument.setting("L:{ch}",
                              """ Decelerate and stop the axis.""",
                              check_set_errors=True
                              )

    step = Instrument.measurement("?:P{ch}",
                                  """ Query the step size per pulse in nanometer. The step size is calculated from 
                                  BASERATE (B) and DIVIDE (D) expressed as B*10/D """)

    def wait_for_stop(self, interval=0.05, timeout=10):
        """ Wait for the axis to stop moving.

        :param interval: The time in seconds to wait between checks
        :param timeout: The maximum time in seconds to wait
        """

        loop = 0
        while self.motion_done == "B":
            sleep(interval)
            loop = loop + 1
            if loop > timeout / interval:
                break
                # raise TimeoutError("Timeout waiting for axis to stop.")

    def move(self, position):
        """ Move the axis to a position.
        """
        if position >= 0:
            self.write("A:{ch}" + f"+P{position}")
        else:
            self.write("A:{ch}" + f"-P%{abs(position)}")
        self.write("G:")
        self.wait_for_stop()
        return self.read()

    def move_relative(self, position, speed=None, units=None):
        """ Move the axis to a relative position.
        """
        if position >= 0:
            self.write("M:{ch}" + f"+P{position}")
        else:
            self.write("M:{ch}" + f"-P%{abs(position)}")
        self.write("G:")
        self.wait_for_stop()
        return self.read()

    def home(self):
        """ Home the axis to the mechanical origin.
        """
        self.write("H:{ch}")
        return self.read()

    def error(self):
        """ Get an error code from the motion controller.
        """
        code = self.ask("SRQ:{ch}S")
        code = code.split(",")[0]
        return AxisError(code)


class SHRC203(Instrument):
    """
    Represents the OptoSigma SHRC-203 Three-Axis Controller and provides a
    high-level interface for interacting with the instrument.

    By default this instrument is constructed with x, y, and z
    attributes that represent axes 1, 2, and 3. Custom implementations
    can overwrite this depending on the available axes. Axes are controlled
    through an :class:`Axis <pymeasure.instruments.optosigma.shrc203.Axis>`
    class.

    :param adapter: The VISA resource name of the controller
    :param name: The name of the controller
    :param kwargs: Any valid key-word argument for VISAAdapter
    """

    def __init__(self,
                 adapter,
                 name="OptoSigma SHRC-203 Stage Controller",
                 **kwargs
                 ):
        self.termination_str = "\r\n"

        super().__init__(
            adapter,
            name,
            write_termination=self.termination_str,
            read_termination=self.termination_str,
            **kwargs
        )

    ch_1 = Instrument.ChannelCreator(Axis, 1)
    ch_2 = Instrument.ChannelCreator(Axis, 2)
    ch_3 = Instrument.ChannelCreator(Axis, 3)

    # axis_all = Instrument.ChannelCreator(Axis, "W")

    mode = Instrument.control("?:MODE", "MODE:%s", """Query or set the controller mode.""",
                              validator=strict_discrete_set,
                              values=["HOST", "MANUAL", "REMOTE", "TEACHING", "EDIT", "LOAD", "TEST"],
                              check_set_errors=True
                              )

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
        if msg == "NG":
            raise ValueError('SHRC203 Error')
        return msg
