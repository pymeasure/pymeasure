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

import logging

import numpy as np
from copy import copy


class Adapter:
    """ Base class for Adapter child classes, which adapt between the Instrument
    object and the connection, to allow flexible use of different connection
    techniques.

    This class should only be inherited from.

    :param preprocess_reply: optional callable used to preprocess strings
        received from the instrument. The callable returns the processed string.
    :param kwargs: all other keyword arguments are ignored.
    """

    def __init__(self, preprocess_reply=None, **kwargs):
        self.preprocess_reply = preprocess_reply
        self.connection = None
        self.log = logging.Logger("Adapter")
        self.log.addHandler(logging.NullHandler())

    def __del__(self):
        """Close connection upon garbage collection of the device"""
        if self.connection is not None:
            self.connection.close()

    # Directly called methods
    def write(self, command):
        """
        Writes a command to the instrument.

        :param command: SCPI command string to be sent to the instrument
        """
        self.log.debug(f"WRITE:{command.encode()}")
        self._write(command)

    def _write(self, command):
        """Writing to the instrument. Implement in subclass."""
        raise NotImplementedError("Adapter class has not implemented writing")

    def write_bytes(self, content):
        """Write the bytes `content`. If a command is full, fill the read."""
        self.log.debug(f"WRITE:{content}")
        self._write_bytes(content)

    def _write_bytes(self, content):
        """Write bytes to the instrument. Implement in subclass."""
        raise NotImplementedError("Adapter class has not implemented writing")

    def ask(self, command):
        """ Writes the command to the instrument and returns the resulting
        ASCII response

        :param command: SCPI command string to be sent to the instrument
        :returns: String ASCII response of the instrument
        """
        raise DeprecationWarning("Ask is now in the instrument")
        self.write(command)
        return self.read()

    def read(self):
        """ Reads until the buffer is empty and returns the resulting
        ASCII respone

        :returns: String ASCII response of the instrument.
        """
        read = self._read()
        self.log.debug(f"READ:{read.encode()}")
        return read

    def _read(self):
        """Read from the instrument. Implement in subclass."""
        raise NotImplementedError("Adapter class has not implemented reading")

    def read_bytes(self, count):
        """Read `count` number of bytes."""
        read = self._read_bytes(count)
        self.log.debug(f"READ:{read}")
        return read

    def _read_bytes(self, count):
        """Read from the instrument. Implement in subclass."""
        raise NotImplementedError("Adapter class has not implemented reading")

    def values(self, command, separator=',', cast=float, preprocess_reply=None):
        """ Writes a command to the instrument and returns a list of formatted
        values from the result

        :param command: SCPI command to be sent to the instrument
        :param separator: A separator character to split the string into a list
        :param cast: A type to cast the result
        :param preprocess_reply: optional callable used to preprocess values
            received from the instrument. The callable returns the processed string.
            If not specified, the Adapter default is used if available, otherwise no
            preprocessing is done.
        :returns: A list of the desired type, or strings where the casting fails
        """
        raise DeprecationWarning("Moved to instrument")
        results = str(self.ask(command)).strip()
        if callable(preprocess_reply):
            results = preprocess_reply(results)
        elif callable(self.preprocess_reply):
            results = self.preprocess_reply(results)
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

    def _read(self):
        """ Returns the last commands given after the
        last read call.
        """
        result = copy(self._buffer)
        # Reset the buffer
        self._buffer = ""
        return result

    def _write(self, command):
        """ Writes the command to a buffer, so that it can
        be read back.
        """
        self._buffer += command

    def __repr__(self):
        return "<FakeAdapter>"


"""
TODO Adapter rework
-------------------
- see also protocol.py
- adjust tests
- prologix adapter: remove rw_delay
- move read/write binary_values to adapter or instrument?

For individual instruments
--------------------------
- move rw_delay from prologix adapter to the instruments
- no ask/values from adapter

Special Adapters
----------------
- attocube
- danfysik: should be removable, verify, that it works as expected.
- lakeshore: could be moved to pyvisa, I guess
- Oxford Adapter: move it to its own superclass between Instrument and the
    specific instrument itself.
- Toptica: move to instrument itself.

Instruments with changes in read/write/ask/values
------------------------
fwbell.fwbell5080
danfysik.danfysik8500
hcp.TC038
attocube.anc300
anaheim.dpseries
keithley.keithley2306
hp.hp8116a
lakeshore.lakeshore421
parker.parkerGV6   move to pyvisa
"""
