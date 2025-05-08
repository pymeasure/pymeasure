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

import logging
import time

from pymeasure.instruments.keithley.keithley2260B import Keithley2260B

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TexioPSW360L30(Keithley2260B):
    r""" Represents the TEXIO PSW-360L30 Power Supply (minimal implementation)
    and provides a high-level interface for interacting with the instrument.

    For a connection through tcpip, the device only accepts
    connections at port 2268, which cannot be configured otherwise.
    example connection string: 'TCPIP::xxx.xxx.xxx.xxx::2268::SOCKET'

    For a connection through USB on Linux, the kernel is going to create
    a /dev/ttyACMX device automatically. The serial connection properties are
    fixed at 9600–8-N-1.

    The read termination for this interface is Line-Feed \n.

    This driver inherits from the Keithley2260B one. All instructions
    implemented in the Keithley 2260B driver are also available for the
    TEXIO PSW-360L30 power supply.

    The only addition is the "output" property that is just an alias for
    the "enabled" property of the Keithley 2260B. Calling the output switch
    "enabled" is confusing because it is not clear if the whole device is
    enabled/disable or only the output.

    .. code-block:: python

        source = TexioPSW360L30("TCPIP::xxx.xxx.xxx.xxx::2268::SOCKET")
        source.voltage = 1
        print(source.voltage)
        print(source.current)
        print(source.power)
        print(source.applied)
    """

    def __init__(self, adapter, name="TEXIO PSW-360L30 Power Supply", **kwargs):
        super().__init__(adapter, name, **kwargs)

    def check_errors(self):
        """ Logs any system errors reported by the instrument.
        """
        code, message = self.next_error
        while code != 0:
            t = time.time()
            log.info("TEXIO PSW-360L30 reported error: %d, %s" % (code, message))
            code, message = self.next_error
            if (time.time() - t) > 10:
                log.warning("Timed out for TEXIO PSW-360L30 error retrieval.")
