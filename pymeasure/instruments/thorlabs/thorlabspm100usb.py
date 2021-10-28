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

from pymeasure.instruments import Instrument, RangeException

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ThorlabsPM100USB(Instrument):
    """Represents Thorlabs PM100USB powermeter"""

    # TODO: refactor to check if the sensor wavelength is adjustable
    wavelength = Instrument.control(
        "SENSE:CORR:WAV?",
        "SENSE:CORR:WAV %g",
        "Wavelength in nm; not set outside of range",
    )

    # TODO: refactor to check if the sensor is a power sensor
    power = Instrument.measurement("MEAS:POW?", "Power, in Watts")

    wavelength_min = Instrument.measurement(
        "SENS:CORR:WAV? MIN", "Get minimum wavelength, in nm"
    )

    wavelength_max = Instrument.measurement(
        "SENS:CORR:WAV? MAX", "Get maximum wavelength, in nm"
    )

    def __init__(self, adapter, **kwargs):
        super(ThorlabsPM100USB, self).__init__(
            adapter, "ThorlabsPM100USB powermeter", **kwargs
        )
        self.timout = 3000
        self.sensor()

    def measure_power(self, wavelength):
        """
        Set wavelength in nm and get power in W.

        If wavelength is out of range it will be set to range limit.
        """
        if wavelength < self.wavelength_min:
            raise RangeException(
                ("Wavelength %.2f nm out of range: "
                    "using minimum wavelength: %.2f nm")
                % (wavelength, self.wavelength_min)
            )
            # explicit setting wavelenghth, althought it would be automatically
            # set
        if wavelength > self.wavelength_max:
            raise RangeException(
                ("Wavelength %.2f nm out of range: "
                    "using maximum wavelength: %.2f nm")
                % (wavelength, self.wavelength_max)
            )
        self.wavelength = wavelength
        return self.power

    def sensor(self):
        """Get sensor info."""
        response = self.ask("SYST:SENSOR:IDN?").split(",")
        self.sensor_name = response[0]
        self.sensor_sn = response[1]
        self.sensor_cal_msg = response[2]
        self.sensor_type = response[3]
        self.sensor_subtype = response[4]
        _flags_str = response[5].rstrip('\n')

        # interpretation of the flags, see p. 49 of the manual:
        # https://www.thorlabs.de/_sd.cfm?fileName=17654-D02.pdf&partNumber=PM100D

        # Convert to binary representation and pad zeros to 9 bit for sensors
        # where not all flags are present.
        _flags_str = format(int(_flags_str), "09b")
        # Reverse the order so it matches the flag order from the manual, i.e.
        # from decimal values from 1 to 256.
        _flags_str = _flags_str[::-1]

        # setting the flags; _dn are unused; decimal values as comments
        (
            self.is_power,              # 1
            self.is_energy,             # 2
            _d4,                        # 4
            _d8,                        # 8
            self.resp_settable,         # 16
            self.wavelength_settable,   # 32
            self.tau_settable,          # 64
            _d128,                      # 128
            self.temperature_sens,      # 256
        ) = self.flags

    @property
    def energy(self):
        """Get energy in J."""
        if self.is_energy:
            return self.values("MEAS:ENER?")
        else:
            raise Exception("%s is not an energy sensor" % self.sensor_name)
