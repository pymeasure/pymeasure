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
import re
import time
from pymeasure.instruments import Instrument
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SMC(Instrument, includeSCPI=False):
    """ Represents the Scientific Magnetics (Twickenham Scientific Instruments)
    Superconducting Magnet Controller and provides a high-level interface for
    interacting with the instrument.
    """

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Scientific Magnetics SMC",
            **kwargs
        )

        # Define RegExpressions to match the responses of the instrument
        self._reG = re.compile(r'^I([\s+-]\d{3}.\d{3})V([\s+-]\d{2}.\d)R(\d[AV])\r\n$')
        self._reJF = re.compile(r'^F([\s+-]\d{2}.\d{4})H(\d)\r\n$')
        self._reJI = re.compile(r'^I([\s+-]\d{3}.\d{3})H(\d)\r\n$')
        self._reKF = re.compile(r'^R(\d)M(\d)P(\d)X(\d)H(\d)Z0.00E(\d{2})Q([\s+-]\d{2}.\d{4})\r\n$')
        self._reKI = re.compile(r'^R(\d)M(\d)P(\d)X(\d)H(\d)Z0.00E(\d{2})Q([\s+-]\d{3}.\d{3})\r\n$')
        self._reN = re.compile(r'^F([\s+-]\d{2}.\d{4})V([\s+-]\d{2}.\d)R(\d[AV])\r\n$')
        self._reO = re.compile(r'^A(\d{2}.\d{5})D(\d)T(\d)B(\d)W(\d{3}.)C(0.\d{6})\r\n$')
        self._reSF = re.compile(r'^T(\d)U(\d{2}.\d{4})L(\d{2}.\d{4})Y(\d{2}.\d)\r\n$')
        self._reSI = re.compile(r'^T(\d)U(\d{3}.\d{3})L(\d{3}.\d{3})Y(\d{2}.\d)\r\n$')

    def pause_off(self):
        self.write('P0')

    def pause_on(self):
        self.write('P1')

    def unit_amps(self):
        self.write('T0')

    def unit_tesla(self):
        self.write('T1')

    def upper_setpoint_tesla(self, tesla):
        self.unit_tesla()
        self.write('U{tesla:07.4f}'.format(tesla=tesla))

    def lower_setpoint_tesla(self, tesla):
        self.unit_tesla()
        self.write('L{tesla:07.4f}'.format(tesla=tesla))

    def switch_forward(self):
        self.write('D0')

    def switch_reversed(self):
        self.write('D1')

    def ramp_zero(self):
        self.write('R0')

    def ramp_lower(self):
        self.write('R1')

    def ramp_upper(self):
        self.write('R2')

    def heater_off(self):
        self.write('H0')

    def heater_conditional_on(self):
        """ Standard function to be used when turning on switch heater """
        self.write('H1')

    def heater_unconditional_on(self):
        """ Warning this will turn on the heater without any interlocks.
            Usage at own risk!
        """
        self.write('H2')

    def heater_reset_persistent_mode_current_record_to_zero(self):
        self.write('H9')

    @property
    def output_parameters_amps(self):
        self.unit_amps()
        self.write('G')
        message = self.read()
        match = self._reG.match(message)

        if not match:
            return None

        I = float(match.group(1))
        U = float(match.group(2))
        R = match.group(3)

        return dict(current=I, voltage=U, ramp=R)

    @property
    def output_parameters_tesla(self):
        self.unit_tesla()
        self.write('N')
        message = self.read()
        match = self._reN.match(message)

        if not match:
            print('DEBUG', self._reN, match, message)
            return None

        F = float(match.group(1))
        U = float(match.group(2))
        R = match.group(3)

        return dict(field=F, voltage=U, ramp=R)

    @property
    def magnet_status(self):
        self.write('J')
        message = self.read()

        matchF = self._reJF.match(message)
        matchI = self._reJI.match(message)

        if matchF:
            return dict(heater=int(matchF.group(2)),
                        value=float(matchF.group(1)),
                        units=1)
        elif matchI:
            return dict(heater=int(matchI.group(2)),
                        value=float(matchI.group(1)),
                        units=0)
        else:
            return None

    @property
    def current_status(self):
        self.write('K')
        message = self.read()

        matchF = self._reKF.match(message)
        matchI = self._reKI.match(message)

        if matchF:
            return dict(
                ramp_target=int(matchF.group(1)),
                ramp_status=int(matchF.group(2)),
                pause=int(matchF.group(3)),
                external_trip=int(matchF.group(4)),
                heater_mode=int(matchF.group(5)),
                error_code=int(matchF.group(6)),
                quench_value=float(matchF.group(7)),
                units=1
            )
        elif matchI:
            return dict(
                ramp_target=int(matchI.group(1)),
                ramp_status=int(matchI.group(2)),
                pause=int(matchI.group(3)),
                external_trip=int(matchI.group(4)),
                heater_mode=int(matchI.group(5)),
                error_code=int(matchI.group(6)),
                quench_value=float(matchI.group(7)),
                units=0
            )
        else:
            return None

    @property
    def operating_parameters(self):
        self.write('O')
        message = self.read()

        match = self._reO.match(message)

        if match:
            return dict(
                ramp_rate=float(match.group(1)),
                switch_direction=int(match.group(2)),
                units=int(match.group(3)),
                front_panel_lock=int(match.group(4)),
                heater_current_mA=float(match.group(5)),
                telsa_per_amps=float(match.group(6))
            )
        else:
            return None

    @property
    def set_point_status(self):
        self.write('S')
        message = self.read()

        matchF = self._reSF.match(message)
        matchI = self._reSI.match(message)

        if matchF:
            return dict(
                units=int(matchF.group(1)),
                upper_set_point=float(matchF.group(2)),
                lower_set_point=float(matchF.group(3)),
                terminal_voltage=float(matchF.group(4))
            )
        elif matchI:
            return dict(
                units=int(matchI.group(1)),
                upper_set_point=float(matchI.group(2)),
                lower_set_point=float(matchI.group(3)),
                terminal_voltage=float(matchI.group(4))
            )
        else:
            return None

    @property
    def tesla(self) -> float:
        value = self.output_parameters_tesla["field"]
        if self.operating_parameters["switch_direction"] == 0:
            sign = +1
            return float(sign * value)
        elif self.operating_parameters["switch_direction"] == 1:
            sign = -1
            return float(sign * value)


    @tesla.setter
    def tesla(self, value: float):
        if value == 0:
            self.ramp_zero()
        else:
            # 1. Get actual direction
            if self.operating_parameters["switch_direction"] == 0:
                sign = +1
            elif self.operating_parameters["switch_direction"] == 1:
                sign = -1
            else:
                sign = 0

            # 2. Check, if value and sign are both positive or both negative
            if value * sign > 0:
                self.upper_setpoint_tesla(abs(value))
            elif value * sign < 0:
                self.ramp_zero()

                # At zero-field: switch direction.
                while not (self.current_status["ramp_status"] == 1):
                    time.sleep(1)
                if value > 0:
                    self.switch_forward()
                elif value < 0:
                    self.switch_reversed()

                self.upper_setpoint_tesla(abs(value))
            self.ramp_upper()

