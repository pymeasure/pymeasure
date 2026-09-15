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

import numpy as np
import time

from pymeasure.instruments import Instrument
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, truncated_range
from pymeasure.instruments._strenum import StrEnum


class Chroma66205(SCPIMixin, Instrument):
    """Control the Chroma 66205 Digital Power Meter

    The 66205 is a single-channel digital power meter, with voltage, current, power,
    energy, phase, and frequency measurements, and waveform capture. A Chinese user manual
    with programming information in English is available.
    """

    class Measure(StrEnum):
        VOLTAGE = "V"
        DC_VOLTAGE = "VDC"
        MEAN_VOLTAGE = "VMEAN"
        CURRENT = "I"
        DC_CURRENT = "IDC"
        REAL_POWER = "W"
        APPARENT_POWER = "VA"
        PEAK_POS_VOLTAGE = "VPK+"
        PEAK_POS_CURRENT = "IPK+"
        PEAK_NEG_VOLTAGE = "VPK-"
        PEAK_NEG_CURRENT = "IPK-"
        POWER_FACTOR = "PF"
        PHASE = "DEG"
        THD_VOLTAGE = "THDV"
        THD_CURRENT = "THDI"
        INRUSH_CURRENT = "IS"
        REACTIVE_POWER = "VAR"
        VOLTAGE_CREST_FACTOR = "CFV"
        CURRENT_CREST_FACTOR = "CFI"
        CHARGE_AH = "AH"
        ENERGY_WH = "WH"
        VOLTAGE_FREQUENCY = "VHZ"
        CURRENT_FREQUENCY = "IHZ"

    CHANNEL_A_DISPLAY_OPTS = [
        Measure.VOLTAGE,
        Measure.CURRENT,
        Measure.REAL_POWER,
        Measure.APPARENT_POWER,
        Measure.PEAK_POS_VOLTAGE,
        Measure.PEAK_NEG_VOLTAGE,
        Measure.PEAK_POS_CURRENT,
        Measure.PEAK_NEG_CURRENT,
    ]
    CHANNEL_B_DISPLAY_OPTS = [
        Measure.VOLTAGE,
        Measure.CURRENT,
        Measure.REAL_POWER,
        Measure.POWER_FACTOR,
        Measure.PHASE,
        Measure.THD_VOLTAGE,
        Measure.THD_CURRENT,
        Measure.INRUSH_CURRENT,
    ]
    CHANNEL_C_DISPLAY_OPTS = [
        Measure.VOLTAGE,
        Measure.CURRENT,
        Measure.REAL_POWER,
        Measure.REACTIVE_POWER,
        Measure.VOLTAGE_CREST_FACTOR,
        Measure.CURRENT_CREST_FACTOR,
        Measure.CHARGE_AH,
        Measure.ENERGY_WH,
    ]
    CHANNEL_D_DISPLAY_OPTS = [
        Measure.VOLTAGE,
        Measure.CURRENT,
        Measure.REAL_POWER,
        Measure.POWER_FACTOR,
        Measure.VOLTAGE_FREQUENCY,
        Measure.CURRENT_FREQUENCY,
        Measure.THD_VOLTAGE,
        Measure.THD_CURRENT,
    ]

    def __init__(self, adapter, name="Chroma 66205", **kwargs):
        super().__init__(adapter, name, **kwargs)

    system_error = Instrument.measurement(
        "SYSTEM:ERROR?",
        """Get the error string of the instrument.""",
        cast=str,
    )

    # SETTINGS #
    mode = Instrument.control(
        "CONF:MEAS:MODE?",
        "CONF:MEAS:MODE %s",
        """Control measurement mode. Can be RMS, DC, or VMEAN.""",
        validator=strict_discrete_set,
        values=["RMS", "DC", "VMEAN"],
        cast=str,
    )

    voltage_range = Instrument.control(
        "VOLT:RANG?",
        "VOLT:RANG %s",
        """Set the voltage range for measurement. Can be AUTO, V15, V30, V60, V150, V300, or
        V600.""",
        validator=strict_discrete_set,
        values=["AUTO", "V600", "V300", "V150", "V60", "V30", "V15"],
        cast=str,
    )

    current_range = Instrument.control(
        "CURR:RANG?",
        "CURR:RANG %s",
        """Set the current range for measurement. Can be AUTO, A30, A20, A5, A2, A05, A03,
        A02, A005, A002, or A0005 when external shunt is OFF, or AUTO, E015, E01, E005, E0025, or
        E001 when external shunt is ON.""",
        validator=strict_discrete_set,
        values=[
            "AUTO",
            "A30",
            "A20",
            "A5",
            "A2",
            "A05",
            "A03",
            "A02",
            "A005",
            "A002",
            "A0005",
            "E015",
            "E01",
            "E005",
            "E0025",
            "E001",
        ],
        cast=str,
    )

    averages = Instrument.control(
        "CONF:MEAS:AVERAGE?",
        "CONF:MEAS:AVERAGE %d",
        """Control number of measurements to average in averaging mode. Must be a power of 2
        between 1 and 64 inclusive.""",
        validator=strict_discrete_set,
        values=[1, 2, 4, 8, 16, 32, 64],
    )

    update_time = Instrument.control(
        "MEAS:UPD?",
        "MEAS:UPD %f",
        """Set the time of measurement in seconds over which the data calculation is to
        be performed. Can be 0.05, 0.1, 0.25, 0.5, 1, 2, 5, or 10.""",
        validator=strict_discrete_set,
        values=[0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10],
    )

    ct_enabled = Instrument.control(
        "CONF:INP:CT?",
        "CONF:INP:CT %s",
        """Control current transformer (CT) function, ON (True) or OFF (False).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        cast=str,
    )

    ct_ratio = Instrument.control(
        "CONF:INP:CT:RAT?",
        "CONF:INP:CT:RAT %f",
        """Set the CT ratio, from 1.0 to 9999.9 with 0.1 resolution.""",
        validator=truncated_range,
        values=[1, 9999.9],
        set_process=lambda v: round(v, 1),
    )

    hv = Instrument.control(
        "CONF:INP:HV?",
        "CONF:INP:HV %s",
        """Control the HV function ON (True) or OFF (False).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        cast=str,
    )

    input_shunt = Instrument.control(
        "CONF:INP:SHUN?",
        "CONF:INP:SHUN %s",
        """Control the external input shunt resistance ON (True) or OFF (False).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        cast=str,
    )

    input_shunt_resistance = Instrument.control(
        "CONF:INP:SHUNT:RES?",
        "CONF:INP:SHUNT:RES %f",
        """Set the external input shunt resistance. Can be between 0.0000001 and 99.9999999.""",
        validator=truncated_range,
        values=[0.0000001, 99.9999999],
        set_process=lambda v: round(v, 7),
    )

    null_measure_current = Instrument.control(
        "CURR:NULL?",
        "CURR:NULL %s",
        """Control null measurements function for measuring current, enabled (True) or disabled
        (False).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        cast=str,
    )

    hold = Instrument.control(
        "CONF:HOLD?",
        "CONF:HOLD %s",
        """Control the hold function, ON (True) or OFF (False).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        cast=str,
    )

    hold_mode = Instrument.control(
        "CONF:HOLD:MODE?",
        "CONF:HOLD:MODE %s",
        """Control the hold function mode. Can be STOP, MAX, or MIN.""",
        validator=strict_discrete_set,
        values=["STOP", "MAX", "MIN"],
        cast=str,
    )

    hold_time = Instrument.control(
        "CONF:HOLD:TIME?",
        "CONF:HOLD:TIME %d",
        """Control the time of the hold function in seconds, from 0s to 9999s.""",
        validator=truncated_range,
        values=[0, 9999],
    )

    window_time = Instrument.control(
        "CONF:MEAS:WINDOW?",
        "CONF:MEAS:WINDOW %f",
        """Control window time, from 0.1s to 60.0s in 0.1s increments.""",
        validator=truncated_range,
        values=[0.1, 60.0],
        set_process=lambda v: round(v, 1),
    )

    window_interval = Instrument.control(
        "CONF:MEAS:WINDOW:UPDATE?",
        "CONF:MEAS:WINDOW:UPDATE %s",
        """Set fixed or varied interval according to window time. Can be FIXED or WINDOW.""",
        validator=strict_discrete_set,
        values=["FIXED", "WINDOW"],
        cast=str,
    )

    integrate = Instrument.control(
        "CONF:INTEGRATE?",
        "CONF:INTEGRATE %s",
        """Control meter integration ON or OFF.""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        cast=str,
    )

    integration_mode = Instrument.control(
        "CONF:INTEG:MODE?",
        "CONF:INTEG:MODE %s",
        """Set the mode of execution in integration mode. Can be NORMAL or CONTINUE.""",
        validator=strict_discrete_set,
        values=["NORMAL", "CONTINUE"],
        cast=str,
    )

    integration_time = Instrument.control(
        "CONF:INTEGRATE:TIME?",
        "CONF:INTEGRATE:TIME %d",
        """Set integration time in seconds, between 0s and 35,999,999s.""",
        validator=truncated_range,
        values=[0, 35999999],
    )

    filter = Instrument.control(
        "CONF:FILTER?",
        "CONF:FILTER %s",
        """Set the bandwidth of the digital low pass filter on input signal path.
        Can be OFF, BW500, or BW5500.""",
        validator=strict_discrete_set,
        values=["OFF", "BW500", "BW5500"],
        cast=str,
    )

    filter_frequency = Instrument.control(
        "CONF:FILT:FREQ?",
        "CONF:FILT:FREQ %s",
        """Control the low pass filter on the path of frequency detect, True (ON) or
        False (OFF).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        cast=str,
    )

    energy_time = Instrument.control(
        "CONF:ENERGY:TIME?",
        "CONF:ENERGY:TIME %d",
        """Set energy measurement time in seconds, from 0s to 35,999,999s.""",
        validator=truncated_range,
        values=[0, 35999999],
    )

    # DISPLAY #
    show = Instrument.setting(
        "SHOW:DISP:ITEM %s",
        """Control which items of measurement will be displayed on the four displays, A-D.
        All four displays must get parameters, in a comma-separated list. There is no query
        version of this command.

        +---------+---------------------------------------+
        | Display | Valid parameters                      |
        +=========+=======================================+
        | A       | V, I, W, VA, VPK+, IPK+, VPK-, IPK-   |
        +---------+---------------------------------------+
        | B       | V, I, W, PF, DEG, THDV, THDI, IS      |
        +---------+---------------------------------------+
        | C       | V, I, W, VAR, CFV, CFI, AH, WH        |
        +---------+---------------------------------------+
        | D       | V, I, W, PF, VHZ, IHZ, THDV, THDI     |
        +---------+---------------------------------------+
        """,
    )

    def configure_display(self, A: Measure, B: Measure, C: Measure, D: Measure):
        """Control the measurements shown on the four displays.

        +---------+---------------------------------------+
        | Display | Valid parameters                      |
        +=========+=======================================+
        | A       | V, I, W, VA, VPK+, IPK+, VPK-, IPK-   |
        +---------+---------------------------------------+
        | B       | V, I, W, PF, DEG, THDV, THDI, IS      |
        +---------+---------------------------------------+
        | C       | V, I, W, VAR, CFV, CFI, AH, WH        |
        +---------+---------------------------------------+
        | D       | V, I, W, PF, VHZ, IHZ, THDV, THDI     |
        +---------+---------------------------------------+
        """
        if A not in self.CHANNEL_A_DISPLAY_OPTS:
            raise ValueError(
                f"Parameter {A} not valid for display A. Must be "
                f"one of: {self.CHANNEL_A_DISPLAY_OPTS}"
            )
        if B not in self.CHANNEL_B_DISPLAY_OPTS:
            raise ValueError(
                f"Parameter {B} not valid for display B. Must be "
                f"one of: {self.CHANNEL_B_DISPLAY_OPTS}"
            )
        if C not in self.CHANNEL_C_DISPLAY_OPTS:
            raise ValueError(
                f"Parameter {C} not valid for display C. Must be "
                f"one of: {self.CHANNEL_C_DISPLAY_OPTS}"
            )
        if D not in self.CHANNEL_D_DISPLAY_OPTS:
            raise ValueError(
                f"Parameter {D} not valid for display D. Must be "
                f"one of: {self.CHANNEL_D_DISPLAY_OPTS}"
            )
        self.show = f"{A.value}, {B.value}, {C.value}, {D.value}"

    # MEASUREMENTS #
    voltage_rms = Instrument.measurement(
        "FETCH? V",
        """Get the last measured RMS voltage.""",
    )

    voltage_dc = Instrument.measurement(
        "FETCH? VDC",
        """Get the last measured DC voltage.""",
    )

    voltage_peak_pos = Instrument.measurement(
        "FETCH? VPK+",
        """Get the last measured positive peak voltage.""",
    )

    voltage_peak_neg = Instrument.measurement(
        "FETCH? VPK-",
        """Get the last measured negative peak voltage.""",
    )

    voltage_mean = Instrument.measurement(
        "FETCH? VMEAN",
        """Get the last measured mean voltage.""",
    )

    current_rms = Instrument.measurement(
        "FETCH? I",
        """Get the last measured RMS current.""",
    )

    current_dc = Instrument.measurement(
        "FETCH? IDC",
        """Get the last measured DC current.""",
    )

    current_peak_pos = Instrument.measurement(
        "FETCH? IPK+",
        """Get the last measured positive peak current.""",
    )

    current_peak_neg = Instrument.measurement(
        "FETCH? IPK-",
        """Get the last measured negative peak current.""",
    )

    inrush_current = Instrument.measurement(
        "FETCH? IS",
        """Get the last measured in-rush current.""",
    )

    current_crest_factor = Instrument.measurement(
        "FETCH? CFI",
        """Get the last measured current crest factor.""",
    )

    voltage_crest_factor = Instrument.measurement(
        "FETCH:VOLT:CRES?",
        """Get the last measured voltage crest factor.""",
    )

    power_real = Instrument.measurement(
        "FETCH? W",
        """Get the last measured RMS power.""",
    )

    power_dc = Instrument.measurement(
        "FETCH? WDC",
        """Get the last measured DC power.""",
    )

    power_factor = Instrument.measurement(
        "FETCH? PF",
        """Get the last measured power factor.""",
    )

    phase = Instrument.measurement(
        "FETCH? DEG",
        """Get phase in degrees.""",
    )

    power_apparent = Instrument.measurement(
        "FETCH? VA",
        """Get the last measured apparent power.""",
    )

    power_reactive = Instrument.measurement(
        "FETCH? VAR",
        """Get the last measured reactive power.""",
    )

    frequency = Instrument.measurement(
        "FETCH? FREQ",
        """Get the last measured frequency.""",
    )

    voltage_THD = Instrument.measurement(
        "FETCH? THDV",
        """Get the last measured voltage total harmonic distortion (THD).""",
    )

    current_THD = Instrument.measurement(
        "FETCH? THDI",
        """Get the last measured current total harmonic distortion (THD).""",
    )

    energy_wh = Instrument.measurement(
        "FETCH? WH",
        """Get the last measured energy in units of watt-hours.""",
    )

    charge_ah = Instrument.measurement(
        "FETCH? AH",
        """Get the last measured charge in units of amp-hours.""",
    )

    trigger_mode = Instrument.control(
        "TRIG:MODE?",
        "TRIG:MODE %s",
        """Set which mode will be triggered by trigger command.
        Can be NONE|INTEGRATION|INRUSH|LIMIT.""",
        validator=strict_discrete_set,
        values=["NONE", "INTEGRATION", "INRUSH", "LIMIT"],
        cast=str,
    )

    trigger = Instrument.control(
        "TRIGGER?",
        "TRIGGER %s",
        """Set trigger for energy calculation, inrush, or limit (go/no-go).
        Status is STOP|FINISH|RUNNING.
        To trigger, pass 'ON'. To stop or reset integration cycle, pass 'OFF'.""",
        cast=str,
    )

    def measure(self, param: Measure):
        """Get a measurement."""
        return float(self.ask(f"MEAS? {param.value}").strip())

    def integrate_energy(self, integration_time_s: float = 10.0):
        # Set up
        self.energy_time = integration_time_s
        self.trigger_mode = "INTEGRATION"
        # Check state and reset if necessary
        if self.trigger == "FINISH":
            self.trigger = "OFF"  # Reset
        # Trigger
        self.trigger = "ON"
        tr = self.trigger
        if tr != "RUNNING":
            print(f"Warning: Triggered but trigger is not set to 'RUNNING' (instead got {tr})")
        else:
            timeout_duration = integration_time_s * 1.5  # use 1.5x expected integration time
            start_time = time.monotonic()
            while self.trigger == "RUNNING":
                if time.monotonic() - start_time > timeout_duration:
                    raise TimeoutError(
                        f"Integration was expected to take {integration_time_s} "
                        f"secs, but took longer than {timeout_duration} secs."
                    )
        return self.energy_wh

    def capture_waveform(self, param: str = "V"):
        """Get waveform as ts,wave for voltage (V) or current (I)."""
        if param not in ["I", "V"]:
            raise ValueError(f"Unexpected parameter {param}. Must be 'V' or 'I'.")
        timeout = 100
        while self.ask("WAVEFORM:CAPTURE?") != "OK\n" and timeout > 0:
            timeout -= 1
        if timeout <= 0:
            raise TimeoutError("Waveform capture timeout.")
        print("Receiving waveform. This may take a minute...")
        bvals = self.binary_values(f"WAVEFORM:DATA? {param}", dtype=np.uint8)
        print("Done.")
        bvals = bvals[len("#48192"):-1]  # strip
        wave = bvals.view(np.float32)

        # Wave contains exactly two 60Hz cycles, so sample rate is 61440 (=2048 Samples / 2 * 60Hz)
        # This might not be consistent across all settings and configurations?
        Fs = 61.44e3
        ts = np.arange(0, len(wave) / Fs, 1 / Fs)
        return ts, wave
