import logging
from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def check_error_decorator(func):
    """
    Decorator to automatically check for errors after executing a method.
    Logs errors and raises exceptions if the device reports an error.
    """
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)  # Call the wrapped method
        error = self.check_error()  # Check for errors
        if error and error != "No error":
            logging.error(f"Instrument error after {func.__name__}: {error}")
            raise RuntimeError(f"Instrument Error: {error}")
        return result
    return wrapper


class RigolDP932U(SCPIMixin, Instrument):
    """
    PyMeasure interface for the Rigol DP932U DC Power Supply Unit.

    This class provides methods to control the active channel,
    voltage, current, output state, and connection mode of the device.
    It also includes methods to measure voltage and current, reset the device,
    and check for errors.
    """

    def __init__(self, adapter, name="Rigol DP932U Power Supply", **kwargs):
        """
        Initialize the Rigol DP932U DC Power Supply Unit.

        :param adapter: The communication adapter (e.g., USB or GPIB) to connect to the instrument.
        :param kwargs: Additional arguments for instrument initialization.
        """

        if not adapter:
            raise ValueError("Adapter cannot be None. Provide a valid communication adapter.")
        kwargs.pop("name", None)
        super().__init__(adapter, name, **kwargs)

    control_channel = Instrument.control(
        ":INSTrument:NSELect?",
        ":INSTrument:NSELect %d",
        """Control the active channel (1, 2, or 3).

        :param int value: Channel number to set as active.
        :raises ValueError: If the channel number is outside the valid range [1, 3].
        """,
        validator=strict_discrete_set,
        values=[1, 2, 3],
    )

    control_voltage = Instrument.control(
        ":MEASure:VOLTage:DC?",
        ":SOURce:VOLTage %.3f",
        """Control the voltage of the selected channel in Volts (0 to 32).

        :param float value: Voltage level to set, within the range [0, 32].
        :raises ValueError: If the voltage is outside the valid range.
        """,
        validator=strict_range,
        values=[0, 32],
    )

    control_current = Instrument.control(
        ":MEASure:CURRent:DC?",
        ":SOURce:CURRent %.3f",
        """Control the current of the selected channel in Amps (0 to 3).

        :param float value: Current level to set, within the range [0, 3].
        :raises ValueError: If the current is outside the valid range.
        """,
        validator=strict_range,
        values=[0, 3],
    )

    control_output_state = Instrument.control(
        ":OUTPut:STATe?",
        ":OUTPut:STATe %s",
        """Control the output state of the selected channel (ON or OFF).

        :param str value: Output state, either "ON" to enable or "OFF" to disable the output.
        """,
        validator=strict_discrete_set,
        values=["OFF", "ON"],
        map_values=True,
    )

    control_connection_mode = Instrument.control(
        ":OUTPut:PAIR?",
        ":OUTPut:PAIR %s",
        """Control the connection mode (OFF, PAR, or SER).

        :param str value: Connection mode, either "OFF", "PAR" (parallel), or "SER" (series).
        """,
        validator=strict_discrete_set,
        values={"OFF": "OFF", "PAR": "PAR", "SER": "SER", "PARALLEL": "PAR", "SERIES": "SER"},
        map_values=True,
    )

    @check_error_decorator
    def measure_voltage(self):
        """
        Measure the voltage of the currently selected channel.
        :return: Measured voltage in Volts (float).
        """
        return float(self.ask(":MEASure:VOLTage:DC?"))

    @check_error_decorator
    def measure_current(self):
        """
        Measure the current of the currently selected channel.
        :return: Measured current in Amps (float).
        """
        return float(self.ask(":MEASure:CURRent:DC?"))

    @check_error_decorator
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

        :return: Identification string (str), including manufacturer,
         model, serial number, and firmware version.
        """
        return self.ask("*IDN?").strip()

    def check_error(self):
        """
        Check for system errors.

        :return: Error message (str) or "No error" if the system is
        operating correctly.
        """
        error = self.ask(":SYSTem:ERRor?").strip()
        if error and "No error" not in error:
            logging.error(f"System Error: {error}")
            raise RuntimeError(f"System Error: {error}")
        return error
