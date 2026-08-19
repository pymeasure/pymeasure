#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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
import logging
from time import sleep

import numpy as np

from pymeasure.instruments import Instrument
from pymeasure.instruments._strenum import StrEnum
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Functions(StrEnum):
    SINE = "SIN"
    SQUARE = "SQU"
    CLIPPED_SINE = "CSIN"  # Clipped sinewave output. Both positive and negative peak amplitudes
    # are clipped at a value determined by the FUNC:CSIN command.


class Modes(StrEnum):
    FIXED = "FIX"  # unaffected by a triggered output transient.
    STEP = "STEP"  # programmed to the value set by X:TRIG when a triggered transient occurs.
    PULSE = "PULS"  # changed to the value set by X:TRIG for a duration determined by the pulse
    # commands.
    LIST = "LIST"  # controlled by the waveform shape list when a triggered transient occurs.


class Keysight681xB(SCPIMixin, Instrument):
    """Represents the Keysight 681xB series of AC Power Source/Analyzers.

    Do not use this class directly; use one of its subclasses.
    """

    _BOOLS = {True: 1, False: 0}
    FREQ_RANGE = [45, 1000]
    ROUT_RANGE = [0, 1]
    LOUT_RANGE = [20e-6, 1e-3]  # Henries

    def __init__(self, adapter, name="Keysight 681xB AC Power Source/Analyzer", **kwargs):
        super().__init__(adapter, name, **kwargs)

    voltage_setpoint = Instrument.control(
        "VOLT?",
        "VOLT %f",
        """Control the AC RMS voltage amplitude setpoint in volts.""",
        validator=strict_range,
        values=[0, 1],
        dynamic=True,
    )

    clipped_sine_setpoint_pct = Instrument.control(
        "FUNC:CSIN?",
        "FUNC:CSIN %f",
        """Control clipped sine clipping point as a percent (0-100) of peak amplitude.""",
        validator=strict_range,
        values=[0.0, 100.0],
    )

    current_setpoint = Instrument.control(
        "CURRENT?",
        "CURRENT %f",
        """Control the AC RMS current limit setpoint in amperes.""",
        validator=strict_range,
        values=[0, 1],
        dynamic=True,
    )

    frequency_setpoint = Instrument.control(
        "FREQ?",
        "FREQ %f",
        """Control the frequency setpoint in hertz.""",
        validator=strict_range,
        values=FREQ_RANGE,
    )

    voltage_dc = Instrument.measurement("MEAS:VOLT:DC?", """Measure DC voltage in volts.""")
    voltage_ac = Instrument.measurement("MEAS:VOLT:AC?", """Measure AC RMS voltage in volts.""")
    voltage_acdc = Instrument.measurement("MEAS:VOLT:ACDC?", """Measure ACDC voltage in volts.""")
    current_dc = Instrument.measurement("MEAS:CURR:DC?", """Measure DC current in amperes.""")
    current_ac = Instrument.measurement("MEAS:CURR:AC?", """Measure AC RMS current in amperes.""")
    current_acdc = Instrument.measurement("MEAS:CURR:ACDC?", """Measure ACDC current in amperes.""")
    current_amplitude = Instrument.measurement(
        "MEAS:CURR:AMPL:MAX?", """Measure peak current amplitude in amperes."""
    )

    crest_factor = Instrument.measurement(
        "MEAS:CURR:CRESTFACTOR?", """Measure current crest factor."""
    )

    power_dc = Instrument.measurement("MEAS:POW:DC?", """Measure DC power.""")
    power_real = Instrument.measurement("MEAS:POW:AC:REAL?", """Measure AC real power in watts.""")
    power_apparent = Instrument.measurement(
        "MEAS:POW:AC:APPARENT?", """Measure AC apparent power in VA."""
    )

    power_reactive = Instrument.measurement(
        "MEAS:POW:AC:REACTIVE?", """Measure AC reactive power in VAR."""
    )

    power_total = Instrument.measurement(
        "MEAS:POW:AC:TOTAL?", """Measure three-phase total AC power."""
    )

    frequency = Instrument.measurement("MEAS:FREQUENCY?", """Measure AC frequency in hertz.""")
    power_factor = Instrument.measurement(
        "MEAS:POW:AC:PFACTOR?", """Measure AC power factor in degrees."""
    )

    waveform = Instrument.control(
        "FUNC?",
        "FUNC %s",
        """Control the output function of the ac source. Can be SIN, SQU, CSIN, or a user
        waveform.""",
        cast=str,
    )

    output_enabled = Instrument.control(
        "OUTPUT:STATE?",
        "OUTPUT:STATE %s",
        """Control the enabled/disabled state of the AC source (bool).""",
        validator=strict_discrete_set,
        values=_BOOLS,
        map_values=True,
    )

    trigger_source = Instrument.control(
        "TRIG:SOUR?",
        "TRIG:SEQ1:SOUR %s",
        """Control the trigger source for first sequence. Can be BUS|EXT|IMM.

        When set to BUS, the trigger will activate after receiving a *TRG command over GPIB.
        When set to EXTernal, the AC source backplane BNC trigger input is used as the trigger.
        When set to IMMediate, the trigger is generated as soon as the trigger system is initiated.
        """,
        validator=strict_discrete_set,
        values=["BUS", "EXT", "IMM"],
        cast=str,
    )

    trigger_sync_source = Instrument.control(
        "TRIG:SYNC:SOUR?",
        "TRIG:SYNC:SOUR %s",
        """Control the trigger system synchronization source.
        The trigger system can delay the trigger event until a certain synchronization event
        occurs. In particular, it can delay until the waveform phase reaches a particular value.

        Values can be IMM|PHAS.
        """,
        validator=strict_discrete_set,
        values=["IMM", "PHAS"],
        cast=str,
    )

    trigger_sync_phase = Instrument.control(
        "TRIG:SYNC:PHASE?",
        "TRIG:SYNC:PHASE %f",
        """Control the trigger synchronization phase value in degrees.

        When the trigger is phase synchronized, it waits until the waveform reaches this phase
        before the triggered event actually occurs.
        """,
        validator=strict_range,
        values=[0, 360],
    )

    voltage_trigger_level = Instrument.control(
        "VOLT:TRIG?",
        "VOLT:TRIG %f",
        """Control the AC RMS amplitude in volts of the output waveform when triggered.""",
        validator=strict_range,
        values=[0, 1],
        dynamic=True,
    )

    voltage_trigger_mode = Instrument.control(
        "VOLT:MODE?",
        "VOLT:MODE %s",
        """Control the voltage trigger mode. Can be FIX|STEP|PULS|LIST.""",
        validator=strict_discrete_set,
        values=["FIX", "STEP", "PULS", "LIST"],
        cast=str,
    )

    pulse_count = Instrument.control(
        "PULSE:COUNT?",
        "PULSE:COUNT %f",
        """Control the number of pulses when trigger mode is set to PULS.""",
        validator=strict_range,
        values=[1, 9.9e37],
    )

    pulse_period = Instrument.control(
        "PULSE:PER?",
        "PULSE:PER %f",
        """Control pulse period in seconds when trigger mode is set to PULS.""",
        validator=strict_range,
        values=[0, 430133],
    )

    pulse_duty_cycle_pct = Instrument.control(
        "PULSE:DCYCLE?",
        "PULSE:DCYCLE %f",
        """Control pulse duty cycle as a percentage (0-100) when trigger mode is set to PULS.""",
        validator=strict_range,
        values=[0, 100],
    )

    pulse_width = Instrument.control(
        "PULSE:WIDTH?",
        "PULSE:WIDTH %f",
        """Control the width in seconds of a transient output pulse when trigger mode is set to
        PULS.""",
        validator=strict_range,
        values=[0, 4.30133e5],
    )

    voltage_sense_source = Instrument.control(
        "VOLTAGE:SENSE:SOURCE?", "VOLTAGE:SENSE:SOURCE %s",
        """Control the source from which the output voltage is sensed. Can be INT or
        EXT.""",
        validator=strict_discrete_set,
        values=['EXT', 'INT'],
        cast=str,
    )

    def arm_immediate_trigger(self):
        """Arm the trigger system (SEQ1). Before a trigger can have effect, the trigger subsystem
        must be armed, or 'initialized'. This method arms the trigger for a single event."""
        self.write("INIT:SEQ1")

    def arm_continuous_trigger(self, run=True):
        """Arm the trigger system (SEQ1). Before a trigger can have effect, the trigger subsystem
        must be armed, or 'initialized'. This method arms or disarms the trigger for a continuous
        run.

        :param run: if True, enable continuous triggering; if False, stop continuous triggering."""
        if run:
            self.write("INIT:CONT:SEQ1 ON")
        else:
            self.write("INIT:CONT:SEQ1 OFF")

    def send_GPIB_trigger(self):
        """Send a GPIB trigger signal. The trigger source must be set to BUS for this to have
        any effect. This function forces the trigger source to be BUS before sending."""
        self.trigger_source = "BUS"
        self.write("*TRG")

    def output_enable_at_phase(self, trig_phase: float):
        """Enable the output at a given phase.

        This method uses the existing voltage setpoint to set a voltage step level on trigger.
        The voltage setpoint is set to 0V, the output is enabled, and the trigger system is used
        to step the voltage to the prior setpoint when we send *TRG and the waveform phase
        reaches `phase`. A GPIB trigger is sent.

        After this method, the voltage setpoint will be the same as before, the trigger SYNC
        source will be PHAS, and the voltage trigger mode will be STEP.

        Example:
        ```python
        # Reset and configure the output
        acsource.reset()
        acsource.voltage_setpoint = 50
        acsource.frequency_setpoint = 60
        acsource.output_enable_at_phase(90)  # start waveform at 90 degrees
        ```
        """
        vset = self.voltage_setpoint
        self.voltage_setpoint = 0
        self.output_enabled = True
        self.voltage_trigger_mode = "STEP"
        self.voltage_trigger_level = vset
        self.trigger_sync_source = "PHAS"
        self.trigger_sync_phase = trig_phase
        sleep(1)  # MUST dwell here for trigger to work.
        self.arm_immediate_trigger()
        self.send_GPIB_trigger()

    def output_pulse(self, v_default, v_pulse, pulse_period, npulses=1, pulse_on_time=-1):
        """Trigger one or more voltage pulses.

        :param v_default: default voltage, or pulse OFF state voltage
        :param v_pulse: pulse ON state voltage
        :param pulse_period: Time duration of one full pulse (an ON and an OFF duration)
        :param npulses: number of pulses to output
        :param pulse_on_time: Time duration for pulse ON state, or -1 for a single pulse.
        """
        if pulse_on_time == -1:
            pulse_on_time = pulse_period
        self.voltage_setpoint = v_default
        self.output_enabled = True
        sleep(1)  # Dwell before trigger setup
        self.voltage_trigger_mode = "PULS"
        self.voltage_trigger_level = v_pulse
        self.pulse_count = npulses
        self.pulse_period = pulse_period
        self.pulse_width = pulse_on_time
        self.arm_immediate_trigger()
        self.send_GPIB_trigger()

    def output_pulse_at_phase(
        self,
        v_default: float,
        v_pulse: float,
        pulse_period: float,
        trig_phase: float = 0.0,
        npulses: int = 1,
        pulse_on_time: float = -1,
        trigger_source: str = "GPIB",
    ):
        """Trigger one or more voltage pulses, waiting for a particular phase angle before
        triggering.

        If trigger source is GPIB, trigger is sent immediately. if trigger source is
        external, this function returns with the system armed for an external trigger.

        :param v_default: default voltage, or pulse OFF state voltage
        :param v_pulse: pulse ON state voltage
        :param pulse_period: Time duration of one full pulse (an ON and an OFF duration)
        :param trig_phase: waveform phase angle at which to trigger
        :param npulses: number of pulses to output
        :param pulse_on_time: Time duration for pulse ON state, or -1 for a single pulse.
        :param trigger_source: Trigger source, can be GPIB|BUS|EXT|IMM.
        """
        if pulse_on_time == -1:
            pulse_on_time = pulse_period
        self.voltage_setpoint = v_default
        self.output_enabled = True
        sleep(1)  # Dwell before trigger setup
        self.voltage_trigger_mode = "PULS"
        self.voltage_trigger_level = v_pulse
        self.pulse_count = npulses
        self.pulse_period = pulse_period
        self.pulse_width = pulse_on_time
        self.trigger_sync_source = "PHAS"
        self.trigger_sync_phase = trig_phase
        self.arm_immediate_trigger()
        if trigger_source == "GPIB" or trigger_source == "BUS":
            self.send_GPIB_trigger()
        else:
            self.trigger_source = trigger_source

    # WAVEFORMS #
    user_wfm_catalog = Instrument.measurement(
        "TRACE:CATALOG?",
        """Get the user waveform catalog.""",
        get_process_list=lambda names: [str(name).replace('"', "") for name in names],
        cast=str,
    )

    def get_user_wfm_data(self, name: str) -> np.ndarray:
        """Get the data points for a particular user waveform.

        :param name: internal name of user waveform.
        :return: numpy array of y-data points with dtype float.
        """
        data_str = self.ask(f"TRACE:DATA? {name.upper()}")
        data = np.array(data_str.strip().split(","), dtype=float)
        return data

    def get_user_waveform_catalog(self) -> dict:
        """Query the list of user waveforms.."""
        print("Retrieving user waveform catalog. This might take a minute...")
        names = self.user_wfm_catalog
        cat = {}
        for name in names:
            if name not in ["SINUSOID", "SQUARE", "CSINUSOID"]:
                namedata = self.get_user_wfm_data(name)
                cat[name] = namedata
        return cat

    def delete_user_waveform(self, name: str) -> None:
        """Delete a user waveform by name."""
        self.write(f"TRACE:DEL {name}")

    def define_user_waveform_name(self, name: str) -> None:
        """Define a user waveform name without data."""
        self.write(f"TRACE:DEF {name}")

    def add_user_waveform(self, name: str,
                          data: list[float],
                          delete_existing: bool = False) -> None:
        """Add a waveform called `name` with 1024 float data points to the user
        waveform catalog.

        From the programming guide:
        "data points define the relative amplitudes of exactly one cycle of the waveform. The first
        data point defines the amplitude that will be output at 0 degrees phase reference."

        "Data points can be in any arbitrary units. The ac source scales the data to an
        internal format that removes the dc component and ensures that the correct ac rms
        voltage is output when the waveform is selected. When queried, trace data is returned
        as normalized values in the range of 1. Waveform data is stored in nonvolatile memory
        and is retained when input power is removed. Up to 12 user defined waveforms may be
        created and stored."

        :param name: str, name of waveform, will be converted to ALL CAPS.
        :param data1024: numpy array of length 1024, dtype float, all values in [0.0, 1.0].
                         Points will be rounded to 5 digits of precision.
        :param delete_existing: if True, any waveform with the same name will be deleted before
                                adding the new data. If False, raises an exception if name exists.
        """
        if len(data) != 1024:
            raise ValueError(
                f"Length error, received array of length {len(data)}; length must be 1024."
            )
        data_f = data.astype(float)

        # Preprocess name, delete existing trace if present
        name = name.upper()
        if name in self.user_wfm_catalog:
            if delete_existing:
                log.info(f"NOTE: Deleting existing waveform '{name}'")
                self.delete_user_waveform(name)
            else:
                raise ValueError(
                    "Waveform with this name already exists. To override, "
                    "use `delete_existing=True`."
                )

        # Convert to 5 digits of precision
        wave = [f"{x:.5f}" for x in data_f]

        # Add name if needed, then write data
        self.define_user_waveform_name(name)
        self.write(f"TRACE:DATA {name}, " + ", ".join(wave))


class Keysight6811B(Keysight681xB):
    VRMS_MAX = 300
    IRMS_MAX = 3.25
    VPEAK_MAX = 425
    IPEAK_MAX = 40

    def __init__(self, adapter, name="Keysight 6811B AC Power Source/Analyzer", **kwargs):
        """Represents the Keysight 6811B AC Power Source/Analyzer."""
        super().__init__(adapter, name, **kwargs)
        self.voltage_setpoint_values = [0, self.VRMS_MAX]
        self.current_setpoint_values = [0, self.IRMS_MAX]
        self.voltage_trigger_level_values = [0, self.VRMS_MAX]


class Keysight6812B(Keysight681xB):
    VRMS_MAX = 300
    IRMS_MAX = 6.5
    VPEAK_MAX = 425
    IPEAK_MAX = 40

    def __init__(self, adapter, name="Keysight 6812B AC Power Source/Analyzer", **kwargs):
        """Represents the Keysight 6812B AC Power Source/Analyzer."""
        super().__init__(adapter, name, **kwargs)
        self.voltage_setpoint_values = [0, self.VRMS_MAX]
        self.current_setpoint_values = [0, self.IRMS_MAX]
        self.voltage_trigger_level_values = [0, self.VRMS_MAX]


class Keysight6813B(Keysight681xB):
    VRMS_MAX = 300
    IRMS_MAX = 13
    VPEAK_MAX = 425
    IPEAK_MAX = 80

    def __init__(self, adapter, name="Keysight 6813B AC Power Source/Analyzer", **kwargs):
        """Represents the Keysight 6813B AC Power Source/Analyzer."""
        super().__init__(adapter, name, **kwargs)
        self.voltage_setpoint_values = [0, self.VRMS_MAX]
        self.current_setpoint_values = [0, self.IRMS_MAX]
        self.voltage_trigger_level_values = [0, self.VRMS_MAX]

