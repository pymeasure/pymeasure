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

import logging
from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class RigolDP932U(SCPIMixin, Instrument):
    """
    PyMeasure interface for the Rigol DP932U DC Power Supply Unit.

    This class provides methods to control the active channel, voltage, current,
    output state, and connection mode of the device. It also includes methods
    to measure voltage and current, reset the device, and check for errors.
    """

    def __init__(self, adapter, name="Rigol DP932U Power Supply", **kwargs):
        """
        Initialize the Rigol DP932U DC Power Supply Unit.

        :param adapter: The communication adapter (e.g., USB or GPIB) to connect to the instrument.
        :type adapter: str

        :param name: The name of the instrument.
        :type name: str

        :param kwargs: Additional arguments for instrument initialization.
        :type kwargs: dict
        """
        super().__init__(adapter, name, **kwargs)

    active_channel = Instrument.control(
        ":INSTrument:NSELect?",
        ":INSTrument:NSELect %d",
        """Control the currently active channel (1, 2, or 3).

        :param int value: Channel number to set as active.

        :raises ValueError: If the channel number is outside the valid range [1, 3].
        """,
        validator=strict_discrete_set,
        values=[1, 2, 3],
    )

    voltage = Instrument.control(
        ":SOURce:VOLTage?",
        ":SOURce:VOLTage %.3f",
        """Control the voltage of the selected channel in Volts (0 to 32).

        :param float value: Voltage level to set, within the range [0, 32].

        :raises ValueError: If the voltage is outside the valid range.
        """,
        validator=strict_range,
        values=[0, 32],
    )

    current = Instrument.control(
        ":SOURce:CURRent?",
        ":SOURce:CURRent %.3f",
        """Control the current of the selected channel in Amps (0 to 3).

        :param float value: Current level to set, within the range [0, 3].

        :raises ValueError: If the current is outside the valid range.
        """,
        validator=strict_range,
        values=[0, 3],
    )

    output_enabled = Instrument.control(
        ":OUTPut:STATe?",
        ":OUTPut:STATe %d",
        """Control the output state of the selected channel as a boolean.

        :param bool value: `True` to enable output, `False` to disable output.
        """,
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True,
    )

    connection_mode = Instrument.control(
        ":OUTPut:PAIR?",
        ":OUTPut:PAIR %s",
        """Control the connection mode (OFF, PAR, or SER).

        :param str value: Connection mode, either "OFF", "PAR" (parallel), or "SER" (series).
        """,
        validator=strict_discrete_set,
        values={"OFF": "OFF", "PAR": "PAR", "SER": "SER", "PARALLEL": "PAR", "SERIES": "SER"},
        map_values=True,
    )

    measure_voltage = Instrument.measurement(
        ":MEASure:VOLTage:DC?",
        """Measure the voltage of the currently selected channel in Volts.

        :return: Measured voltage in Volts (float).
        """
    )

    measure_current = Instrument.measurement(
        ":MEASure:CURRent:DC?",
        """Measure the current of the currently selected channel in Amps.

        :return: Measured current in Amps (float).
        """
    )

    def reset(self):
        """
        Resets the device to its factory defaults.
        """
        logging.info("Resetting Rigol DP932U to factory defaults...")
        self.write("*RST")
        logging.info("Reset complete.")

    def get_device_id(self):
        """
        Query the device identification string.

        :return: Identification string (str), including manufacturer, model, serial number, and firmware version.
        """
        return self.ask("*IDN?").strip()

    def check_error(self):
        """
        Check for system errors.

        :return: Error message (str) or "No error" if the system is operating correctly.
        """
        error = self.ask(":SYSTem:ERRor?").strip()
        if error and "No error" not in error:
            logging.error(f"System Error: {error}")
            raise RuntimeError(f"System Error: {error}")
        return error
