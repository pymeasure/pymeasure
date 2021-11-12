#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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
from pymeasure.instruments.anritsu import AnritsuMS9710C
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
r_value_units = re.compile("([-\d]*\.\d*)(.*)")

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


class AnritsuMS9740A(AnritsuMS9710C):
    """Anritsu MS9740A Optical Spectrum Analyzer."""
    
    #############
    #  Mappings #
    #############
    ONOFF = ["ON", "OFF"]
    ONOFF_MAPPING = {True: 'ON', False: 'OFF', 1: 'ON', 0: 'OFF'}

        # OPC = Instrument.control(
    #     "*OPC?", "*OPC?",
    #     "Operation complete?",
    #     get_process=int
    # )

    ###########
    #  Modes  #
    ###########

    measure_mode = Instrument.measurement(
        "MOD?", "Returns the current Measure Mode the OSA is in.",
        values={None: 0, "SINGLE": 1.0, "REPEAT": 2.0, "POWER": 3.0},
        map_values=True
    )

    ####################################
    # Spectrum Parameters - Wavelength #
    ####################################
    

    resolution = Instrument.control(
        "RES?", "RES %s", "Resolution (nm)",
        validator=truncated_discrete_set,
        values=[0.03, 0.05, 0.07, 0.1, 0.2, 0.5, 1.0],
    )

    resolution_vbw = Instrument.control(
        "VBW?", "VBW %s", "Video Bandwidth Resolution",
        validator=strict_discrete_set,
        values=["1MHz", "100kHz", "10kHz", "2kHz", "1kHz", "200Hz", "100Hz", "10Hz"]
    )

    # average_point = Instrument.control(
    #     "AVT?", "AVT %d",
    #     "Number of averages to take on each point (2-1000) or OFF",
    #             validator=truncated_range_or_off,
    #     values=[["OFF"], [2, 1000]]

    # )

    average_sweep = Instrument.control(
        "AVS?", "AVS %d",
        "Number of averages to make on a sweep (1-1000)",
        validator=truncated_range, values=[1, 1000]
    )

    sampling_points = Instrument.control(
        "MPT?", "MPT %d", "Number of sampling points",
        validator=truncated_discrete_set,
        values=[51, 101, 251, 501, 1001, 2001, 5001, 10001, 20001, 50001],
        get_process=lambda v: int(v)
    )

   

    ##########################
    #  Data Memory Commands  #
    ##########################

    data_memory_select = Instrument.control(
        "TTP?", "TTP %s",
        "Memory Data Select.",
        validator=strict_discrete_set,
        values=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    )

    def __init__(self, adapter, **kwargs):
        """Constructor."""
        self.analysis_mode = None
        super(AnritsuMS9740A, self).__init__(adapter, "Anritsu MS9740A Optical Spectrum Analyzer", **kwargs)

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

        while(self.esr2 != 1 and n > 0):
            print(self.esr2)
            log.debug("Wait for sweep [{}]".format(n))
            # log.debug("ESR2: {}".format(esr2))
            sleep(delay)
            n -= 1

        if n <= 0:
            log.warning("Sweep Timeout Occurred ({} s)".format(int(delay * n)))

    def repeat_sweep(self, **kwargs):
        """Perform a single sweep and wait for completion."""
        log.debug("Performing a repeat Spectrum Sweep")
        self.clear()
        self.write('SRT')
        self.wait_for_sweep(**kwargs)

   