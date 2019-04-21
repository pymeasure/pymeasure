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

import numpy as np
from copy import copy


class Adapter(object):
    """ Base class for Adapter child classes, which adapt between the Instrument 
    object and the connection, to allow flexible use of different connection 
    techniques.

    This class should only be inhereted from.
    """

    def write(self, command):
        """ Writes a command to the instrument

        :param command: SCPI command string to be sent to the instrument
        """
        raise NameError("Adapter (sub)class has not implemented writing")

    def ask(self, command):
        """ Writes the command to the instrument and returns the resulting 
        ASCII response

        :param command: SCPI command string to be sent to the instrument
        :returns: String ASCII response of the instrument
        """
        self.write(command)
        return self.read()

    def read(self):
        """ Reads until the buffer is empty and returns the resulting
        ASCII respone

        :returns: String ASCII response of the instrument.
        """
        raise NameError("Adapter (sub)class has not implemented reading")

    def values(self, command, separator=',', cast=float):
        """ Writes a command to the instrument and returns a list of formatted
        values from the result 

        :param command: SCPI command to be sent to the instrument
        :param separator: A separator character to split the string into a list
        :param cast: A type to cast the result
        :returns: A list of the desired type, or strings where the casting fails
        """
        results = str(self.ask(command)).strip()
        results = results.split(separator)
        for i, result in enumerate(results):
            try:
                if cast == bool:
                    # Need to cast to float first since results are usually
                    # strings and bool of a non-empty string is always True
                    results[i] = bool(float(result))
                else:
                    results[i] = cast(result)
            except Exception:
                pass  # Keep as string
        return results

    def binary_values(self, command, header_bytes=0, dtype=np.float32):
        """ Returns a numpy array from a query for binary data 

        :param command: SCPI command to be sent to the instrument
        :param header_bytes: Integer number of bytes to ignore in header
        :param dtype: The NumPy data type to format the values with
        :returns: NumPy array of values
        """
        raise NameError("Adapter (sub)class has not implemented the "
                        "binary_values method")


class FakeAdapter(Adapter):
    """Provides a fake adapter for debugging purposes,
    which bounces back the command so that arbitrary values 
    testing is possible.

    .. code-block:: python

        a = FakeAdapter()
        assert a.read() == ""
        a.write("5")
        assert a.read() == "5"
        assert a.read() == ""
        assert a.ask("10") == "10"
        assert a.values("10") == [10]

    """

    _buffer = ""

    def read(self):
        """ Returns the last commands given after the
        last read call.
        """
        result = copy(self._buffer)
        # Reset the buffer
        self._buffer = ""
        return result

    def write(self, command):
        """ Writes the command to a buffer, so that it can
        be read back.
        """
        self._buffer += command

    def __repr__(self):
        return "<FakeAdapter>"
