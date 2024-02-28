
import enum

from pymeasure.instruments import Instrument
from pymeasure.instruments.keithley.buffer import KeithleyBuffer
from pymeasure.instruments.validators import strict_discrete_set, strict_range, truncated_range
import numpy as np
import pandas as pd


@enum.unique
class Keithley2281SOperationCondition(enum.IntFlag):
    """Enum containing Keithley2281S operation condition defintition"""
    CALIBRATION = 1
    _RESERVED_1 = 2
    _RESERVED_2 = 4
    _RESERVED_3 = 8
    MEASUREMENT = 16
    TRIGGER = 32
    ARM = 64
    _RESERVED_4 = 128
    FILT = 256
    LIST = 512
    IDLE = 1024
    _RESERVED_5 = 2048
    _RESERVED_6 = 4096
    _RESERVED_7 = 8192
    _RESERVED_8 = 16384


class Keithley2281S(Instrument, KeithleyBuffer):
    """
    Represents the Keithley 2281S-20-6 power supply and battery simulator / characterizer.
    Common commands, beside `function_mode` and power supply commands should also work for
    Keithley 2280S power supplies, although this is untested.
    """
    _VOLTAGE_RANGE = [0.0, 20]
    _CURRENT_RANGE_PS = [0.1, 6.1]
    _CURRENT_RANGE_BT_BS = [0.0, 6.1]
    _INTERNAL_MEMORY_SLOTS = [*range(1, 10)]

    def __init__(self, adapter, name="Keithley2281S", **kwargs):
        super().__init__(adapter, name, **kwargs)

    # Common commands

    cm_display_text_data = Instrument.setting(
        ":DISP:USER:TEXT '%s'",
        """Control text to be displayed(24 characters)."""
    )

    cm_function_mode = Instrument.control(
        ":ENTR:FUNC?",
        ":ENTR:FUNC %s",
        """Control which function to use.""",
        validator=strict_discrete_set,
        values=["POWER", "TEST", "SIMULATOR"]
    )

    cm_buffer_points = Instrument.control(
        ":TRAC:POIN?", ":TRAC:POIN %d",
        """
        An integer property that controls the maximum number of buffer points.
        This does not represent actual points in the buffer, but the configuration
        value instead.
        """,
        validator=truncated_range,
        values=[2, 2500],
        cast=int
    )

    cm_operation_condition = Instrument.measurement(
        ":STAT:OPER:INST:ISUM:COND?",
        """Query test status.""",
        get_process=lambda x: Keithley2281SOperationCondition(int(x))
    )

    # Power Supply Commands, only applicable in power supply mode

    ps_buffer_data = Instrument.measurement(
        ":DATA:DATA? \"READ,SOUR,REL\"",
        """Read the buffer in power supply mode and returns its content as a pandas dataframe""",
        separator=",",
        get_process=lambda v: Keithley2281S._ps_parse_buffer(v)  # Does not work without lambda
    )

    @staticmethod
    def _ps_parse_buffer(buffer_content):
        if len(buffer_content) < 3:
            return pd.DataFrame({'current': [], 'voltage': [], 'time': []})
        data = np.array(buffer_content, dtype=np.float32)
        return pd.DataFrame({'current': data[0::3], 'voltage': data[1::3], 'time': data[2::3]})

    ps_voltage = Instrument.control(
        ":VOLT?",
        ":VOLT %g",
        """Control output voltage in Volts.""",
        validator=strict_range,
        values=_VOLTAGE_RANGE
    )

    ps_current_limit = Instrument.control(
        ":CURR?",
        ":CURR %g",
        """Control output current in Amps.""",
        validator=strict_range,
        values=_CURRENT_RANGE_PS
    )

    ps_voltage_limit = Instrument.control(
        ":VOLT:LIM?",
        ":VOLT:LIM %g",
        """Control the maximum voltage that can be set.""",
        validator=strict_range,
        values=_VOLTAGE_RANGE
    )

    ps_power_supply_mode = Instrument.control(
        ":FORM:ELEM:MODE?",
        ":FORM:ELEM:MODE %s",
        """Control which power supply mode to use.""",
        validator=strict_discrete_set,
        values={"CV", "CC", "OFF"}
    )

    ps_output_enabled = Instrument.control(
        "OUTP:STAT?",
        "OUTP:STAT %s",
        """ Control the output state.""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True
    )

    ps_conc_nplc = Instrument.control(
        ":SENS:CONC:NPLC?",
        ":SENS:CONC:NPLC %g",
        """
        Set number of power line cycles for current and voltage measurements.
        The upper limit is for the 50Hz setting, the 60Hz settings goes up to 15.
        TODO: use dynamic property to adapt range
        """,
        validator=truncated_range,
        values=[0.002, 12]
    )

    # Battery test commands, only applicable in battery test mode

    bt_charge_voltage = Instrument.control(
        ":BATT:TEST:VOLT?",
        ":BATT:TEST:VOLT %g",
        """
        Target voltage for battery tests.
        If it is lower than terminal voltage, the battery gets discharged,
        if it is higher than the terminal voltage the battery gets charged.
        """,
        validator=strict_range,
        values=_VOLTAGE_RANGE
    )

    bt_charge_voltage_limit = Instrument.control(
        ":BATT:TEST:SENS:AH:VFUL?",
        ":BATT:TEST:SENS:AH:VFUL %g",
        """Charging target voltage for battery tests.""",
        validator=strict_range,
        values=_VOLTAGE_RANGE
    )

    bt_charge_current_limit = Instrument.control(
        ":BATT:TEST:SENS:AH:ILIM?",
        ":BATT:TEST:SENS:AH:ILIM %g",
        """Maximum charging current for battery tests.""",
        validator=strict_range,
        values=_CURRENT_RANGE_BT_BS
    )

    bt_termination_current = Instrument.control(
        ":BATT:TEST:CURR:END?",
        ":BATT:TEST:CURR:END %g",
        """Termination current for battery charging and discharging.""",
        validator=strict_range,
        values=[0, 0.1]
    )

    bt_output_enabled = Instrument.control(
        ":BATT:OUTP?",
        ":BATT:OUTP %s",
        """Control the output state.""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True
    )

    bt_test_control = Instrument.setting(
        ":BATT:TEST:SENS:AH:EXEC %s",
        """Control the output state.""",
        validator=strict_discrete_set,
        values={"START", "STOP", "PAUSE", "CONTINUE"}
    )

    bt_save_model_internal = Instrument.setting(
        ":BATT:TEST:SENS:AH:GMOD:SAVE:INTE %d",
        """Save the battery model to internal memory.""",
        validator=strict_discrete_set,
        values=_INTERNAL_MEMORY_SLOTS
    )

    bt_save_model_usb = Instrument.setting(
        ":BATT:TEST:SENS:AH:GMOD:SAVE:USB \"%s\"",
        """Save the battery model to usb memory."""
    )

    bt_buffer_data = Instrument.measurement(
        ":BATT:DATA:DATA? \"VOLT, CURR, RES, AH, REL\"",
        """Read the buffer in battery test mode and returns its content as a pandas dataframe""",
        separator=",",
        get_process=lambda v: Keithley2281S._bt_parse_buffer(v)  # Does not work without lambda
    )

    @staticmethod
    def _bt_parse_buffer(buffer_content):
        if len(buffer_content) < 3:
            return pd.DataFrame({'current': [], 'voltage': [], 'capacity': [], 'resistance': [], 'time': []})
        data = np.array(buffer_content, dtype=np.float32)
        return pd.DataFrame({'voltage': data[0::5], 'current': data[1::5],
                             'resistance': data[2::5], 'capacity': data[3::5], 'time': data[4::5]})

    # Battery simulation commands, only applicable in battery simulator mode

    bs_select_model_internal = Instrument.setting(
        ":BATT:MOD:RCL %d",
        """Select the battery model from internal memory.""",
        validator=strict_discrete_set,
        values=_INTERNAL_MEMORY_SLOTS
    )

    # Needs two arguments
    # bs_load_model_usb = Instrument.setting(
    #    ":BATT:MOD:LOAD:USB %d, \"%s\"",
    #    """Loads a battery model from USB to the internal memory.""",
    #    validator=strict_discrete_set,
    #    values=_INTERNAL_MEMORY_SLOTS
    #    cast=int
    # )

    # To be consistent in the interface
    bs_output_enabled = bt_output_enabled

    bs_simulation_mode = Instrument.control(
        ":BATT:SIM:METH?",
        ":BATT:SIM:METH %s",
        """Select simulation mode to use. I.e. does the SoC change when charging or discharging.""",
        validator=strict_discrete_set,
        values={"DYNAMIC", "STATIC"}
    )

    bs_capacity = Instrument.control(
        ":BATT:SIM:CAP:LIM?",
        ":BATT:SIM:CAP:LIM %g",
        """Set maximum capacity of the simulated battery.""",
        validator=truncated_range,
        values=[0.001, 99]
    )

    bs_current_limit = Instrument.control(
        ":BATT:SIM:CURR:LIM?",
        ":BATT:SIM:CURR:LIM %g",
        """Set maximum current of the simulated battery.""",
        validator=truncated_range,
        values=_CURRENT_RANGE_BT_BS
    )

    bs_resistance_offset = Instrument.control(
        ":BATT:SIM:RES:OFFS?",
        ":BATT:SIM:RES:OFFS %g",
        """Set an offset for the internal resistance of the simulated battery.""",
        validator=truncated_range,
        values=[-100, 100]
    )

    bs_soc = Instrument.control(
        ":BATT:SIM:SOC?",
        ":BATT:SIM:SOC %g",
        """Set the SoC of the simulated battery.""",
        validator=truncated_range,
        values=[0.0, 100]
    )

    bs_voc = Instrument.control(
        ":BATT:SIM:VOC?",
        ":BATT:SIM:VOC %g",
        """Set the Voc of the simulated battery.""",
        validator=truncated_range,
        values=_VOLTAGE_RANGE
    )

    bs_voc_full = Instrument.control(
        ":BATT:SIM:VOC:FULL?",
        ":BATT:SIM:VOC:FULL %g",
        """Set the Voc for the full simulated battery.""",
        validator=truncated_range,
        values=_VOLTAGE_RANGE
    )

    bs_voc_empty = Instrument.control(
        ":BATT:SIM:VOC:EMPT?",
        ":BATT:SIM:VOC:EMPT %g",
        """Set the Voc for the empty simulated battery.""",
        validator=truncated_range,
        values=_VOLTAGE_RANGE
    )

    bs_buffer_data = Instrument.measurement(
        ":BATT:DATA:DATA? \"VOLT, CURR, SOC, RES,REL\"",
        """Read the buffer in battery simulator mode and returns its content as a pandas dataframe""",
        separator=",",
        get_process=lambda v: Keithley2281S._bs_parse_buffer(v)  # Does not work without lambda
    )

    @staticmethod
    def _bs_parse_buffer(buffer_content):
        if len(buffer_content) < 3:
            return pd.DataFrame({'current': [], 'voltage': [], 'soc': [], 'resistance': [], 'time': []})
        data = np.array(buffer_content, dtype=np.float32)
        return pd.DataFrame({'voltage': data[0::5], 'current': data[1::5], 'soc': data[2::5], 'resistance': data[3::5], 'time': data[4::5]})
