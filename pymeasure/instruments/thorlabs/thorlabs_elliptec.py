# -*- coding: utf-8 -*-
"""
Created the 15/06/2023

@author: Sebastien Weber
"""
from pymeasure.instruments import Instrument
from pymeasure.instruments.thorlabs.elliptec_utils.tools import parse
from pymeasure.instruments.thorlabs.elliptec_utils.base import MotorChannel, ElliptecController

import logging


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class RotatorChannel(MotorChannel):
    units = 'degree'

    position = Instrument.control("gp",
                                  "ma%s",
                                  """ Control Rotator Position in degrees """,
                                  dynamic=True,
                                  )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position_get_process = lambda x: self.pos_to_angle(parse(x)[2])
        self.position_set_process = lambda x: self.int_to_hex(self.angle_to_pos(x))

    def pos_to_angle(self, posval):
        """ Convert a position in steps to an angle in degrees """
        angle = posval / self.pulse_per_rev * self.range
        angle_rounded = round(angle, 4)
        return angle_rounded

    def angle_to_pos(self, angleval):
        """ Convert an angle in degrees to a position in steps """
        position = int(angleval / self.range * self.pulse_per_rev)
        return position

    def move(self, angle: float, move_type: str = 'abs') -> float:
        """Move the RotatorChannel to an absolute or relative angle in degrees
        """
        if move_type == 'abs':
            command = 'ma'
        else:
            command = 'mr'
        command += self.int_to_hex(self.angle_to_pos(angle))
        ret = self.pos_to_angle(parse(self.ask(command))[2])
        return ret


class LinearChannel(MotorChannel):
    units = 'mm'

    position = Instrument.control("gp",
                                  "ma%s",
                                  """ Control Linear Channel position in millimeters """,
                                  dynamic=True,
                                  )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position_get_process = lambda x: self.pos_to_dist(parse(x)[2])
        self.position_set_process = lambda x: self.int_to_hex(self.dist_to_pos(x))

    def pos_to_dist(self, position):
        """ Converts position in pulses to distance in millimeters. """
        pulse_range = self.pulse_per_rev * self.range
        distance = position / pulse_range * self.range
        distance_rounded = round(distance, 4)
        return distance_rounded

    def dist_to_pos(self, distance):
        """ Converts distance in millimeters to position in pulses. """
        pulse_range = self.pulse_per_rev * self.range
        position = int(distance / self.range * pulse_range)
        return position

    def move(self, position: float, move_type: str = 'abs') -> float:
        """Move the LinearChannel to an absolute or relative position in millimeters
        """
        if move_type == 'abs':
            command = 'ma'
        else:
            command = 'mr'
        command += self.int_to_hex(self.dist_to_pos(position))
        ret = self.pos_to_dist(parse(self.ask(command))[2])
        return ret


if __name__ == '__main__':
    rot = ElliptecController('ASRL19::INSTR', klass=RotatorChannel, address=0)
    print(rot.channels['0'].idn)
    rot.channels['0'].move(45, 'abs')
    rot.channels['0'].position = 180
    rot.close()

