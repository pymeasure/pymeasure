#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

import struct
from pymeasure.instruments import Instrument
from pymeasure.instruments.common_base import CommonBase


# - PARAMETER STRINGS - #
TEMP = '0817bf'
TEMP_STABLE = '0817ca'
SET_POINT_MIN = '0817bc'
SET_POINT_MAX = '0817bd'
SET_POINT_GET = '0817c2'
SET_POINT_SET = '0617be %f'
CHOPPER_FREQ_GET = '081939'
CHOPPER_FREQ_SET = '06193a %f'
CHOPPER_POS = '06193b %i'


class SR200N(Instrument):

    # - temperature parameters ------------------------------ #
    temp = CommonBase.measurement(
        TEMP,
        """Float representing the current temperature of the blackbody source.""",
    )

    temp_is_stable = CommonBase.measurement(
        TEMP_STABLE,
        """Boolean parameter to check if the temperature has stabilized.""",
        cast=bool,
    )
    
    set_point_min = CommonBase.measurement(
        SET_POINT_MIN,
        """Float representing the minimum temperature set point.""",
    )
    
    set_point_max = CommonBase.measurement(
        SET_POINT_MAX,
        """Float representing the maximum temperature set point.""",
    )
    
    set_point = CommonBase.control(
        SET_POINT_GET, SET_POINT_SET,
        """Float representing the blackbody temperature set point.""",
    )

    # - chopper parameters ---------------------------------- #
    chopper_frequency = CommonBase.control(
        CHOPPER_FREQ_GET, CHOPPER_FREQ_SET,
        """Float representing the frequency of the internal chopper."""
    )

    chopper_position = CommonBase.setting(
        CHOPPER_POS,
        """Integer for manual control of the chopper (0 for closed, 1 for open)."""
    )

    # - internal parameters for constructing and reading messages - #
    _header = b'\xaa\x01' 
    _read_dict = {
        TEMP: (14, float),
        TEMP_STABLE: (11, bool),
        SET_POINT_MIN: (14, float),
        SET_POINT_MAX: (14, float),
        SET_POINT_GET: (14, float),
        CHOPPER_FREQ_GET: (14, float),
    }
    _read_count = 0
    _read_type = None

    def __init__(self, adapter, name='SR200N Blackbody', **kwargs):
        super().__init__(
            adapter,
            name,
            asrl={
                'baud_rate': 115200,
            },
            **kwargs
        )

    @staticmethod
    def add_bytes(byte1, byte2):
        """ Static method to implement the addition of two bytes with overflow. Used for checksum
        calculation.

        :param byte1: First byte object to add.
        :param byte2: Second byte object to add.
        """
        int_value = (int.from_bytes(byte1, 'big') + int.from_bytes(byte2, 'big')) & 0xff
        byte_value = int_value.to_bytes(length=4, byteorder='big')
        return byte_value        

    def calc_checksum(self, add):
        """ Calculate a checksum for a string of bytes.

        :param add: Byte string to calculate a checksum on.
        """
        sum_bytes = bytes.fromhex('00')
        for i in range(len(add)):
            b = add[i:i+1]
            sum_bytes = self.add_bytes(sum_bytes, b)
        b255 = bytes.fromhex('ff')
        cs = int.from_bytes(b255, 'big') - int.from_bytes(sum_bytes, 'big') + 1
        
        return cs.to_bytes(length=4, byteorder='big')

    def write(self, command, **kwargs):
        """ Override the base write method to construct the checksum and use `write_bytes()`.

        :param command: hexadecimal command as a string.
        """
        # - split the command string on spaces, get the command value if present - #
        cmd_split = command.split(' ')
        cmd = cmd_split[0]
        cmd_bytes = bytes.fromhex(cmd)
        val = b'' if len(cmd_split) == 1 else float(cmd_split[1])
        service_code = cmd_bytes[0:1]

        # - calculate the total size and parameter size based on the command type - #
        if val == b'':
            self._read_count, self._read_type = self._read_dict[cmd]
            total_size = b'\x00\x06'
            parameter_size = b'\x00\x00'
        elif command == CHOPPER_POS:
            total_size = b'\x00\x07'
            parameter_size = b'\x00\x01'
            val = b'\x00' if val == 0.0 else b'\x01'
        elif service_code == b'\x06':
            total_size = b'\x00\x0a'
            parameter_size = b'\x00\x04'
            val = struct.pack('!f', val)
        else:
            raise IOError('Invalid command string: %s' % command)
        
        # - construct the final message with the header and checksum - #
        b = self._header + total_size + cmd_bytes + parameter_size + val
        checksum = self.calc_checksum(b)
        msg = b + checksum

        # - write the final message - #
        self.write_bytes(msg)

    def read(self):
        """ Override the base read method to parse the returned floating messages.
        """
        ret = self.read_bytes(count=self._read_count)
        size = int.from_bytes(ret[7:9], 'big')
        data = ret[9:9+size]
        
        # - convert hex floating point data to float object - #
        if self._read_type == float:
            value = struct.unpack('!f', data)[0]
        else:
            value = int.from_bytes(data, 'big')
        
        return str(value)
        