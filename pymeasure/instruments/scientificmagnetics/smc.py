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
from pymeasure.instruments.validators import strict_discrete_set, strict_range
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# Define RegExpressions to match the responses of the instrument
_reG = re.compile(r'^I([\s+-]\d{3}.\d{3})V([\s+-]\d{2}.\d)R(\d[AV])\r\n$')
_reJF = re.compile(r'^F([\s+-]\d{2}.\d{4})H(\d)\r\n$')
_reJI = re.compile(r'^I([\s+-]\d{3}.\d{3})H(\d)\r\n$')
_reKF = re.compile(r'^R(\d)M(\d)P(\d)X(\d)H(\d)Z0.00E(\d{2})Q([\s+-]\d{2}.\d{4})\r\n$')
_reKI = re.compile(r'^R(\d)M(\d)P(\d)X(\d)H(\d)Z0.00E(\d{2})Q([\s+-]\d{3}.\d{3})\r\n$')
_reN = re.compile(r'^F([\s+-]\d{2}.\d{4})V([\s+-]\d{2}.\d)R(\d[AV])\r\n$')
_reO = re.compile(r'^A(\d{2}.\d{5})D(\d)T(\d)B(\d)W(\d{3}.)C(0.\d{6})\r\n$')
_reSF = re.compile(r'^T(\d)U(\d{2}.\d{4})L(\d{2}.\d{4})Y(\d{2}.\d)\r\n$')
_reSI = re.compile(r'^T(\d)U(\d{3}.\d{3})L(\d{3}.\d{3})Y(\d{2}.\d)\r\n$')

def extract_value_output_parameters_amps(reply) -> dict:
    match = _reG.match(reply)
    if not match:
        return None
    i = float(match.group(1))
    u = float(match.group(2))
    r = match.group(3)
    return dict(current=i, voltage=u, ramp=r)




class SMC(Instrument, includeSCPI=False):
    """ Represents the Scientific Magnetics (Twickenham Scientific Instruments)
    Superconducting Magnet Controller and provides a high-level interface for
    interacting with the instrument.
    """

    _RAMP_RATE_MAX = 5
    _VOLTAGE_LIMIT_MAX = 1

    pause = Instrument.setting(
        "P%d",
        """A boolean property that controls the pause-status,
         which takes the values True (pause) and False (continue)""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    unit = Instrument.setting(
        "T%d",
        """Sets the units displayed and can take the values
         "A"mpere or "T"esla""",
        validator=strict_discrete_set,
        values={"A": 0, "T": 1},
        map_values=True
    )

    direction = Instrument.setting(
        "D%d",
        """Sets the direction of the reversing switch, if installed.
         Can take the values "F"orward or "R"everse.
         WARNING: Change only if Magnet has been ramped to Zero!""",
        validator=strict_discrete_set,
        values={"F": 0, "R": 1},
        map_values=True
    )

    ramp_target = Instrument.setting(
        "R%d",
        """Sets Ramp Target. Can take the values "Z"ero, "L"ower, "U"pper.""",
        validator=strict_discrete_set,
        values={"Z": 0, "L": 1, "U": 2},
        map_values=True
    )

    persistent_mode_heater = Instrument.setting(
        "H%d",
        """Sets the persistent mode.
        Can take the values "O"ff, "C"onditional on, "U"nconditional on, "R"eset persistent current mode to zero.
        WARNING: Unconditional on will turn on the heater without any interlocks! Use at own risk.
        Standard mode to switch heater on is Conditional.
        Simplified Commands are "True" (Conditional on) and "False" (Off).""",
        validator=strict_discrete_set,
        values={"O": 0, "C": 1, "U": 2, "R": 9, False: 0, True: 1},
        map_values=True
    )

    ramp_rate = Instrument.setting(
        "A%08.5f",
        "Sets the Ramp rate in A/s.",
        validator=strict_range,
        values=[0, _RAMP_RATE_MAX],
    )

    external_trip = Instrument.setting(
        "X%d",
        """Sets the External trip:
         False = Off, True = Simple trip On, "Auto" = Auto-rampdown On.""",
        validator=strict_discrete_set,
        values={False: 0, True: 1, "Auto": 4},
        map_values=True
    )

    terminal_voltage_limit = Instrument.setting(
        "Y%04.1f",
        """Sets the terminal voltage limit to nn.n V.""",
        validator=strict_range,
        values=[0, _VOLTAGE_LIMIT_MAX]
    )

    heater_current_output = Instrument.setting(
        "W%03d",
        """Sets the Heater current output to nnn mA.""",
        validator=strict_range,
        values=[0, 255]
    )

    calibrate_tesla_per_amp = Instrument.setting(
        "C%08.6f",
        """Calibrate the output to Tesla per Amp value of the superconducting magnet.
         The Value is assumed to lie between 0.01 and 0.5 T/A
         and will be set to zero if a number outside this range is entered.""",
        validator=strict_range,
        values=[0.01, 0.5],
    )



    def __init__(self, resourceName,
                 ramp_rate_max=5,
                 voltage_limit_max=1,
                 **kwargs):
        super().__init__(
            resourceName,
            "Scientific Magnetics SMC",
            **kwargs
        )
        self._RAMP_RATE_MAX = ramp_rate_max  # A/s
        self._VOLTAGE_LIMIT_MAX = voltage_limit_max  # V


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
        self.unit = "T"
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

    def shutdown(self):
        self.persistent_mode_heater = True
        self.ramp_target = "Z"
        self.pause = False

