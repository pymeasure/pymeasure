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

import io
import logging
import re

from pymeasure.adapters import VISAAdapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def write_test(file, name, cls_name, comm_pairs, tests):
    """Write a test."""
    inst = ""
    for test in tests:
        if "inst" in test:
            inst = " as inst"
            break
    file.writelines(
        ["\n", "\n", f"def test_{name}():\n",
         "    with expected_protocol(\n",
         f"            {cls_name},\n",
         f"            {comm_pairs}\n".replace("), (", "),\n             ("),
         f"            ){inst}:\n"])
    if tests == ["pass"]:
        tests = ["pass  # Verify the expected communication."]
    file.writelines(f"        {test}\n" for test in tests)


def parse_binary_string(text):
    """Parse a bytes string in `text` and return the bytes object."""
    return b''.join([bytes(text, 'ascii') or bytes([int(binary[-2:], 16)])
                     for binary, text in re.findall(r"(\\x[0-9a-fA-F]{2,2})|(.+?)",
                                                    text[2:-1], re.DOTALL)])


def parse_stream(stream):
    """
    Parse the data stream.

    It is expected, that a message is always written in one write, while
    reading may extend over several reads, e.g. reading bytes.
    """
    comm = []
    lines = stream.readlines()
    print(lines)
    write = None
    read = None
    for line in lines:
        if line.startswith(b"WRITE:"):
            # Store the last comm_pair unless there is none.
            if write is not None or read is not None:
                comm.append((write, read))
                read = None
            write = line[6:-1]#parse_binary_string(line[6:-1])
        else:
            if read is not None:
                read += line[5:-1]#parse_binary_string(line[5:-1])
            else:
                read = line[5:-1]#parse_binary_string(line[5:-1])
    if read is not None or write is not None:
        comm.append((write, read))
    return comm


class ByteFormatter(logging.Formatter):
    """Logging formatter with bytes values for the test generation."""

    @staticmethod
    def make_bytes(value):
        if isinstance(value, (bytes, bytearray)):
            return value
        if isinstance(value, str):
            return value.encode()

    def format(self, record):
        return b"".join((record.msg.replace(r"%s", "").encode(),
                         *[self.make_bytes(arg) for arg in record.args]))


class ByteStreamHandler(logging.StreamHandler):
    """Logging handler using bytes streams."""

    terminator = b"\n"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.formatter = ByteFormatter()


class Generator:
    """
    Generates tests from the communication with an instrument.

    Example usage:
    g = Generator("test_tc038.py")
    g.instantiate(TC038, "COM5", 'hcp')
    g.test_property("information")
    g.test_property("monitored_value")
    g.test_property_setter("setpoint", 20)
    g.test_property("setpoint")
    """

    def __init__(self, filepath="tests.py"):
        """Initialize the generator writing the testfile to `filepath`."""
        if isinstance(filepath, io.StringIO):
            self._file = filepath
        else:
            self._file = open(filepath, "w")
        self._stream = io.BytesIO()
        self._index = 0
        self._incomm = []  # Initializiation comm_pairs

    def __del__(self):
        self.close()

    def close(self):
        """Close the file handler."""
        if not self._file.closed:
            self._file.close()

    def parse_stream(self):
        """Parse the stream not yet read."""
        self._stream.seek(self._index)
        comm = parse_stream(self._stream)
        self._index = self._stream.tell()
        return self._incomm + comm

    def instantiate(self, instrument_class, adapter, manufacturer, **kwargs):
        """
        Instantiate the instrument with the `adapter` and `kwargs`.

        This method also writes the necessary import header for the tests.

        The argument `manufacturer` is the module from which to import the
        instrument, e.g. 'hcp' if instrument_class is 'pymeasure.hcp.tc038'.
        """
        self._class = instrument_class.__name__
        log.info(f"Instantiate {self._class}.")
        self._file.write(
            "from pymeasure.test import expected_protocol\n"
            f"from pymeasure.instruments.{manufacturer} import {self._class}\n")
        if isinstance(adapter, (int, str)):
            try:
                adapter = VISAAdapter(adapter, **kwargs)
            except ImportError:
                raise Exception("Invalid Adapter provided for Instrument since"
                                " PyVISA is not present")
        adapter.log.addHandler(ByteStreamHandler(self._stream))
        adapter.log.setLevel(logging.DEBUG)
        self.inst = instrument_class(adapter, **kwargs)
        comm = self.parse_stream()
        self._incomm = comm
        write_test(self._file, "init", self._class, comm, ['pass'])

    def test_property(self, property):
        """Test getting some `property` of an instrument."""
        log.info(f"Test property {property} getter.")
        value = getattr(self.inst, property)
        comm = self.parse_stream()
        if isinstance(value, str):
            value = f"\'{value}\'"
        write_test(self._file, property, self._class, comm,
                   [f"assert inst.{property} == {value}"])
        return value

    def test_property_setter(self, property, value):
        """Test setting the `property` of the instrument to `value`."""
        log.info(f"Test property {property} setter.")
        setattr(self.inst, property, value)
        comm = self.parse_stream()
        if isinstance(value, str):
            value = f"\'{value}\'"
        write_test(self._file, f"{property}_setter", self._class, comm,
                   [f"inst.{property} = {value}"])

    def test_method(self, method, *args, **kwargs):
        """Test calling the `method` of the instruments with `args` and `kwargs`."""
        log.info(f"Test method {method}.")
        value = getattr(self.inst, method)(*args, **kwargs)
        comm = self.parse_stream()
        if isinstance(value, str):
            value = f"\'{value}\'"
        write_test(self._file, method, self._class, comm,
                   [f"assert inst.{method}({f'*{args}, ' if args else ''}"
                    f"{f'**{kwargs}' if kwargs else ''}) == {value}"])
