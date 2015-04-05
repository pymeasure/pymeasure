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

import visa
import numpy as np
import copy


class VISAAdapter(Adapter):
    """ Wrapper class for the VISA library """

    def __init__(self, resourceName, **kwargs):
        self.manager = visa.ResourceManager()
        if isinstance(resourceName, (int, long)):
            resourceName = "GPIB0::%d::INSTR" % resourceName
        if self.version == '1.5':
            safeKeywords = ['resource_name', 'timeout', 'term_chars',
                            'chunk_size', 'lock', 'delay', 'send_end',
                            'values_format']
            kwargsCopy = copy.deepcopy(kwargs)
            for key in kwargsCopy:
                if key not in safeKeywords:
                    kwargs.pop(key)
            self.connection = self.manager.get_instrument(
                                    resourceName,
                                    **kwargs
                              )
        elif self.version == '1.4':
            self.connection = visa.instrument(resourceName, **kwargs)

    @property
    def version(self):
        if hasattr(visa, '__version__'):
            return visa.__version__
        else:
            return '1.4'

    def write(self, command):
        self.connection.write(command)

    def read(self):
        return self.connection.read()

    def ask(self, command):
        return self.connection.ask(command)

    def values(self, command):
        return self.connection.ask_for_values(command)

    def binary_values(self, command, header_bytes=0, dtype=np.float32):
        self.connection.write(command)
        binary = self.connection.read_raw()
        header, data = binary[:header_bytes], binary[header_bytes:]
        return np.fromstring(data, dtype=dtype)

    def wait_for_srq(self, timeout=25, delay=0.1):
        self.connection.wait_for_srq(timeout)

    def __repr__(self):
        return "<VISAAdapter(resource='%s')>" % self.connection.resourceName
