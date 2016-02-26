#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure
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

from .adapter import Adapter

import socket, select

import logging
log = logging.getLogger(__name__)
#log.addHandler(log.NullHandler())

long = int # Python 3 fix

class SocketAdapter(Adapter):
    """ Adapter class for a socket connection.

    :param host: Socket host IP
    :param port: Socket port
    """

    def __init__(self, host, port, **kwargs):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.host, self.port = host, port

    def __repr__(self):
        return "<SocketAdapter(host='%s', port='%s')>" % (self.host, self.port)

    def socket_poll(self):
        """ Poll the socket
        """
        inputready, o, e = select.select([s],[],[], 0.0)
        return len(inputready)>0

    def ask_socket_raw(self, command):
        import time
        s = self.socket
        '''query socket and return response'''
        #empty socket buffer
        while socket_poll(s):
            s.recv(1024)
            time.sleep(.01)
        s.sendall(command.encode())
        while not self.socket_poll():
            time.sleep(.01)
        data = b''
        while self.socket_poll():
            data += s.recv(1024)
            time.sleep(.01)
        return data

    def ask(command, startbytes=0):
        data = self.ask_socket_raw(command)
        if startbytes>0:
            data = data[startbytes:]
        try:
            ans = eval(data)
        except (IndentationError, SyntaxError, NameError, TypeError):
            ans = data.decode()
        return ans

    def values(self, command, separator = ','):
        """ Writes a command to the instrument and returns a list of numerical
        values from the result.

        :param command: SCPI command to be sent to the instrument.
        :returns: A list of numerical values.
        """
        results = str(self.ask(command)).strip()
        results = results.split(separator)
        for result in results:
            try:
                result = float(result)
            except:
                pass # Keep as string
        return results