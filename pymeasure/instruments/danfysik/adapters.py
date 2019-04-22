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

from pymeasure.adapters.serial import SerialAdapter

import re


class DanfysikAdapter(SerialAdapter):
    """ Provides a :class:`SerialAdapter` with the specific baudrate
    and timeout for Danfysik serial communication.

    Initiates the adapter to open serial communcation over
    the supplied port.

    :param port: A string representing the serial port
    """

    def __init__(self, port):
        super(DanfysikAdapter, self).__init__(port, baudrate=9600, timeout=0.5)

    def write(self, command):
        """ Overwrites the :func:`SerialAdapter.write <pymeasure.adapters.SerialAdapter.write>`
        method to automatically append a Unix-style linebreak at
        the end of the command.

        :param command: SCPI command string to be sent to the instrument
        """
        command += "\r"
        self.connection.write(command.encode())

    def read(self):
        """ Overwrites the :func:`SerialAdapter.read <pymeasure.adapters.Adapter.read>`
        method to automatically raise exceptions if errors are reported by the instrument.

        :returns: String ASCII response of the instrument
        :raises: An :code:`Exception` if the Danfysik raises an error
        """
        # Overwrite to raise exceptions on error messages
        result = b"".join(self.connection.readlines())
        result = result.decode()
        result = result.replace("\r", "")
        search = re.search(r"^\?\x07\s(?P<name>.*)$", result, re.MULTILINE)
        if search:
            raise Exception("Danfysik raised the error: %s" % (
                            search.groups()[0]))
        else:
            return result

        def __repr__(self):
            return "<DanfysikAdapter(port='%s')>" % self.connection.port
