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
import logging
from pymeasure.instruments import Instrument
from pymeasure.instruments.anritsu import AnritsuMS9710C
from pymeasure.instruments.validators import (
    strict_discrete_set,
    truncated_discrete_set,
    truncated_range,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AnritsuMS9740A(AnritsuMS9710C):
    """Anritsu MS9740A Optical Spectrum Analyzer."""

    def __init__(self, adapter, name="Anritsu MS9740A Optical Spectrum Analyzer", **kwargs):
        """Constructor."""
        self.analysis_mode = None
        super().__init__(
            adapter, name, **kwargs)

    ####################################
    # Spectrum Parameters - Wavelength #
    ####################################

    resolution = Instrument.control(
        "RES?", "RES %s", "Control Resolution (nm)",
        validator=truncated_discrete_set,
        values=[0.03, 0.05, 0.07, 0.1, 0.2, 0.5, 1.0],
    )

    resolution_vbw = Instrument.control(
        "VBW?", "VBW %s", "Control Video Bandwidth Resolution",
        validator=strict_discrete_set,
        values=["1MHz", "100kHz", "10kHz", "2kHz", "1kHz", "200Hz", "100Hz", "10Hz"]
    )

    average_sweep = Instrument.control(
        "AVS?", "AVS %d",
        """Control number of averages to make on a sweep (1-1000),
        with 1 being a single (non-averaged) sweep""",
        validator=truncated_range, values=[1, 1000]
    )

    sampling_points = Instrument.control(
        "MPT?", "MPT %d", "Control number of sampling points",
        validator=truncated_discrete_set,
        values=[51, 101, 251, 501, 1001, 2001, 5001, 10001, 20001, 50001],
        get_process=lambda v: int(v)
    )

    ##########################
    #  Data Memory Commands  #
    ##########################

    data_memory_select = Instrument.control(
        "TTP?", "TTP %s",
        "Control Memory Data Select.",
        validator=strict_discrete_set,
        values=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    )

    def repeat_sweep(self, n=20, delay=0.5):
        """Perform a single sweep and wait for completion."""
        log.debug("Performing a repeat Spectrum Sweep")
        self.clear()
        self.write('SRT')
        self.wait_for_sweep(n=n, delay=delay)
