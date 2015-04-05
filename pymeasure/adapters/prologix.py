"""

This file is part of the PyMeasure package.

Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from adapter import Adapter

import serial
import numpy as np


class PrologixAdapter(SerialAdapter):
    """ Encapsulates the additional commands necessary
    to communicate over a Prologix GPIB-USB Adapter and
    implements the IConnection interface
    
    To allow user access to the Prologix adapter in Linux, create the file:
    /etc/udev/rules.d/51-prologix.rules, with contents:
    
    SUBSYSTEMS=="usb",ATTRS{idVendor}=="0403",ATTRS{idProduct}=="6001",MODE="0666"
    
    Then reload the udev rules with:
    sudo udevadm control --reload-rules
    sudo udevadm trigger
        
    """
    def __init__(self, port, address=None, **kwargs):
        self.address = address
        if isinstance(port, serial.Serial):
            # A previous adapter is sharing this connection
            self.connection = port
        else:
            # Construct a new connection
            self.connection = serial.Serial(port, 9600, timeout=0.5, **kwargs)
            self.connection.open()
            self.setDefaults()

    def setDefaults(self):
        self.write("++auto 0") # Turn off auto read-after-write
        self.write("++eoi 1") # Append end-of-line to commands
        self.write("++eos 2") # Append line-feed to commands

    def __del__(self):
        if self.connection.isOpen():
            self.connection.close()

    def write(self, command):
        if self.address is not None:
            self.connection.write("++addr %d\n" % self.address)
        self.connection.write(command + "\n")
        
    def read(self):
        """ Reads until timeout """
        self.write("++read")
        return "\n".join(self.connection.readlines())
        
    def gpib(self, gpib_address):
        """ Returns and PrologixAdapter object that references the GPIB 
        address specified, while sharing the Serial connection with other
        calls of this function 
        """
        return PrologixAdapter(self.connection, gpib_address)
        
    def wait_for_srq(self, timeout=25, delay=0.1):
        """ Wait for a SRQ, and leaves the bit high """
        while int(self.ask("++srq")) != 1:
            time.sleep(delay)
        
    def __repr__(self):
        if self.address:
            return "<PrologixAdapter(port='%s',address=%d)>" % (
                    self.port, self.address)
        else:
            return "<PrologixAdapter(port='%s')>" % self.connection.port