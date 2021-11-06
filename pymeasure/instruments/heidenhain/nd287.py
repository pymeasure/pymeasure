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

from pymeasure.instruments import Instrument


class Nd287(Instrument):
    """ Represents the Heidenhain ND287 position display unit used to readout and display absolute position measured by Heidenhain encoders.
    """
    
    position = Instrument.measurement(
        "\x1BA0200", "Read the encoder's current position.",
        get_process=lambda p: Nd287.position_proc(float(p.split("\x02")[-1])),
    )
    
    id = Instrument.measurement(
        "\x1BA0000", "Read the instrument's indentification"
    )
    
    # additional configuration properties that must be set on the device, but should be configurable in this driver #
    _units = "mm"
    
    @classmethod
    def position_proc(cls, pos):
        """ Apply the appropriate scaling factor to the position read-out from the encoder based on the value of the units property.
        """
        if cls._units == "mm":
            pos *= 1e-4
        elif cls._units == "inch":
            pos *= 1e-5
        return pos
    
    def __init__(self, resourceName, serial_configuration=None, **kwargs):
        """ Initialize
        """
        super().__init__(
            resourceName,
            "Heidenhain ND287",
            includeSCPI=False,
            write_termination="\r",
            **kwargs
        )
        
        """
        self.position = Instrument.measurement(
            "\x1BA0200", "Read the encoder's current position.",
            get_process=lambda p: float(p.split("\x02")[-1]),
        )"""
        
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
            self._units = unit
            Nd287._units = unit

