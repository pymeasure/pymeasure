#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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
from pyvisa.errors import VisaIOError
from pymeasure.instruments import Instrument


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ND287(Instrument):
    """ Represents the Heidenhain ND287 position display unit used to readout and display absolute position measured by
        Heidenhain encoders.
    """
    
    position = Instrument.measurement(
        "\x1BA0200", "Read the encoder's current position.",
        get_process=lambda p: ND287.position_proc(float(p.split("\x02")[-1])),
    )

    status = Instrument.measurement(
        "\x1BA0800", "Read the encoder's status bar"
    )

    def __init__(self, resourceName, units="mm", **kwargs):
        """ Initialize the nd287 with a carriage return write termination.

        :param: units: Specify the units that the gauge is working in. Note that this parameter can only be set
                       manually on the device. And this argument is to synchronize the driver with the device settings.
        """

        self._units = units

        super().__init__(
            resourceName,
            "Heidenhain ND287",
            includeSCPI=False,
            write_termination="\r",
            **kwargs
        )

    def position_proc(self, pos):
        """ Apply the appropriate scaling factor to the position read-out from the encoder based on the value of the
            units property.
        """
        if self._units == "mm":
            pos *= 1e-4
        elif self._units == "inch":
            pos *= 1e-5
        return pos

    @property
    def id(self):
        """ String identification property for the device.
        """
        self.adapter.connection.write("\x1BA0000")
        id_str = self.adapter.connection.read_bytes(36).decode("utf-8")
        return id_str

    @property
    def units(self):
        """ String property representing the unit of measure set on the device. Valid values are 'mm' and 'inch'
        """
        return self._units
    
    @units.setter
    def units(self, unit):
        """ Setter for the 'units' property.
        
        :param unit: String argument with value 'mm' or 'inch'
        """
        val_units = ["mm", "inch"]
        if unit in val_units:
            ND287._units = unit

    def check_errors(self):
        """ Method to read an error status message and log when an error is detected.

        :return: String with the error message as its contents.
        """
        self.adapter.connection.write("\x1BA0301")
        try:
            err_str = self.adapter.connection.read_bytes(36).decode("utf-8")
        except VisaIOError:
            err_str = None

        if err_str is not None:
            log.error("Heidenhain ND287 error message received: %s" % err_str)

        return err_str

