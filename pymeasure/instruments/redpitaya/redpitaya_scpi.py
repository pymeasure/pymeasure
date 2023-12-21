import datetime

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import modular_range, truncated_discrete_set, truncated_range, strict_discrete_set

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DigitalChannel(Channel):
    """A base class for a Digital line on the board"""

    def insert_id(self, command):
        raise NotImplementedError

    direction = Channel.control(
        ":DIR?", ":DIR %s",
        """ Control a digital line to the given direction (str either 'IN' or 'OUT')""",
        validator=truncated_discrete_set,
        values=['IN', 'OUT'],
    )

    state = Channel.control(
        "?", " ,%d",
        """ Control the state of the line (bool)""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )


class DigitalChannelN(DigitalChannel):
    """ A digital line of the N type"""
    def insert_id(self, command):
        return f"DIG:PIN{command},DIO{self.id}_N"


class DigitalChannelP(DigitalChannel):
    """ A digital line of the P type"""
    def insert_id(self, command):
        return f"DIG:PIN{command},DIO{self.id}_P"


class DigitalChannelLed(DigitalChannel):
    """ A LED digital line (Output only)"""

    def insert_id(self, command):
        return f"DIG:PIN{command},LED{self.id}"


class RedPitayaScpi(Instrument):
    """This is the class for the Redpitaya reconfigurable board

    The instrument is accessed using a TCP/IP Socket communication, that is an adapter in the form:
    "TCPIP::x.y.z.k::port::SOCKET" where x.y.z.k is the IP address of the SCPI server
    (that should be activated on the board) and port is the TCP/IP port number, usually 5000

    :parameter

    """

    def __init__(self, ip_address: str, port: int = 5000, name="Redpitaya SCPI",
                 read_termination='\r\n',
                 write_termination='\r\n',
                 **kwargs):

        adapter = f"TCPIP::{ip_address}::{port}::SOCKET"

        super().__init__(
            adapter,
            name,
            read_termination=read_termination,
            write_termination=write_termination,
            **kwargs)

    time = Instrument.control("SYST:TIME?",
                              "SYS:TIME %s",
                              """Control the time on board
                              time should be given as a datetime.time object""",
                              get_process=lambda tstr: datetime.time(*[int(split) for split in tstr.split(',')]),
                              set_process=lambda time: time.strftime('%H,%M,%S'),
                              )

    date = Instrument.control("SYST:DATE?",
                              "SYS:DATE %s",
                              """Control the date on board
                              date should be given as a datetime.date object""",
                              get_process=lambda dstr: datetime.date(*[int(split) for split in dstr.split(',')]),
                              set_process=lambda date: date.strftime('%Y,%m,%d'),
                              )

    name = Instrument.measurement("SYST:BRD:Name?",
                                  """Get the RedPitaya board name""")

    def digital_reset(self):
        """Reset the state of all digital lines"""
        self.write("DIG:RST")

    digitalN = Instrument.MultiChannelCreator(DigitalChannelN, list(range(7)), prefix='dioN')

    digitalP = Instrument.MultiChannelCreator(DigitalChannelN, list(range(7)), prefix='dioN')

    led = Instrument.MultiChannelCreator(DigitalChannelLed, list(range(7)), prefix='led')

    # ANALOG SECTION

    def analog_reset(self):
        """ Reset the voltage of all analog channels """
        self.write("ANALOG:RST")

    # ACQUISITION SECTION

    def acquisition_start(self):
        self.write("ACQ:START")

    def acquisition_stop(self):
        self.write("ACQ:STOP")

    def acquisition_reset(self):
        self.write("ACQ:RST")


if __name__ == '__main__':
    rp = RedPitayaScpi(ip_address='169.254.134.87', port=5000)
    rp.time
    rp.clear()