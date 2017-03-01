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
from time import sleep
from functools import wraps
from .adapter import Adapter, AdapterError
from usb.core import USBError
from usbtmc.usbtmc import Instrument as USBTMCDriver, UsbtmcException, struct

RECONNECTION_ATTEMPTS = 3


def attempt_reconnect(fn):
    """Method wrapper to reconnect if wrapped method times out."""
    @wraps(fn)
    def wrapped(self, *args, **kwargs):
        n_attempts = RECONNECTION_ATTEMPTS
        while n_attempts > 0:
            try:
                return fn(self, *args, **kwargs)
            except USBError as err:
                log.warning(str(err))
                if err.errno == 110:  # Timeout Error
                    n_attempts -= 1
                    self.reset_device()  # This seems to fix it when working manually
            except (UsbtmcException, struct.error) as err:
                # Catch any usbtmc errors and handle them appropriately
                log.warning(str(err))
                n_attempts -= 1
                self.reset_device()

        log.error("Max reconnection attempts encountered [{}]".format(fn.__name__))
        return ''

    return wrapped


class USBTMCAdapter(Adapter):
    r"""Implement a USBTMC interface via the ``python-usbtmc`` library.

    :keyword encoding: Optional encoding to use when communicating with the device, defaults to ``utf-8``
    :type encoding: ``str``

    :param \*args:
        See Arguments Below
    :param \**kwargs:
        See Keyword Arguments Below

    :Arguments:
        * *VISAResourceString* (``str``) --
            A VISA resource string corresponding to the connected device
        * *idVendor* (``int``) --
            The vendor ID of the device to connect as a hex or int
        * *idProduct* (``int``) --
            The product ID of the device to connect as a hex or int
        * *idSerial* (``int``) --
            The Serial number of the device to connect in hex or int

    :Keyword Arguments:
        * *idVendor* (``int``) --
            The vendor ID of the device to connect as a hex or int
        * *idProduct* (`int`) --
            The product ID of the device to connect as a hex or int
        * *idSerial* (``int``) --
            The Serial number of the device to connect in hex or int

    .. note:: Usage

        The USBTMC protocol requires some extra knowledge in order to connect
        to devices. This attempts to explain some common connection scenarios.

    Any additional constructor positional and keyword arguments are passed
     onwards to the ``python-usbtmc`` connection driver, which accepts several
     types of arguments.   More detail can be found in the `python-usbtmc`
     `docs <https://www.mankier.com/1/pythonusbtmc#Python_Usbtmc_Examples>`_

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
        try:
            self.connection = USBTMCDriver(*args, **kwargs)
        except UsbtmcException as e:
            raise AdapterError(str(e))

    @attempt_reconnect
    def write(self, command):
        """Write to the USBTMC device."""
        self.connection.write(command, encoding=self.encoding)

    @attempt_reconnect
    def read(self):
        """Read from the USBTMC device."""
        return self.connection.read(encoding=self.encoding)

    def close(self):
        """Close the current connection and release back to OS."""
        return self.connection.close()

    def reset_device(self):
        """Try and reset the device."""
        if self.connection.iface is not None:
            log.info("Resetting USBTMC Device")
            self.connection.device.reset()
            sleep(0.5)
