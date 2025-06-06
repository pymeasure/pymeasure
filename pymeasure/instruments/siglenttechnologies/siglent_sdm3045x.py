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
from pymeasure.instruments import SCPIMixin, Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class SiglentSDM3045X(SCPIMixin, Instrument):
    """
    Driver for the Siglent SDM3045X Digital Multimeter.

    Provides functionality for measuring voltage, current, and temperature.
    It also allows configuration of DC voltage range, filter settings,
    and switching between 2-wire and 4-wire measurement modes.
    """

    def __init__(self, adapter, name="Siglent SDM3045X Multimeter", **kwargs):
        """
        Initializes the instrument with the given VISA adapter.

        Args:
            adapter: VISA Adapter used to communicate with the instrument.
            name: Optional name for the instrument (default: "Siglent SDM3045X Multimeter").
        """
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    # Measurement Modes
    measurement_mode = Instrument.control(
        "CONFigure?",
        "CONFigure:%s",
        "Set the measurement mode "
        "'VOLT:DC', 'VOLT:AC', 'CURR:DC', 'CURR:AC', 'TEMP', and 'RES'.",
        validator=strict_discrete_set,
        values=["VOLT:DC", "VOLT:AC", "CURR:DC", "CURR:AC", "TEMP", "RES"],
    )

    # Voltage Measurement
    voltage = Instrument.measurement(
        "MEASure:VOLT:DC?",
        "Measure the DC voltage in volts.",
    )

    # Current Measurement
    current = Instrument.measurement(
        "MEASure:CURR:DC?",
        "Measure the DC current in amperes.",
    )

    # Temperature Measurement
    temperature = Instrument.measurement(
        "MEASure:TEMP?",
        "Measure the temperature in Celsius.",
    )

    # Set DC Voltage Range
    dc_voltage_range = Instrument.control(
        "VOLT:RANGe?",
        "VOLT:RANGe %g",
        "Set the DC voltage range in volts.",
        validator=strict_range,
        values=[0.1, 1000],
    )

    def reset(self):
        """
        Resets the instrument to its default state.
        This is equivalent to pressing the reset button on the instrument.
        """
        self.write("*RST")

    def identify(self):
        """
        Queries the device identity.

        Returns:
            str: The identity string of the instrument, typically including
                 manufacturer, model, and serial number.
        """
        return self.ask("*IDN?")

    def close(self):
        """
        Closes the instrument connection.

        Ensures the connection is properly terminated.
        """
        self.adapter.connection.close()
