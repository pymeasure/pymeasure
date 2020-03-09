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
import time

import serial

from .serial import SerialAdapter


class PrologixAdapter(SerialAdapter):
    """ Encapsulates the additional commands necessary
    to communicate over a Prologix GPIB-USB Adapter,
    using the SerialAdapter.

    Each PrologixAdapter is constructed based on a serial port or
    connection and the GPIB address to be communicated to.
    Serial connection sharing is achieved by using the :meth:`.gpib`
    method to spawn new PrologixAdapters for different GPIB addresses.

    :param port: The Serial port name or a serial.Serial object
    :param address: Integer GPIB address of the desired instrument
    :param rw_delay: An optional delay to set between a write and read call for slow to respond instruments.
    :param kwargs: Key-word arguments if constructing a new serial object

    :ivar address: Integer GPIB address of the desired instrument

    To allow user access to the Prologix adapter in Linux, create the file:
    :code:`/etc/udev/rules.d/51-prologix.rules`, with contents:

    .. code-block:: bash

        SUBSYSTEMS=="usb",ATTRS{idVendor}=="0403",ATTRS{idProduct}=="6001",MODE="0666"

    Then reload the udev rules with:

    .. code-block:: bash

        sudo udevadm control --reload-rules
        sudo udevadm trigger

    """

    def __init__(self, port, address=None, rw_delay=None, serial_timeout = 0.5, **kwargs):
        super().__init__(port, timeout = serial_timeout, **kwargs)
        self.address = address
        self.rw_delay = rw_delay
        if not isinstance(port, serial.Serial):
            self.set_defaults()

    def set_defaults(self):
        """ Sets up the default behavior of the Prologix-GPIB
        adapter
        """
        self.write("++auto 0")  # Turn off auto read-after-write
        self.write("++eoi 1")  # Append end-of-line to commands
        self.write("++eos 2")  # Append line-feed to commands

    def ask(self, command):
        """ Ask the Prologix controller, include a forced delay for some instruments.

        :param command: SCPI command string to be sent to instrument
        """

        self.write(command)
        if self.rw_delay is not None:
            time.sleep(self.rw_delay)
        return self.read()

    def write(self, command):
        """ Writes the command to the GPIB address stored in the
        :attr:`.address`

        :param command: SCPI command string to be sent to the instrument
        """
        if self.address is not None:
            address_command = "++addr %d\n" % self.address
            self.connection.write(address_command.encode())
        command += "\n"
        self.connection.write(command.encode())

    def read(self):
        """ Reads the response of the instrument until timeout

        :returns: String ASCII response of the instrument
        """
        self.write("++read eoi")
        return b"\n".join(self.connection.readlines()).decode()

    def gpib(self, address, rw_delay=None):
        """ Returns and PrologixAdapter object that references the GPIB
        address specified, while sharing the Serial connection with other
        calls of this function

        :param address: Integer GPIB address of the desired instrument
        :param rw_delay: Set a custom Read/Write delay for the instrument
        :returns: PrologixAdapter for specific GPIB address
        """
        rw_delay = rw_delay or self.rw_delay
        return PrologixAdapter(self.connection, address, rw_delay=rw_delay)

    def wait_for_srq(self, timeout=25, delay=0.1):
        """ Blocks until a SRQ, and leaves the bit high

        :param timeout: Timeout duration in seconds
        :param delay: Time delay between checking SRQ in seconds
        """
        while int(self.ask("++srq")) != 1:  # TODO: Include timeout!
            time.sleep(delay)

    def __repr__(self):
        if self.address is not None:
            return "<PrologixAdapter(port='%s',address=%d)>" % (
                self.connection.port, self.address)
        else:
            return "<PrologixAdapter(port='%s')>" % self.connection.port
