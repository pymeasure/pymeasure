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

from .ophir_base import KeyMixin, OphirCommunication, OphirBase


class NovaEnums:
    """This method is needed to separate the enums from the Nova for the documentation"""

    Capabilities = OphirBase.Capabilities
    LegacyModes = OphirBase.LegacyModes
    ScreenModes = OphirBase.ScreenModes


class Nova(KeyMixin, NovaEnums, OphirCommunication):
    """For the older Nova device.

    Does not support most commands, only:
    AT, BC, BM, DI, EF, ER, FE, FO, FP, FS, FZ, HI, HT, II, KL, LI, LR, LS, RE, RN, SE, SF, SI, SK,
    SL, SP, VE, WL, WN, WW
    """

    def __init__(self, adapter, name="Nova", **kwargs):
        super().__init__(adapter, name=name, **kwargs)
        # Set timeouts for Nova device.
        self._power_timeout = 0
        self._energy_timeout = 0

    mode = OphirBase.mode_legacy

    # Measurement
    range = OphirBase.range

    frequency = OphirBase.frequency

    units = OphirBase.units

    power = OphirBase.power

    energy_flag = OphirBase.energy_flag

    energy_ready = OphirBase.energy_ready

    energy = OphirBase.energy

    wavelength = OphirBase.wavelength

    diffuser = OphirBase.diffuser

    # Device
    head_information = OphirBase.head_information

    head_type = OphirBase.head_type

    id = OphirBase.id

    reset = OphirBase.reset

    software_version = OphirBase.software_version

    screen_mode = OphirBase.screen_mode

    # additional working
    @property
    def power_timeout(self):
        """Control the timeout in ms waiting for a power signal."""
        return self._power_timeout

    @power_timeout.setter
    def power_timeout(self, timeout=0):
        """Control the timeout in ms waiting for a power signal."""
        self._power_timeout = timeout
        if timeout:
            self.power_command_process = lambda c: f"{c}{timeout/100:.0f}"
        else:
            self.power_command_process = lambda c: c

    @property
    def energy_timeout(self):
        """Control the timeout in ms waiting for an energy signal."""
        return self._energy_timeout

    @energy_timeout.setter
    def energy_timeout(self, timeout=0):
        """Control the timeout in ms waiting for an energy signal."""
        self._energy_timeout = timeout
        if timeout:
            self.energy_command_process = lambda c: f"{c}{timeout/100:.0f}"
        else:
            self.energy_command_process = lambda c: c
