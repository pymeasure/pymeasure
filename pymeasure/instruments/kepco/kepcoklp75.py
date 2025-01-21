from enum import IntFlag
from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import truncated_range, strict_discrete_set


# Error Codes for Confidence Testing
class KepcoErrorCode(IntFlag):
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
    Supports voltage/current setting, output enable, protection, and confidence tests.
    """
    _Vmax = 75  # Maximum Voltage
    _Imax = 16  # Maximum Current
    _Pmax = 1200  # Maximum Power in watts
    _Imin = 0.4  # Minimum programmable current

    def __init__(self, adapter, name="Kepco KLP75", **kwargs):
        """
        Initialize the Kepco KLP75 instrument with the specified adapter and settings.
        Parameters:
            adapter: The communication adapter (e.g., GPIB address).
            name (str): The name of the instrument.
            kwargs: Additional keyword arguments for Instrument initialization.
        """
        super().__init__(
            adapter=adapter,
            name=name,
            read_termination="\n",
            write_termination="\n",
            **kwargs
        )

    # Output Enable Control
    output_enabled = Instrument.control(
        "OUTPut:STATe?", "OUTPut:STATe %d",
        "Control whether the output is enabled.",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    # Voltage Measurement
    voltage = Instrument.measurement(
        "MEASure:VOLTage?",
        "Measure the voltage across output terminals (V).",
        cast=float,
    )

    # Current Measurement
    current = Instrument.measurement(
        "MEASure:CURRent?",
        "Measure the current through the output terminals (A).",
        cast=float,
    )

    # Voltage Setpoint
    voltage_setpoint = Instrument.control(
        "SOURce:VOLTage?", "SOURce:VOLTage %.1f",
        "Set or get the voltage setpoint (0-75V).",
        validator=truncated_range,
        values=[0, _Vmax],
    )

    # Current Setpoint
    current_setpoint = Instrument.control(
        "SOURce:CURRent?", "SOURce:CURRent %.1f",
        "Set or get the current setpoint (0.4-16A).",
        validator=truncated_range,
        values=[_Imin, _Imax],
    )

    def enable_protection(self, ovp=None, ocp=None):
        """Enable Overvoltage/Overcurrent Protection
        Parameters:
            ovp (float, optional): Overvoltage protection threshold (V).
            ocp (float, optional): Overcurrent protection threshold (A).
        """
        if ovp is not None:
            if ovp < 0 or ovp > self._Vmax:
                raise ValueError(f"OVP value {ovp} is out of range (0-{self._Vmax} V).")
            self.write(f"SOURce:VOLTage:PROTection {ovp}")
        if ocp is not None:
            if ocp < self._Imin or ocp > self._Imax:
                raise ValueError(f"OCP value {ocp} is out of range ({self._Imin}-{self._Imax} A).")
            self.write(f"SOURce:CURRent:PROTection {ocp}")

    # Status Query
    def status(self):
        """
        Query the status of the instrument.
        Returns:
            str: The status message returned by the instrument.
        """
        return self.ask("STATus:QUEStionable?")

    # Confidence Test
    confidence_test = Instrument.measurement(
        "*TST?",
        "Measure the result of the self-test and return the error code.",
        cast=int,
    )

    # Reset
    def reset(self):
        """
        Reset the instrument to its default state.
        """
        self.write("*RST")

    # Clear Errors
    def clear(self):
        """
        Clear the instrument's error queue.
        """
        self.write("*CLS")

    def get_id(self):
        """
        Query the instrument for its identification string.
        Returns:
            str: The identification string of the instrument.
        """
        return self.ask("*IDN?")
#
# if __name__ == "__main__":
#     psu = KepcoKLP75("GPIB0::8::INSTR")
#     psu.getID()
#     psu.output_enabled = 0
#     a = psu.output_enabled
#     print(a)
#     psu.current_setpoint = 1.0
#     psu.voltage_setpoint = 5.0
#     b = psu.voltage_setpoint
#     print(b)
#     c = psu.current
#     print(c)
#     psu.status()
#     psu.clear()
#     d = psu.confidence_test
#     print(d)
#     psu.reset()
#     psu.set_safe_output(voltage=20.0, current=5.0)  # Set 20V, 5A
#     print("Voltage Setpoint:", psu.voltage_setpoint)
#     print("Current Setpoint:", psu.current_setpoint)
#     psu.enable_protection(ovp=25.0, ocp=6.0)  # Set OVP to 25V and OCP to 6A
#     print("Protection enabled with OVP=25V and OCP=6A.")
