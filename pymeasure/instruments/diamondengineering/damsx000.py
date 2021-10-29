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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from pymeasure.adapters import VISAAdapter
from math import sqrt, sin, cos, radians, degrees, atan

class ZeroPositionNotSet(Exception):
    """Raised when a zero position is required."""
    pass

class Axis(object):
    """ Implementation of a DAMS x000 stepper motor axis."""

    speed_base = Instrument.setting("0B%d",
                                    """ A integer property to set the initial speed in steps/second.
                                    """,
                                    validator=strict_range,
                                    values = (10, 300),
                                   )

    speed_final = Instrument.setting("0E%d",
                                     """ A integer property to set the final speed in steps/second
                                     """,
                                     validator=strict_range,
                                     values = (20, 2000),
                                 )

    speed_slope = Instrument.setting("0S%d",
                                     """ A integer property to set the acceleration slope.
                                     (Recommended values are in the range 1-3)
                                     """,
                                     validator=strict_range,
                                     values = (1, 200),
    )
    
    step_width = Instrument.setting("0%s",
                                    """ A string property to set the step width
                                    """,
                                    validator=strict_discrete_set,
                                    map_values = True,
                                    values = {"FULL": "F",
                                              "HALF": "H"},
                                )

    holding_current = Instrument.setting("0P%d",
                                         """ A string property to set the holding current
                                         """,
                                         validator=strict_discrete_set,
                                         map_values = True,
                                         values = {"ZERO": 2,
                                                   "HALF": 1},
                                     )
    
    step_rel = Instrument.setting("0RN%d",
                                  """ A integer property to start a relative movement for the desired steps
                                  """,
                                  validator=strict_range,
                                  values = (-100000, 100000), # Really no limits
                              )

    angle_min = None # No limit in rotation
    angle_max = None # No limit in rotation

    def __init__(self, instrument, axis_name):
        self.instrument = instrument
        assert((axis_name == 'X') or (axis_name == 'Y'))
        self.axis = axis_name
        self.zero_set = False
        self.current_angle = None

    def set_zero(self, angle=0):
        """ Set the absolute angle to position (0 degree by default)
        
        :param angle: Zero angle in degree
        """
        self.zero_set = True
        self.current_angle = angle

    def write(self, command):
        self.instrument.write("%s%s" % (self.axis, command))

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
        steps = self.degrees2steps(movement_degrees)

        self.step_rel = steps
        self.current_angle += self.steps2degrees(steps)

    def angle_rel(self, degrees):
        steps = self.degrees2steps(degrees)
        self.step_rel = steps
        return steps

    def encoder_enable(self):
        self.write("0qmC")
        self.write("0qN-")
        self.write("0qE")

    def read_encoder(self):
        self.terminal.flush()
        self.write("0qP")
        time.sleep(.030)
        readbuffer = self.terminal.read_all()
        asciibuffer = readbuffer.decode("utf-8")
        print(asciibuffer)

    def read_count(self):
        self.terminal.flush()
        self.write("0m")
        time.sleep(.030)
        readbuffer = self.terminal.read_all()
        asciibuffer = readbuffer.decode("utf-8")
        splitbuffer = asciibuffer.split('>')
        print(splitbuffer[1])
        self.xcount = (splitbuffer[1])

class XAxis(Axis):
    """ Implementation of a DAMS x000 stepper motor X axis (azimuth)."""

    steps_per_meter = 2880
    def degrees2steps(self, degrees):
        """ Translate degrees to steps """
        # TODO: Check that 2880 is OK both for full step and half step
        return (self.steps_per_meter * degrees) / 360

    def steps2degrees(self, steps):
        """ Translate steps to degrees """
        return (360 * steps) / self.steps_per_meter

    def __init__(self, instrument):
        super().__init__(instrument, 'X')

class YAxis(Axis):
    """ Implementation of a DAMS x000 stepper motor Y axis (elevation).
    
    Elevation axis is achieve using a threaded rod that rotates using a stepper motor.
    The elevation can  be moved from -45 degrees to + 45 degrees.
    """

    def inches2m(a):
        return a*0.0254

    x0 = inches2m(-4.2) # X coordinate of motor position
    y0 = inches2m(-3.8) # Y coordinate of motor position
    h =  inches2m(1.7)
    R = inches2m(3.75) # To be verified
    steps_per_meter = 2083/inches2m(1)
    R1 = sqrt(R**2+h**2)
    d0 = sqrt((x0+R)**2+(y0-h)**2)
    offset_angle = degrees(atan(h/R))

    angle_min = -45.1 # Actually it is -45, extra 0.1 is to deal with roundings errors
    angle_max = 45.1 # Actually it is 45, extra 0.1 is to deal with roundings errors

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
        d=sqrt((x1-x0)**2 + (y1-y0)**2)

        a=(r0**2-r1**2+d**2)/(2*d)
        h=sqrt(r0**2-a**2)
        x2=x0+a*(x1-x0)/d   
        y2=y0+a*(y1-y0)/d   
        x3=x2+h*(y1-y0)/d     
        y3=y2-h*(x1-x0)/d 
        
        x4=x2-h*(y1-y0)/d
        y4=y2+h*(x1-x0)/d

        return (x3, y3, x4, y4)

    def degrees2steps(self, degrees):
        """ Steps required to move of degrees from current position """

        # Assume angle is zero, if not set. This is useful to allow
        # movements to center elevation axis
        current_angle = self.current_angle if self.zero_set else 0

         # Check limits if any
        if self.angle_min is not None:
            assert((current_angle+degrees) >= self.angle_min)

        if self.angle_max is not None:
            print ("*", self.current_angle, current_angle, degrees, self.angle_max)
            assert((current_angle+degrees) <= self.angle_max)

        current_angle = radians(current_angle)
        # Calculate current x and y coordinates from current_angle
        R = self.R
        h = self.h

        xs = -R*cos(current_angle)+h*sin(current_angle)
        ys = R*sin(current_angle)+h*cos(current_angle)
        ds = sqrt((xs-self.x0)**2+(ys-self.y0)**2)

        angle = radians(degrees)
        x1 = -R*cos(angle)+h*sin(angle)
        y1 = R*sin(angle)+h*cos(angle)
        d1 = sqrt((x1-self.x0)**2+(y1-self.y0)**2)
        return round((d1-ds) * self.steps_per_meter)

    def steps2degrees(self, steps):
        """ Translate steps to absolute degrees """
        current_angle = self.current_angle if self.zero_set else 0
        current_angle = radians(current_angle)
        # Calculate current x and y coordinates from current_angle
        R = self.R
        h = self.h
        xs = -R*cos(current_angle)+h*sin(current_angle)
        ys = R*sin(current_angle)+h*cos(current_angle)
        x0 = self.x0
        y0 = self.y0
        ds = sqrt((xs-x0)**2+(ys-y0)**2)

        d1 = steps/self.steps_per_meter + ds
        x1,y1,x2,y2 = self.get_intersections(d1)
        angle = -(degrees(atan(y2/x2))+self.offset_angle)

        return angle

    def __init__(self, instrument):
        super().__init__(instrument, 'Y')

class DAMSx000(Instrument):
    """ Represents the DAMS x000 series 2-axis positioner from Diamond Engineering
    """

    def __init__(self, resource_name, **kwargs):
        super().__init__(
            resource_name,
            "DAMS x000",
            timeout=2000,
            write_termination='\r\n',
            includeSCPI=False,
            **kwargs
        )

        if isinstance(self.adapter, VISAAdapter):
            self.adapter.connection.baud_rate = 57600

        self.x = Axis(self, 'X')
        self.y = Axis(self, 'Y')

        # Init controller
        self.write("GG*")
        self.write("GGN+0c")

    @property
    def zero_set(self):
        return self.x.zero_set and self.y.zero_set

    @property
    def azimuth_angle(self):
        return self.x.angle

    @property
    def elevation_angle(self):
        return self.y.angle

    def azimuth(self, degree):
        """ Bring the positioner to absolute azimuth angle """

        self.x.angle = degree
        return self.x.angle

    def azimuth_rel(self, degree):
        """ Move the positioner of degrees relative to current position.
        
        This method may be useful to center the azimuth to zero
        """

        self.x.angle_rel = degree

    def elevation(self, degree):
        """ Bring the positioner to absolute elevation angle (range -45, 45) """
        self.y.angle = degree
        return self.y.angle

    def elevation_rel(self, degree):
        """ Move the positioner of degrees relative to current position.
        
        This method may be useful to center the elevation to zero
        """
        self.y.angle_rel = degree

    def set_zero_position(self):
        self.x.set_zero()
        self.y.set_zero()
