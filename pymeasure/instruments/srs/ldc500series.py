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

from time import sleep
from enum import IntEnum

from pymeasure.errors import Error
from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class ThermometerType(IntEnum):
    """Enumerator of thermometer types supported by the SRS LDC500Series."""

    NTC10UA = 0
    NTC100UA = 1
    NTC1MA = 2
    NTCAUTO = 3
    RTD = 4
    LM335 = 5
    AD590 = 6


class LDC500SeriesBase(SCPIMixin, Instrument):
    """Base class for LDC500Series classes."""

    def __init__(self, adapter, name="LDC500Series laser diode controller", **kwargs):
        super().__init__(adapter, name, **kwargs)

    @property
    def options(self):
        """Get options not implemented, raises ``NotImplementedError``"""
        raise NotImplementedError("options not implemented in LDC500series.")

    @property
    def next_error(self):
        """Get next error not implemented, raises: ``NotImplementedError``"""
        raise NotImplementedError("next_error not implemented in LDC500series.")

    last_execution_error = Instrument.measurement(
        "LEXE?",
        """Get the last execution error code. This also resets the execution error code to 0.""",
        cast=int,
    )

    last_command_error = Instrument.measurement(
        "LCME?",
        """Get the last command error code. This also resets the execution error code to 0.""",
        cast=int,
    )

    def check_errors(self):
        """Read all errors from the instrument.

        :return: List of [``last_execution_error``, ``last_command_error``]
        """
        return [self.last_execution_error, self.last_command_error]

    def check_set_errors(self):
        """Check for errors after having set a property, and raise an error if any are present."""
        # FIXME: The LDC500 has a delay between a command being executed and an error being logged.
        #        *OPC? didn't work to wait for the previous command, so instead as short a delay
        #        as possible has been put in. It's not a nice solution and any ideas would be
        #        appreciated.
        sleep(0.015)
        errors = self.check_errors()
        if errors == [0, 0]:
            return []
        raise Error(f"Error setting value: {errors}")


class LDC500Series(LDC500SeriesBase):
    """Represents an SRS LDC500Series laser diode controller
    and provides a high-level interface for interacting with the instrument.

    Attributes
    ----------
    ld : LDC500SeriesLDSubsystem
        Provides access to laser diode control (e.g. ``ldc.ld.mode``)
    pd : LDC500SeriesPDSubsystem
        Provides access to photodiode control (e.g. ``ldc.pd.power``)
    tec : LDC500SeriesTECSubsystem
        Provides access to TEC control (e.g. ``ldc.tec.current``)

    Example
    ~~~~~~~

    .. code-block:: python

        ldc = LDC500Series("GPIB::5")
        ldc.ld.enabled = True
        temperature = ldc.tec.temperature

    Glossary:
    ~~~~~~~~~

        - CC: Constant Current Mode
        - CP: Constant Power Mode
        - CT: Constant Temperature Mode
        - LD: Laser diode
        - PD: Photodiode
        - TEC: Thermo-electric controller
    """

    def __init__(self, adapter, name="LDC500Series", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self.ld = LDC500SeriesLDSubsystem(self)
        self.pd = LDC500SeriesPDSubsystem(self)
        self.tec = LDC500SeriesTECSubsystem(self)


class LDC500SeriesLDSubsystem(LDC500SeriesBase):
    """Subsystem of LDC500Series for control of the laser-diode (LD)."""

    def __init__(self, adapter, name="LDC500Series LD Subsystem", **kwargs):
        super().__init__(adapter, name, **kwargs)

    interlock_closed = Instrument.measurement(
        "ILOC?",
        """Get the status of the interlock, True if closed, False if open.
        Laser will only operate with a closed interlock.""",
        values={True: "CLOSED", False: "OPEN"},
        map_values=True,
    )

    enabled = Instrument.control(
        "LDON?",
        "LDON %s",
        """Control whether the laser diode current source is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    mode = Instrument.control(
        "SMOD?",
        "SMOD %s",
        """Control the laser diode control mode, (str "CC" or "CP").

        If the laser is on when ``mode`` is changed, the controller performs a *bumpless
        transfer* to switch control modes on-the-fly.

        If ``mode`` is changed from "CC" to "CP", the present value of the photodiode current
        (or equivalently optical power) is measured and the CP setpoint is set to this measurement.
        If the measured photodiode current or power exceed the setpoint limit, an error is thrown.

        If the ``mode`` is changed from "CP" to "CC", the present value of the laser current is
        measured and the CC setpoint set to this measurement. Note that, by hardware design, the
        measured laser current can never exceed the setpoint limit.
        """,
        validator=strict_discrete_set,
        values=["CC", "CP"],
        check_set_errors=True,
    )

    # --- direct ld current control ---

    current = Instrument.measurement(
        "RILD?",
        """Measure the laser diode current, in mA (float).""",
    )

    current_setpoint = Instrument.control(
        "SILD?",
        "SILD %g",
        """Control the laser diode current setpoint, in mA, when ``mode == "CC"`` (float).""",
        check_set_errors=True,
    )

    current_limit = Instrument.control(
        "SILM?",
        "SILM %g",
        """Control the laser diode current limit, in mA (float).

        The ouput current is clamped to never exceed ``current_limit`` under any conditions.
        If ``current_limit`` is reduced below ``current_setpoint``,
        ``current_setpoint`` is "dragged" down with ``current_limit``.
        """,
        check_set_errors=True,
    )

    current_range = Instrument.control(
        "RNGE?",
        "RNGE %s",
        """Control the laser diode current range (str "HIGH" or "LOW").

        The currents corresponding to current range depend on the model:

        .. csv-table::
            :header: , LDC500, LDC501, LDC502

            "HIGH", "100mA", "500mA", "2000mA"
            "LOW", "50mA", "250mA", "1000mA"
        """,
        validator=strict_discrete_set,
        values=("HIGH", "LOW"),
    )

    # --- ld voltage control ---

    voltage = Instrument.measurement(
        "RVLD?",
        """Measure the laser diode voltage, in V (float).""",
    )

    voltage_limit = Instrument.control(
        "SVLM?",
        "SVLM %g",
        """Control the laser diode voltage limit, in V (float strictly in range 0.1 to 10).
        The current source turns off when the voltage limit is exceeded.""",
        validator=strict_range,
        values=(0.1, 10),
    )

    # --- ld modulation ---

    modulation_enabled = Instrument.control(
        "MODU?",
        "MODU %s",
        """Control whether analog modulation of the laser diode is enabled (bool)""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    modulation_bandwidth = Instrument.control(
        "SIBW?",
        "SIBW %s",
        """Control the laser diode modulation bandwidth (str "HIGH" or "LOW").

        The analog modulation input is DC coupled, with the –3 dB roll-off frequency dependent on
        ``mode`` and ``modulation_bandwidth``:

        .. csv-table::
            :header: , CC, CP

            "LOW", "10kHz", "100Hz"
            "HIGH", "1.2mhz", "5kHz"
        """,
        validator=strict_discrete_set,
        values=("HIGH", "LOW"),
    )


class LDC500SeriesPDSubsystem(LDC500SeriesBase):
    """Subsystem of LDC500Series for control of the photodiode (PD)."""

    def __init__(self, adapter, name="LDC500Series PD Subsystem", **kwargs):
        super().__init__(adapter, name, **kwargs)

    units = Instrument.control(
        "PDMW?",
        "PDMW %s",
        """Control the CP photodiode units (str "mW" or "uA").""",
        validator=strict_discrete_set,
        values={"mW": "ON", "uA": "OFF"},
        map_values=True,
    )

    bias = Instrument.control(
        "BIAS?",
        "BIAS %g",
        """Control the photodiode bias (float strictly in range 0 to 5).""",
        validator=strict_range,
        values=(0, 5),
    )

    # --- pd current control ---

    current = Instrument.measurement(
        "RIPD?",
        """Measure the photodiode current, in uA (float).""",
    )

    current_setpoint = Instrument.control(
        "SIPD?",
        "SIPD %g",
        """Control the photodiode current setpoint, in uA,
        when ``mode == "CP"`` and ``photodiode_units == "uA"`` (float).""",
        check_set_errors=True,
    )

    current_limit = Instrument.control(
        "PILM?",
        "PILM %g",
        """Control the photodiode current limit, in uA,
        when ``mode == "CP"`` and ``photodiode_units == "uA"`` (float).""",
        validator=strict_range,
        values=(0, 5000),
    )

    # --- pd power control ---

    responsivity = Instrument.control(
        "RESP?",
        "RESP %g",
        """Control the photodiode responsivity, in uA/mW (float).

        Changing ``responsivity``, either directly or via ``calibrate``, indirectly changes:

        - ``current_setpoint`` and ``current_limit`` if ``units == "mW"``
        - ``power_setpoint`` and ``power_limit`` if ``units == "uA"``

        This is to maintain the relationships:

        - ``current_setpoint = power_setpoint x responsivity``
        - ``current_limit = power_limit x responsivity``
        """,
    )

    def calibrate(self, power):
        """Set the photodiode responsivity, ``responsivity``, via a real time power measurement.

        Parmeters:
            power (float): Real time power measurement, in mW."""

        self.write("CALP %g" % power)

    power = Instrument.measurement(
        "RWPD?",
        """Measure the photodiode power, in mW (float).""",
    )

    power_setpoint = Instrument.control(
        "SWPD?",
        "SWPD %g",
        """Control the photodiode optical power setpoint, in mW,
        when ``mode == "CP"`` and ``photodiode_units == "mW"`` (float).""",
    )

    power_limit = Instrument.control(
        "PWLM?",
        "PWLM %g",
        """Control the photodiode power limit, in mW,
        when ``mode == "CP"`` and ``photodiode_units == "mW"`` (float).

        If ``power_limit`` is reduced below ``power_setpoint``,
        ``power_setpoint`` is "dragged" down with ``power_limit``.""",
    )


class LDC500SeriesTECSubsystem(LDC500SeriesBase):
    """Subsystem of LDC500Series for control of the thermo-electric-controller (TEC)."""

    def __init__(self, adapter, name="LDC500Series TEC Subsystem", **kwargs):
        super().__init__(adapter, name, **kwargs)

    enabled = Instrument.control(
        "TEON?",
        "TEON %d",
        """Control whether the laser diode current source is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    mode = Instrument.control(
        "TMOD?",
        "TMOD %s",
        """Control the TEC control mode (str "CC" or "CT").

        If the TEC is on when ``mode`` is changed, the controller performs a *bumpless transfer*
        to swich control modes on-the-fly.

        If ``mode`` is changed from "CT" to "CC", the present value of the TEC current is
        measured, and the CC setpoint is set to this measurement.

        If ``mode`` is changed from "CC" to "CT", the present value of the temperature sensor
        is measured, and the CT setpoint is set to this measurement.
        """,
    )

    thermometer_type = Instrument.control(
        "TSNR?",
        "TSNR %d",
        """Control the temperature sensor type (ThermometerType enum).""",
        get_process=lambda t: ThermometerType(t),
        set_process=lambda t: t.value,
    )

    # --- tec current control ---

    current = Instrument.measurement(
        "TIRD?",
        """Measure the TEC current, in A.""",
    )

    current_setpoint = Instrument.control(
        "TCUR?",
        "TCUR %g",
        """Control the TEC current setpoint, in A, when ``mode == "CC"`` (float).""",
        check_set_errors=True,
    )

    current_limit = Instrument.control(
        "TILM?",
        "TILM %g",
        """Control the TEC current limit, in A (float strictly in range -4.5 to 4.5).

        If ``current_limit`` is reduced below ``current_setpoint``,
        ``current_setpoint`` is *dragged* down with ``current_limit``.
        """,
        validator=strict_range,
        values=(-4.5, 4.5),
    )

    # --- tec voltage control ---

    voltage = Instrument.measurement(
        "TVRD?",
        """Measure the TEC voltage, in V (float).""",
    )

    voltage_limit = Instrument.control(
        "TVLM?",
        "TVLM %g",
        """Control the TEC voltage limit, in V (float strictly in range -8.5 to 8.5).""",
        validator=strict_range,
        values=(-8.5, 8.5),
    )

    # --- tec temperature control ---

    temperature = Instrument.measurement(
        "TTRD?",
        """Measure the TEC temperature, in °C (float).""",
    )

    thermometer_raw = Instrument.measurement(
        "TRAW?",
        """Measure the raw thermometer reading,
        kΩ, V, or μA depending on the sensor type (float).""",
    )

    temperature_setpoint = Instrument.control(
        "TEMP?",
        "TEMP %g",
        """Control the TEC temperature setpoint, in °C (float).""",
        check_set_errors=True,
    )

    temperature_low_limit = Instrument.control(
        "TMIN?",
        "TMIN %g",
        """Control the TEC low temperature limit, in °C (float).""",
        check_set_errors=True,
    )

    temperature_high_limit = Instrument.control(
        "TMAX?",
        "TMAX %g",
        """Control the TEC high temperature limit, in °C (float).""",
        check_set_errors=True,
    )

    @property
    def temperature_limits(self):
        """Control the TEC temperature limits, in °C (two-tuple of floats)."""
        return (self.temperature_low_limit, self.temperature_high_limit)

    @temperature_limits.setter
    def temperature_limits(self, temp_limits):
        self.temperature_low_limit, self.temperature_high_limit = temp_limits

    # --- tec resistance control ---

    resistance_setpoint = Instrument.control(
        "TRTH?",
        "TRTH %g",
        """Control the TEC resistance setpoint, in kΩ (float).""",
        check_set_errors=True,
    )

    resistance_low_limit = Instrument.control(
        "TRMN?",
        "TRMN %g",
        """Control the TEC low resistance limit, in kΩ (float).""",
        check_set_errors=True,
    )

    resistance_high_limit = Instrument.control(
        "TRMX?",
        "TRMX %g",
        """Control the TEC high resistance limit, in kΩ (float).""",
        check_set_errors=True,
    )

    @property
    def resistance_limits(self):
        """Control the TEC resistance limits, in kΩ (two-tuple of floats)."""
        return (self.resistance_low_limit, self.resistance_high_limit)

    @resistance_limits.setter
    def resistance_limits(self, res_limits):
        self.resistance_low_limit, self.resistance_high_limit = res_limits
