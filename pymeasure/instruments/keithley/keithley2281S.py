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

import enum
import time

import numpy as np
import pandas as pd

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.channel import Channel
from pymeasure.instruments.keithley.buffer import KeithleyBuffer
from pymeasure.instruments.validators import strict_discrete_set, strict_range, truncated_range


@enum.unique
class Keithley2281SOperationEventRegister(enum.IntFlag):
    """
    Enum containing Keithley2281S Operation Instrument Summary Event Register definition
    """

    CALIBRATION = 1  # Performing calibration
    _RESERVED_1 = 2
    _RESERVED_2 = 4
    _RESERVED_3 = 8
    MEASUREMENT = 16  # Performing measurement
    TRIGGER = 32  # Waiting for trigger
    ARM = 64  # Waiting for arm event
    _RESERVED_4 = 128
    FILTER_SETTLED = 256  # Filter has settled or is disabled
    LIST = 512  # Running a list
    IDLE = 1024  # Idling
    _RESERVED_5 = 2048
    _RESERVED_6 = 4096
    _RESERVED_7 = 8192
    _RESERVED_8 = 16384


@enum.unique
class Keithley2281SMeasurementEventRegister(enum.IntFlag):
    """
    Enum containing Keithley2281S Measurement Instrument Summary Event Register definition
    """

    READING_OVERFLOW = 1
    _RESERVED_1 = 2
    _RESERVED_2 = 4
    _RESERVED_3 = 8
    _RESERVED_4 = 16
    _RESERVED_5 = 32
    READING_AVAILABLE = 64
    BUFFER_HALF_FULL = 128
    BUFFER_FULL = 256
    BUFFER_THREE_QUARTERS_FULL = 512
    BUFFER_ONE_QUARTER_FULL = 1024
    _RESERVED_6 = 2048
    _RESERVED_7 = 4096
    _RESERVED_8 = 8192
    _RESERVED_9 = 16384


# Constants needed in multiple classes
_VOLTAGE_RANGE = [0.0, 20]
_CURRENT_RANGE_BT_BS = [0.0, 6.1]
_INTERNAL_MEMORY_SLOTS = list(range(1, 10))
_PLC_RANGE = [0.002, 12]
_CURRENT_RANGE = [0.1, 6.1]


class PowerSupplyChannel(Channel):
    """
    Power Supply Mode of the device

    The channels are just a virtual representation of the different functions this device offers,
    but are mutually exclusive!
    Make sure that the parent's instrument `function_mode` property is set to `POWER` before using
    this channel.
    """

    _data_buffer = Instrument.measurement(
        ':DATA:DATA? "READ,SOUR,REL"',
        """Get the buffer in power supply mode.""",
        separator=",",
    )

    @property
    def buffer_data(self) -> pd.DataFrame:
        """Get the buffer in power supply mode and return its content as a pandas dataframe."""
        if not self.parent.reading_available:
            return pd.DataFrame({"current": [], "voltage": [], "time": []})
        data = np.array(self._data_buffer, dtype=np.float32)
        return pd.DataFrame({"current": data[0::3], "voltage": data[1::3], "time": data[2::3]})

    voltage_setpoint = Instrument.control(
        ":VOLT?",
        ":VOLT %g",
        """Control the output voltage in Volts.""",
        validator=strict_range,
        values=_VOLTAGE_RANGE,
    )

    current_limit = Instrument.control(
        ":CURR?",
        ":CURR %g",
        """Control the output current limit in Amps.""",
        validator=strict_range,
        values=_CURRENT_RANGE,
    )

    voltage_limit = Instrument.control(
        ":VOLT:LIM?",
        ":VOLT:LIM %g",
        """Control the maximum voltage that can be set.""",
        validator=strict_range,
        values=_VOLTAGE_RANGE,
    )

    output_enabled = Instrument.control(
        ":OUTP:STAT?",
        ":OUTP:STAT %s",
        """Control the output state.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    power_line_cycles = Instrument.control(
        ":SENS:CONC:NPLC?",
        ":SENS:CONC:NPLC %g",
        """
        Control the number of power line cycles for current and voltage measurements.
        The upper limit depends on the line frequency and is adapted at startup.
        """,
        validator=truncated_range,
        values=_PLC_RANGE,
    )


class BatteryTestChannel(Channel):
    """
    Battery Test Mode of the device

    The channels are just a virtual representation of the different functions this device offers,
    but are mutually exclusive!
    Make sure that the parent's instrument `function_mode` property is set to `TEST` before using
    this channel.
    """

    charge_voltage_setpoint = Instrument.control(
        ":BATT:TEST:VOLT?",
        ":BATT:TEST:VOLT %g",
        """
        Control the target voltage for battery tests.
        If it is lower than terminal voltage, the battery gets discharged,
        if it is higher than the terminal voltage the battery gets charged.
        """,
        validator=strict_range,
        values=_VOLTAGE_RANGE,
    )

    charge_voltage_limit = Instrument.control(
        ":BATT:TEST:SENS:AH:VFUL?",
        ":BATT:TEST:SENS:AH:VFUL %g",
        """Control the charging target voltage for battery tests.""",
        validator=strict_range,
        values=_VOLTAGE_RANGE,
    )

    charge_current_limit = Instrument.control(
        ":BATT:TEST:SENS:AH:ILIM?",
        ":BATT:TEST:SENS:AH:ILIM %g",
        """Control the maximum charging current for battery tests.""",
        validator=strict_range,
        values=_CURRENT_RANGE_BT_BS,
    )

    termination_current = Instrument.control(
        ":BATT:TEST:CURR:END?",
        ":BATT:TEST:CURR:END %g",
        """Control the termination current for battery charging and discharging.""",
        validator=truncated_range,
        values=[0, 0.1],
    )

    output_enabled = Instrument.control(
        ":BATT:OUTP?",
        ":BATT:OUTP %s",
        """Control the output state.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    test_control = Instrument.setting(
        ":BATT:TEST:SENS:AH:EXEC %s",
        """
        Set the battery-characterization state.

        Set to "START", "STOP", "PAUSE" or "CONTINUE". This will en-/disable the output
        for the characterization process. The device will measure and collect data for
        the battery model. See the Keithley 077114601 p. 251 for details.
        """,
        validator=strict_discrete_set,
        values={"START", "STOP", "PAUSE", "CONTINUE"},
    )

    save_model_internal = Instrument.setting(
        ":BATT:TEST:SENS:AH:GMOD:SAVE:INTE %d",
        """Set the memory slot the battery model will be saved to.""",
        validator=strict_discrete_set,
        values=_INTERNAL_MEMORY_SLOTS,
    )

    _data_buffer = Instrument.measurement(
        ':BATT:DATA:DATA? "VOLT, CURR, RES, AH, REL"',
        """Get the buffer in battery test mode.""",
        separator=",",
    )

    def set_battery_model_range(self, lower_voltage: float, upper_voltage: float):
        """Set the lower and upper end voltage of the model.

        Args:
            lower_voltage (float): discharge end voltage
            upper_voltage (float): charge end voltage
        """
        self.write(f":BATT:TEST:SENS:AH:GMOD:RANG {lower_voltage}, {upper_voltage}")

    def save_model_to_usb(self, memory_slot: int, model_file_name: str):
        """Save battery model to USB.

        Args:
            memory_slot (int): Number of memory slot to save model from. Valid values are 1 to 10.
            model_file_name (str): Name of battery model to save. '.csv' will be appended by device

        Raises:
            ValueError: invalid memory slot given
        """
        if _INTERNAL_MEMORY_SLOTS[0] > memory_slot > _INTERNAL_MEMORY_SLOTS[-1]:
            raise ValueError
        self.write(f":BATT:MOD:SAVE:USB {memory_slot}, \"{model_file_name}\"")

    @property
    def buffer_data(self) -> pd.DataFrame:
        """Get the buffer in battery test mode and return its content as a pandas dataframe."""
        if not self.parent.reading_available:
            return pd.DataFrame(
                {"current": [], "voltage": [], "capacity": [], "resistance": [], "time": []}
            )
        data = np.array(self._data_buffer, dtype=np.float32)
        return pd.DataFrame(
            {
                "voltage": data[0::5],
                "current": data[1::5],
                "resistance": data[2::5],
                "capacity": data[3::5],
                "time": data[4::5],
            }
        )


class BatterySimulationChannel(Channel):
    """
    Battery Simulation Mode of the device

    The channels are just a virtual representation of the different functions this device offers,
    but are mutually exclusive!
    Make sure that the parent's instrument `function_mode` property is set to `SIMULATION` before
    using this channel.
    """

    select_model_internal = Instrument.setting(
        ":BATT:MOD:RCL %d",
        """Set the battery model from internal memory.""",
        validator=strict_discrete_set,
        values=_INTERNAL_MEMORY_SLOTS,
    )

    def load_model_from_usb(self, memory_slot: int, model_file_name: str):
        """Load battery model from USB.

        Args:
            memory_slot (int): Number of memory slot to load model to. Valid values are 1 to 10.
            model_file_name (str): Name of battery model to load. Omit '.csv'

        Raises:
            ValueError: invalid memory slot given
        """
        if _INTERNAL_MEMORY_SLOTS[0] > memory_slot > _INTERNAL_MEMORY_SLOTS[-1]:
            raise ValueError
        self.write(f":BATT:MOD:LOAD:USB {memory_slot}, \"{model_file_name}\"")

    output_enabled = Instrument.control(
        ":BATT:OUTP?",
        ":BATT:OUTP %s",
        """Control the output state.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    dynamic_soc = Instrument.control(
        ":BATT:SIM:METH?",
        ":BATT:SIM:METH %s",
        """
        Control simulation mode to use.
        I.e. does the State of Charge (SoC) change when charging or discharging.
        """,
        validator=strict_discrete_set,
        values={True: "DYN", False: "STAT"},
        map_values=True,
    )

    capacity_limit = Instrument.control(
        ":BATT:SIM:CAP:LIM?",
        ":BATT:SIM:CAP:LIM %g",
        """
        Control maximum capacity of the simulated battery in Ah.

        Output needs to be disabled to set this property!
        """,
        validator=truncated_range,
        values=[0.001, 99],
    )

    current_capacity = Instrument.measurement(
        ":BATT:SIM:CAP?",
        """Get the real-time capacity of the simulated battery in Ah.""",
    )

    current_limit = Instrument.control(
        ":BATT:SIM:CURR:LIM?",
        ":BATT:SIM:CURR:LIM %g",
        """Control maximum current of the simulated battery.""",
        validator=truncated_range,
        values=_CURRENT_RANGE_BT_BS,
    )

    resistance_offset = Instrument.control(
        ":BATT:SIM:RES:OFFS?",
        ":BATT:SIM:RES:OFFS %g",
        """
        Control an offset for the internal resistance of the simulated battery.

        ESR might not be displayed correctly until display is updated (e.g. via enabled output).
        """,
        validator=truncated_range,
        values=[-100, 100],
    )

    soc_setpoint = Instrument.control(
        ":BATT:SIM:SOC?",
        ":BATT:SIM:SOC %g",
        """Control the State of Charge (SoC) of the simulated battery.""",
        validator=truncated_range,
        values=[0.0, 100],
    )

    voc_setpoint = Instrument.control(
        ":BATT:SIM:VOC?",
        ":BATT:SIM:VOC %g",
        """
        Control the Voc (Open Circuit Voltage) of the simulated battery.

        The set voltage will internally be converted to an equivalent State of Charge (SoC) in the
        device.
        """,
        validator=truncated_range,
        values=_VOLTAGE_RANGE,
    )

    voc_full = Instrument.control(
        ":BATT:SIM:VOC:FULL?",
        ":BATT:SIM:VOC:FULL %g",
        """Control the Voc for the full simulated battery.""",
        validator=truncated_range,
        values=_VOLTAGE_RANGE,
    )

    voc_empty = Instrument.control(
        ":BATT:SIM:VOC:EMPT?",
        ":BATT:SIM:VOC:EMPT %g",
        """Control the Voc for the empty simulated battery.""",
        validator=truncated_range,
        values=_VOLTAGE_RANGE,
    )

    _data_buffer = Instrument.measurement(
        ':BATT:DATA:DATA? "VOLT, CURR, SOC, RES,REL"',
        """Get the buffer in battery simulator mode.""",
        separator=",",
    )

    @property
    def buffer_data(self) -> pd.DataFrame:
        """Get the buffer in battery simulator mode and return its content as a pandas dataframe."""
        if not self.parent.reading_available:
            return pd.DataFrame(
                {"current": [], "voltage": [], "soc": [], "resistance": [], "time": []}
            )
        data = np.array(self._data_buffer, dtype=np.float32)
        return pd.DataFrame(
            {
                "voltage": data[0::5],
                "current": data[1::5],
                "soc": data[2::5],
                "resistance": data[3::5],
                "time": data[4::5],
            }
        )


class Keithley2281S(SCPIMixin, Instrument, KeithleyBuffer):
    """
    Represents the Keithley 2281S-20-6 power supply and battery simulator / characterizer.
    Common commands beside `function_mode` and power supply commands should also work for
    Keithley 2280S power supplies, although this is untested.
    """

    ps = Instrument.ChannelCreator(PowerSupplyChannel, "PS")
    bt = Instrument.ChannelCreator(BatteryTestChannel, "BT")
    bs = Instrument.ChannelCreator(BatterySimulationChannel, "BS")

    def __init__(self, adapter, name="Keithley2281S", **kwargs):
        super().__init__(adapter, name, **kwargs)
        if self.line_frequency == 60:
            _PLC_RANGE[1] = 15

    # Overwritten parent property

    @property
    def buffer_data(self):
        """Get a pandas dataframe of values from the buffer."""
        # Replace with match case, once Python>=3.10 is required
        function_mode = self.function_mode
        if function_mode == "POWER":
            return self.ps.buffer_data
        if function_mode == "TEST":
            return self.bt.buffer_data
        if function_mode == "SIMULATOR":
            return self.bs.buffer_data

    display_text_data = Instrument.setting(
        ":DISP:USER:TEXT '%s'", """Set control text to be displayed(24 characters)."""
    )

    function_mode = Instrument.control(
        ":ENTR:FUNC?",
        ":ENTR:FUNC %s",
        """
        Control function mode to use.

        Valid values are "POWER", "TEST" and "SIMULATOR".
        """,
        validator=strict_discrete_set,
        values=["POWER", "TEST", "SIMULATOR"],
    )

    buffer_points = Instrument.control(
        ":TRAC:POIN?",
        ":TRAC:POIN %d",
        """Control the maximum number of buffer points to store.""",
        validator=truncated_range,
        values=[2, 2500],
        cast=int,
    )

    summary_event = Instrument.measurement(
        ":STAT:OPER:INST:ISUM:COND?",
        """Get summary event register.""",
        get_process=lambda x: Keithley2281SOperationEventRegister(int(x)),
    )

    measurement_event = Instrument.measurement(
        ":STAT:MEAS:INST:ISUM:COND?",
        """Get measurement event register.""",
        get_process=lambda x: Keithley2281SMeasurementEventRegister(int(x)),
    )

    line_frequency = Instrument.measurement(
        ":SYST:LFR?",
        """Get line frequency.""",
        cast=int,
    )

    @property
    def measurement_ongoing(self) -> bool:
        """Get measurement status."""
        return Keithley2281SOperationEventRegister.MEASUREMENT in self.summary_event

    @property
    def reading_available(self) -> bool:
        """Get availability of a reading."""
        return Keithley2281SMeasurementEventRegister.READING_AVAILABLE in self.measurement_event

    def characterize(
        self,
        lower_voltage: float,
        upper_voltage: float,
        charge_current: float,
        memory_slot: int,
        model_voltage_offset: float = 0.05,
        charge_delay: float = 0,
    ):
        """
        Convenience function for testing a battery and saving its model to the internal memory.

        The device can only discharge the battery at a fixed 1A! If this current is too high,
        a series resistor has to be used during discharge to limit the current!
        If the battery is discharged below the lower limit, it will be charged with a 10th of
        the set charge current till it reaches the lower limit, then the battery profile will
        be characterized.
        The function will block until the end of the measurement!

        :param lower_voltage: discharge end voltage, set this slightly lower (~0.05V)
                              than in normal operation
        :type lower_voltage: float
        :param upper_voltage: charge end voltage, set this slightly higher (~0.05V)
                              than in normal operation
        :type upper_voltage: float
        :param charge_current: maximum charge current.
                               A 1/100th is used as (dis-)charge end current.
        :type charge_current: float
        :param memory_slot: Internal memory slot to save the model to
        :type memory_slot: int
        :param model_voltage_offset: Voltage offset for the generated model
                                     upper and lower limits. These have to be in
                                     the range of the actual measured values, i.e.
                                     in between the hard limits of the measurement.
                                     Defaults to 0.05
        :type model_voltage_offset: float, optional
        :param charge_delay: Seconds to wait between discharging and charging.
                             Actual time is higher since the device has some internal
                             delay on reporting end of a test. Defaults to 0.
        :type charge_delay: float, optional
        """

        # Reset device to known state
        self.reset()
        self.function_mode = "TEST"

        # Set discharging conditions and start discharging
        self.bt.charge_voltage_setpoint = lower_voltage
        self.bt.charge_current_limit = charge_current / 10
        self.bt.termination_current = charge_current / 100
        self.bt.output_enabled = True
        self.display_text_data = "Measurement Ongoing! Discharging..."
        while self.measurement_ongoing:
            time.sleep(1)

        # Discharging finished, wait some time if set
        time.sleep(charge_delay)

        # Set charging conditions and start charging
        self.bt.charge_voltage_limit = upper_voltage
        self.bt.charge_current_limit = charge_current
        self.bt.termination_current = charge_current / 100
        self.bt.test_control = "START"
        self.display_text_data = "Measurement Ongoing! Charging..."
        while self.measurement_ongoing:
            time.sleep(1)

        # Charging finished, generate and save model
        self.bt.set_battery_model_range(
            lower_voltage+model_voltage_offset,
            upper_voltage-model_voltage_offset
            )
        self.bt.save_model_internal = memory_slot
        self.display_text_data = "Measurement Finished!"
