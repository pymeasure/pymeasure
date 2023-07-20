#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

import clr
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.KCube.PiezoCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.PiezoCLI import *
from System import Decimal  # necessary for real world units

import time

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set

class ThorlabsKPZ101(Instrument):
    """
    Represents Thorlabs KPZ101 piezo controller and provides a high-level interface for
    interacting with the instrument.



    .. code-block:: python

        thorlabs = ThorlabsKPZ101({'serial_number': str(12345678)}, max_voltage='low', includeSCPI=False)

        thorlabs.id                             # Prints the device information

        thorlabs.max_volt                   # Prints the maximum voltage in Volts
        thorlabs.min_volt                   # Prints the minimum voltage in Volts

        thorlabs.voltage                 # Prints the voltage in Volts

        thorlabs.disconnect()             # disconnects from the instrument


    """
    def __init__(self, adapter, name="Thorlabs KPZ101", max_voltage='low', **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

        DeviceManagerCLI.BuildDeviceList()

        self.device = KCubePiezo.CreateKCubePiezo(adapter['serial_number'])

        if not self.device == None:

            self.device.Connect(adapter['serial_number'])
            if not self.device.IsSettingsInitialized():
                self.device.WaitForSettingsInitialized(3000)

            self.device.StartPolling(50)
            time.sleep(.1)
            self.device.EnableDevice()
            time.sleep(.1)

        self.device.Connect(adapter['serial_number'])
        self.device_info = self.device.GetDeviceInfo()
        assert self.device_info.Description.find('KPZ101') > -1, f'device_info.Description should include {self.what}'

        self.device_config = self.device.GetPiezoConfiguration(adapter['serial_number'])
        log.info(self.device_config)

        self.device_settings = self.device.PiezoDeviceSettings
        log.info(self.device_settings)
        time.sleep(0.1)
        self._voltage = float(str(self.device.GetOutputVoltage()))
        max_voltage_dict = {'low': 75, 'medium': 100, 'high': 150}
        self.device.SetMaxOutputVoltage(Decimal(max_voltage_dict[max_voltage]))

    def disconnect(self):
        self.device.StopPolling()
        self.device.Disconnect()
        log.info(f"Finished disconnecting down {self.name}")


    @property
    def max_volt(self):
        return  float(str(self.device.GetMaxOutputVoltage()))

    @property
    def min_volt(self):
        return  float(str(self.device.GetMinOutputVoltage()))

    @property
    def voltage(self):
        return self._voltage
    @voltage.setter
    def voltage(self, value, ):
        tol = 0.02 # V tolerance
        if self.min_volt <= float(value) <= self.max_volt:
            self.device.SetOutputVoltage(Decimal(value))
            self._voltage = float(str(self.device.GetOutputVoltage()))
            while (abs(value - self._voltage) > tol):
                #print(f'self._voltage - value = {self._voltage - value}')
                #value = self._set_voltage # last measurement
                time.sleep(0.01)
                self._voltage = float(str(self.device.GetOutputVoltage()))
        else:
            raise ValueError(f'Voltage must be between {self.min_volt} and {self.max_volt} V')
    @property
    def id(self):
        return self.device_info.Description

