#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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
from pymeasure.instruments.validators import (
    strict_discrete_set,
    truncated_discrete_set,
    truncated_range,
    joined_validators
)
import re

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# Analysis Results with Units, ie -24.5DBM -> (-24.5, 'DBM')
r_value_units = re.compile(r"([-\d]*\.\d*)(.*)")

# Join validators to allow for special sets of characters
truncated_range_or_off = joined_validators(strict_discrete_set, truncated_range)


def _int_or_neg_one(v):
    try:
        return int(v)
    except ValueError:
        return -1


def _parse_trace_peak(vals):
    """Parse the returned value from a trace peak query."""
    l, p = vals
    res = [l]
    m = r_value_units.match(p)
    if m is not None:
        data = list(m.groups())
        data[0] = float(data[0])
        res.extend(data)
    else:
        res.append(float(p))
    return res


class AnritsuMS9710C(Instrument):
    """Anritsu MS9710C Optical Spectrum Analyzer."""

    #############
    #  Mappings #
    #############
    ONOFF = ["ON", "OFF"]
    ONOFF_MAPPING = {True: 'ON', False: 'OFF', 1: 'ON', 0: 'OFF'}

    ######################
    #  Status Registers  #
    ######################

    ese2 = Instrument.control(
        "ESE2?", "ESE2 %d",
        "Extended Event Status Enable Register 2",
        get_process=int
    )

    esr2 = Instrument.control(
        "ESR2?", "ESR2 %d",
        "Extended Event Status Register 2",
        get_process=_int_or_neg_one
    )

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
    wavelength_center = Instrument.control('CNT?', 'CNT %g', "Center Wavelength of Spectrum Scan in nm.")

    wavelength_span = Instrument.control('SPN?', 'SPN %g', "Wavelength Span of Spectrum Scan in nm.")

    wavelength_start = Instrument.control('STA?', 'STA %g', "Wavelength Start of Spectrum Scan in nm.")

    wavelength_stop = Instrument.control('STO?', 'STO %g', "Wavelength Stop of Spectrum Scan in nm.")

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

    level_scale = Instrument.measurement(
        'LVS?', "Current Level Scale",
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

    ##########################
    #  Data Memory Commands  #
    ##########################

    data_memory_a_size = Instrument.measurement(
        'DBA?',
        "Returns the number of points sampled in data memory register A."
    )

    data_memory_b_size = Instrument.measurement(
        'DBB?',
        "Returns the number of points sampled in data memory register B."
    )

    data_memory_a_condition = Instrument.measurement(
        "DCA?",
        """Returns the data condition of data memory register A.
        Starting wavelength, and a sampling point (l1, l2, n)."""
    )

    data_memory_b_condition = Instrument.measurement(
        "DCB?",
        """Returns the data condition of data memory register B.
        Starting wavelength, and a sampling point (l1, l2, n)."""
    )

    data_memory_a_values = Instrument.measurement(
        "DMA?",
        "Reads the binary data from memory register A."
    )

    data_memory_b_values = Instrument.measurement(
        "DMA?",
        "Reads the binary data from memory register B."
    )

    data_memory_select = Instrument.control(
        "MSL?", "MSL %s",
        "Memory Data Select.",
        validator=strict_discrete_set,
        values=["A", "B"]
    )

    ###########################
    #  Trace Marker Commands  #
    ###########################

    trace_marker_center = Instrument.setting(
        "TMC %s", "Trace Marker at Center. Set to 1 or True to initiate command",
        map_values=True,
        values={True: ''}
    )

    trace_marker = Instrument.control(
        "TMK?", "TMK %f",
        "Sets the trace marker with a wavelength.  Returns the trace wavelength and power.",
        get_process=_parse_trace_peak
    )

    def __init__(self, adapter, **kwargs):
        """Constructor."""
        self.analysis_mode = None
        super(AnritsuMS9710C, self).__init__(adapter, "Anritsu MS9710C Optical Spectrum Analyzer", **kwargs)

    @property
    def wavelengths(self):
        """Return a numpy array of the current wavelengths of scans."""
        return np.linspace(
            self.wavelength_start,
            self.wavelength_stop,
            self.sampling_points
        )

    def read_memory(self, slot="A"):
        """Read the scan saved in a memory slot."""
        cond_attr = "data_memory_{}_condition".format(slot.lower())
        data_attr = "data_memory_{}_values".format(slot.lower())

        scan = getattr(self, cond_attr)
        wavelengths = np.linspace(scan[0], scan[1], int(scan[2]))
        power = np.fromstring(getattr(self, data_attr), sep="\r\n")

        return wavelengths, power

    def wait(self, n=3, delay=1):
        """Query OPC Command and waits for appropriate response."""
        log.info("Wait for OPC")
        res = self.adapter.ask("*OPC?")
        n_attempts = n
        while(res == ''):
            log.debug("Empty OPC Repsonse. {} remaining".format(n_attempts))
            if n_attempts == 0:
                break
            n_attempts -= 1
            sleep(delay)
            res = self.adapter.read().strip()

        log.debug(res)

    def wait_for_sweep(self, n=20, delay=0.5):
        """Wait for a sweep to stop.

        This is performed by checking bit 1 of the ESR2.
        """
        log.debug("Waiting for spectrum sweep")

        while(self.esr2 != 3 and n > 0):
            log.debug("Wait for sweep [{}]".format(n))
            # log.debug("ESR2: {}".format(esr2))
            sleep(delay)
            n -= 1

        if n <= 0:
            log.warning("Sweep Timeout Occurred ({} s)".format(int(delay * n)))

    def single_sweep(self, **kwargs):
        """Perform a single sweep and wait for completion."""
        log.debug("Performing a Spectrum Sweep")
        self.clear()
        self.write('SSI')
        self.wait_for_sweep(**kwargs)

    def center_at_peak(self, **kwargs):
        """Center the spectrum at the measured peak."""
        self.write("PKC")
        self.wait(**kwargs)

    def measure_peak(self):
        """Measure the peak and return the trace marker."""
        self.peak_search = "PEAK"
        return self.trace_marker
