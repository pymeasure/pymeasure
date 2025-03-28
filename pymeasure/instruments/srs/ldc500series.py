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

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class LDC500(Instrument, SCPIMixin):
    """Represents an SRS LDC500 laser diode controller
    and provides a high-level interface for interacting with the instrument.

    Glossary:

        - CC: Constant Current
        - CP: Constant Power
        - CT: Constant Temperature
        - LD: Laser diode
        - PD: Photodiode
        - TEC: Thermo-electric controller
    """

    def __init__(self, adapter, name="LDC500 laser diode controller", **kwargs):
        super().__init__(adapter, name, **kwargs)

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
        "LDON %d",
        """Control whether the laser diode current source is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    ld_mode = Instrument.control(
        "SMOD?",
        "SMOD %s",
        """Control the laser diode control mode, "CC" (constant current) or "CP" (constant power).
        
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
        "SILD %f",
        """Control the laser diode current setpoint, in mA,
        when ``ld_mode == "CC"`` (float).""",
        check_set_errors=True,  # TODO: Check that this works
    )

    ld_current_limit = Instrument.control(
        "SILM?",
        "SILM %f",
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
        """Control the laser diode current range, "HIGH" or "LOW".

        - In "HIGH" mode the maximum laser diode current is 100mA.
        - In "LOW" mode the maximum laser diode current is 50mA.""",
        validator=strict_discrete_set,
        values={"HIGH": 1, "LOW": 0},
    )

    # --- ld voltage control ---

    ld_voltage = Instrument.measurement(
        "RVLD?",
        """Measure the laser diode voltage, in V (float).""",
    )

    ld_voltage_limit = Instrument.control(
        "SVLM?",
        "SVLM %f",
        """Control the laser diode voltage limit, in V (float).
        The current source turns off when the voltage limit is exceeded.""",
        validator=strict_range,
        values=(0.1, 10),
    )

    # ===============================
    # === PHOTODIODE (PD) CONTROL ===
    # ===============================

    pd_units = Instrument.control(
        "PDMW?",
        "PDMW %s",
        """Control the CP photodiode units, "mW" or "uA".""",
        validator=strict_discrete_set,
        values={"mW": "ON", "uA": "OFF"},
        map_values=True,
    )

    pd_bias = Instrument.control(
        "BIAS?",
        "BIAS %f",
        """Control the photodiode bias.""",
        validator=strict_range,
        values=(0, 5),
    )

    # --- pd current control ---

    pd_current = Instrument.measurement(
        "RWPD?",
        """Measure the photodiode current, in uA (float).""",
    )

    pd_current_setpoint = Instrument.control(
        "SIPD?",
        "SIPD %f",
        """Control the photodiode current setpoint, in uA,
        when ``ld_mode == "CP"`` and ``photodiode_units == "uA"`` (float).""",
        validator=strict_range,
        values=(0, 5000),
    )

    pd_current_limit = Instrument.control(
        "PILM?",
        "PILM %f",
        """Control the photodiode current limit, in uA,
        when ``ld_mode == "CP"`` and ``photodiode_units == "uA"`` (float).""",
        validator=strict_range,
        values=(0, 5000),
    )

    # --- pd power control ---

    pd_responsivity = Instrument.control(
        "RESP?",
        "RESP %f",
        """Control the photodiode responsivity, in uA/mW (float).

        Changing ``pd_responsivity``, either directly or via ``pd_calibrate``, indirectly changes:
        
        - ``pd_current_setpoint`` and ``pd_current_limit`` if ``pd_units == "mW"``
        - ``pd_power_setpoint`` and ``pd_power_limit`` if ``pd_units == "uA"``
        
        This is to maintain the relationships:
        
        - ``pd_current_setpoint = pd_power_setpoint x responsivity``
        - ``pd_current_limit = pd_power_limit x responsivity``
        """,
    )

    pd_calibrate = Instrument.setting(
        "CALP %f",
        """Set the photodiode responsivity, ``pd_responsivity``, via a real time power measurement,
        in mW.""",
    )

    pd_power_setpoint = Instrument.control(
        "SWPD?",
        "SWPD %f",
        """Control the photodiode optical power setpoint, in mW,
        when ``ld_mode == "CP"`` and ``photodiode_units == "mW"`` (float).""",
    )

    pd_power_limit = Instrument.control(
        "PWLM?",
        "PWLM %f",
        """Control the photodiode power limit, in mW,
        when ``ld_mode == "CP"`` and ``photodiode_units == "mW"`` (float).

        If ``pd_power_limit`` is reduced below ``pd_power_setpoint``,
        ``pd_power_setpoint`` is "dragged" down with ``pd_power_limit.""",
    )

    # ================================================
    # === THERMO-ELECTRIC CONTROLLER (TEC) CONTROL ===
    # ================================================

    tec_enabled = Instrument.control(
        "LDON?",
        "LDON %d",
        """Control whether the laser diode current source is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    tec_mode = Instrument.control(
        "TMOD?",
        "TMOD %s",
        """Control the TEC control mode, "CC" (constant current) or "CT" (constant temperature).

        If the TEC is on when ``tec_mode`` is changed, the controller performs a *bumpless transfer*
        to swich control modes on-the-fly.

        If ``tec_mode`` is changed from "CT" to "CC", the present value of the TEC current is
        measured, and the CC setpoint is set to this measurement.

        If ``tec_mode`` is changed from "CC" to "CT", the present value of the temperature sensor
        is measured, and the CT setpoint is set to this measurement.
        """,
    )

    # --- tec current control ---

    tec_current = Instrument.measurement("TIRD?", """Measure the TEC current, in A.""")

    tec_current_setpoint = Instrument.control(
        "TCUR?",
        "TCUR %f",
        """Control the TEC current setpoint, in A, when ``tec_mode == "CC".""",
        check_set_errors=True,  # TODO: Check that this works
    )

    tec_current_limit = Instrument.control(
        "TLIM?",
        "TCUR %f",
        """Control the TEC current limit, in A.

        If ``tec_current_limit`` is reduced below ``tec_current_setpoint``,
        ``tec_current_setpoint`` is *dragged* down with ``tec_current_limit``.
        """,
        validato=strict_range,
        values=(-4.5, 4.5),
    )

    # --- tec voltage control ---

    tec_voltage = Instrument.measurement("TVRD?", """Measure the TEC voltage, in V.""")

    # tec_voltage
    # tec_voltage_limit

    # tec_temperature_setpoint
    # tec_temperature_raw
    # tec_temperature
    # tec_temperature_low_limit
    # tec_temperature_high_limit
    # tec_temperature_limits

    # tec_resistance_setpoint
    # tec_resistance_low_limit
    # tec_resistance_high_limit
    # tec_resistance_limits
