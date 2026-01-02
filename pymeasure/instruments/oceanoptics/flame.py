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

from enum import IntEnum
from pymeasure.instruments import Instrument, validators


class CommandFlameS(IntEnum):
    INITIALIZE = 0x01
    SET_INTEGRATION_TIME = 0x02
    SET_STROBE_STATUS = 0x03
    SET_SHUTDOWN_MODE = 0x04
    QUERY = 0x05
    WRITE = 0x06
    REQUEST_SPECTRA = 0x09
    SET_TRIGGER_MODE = 0x0A
    QUERY_NUM_OF_PLUGIN_ACCESSORIES = 0x0B
    QUERY_PLUGIN_IDS = 0x0C
    DETECT_PLUGINS = 0x0D
    LED_STATUS = 0x12
    I2C_READ = 0x60
    I2C_WRITE = 0x61
    SPI_IO = 0x6A
    WRITE_REGISTER_INFO = 0x6A
    READ_REGISTER_INFO = 0x6B
    READ_PCB_TEMPERATURE = 0x6C
    READ_IRRADIANCE_CALIBRATION_FACTORS = 0x6D
    WRITE_IRRADIANCE_CALIBRATION_FACTORS = 0x6E
    QUERY_INFO = 0xFE


class FlameS(Instrument):
    """Control the Ocean Optics Flame S instrument."""
    NUM_PIXELS = 2048

    def __init__(self, adapter, name="Ocean Optics Flame S", **kwargs):
        super().__init__(adapter, name, **kwargs)

    def init(self):
        self.write_bytes(CommandFlameS.INITIALIZE.to_bytes())

    def set_integration_time(self, integration_time: int):
        """Set the integration time.
        :integration_time (int): Integration time in microseconds.
        """
        validators.strict_range(integration_time, [1_000, 65_535_000])
        payload = integration_time.to_bytes(length=4, byteorder='little')
        cmd = bytearray(CommandFlameS.SET_INTEGRATION_TIME.to_bytes())
        cmd.extend(payload)
        self.write_bytes(cmd)

    def request_spectra(self):
        PIXELS_PER_PACKET = 256
        self.write_bytes(CommandFlameS.REQUEST_SPECTRA.to_bytes())
        raw = self.read_bytes()

class CommandFlameT(IntEnum):
    INITIALIZE = 0x01
    SET_INTEGRATION_TIME = 0x02
    SET_STROBE_STATUS = 0x03
    QUERY = 0x05
    WRITE = 0x06
    REQUEST_SPECTRA = 0x09
    SET_TRIGGER_MODE = 0x0A
    QUERY_NUM_OF_PLUGIN_ACCESSORIES = 0x0B
    QUERY_PLUGIN_IDS = 0x0C
    DETECT_PLUGINS = 0x0D
    LED_STATUS = 0x12
    I2C_READ = 0x60
    I2C_WRITE = 0x61
    SPI_IO = 0x62
    PSOC_READ = 0x68
    PSOC_WRITE = 0x69
    WRITE_REGISTER_INFO = 0x6A
    READ_REGISTER_INFO = 0x6B
    READ_PCB_TEMPERATURE = 0x6C
    READ_IRRADIANCE_CALIBRATION_FACTORS = 0x6D
    WRITE_IRRADIANCE_CALIBRATION_FACTORS = 0x6E
    QUERY_INFO = 0xFE


class FlameT(Instrument):
    """Control the Ocean Optics Flame T instrument."""
    NUM_PIXELS = 3648

    def __init__(self, adapter, name="Ocean Optics Flame T", **kwargs):
        super().__init__(adapter, name, **kwargs)
