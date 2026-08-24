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

from enum import IntFlag
from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import truncated_range, strict_discrete_set


class KepcoErrorCode(IntFlag):
    """
    Enum for error codes during confidence testing.
    """
    OK = 0
    QUARTER_SCALE_VOLTAGE = 256
    MIN_VOLTAGE_OUTPUT = 128
    MAX_VOLTAGE_OUTPUT = 64
    LOOP_BACK_TEST = 32
    DIGITAL_POT = 16
    OPTICAL_BUFFER = 8
    FLASH = 4
    RAM = 2
    ROM = 1


class KepcoKLP75(SCPIMixin, Instrument):
    """
    Represents the Kepco KLP75 programmable power supply.

    This class provides methods for controlling and querying the device,
    including voltage/current setting, enabling/disabling output, applying
    protection settings, and performing confidence tests.
    """
    _Vmax = 75  # Maximum Voltage (V)
    _Imax = 16  # Maximum Current (A)
    _Pmax = 1200  # Maximum Power (W)
    _Imin = 0.4  # Minimum programmable current (A)

    def __init__(self, adapter, name="Kepco KLP75", **kwargs):
        """
        Initialize the Kepco KLP75 instrument with the specified adapter and settings.

        Parameters:
            adapter: Communication adapter (e.g., GPIB address).
            name (str): Name of the instrument.
            kwargs: Additional keyword arguments for Instrument initialization.
        """
        super().__init__(
            adapter=adapter,
            name=name,
            read_termination="\n",
            write_termination="\n",
            **kwargs
        )

    output_enabled = Instrument.control(
        "OUTPut:STATe?", "OUTPut:STATe %d",
        "Control whether the output is enabled or disabled.",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    voltage = Instrument.measurement(
        "MEASure:VOLTage?",
        "Measure the voltage across the output terminals (V).",
        cast=float,
    )

    current = Instrument.measurement(
        "MEASure:CURRent?",
        "Measure the current through the output terminals (A).",
        cast=float,
    )

    voltage_setpoint = Instrument.control(
        "SOURce:VOLTage?", "SOURce:VOLTage %.1f",
        "Set or get the voltage setpoint (0-75 V).",
        validator=truncated_range,
        values=[0, _Vmax],
    )

    current_setpoint = Instrument.control(
        "SOURce:CURRent?", "SOURce:CURRent %.1f",
        "Set or get the current setpoint (0.4-16 A).",
        validator=truncated_range,
        values=[_Imin, _Imax],
    )

    def enable_protection(self, ovp=None, ocp=None):
        """
        Control the enabling of overvoltage or overcurrent protection.

        Parameters:
            ovp (float, optional): Overvoltage protection threshold in volts (V).
            ocp (float, optional): Overcurrent protection threshold in amperes (A).

        Raises:
            ValueError: If the specified thresholds are out of valid range.
        """
        if ovp is not None:
            if ovp < 0 or ovp > self._Vmax:
                raise ValueError(f"OVP value {ovp} is out of range (0-{self._Vmax} V).")
            self.write(f"SOURce:VOLTage:PROTection {ovp}")
        if ocp is not None:
            if ocp < self._Imin or ocp > self._Imax:
                raise ValueError(f"OCP value {ocp} is out of range ({self._Imin}-{self._Imax} A).")
            self.write(f"SOURce:CURRent:PROTection {ocp}")

    def status(self):
        """
        Query the instrument's status.

        Returns:
            str: The status message returned by the instrument.
        """
        return self.ask("STATus:QUEStionable?")

    confidence_test = Instrument.measurement(
        "*TST?",
        "Measure the result of the self-test and return the error code.",
        cast=int,
    )

    def reset(self):
        """
        Control the reset of the instrument to its default state.
        """
        self.write("*RST")

    def clear(self):
        """
        Control the clearing of the instrument's error queue.
        """
        self.write("*CLS")

    def get_id(self):
        """
        Get the instrument's identification string.

        Returns:
            str: The identification string of the instrument.
        """
        return self.ask("*IDN?")
