#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

from enum import Enum
from pymeasure.instruments import Instrument


class VGCDef(Enum):
    """
    Represents VGC Definitions used in data transmission.
    """
    ENQ = b'\x05'
    ACK = b'\x06\r\n'
    NAK = b'\x15\r\n'


class VGC501(Instrument):
    """
    Represents the INFICON VGC501 pressure gauge.
    """

    def __init__(self,
                 adapter,
                 name="VGC501",
                 baud_rate=9600,
                 **kwargs
                 ):
        super().__init__(
            adapter,
            name,
            baud_rate=baud_rate,
            includeSCPI=False,
            timeout=100,
            write_termination="\r\n\x05",
            read_termination="\r\n",
            **kwargs
        )

    def read(self, **kwargs):
        """
        Read from the device and check the response.

        The first read line contains an acknowledgement of the read command.
        The second line contains the value to be parsed to the measurement.
        """
        response = super().read_bytes(3)
        if response == VGCDef.ACK.value:
            val = super().read()
            return val
        elif response == VGCDef.NAK.value:
            raise ValueError(
                f"Received negative acknowledgement {response}."
                )
        else:
            raise ValueError(
                f"Expected positive acknowledgement {VGCDef.ACK.value}, received {response}."
                )

    pressure = Instrument.measurement(
        "PR1",
        """Measure the pressure of the gauge in mbar.""",
    )

    information = Instrument.measurement(
        "AYT",
        """Get information about the connected instrument.""",
    )

    error_status = Instrument.measurement(
        "ERR",
        """
        Get the error status of the gauge
        """,
    )
