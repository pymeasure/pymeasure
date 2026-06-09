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
        """Control measurement mode. Can be WINDOW or AVERAGE.""",
        validator=strict_discrete_set,
        values=["WINDOW","AVERAGE"]
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
        """Set the low pass filter ON or OFF.""",
        validator=strict_discrete_set,
        values={True:"ON",False:"OFF"},
        map_values=True,
    )
    energy_unit = Instrument.control(
        "CONF:ENERGY:MODE?",
        "CONF:ENERGY:MODE %s",
        """Set energy unit to joules (JOULES) or watt-hours (WHR).""",
        validator=strict_discrete_set,
        values=["JOULES","WHR"]
    )
    energy_time = Instrument.control(
        "CONF:ENERGY:TIME?",
        "CONF:ENERGY:TIME %d",
        """Set energy measurement time in seconds, from 0s to 35,999,999s.""",
        validator=truncated_range,
        values=[0,35999999]
    )

    # MEASUREMENTS #
    voltage = Instrument.measurement(
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
    current = Instrument.measurement(
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
    power = Instrument.measurement(
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
    energy = Instrument.measurement(
        "MEAS:POW:ENER?",
        """Get the last measured energy, with units according to CONF:ENERGY:MODE."""
    )

