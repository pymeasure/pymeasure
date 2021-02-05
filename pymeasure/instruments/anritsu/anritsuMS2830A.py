#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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

from pymeasure.instruments.spectrum_analyzer import SpectrumAnalyzer

class AnritsuMS2830A(SpectrumAnalyzer):
    """ This class represent an Anritsu MS2830A Spectrum Analyzer """

    # Customize parameters with values taken from datasheet/user manual 
    reference_level_values = (-130, 50)
    reference_level_set_command = ":DISPlay:WINDow:TRACe:Y:RLEVel %e ;"
    
    resolution_bw_values = (1, 3e6)
    resolution_bw_set_command = ":SENSe:BANDwidth %d ;"
    
    input_attenuation_values = (0, 60)

    frequency_span_values = (0, 13.7e9)
    frequency_span_set_command = ":SENS:FREQ:SPAN %d ;"

    frequency_step_set_command = ":SENS:FREQ:CENT:STEP:INCR %g;"
    
    start_frequency_set_command = ":SENS:FREQ:STAR %e ;"

    stop_frequency_set_command = ":SENS:FREQ:STOP %e ;"

    frequency_points_values = (11, 30001)

    detector_values = ("NORM", "POS", "SAMP", "NEG", "RMS")

    center_frequency_set_command = ":SENS:FREQ:CENT %e ;"

    trace_mode_get_command = ":TRACE:TYPE?;"
    trace_mode_set_command = ":TRACe:TYPE %s;"
    
    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Anritsu MS2830A Spectrum Analyzer",
            **kwargs
        )
        # Switch in SCPI mode
        self.write("SYST:LANG SCPI")
        # Switch to spectrum analyzer mode
        self.write(":INSTRUMENT:SELECT SPECT")
