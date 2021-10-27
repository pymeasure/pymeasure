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
from math import sqrt, sin, cos, radians

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
                                    validator=strict_set,
                                    map_values = True,
                                    values = {"FULL": "F",
                                              "HALF": "H"},
                                )

    holding_current = Instrument.setting("0P%d",
                                         """ A string property to set the holding current
                                         """,
                                         validator=strict_set,
                                         map_values = True,
                                         values = {"ZERO": 2,
                                                   "HALF": 1},
                                     )
    
    step_rel = Instrument.setting("0RN%d",
                                  """ A integer property to start a relative movement for the desired steps
                                  """,
                                  validator=strict_range,
                                  values = (-2880, 2880),
                              )

    def __init__(self, instrument, axis, X0=None, Y0=None, H=None):
        self.instrument = instrument
        assert((axis == 'X') or (axis == 'Y'))
        self.axis = axis
        if self.axis == 'Y':
            self.x0 = X0
            self.y0 = Y0
            self.h = H

    def write(self, command):
        self.instrument.write("%s%s" % (self.axis, command))

    def degree2step(self, degrees):
        """ Translate degrees to steps for the specific axis """
        if self.axis == 'X':
            # TODO: Check that 2880 is OK both for full step and half step
            return (2880 * degrees) / 360
        elif self.axis == 'Y':
            raise Exception("Not implemented")
            h = self.h
            R = self.R
            x0 = self.x0
            angle = radians(degrees)
            step = sqrt(((-R*cos(angle)+h*sin(angle)-x0)**2+((R*sin(angle)+h*cos(angle))-y0)**2)-sqrt((x0+R)**2+y0**2)

    def step2degree(self, steps):
        """ Translate steps to degrees for the specific axis """
        if self.axis == 'X':
            return (360 * steps) / 2880
        elif self.axis == 'Y':
            raise Exception("Not implemented")

class DAMSx000(Instrument):
    """ Represents the DAMS x000 series 2-axis positioner from Diamond Engineering
    """

    X0 = -4.2*0.0254 # In meters
    Y0 = -3.8*0.0254 # In meters
    H =  1.7**0.0254 # In meters

    def __init__(self, resource_name, **kwargs):
        super().__init__(
            resource_name,
            "DAMS x000",
            timeout=2000,
            write_termination='\r\n',
            includeSCPI=False,
            radius =
            h = 0.04318, # 1.7 inches in meters
            **kwargs
        )

        if isinstance(self.adapter, VISAAdapter):
            self.adapter.connection.baud_rate = 57600

        self.x = Axis(self, 'X')
        self.y = Axis(self, 'Y')

        # Init controller
        self.write("GG*")
        self.write("GGN+0c")
        self.zero_set = False

    def azimut(self, degree):
        """ Bring the positioner to absolute azimuth angle """

        if (not self.zero_set):
            raise Exception ("Zero position not set")

        movement_degree = (degree - self.azimut_angle) % 360
        steps = self.x.degree2step(movement_degree))

        self.x.step_rel = steps
        self.azimut_angle += self.x.step2degree(steps)

        return self.azimut_angle

    def elevation(self, degree):
        """ Bring the positioner to absolute elevation angle (range -45, 45) """
        if (not self.zero_set):
            raise Exception ("Zero position not set")

        assert ((degree >= -45) and (degree <= 45))

        movement_degree = (degree - self.azimut_angle) % 360
        steps = self.y.degree2step(movement_degree))

        self.y.step_rel = steps
        self.elevation_angle += self.y.step2degree(steps)

        return self.elevation_angle

    def set_zero_position(self):
        self.azimut_angle = 0
        self.elevation_angle = 0
        self.zero_set = True
