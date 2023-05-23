#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    strict_discrete_set,
    truncated_discrete_set,
    truncated_range,
    joined_validators
)


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# Join validators to allow for special sets of characters
truncated_range_or_off = joined_validators(strict_discrete_set, truncated_range)


class AdvantestQ8381(Instrument):
    """Advantest Q8381 Optical Spectrum Analyzer."""
    ONOFF = {True: 'ON', False: 'OFF'}

    def __init__(self, adapter, name="Anritsu MS9710C Optical Spectrum Analyzer", **kwargs):
        """Constructor."""
        self.analysis_mode = None
        super().__init__(adapter, name=name, **kwargs)

    ###########
    #  Modes  #
    ###########

    measure_mode = Instrument.measurement(
        "MOD?", "Returns the current Measure Mode the OSA is in.",
        values={None: 0, "SINGLE": 1.0, "AUTO": 2.0, "POWER": 3.0},
        map_values=True
    )

    ####################################
    # Spectrum Parameters - Wavelength #
    ####################################
    wavelength_center = Instrument.control(
        'CEN?', 'CEN %gnm', "Center Wavelength of Spectrum Scan in nm.")

    wavelength_span = Instrument.control(
        'SPA?', 'SPA %gnm', "Wavelength Span of Spectrum Scan in nm.")

    wavelength_start = Instrument.control(
        'STA?', 'STA %gnm', "Wavelength Start of Spectrum Scan in nm.")

    wavelength_stop = Instrument.control(
        'STO?', 'STO %gnm', "Wavelength Stop of Spectrum Scan in nm.")

    wavelength_marker_value = Instrument.control(
        'MKV?', 'MKV %s',
        "Wavelength Marker Value (wavelength or freq.?)",
        validator=strict_discrete_set,
        values=["WL", "FREQ"]
    )

    wavelength_value_in = Instrument.control(
        'WDP?', 'WDP %s',
        "Wavelength value in Vacuum or Air",
        validator=strict_discrete_set,
        values=["VACUUM", "AIR"]
    )

    level_scale = Instrument.control(
        'LVS?', "LVS %s", 
        "Current Level Scale",
        values=["LOG", "LIN"]
    )

    level_log = Instrument.control(
        "LOG?", "LOG %f", "Level Log Scale (/div)",
        validator=truncated_range, values=[0.1, 10.0]
    )

    level_lin = Instrument.control(
        "LIN?", "LIN %f", "Level Linear Scale (/div)",
        validator=truncated_range, values=[1e-12, 1]
    )

    level_opt_attn = Instrument.control(
        "ATT?", "ATT %s", "Optical Attenuation Status (ON/OFF)",
        validator=strict_discrete_set,
        values=ONOFF
    )

    resolution = Instrument.control(
        "RES?", "RES %f", "Resolution (nm)",
        validator=truncated_discrete_set,
        values=[0.05, 0.07, 0.1, 0.2, 0.5, 1.0]
    )

    resolution_actual = Instrument.control(
        "ARES?", "ARES %s", "Resolution Actual (ON/OFF)",
        validator=strict_discrete_set,
        values=ONOFF,
        map_values=True

    )

    resolution_vbw = Instrument.control(
        "VBW?", "VBW %s", "Video Bandwidth Resolution",
        validator=strict_discrete_set,
        values=["1MHz", "100kHz", "10kHz", "1kHz", "100Hz", "10Hz"]
    )

    average_point = Instrument.control(
        "AVT?", "AVT %d",
        "Number of averages to take on each point (2-1000), or OFF",
        validator=truncated_range_or_off,
        values=[["OFF"], [2, 1000]]
    )

    average_sweep = Instrument.control(
        "AVS?", "AVS %d",
        "Number of averages to make on a sweep (2-1000) or OFF",
        validator=truncated_range_or_off,
        values=[["OFF"], [2, 1000]]
    )

    sampling_points = Instrument.control(
        "MPT?", "MPT %d", "Number of sampling points",
        validator=truncated_discrete_set,
        values=[51, 101, 251, 501, 1001, 2001, 5001],
        get_process=lambda v: int(v)
    )

    #####################################
    #  Analysis Peak Search Parameters  #
    #####################################

    peak_search = Instrument.control(
        "PKS?", "PKS %s", "Peak Search Mode",
        validator=strict_discrete_set,
        values=["PEAK", "NEXT", "LAST", "LEFT", "RIGHT"]
    )

    dip_search = Instrument.control(
        "DPS?", "DPS %s", "Dip Search Mode",
        validator=strict_discrete_set,
        values=["DIP", "NEXT", "LAST", "LEFT", "RIGHT"]
    )

    analysis = Instrument.control(
        "ANA?", "ANA %s", "Analysis Control"
    )

    analysis_result = Instrument.measurement(
        "ANAR?", "Read back anaysis result from current scan."
    )
