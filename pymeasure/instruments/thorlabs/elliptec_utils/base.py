# -*- coding: utf-8 -*-
"""
Created the 19/06/2023

@author: Sebastien Weber

Set Of base class to interact with elliptec Thorlabs Motor Controller and any piezo motors. The basic MotorChannel
(with units as steps)
can then be inherited to produce some real physical quantities motors: LinearChannel, RotatorChannel with units as mm
and degrees

"""
from pyvisa.errors import VisaIOError

from pymeasure.instruments import Instrument, Channel
import logging
from typing import Union, List
from collections.abc import Sequence

from pymeasure.instruments.thorlabs.elliptec_utils.tools import parse, int_to_hex
from pymeasure.instruments.thorlabs.elliptec_utils.errors import error_codes, StatusError, ExternalDeviceNotFound

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
        """ Format the channel id as a direct channel integer as a string"""
        return f"{self.id}{command}"

    idn = Instrument.measurement("in",
                                 """ Get the Motor identification as a dictionary""",
                                 get_process=lambda x: parse(x),
                                 )

    address = Instrument.control('in',
                                 'ca%s',
                                 """ Control the Motor Address when using multichannel controller""",
                                 get_process=lambda x: int(parse(x)['Address']),
                                 set_process=lambda v: MotorChannel.int_to_hex(v),
                                 check_set_errors=True,
                                 )

    status = Instrument.measurement('gs',
                                    """ Get Motor error status """,
                                    get_process=lambda x: int(parse(x)[2]),
                                    )

    position = Instrument.control("gp",
                                  "ma%s",
                                  """ Control Motor Position in specified units """,
                                  get_process=lambda x: parse(x)[2],
                                  set_process=lambda v: MotorChannel.int_to_hex(v),
                                  )

    step_size = Instrument.control("gj",
                                   "sj%s",
                                   """ Control the motor step size for jogging """,
                                   get_process=lambda x: parse(x)[2],
                                   set_process=lambda v: MotorChannel.int_to_hex(v),
                                   check_set_errors=True,
                                   )

    home_offset = Instrument.control("go",
                                     "so%s",
                                     """ Control the motor home offset """,
                                     get_process=lambda x: parse(x)[2],
                                     set_process=lambda v: MotorChannel.int_to_hex(v),
                                     check_set_errors=True,
                                     )

    def load_motor_info(self):
        """ Get the identification of the Motor and initialize some relevant attributes

        Attributes are needed for physical units from steps (for Rotator or Linear Channel for instance)
        """
        info = self.idn
        if info is None:
            raise ExternalDeviceNotFound
        else:
            self.info = info

            self.range = self.info['Range']
            self.pulse_per_rev = self.info['Pulse/Rev']
            self.serial_no = self.info['Serial No.']
            self.motor_type = self.info['Motor Type']

    def home(self, direction: str = 'forward') -> None:
        """ Homing forward or backward

        :param direction:
        """
        if direction == 'forward':
            self.ask('ho0')
        else:
            self.ask('ho1')

    def move(self, position: int, move_type: str = 'abs') -> None:
        """ Move the MotorChannel to an absolute or relative position in steps

        :param position: value to move in steps
        :param move_type: either 'abs' for an absolute move or something else for relative move
        """
        if move_type == 'abs':
            command = 'ma'
        else:
            command = 'mr'
        command += self.int_to_hex(position)
        self.ask(command)

    @staticmethod
    def int_to_hex(number: int):
        """ Convert integer to uppercase hexadecimal character """
        return int_to_hex(number)


class ElliptecController(Instrument):
    """ An Elliptec Controller adding motor channels at given addresses

    :arg channels: dictionary mapping from an integer as a string ('0', '1', ...) to a MotorChannel or inherited
    objects
    """

    def __init__(self, adapter, name="Elliptec Rotator", klass=MotorChannel, address: Union[int, List] = 0, **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs)

        if address is not None:
            self.add_motor_channel(klass, address)

    def add_motor_channel(self, klass=MotorChannel, address: Union[int, List] = 0):
        """ Add one or several MotorChannel instance (or subclassed) with a given address to the Motor channels

        :param klass: A MotorChannel object or any inherited Motor (LinearChannel, RotatorChannel...)
        :param address: integer or list of integer as Motor address
        """
        if not isinstance(address, Sequence):
            address = [address]

        for ad in address:
            self.add_child(klass, str(ad))
            try:
                self.load_motor_info()
            except VisaIOError:
                raise ExternalDeviceNotFound

    def load_motor_info(self, address: int = 0):
        """ Asks motor for info and load response into properties """
        self.channels[str(address)].load_motor_info()

    def close(self):
        """ Close the adapter communication, here the COM port"""
        try:
            self.adapter.close()
        except:
            pass


def scan_for_devices(adapter, start_address=0, stop_address=0):
    """ Scan for valid addresses at the given ElliptecController

    :param adapter: Visa Adapter
    :param start_address: scan from an address integer
    :param stop_address: scan up to an address integer
    """
    channels = []
    motor = ElliptecController(adapter, address=None)
    for address in range(start_address, stop_address+1):
        try:
            motor.add_motor_channel(address=address)
            channels.append(address)
        except ExternalDeviceNotFound:
            pass
    motor.adapter.close()
    return channels


if __name__ == '__main__':

    channels = scan_for_devices('ASRL19::INSTR', 0, 3)

    rot = ElliptecController('ASRL19::INSTR', address=0)
    print(rot.channels['0'].idn)
    rot.channels['0'].move(45, 'abs')
    rot.channels['0'].step_size = 10000
    rot.close()
