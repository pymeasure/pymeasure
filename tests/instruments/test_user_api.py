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

import pytest
import serial

from pymeasure.adapters import SerialAdapter, VISAAdapter
from pymeasure.instruments import Instrument
from pyvisa.constants import InterfaceType


class MultiprotocolInstrument(Instrument):
    """Test instrument for testing the configuration and use of multiple connection methods.

    The instrument support multiple transports methods(serial, TCP/IP, GPIB).
    In case of serial connections, the default baud rate is low (2400), but configurable in
    the device, so it can use faster communication if desired.
    Two examples in our instruments are AMI430, Keithley2260B (for TCP/IP, there are more
    with GPIB capability)

    It also has an attribute to configure a non-serial (gpib) connection. This demonstrates
    that there may be attributes that are not valid for a serial connection, only others.
    """
    def __init__(self, adapter, name="Instrument with multiple connection methods", **kwargs):
        # As an instrument contributor, I want to define default connection settings for my
        # instrument with a minimum of boiler-plate. These settings should be easily
        # user-overridable if appropriate without having to change the code/implementation
        # of my instrument.

        super().__init__(adapter,
                         name=name,
                         **kwargs)
        if isinstance(adapter, (int, str)):
            # These are only cases where adapter is created by Instrument class, in this case
            # the adapter is a VISAAdapter class based on pyvisa
            if_type = self.adapter.connection.resource_info.interface_type
            # Different communication methods might have different valid and/or needed attributes
            # This is just an example on how this is possible since pyvisa includes
            # several type of interfaces
            if if_type is InterfaceType.asrl and not 'baud_rate' in kwargs:
                self.adapter.connection.baud_rate = 2400
            elif if_type is InterfaceType.gpib and not 'enable_repeat_addressing' in kwargs:
                self.adapter.connection.enable_repeat_addressing = False

# The defined tests use the pyvisa-sim simulated connections to avoid the need for a connected
# instrument. The argument handling and connection creation happens in pyvisa just like for a
# real instrument, through.


def test_serial_default_settings():
    """As a user, I want to simply connect to an instrument using default settings"""
    instr = MultiprotocolInstrument(adapter='ASRL1::INSTR', visa_library='@sim')
    assert instr.adapter.connection.baud_rate == 2400


def test_serial_custom_baud_rate_is_set():
    """As a user, I want to easily override default settings to fit my needs"""
    instr = MultiprotocolInstrument(adapter='ASRL1::INSTR', baud_rate=115200, visa_library='@sim')
    assert instr.adapter.connection.baud_rate == 115200


def test_connections_use_tcpip():
    """As a user, I want to be free to choose which connection to use (e.g. serial-over RS-232,
    USB, TCP/IP) should an instrument support more than one
    """
    # here, baud_rate is invalid for pyvisa, but is a default kwarg anyway
    instr = MultiprotocolInstrument(adapter='TCPIP::localhost:1111::INSTR', visa_library='@sim')
    assert hasattr(instr.adapter.connection, 'control_ren') # method specific to pyvisa TCPIPInstrument


def test_connections_use_gpib():
    """As a user, I want to be free to choose which connection to use (e.g. serial-over RS-232,
    USB, TCP/IP) should an instrument support more than one
    """
    # here, baud_rate is invalid for pyvisa, but is a default kwarg anyway
    instr = MultiprotocolInstrument(adapter='GPIB::8::INSTR', visa_library='@sim')
    assert instr.adapter.connection.enable_repeat_addressing == False  # attribute specific to pyvisa GPIBInstrument


def test_use_separate_adapter_instance():
    """As a user, I want to be able to supply a self-generated Adapter instance
    (e.g. to enable serial connection sharing over RS-485/-422)
    """
    ser = SerialAdapter(serial.serial_for_url("loop://", baudrate = 4800)) # note: not baud_rate, as this goes to pyserial
    instr = MultiprotocolInstrument(ser)  # don't need visa_library here as this does not go to pyvisa, kwargs are ignored if provided
    print (ser, ser.connection)
    print (instr.adapter)
    assert instr.adapter.connection.baudrate == 4800

def test_use_separate_adapter_instance1():
    """As a user, I want to be able to supply my own VISAAdpter with my settings
    """
    # User can use its own VISAAdapter
    ser = VISAAdapter('ASRL1::INSTR', baud_rate = 1200, visa_library='@sim')
    instr = MultiprotocolInstrument(ser)  # don't need visa_library here as this does not go to pyvisa, kwargs are ignored if provided
    assert instr.adapter.connection.baud_rate == 1200


def test_incorrect_arg_is_flagged():
    """As a user or instrument contributor that used an incorrect/invalid (kw)arg,
    I want to be alerted to that fact.
    """
    with pytest.raises(ValueError, match='bitrate'):
        instr = MultiprotocolInstrument(adapter='ASRL1::INSTR', bitrate=1234, visa_library='@sim')
