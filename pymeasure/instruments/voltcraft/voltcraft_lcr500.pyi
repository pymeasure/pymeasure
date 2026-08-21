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

from __future__ import annotations
from typing import Literal

from pymeasure.instruments import Instrument
from pymeasure.adapters import Adapter

MeasurementFrequencies = Literal[
    100,
    200,
    300,
    400,
    500,
    600,
    700,
    800,
    900,
    1000,
    2000,
    3000,
    4000,
    5000,
    6000,
    7000,
    8000,
    9000,
    10000,
    20000,
    30000,
    40000,
    50000,
    60000,
    70000,
    80000,
    90000,
    100000,
]
MeasurementRanges = Literal["auto", 10, 100, 1_000, 10_000, 100_000]
SignalLevels = Literal[300, 600]
MainParameters = Literal["r", "l", "c", "z", "auto"]
SecondaryParameters = Literal["x", "q", "d", "theta", "esr"]

class LCR500(Instrument):
    """Voltcraft LCR-500 LCR Meter.

    Args:
        adapter: A PyVISA resource name or adapter instance.
        name: Name of the instrument instance.
        kwargs: Additional keyword arguments passed to the parent Instrument class.
    """

    def __init__(
        self, adapter: Adapter | str, name: str = "Voltcraft LCR-500", **kwargs
    ) -> None: ...
    def go_to_local(self) -> None:
        """Set the instrument to local mode."""
        ...

    @property
    def frequency(self) -> float:
        """Return the measurement frequency in Hz.

        Returns:
            float: Frequency in Hz.
        """
        ...

    @frequency.setter
    def frequency(
        self,
        _value: MeasurementFrequencies,
    ) -> None:
        """Set the measurement frequency in Hz.

        Args:
            _value (int): Frequency in Hz. Allowed values are between 100 and 100_000.
        """
        ...

    @property
    def main_parameter(self) -> MainParameters:
        """Return the main measurement parameter.

        Returns:
            str: Main measurement parameter, one of 'r', 'l', 'c', 'z', or 'auto'.
        """
        ...

    @main_parameter.setter
    def main_parameter(self, _value: MainParameters) -> None:
        """Set the main measurement parameter.

        Args:
            _value (str): Main measurement parameter, one of 'r', 'l', 'c', 'z', or 'auto'.
        """
        ...

    @property
    def secondary_parameter(self) -> SecondaryParameters:
        """Return the secondary measurement parameter.

        Returns:
            str: Secondary measurement parameter, one of 'x', 'q', 'd', 'theta', or 'esr'.
        """
        ...

    @secondary_parameter.setter
    def secondary_parameter(self, _value: SecondaryParameters) -> None:
        """Set the secondary measurement parameter.

        Args:
            _value (str): Secondary measurement parameter, one of 'x', 'q', 'd', 'theta', or 'esr'.
        """
        ...

    @property
    def measurement_range(self) -> MeasurementRanges:
        """Return the measurement range.

        Returns:
            str | int: Measurement range, either 'auto' or one of 10, 100, 1_000, 10_000, 100_000.
        """
        ...

    @measurement_range.setter
    def measurement_range(self, _value: MeasurementRanges) -> None:
        """Set the measurement range.

        Args:
            _value (str | int): Measurement range,
                either 'auto' or one of 10, 100, 1_000, 10_000, 100_000.
        """
        ...

    @property
    def level(self) -> SignalLevels:
        """Return the signal level in mVrms.

        Returns:
            int: Signal level in mVrms, either 300 or 600.
        """
        ...

    @level.setter
    def level(self, _value: SignalLevels) -> None:
        """Set the signal level in mVrms.

        Args:
            _value (int): Signal level in mVrms, either 300 or 600.
        """
        ...

    @property
    def equivalent_circuit_serial_enabled(self) -> bool:
        """Return whether the equivalent circuit is set to serial.

        Returns:
            bool: True if equivalent circuit is set to serial, False if set to parallel."""
        ...

    @equivalent_circuit_serial_enabled.setter
    def equivalent_circuit_serial_enabled(self, _value: bool) -> None:
        """Set the equivalent circuit type to serial.

        Args:
            _value (bool): If True, set equivalent circuit to serial. If False, set to parallel.
        """
        ...

    @property
    def fetch(self) -> list[float]:
        """Return a measurement result from the instrument.

        Returns:
            list[float]: A list of [primary_value, secondary_value, range_used].
        """
        ...
