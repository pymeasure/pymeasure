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

import logging

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ThorlabsPM100USB(Instrument):
    """Represents Thorlabs PM100USB powermeter."""

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter, "ThorlabsPM100USB powermeter", **kwargs
        )
        self.timout = 3000
        self._set_flags()

    wavelength_min = Instrument.measurement(
        "SENS:CORR:WAV? MIN", "Minimum wavelength, in nm"
    )

    wavelength_max = Instrument.measurement(
        "SENS:CORR:WAV? MAX", "Maximum wavelength, in nm"
    )

    @property
    def wavelength(self):
        """Wavelength in nm."""
        value = self.values("SENSE:CORR:WAV?")[0]
        return value

    @wavelength.setter
    def wavelength(self, value):
        """Wavelength in nm."""
        if self.wavelength_settable:
            # Store min and max wavelength to only request them once.
            if not hasattr(self, "_wavelength_min"):
                self._wavelength_min = self.wavelength_min
            if not hasattr(self, "_wavelength_max"):
                self._wavelength_max = self.wavelength_max

            value = truncated_range(
                value, [self._wavelength_min, self._wavelength_max]
            )
            self.write(f"SENSE:CORR:WAV {value}")
        else:
            raise AttributeError(
                f"{self.sensor_name} does not allow setting the wavelength."
            )

    @property
    def power(self):
        """Power in W."""
        if self.is_power_sensor:
            return self.values("MEAS:POW?")[0]
        else:
            raise AttributeError(f"{self.sensor_name} is not a power sensor.")

    @property
    def energy(self):
        """Energy in J."""
        if self.is_energy_sensor:
            return self.values("MEAS:ENER?")[0]
        else:
            raise AttributeError(
                f"{self.sensor_name} is not an energy sensor."
            )

    def _set_flags(self):
        """Get sensor info and write flags."""
        response = self.values("SYST:SENSOR:IDN?")
        if response[0] == "no sensor":
            raise OSError("No sensor connected.")
        self.sensor_name = response[0]
        self.sensor_sn = response[1]
        self.sensor_cal_msg = response[2]
        self.sensor_type = response[3]
        self.sensor_subtype = response[4]
        _flags_str = response[5]

        # interpretation of the flags, see p. 49 of the manual:
        # https://www.thorlabs.de/_sd.cfm?fileName=17654-D02.pdf&partNumber=PM100D

        # Convert to binary representation and pad zeros to 9 bit for sensors
        # where not all flags are present.
        _flags_str = format(int(_flags_str), "09b")
        # Reverse the order so it matches the flag order from the manual, i.e.
        # from decimal values from 1 to 256.
        _flags_str = _flags_str[::-1]

        # Convert to boolean.
        self.flags = [x == "1" for x in _flags_str]

        # setting the flags; _dn are unused; decimal values as comments
        (
            self.is_power_sensor,  # 1
            self.is_energy_sensor,  # 2
            _d4,  # 4
            _d8,  # 8
            self.response_settable,  # 16
            self.wavelength_settable,  # 32
            self.tau_settable,  # 64
            _d128,  # 128
            self.has_temperature_sensor,  # 256
        ) = self.flags
