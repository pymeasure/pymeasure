#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from re import compile

from pymeasure.instruments import Channel, Instrument
from pymeasure.instruments.validators import strict_discrete_set


class RelayChannel(Channel):
    """
    Settings of the optionally included setpoint relay.

    The relay is energized either below or above the setpoint depending on the
    'direction' property. The relay is de-energized when the reset value is
    crossed in the opposite direction.

    Note that device by default uses an auto hysteresis setting of 10% of the
    setpoint value that overwrites the current reset value whenever the setpoint
    value or direction is changed. If other hysteresis value than 10% is
    required, first set the setpoint value and direction before setting the
    reset value.
    """
    status = Channel.measurement(
        "SS{ch}?",
        """Get the setpoint relay status""",
        values={True: "SET", False: "CLEAR"},
    )

    setpoint = Channel.control(
        "SP{ch}?", "SP{ch}!%s",
        """Control the relay switch setpoint""",
        check_set_errors=True,
    )

    resetpoint = Channel.control(
        "SH{ch}?", "SH{ch}!%s",
        """Control the relay switch off value""",
        check_set_errors=True,
    )

    direction = Channel.control(
        "SD{ch}?", "SD{ch}!%s",
        """Control the switching direction""",
        validator=strict_discrete_set,
        values=["ABOVE", "BELOW"],
        check_set_errors=True,
    )


class MKSInstrument(Instrument):
    """Abstract MKS Instrument

    Connection to the device is made through an RS232/RS485 serial connection.
    The communication protocol of these devices is as follows:

    Query: '@<aaa><Command>?;FF' with the response '@<aaa>ACK<Response>;FF'
    Set command: '@<aaa><Command>!<parameter>;FF' with the response '@<aaa>ACK<Response>;FF'
    Above <aaa> is an address from 001 to 254 which can be specified upon
    initialization. Since ';FF' is not supported by pyvisa as terminator this
    class overloads the device communication methods.

    :param adapter: pyvisa resource name of the instrument or adapter instance
    :param string name: The name of the instrument.
    :param address: device address included in every message to the instrument
                    (default=253)
    :param kwargs: Any valid key-word argument for Instrument
    """

    def __init__(self, adapter, name="MKS Instrument", address=253, **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            read_termination=";",  # in reality its ";FF"
            # which is, however, invalid for pyvisa. Therefore extra bytes have to
            # be read in the read() method and the terminators are hardcoded here.
            write_termination=";FF",
            **kwargs
        )
        self.address = address
        # compiled regular expression for finding numerical values in reply strings
        self._re_response = compile(fr"@{self.address:03d}(?P<ack>ACK)?(?P<msg>.*)")

    def _extract_reply(self, reply):
        """ preprocess_reply function which tries to extract <Response> from
        '@<aaa>ACK<Response>;FF'. If <Response> can not be identified the orignal string
        is returned.
        :param reply: reply string
        :returns: string with only the response, or the original string
        """
        rvalue = self._re_response.search(reply)
        if rvalue:
            return rvalue.group('msg')
        return reply

    def _prepend_address(self, cmd):
        """
        create command string by including the device address
        """
        return f"@{self.address:03d}{cmd}"

    def _check_extra_termination(self):
        """
        Check the read termination to correspond to the protocol
        """
        t = super().read_bytes(2)  # read extra termination chars 'FF'
        if t != b'FF':
            raise ValueError(f"unexpected termination string received {t}")

    def read(self):
        """
        Reads from the instrument including the correct termination characters
        """
        ret = super().read()
        self._check_extra_termination()
        return self._extract_reply(ret)

    def write(self, command):
        """
        Write to the instrument including the device address.

        :param command: command string to be sent to the instrument
        """
        super().write(self._prepend_address(command))

    def check_set_errors(self):
        """
        Check reply string for acknowledgement string.
        """
        ret = super().read()  # use super read to get raw reply
        reply = self._re_response.search(ret)
        if reply:
            if reply.group('ack') == 'ACK':
                self._check_extra_termination()
                return []
        # no valid acknowledgement message found
        raise ValueError(f"invalid reply '{ret}' found in check_errors")
