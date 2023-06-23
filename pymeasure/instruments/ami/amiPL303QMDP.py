"""The PL303 single channel 30V 3A power supply."""
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class PL303QMDP(Instrument):
    """Represents the PL303QMD-P from Aim-TTI."""

    def __init__(self, resource_name, **kwargs):
        """Create a PL303 instrument."""
        super().__init__(resource_name, "PL303", **kwargs)

    id = Instrument.measurement("*IDN?", """ Reads the instrument identification """)

    voltage1 = Instrument.control(
        "V1?",
        "V1 %g",
        """ A floating point property that controls the voltage output
            in Volts. This property can be set.
        """,
        validator=strict_range,
        values=[0, 30],
        get_process=lambda v: float(v.replace("V1", "")),
    )

    current1 = Instrument.control(
        "I1?",
        "I1 %g",
        """ A floating point property that controls the current limit
        in Amperes. This property can be set.
        """,
        validator=strict_range,
        values=[0, 3],
        get_process=lambda v: float(v.replace("I1", "")),
    )

    over_voltage1 = Instrument.control(
        "OVP1?",
        "OVP1 %g",
        """ A floating point property that controls over voltage protection
            in Volts. This property can be set.
        """,
        validator=strict_range,
        values=[0, 30],
        get_process=lambda v: float(v.replace("VP1", "")),
    )

    over_current1 = Instrument.control(
        "OCP1?",
        "OCP1 %g",
        """ A floating point property that controls over current protection
            in Volts. This property can be set.
        """,
        validator=strict_range,
        values=[0, 30],
        get_process=lambda v: float(v.replace("CP1", "")),
    )

    voltage_output1 = Instrument.measurement(
        "V1O?",
        """ The readback output of the voltage for the output, in Volts
        """,
        get_process=lambda v: float(v.replace("V", "")),
    )

    current_output1 = Instrument.measurement(
        "I1O?",
        """ The readback output of the current for the output, in Amperes
        """,
        get_process=lambda v: float(v.replace("A", "")),
    )

    output1 = Instrument.control(
        "OP1?",
        "OP1 %d",
        """ A property that shows the output state (On/Off).
         This property can be set.
        """,
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True,
    )

    voltage2 = Instrument.control(
        "V2?",
        "V2 %g",
        """ A floating point property that controls the voltage output
            in Volts. This property can be set.
        """,
        validator=strict_range,
        values=[0, 30],
        get_process=lambda v: float(v.replace("V2", "")),
    )

    current2 = Instrument.control(
        "I2?",
        "I2 %g",
        """ A floating point property that controls the current limit
        in Amperes. This property can be set.
        """,
        validator=strict_range,
        values=[0, 3],
        get_process=lambda v: float(v.replace("I2", "")),
    )

    over_voltage2 = Instrument.control(
        "OVP2?",
        "OVP2 %g",
        """ A floating point property that controls over voltage protection
            in Volts. This property can be set.
        """,
        validator=strict_range,
        values=[0, 30],
        get_process=lambda v: float(v.replace("VP2", "")),
    )

    over_current2 = Instrument.control(
        "OCP2?",
        "OCP2 %g",
        """ A floating point property that controls over current protection
            in Volts. This property can be set.
        """,
        validator=strict_range,
        values=[0, 30],
        get_process=lambda v: float(v.replace("CP2", "")),
    )

    voltage_output2 = Instrument.measurement(
        "V2O?",
        """ The readback output of the voltage for the output, in Volts
        """,
        get_process=lambda v: float(v.replace("V", "")),
    )

    current_output2 = Instrument.measurement(
        "I2O?",
        """ The readback output of the current for the output, in Amperes
        """,
        get_process=lambda v: float(v.replace("A", "")),
    )

    output2 = Instrument.control(
        "OP2?",
        "OP2 %d",
        """ A property that shows the output state (On/Off).
         This property can be set.
        """,
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True,
    )

    trip_reset = Instrument.setting(
        "TRIPRST", """Reset any trip errors (e.g. over voltage or over current)"""
    )