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

from enum import StrEnum
import logging

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range, strict_discrete_set


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class LDP3811Mode(StrEnum):
    CONT_WAVE = "CW"
    CONST_DUTY_CYCLE = "CDC"
    CONST_PULSE_REP = "PRI"
    EXTERNAL = "EXT"


class LDP3811(Instrument):

    def __init__(self, adapter, name="ILX Lightwave LDP 3811", **kwargs):
        super().__init__(adapter, name, **kwargs)

    def check_errors(self):
        errors = self.values("ERRORS?")
        for err in errors:
            log.error(err)
        return errors

    output_enabled = Instrument.control(
        "OUTPUT?",
        "OUTPUT: %d",
        """Control whether the current output is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    mode = Instrument.control(
        "MODE?",
        "MODE:%s",
        """Control the mode as an :class:`LDP3811Mode` enum.""",
        validator=strict_discrete_set,
        values=LDP3811Mode,
    )

    # --- Current Control ---

    current = Instrument.measurement(
        "LDI?",
        """Measure the current, in mA (float).""",
    )

    def _current_setpoint_validator(self, value, values):
        return strict_range(
            value, (0, self.current_limit_500 if self.current_range_500_enabled else self.current)
        )

    current_setpoint = Instrument.control(
        "SET:LDI?",
        "LDI %g",
        """Control the current setpoint, in mA (float, strictly in range 0 to
        (:prop:`current_limit_500` if :prop:`current_range_500_enabled`
         else :prop:`current_limit_200`)).""",
        validator=_current_setpoint_validator,
        values=None,  # Placeholder for custom validator
    )

    current_range_500_enabled = Instrument.control(
        "RANGE?",
        "RANGE %d",
        """Control whether the 500mA output current range is enabled (bool).
        If False the 200mA output current range is selected.""",
        validator=strict_discrete_set,
        values={True: 500, False: 200},
        map_values=True,
    )

    current_limit_200 = Instrument.control(
        "LIMIT:I200?",
        "LIMIT:I200 %g",
        """Control the current limit for the 200mA range, in mA
        (float, strictly in range 0 to 200).""",
        validator=strict_range,
        values=(0, 200),
    )

    current_limit_500 = Instrument.control(
        "LIMIT:I500?",
        "LIMIT:I500 %g",
        """Control the current limit for the 500mA range, in mA
        (float, strictly in range 0 to 500).""",
        validator=strict_range,
        values=(0, 500),
    )

    # --- Pulse control ---

    duty_cycle = Instrument.measurement(
        "CDC?",
        """Measure the duty cycle, as a percentage (float).""",
    )

    def _duty_cycle_setpoint_validator(self, value, values):
        return strict_range(value, (100 * self.pulse_width / 6500, 100))

    duty_cycle_setpoint = Instrument.control(
        "SET:CDC?",
        "CDC %g",
        """Control the duty cycle (pulse width / pulse repetition interval) as a percentage
        (float, strictly in range (100 * :prop:`pulse_width` / 6500) to 100).""",
        validator=_duty_cycle_setpoint_validator,
        values=None,  # Placeholder for custom validator
    )

    pulse_repetition_interval = Instrument.measurement(
        "PRI?",
        """Measure the pulse repetition interval, in us (float).""",
    )

    def _pulse_repetition_interval_setpoint_validator(self, value, values):
        return strict_range(value, (max(1, self.pulse_width), 6500))

    pulse_repetition_interval_setpoint = Instrument.control(
        "SET:PRI?",
        "PRI %g",
        """Control the pulse repetition interval, in us
        (float, strictly in range max(1, :prop:`pulse_width`) to 6500).""",
        validator=_pulse_repetition_interval_setpoint_validator,
        values=None,  # Placeholder for custom validator
    )

    pulse_width = Instrument.measurement(
        "PW?",
        """Measure the pulse width, in us (float).""",
    )

    def _pulse_width_setpoint_validator(self, value, values):
        return strict_range(value, (0.1, self.pulse_repetition_interval))

    pulse_width_setpoint = Instrument.control(
        "SET:PW?",
        "PW %g",
        """Control the pulse width, in us (float strictly in range 0.1 to
        `~.pulse_repetition_interal`.""",
        validator=_pulse_width_setpoint_validator,
        values=None,  # Placeholder for custom validator
    )
