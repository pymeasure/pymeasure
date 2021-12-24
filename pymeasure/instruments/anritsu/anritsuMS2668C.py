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

def anritsu_get_trace_mode(mode):
    # TODO check this function
    mode_map = {
        'WRIT;OFF': 'WRIT',
        'WRIT;MINH': 'MINH',
        'WRIT;MAXH': 'MAXH',
        'WRIT;AVER': 'WRIT',
        'WRIT;LAV': 'WRIT',
        'BLAN;OFF': 'BLANK',
        'BLAN;MINH': 'BLANK',
        'BLAN;MAXH': 'BLANK',
        'BLAN;AVER': 'BLANK',
        'BLAN;LAV': 'BLANK',
        'VIEW;OFF': 'VIEW',
        'VIEW;MINH': 'VIEW',
        'VIEW;MAXH': 'VIEW',
        'VIEW;AVER': 'VIEW',
        'VIEW;LAV': 'VIEW',
    }
    return mode_map[mode]
    
def anritsu_set_trace_mode(mode):
    # TODO check these settings
    mode_map = {
    'WRITE': "AWR 1 ; AMD 0",
    'BLANK': "BLANK",
    'VIEW': "AWR 0",
    'MAXHOLD': "AWR 1 ; AMD 1",
    'MINHOLD': "AWR 1 ; AMD 3",
    }
    return mode_map[mode]
    

class AnritsuMS2668C(SpectrumAnalyzer):
    """ This class represent an Anritsu MS2668C Spectrum Analyzer """

    # Customize parameters with values taken from datasheet/user manual 
    reference_level_values = (-100, 30)
    reference_level_set_command = "RLV %e ;"
    reference_level_get_command = "RLV?;"
    
    resolution_bw_values = (10, 3e6)
    resolution_bw_set_command = "RBW %d ;"
    resolution_bw_get_command = "RBW? ;"
    
    input_attenuation_values = {0:0, 1:10, 2:20, 3:30, 4:40, 5:50, 12:60, 13:70)
    input_attenuation_map_values = True
    input_attenuation_set_command = "ATT %d ;"
    input_attenuation_get_command = "ATT? ;"

    frequency_span_values = (0, 40.1e9)
    frequency_span_set_command = "SPF %d ;"
    frequency_span_get_command = "SPF? ;"

    start_frequency_values = (-100e6, 40e9)
    start_frequency_set_command = "STF %e ;"
    start_frequency_get_command = "STF? ;"

    stop_frequency_values = (-100e6, 40e9)
    stop_frequency_set_command = "SOF %e ;"
    stop_frequency_get_command = "SOF? ;"

    frequency_points = None # Not available

    frequency_step_values = (1, 40e9)
    frequency_step_set_command = "FSS %e ;"
    frequency_step_get_command = "FSS? ;"
    
    center_frequency_values = (-100e6, 40e9)
    center_frequency_set_command = "CNF %e ;"
    center_frequency_get_command = "CNF? ;"

    sweep_time_values = (0.02, 1000)
    sweep_time_set_command = "SWT %eS ;"
    sweep_time_get_command = "SWT? ;" # TODO check if the returned value is uS

    detector_values = ("NRM" : "NORM", "POS" : "POS", "SMP": "SAMP", "NEG" : "NEG")
    detector_map_values = True
    detector_set_command = "DET %s ;"
    detector_get_command = "DET? ;"

    sweep_mode_continuous = Instrument.setting(
        "%s;",
        """ A boolean property that allows you to switches the analyzer between continuous-sweep and single-sweep mode.
        """,
        validator=strict_discrete_set,
        values={"ON" : "CONTS",
                "OFF" : "SNGLS"},
        map_values = True,
        dynamic=True
    )

    # TODO check trace_mode
    trace_mode_get_command = ":TRACE:TYPE?;:TRACE:STORAGE:MODE?"
    trace_mode_get_process = anritsu_get_trace_mode
    trace_mode_set_command = ":TRACe:TYPE %s;"
    trace_mode_set_process = anritsu_set_trace_mode
    
    # TODO chack average_mode
    average_type_get_command = "AMD?"
    average_type_set_command = "AMD %s;"
    average_type_values = {"POWER" : 2,
                           "_NORMAL" : 0,
                           "_MAXHOLD": 1,
                           "_MINHOLD": 3,
                           "_CUMULATIVE": 4,
                           "_OVERWRITE": 5,
            }

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Anritsu MS2668C Spectrum Analyzer",
            **kwargs
        )

