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
from pyvisa.errors import VisaIOError
from pymeasure.instruments import Instrument


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ND287(Instrument):
    """ Represents the Heidenhain ND287 position display unit used to readout and display
        absolute position measured by Heidenhain encoders.
    """

    status = Instrument.measurement(
        "\x1BA0800", "Get the encoder's status bar"
    )

    # get_process lambda functions used in the position property
    position_get_process_map = {
        "mm": lambda p: float(p.split("\x02")[-1]) * 1e-4,
        "inch": lambda p: float(p.split("\x02")[-1]) * 1e-5
    }

    position = Instrument.measurement(
        "\x1BA0200", """Measure the encoder's current position (float).
                        Note that the get_process performs a mapping from the returned
                        value to a float measured in the units specified by :attr:`.ND287.units`.
                        The get_process is modified dynamically as this mapping changes slightly
                        between different units.""",
        get_process=position_get_process_map["mm"],
        dynamic=True
    )

    def __init__(self, adapter, name="Heidenhain ND287", units="mm", **kwargs):
        """ Initialize the nd287 with a carriage return write termination.

        :param: units: Specify the units that the gauge is working in.
        Valid values are "inch" and "mm" with "mm" being the default.
        """
        self._units = units

        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            write_termination="\r",
            **kwargs
        )

    @property
    def id(self):
        """ Get the string identification property for the device.
        """
        self.write("\x1BA0000")
        id_str = self.read_bytes(37).decode("utf-8")
        return id_str

    @property
    def units(self):
        """ Control the unit of measure set on the device.
            Valid values are 'mm' and 'inch' Note that this parameter can only be set
            manually on the device. So this argument only ensures that the instance units
            and physical device settings match. I.e., this property does not change any
            physical device setting.
        """
        return self._units

    @units.setter
    def units(self, unit):
        if unit in self.position_get_process_map.keys():
            self._units = unit
            self.position_get_process = self.position_get_process_map[unit]

    def check_errors(self):
        """ Method to read an error status message and log when an error is detected.

        :return: String with the error message as its contents.
        """
        self.write("\x1BA0301")
        try:
            err_str = self.read_bytes(36).decode("utf-8")
        except VisaIOError:
            err_str = None

        if err_str is not None:
            log.error("Heidenhain ND287 error message received: %s" % err_str)

        return err_str
