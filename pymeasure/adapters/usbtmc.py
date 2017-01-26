#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure Developers
#
# Python USBTMC driver, lifted from python-usbtmc.
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
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())
from functools import wraps
from .adapter import Adapter
try:
    from usbtmc import Instrument as USBTMCDriver
    from usb.core import USBError
except ImportError:
    log.warning("Missing required package, python-usbtmc")


def reconnect_attempt(fn):
    """Method wrapper to reconnect if method times out."""

    def wrapped(self, *args, **kwargs):
        n_attempts = 3
        while n_attempts > 0:
            log.info("Reconnect Attempts: {}".format(n_attempts))
            try:
                return fn(self, *args, **kwargs)
            except USBError as err:
                log.error(dir(err))
                if err.code == 110:  # Timeout Error
                    n_attempts -= 1
                    self = args[0]
                    self.reset_device()

        log.error("Reconnection timeout [{}]".format(fn.__name__))
        return ''

    return wrapped


class USBTMCAdapter(Adapter):
    """Implement a USBTMC interface via the ``python-usbtmc`` library.

    :keyword encoding: Optional encoding to use when communicating with the device, defaults to ``utf-8``
    :type encoding: str

    .. topic:: Usage

        The USBTMC protocol requires some extra knowledge in order to connect
        to devices. This attempts to explain some common connection scenarios.

    Any additional constructor positional and keyword arguments are passed
     onwards to the python-usbtmc connection driver.  This accepts several types of arguments.

    If the entire VISA resource name is known, this can be passed as a simple string.

    .. code-block:: python

        adapter = USBTMCAdapter("USB::1234::5678::INSTR")

    USB Instruments make available identifing information such as Vendor,
    Product, and Serial.  For a unique instrument on the bus, the Product/
    Vendor codes are enough.  For multiple instances of a device on the bus
    requires an additional serial number to identify each.

    These values can be parsed on UNIX machines via the ``lsusb`` command.

    .. code-block:: bash

        $> lsusb
        ...
        Bus 002 Device 013: ID 1313:804f ThorLabs
        ...

    These values are hexidecimal, take care to specify them appropriately.

    .. code-block:: python

        adapter = USBTMCAdapter(0x1313, 0x804f)  # Specify in Hex
        adapter = USBTMCAdapter(4883, 32487)     # Equally valid as ints

    And, if there are several of these on the same bus, then we need the serial number in addition.

    .. code-block:: python

        adapter = USBTMCAdapter(0x1313, 0x804f, "M00337123")  # Device A
        adapter2 = USBTMCAdapter(0x1313, 0x804f, "M00337124")  # Device B

    .. note::

        On Unix machines, custom udev rules are likely required.  See the
        `README <https://github.com/python-ivi/python-usbtmc#configuring-udev>`_
        note on this in the ``python-usbtmc`` package.

    """

    def __init__(self, *args, **kwargs):
        """Constructor."""
        self.encoding = kwargs.pop('encoding', 'utf-8')
        self.connection = USBTMCDriver(*args, **kwargs)

    @reconnect_attempt
    def write(self, command):
        """Write to the USBTMC device."""
        self.connection.write(command, encoding=self.encoding)

    @reconnect_attempt
    def read(self):
        """Read from the USBTMC device."""
        return self.connection.read(encoding=self.encoding)

    def reset_device(self):
        """Try and reset the device."""
        if self.connection.iface is not None:
            self.connection.device.reset()
