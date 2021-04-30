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
        i = u = r = None
        log.warning(
            """
            Could not match regex to reply of output_parameters_amps.
            Reply received: 
            %s
            """ % reply
        )
    else:
        i = float(match.group(1))
        u = float(match.group(2))
        r = match.group(3)
    return dict(current=i, voltage=u, ramp=r)


def extract_value_output_parameters_tesla(reply) -> dict:
    match = _reN.match(reply)
    if not match:
        f = u = r = None
        log.warning(
            """
            Could not match regex to reply of output_parameters_tesla.
            Reply received: 
            %s
            """ % reply
        )
    else:
        f = float(match.group(1))
        u = float(match.group(2))
        r = match.group(3)

    return dict(field=f, voltage=u, ramp=r)


def extract_value_magnet_status(reply) -> dict:
    match_f = _reJF.match(reply)
    match_i = _reJI.match(reply)

    if match_f:
        return dict(heater=int(match_f.group(2)),
                    value=float(match_f.group(1)),
                    units=1)
    elif match_i:
        return dict(heater=int(match_i.group(2)),
                    value=float(match_i.group(1)),
                    units=0)
    else:
        log.warning(
            """
            Could not match regex to reply of magnet_status.
            Reply received: 
            %s
            """ % reply
        )
        return dict(heater=None,
                    value=None,
                    units=None)


def extract_value_current_status(reply) -> dict:
    match_f = _reKF.match(reply)
    match_i = _reKI.match(reply)

    if match_f:
        return dict(
            ramp_target=int(match_f.group(1)),
            ramp_status=int(match_f.group(2)),
            pause=int(match_f.group(3)),
            external_trip=int(match_f.group(4)),
            heater_mode=int(match_f.group(5)),
            error_code=int(match_f.group(6)),
            quench_value=float(match_f.group(7)),
            units=1
        )
    elif match_i:
        return dict(
            ramp_target=int(match_i.group(1)),
            ramp_status=int(match_i.group(2)),
            pause=int(match_i.group(3)),
            external_trip=int(match_i.group(4)),
            heater_mode=int(match_i.group(5)),
            error_code=int(match_i.group(6)),
            quench_value=float(match_i.group(7)),
            units=0
        )
    else:
        log.warning(
            """
            Could not match regex to reply of current_status.
            Reply received: 
            %s
            """ % reply
        )
        return dict(
            ramp_target=None,
            ramp_status=None,
            pause=None,
            external_trip=None,
            heater_mode=None,
            error_code=None,
            quench_value=None,
            units=None
        )


def extract_value_operating_parameters(reply) -> dict:
    match = _reO.match(reply)

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
        log.warning(
            """
            Could not match regex to reply of operating_parameters.
            Reply received: 
            %s
            """ % reply
        )
        return dict(
            ramp_rate=None,
            switch_direction=None,
            units=None,
            front_panel_lock=None,
            heater_current_mA=None,
            telsa_per_amps=None
        )



def extract_value_set_point_status(reply) -> dict:
    match_f = _reSF.match(reply)
    match_i = _reSI.match(reply)

    if match_f:
        return dict(
            units=int(match_f.group(1)),
            upper_set_point=float(match_f.group(2)),
            lower_set_point=float(match_f.group(3)),
            terminal_voltage=float(match_f.group(4))
        )
    elif match_i:
        return dict(
            units=int(match_i.group(1)),
            upper_set_point=float(match_i.group(2)),
            lower_set_point=float(match_i.group(3)),
            terminal_voltage=float(match_i.group(4))
        )
    else:
        log.warning(
            """
            Could not match regex to reply of set_point_status.
            Reply received: 
            %s
            """ % reply
        )
        return dict(
            units=None,
            upper_set_point=None,
            lower_set_point=None,
            terminal_voltage=None
        )


class SciMag(Instrument):
    """ Represents the Scientific Magnetics (Twickenham Scientific Instruments)
    Superconducting Magnet Controller SciMag S-11-52-13.

    Provides a high-level interface for
    interacting with the instrument.
    WARNING: Use at your own risk!
    Faulty operation of a superconducting magnet can lead to severe damage or injury!
    Read the manual: https://www.twicksci.co.uk/manuals/pdf/smc552+.pdf
    """

    _RAMP_RATE_MAX = 5
    _VOLTAGE_LIMIT_MAX = 1

    pause = Instrument.setting(
        "P%d",
        """A boolean property that controls the pause-status,
         which takes the values True (pause) and False (continue)
         """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    unit = Instrument.setting(
        "T%d",
        """Sets the units displayed and can take the values
         "A"mpere or "T"esla
         """,
        validator=strict_discrete_set,
        values={"A": 0, "T": 1},
        map_values=True
    )

    reverse_switch_on = Instrument.setting(
        "D%d",
        """Sets the direction of the reversing switch, if installed.
        Forward if switch is off; Reverse if switch is on.
        Takes boolean value. True = Switch is on, Field is reverse.
        WARNING: Change only if Magnet has been ramped to Zero!
        """,
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    ramp_target = Instrument.setting(
        "R%d",
        """Sets Ramp Target. Can take the values "Z"ero, "L"ower, "U"pper.
        """,
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
        Simplified Commands are "True" (Conditional on) and "False" (Off).
        """,
        validator=strict_discrete_set,
        values={"O": 0, "C": 1, "U": 2, "R": 9, False: 0, True: 1},
        map_values=True
    )

    ramp_rate = Instrument.setting(
        "A%08.5f",
        """Sets the Ramp rate in A/s.""",
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
         and will be set to zero if a number outside this range is entered.
         """,
        validator=strict_range,
        values=[0.01, 0.5],
    )

    lower_setpoint = Instrument.setting(
        "L%08.4f",
        """Sets the lower setpoint. 
        Unit depends on the unit set in the magnet controller.
        Unit can be "T" or "A" and must be set before.
        """,
        validator=strict_range,
        values=[0, 200]
    )

    upper_setpoint = Instrument.setting(
        "U%08.4f",
        """Sets the upper setpoint. 
        Unit depends on the unit set in the magnet controller.
        Unit can be "T" or "A" and must be set before.
        """,
        validator=strict_range,
        values=[0, 200]
    )

    output_parameters_amps = Instrument.measurement(
        "G",
        """Returns dict of output parameters.""",
        preprocess_reply=extract_value_output_parameters_amps
    )

    output_parameters_tesla = Instrument.measurement(
        "N",
        """Returns dict of output parameters.""",
        preprocess_reply=extract_value_output_parameters_tesla
    )

    magnet_status = Instrument.measurement(
        "J",
        "Returns dict of magnet status.",
        preprocess_reply=extract_value_magnet_status
    )

    current_status = Instrument.measurement(
        "K",
        "Returns dict of current status.",
        preprocess_reply=extract_value_current_status
    )

    operating_parameters = Instrument.measurement(
        "O",
        "Returns dict of operation parameters",
        preprocess_reply=extract_value_operating_parameters
    )

    set_point_status = Instrument.measurement(
        "S",
        "Returns dict of set point status.",
        preprocess_reply=extract_value_set_point_status
    )


    def __init__(self, resourceName,
                 ramp_rate_max=5,
                 voltage_limit_max=1,
                 field_max=10,
                 **kwargs):
        super().__init__(
            resourceName,
            "Scientific Magnetics SMC",
            includeSCPI = False
            **kwargs
        )
        self._RAMP_RATE_MAX = ramp_rate_max  # A/s
        self._VOLTAGE_LIMIT_MAX = voltage_limit_max  # V
        self._T_MAX  # T

    @property
    def tesla(self) -> float:
        """
        High-Level property for setting and getting the field in the solenoid.

        If installed, the setter-funktion toggles the
        reversal-switch automatically at zero-field.
        """
        self.unit = "T"
        value = self.output_parameters_tesla["field"]
        if self.operating_parameters["switch_direction"] == 0:
            sign = +1
            return float(sign * value)
        elif self.operating_parameters["switch_direction"] == 1:
            sign = -1
            return float(sign * value)

    @tesla.setter
    def tesla(self, value: float):
        self.unit = "T"
        if value == 0:
            self.ramp_target = "Z"
        elif abs(value) < self.MAX_FIELD_TESLA:
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
                self.ramp_target = "Z"
                # At zero-field: switch direction.
                while not (self.current_status["ramp_status"] == 1):
                    time.sleep(1)
                if value > 0:
                    self.reverse_switch_on = False
                elif value < 0:
                    self.reverse_switch_on = True
                self.upper_setpoint_tesla(abs(value))
            self.ramp_target = "U"
        else:
            log.warning("Intended field was: %08.4f T.\nAllowed maximum field is: %08.4f T" %(value, self._T_MAX))
            raise UserWarning("Intended field value exceeded range of the solenoid. Value was NOT set.")

    def shutdown(self):
        """Brings the instrument to a safe and stable state.
        """
        self.isShutdown = True
        log.info("Shutting down %s" % self.name)
        self.persistent_mode_heater = True
        self.ramp_target = "Z"
        self.pause = False

