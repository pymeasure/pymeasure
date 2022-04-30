#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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
from math import sqrt, sin, cos, radians, degrees, atan

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ZeroPositionNotSet(Exception):
    """Raised when a zero position is required."""
    pass


class Axis(object):
    """ Implementation of a DAMS x000 stepper motor axis."""

    speed_base = Instrument.setting(
        "0B%d",
        """ A integer property to set the initial speed in steps/second.
        """,
        validator=strict_range,
        values=(10, 500),
        dynamic=True
    )

    speed_final = Instrument.setting(
        "0E%d",
        """ A integer property to set the final speed in steps/second
        """,
        validator=strict_range,
        values=(20, 2000),
        dynamic=True
    )

    speed_slope = Instrument.setting(
        "0S%d",
        """ A integer property to set the acceleration slope.
        (Recommended values are in the range 1-3)
        """,
        validator=strict_range,
        values=(1, 200),
        dynamic=True
    )

    step_width = Instrument.setting(
        "0%s",
        """ A string property to set the step width
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={"FULL": "F",
                "HALF": "H"},
    )

    holding_current = Instrument.setting(
        "0P%d",
        """ A string property to set the holding current
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={"ZERO": 2,
                "HALF": 1},
    )

    step_rel = Instrument.setting(
        "0RN%+d",
        """ A integer property to start a relative movement for the desired steps """,
        validator=strict_range,
        values=(-100000, 100000),  # Really no limits
    )

    angle_min = None  # No limit in rotation
    angle_max = None  # No limit in rotation

    @property
    def angle(self):
        """ Return current absolute angle position """

        if (not self.zero_set):
            raise ZeroPositionNotSet("Zero position not set")

        return self.current_angle

    @angle.setter
    def angle(self, degrees):
        """ Move to absolute angle position """

        if (not self.zero_set):
            raise ZeroPositionNotSet("Zero position not set")

        movement_degrees = (degrees - self.current_angle)
        steps = self.angle_rel(movement_degrees)
        self.current_angle += self.steps2degrees(steps)
        if self.wrap:
            self.current_angle %= 360

    def __init__(self, instrument, axis_name, wrap):
        self.instrument = instrument
        assert((axis_name == 'X') or (axis_name == 'Y'))
        self.axis = axis_name
        self.zero_set = False
        self.current_angle = None
        self.wrap = wrap

    def set_zero(self, angle=0):
        """ Set the absolute angle to position (0 degree by default)

        :param angle: Zero angle in degree
        """
        self.zero_set = True
        self.current_angle = angle

    def write(self, command):
        if command == ("0RN+0") or command == ("0RN-0"):
            expected_responses = [f'{self.axis}0!']
        if command.startswith("0RN"):
            expected_responses = [f'{self.axis}0b', f'{self.axis}0f']
        elif command.startswith("0"):
            expected_responses = [f'{self.axis}0>']
        else:
            expected_responses = []

        self.instrument.write("%s%s" % (self.axis, command))
        for response in expected_responses:
            actual_response = self.instrument.read()
            if actual_response != response:
                raise Exception(f'Expected response "{response}" but got "{actual_response}"')

    def steps2degrees(self, steps):
        """ Translate steps to angle expressed in degrees

        :param steps: motor steps
        :return: angle movement from current position in degrees
        """
        raise NotImplementedError("Subclasses should implement this method")

    def degrees2steps(self, degrees):
        """ Translate angle movement from current position to motor steps

        :param degrees: Relative angle from current position in degrees

        :return: the actual angle expressed in degrees of movement after rounding with motor steps
        """
        raise NotImplementedError("Subclasses should implement this method")

    def angle_rel(self, degrees):
        steps = self.degrees2steps(degrees)
        self.step_rel = steps
        return steps


class XAxis(Axis):
    """ Implementation of a DAMS x000 stepper motor X axis (azimuth)."""

    steps_per_full_revolution = 2880  # 360 degree revolution

    def degrees2steps(self, degrees):
        # TODO: Check that 2880 is OK both for full step and half step
        degrees = degrees % 360
        if (abs(degrees) > 180):
            degrees = degrees - 360
        return round((self.steps_per_full_revolution * degrees) / 360)

    def steps2degrees(self, steps):
        return (360 * steps) / self.steps_per_full_revolution

    def __init__(self, instrument):
        prefix = Instrument._Instrument__reserved_prefix
        setattr(self, prefix + 'speed_base_values', (10, 300))
        setattr(self, prefix + 'speed_final_values', (20, 600))
        setattr(self, prefix + 'speed_slope_values', (1, 3))
        super().__init__(instrument, 'X', wrap=True)


class YAxis(Axis):
    """ Implementation of a DAMS x000 stepper motor Y axis (elevation).

    Elevation axis is achieved using a threaded rod that rotates using a stepper motor.
    The elevation can  be moved from -45 degrees to + 45 degrees.
    The number of steps are calculated using formula derived from the following picture.

.. image:: elevation-diagram.png
    :alt: Elevation diagram


Picture details are as follow:

    - Positioner is observed from side
    - (0, 0) are the coordinates of the elevation rotation axis
    - (|x0|, |y0|) are the coordinates of the motor axis
    - |d0| is the distance of (|x0|, |y0|) to coordinates (-R, h), that is
      the rod length when plate is in horizontal position
    - (|x1|, |y1|) are the coordinated of the rod joint with bottom plate for
      an arbitrary angle :math:`{\\alpha}`
    - |d1| is the distance of (|x0|, |y0|) to coordinates (|x1|, |y1|), that
      is the rod length when plate is in forming an angle :math:`{\\alpha}` with
      horizontal plane
    - :math:`{\\alpha}` is an arbitrary angle with horizontal plane
    - R is the distance of the rod joint with bottom plate to the center of the positioner
    - h is the distance of rotation axis from the center of the positioner
    - the two circles represent the circle of arbitrary radius |d1| and center
      (|x0|, |y0|) and the circle of radius :math:`\\sqrt {R^2 + h^2}` and
      center (0, 0)

.. |d0| replace:: d :sub:`0`
.. |d1| replace:: d :sub:`1`
.. |x0| replace:: x :sub:`0`
.. |x1| replace:: x :sub:`1`
.. |y0| replace:: y :sub:`0`
.. |y1| replace:: y :sub:`1`

    """

    def inches2m(a):
        return a*0.0254

    x0 = inches2m(-3.95)  # X coordinate of motor position
    y0 = inches2m(-4.4)  # Y coordinate of motor position
    h = inches2m(1.83)
    R = inches2m(3.85)
    steps_per_meter = 2*2083/inches2m(1)
    R1 = sqrt(R**2+h**2)
    d0 = sqrt((x0+R)**2+(y0-h)**2)
    offset_angle = degrees(atan(h/R))

    angle_min = -45.1  # Actually it is -45, extra 0.1 is to deal with roundings errors
    angle_max = 45.1  # Actually it is 45, extra 0.1 is to deal with roundings errors

    def distance(self, x1, y1, x2, y2):
        """ Compute distance between two points """
        return sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def get_intersections(self, r_motor):
        """ return point of intersection between two circles """
        # circle 1: (x0, y0), radius r_motor
        # circle 2: (0, 0), radius R1

        # Copy to convenience variables
        x0 = self.x0
        y0 = self.y0
        r0 = r_motor
        x1 = 0
        y1 = 0
        r1 = self.R1

        # Center distance
        d = self.distance(x1, y1, x0, y0)

        a = (r0**2-r1**2+d**2)/(2*d)
        h = sqrt(r0**2-a**2)
        x2 = x0+a*(x1-x0)/d
        y2 = y0+a*(y1-y0)/d
        x3 = x2+h*(y1-y0)/d
        y3 = y2-h*(x1-x0)/d

        x4 = x2-h*(y1-y0)/d
        y4 = y2+h*(x1-x0)/d

        return (x3, y3, x4, y4)

    def degrees2steps(self, degrees):
        # Assume angle is zero, if not set. This is useful to allow
        # relative movements to center elevation axis
        angle = self.current_angle if self.zero_set else 0

        # Check limits if any
        if self.angle_min is not None:
            assert((angle+degrees) >= self.angle_min)

        if self.angle_max is not None:
            assert((angle+degrees) <= self.angle_max)

        angle_rad = radians(angle)
        # Calculate current x and y coordinates from current_angle
        R = self.R
        h = self.h

        xs = -R*cos(angle_rad)+h*sin(angle_rad)
        ys = R*sin(angle_rad)+h*cos(angle_rad)
        ds = self.distance(xs, ys, self.x0, self.y0)

        new_angle_rad = radians(degrees + angle)
        x1 = -R*cos(new_angle_rad)+h*sin(new_angle_rad)
        y1 = R*sin(new_angle_rad)+h*cos(new_angle_rad)
        d1 = self.distance(x1, y1, self.x0, self.y0)
        return round((ds-d1) * self.steps_per_meter)

    def steps2degrees(self, steps):

        # Assume angle is zero, if not set. This is useful to allow
        # relative movements to center elevation axis
        angle = self.current_angle if self.zero_set else 0
        angle_rad = radians(angle)
        # Calculate current x and y coordinates from current_angle
        R = self.R
        h = self.h
        xs = -R * cos(angle_rad) + h * sin(angle_rad)
        ys = R * sin(angle_rad) + h * cos(angle_rad)
        ds = self.distance(xs, ys, self.x0, self.y0)

        d1 = -steps/self.steps_per_meter + ds
        x1, y1, x2, y2 = self.get_intersections(d1)
        new_angle = -(degrees(atan(y2/x2))+self.offset_angle)

        return new_angle - angle

    def __init__(self, instrument):
        prefix = Instrument._Instrument__reserved_prefix
        setattr(self, prefix + 'speed_base_values', (10, 500))
        setattr(self, prefix + 'speed_final_values', (20, 1200))
        setattr(self, prefix + 'speed_slope_values', (1, 3))
        super().__init__(instrument, 'Y', wrap=False)


class DAMSx000(Instrument):
    """ Represents the DAMS x000 series 2-axis positioner from Diamond Engineering
    """

    def __init__(self, resource_name, debug=False, **kwargs):
        super().__init__(
            resource_name,
            "DAMS x000",
            timeout=5000,
            write_termination='\r',
            read_termination='\r',
            baud_rate=57600,
            includeSCPI=False,
            **kwargs
        )
        self.debug = debug

        self.x = XAxis(self)
        self.y = YAxis(self)

        # Init controller
        self.write("GG*")
        self.write("GGN+0cz")

    @property
    def zero_set(self):
        """ This property return True, if the reference position has been set.

        See also :meth:`set_zero_position`

        """
        return self.x.zero_set and self.y.zero_set

    @property
    def azimuth(self):
        """ This property allows to set and read the absolute azimuth position in degrees.

        An exception `ZeroPositionNotSet` is raised if the reference position has not been set

        See also :meth:`set_zero_position`
        """
        return self.x.angle

    @azimuth.setter
    def azimuth(self, degrees):
        self.x.angle = degrees

    @property
    def elevation(self):
        """ This property allows to set and read the absolute elevation position in degrees.

        An exception `ZeroPositionNotSet` is raised if the reference position has not been set.

        See also :meth:`set_zero_position`
        """
        return self.y.angle

    @elevation.setter
    def elevation(self, degrees):
        self.y.angle = degrees

    def azimuth_rel(self, degree):
        """ Move the positioner azimuth angle relative to current position.

        This method may be useful to center the azimuth to zero.

        See also :meth:`set_zero_position`

        :param degree: angle in degrees
        """

        self.x.angle_rel(degree)

    def elevation_rel(self, degree):
        """ Move the positioner elevation angle relative to current position.

        This method may be useful to center the elevation to zero.

        See also :meth:`set_zero_position`

        :param degree: angle in degrees
        """
        self.y.angle_rel(degree)

    def set_zero_position(self):
        """ Set current position to zero degrees both for azimuth and elevation

        See also :meth:`elevation_rel` and :meth:`azimuth_rel`
        """
        self.x.set_zero()
        self.y.set_zero()

    def write(self, command):
        """ Wrapper method for
        :meth:`Instrument.write <pymeasure.instruments.Instrument.write>`
        method to allow logging debug information """
        if self.debug:
            log.debug("=>{}".format(command))
        return super().write(command)
