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

from enum import IntEnum
from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class ThemometerType(IntEnum):
    """Enumerator of thermometer types supported by the SRS LDC500Series."""

    NTC10UA = 0
    NTC100UA = 1
    NTC1MA = 2
    NTCAUTO = 3
    RTD = 4
    LM335 = 5
    AD590 = 6


class LDC500Series(SCPIMixin, Instrument):
    """Represents an SRS LDC500Series laser diode controller
    and provides a high-level interface for interacting with the instrument.

    Glossary:

        - CC: Constant Current Mode
        - CP: Constant Power Mode
        - CT: Constant Temperature Mode
        - LD: Laser diode
        - PD: Photodiode
        - TEC: Thermo-electric controller
    """

    def __init__(self, adapter, name="LDC500Series laser diode controller", **kwargs):
        super().__init__(adapter, name, **kwargs)

    # =================================
    # === OVERIDE NON-SCPI COMMANDS ===
    # =================================

    options = None

    last_execution_error = Instrument.measurement(
        "LEXE?",
        """Get the last execution error code. This also resets the execution error code to 0.""",
    )

    last_command_error = Instrument.measurement(
        "LCME?",
        """Get the last command error code. This also resets the execution error code to 0.""",
    )

    def check_errors(self):
        """Read all errors from the instrument.

        :return: List of error entries.
        """
        errors = []
        for err in [self.last_execution_error, self.last_command_error]:
            if int(err) != 0:
                errors.append(err)
        return errors

    # =================
    # === INTERLOCK ===
    # =================

    interlock_closed = Instrument.measurement(
        "ILOC?",
        """Get the status of the interlock, True if closed, False if open.
        Laser will only operate with a closed interlock.""",
        values={True: "CLOSED", False: "OPEN"},
        map_values=True,
    )

    # ================================
    # === LASER DIODE (LD) CONTROL ===
    # ================================

    ld_enabled = Instrument.control(
        "LDON?",
        "LDON %s",
        """Control whether the laser diode current source is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    ld_mode = Instrument.control(
        "SMOD?",
        "SMOD %s",
        """Control the laser diode control mode, (str "CC" or "CP").

        If the laser is on when ``ld_mode`` is changed, the controller performs a *bumpless
        transfer* to switch control modes on-the-fly.

        If ``ld_mode`` is changed from "CC" to "CP", the present value of the photodiode current
        (or equivalently optical power) is measured and the CP setpoint is set to this measurement.
        If the measured photodiode current or power exceed the setpoint limit, an error is thrown.

        If the ``ld_mode`` is changed from "CP" to "CC", the present value of the laser current is
        measured and the CC setpoint set to this measurement. Note that, by hardware design, the
        measured laser current can never exceed the setpoint limit.
        """,
        validator=strict_discrete_set,
        values=["CC", "CP"],
        check_set_errors=True,
    )

    # --- direct ld current control ---

    ld_current = Instrument.measurement(
        "RILD?",
        """Measure the laser diode current, in mA (float).""",
    )

    ld_current_setpoint = Instrument.control(
        "SILD?",
        "SILD %g",
        """Control the laser diode current setpoint, in mA, when ``ld_mode == "CC"`` (float).""",
        check_set_errors=True,  # TODO: Check that this works
    )

    ld_current_limit = Instrument.control(
        "SILM?",
        "SILM %g",
        """Control the laser diode current limit, in mA (float).

        The ouput current is clamped to never exceed ``ld_current_limit`` under any conditions.
        If ``ld_current_limit`` is reduced below ``ld_current_setpoint``,
        ``ld_current_setpoint`` is "dragged" down with ``ld_current_limit``.
        """,
        check_set_errors=True,  # TODO: Check that this works
    )

    ld_current_range = Instrument.control(
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

    ld_voltage = Instrument.measurement(
        "RVLD?",
        """Measure the laser diode voltage, in V (float).""",
    )

    ld_voltage_limit = Instrument.control(
        "SVLM?",
        "SVLM %g",
        """Control the laser diode voltage limit, in V (float strictly in range 0.1 to 10).
        The current source turns off when the voltage limit is exceeded.""",
        validator=strict_range,
        values=(0.1, 10),
    )

    # --- ld modulation ---

    ld_modulation_enabled = Instrument.control(
        "MODU?",
        "MODU %s",
        """Control whether analog modulation of the laser diode is enabled (bool)""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    ld_modulation_bandwidth = Instrument.control(
        "SIBW?",
        "SIBW %s",
        """Control the laser diode modulation bandwidth (str "HIGH" or "LOW").

        The analog modulation input is DC coupled, with the –3 dB roll-off frequency dependent on
        ``ld_mode`` and ``ld_modulation_bandwidth``:

        .. csv-table::
            :header: , CC, CP

            "LOW", "10kHz", "100Hz"
            "HIGH", "1.2mhz", "5kHz"
        """,
        validator=strict_discrete_set,
        values=("HIGH", "LOW"),
    )

    # ===============================
    # === PHOTODIODE (PD) CONTROL ===
    # ===============================

    pd_units = Instrument.control(
        "PDMW?",
        "PDMW %s",
        """Control the CP photodiode units (str "mW" or "uA").""",
        validator=strict_discrete_set,
        values={"mW": "ON", "uA": "OFF"},
        map_values=True,
    )

    pd_bias = Instrument.control(
        "BIAS?",
        "BIAS %g",
        """Control the photodiode bias (float strictly in range 0 to 5).""",
        validator=strict_range,
        values=(0, 5),
    )

    # --- pd current control ---

    pd_current = Instrument.measurement(
        "RIPD?",
        """Measure the photodiode current, in uA (float).""",
    )

    pd_current_setpoint = Instrument.control(
        "SIPD?",
        "SIPD %g",
        """Control the photodiode current setpoint, in uA,
        when ``ld_mode == "CP"`` and ``photodiode_units == "uA"`` (float).""",
        validator=strict_range,
        values=(0, 5000),
    )

    pd_current_limit = Instrument.control(
        "PILM?",
        "PILM %g",
        """Control the photodiode current limit, in uA,
        when ``ld_mode == "CP"`` and ``photodiode_units == "uA"`` (float).""",
        validator=strict_range,
        values=(0, 5000),
    )

    # --- pd power control ---

    pd_responsivity = Instrument.control(
        "RESP?",
        "RESP %g",
        """Control the photodiode responsivity, in uA/mW (float).

        Changing ``pd_responsivity``, either directly or via ``pd_calibrate``, indirectly changes:

        - ``pd_current_setpoint`` and ``pd_current_limit`` if ``pd_units == "mW"``
        - ``pd_power_setpoint`` and ``pd_power_limit`` if ``pd_units == "uA"``

        This is to maintain the relationships:

        - ``pd_current_setpoint = pd_power_setpoint x responsivity``
        - ``pd_current_limit = pd_power_limit x responsivity``
        """,
    )

    def pd_calibrate(self, power):
        """Set the photodiode responsivity, ``pd_responsivity``, via a real time power measurement.

        Parmeters:
            power (float): Real time power measurement, in mW."""

        self.write("CALP %g" % power)

    pd_power = Instrument.measurement(
        "RWPD?",
        """Measure the photodiode power, in mW (float).""",
    )

    pd_power_setpoint = Instrument.control(
        "SWPD?",
        "SWPD %g",
        """Control the photodiode optical power setpoint, in mW,
        when ``ld_mode == "CP"`` and ``photodiode_units == "mW"`` (float).""",
    )

    pd_power_limit = Instrument.control(
        "PWLM?",
        "PWLM %g",
        """Control the photodiode power limit, in mW,
        when ``ld_mode == "CP"`` and ``photodiode_units == "mW"`` (float).

        If ``pd_power_limit`` is reduced below ``pd_power_setpoint``,
        ``pd_power_setpoint`` is "dragged" down with ``pd_power_limit``.""",
    )

    # ================================================
    # === THERMO-ELECTRIC CONTROLLER (TEC) CONTROL ===
    # ================================================

    tec_enabled = Instrument.control(
        "TEON?",
        "TEON %d",
        """Control whether the laser diode current source is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    tec_mode = Instrument.control(
        "TMOD?",
        "TMOD %s",
        """Control the TEC control mode (str "CC" or "CT").

        If the TEC is on when ``tec_mode`` is changed, the controller performs a *bumpless transfer*
        to swich control modes on-the-fly.

        If ``tec_mode`` is changed from "CT" to "CC", the present value of the TEC current is
        measured, and the CC setpoint is set to this measurement.

        If ``tec_mode`` is changed from "CC" to "CT", the present value of the temperature sensor
        is measured, and the CT setpoint is set to this measurement.
        """,
    )

    tec_thermometer_type = Instrument.control(
        "TSNR?",
        "TSNR %d",
        """Control the temperature sensor type (ThermometerType enum).""",
        get_process=lambda t: ThemometerType(t),
        set_process=lambda t: t.value,
    )

    # --- tec current control ---

    tec_current = Instrument.measurement(
        "TIRD?",
        """Measure the TEC current, in A.""",
    )

    tec_current_setpoint = Instrument.control(
        "TCUR?",
        "TCUR %g",
        """Control the TEC current setpoint, in A, when ``tec_mode == "CC"`` (float).""",
        check_set_errors=True,  # TODO: Check that this works
    )

    tec_current_limit = Instrument.control(
        "TLIM?",
        "TCUR %g",
        """Control the TEC current limit, in A (float strictly in range -4.5 to 4.5).

        If ``tec_current_limit`` is reduced below ``tec_current_setpoint``,
        ``tec_current_setpoint`` is *dragged* down with ``tec_current_limit``.
        """,
        validator=strict_range,
        values=(-4.5, 4.5),
    )

    # --- tec voltage control ---

    tec_voltage = Instrument.measurement(
        "TVRD?",
        """Measure the TEC voltage, in V (float).""",
    )

    tec_voltage_limit = Instrument.control(
        "TVLM?",
        "TVLM %g",
        """Control the TEC voltage limit, in V (float strictly in range -8.5 to 8.5).""",
        validator=strict_range,
        values=(-8.5, 8.5),
    )

    # --- tec temperature control ---

    tec_temperature = Instrument.measurement(
        "TTRD?",
        """Measure the TEC temperature, in °C (float).""",
    )

    tec_thermometer_raw = Instrument.measurement(
        "TRAW?",
        """Measure the raw thermometer reading,
        kΩ, V, or μA depending on the sensor type (float).""",
    )

    tec_temperature_setpoint = Instrument.control(
        "TEMP?",
        "TEMP %g",
        """Control the TEC temperature setpoint, in °C (float).""",
        check_set_errors=True,  # TODO: Check that this works
    )

    tec_temperature_low_limit = Instrument.control(
        "TMIN?",
        "TMIN %g",
        """Control the TEC low temperature limit, in °C (float).""",
        check_set_errors=True,  # TODO: Check that this works
    )

    tec_temperature_high_limit = Instrument.control(
        "TMAX?",
        "TMAX %g",
        """Control the TEC high temperature limit, in °C (float).""",
        check_set_errors=True,  # TODO: Check that this works
    )

    @property
    def tec_temperature_limits(self):
        """Control the TEC temperature limits, in °C (two-tuple of floats)."""
        return (self.tec_temperature_low_limit, self.tec_temperature_high_limit)

    @tec_temperature_limits.setter
    def tec_temperature_limits(self, temp_limits):
        self.tec_temperature_low_limit, self.tec_temperature_high_limit = temp_limits

    # --- tec resistance control ---

    tec_resistance_setpoint = Instrument.control(
        "TRTH?",
        "TRTH %g",
        """Control the TEC resistance setpoint, in kΩ (float).""",
        check_set_errors=True,  # TODO: Check that this works
    )

    tec_resistance_low_limit = Instrument.control(
        "TRMN?",
        "TRMN %g",
        """Control the TEC low resistance limit, in kΩ (float).""",
        check_set_errors=True,  # TODO: Check that this works
    )

    tec_resistance_high_limit = Instrument.control(
        "TRMX?",
        "TRMX %g",
        """Control the TEC high resistance limit, in kΩ (float).""",
        check_set_errors=True,  # TODO: Check that this works
    )

    @property
    def tec_resistance_limits(self):
        """Control the TEC resistance limits, in kΩ (two-tuple of floats)."""
        return (self.tec_resistance_low_limit, self.tec_resistance_high_limit)

    @tec_resistance_limits.setter
    def tec_resistance_limits(self, res_limits):
        self.tec_resistance_low_limit, self.tec_resistance_high_limit = res_limits
