#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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


# As an instrument contributor, I want to define default connection settings for my
# instrument with a minimum of boiler-plate. These settings should be easily
# user-overridable if appropriate without having to change the code/implementation
# of my instrument.
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
    def __init__(self, adapter, name="Instrument with multiple connection methods",
                 baud_rate=2400, **kwargs):
        # - baud_rate is placed in the signature if it's expected to be modified by the user
        # - baud_rate is only valid for the asrl protocol
        # - enable_repeat_addressing is only for gpib and always False for this device
        # - timeout is the same for all pyvisa protocols, using setdefault it is user-modifiable
        # without cluttering the signature:
        kwargs.setdefault('timeout', 1500)

        super().__init__(adapter,
                         name=name,
                         gpib=dict(enable_repeat_addressing=False,
                                   read_termination='\r'),
                         asrl={'baud_rate': baud_rate,
                               'read_termination': '\r\n'},
                         **kwargs,  # all others/generally valid kwargs
                         )

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
    # method specific to pyvisa TCPIPInstrument
    assert hasattr(instr.adapter.connection, 'control_ren')


def test_connections_use_gpib():
    """As a user, I want to be free to choose which connection to use (e.g. serial-over RS-232,
    USB, TCP/IP) should an instrument support more than one
    """
    # here, baud_rate is invalid for pyvisa, but is a default kwarg anyway
    instr = MultiprotocolInstrument(adapter='GPIB::8::INSTR', visa_library='@sim')
    # attribute specific to pyvisa GPIBInstrument
    assert instr.adapter.connection.enable_repeat_addressing is False


def test_use_separate_SerialAdapter():
    """As a user, I want to be able to supply a self-generated Adapter instance
    (e.g. to enable serial connection sharing over RS-485/-422)
    """
    # note: baudrate, not baud_rate, as this goes to pyserial
    ser = SerialAdapter(serial.serial_for_url("loop://", baudrate=4800))
    instr = MultiprotocolInstrument(ser)
    # don't need visa_library here as this does not go to pyvisa, kwargs are ignored if provided
    assert instr.adapter.connection.baudrate == 4800


def test_separate_adapter_discards_additional_args():
    """When passing in a separate Adapter instance, all connection-specific args and settings
    are ignored.
    """
    ser = SerialAdapter(serial.serial_for_url("loop://"))
    instr = MultiprotocolInstrument(ser, baud_rate=1234, wrong_kwarg='fizzbuzz')
    assert instr.adapter.connection.baudrate == 9600  # default of serial


def test_use_separate_VISAAdapter():
    """As a user, I want to be able to supply my own VISAAdpter with my settings
    """
    # User can use their own VISAAdapter
    ser = VISAAdapter('ASRL1::INSTR', baud_rate=1200, visa_library='@sim')
    instr = MultiprotocolInstrument(ser)
    # don't need visa_library here as this does not go to pyvisa, kwargs are ignored if provided
    assert instr.adapter.connection.baud_rate == 1200


def test_incorrect_arg_is_flagged():
    """As a user or instrument contributor that used an incorrect/invalid (kw)arg,
    I want to be alerted to that fact.
    """
    with pytest.raises(ValueError, match='bitrate'):
        _ = MultiprotocolInstrument(adapter='ASRL1::INSTR', bitrate=1234, visa_library='@sim')


def test_incorrect_interface_type_is_flagged():
    """As a user or instrument contributor that used an incorrect/invalid interface type,
    I want to be alerted to that fact.
    """
    class WrongInterfaceInstrument(Instrument):
        def __init__(self, adapter, name="Instrument with incorrect interface name", **kwargs):
            super().__init__(adapter,
                             name=name,
                             arsl={'read_termination': '\r\n'},  # typo here
                             **kwargs,
                             )
    with pytest.raises(ValueError, match='arsl'):
        _ = WrongInterfaceInstrument(adapter='ASRL1::INSTR', visa_library='@sim')


def test_improper_arg_is_flagged():
    """As a user or instrument contributor that used a kwarg that is inappropriate for the present
    connection, I want to be alerted to that fact.
    """
    with pytest.raises(ValueError, match='enable_repeat_addressing'):
        _ = MultiprotocolInstrument(adapter='ASRL1::INSTR', enable_repeat_addressing=True,
                                    visa_library='@sim')


def test_common_kwargs_are_retained():
    instr1 = MultiprotocolInstrument(adapter='ASRL1::INSTR', visa_library='@sim')
    assert instr1.adapter.connection.timeout == 1500
    instr2 = MultiprotocolInstrument(adapter='GPIB::8::INSTR', visa_library='@sim')
    assert instr2.adapter.connection.timeout == 1500


def test_distinct_interface_specific_defaults():
    """As an instrument implementor, I can easily prescribe default settings
    that are different between interfaces.
    """
    instr1 = MultiprotocolInstrument(adapter='ASRL1::INSTR', visa_library='@sim')
    assert instr1.adapter.connection.read_termination == '\r\n'
    instr2 = MultiprotocolInstrument(adapter='GPIB::8::INSTR', visa_library='@sim')
    assert instr2.adapter.connection.read_termination == '\r'


def test_modified_non_signature_kwargs_are_retained():
    instr1 = MultiprotocolInstrument(adapter='ASRL1::INSTR', timeout=3000, visa_library='@sim')
    assert instr1.adapter.connection.timeout == 3000
    instr2 = MultiprotocolInstrument(adapter='GPIB::8::INSTR', timeout=3000, visa_library='@sim')
    assert instr2.adapter.connection.timeout == 3000


def test_override_interface_specific_defaults():
    """As as user, I want to be able to override interface-specific hardcoded defaults.
    """
    instr1 = MultiprotocolInstrument(adapter='ASRL1::INSTR', read_termination='\r',
                                     visa_library='@sim')
    assert instr1.adapter.connection.read_termination == '\r'
    instr2 = MultiprotocolInstrument(adapter='GPIB::8::INSTR', enable_repeat_addressing=True,
                                     visa_library='@sim')
    assert instr2.adapter.connection.enable_repeat_addressing is True
