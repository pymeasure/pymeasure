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
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ConexCC(Instrument):
    """
    Class for Newport ConexCC Controllers
    """
    def __init__(self, address, index=1, **kwargs):
        super(ConexCC, self).__init__(
            address, "Conex-CC Controller for Linear Stages", baud_rate=921600,
            read_termination='\r\n', write_termination='\r\n', **kwargs)
        # Implementation of this index should allow for communication with
        # serially connected controllers on a single USB interface
        # This is not (yet) tested however!
        self.index = index
        self.zero()

    def ask(self, command):
        super(ConexCC, self).ask(str(self.index)+command)

    def write(self, command):
        super(ConexCC, self).write(str(self.index)+command)

    def values(self, command, **kwargs):
        # Cut off the repetition of the command that is included in the reply
        reply = super(ConexCC, self).values(
            str(self.index)+command, **kwargs)[0][len(str(self.index))+2:]
        return reply

    acceleration = Instrument.control(
        'AC?', 'AC%f',
        """ Acceleration of the stage in
        units/s^2. """,
        get_process=lambda v: float(v),
        validator=strict_range,
        values=(1e-6, 1e12))

    velocity = Instrument.control(
        'VA?', 'VA%f',
        """ Acceleration of the stage in
        units/s. """,
        get_process=lambda v: float(v),
        validator=strict_range,
        values=(1e-6, 1e12))

    position = Instrument.measurement(
        'TP', """ Get current Stage Position. """)

    Kp = Instrument.control(
        'KP?', 'KP%f',
        """ Proportional Gain for PID control loop.""",
        validator=strict_range,
        values=(0, 1e12)
    )

    Ki = Instrument.control(
        'KI?', 'KI%f',
        """ Integral Gain for PID control loop.""",
        validator=strict_range,
        values=(0, 1e12)
    )

    Kd = Instrument.control(
        'KD?', 'KD%f',
        """ Derivative Gain for PID control loop.""",
        validator=strict_range,
        values=(0.001, 1e12)
    )

    PID_enabled = Instrument.control(
        'SC?', 'SC%g',
        """ PID Control Loop State (enabled/disabled).""",
        map_values=True, values={True: 1, False: 0},
        validator=strict_discrete_set
    )

    def move_to(self, pos):
        """ Move to absolute position
        :param pos Absolute position to move to.
        """
        cmd = 'PA%f' % (pos)
        self.write(cmd)

    def move_by(self, amount):
        """ Move by a relative amount
        :param amount Relative amount to move.
        """
        cmd = 'PR%f' % (amount)
        self.write(cmd)

    def setup_pid(self, Kp, Ki, Kd):
        """ Setup function for setting proportional, integral
        and derivative gain in one command.
        :param Kp Proportional Gain
        :param Ki Integral Gain
        :param Kd Derivative Gain
        """
        self.Kp = Kp
        self.Kd = Kd
        self.Ki = Ki

    def reset(self):
        """ Reset the device. """
        self.write('RS')

    def zero(self):
        """ Set the current position as the new zero/home. """
        self.write('TH1')

    def home(self, pos=None):
        """ Do homing process. """
        # If a certain position should be defined as home,
        # move there and set new zero
        if pos:
            self.move_to(pos)
            self.zero()
        self.write('OR')
