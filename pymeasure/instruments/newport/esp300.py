#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

from time import sleep

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set


class AxisError(Exception):
    """ Raised when a particular axis causes an error for
    the Newport ESP300. """

    MESSAGES = {
        '00': 'MOTOR TYPE NOT DEFINED',
        '01': 'PARAMETER OUT OF RANGE',
        '02': 'AMPLIFIER FAULT DETECTED',
        '03': 'FOLLOWING ERROR THRESHOLD EXCEEDED',
        '04': 'POSITIVE HARDWARE LIMIT DETECTED',
        '05': 'NEGATIVE HARDWARE LIMIT DETECTED',
        '06': 'POSITIVE SOFTWARE LIMIT DETECTED',
        '07': 'NEGATIVE SOFTWARE LIMIT DETECTED',
        '08': 'MOTOR / STAGE NOT CONNECTED',
        '09': 'FEEDBACK SIGNAL FAULT DETECTED',
        '10': 'MAXIMUM VELOCITY EXCEEDED',
        '11': 'MAXIMUM ACCELERATION EXCEEDED',
        '12': 'Reserved for future use',
        '13': 'MOTOR NOT ENABLED',
        '14': 'Reserved for future use',
        '15': 'MAXIMUM JERK EXCEEDED',
        '16': 'MAXIMUM DAC OFFSET EXCEEDED',
        '17': 'ESP CRITICAL SETTINGS ARE PROTECTED',
        '18': 'ESP STAGE DEVICE ERROR',
        '19': 'ESP STAGE DATA INVALID',
        '20': 'HOMING ABORTED',
        '21': 'MOTOR CURRENT NOT DEFINED',
        '22': 'UNIDRIVE COMMUNICATIONS ERROR',
        '23': 'UNIDRIVE NOT DETECTED',
        '24': 'SPEED OUT OF RANGE',
        '25': 'INVALID TRAJECTORY MASTER AXIS',
        '26': 'PARAMETER CHARGE NOT ALLOWED',
        '27': 'INVALID TRAJECTORY MODE FOR HOMING',
        '28': 'INVALID ENCODER STEP RATIO',
        '29': 'DIGITAL I/O INTERLOCK DETECTED',
        '30': 'COMMAND NOT ALLOWED DURING HOMING',
        '31': 'COMMAND NOT ALLOWED DUE TO GROUP',
        '32': 'INVALID TRAJECTORY MODE FOR MOVING'
    }

    def __init__(self, code):
        self.axis = str(code)[0]
        self.error = str(code)[1:]
        self.message = self.MESSAGES[self.error]

    def __str__(self):
        return "Newport ESP300 axis %s reported the error: %s" % (
            self.axis, self.message)

class GeneralError(Exception):
    """ Raised when the Newport ESP300 has a general error.
    """

    MESSAGES = {
        '1': 'PCI COMMUNICATION TIME-OUT',
        '4': 'EMERGENCY SOP ACTIVATED',
        '6': 'COMMAND DOES NOT EXIST',
        '7': 'PARAMETER OUT OF RANGE',
        '8': 'CABLE INTERLOCK ERROR',
        '9': 'AXIS NUMBER OUT OF RANGE',
        '13': 'GROUP NUMBER MISSING',
        '14': 'GROUP NUMBER OUT OF RANGE',
        '15': 'GROUP NUMBER NOT ASSIGNED',
        '17': 'GROUP AXIS OUT OF RANGE',
        '18': 'GROUP AXIS ALREADY ASSIGNED',
        '19': 'GROUP AXIS DUPLICATED',
        '16': 'GROUP NUMBER ALREADY ASSIGNED',
        '20': 'DATA ACQUISITION IS BUSY',
        '21': 'DATA ACQUISITION SETUP ERROR',
        '23': 'SERVO CYCLE TICK FAILURE',
        '25': 'DOWNLOAD IN PROGRESS',
        '26': 'STORED PROGRAM NOT STARTED',
        '27': 'COMMAND NOT ALLOWED',
        '29': 'GROUP PARAMETER MISSING',
        '30': 'GROUP PARAMETER OUT OF RANGE',
        '31': 'GROUP MAXIMUM VELOCITY EXCEEDED',
        '32': 'GROUP MAXIMUM ACCELERATION EXCEEDED',
        '22': 'DATA ACQUISITION NOT ENABLED',
        '28': 'STORED PROGRAM FLASH AREA FULL',
        '33': 'GROUP MAXIMUM DECELERATION EXCEEDED',
        '35': 'PROGRAM NOT FOUND',
        '37': 'AXIS NUMBER MISSING',
        '38': 'COMMAND PARAMETER MISSING',
        '34': 'GROUP MOVE NOT ALLOWED DURING MOTION',
        '39': 'PROGRAM LABEL NOT FOUND',
        '40': 'LAST COMMAND CANNOT BE REPEATED',
        '41': 'MAX NUMBER OF LABELS PER PROGRAM EXCEEDED'
    }

    def __init__(self, code):
        self.error = str(code)
        self.message = self.MESSAGES[self.error]

    def __str__(self):
        return "Newport ESP300 reported the error: %s" % (
            self.message)

class Axis(object):
    """ Represents an axis of the Newport ESP300 Motor Controller,
    which can have independent parameters from the other axes.
    """

    position = Instrument.control(
        "TP", "PA%g",
        """ A floating point property that controls the position
        of the axis. The units are defined based on the actuator.
        Use the :meth:`~.wait_for_stop` method to ensure the position
        is stable.
        """
    )
    enabled = Instrument.measurement(
        "MO?",
        """ Returns a boolean value that is True if the motion for
        this axis is enabled.
        """,
        cast=bool
    )
    left_limit = Instrument.control(
        "SL?", "SL%g",
        """ A floating point property that controls the left software
        limit of the axis. """
    )
    right_limit = Instrument.control(
        "SR?", "SR%g",
        """ A floating point property that controls the right software
        limit of the axis. """
    )
    units = Instrument.control(
        "SN?", "SN%d",
        """ A string property that controls the displacement units of the
        axis, which can take values of: enconder count, motor step, millimeter,
        micrometer, inches, milli-inches, micro-inches, degree, gradient, radian,
        milliradian, and microradian.
        """,
        validator=strict_discrete_set,
        values={
            'encoder count':0, 'motor step':1, 'millimeter':2,
            'micrometer':3, 'inches':4, 'milli-inches':5,
            'micro-inches':6, 'degree':7, 'gradient':8,
            'radian':9, 'milliradian':10, 'microradian':11
        },
        map_values=True
    )
    motion_done = Instrument.measurement(
        "MD?",
        """ Returns a boolean that is True if the motion is finished.
        """,
        cast=bool
    )

    def __init__(self, axis, controller):
        self.axis = str(axis)
        self.controller = controller

    def ask(self, command):
        command = self.axis + command
        return self.controller.ask(command)

    def write(self, command):
        command = self.axis + command
        self.controller.write(command)

    def values(self, command, **kwargs):
        command = self.axis + command
        return self.controller.values(command, **kwargs)

    def enable(self):
        """ Enables motion for the axis. """
        self.write("MO")

    def disable(self):
        """ Disables motion for the axis. """
        self.write("MF")

    def home(self, type=1):
        """ Drives the axis to the home position, which may be the negative
        hardware limit for some actuators (e.g. LTA-HS).
        type can take integer values from 0 to 6.
        """
        home_type = strict_discrete_set(type, [0,1,2,3,4,5,6])
        self.write("OR%d" % home_type)

    def define_position(self, position):
        """ Overwrites the value of the current position with the given
        value. """
        self.write("DH%g" % position)

    def zero(self):
        """ Resets the axis position to be zero at the current poisiton.
        """
        self.write("DH")

    def wait_for_stop(self, delay=0, interval=0.05):
        """ Blocks the program until the motion is completed. A further
        delay can be specified in seconds.
        """
        self.write("WS%d" % (delay*1e3))
        while not self.motion_done:
            sleep(interval)


class ESP300(Instrument):
    """ Represents the Newport ESP 300 Motion Controller
    and provides a high-level for interacting with the instrument.

    By default this instrument is constructed with x, y, and phi
    attributes that represent axes 1, 2, and 3. Custom implementations
    can overwrite this depending on the avalible axes. Axes are controlled
    through an :class:`Axis <pymeasure.instruments.newport.esp300.Axis>`
    class.
    """

    error = Instrument.measurement(
        "TE?",
        """ Reads an error code from the motion controller.
        """,
        cast=int
    )

    def __init__(self, resourceName, **kwargs):
        super(ESP300, self).__init__(
            resourceName,
            "Newport ESP 300 Motion Controller",
            **kwargs
        )
        # Defines default axes, which can be overwritten
        self.x = Axis(1, self)
        self.y = Axis(2, self)
        self.phi = Axis(3, self)

    def clear_errors(self):
        """ Clears the error messages by checking until a 0 code is
        recived. """
        while self.error != 0:
            continue

    @property
    def errors(self):
        """ Returns a list of error Exceptions that can be later raised, or
        used to diagnose the situation.
        """
        errors = []

        code = self.error
        while code != 0:
            if code > 100:
                errors.append(AxisError(code))
            else:
                errors.append(GeneralError(code))
            code = self.error
        return errors

    @property
    def axes(self):
        """ A list of the :class:`Axis <pymeasure.instruments.newport.esp300.Axis>`
        objects that are present. """
        axes = []
        directory = dir(self)
        for name in directory:
            if name == 'axes':
                continue # Skip this property
            try:
                item = getattr(self, name)
                if isinstance(item, Axis):
                    axes.append(item)
            except TypeError:
                continue
            except Exception as e:
                raise e
        return axes

    def enable(self):
        """ Enables all of the axes associated with this controller.
        """
        for axis in self.axes:
            axis.enable()

    def disable(self):
        """ Disables all of the axes associated with this controller.
        """
        for axis in self.axes:
            axis.disable()

    def shutdown(self):
        """ Shuts down the controller by disabling all of the axes.
        """
        self.disable()
