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

from pymeasure.instruments import Instrument
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set,truncated_range


class Chroma66205(SCPIMixin, Instrument):
    """Control the Chroma 66205 Digital Power Meter

    The 66205 is a single-channel unit. Most of its interface is identical to the other
    6620x instruments.
    """

    def __init__(self, adapter, name="Chroma 66205", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    # SETTINGS #
    mode = Instrument.control(
        "CONF:MEAS:MODE?",
        "CONF:MEAS:MODE %s",
        """Control measurement mode. Can be RMS, DC, or VMEAN.""",
        validator=strict_discrete_set,
        values=["RMS","DC","VMEAN"]
    )
    averages = Instrument.control(
        "CONF:MEAS:AVERAGE?",
        "CONF:MEAS:AVERAGE %d",
        """Control number of measurements to average in averaging mode. Must be a power of 2
        between 1 and 64 inclusive.""",
        validator=strict_discrete_set,
        values=[1,2,4,8,16,32,64],
    )
    window_time = Instrument.control(
        "CONF:MEAS:WINDOW?",
        "CONF:MEAS:WINDOW %f",
        """Control window time, from 0.1s to 60.0s in 0.1s increments.""",
        validator=truncated_range,
        values = [0.1,60.]
    )
    window_interval = Instrument.control(
        "CONF:MEAS:WINDOW:UPDATE?",
        "CONF:MEAS:WINDOW:UPDATE %s",
        """Set fixed or varied interval according to window time. Can be FIXED or WINDOW.""",
        validator=strict_discrete_set,
        values=["FIXED","WINDOW"]
    )
    integrate = Instrument.control(
        "CONF:INTEGRATE?",
        "CONF:INTEGRATE %s",
        """Control meter integration ON or OFF.""",
        validator=strict_discrete_set,
        values={True:"ON",False:"OFF"},
        map_values=True,
    )
    integration_mode = Instrument.control(
        "CONF:INTEG:MODE?",
        "CONF:INTEG:MODE %s",
        """Set the mode of execution in integration mode. Can be NORMAL or CONTINUE.""",
        validator=strict_discrete_set,
        values=["NORMAL","CONTINUE"],
    )
    integration_time = Instrument.control(
        "CONF:INTEGRATE:TIME?",
        "CONF:INTEGRATE:TIME %d",
        """Set integration time in seconds, between 0s and 35,999,999s.""",
        validator=truncated_range,
        values=[0,35999999]
    )
    filter = Instrument.control(
        "CONF:FILTER?",
        "CONF:FILTER %s",
        """Set the bandwidth of the digital low pass filter on input signal path.
        Can be OFF, BW500, or BW5500.""",
        validator=strict_discrete_set,
        values=["OFF","BW500","BW5500"],
    )
    filter_frequency = Instrument.control(
        "CONF:FILT:FREQ?",
        "CONF:FILT:FREQ %s",
        """Set the low pass filter on the path of frequency detect, True (ON) or False (OFF).""",
        values={True:"ON",False:"OFF"},
        map_values=True,
    )
    energy_time = Instrument.control(
        "CONF:ENERGY:TIME?",
        "CONF:ENERGY:TIME %d",
        """Set energy measurement time in seconds, from 0s to 35,999,999s.""",
        validator=truncated_range,
        values=[0,35999999]
    )

    # MEASUREMENTS #
    voltage_rms = Instrument.measurement(
        "FETCH? V",
        """Get the last measured RMS voltage."""
    )
    voltage_dc = Instrument.measurement(
        "FETCH? VDC",
        """Get the last measured DC voltage."""
    )
    voltage_peak_pos = Instrument.measurement(
        "FETCH? VPK+",
        """Get the last measured positive peak voltage."""
    )
    voltage_peak_neg = Instrument.measurement(
        "FETCH? VPK-",
        """Get the last measured negative peak voltage."""
    )
    voltage_mean = Instrument.measurement(
        "FETCH? VMEAN",
        """Get the last measured mean voltage."""
    )
    current_rms = Instrument.measurement(
        "FETCH? I",
        """Get the last measured RMS current."""
    )
    current_dc = Instrument.measurement(
        "FETCH? IDC",
        """Get the last measured DC current."""
    )
    current_peak_pos = Instrument.measurement(
        "FETCH? IPK+",
        """Get the last measured positive peak current."""
    )
    current_peak_neg = Instrument.measurement(
        "FETCH? IPK-",
        """Get the last measured negative peak current."""
    )
    inrush_current = Instrument.measurement(
        "FETCH? IS",
        """Get the last measured in-rush current."""
    )
    crest_factor = Instrument.measurement(
        "FETCH? CFI",
        """Get the last measured current crest factor."""
    )
    power_real = Instrument.measurement(
        "FETCH? W",
        """Get the last measured RMS power."""
    )
    power_dc = Instrument.measurement(
        "FETCH? WDC",
        """Get the last measured DC power."""
    )
    power_factor = Instrument.measurement(
        "FETCH? PF",
        """Get the last measured power factor."""
    )
    phase = Instrument.measurement(
        "FETCH? DEG",
        """Get phase in degrees."""
    )
    power_apparent = Instrument.measurement(
        "FETCH? VA",
        """Get the last measured apparent power."""
    )
    power_reactive = Instrument.measurement(
        "FETCH? VAR",
        """Get the last measured reactive power."""
    )
    frequency = Instrument.measurement(
        "FETCH? FREQ",
        """Get the last measured frequency."""
    )
    voltage_THD = Instrument.measurement(
        "FETCH? THDV",
        """Get the last measured voltage THD."""
    )
    current_THD = Instrument.measurement(
        "FETCH? THDI",
        """Get the last measured current THD."""
    )
    energy_wh = Instrument.measurement(
        "FETCH? WH",
        """Get the last measured energy in units of watt-hours."""
    )
    charge_ah = Instrument.measurement(
        "FETCH? AH",
        """Get the last measured charge in units of amp-hours."""
    )
    trigger_mode = Instrument.control(
        "TRIG:MODE?",
        "TRIG:MODE %s",
        """Set which mode will be triggered by trigger command.
        Can be NONE|INTEGRATION|INRUSH|LIMIT.""",
        validator=strict_discrete_set,
        values=["NONE","INTEGRATION","INRUSH","LIMIT"],
    )
    trigger = Instrument.control(
        "TRIGGER?",
        "TRIGGER %s",
        """Trigger energy calculation, inrush, or limit (go/no-go).
        Status is STOP|FINISH|RUNNING.
        To trigger, pass 'ON'. To stop or reset integration cycle, pass 'OFF'.""",
    )

    def integrate_energy(self,integration_time_s: float=10.):
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
            while self.trigger == "RUNNING":
                pass
        return self.energy_wh

    def capture_waveform(self,param:str='V'):
        """Get waveform as ts,wave for voltage (V) or current (I)."""
        if param not in ['I','V']:
            raise ValueError(f"Unexpected parameter {param}. Must be 'V' or 'I'.")
        timeout = 100
        while self.ask('WAVEFORM:CAPTURE?') != 'OK\n' and timeout > 0:
            timeout -= 1
        print("Receiving waveform. This may take a minute...")
        bvals = self.binary_values(f'WAVEFORM:DATA? {param}',dtype=np.uint8)
        print("Done.")
        bvals = bvals[len('#48192'):-1]  # strip
        wave = bvals.view(np.float32)

        # Wave contains exactly two 60Hz cycles, so sample rate is 61440 (=2048 Samples / 2 * 60Hz)
        # This might not be consistent across all settings and configurations?
        Fs=61.44e3
        ts = np.arange(0,len(wave)/Fs,1/Fs)
        return ts,wave


