# -*- coding: utf-8 -*-
"""
Created the 19/06/2023

@author: Sebastien Weber
"""
from pymeasure.instruments import Instrument, Channel
import logging
from typing import Union, List
from collections.abc import Sequence

from pymeasure.instruments.thorlabs.elliptec_utils.tools import parse
from pymeasure.instruments.thorlabs.elliptec_utils.errors import error_codes, StatusError, ExternalDeviceNotFound
from pymeasure.instruments.thorlabs.elliptec_utils.cmd import get_, set_, mov_


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class MotorChannel(Channel):
    """A channel of the elliptec multichannel controller."""

    units = 'steps'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.info = None
        self.range = None
        self.pulse_per_rev = None
        self.serial_no = None
        self.motor_type = None

    def check_set_errors(self, *args, **kwargs):
        error_code = parse(self.read())[2]
        if error_code != '0':
            return StatusError(error_codes[error_code])
        else:
            return []

    def insert_id(self, command):
        return f"{self.id}{command}"

    idn = Instrument.measurement("in",
                                 """ Get the Motor identification """,
                                 get_process=lambda x: parse(x),
                                 )

    # address = Instrument.control('in',
    #                              'ca%s',
    #                              """ Set the Motor Address """,
    #                              get_process=lambda x: int(parse(x)['Address']),
    #                              set_process=lambda v: MotorChannel.int_to_hex(v),
    #                              check_set_errors=True,
    #                              )
    status = Instrument.measurement('gs',
                                    """ Get Motor error""",
                                    get_process=lambda x: int(parse(x)[2]),
                                    )

    position = Instrument.measurement("gp",
                                      """ Get Motor Position in specified units """,
                                      get_process=lambda x: parse(x)[2],
                                      )

    step_size = Instrument.control("gj",
                                   "sj%s",
                                   """ Control the motor step size""",
                                   get_process=lambda x: parse(x)[2],
                                   set_process=lambda v: MotorChannel.int_to_hex(v),
                                   check_set_errors=True,
                                   )

    home_offset = Instrument.control("go",
                                     "so%s",
                                     """ Control the motor home offset""",
                                     get_process=lambda x: parse(x)[2],
                                     set_process=lambda v: MotorChannel.int_to_hex(v),
                                     check_set_errors=True,
                                     )

    def load_motor_info(self):
        info = self.idn
        if info is None:
            raise ExternalDeviceNotFound
        else:
            self.info = info

            self.range = self.info['Range']
            self.pulse_per_rev = self.info['Pulse/Rev']
            self.serial_no = self.info['Serial No.']
            self.motor_type = self.info['Motor Type']

    def home(self, direction: str = 'forward'):
        if direction == 'forward':
            self.ask('ho0')
        else:
            self.ask('ho1')

    def move(self, position: int, move_type: str = 'abs'):
        """Move the MotorChannel to an absolute or relative position in steps
        """
        if move_type == 'abs':
            command = 'ma'
        else:
            command = 'mr'
        command += self.int_to_hex(position)
        ret = self.ask(command)

    @staticmethod
    def int_to_hex(number: int):
        return number.to_bytes(4, "big", signed=True).hex().upper()


class Motor(Instrument):
    """An Elliptec Motor with added channels."""

    def __init__(self, adapter, name="Elliptec Rotator", adress:Union[int, List] = 0, **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs)

        if not isinstance(adress, Sequence):
            adress = [adress]

        for ad in adress:
            self.add_child(MotorChannel, str(ad))

    def load_motor_info(self, address: int = 0):
        """ Asks motor for info and load response into properties other methods can check later. """
        self.channels[str(address)].load_motor_info()


if __name__ == '__main__':
    rot = Motor('ASRL19::INSTR')
    print(rot.channels['0'].idn)
    rot.channels['0'].move(45, 'abs')
    rot.channels['0'].step_size = 10000
    rot.clear()
