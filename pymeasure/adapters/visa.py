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

import logging

import copy
import visa
import numpy as np
from pkg_resources import parse_version

from .adapter import Adapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# noinspection PyPep8Naming,PyUnresolvedReferences
class VISAAdapter(Adapter):
    """ Adapter class for the VISA library using PyVISA to communicate
    with instruments.

    :param resource: VISA resource name that identifies the address
    :param visa_library: VisaLibrary Instance, path of the VISA library or VisaLibrary spec string (@py or @ni).
                         if not given, the default for the platform will be used.
    :param kwargs: Any valid key-word arguments for constructing a PyVISA instrument
    """

    def __init__(self, resourceName, visa_library='', **kwargs):
        if not VISAAdapter.has_supported_version():
            raise NotImplementedError("Please upgrade PyVISA to version 1.8 or later.")

        if isinstance(resourceName, int):
            resourceName = "GPIB0::%d::INSTR" % resourceName
        super(VISAAdapter, self).__init__()
        self.resource_name = resourceName
        self.manager = visa.ResourceManager(visa_library)
        safeKeywords = ['resource_name', 'timeout',
                        'chunk_size', 'lock', 'delay', 'send_end',
                        'values_format', 'read_termination', 'write_termination']
        kwargsCopy = copy.deepcopy(kwargs)
        for key in kwargsCopy:
            if key not in safeKeywords:
                kwargs.pop(key)
        self.connection = self.manager.get_instrument(
            resourceName,
            **kwargs
        )

    @staticmethod
    def has_supported_version():
        """ Returns True if the PyVISA version is greater than 1.8 """
        if hasattr(visa, '__version__'):
            return parse_version(visa.__version__) >= parse_version('1.8')
        else:
            return False

    def __repr__(self):
        return "<VISAAdapter(resource='%s')>" % self.connection.resourceName

    def write(self, command):
        """ Writes a command to the instrument

        :param command: SCPI command string to be sent to the instrument
        """
        self.connection.write(command)

    def read(self):
        """ Reads until the buffer is empty and returns the resulting
        ASCII response

        :returns: String ASCII response of the instrument.
        """
        return self.connection.read()

    def read_bytes(self, size):
        """ Reads specified number of bytes from the buffer and returns
        the resulting ASCII response

        :param size: Number of bytes to read from the buffer
        :returns: String ASCII response of the instrument.
        """
        return self.connection.read_bytes(size)

    def ask(self, command):
        """ Writes the command to the instrument and returns the resulting
        ASCII response

        :param command: SCPI command string to be sent to the instrument
        :returns: String ASCII response of the instrument
        """
        return self.connection.query(command)

    def ask_values(self, command):
        """ Writes a command to the instrument and returns a list of formatted
        values from the result. The format of the return is configurated by
        self.config().

        :param command: SCPI command to be sent to the instrument
        :returns: Formatted response of the instrument.
        """
        return self.connection.query_values(command)

    def binary_values(self, command, header_bytes=0, dtype=np.float32):
        """ Returns a numpy array from a query for binary data

        :param command: SCPI command to be sent to the instrument
        :param header_bytes: Integer number of bytes to ignore in header
        :param dtype: The NumPy data type to format the values with
        :returns: NumPy array of values
        """
        self.connection.write(command)
        binary = self.connection.read_raw()
        header, data = binary[:header_bytes], binary[header_bytes:]
        return np.fromstring(data, dtype=dtype)

    def config(self, is_binary=False, datatype='str',
               container=np.array, converter='s',
               separator=',', is_big_endian=False):
        """ Configurate the format of data transfer to and from the instrument.

        :param is_binary: If True, data is in binary format, otherwise ASCII.
        :param datatype: Data type.
        :param container: Return format. Any callable/type that takes an iterable.
        :param converter: String converter, used in dealing with ASCII data.
        :param separator: Delimiter of a series of data in ASCII.
        :param is_big_endian: Endianness.
        """
        self.connection.values_format.is_binary = is_binary
        self.connection.values_format.datatype = datatype
        self.connection.values_format.container = container
        self.connection.values_format.converter = converter
        self.connection.values_format.separator = separator
        self.connection.values_format.is_big_endian = is_big_endian

    def wait_for_srq(self, timeout=25, delay=0.1):
        """ Blocks until a SRQ, and leaves the bit high

        :param timeout: Timeout duration in seconds
        :param delay: Time delay between checking SRQ in seconds
        """
        self.connection.wait_for_srq(timeout * 1000)
