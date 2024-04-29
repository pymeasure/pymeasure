#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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

# class ResponseChar(enum):
#     """
#     Enumeration for the various response codes sent by the instrument
#     """
#     S = "A" # Set expects Acknowledge
#     Q = "R" # Query expects Response
#     V = "B" # Version expects SW version
#     C = "A" # Configure expects Acknowledge

class Glassman(Instrument):
    """
    Represents the Glassman High Voltage power supplies.
    
    This class was written for the FJ Series, but should also work with the
    FR, EJ, ET, and EY Series.
    
    Prerequisites for remote control:
        - Interlock on J3 must be satisfied
        - HV ON function must be enabled via the front panel `HV ON` button or Remote `HV ON` pins on J3
    
    
    Supports the following, as defined in `Instruction Manual EJ/ET/EY/FJ/FR Series` (102002-177 Rev M2):
        Command: Set (S), Query (Q), Version (V), Configure (C)
    
        Response: Acknowledge (A), Response (R), SW Version (B), Error (E)
    
    
    :param name: Unique device name
    :param maxV: Maximum (100%) output voltage in volts (V)
    :param maxI: Maximum (100%) output current in ampheres (A)
    :param baud_rate: Baud rate (bps) for serial connection
    """
        
    # Methods
    def __init__(self, adapter, maxV, maxI, name="Glassman High Voltage Supply", baud_rate=9600, **kwargs):
        kwargs.setdefault('timeout', 1500)
        super().__init__(
            adapter,
            name,
            maxV,
            maxI,
            asrl={'baud_rate': baud_rate,
                  'read_termination': '\r',
                  'write_termination': '\r'},
            includeSCPI=False,
            **kwargs
        )
    
    # Enumerations

    
    # Properties
    # version = Instrument.ask(self, 
    #     '',
    #     None,
    #     """The software revision level of the power supply's data interface. (str)"""
    #     )
    
    # output_enabled = Instrument.control(
    #     '',
    #     '',
    #     """Get/Set the power output status. (bool)"""
    #     )
    
    # current = Instrument.measurement(
    #     '',
    #     """Measure the output current value"""•
    #     )
    
    # voltage = Instrument.measurement(
    #     '',
    #     """Measure the output voltage value"""
    #     )
    
    # voltage_setpoint = Instrument.setting(
    #     '',
    #     """Set the output voltage """
    #     )
    
    def write(self, command):
        """
        Overrides the adapter's `write` method, prepending the SOH character
        and appending the computed message checksum
        
        :param command: Byte string to be written
        """
        checksum = self.chksum_mod256(command)
        super().write("\x01" + command + checksum)
    
    def read(self):
        """
        Read and validate response
        
        :returns: string message
        """
        # Slave address, function
        got = self.read()
        
        
        return got[1:-2] # remove response code and checksum
    
    @staticmethod
    def chksum_mod256(byte_string):
        """
        Calculates the modulo 256 checksum of a byte string.
        
        :param byte_string: Byte string used to compute the checksum
        
        :returns: string corresponding to the hexidecimal value of the checksum, without the `0x` prefix
        """
        characters = list(byte_string)
        total = 0
        for c in characters:
            total += ord(c)
            
        return format(total % 256, "02X")