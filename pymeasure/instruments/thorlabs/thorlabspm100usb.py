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

import logging
from enum import IntEnum, IntFlag
from warnings import warn

from pymeasure.instruments import Instrument, SCPIUnknownMixin
from pymeasure.instruments.validators import strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SensorTypes(IntEnum):
    PHOTODIODE = 1
    THERMOPILE = 2
    PYROELECTRIC = 3
    FOUR_QUADRANT_THERMOPILE = 4


class SensorFlagMap(IntFlag):
    # For interpretation of the sensor flags see page 49 of
    # https://media.thorlabs.com/globalassets/items/p/pm/pm1/pm100d/17654-d02.pdf?v=0116021333
    # For NEW_FLAG_FORMAT, see the documentation linked in thorlabspm100d2.SensorFlagMap
    WAVELENGTH_SETTABLE = 1 << 5
    TEMPERATURE_SENSOR = 1 << 8
    NEW_FLAG_FORMAT = 1 << 31


class ThorlabsPM100USB(SCPIUnknownMixin, Instrument):
    """Represents Thorlabs PM100USB powermeter interface."""

    sensor_flag_map = SensorFlagMap
    uses_new_flag_format = False

    def __init__(self, adapter, name="ThorlabsPM100USB powermeter", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self.configure_sensor()

    wavelength_min = Instrument.measurement("SENS:CORR:WAV? MIN", "Get minimum wavelength, in nm")

    wavelength_max = Instrument.measurement("SENS:CORR:WAV? MAX", "Get maximum wavelength, in nm")

    @property
    def wavelength(self):
        """Control the wavelength in nm."""
        value = self.values("SENSE:CORR:WAV?")[0]
        return value

    @wavelength.setter
    def wavelength(self, value):
        """Wavelength in nm."""
        if self.is_wavelength_settable:
            # Store min and max wavelength to only request them once.
            if not self._wavelength_range:
                self._wavelength_range = (self.wavelength_min, self.wavelength_max)

            value = strict_range(value, self._wavelength_range)
            self.write(f"SENSE:CORR:WAV {value}")
        else:
            raise AttributeError(f"{self.sensor_name} does not allow setting the wavelength.")

    @property
    def is_power_sensor(self):
        """Get whether the sensor can measure power,
        i.e. is a photodiode, thermopile, or 4-quadrant thermopile sensor, bool."""
        return self.sensor_type in {
            SensorTypes.PHOTODIODE,
            SensorTypes.THERMOPILE,
            SensorTypes.FOUR_QUADRANT_THERMOPILE,
        }

    @property
    def power(self):
        """Measure the power in W.

        Only supported for photodiode, thermopile, and 4-quadrant thermopile sensors,
        raises `AttributeError` otherwise."""
        if self.is_power_sensor:
            return self.values("MEAS:POW?")[0]
        else:
            raise AttributeError(f"{self.sensor_name} is not a power sensor.")

    @property
    def power_density(self):
        """Measure the power density in W/cm^2.

        Only supported for photodiode, thermopile, and 4-quadrant thermopile sensors,
        raises `AttributeError` otherwise."""
        if self.is_power_sensor:
            return self.values("MEAS:PDEN?")[0]
        else:
            raise AttributeError(f"{self.sensor_name} is not a power sensor.")

    @property
    def is_energy_sensor(self):
        """Get whether the sensor can measure energy, i.e. is a pyroelectric sensor, bool."""
        return self.sensor_type in {SensorTypes.PYROELECTRIC}

    @property
    def energy(self):
        """Measure the energy in J."""
        if self.is_energy_sensor:
            return self.values("MEAS:ENER?")[0]
        else:
            raise AttributeError(f"{self.sensor_name} is not an energy sensor.")

    @property
    def energy_density(self):
        """Measure the energy density in J/cm^2.

        Only supported for pyroelectric sensors, raises `AttributeError` otherwise."""
        if self.is_energy_sensor:
            return self.values("MEAS:EDEN?")[0]
        else:
            raise AttributeError(f"{self.sensor_name} is not an energy sensor.")

    @property
    def is_current_sensor(self):
        """Get whether the sensor can measure current, i.e. is a photodiode sensor, bool."""
        return self.sensor_type in {SensorTypes.PHOTODIODE}

    @property
    def current(self):
        """Measure the current in A.

        Only supported for photodiode sensors, raises `AttributeError` otherwise."""
        if self.is_current_sensor:
            return self.values("MEAS:CURR?")[0]
        else:
            raise AttributeError(f"{self.sensor_name} is not a current sensor.")

    @property
    def is_voltage_sensor(self):
        """Get whether the sensor can measure voltage,
        i.e. is a pyroelectric, thermopile, or 4-quadrant thermopile sensor, bool."""
        return self.sensor_type in {
            SensorTypes.PYROELECTRIC,
            SensorTypes.THERMOPILE,
            SensorTypes.FOUR_QUADRANT_THERMOPILE,
        }

    @property
    def voltage(self):
        """Measure the voltage in V.

        Only supported for pyroelectric, thermopile, or 4-quadrant thermopile sensors,
        raises `AttributeError` otherwise."""
        if self.is_voltage_sensor:
            return self.values("MEAS:VOLT?")[0]
        else:
            raise AttributeError(f"{self.sensor_name} is not a voltage sensor.")

    @property
    def temperature(self):
        """Measure the temperature in degC.

        Only supported for certain sensors, raises `AttributeError` otherwise."""
        if self.is_temperature_sensor:
            return self.values("MEAS:TEMP?")[0]
        else:
            raise AttributeError(f"{self.sensor_name} is not a temperature sensor.")

    frequency = Instrument.measurement("MEAS:FREQ?", """Measure the modulation frequency, in Hz.""")

    def configure_sensor(self):
        """Get sensor info and configure the `ThorlabsPM100USB` class for the sensor.

        Call whenever the sensor is changed."""
        response = self.values("SYST:SENSOR:IDN?")
        if response[0] == "no sensor":
            raise OSError("No sensor connected.")
        self.sensor_name = response[0].strip('"')
        self.sensor_sn = self._format_sn(response[1])
        self.sensor_cal_msg = response[2].strip('"')
        self.sensor_type = int(response[3])
        self.sensor_subtype = int(response[4])
        self.sensor_flags = int(response[5])

        if (
            bool(self.sensor_flags & self.sensor_flag_map.NEW_FLAG_FORMAT)
            != self.uses_new_flag_format
        ):
            raise ValueError("Sensor flags not in the expected format.")

        self.is_wavelength_settable = bool(
            self.sensor_flags & self.sensor_flag_map.WAVELENGTH_SETTABLE
        )
        self.is_temperature_sensor = bool(
            self.sensor_flags & self.sensor_flag_map.TEMPERATURE_SENSOR
        )

        self._wavelength_range = None

    @staticmethod
    def _format_sn(sn):
        return str(int(sn))

    @property
    def flags(self):
        """Get the sensor flags, int.

        .. deprecated:: 0.16
           Instead use `sensor_flags`
        """
        warn(
            """Deprecated to use `ThorlabsPM100USB.flags`.
            Instead use `ThorlabsPM100USB.sensor_flags`.""",
            FutureWarning,
        )
        return self.sensor_flags

    @property
    def wavelength_settable(self):
        """Get whether the wavelength is settable, bool.

        .. deprecated:: 0.16
           Instead use `is_wavelength_settable`
        """
        warn(
            """Deprecated to use `ThorlabsPM100USB.wavelength_settable`.
            Instead use `ThorlabsPM100USB.is_wavelength_settable`.""",
            FutureWarning,
        )
        return self.is_wavelength_settable
