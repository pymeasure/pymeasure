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

from enum import Enum
import logging

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range, strict_discrete_set


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class LDP3811Mode(str, Enum):
    """Enumerator of LDP3811 modes.

    Members:
        CONT_WAVE: Continuous wave current source (command 'CW').
        CONST_DUTY_CYCLE: Keep duty cycle (pulse width / pulse repetition interval) constant
            (command 'CDC').
        CONST_PULSE_REP: Keep the pulse repetition interval constant (command 'PRI').
        EXTERNAL: Trigger on the external trigger line (command 'EXT').
    """

    CONT_WAVE = "CW"
    CONST_DUTY_CYCLE = "CDC"
    CONST_PULSE_REP = "PRI"
    EXTERNAL = "EXT"

    def __str__(self):
        return str(self.value)


class LDP3811(Instrument):

    def __init__(self, adapter, name="ILX Lightwave LDP 3811", includeSCPI=False, **kwargs):
        super().__init__(adapter, name, includeSCPI, **kwargs)

    def check_errors(self):
        errors = self.values("ERRORS?")
        for err in errors:
            log.error(err)
        return errors

    output_enabled = Instrument.control(
        "OUTPUT?",
        "OUTPUT %d",
        """Control whether the current output is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    mode = Instrument.control(
        "MODE?",
        "MODE %s",
        """Control the mode as an :class:`LDP3811Mode` enum.""",
        validator=strict_discrete_set,
        values=LDP3811Mode,
        get_process=lambda v: LDP3811Mode(v),
    )

    # --- Current Control ---

    current = Instrument.measurement(
        "LDI?",
        """Measure the current, in mA (float).""",
    )

    @property
    def current_setpoint(self):
        """Control the current setpoint, in mA (float, strictly in range 0 to
        (:attr:`~.current_limit_500` if :attr:`~.current_range_500_enabled`
        else :attr:`~.current_limit_200`))."""
        return self.values("SET:LDI?")[0]

    @current_setpoint.setter
    def current_setpoint(self, value):
        current_limit = (
            self.current_limit_500 if self.current_range_500_enabled else self.current_limit_200
        )
        value = strict_range(value, (0, current_limit))
        self.write(f"LDI {value}")

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
        """Measure the duty cycle (pulse width / pulse repetition interval),
        as a percentage (float).""",
    )

    @property
    def duty_cycle_setpoint(self):
        """Control the duty cycle (pulse width / pulse repetition interval) as a percentage
        (float, strictly in range (100 * :attr:`~.pulse_width` / 6500) to 100)."""
        return self.values("SET:CDC?")[0]

    @duty_cycle_setpoint.setter
    def duty_cycle_setpoint(self, value):
        value = strict_range(value, (100 * self.pulse_width / 6500, 100))
        self.write(f"CDC {value}")

    pulse_repetition_interval = Instrument.measurement(
        "PRI?",
        """Measure the pulse repetition interval, in us (float).""",
    )

    @property
    def pulse_repetition_interval_setpoint(self):
        """Control the pulse repetition interval, in us
        (float, strictly in range max(1, :attr:`~.pulse_width`) to 6500)."""
        return self.values("SET:PRI?")[0]

    @pulse_repetition_interval_setpoint.setter
    def pulse_repetition_interval_setpoint(self, value):
        value = strict_range(value, (max(1, self.pulse_width), 6500))
        self.write(f"PRI {value}")

    pulse_width = Instrument.measurement(
        "PW?",
        """Measure the pulse width, in us (float).""",
    )

    @property
    def pulse_width_setpoint(self):
        """Control the pulse width, in us (float strictly in range 0.1 to
        :attr:`~.pulse_repetition_interval`."""
        return self.values("SET:PW?")[0]

    @pulse_width_setpoint.setter
    def pulse_width_setpoint(self, value):
        value = strict_range(value, (0.1, self.pulse_repetition_interval))
        self.write(f"PW {value}")
