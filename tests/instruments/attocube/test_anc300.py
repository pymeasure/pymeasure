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

from unittest import mock

import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.attocube.adapters import AttocubeConsoleAdapter

from pymeasure.instruments.attocube import ANC300Controller
from pymeasure.instruments.attocube import anc300


class Mock_Adapter(AttocubeConsoleAdapter):
    """Mocking the real adapter using the ProtocolAdapter as connection."""

    def __init__(self, host, port, passwd, **kwargs):
        self.read_termination = '\r\n'
        self.write_termination = self.read_termination
        kwargs.setdefault('preprocess_reply', self.extract_value)
        self.preprocess_reply = kwargs['preprocess_reply']
        self.connection = host  # take the ProtocolAdapter as connection
        self.connection.close = self.close
        self.query_delay = 0
        self.log = mock.MagicMock()
        self.connection.read()  # clear messages sent upon opening the connection
        # send password and check authorization
        self.write(passwd)
        ret = self.connection.read()
        authmsg = ret.split(self.read_termination)[1]
        if authmsg != 'Authorization success':
            raise Exception(f"Attocube authorization failed '{authmsg}'")
        # switch console echo off
        self.write('echo off')
        _ = self.read()

    def close(self):
        pass

    def _read(self):
        """ Reads a reply of the instrument which consists of one or more
        lines. The first ones are the reply to the command while the last one
        is 'OK' or 'ERROR' to indicate any problem. In case the status is not OK
        a ValueError is raised.

        :returns: String ASCII response of the instrument.
        """
        # one would want to use self.read_termination as 'sep' below, but this
        # is not possible because of a firmware bug resulting in inconsistent
        # line endings
        raw = self.connection._read().strip(self.read_termination).rsplit(sep='\n', maxsplit=1)
        if raw[-1] != 'OK':
            if raw[0] == "" or len(raw) == 1:  # clear buffer
                super()._read()  # without error checking
            raise ValueError("AttocubeConsoleAdapter: Error after command "
                             f"{self.lastcommand} with message {raw[0]}")
        return raw[0].strip('\r')  # strip possible CR char

    def _write(self, command):
        """ Writes a command to the instrument

        :param command: command string to be sent to the instrument
        :param check_ack: boolean flag to decide if the acknowledgement is read
            back from the instrument. This should be True for set pure commands
            and False otherwise.
        """
        self.lastcommand = command
        self.connection.write(command + self.write_termination)


@pytest.fixture(autouse=True)
def modding(monkeypatch):
    monkeypatch.setattr(anc300, "AttocubeConsoleAdapter", Mock_Adapter)


def test_stepu():
    """Test a setting."""
    with expected_protocol(
            ANC300Controller,
            [(None, b"xy"),
             (b"passwd\r\n", b'xy\r\nAuthorization success\r\nOK'),
             (b"echo off\r\n", b"x\r\nOK"),
             (b"stepu 1 15\r\n", b"OK")],
            axisnames=["a", "b", "c"],
            passwd="passwd"
            ) as instr:
        instr.a.stepu = 15


def test_voltage():
    """Test a measurement."""
    with expected_protocol(
            ANC300Controller,
            [(None, b"xy"),
             (b"passwd\r\n", b'xy\r\nAuthorization success\r\nOK'),
             (b"echo off\r\n", b"x\r\nOK"),
             (b"geto 1\r\n", b"5\r\nOK")],
            axisnames=["a", "b", "c"],
            passwd="passwd"
            ) as instr:
        assert instr.a.output_voltage == 5
