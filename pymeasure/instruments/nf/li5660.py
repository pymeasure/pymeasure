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

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument #, RangeException
from pymeasure.instruments.validators import truncated_range, strict_discrete_set
# from pymeasure.adapters import PrologixAdapter
# from pymeasure.instruments.validators import truncated_range, strict_discrete_set

# import numpy as np
# import time
# from io import BytesIO
# import re

class LI5660(Instrument):

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "NF Lock-In Amplifier LI5600",
            **kwargs
        )
    
    amplifier_id = Instrument.measurement(
        "*IDN?", """Reads the instrument identification """
    )

    ####################################
    # Calculate subsystem, 23 Nov 2020 #
    ####################################
    calaulate1_format = Instrument.control(
        ":CALC1:FORM?",":CALC1:FORM %s",
        """ A property that allow user to set the measurement parameters to be displayed and output as DATA1. """,
        validator=strict_discrete_set,
        values={"Real": "REAL",
                "Mlinear": "MLIN",
                "Imaginary": "IMAG",
                "Phase": "PHAS",
                "Noise": "NOIS",
                "Aux1": "AUX1",
                "Real2": "REAL2",
                "Mlinear2": "MLIN2"},
        map_values=True
    )

    calculate2_format = Instrument.control(
        ":CALC2:FORM?",":CALC2:FORM %s",
        """ A property that allow user to set the measurement parameters to be displayed and outpout as DATA2. """,
        validator=strict_discrete_set,
        values={"Imaginary": "IMAG",
                "Phase": "PHAS",
                "Aux1": "AUX1",
                "Aux2": "AUX2",
                "Real2": "REAL2",
                "Mlinear2": "MLIN2",
                "Imaginary2": "IMAG2",
                "Phase2": "PHAS2"},
        map_values=True
    )

    calculate3_format = Instrument.control(
        ":CALC3:FORM?", ":CALC3:FORM %s",
        """ A property that allow user to set the measurement parameters to be displayed and outpout as DATA3. """,
        validator=strict_discrete_set,
        values={"Real": "REAL",
                "Mlinear": "MLIN",
                "Imaginary": "IMAG",
                "Phase": "PHAS",
                "Real2": "REAL2",
                "Mlinear2": "MLIN2"},
        map_values=True
    )

    calculate4_format = Instrument.control(
        ":CALC4:FORM?", ":CALC4:FORM %s",
        """ A property that allow user to set the measurement parameters to be displayed and outpout as DATA4. """,
        validator=strict_discrete_set,
        values={"Imaginary": "IMAG",
                "Phase": "PHAS",
                "Real2": "REAL2",
                "Mlinear2": "MLIN2",
                "Imaginary2": "IMAG2",
                "Phase2": "PHAS2"},
        map_values=True
    )

    calculate1_math_current = Instrument.control(
        ":CALC1:MATH:CURR?",":CALC1:MATH:CURR %g",
        """ A property that allow user to set the current reference value for normalize calculation. """,
        validator=truncated_range,
        values=[1e-15, 1e-6]
    )

    calculation1_math_expression_name = Instrument.control(
        ":CALC1:MATH:EXPR:NAME?", ":CALC1:MATH:EXPR:NAME %s", 
        """ A property that allow user to normalize calculation format. """,
        validator=strict_discrete_set,
        values={"DB": "DB, 'dB'",
                "Reference": "PCNT, ''",
                "Sensitivity": "PCFS, ''",
                },
        map_values=True
    )

    calculate1_math_voltage = Instrument.control(
        ":CALC1:MATH:VOLT?", ":CALC1:MATH:VOLT %g",
        """ A property that allow user to set the voltage reference value for normalize calculation. """,
        validator=truncated_range,
        values=[1e-9, 1e+1]
    )

    calculate1_multiplier = Instrument.control(
        ":CALC1:MULT?", ":CALC5:MATH EXP; :CALC1:MULT %d",
        """ A property that allow user to set the primary PSD's R, X output common expand multiplier.
            Display and output of expand results also requires enabling expand calculation with the
            :CALCulate5:MATH EXP command. """,
        validator=strict_discrete_set,
        values=[1, 10, 100]
    )

    calculate2_multiplier = Instrument.control(
        ":CALC2:MULT?", ":CALC5:MATH EXP; :CALC2:MULT %d",
        """ A property that allow user to set the primary PSD's Y output common expand multiplier.
            Display and output of expand results also requires enabling expand calculation with the
            :CALCulate5:MATH EXP command. """,
        validator=strict_discrete_set,
        values=[1, 10, 100]
    )

    calculate3_multiplier = Instrument.control(
        ":CALC3:MULT?", ":CALC5:MATH EXP; :CALC3:MULT %d",
        """ A property that allow user to set the secondary PSD's R, X output common expand multiplier.
            Display and output of expand results also requires enabling expand calculation with the
            :CALCulate5:MATH EXP command. """,
        validator=strict_discrete_set,
        values=[1, 10, 100]
    )

    calculate4_multiplier = Instrument.control(
        ":CALC4:MULT?", ":CALC5:MATH EXP; :CALC4:MULT %d",
        """ A property that allow user to set the secondary PSD's Y output common expand multiplier.
            Display and output of expand results also requires enabling expand calculation with the
            :CALCulate5:MATH EXP command. """,
        validator=strict_discrete_set,
        values=[1, 10, 100]
    )

    calculate1_offset = Instrument.control(
        "CALC1:OFFS?",":CALC1:OFFS:STAT ON; :CALC1:OFFS %g",
        """ A property that allow user to offset for the primary PSD's X output. """,
        validator=truncated_range,
        values=[-105, 105]
    )

    calculate2_offset = Instrument.control(
        "CALC2:OFFS?",":CALC2:OFFS:STAT ON; :CALC2:OFFS %g",
        """ A property that allow user to offset for the primary PSD's Y output. """,
        validator=truncated_range,
        values=[-105, 105]
    )

    calculate3_offset = Instrument.control(
        "CALC3:OFFS?",":CALC3:OFFS:STAT ON; :CALC3:OFFS %g",
        """ A property that allow user to offset for the secondary PSD's X output. """,
        validator=truncated_range,
        values=[-105, 105]
    )

    calculate4_offset = Instrument.control(
        "CALC4:OFFS?",":CALC4:OFFS:STAT ON; :CALC4:OFFS %g",
        """ A property that allow user to offset for the secondary PSD's Y output. """,
        validator=truncated_range,
        values=[-105, 105]
    )

    calculate1_offset_state = Instrument.control(
        ":CALC1:OFFS:STAT?", ":CALC1:OFFS:STAT %s",
        """ A property that allow user to enable/disable offset for the primary PSD's X output. """,
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    calculate2_offset_state = Instrument.control(
        ":CALC2:OFFS:STAT?", ":CALC2:OFFS:STAT %s",
        """ A property that allow user to enable/disable offset for the primary PSD's X output. """,
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    calculate3_offset_state = Instrument.control(
        ":CALC3:OFFS:STAT?", ":CALC3:OFFS:STAT %s",
        """ A property that allow user to enable/disable offset for the primary PSD's X output. """,
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    calculate4_offset_state = Instrument.control(
        ":CALC4:OFFS:STAT?", ":CALC4:OFFS:STAT %s",
        """ A property that allow user to enable/disable offset for the primary PSD's X output. """,
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    calculation_method = Instrument.control(
        ":CALC5:MATH?", ":CALC5:MATH %s",
        """ A property that allow user to set the calculation method for measurement value to be displayed and output. """,
        validator=strict_discrete_set,
        values={"Off": "OFF",
                "Expand": "EXP",
                "Normalize": "NORM",
                "Ratio": "RAT"},
        map_values=True
    )

    ###############################
    # Data subsystem, 24 Nov 2020 #
    ###############################
    buffer1_count = Instrument.measurement(
        ":DATA:COUN? BUF1",
        """ A property that allow user to queries the number of data sampling points recorded in the measurement data buffer1. """
    )

    buffer2_count = Instrument.measurement(
        ":DATA:COUN? BUF2",
        """ A property that allow user to queries the number of data sampling points recorded in the measurement data buffer2. """
    )

    buffer3_count = Instrument.measurement(
        ":DATA:COUN? BUF3",
        """ A property that allow user to queries the number of data sampling points recorded in the measurement data buffer3. """
    )

    data_timer = Instrument.control(
        ":DATA:TIM?", ":DATA:TIM:STAT ON; :DATA:TIM %g",
        """ A property that allow user to set the internal timer time interval. The time resolution is 640 ns """,
        validator=truncated_range,
        values=[1.92E-6, 20]
    )

    data_timer_state = Instrument.control(
        ":DATA:TIM:STAT?", ":DATA:TIM:STAT %d",
        """ A property that allow user to enable or disable the internal timer. """,
        validator=strict_discrete_set,
        values={"On": 1,
                "Off": 0},
        map_values=True
    )

    ##################################
    # Display subsystem, 25 Nov 2020 #
    ##################################
    screen = Instrument.control(
        ":DISP?", ":DISP %s", 
        """There are 3 types of measurement screen display: Normal, Large and Fine Measurement screens""",
        validator = strict_discrete_set,
        values={"Normail": "NORM", "Large": "LARG", "Fine": "FINE"},
        map_values=True
    )

    display_window = Instrument.control(
        ":DISP:WIND?", ":DISP:WIND %d",
        """ A property that allow user to on/off the display screen. """,
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    ################################
    # Fetch subsystem, 25 Nov 2020 #
    ################################
    fetch = Instrument.measurement(
        ":FETC?",
        """ Queries the most recent measurement data. """
    )

    #################################
    # Format subsystem, 25 Nov 2020 #
    #################################
    format = Instrument.control(
        ":FORM?", ":FORM %s",
        """ A property that allow user to set the data transfer format. """,
        validator=strict_discrete_set,
        values={"ASCII": "ASC",
                "Real": "REAL",
                "Integer": "INT"},
        map_values=True
    )

    ################################
    # Input subsystem, 25 Nov 2020 #
    ################################
    input_coupling = Instrument.control(
        ":INP:COUP?", ":INP:COUP %s",
        """ A property that allow user to set the signal input result method. """,
        validator=strict_discrete_set,
        values=["AC", "DC"]
    )

    input_filter_notch_frequency = Instrument.control(
        ":INP:FILT:NOTC1:FREQ?", ":INP:FILT:NOTC1:FREQ %d",
        """ A property that allow user to set the notch filter (fundamental wave) center frequency.
            The notch filter removes power supply frequency noise. Unit in Hz.""",
        validator=strict_discrete_set,
        values=[50, 60]
    )

    input_filter_notch1_state = Instrument.control(
        ":INP:FILT:NOTC1?", ":INP:FILT:NOTC1 %d",
        """ A property that allow user to enable/disable the notch filter. 
            Notch1 filter used to removes the power supply fundamental wave (50 or 60 Hz).""",
        validator=strict_discrete_set,
        values={"On": 1,
                "Off": 0},
        map_values=True
    )

    input_filter_notch2_state =  Instrument.control(
        ":INP:FILT:NOTC2?", ":INP:FILT:NOTC2 %d",
        """ A property that allow user to enable/disable the notch filter. 
            Notch2 filter used to removes the power supply second harmonic (100 or 120 Hz). """,
        validator=strict_discrete_set,
        values={"On": 1,
                "Off": 0},
        map_values=True
    )

    input_gain = Instrument.control(
        ":INP:GAIN?", ":INP:GAIN %s",
        """ A property that allow user to set the current-voltage conversion gain for current input. """,
        validator=strict_discrete_set,
        values={1: "IE6", 100: "IE8"},
        map_values=True
    )

    input_impedance = Instrument.control(
        ":INP:IMP?", ":INP:IMP %g",
        """ A property that allow user to set the HF terminal input impedance.
            Rounding is applied to arbitrary values specified. """,
        values=[50, 1E6],
        map_values=False
    )

    input_low = Instrument.control(
        ":INP:LOW?", ":INP:LOW %s",
        """ A property that allow user to set the grounding of the signal input connector's conductor.""",
        validator=strict_discrete_set,
        values={"Float": "FLO", "Ground": "GRO"},
        map_values=True
    )

    input_offset_auto = Instrument.control(
        ":INP:OFFS:AUTO?", ":INP:OFFS:AUTO %d",
        """ A property that allow user to set the PSD input offset continuius auto adjusted.""",
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    input_offset_stime = Instrument.control(
        ":INP:OFFS:STIM?", ":INP:OFFS:STIM %g",
        """ A property that allow user to set response time for the PSD input offset continuous auto adjustment function.
            Rounding is applied to arbirary values specified. """,
        values=[200E-3, 750E-3, 3000E-3],
        map_values=False
    )

    input_type = Instrument.control(
        ":INP2:TYPE?", ":INP2:TYPE %s",
        """ A property that allow user to set the reference signal waveform. """,
        validator=strict_discrete_set,
        values={"Sine": "SIN",
                "TTL Rising": "TPOS",
                "TTL Falling": "TNEG"},
        map_values=True
    )

    #################################
    # Output subsystem, 26 Nov 2020 #
    #################################
    output1_state = Instrument.control(
        ":OUTP?", ":OUTP %d",
        """ A property that allow user to set the output state of the DATA1 terminal. 
            On: Enables output of the DATA1 terminal.
            Off: Disables output of the DATA1 terminal.""",
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    output2_state = Instrument.control(
        ":OUTP2?", ":OUTP2 %d",
        """ A property that allow user to set the output state of the DATA2 terminal. 
            On: Enables output of the DATA1 terminal.
            Off: Disables output of the DATA1 terminal.""",
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    output3_state = Instrument.control(
        ":OUTP3?", ":OUTP3 %d",
        """ A property that allow user to set the output state of the DATA3 terminal. 
            On: Enables output of the DATA1 terminal.
            Off: Disables output of the DATA1 terminal.""",
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    output4_state = Instrument.control(
        ":OUTP4?", ":OUTP4 %d",
        """ A property that allow user to set the output state of the DATA4 terminal. 
            On: Enables output of the DATA1 terminal.
            Off: Disables output of the DATA1 terminal.""",
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    ################################
    # Route subsystem, 26 Nov 2020 #
    ################################
    route_terminals = Instrument.control(
        ":ROUT?", ":ROUT %s",
        """ A property that control the input connector.
            A: Single end voltage (terminal A, 1 V max).
            AB: Differential voltage (terminal A-B, 1 V max).
            C: Large amplitude voltage (terminal C, 10 V max).
            I: Current(terminal I, 1 \u03BCAmax when conversion gain is 1 MV/A,
                                   10 nAmax when conversion gain is 100MV/A).
            HF: High frequency voltage (terminal HF, 1 V max). """,
        validator=strict_discrete_set,
        values=["A", "AB", "C", "I", "HF"],
        map_values=False
    )

    route2_terminals = Instrument.control(
        ":ROUT2?", "ROUT2 %s",
        """ A property that control the reference signal source.
            Ref In: Reference input connector.
            Internal: Internal oscillator.
            Signal In: Signal input connector. """,
        validator=strict_discrete_set,
        values={"Ref In": "RINP",
                "Internal": "IOSC",
                "Signal In": "SINP"},
        map_values=True
    )

    ######################################
    # Sensitivity subsystem, 26 Nov 2020 #
    ######################################
    current_ac_range_auto = Instrument.control(
        ":CURR:AC:RANG:AUTO?", ":CURR:AC:RANG:AUTO %d",
        """ A property that allow user to set the current sensitivity continuous automatic selection function.
            When current sensitivity is set automatically, dynamic reserve is also set automatically.
            On: Enables continuous automatic selection of current sensitivity.
            Off: Disable continuous automatic selection of current sensitivity.""",
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    current_ac_range = Instrument.control(
        ":CURR:AC:RANG?", ":ROUT I; :CURR:AC:RANG %g",
        """ A property that control the current sensitivity (primary PSD), range from 10E-15, 20E-15, ... 1E-6,
            rounding is applied to arbitrary values specified. Current sensitivity is the product of the current-voltage
            conversion gain and the voltage sensitivity.""",
        validator=truncated_range,
        values=[10e-15, 1e-6]
    )

    current2_ac_range = Instrument.control(
        ":CURR2:AC:RANG?", ":ROUT I; :CURR2:AC:RANG %g",
        """ A property that control the current sensitivity (secondary PSD), range from 10E-15, 20E-15, ... 1E-6,
            rounding is applied to arbitrary values specified. Current sensitivity is the product of the current-voltage
            conversion gain and the voltage sensitivity.""",
        validator=truncated_range,
        values=[10e-15, 1e-6]
    )

    data = Instrument.control(
        ":DATA?", ":DATA %d",
        """ A property that allow user to set measurement data sets. The data sets will be able to read by the :FETC? query.
            1: STATUS (16 bits), reads the measurement status.
            2: DATA1 (16 bits), reads the value of DATA1.
            4: DATA2 (16 bits), reads the value of DATA2.
            8: DATA3 (16 bits), reads the value of DATA3.
            16: DATA4 (16 bits), reads the value of DATA4.
            32: FREQ (32 bits), records the frequency value.
            Nothing is read if 0 is set.""",
        validator=truncated_range,
        values=[0, 63],
        map_values=False
    )

    detector = Instrument.control(
        ":DET?", ":DET %s",
        """ A property that allow user to set the detection mode.
            Single: 1 frequency x 2 phase (single mode). Only the primary PSD is used. Measure at fundamental wave F 
                    or harmonic (n/m) F of fundamental wave. 
            Dual1: 2 frequencies × 2 phases (2-frequency harmonic mode).
                   Primary PSD: Fundamental wave F or fundamental wave harmonic (n/m) F
                   Secondary PSD: Fundamental wave F or fundamental wave harmonic nF.
            DUAL2: 2 frequencies × 2 phases (2-frequency independent mode).
                   primary PSD: primary frequency Fp
                   Secondary PSD: secondary frequency Fs
            CASCade: 2-frequency cascade connection (2-frequency cascade mode)
                     primary PSD: primary frequency Fp
                     Secondary PSD: secondary frequency Fs
                     Further detection on the detection result Xp of Fp is performed using secondary frequency Fs.""",
        validator=strict_discrete_set,
        values={"Single": "SING",
                "Dual1": "DUAL1",
                "Dual2": "DUAL2",
                "Cascade": "CASC"},
        map_values=True
    )

    dynamic_reserve = Instrument.control(
        "DRES?", "DRES %s",
        """ A property that control the dynamic reserver sensitivity.
            High: High dynamic reserve when noise level is high.
            Medium: Medium dynamic reserve.
            Low: Low dynamic reserve when noise level is low. """,
        validator=strict_discrete_set,
        values={"High": "HIGH", 
                "Medium": "MED", 
                "Low": "LOW"},
        map_values=True
    )

    filter_slope = Instrument.control(
        ":FILT:SLOP?", ":FILT:SLOP %d",
        """ A property that control the filter attenuation slope (primary PSD).
            Range {6|12|18|24}, unit dB/oct}. """,
        validator=strict_discrete_set,
        values=[6, 12, 18,24],
        map_values=False
    )

    time_constant = Instrument.control(
        ":FILT:TCON?",":FILT:TCON %g",
        """ A property that control the filter time constant (primary PSD). 
            Range 1E-6 to 50E+3 1-2-5 sequence, unit s.
            Rounding is applied to arbitrary values specified. """,
        validator=truncated_range,
        values=[1e-6, 50e+3]
    )

    filter_type = Instrument.control(
        ":FILT:TYPE?",":FILT:TYPE %s",
        """ A property that control the filter type (primary PSD). 
            Exponential: Time constant filter
            Moving: Synchronous filter (moving average type)""",
        validator=strict_discrete_set,
        values={"Exponential": "EXP", "Moving": "MOV"},
        map_values=True
    )

    filter2_slope = Instrument.control(
        ":FILT2:SLOP?", ":FILT2:SLOP %d",
        """ A property that control the filter attenuation slope (secondary PSD).
            Range {6|12|18|24}, unit dB/oct}. """,
        validator=strict_discrete_set,
        values=[6, 12, 18,24],
        map_values=False
    )

    time_constant2 = Instrument.control(
        ":FILT2:TCON?",":FILT2:TCON %g",
        """ A property that control the filter time constant (secondary PSD). 
            Range 1E-6 to 50E+3 1-2-5 sequence, unit s.
            Rounding is applied to arbitrary values specified. """,
        validator=truncated_range,
        values=[1e-6, 50e+3]
    )

    filter2_type = Instrument.control(
        ":FILT2:TYPE?",":FILT2:TYPE %s",
        """ A property that control the filter type (secondary PSD). 
            Exponential: Time constant filter
            Moving: Synchronous filter (moving average type)""",
        validator=strict_discrete_set,
        values={"Exponential": "EXP", "Moving": "MOV"},
        map_values=True
    )

    primary_frequency = Instrument.measurement(
        ":FREQ?",
        """ Return the fundamental wave, primary frequency. 
            For instrument LI5660, this property will returen a numeric value,
            in the NR3 format, from range 3.0E-1 to 1.15E+7, resolution 7 digits, unit Hz"""
    )

    frequency_harmonic = Instrument.control(
        ":FREQ:HARM?", ":FREQ:HARM %d",
        """ A property that enable/disable the harmonics measurement. """,
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    frequency_harmonics_multiplier = Instrument.control(
        ":FREQ:MULT?", ":FREQ:HARM ON; :FREQ:MULT %d",
        """ A property that control the harmonic order n for measurement (Primary PSD) """,
        validator=truncated_range,
        values=[1, 63]
    )
    
    frequency_subharmonic_multiplier = Instrument.control(
        "FREQ:SMUL?", ":FREQ:HARM ON; :FREQ:MULT %d",
        """ A property that control the subharmonic order m for measurement (Primary PSD) """,
        validator=truncated_range,
        values=[1, 63]
    )

    secondary_frequency = Instrument.measurement(
        ":FREQ2?",
        """ Return the secondary frequency used with detection modes DUAL2 and CASCADE. """
    )

    frequency2_harmonics = Instrument.control(
        ":FREQ2:HARM?",":FREQ2:HARM %d",
        """ A property that control the harmonic measurement (enabled or disabled) (secondary PSD)""",
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    frequency2_harmonic_multiplier = Instrument.control(
        ":FREQ2:MULT?", ":FREQ2:HARM ON; :FREQ2:MULT %d",
        """ A property that control the harmonic order n for measurement (secondary PSD) """,
        validator=truncated_range,
        values=[1, 63]
    )

    smoothing = Instrument.control(
        ":NOIS?",":NOIS %d",
        """ A property that control the output smoothing coefficient for noise density measurement. """,
        validator=strict_discrete_set,
        values=[1, 4, 16, 64]
    )

    phase = Instrument.control(
        ":PHAS?", ":PHAS %g",
        """ A property that control the phase shift amount (primary PSD). """,
        validator=truncated_range,
        values=[-180.000, 179.000]
    )

    phase2 = Instrument.control(
        ":PHAS2?", ":PHAS %g",
        """ A property that control the phase shift amount (primary PSD). """,
        validator=truncated_range,
        values=[-180.000, 179.000]
    )

    reference_frequency_source = Instrument.control(
        ":ROSC:SOUR?",":ROSC:SOUR %s",
        """ A property that control the reference frequency source for frequency synthesis.
            Internal: Internal frequency source
            External: External frequency source (10 MHz IN terminal).

            Even when the reference frequency source is set to external, operation continues with
            the internal reference frequency source until a 10 MHz signal is applied to the 10 MHz IN terminal. """,
        validator=strict_discrete_set,
        values={"Internal": "INT", "External": "EXT"},
        map_values=True
    )

    voltage_ac_range_auto = Instrument.control(
        ":VOLT:AC:RANG:AUTO?", ":VOLT:AC:RANG:AUTO %d",
        """ A property that allow user to set the voltage sensitivity continuous automatic selection function.
            When voltage sensitivity is set automatically, dynamic reserve is also set automatically.
            On: Enables continuous automatic selection of voltage sensitivity.
            Off: Disable continuous automatic selection of voltage sensitivity.""",
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    voltage_ac_range = Instrument.control(
        ":VOLT:AC:RANG?", "::VOLT:AC:RANG %g",
        """ A property that control the current sensitivity (primary PSD), range from 10E-15, 20E-15, ... 1E-6,
            rounding is applied to arbitrary values specified. Current sensitivity is the product of the current-voltage
            conversion gain and the voltage sensitivity.""",
        validator=truncated_range,
        values=[10e-15, 1e-6]
    )

    ##########
    # Source #
    ##########
    source_frequency = Instrument.control(
        ":SOUR:FREQ?", "SOUR:FREQ %d",
        """ A property that control the internal oscillator (primary PSD) frequency. """,
        validator=truncated_range,
        values=[300e-3, 1.15e+7]
    )

    source_voltage = Instrument.control(
        ":SOUR:VOLT?", ":SOUR:VOLT %d",
        """ A property that control the internal oscillator output voltage AC amplitude. """,
        validator=truncated_range,
        values=[0, 1]
    )

    ############
    # Methods  #
    ############
    def abort(self):
        """ A property that allow user to abort recording to the measurement data buffer and puts the trigger system in the idle state. """
        log.info("Recording abort.")

        self.write(":ABOR")

    def data1_format(self, FORMAT="Real"):
        """ A property that allow user to set the measurement parameters to be displayed and output as DATA1. """
        log.info("The display format is set to {}".format(self.name))

        self.calculate1_format = FORMAT

    def data2_format(self, FORMAT="Imaginary"):
        """ A property that allow user to set the measurement parameters to be displayed and outpout as DATA2. """
        log.info("The display format is set to {}".format(self.name))

        self.calculate2_format = FORMAT

    def data3_format(self, FORMAT="Real"):
        """ A property that allow user to set the measurement parameters to be displayed and outpout as DATA3. """
        log.info("The display format is set to {}".format(self.name))

        self.calculate3_format = FORMAT

    def data4_format(self, FORMAT="Imaginary"):
        """ A property that allow user to set the measurement parameters to be displayed and outpout as DATA4. """
        log.info("The display format is set to {}".format(self.name))

        self.calculate4_format = FORMAT

    def current_reference(self, VALUE=1e-15):
        """ A property that allow user to set the current reference value for normalize calculation. """
        log.info("The current reference value for normalize calculation is set to {}".format(self.name))

        self.calculate1_math_current = VALUE

    def calculation_format(self, FORMAT="Reference"):
        """ A property that allow user to set the normalize calculation format. """
        log.info("The calculation format is set to {}".format(self.name))

        self.calculation1_math_expression_name = FORMAT

    def voltage_reference(self, VALUE=1e-9):
        """ A property that allow user to set the voltage reference value for normalize calculation. """
        log.info("The voltage reference value for normalize calculation is set to {}".format(self.name))

        self.calculate1_math_voltage = VALUE

    def primaryRX_multiplier(self, MULTIPLIER=1):
        """ A property that allow user to set the primary PSD's R, X output common expand multiplier.
            Display and output of expand results also requires enabling expand calculation with the
            :CALCulate5:MATH EXP command. """
        log.info("The primary PSD's R, X output common expand multiplier is set to {}".format(self.name))

        self.calculate1_multiplier = MULTIPLIER

    def primaryY_multiplier(self, MULTIPLIER=1):
        """ A property that allow user to set the primary PSD's R, X output common expand multiplier.
            Display and output of expand results also requires enabling expand calculation with the
            :CALCulate5:MATH EXP command. """
        log.info("The primary PSD's R, X output common expand multiplier is set to {}".format(self.name))

        self.calculate2_multiplier = MULTIPLIER

    def secondaryRX_multiplier(self, MULTIPLIER=1):
        """ A property that allow user to set the secondary PSD's R, X output common expand multiplier.
            Display and output of expand results also requires enabling expand calculation with the
            :CALCulate5:MATH EXP command. """
        log.info("The primary PSD's R, X output common expand multiplier is set to {}".format(self.name))

        self.calculate3_multiplier = MULTIPLIER

    def secondaryY_multiplier(self, MULTIPLIER=1):
        """ A property that allow user to set the primary PSD's R, X output common expand multiplier.
            Display and output of expand results also requires enabling expand calculation with the
            :CALCulate5:MATH EXP command. """
        log.info("The primary PSD's R, X output common expand multiplier is set to {}".format(self.name))

        self.calculate4_multiplier = MULTIPLIER

    def primaryX_offset(self, OFFSET=0):
        """ A property that allow user to offset for the primary PSD's X output. """

        self.calculate1_offset = OFFSET
        log.info("The offset with respect to secondary PSD's X output to {} of sensitivity full scale.".format(self.calculate1_offset))

    def primaryY_offset(self, OFFSET=0):
        """ A property that allow user to offset for the primary PSD's X output. """

        self.calculate2_offset = OFFSET
        log.info("The offset with respect to secondary PSD's X output to {} of sensitivity full scale.".format(self.calculate2_offset))

    def secondaryX_offset(self, OFFSET=0):
        """ A property that allow user to offset for the primary PSD's X output. """

        self.calculate3_offset = OFFSET
        log.info("The offset with respect to secondary PSD's X output to {} of sensitivity full scale.".format(self.calculate3_offset))

    def secondaryY_offset(self, OFFSET=0):
        """ A property that allow user to offset for the primary PSD's X output. """

        self.calculate4_offset = OFFSET
        log.info("The offset with respect to secondary PSD's X output to {} of sensitivity full scale.".format(self.calculate4_offset))

    def primaryXY_offset_auto(self):
        """ Automatically sets offsets so that primary PSD's X and Y output become zero at that point, and enables offset adjustment.
            The function is the same as that of the ":CALC2:OFFS:AUTO:ONCE". Both of these commands work on both X and Y. Automatic setting
            of just X and Y is not possible."""
        log.info("Auto offset the primary PSD's X and Y.")
        self.write(":CALC1:OFFS:AUTO:ONCE")

    def secondaryXY_offset_auto(self):
        """ Automatically sets offsets so that primary PSD's X and Y output become zero at that point, and enables offset adjustment.
            The function is the same as that of the ":CALC4:OFFS:AUTO:ONCE". Both of these commands work on both X and Y. Automatic setting
            of just X and Y is not possible."""
        log.info("Auto offset secondary PSD's X and Y.")
        self.write(":CALC3:OFFS:AUTO:ONCE")

    def primaryX_offset_state(self, STATUS="Off"):
        """ A property that allow user to enable/disable offset for the primary PSD's X output. """
        log.info("The offset adjustment is set to {}".format(self.name))

        self.calculate1_offset_state = STATUS

    def primaryY_offset_state(self, STATUS="Off"):
        """ A property that allow user to enable/disable offset for the primary PSD's X output. """
        log.info("The offset adjustment is set to {}".format(self.name))

        self.calculate2_offset_state = STATUS

    def secondaryX_offset_state(self, STATUS="Off"):
        """ A property that allow user to enable/disable offset for the primary PSD's X output. """
        log.info("The offset adjustment is set to {}".format(self.name))

        self.calculate3_offset_state = STATUS

    def secondaryY_offset_state(self, STATUS="Off"):
        """ A property that allow user to enable/disable offset for the primary PSD's X output. """
        log.info("The offset adjustment is set to {}".format(self.name))

        self.calculate4_offset_state = STATUS

    def set_calculation_method(self, METHOD="Off"):
        """ A property that allow user to set the calculation method for measurement value to be displayed and output. """
        log.info("The calculation method for measurement value is set to {}".format(self.name))

        self.calculation_method = METHOD

    def get_buffer(self, BUFFER="Buffer1", LENGTH=1, START=0):
        """ A aquire the floating point data through binary transfer. """
        buffer = {"Buffer1": "BUF1",
                  "Buffer2": "BUF2",
                  "Buffer3": "BUF3"}
        return self.values(":DATA:DATA? {}, {}, {}".format(buffer[BUFFER], LENGTH, START))

    def clere_buffer(self, BUFFER="Buffer1"):
        """ Clears the specified measurement data buffer. """
        buffer = {"Buffer1": "BUF1",
                  "Buffer2": "BUF2",
                  "Buffer3": "BUF3"}
        self.write(":DATA:DEL {}".format(buffer[BUFFER]))

    def clear_all_buffer(self):
        """ Clear all measurement data buffers. """
        self.write(":DATA:DEL:ALL")

    def data_feed(self, BUFFER="Buffer1", DATA=30):
        """ Set measurement data sets recorded in measurement data buffer 1, 2 or 3. """
        buffer = {"Buffer1": "BUF1",
                  "Buffer2": "BUF2",
                  "Buffer3": "BUF3"}
        self.write(":DATA:FEED {}, {}".format(buffer[BUFFER], DATA))

    def data_feed_control(self, BUFFER="Buffer1", STATUS="Always"):
        """ Set whether measurement data is to be recorded in a measurement data buffer. """
        buffer = {"Buffer1": "BUF1",
                  "Buffer2": "BUF2",
                  "Buffer3": "BUF3"}
        status = {"Always": "ALW",
                  "Never": "NEV"}
        self.write(":DATA:FEED:CONT {}, {}".format(buffer[BUFFER], status[STATUS]))

    def data_points(self, BUFFER="Buffer1", SIZE=16):
        """ Set measurement data buffer size. """
        buffer = {"Buffer1": "BUF1",
                  "Buffer2": "BUF2",
                  "Buffer3": "BUF3"}
        self.write(":DATA:POIN {}, {}".format(buffer[BUFFER], SIZE))

    def interval(self, TIME=10E-3):
        """ A property that allow user to set the internal timer time interval. """
        self.data_timer = TIME

    def timer_state(self, STATE="Off"):
        """ A property that allow user to enable or disable the internal timer. """
        self.data_timer_state = STATE  

    def default_display(self):
        """ Configures the measurement screen. """
        self.screen = "Fine"

    def display(self, DISPLAY=None):
        """ A property that allows user to switch between the 'Standard', 'Expanded', 'Detail' screens. """
        log.info("Screen is display in {}".format(self.name))
        
        if DISPLAY is None:
            self.default_display()
        else:
            self.screen = DISPLAY   

    def display_state(self, STATE="On"):
        """ A property that allow user to enable/disable the display screen. """
        log.info("Screen display change")

        self.display_window = STATE

    def data_format(self, FORMAT="ASCII"):
        """ A property that allow user to set the data transfer format. """
        self.format = FORMAT
        log.info("The data format is set to {}".format(self.format))

    def initiate(self):
        """ A property that allow user to set the awaiting trigger state. """
        self.write(":INIT")

    def coupling(self, INPUT="AC"):
        """ A property that allow user to set the signal input result method. """
        
        self.input_coupling = INPUT
        log.info("The input coupling is set to {}".format(self.input_coupling))

    def notch_frequency(self, FREQUENCY=50):
        """ A property that allow user to removes power supply frequency noise. """
        self.input_filter_notch_frequency = FREQUENCY
        log.info("Power supply frequency is set to {}".format(self.input_filter_notch_frequency))

    def primary_notch_state(self, STATE="On"):
        """ A property that allow user to enable/disable the notch1 filter.
            The notch1 filter removes power supply frequency (50 or 60 Hz) noise. """
        self.input_filter_notch1_state = STATE
        log.info("The power supply frequency is set")

    def secondary_notch_state(self, STATE="On"):
        """ A property that allow user to enable/disable the notch2 filter.
            The notch2 filter removes power supply secondary harmonic (100 or 120 Hz) noise. """
        self.input_filter_notch2_state = STATE
        log.info("The power supply secondary harmonic is set")

    def gain(self, GAIN=1):
        """ A property that allow user to set the current-voltage conversion gain for current input.
            1: IE6 Conversion gain 1 MV/A, 1uAmax
            100: IE8 Conversion gain 100 MV/A, 10nAmax """
        self.input_gain = GAIN
        log.info("The current-voltage conversion gain is set to {}".format(self.input_gain))

    def impedance(self, Z=50):
        """ A property that allow user to set HF terminal input impedance.
            Rounding is applied to arbitrary values specified. """
        self.input_impedance = Z
        log.info("The HF terminal input impedance is set to {}".format(self.input_impedance))

    def grounding(self, GROUND="Ground"):
        """ A property that allow user to set grounding of the signal input connectedor's outer conductor. """
        self.input_low = GROUND
        log.info("The grounding of the signal input connector's outer conductor is set to {}".format(self.input_low))

    def input_offset(self, OFFSET="Once"):
        """ A property that allow user to set the PSD input offset. 
            On: Enables continuius automatic adjustment of PSD input offset.
            Off: Disable continuous automatic adjustment of PSD input offset.
            Once: PSD input offset is autumatically adjusted just once.
            Resotre: Disables PSD input offset adjustment and restores the factory default setting. """
        if OFFSET=="Once":
            self.write(":INP:OFFS:AUTO:ONCE")
        elif OFFSET == "Restore":
            self.write(":INP:OFFS:RST")
        else:
            self.input_offset_auto = OFFSET
        log.info("The input PSD offset is set to {}".format(self.input_offset_auto))

    def response(self, TIME=200E-3):
        """ A property that allow user to set response time for the PSD input offset continuous auto adjustment function.
            Rounding is applied to arbitrary values specified. """
        self.input_offset_stime = TIME
        log.info("The response time is set to {}".format(self.input_offset_stime))

    def signal_type(self, TYPE="Sine"):
        """ A property that allow user to set the reference signal wavefrom.
            Sine: Sinusoid wave.
            TTL Rising: TTL level rising edge.
            TTL Falling: TTL level falling edge. """
        self.input_type = TYPE
        log.info("The input signal type is set to {}".format(self.input_type))

    def delete_memory(self, N=None):
        """ A property that allow user to clears the contents of the specified configuration memory. """
        if N is None:
            return "Please specified whick memory you want to clear."
        else:
            self.write(":MEM:STAT:DEL {}".format(N))
        log.info("{} memory has been cleared.")

    def name_memory(self, NAME:str, N:int):
        """ A property that allow uset to changes the name of the specified configuration memory. """
        if NAME is None or N is None:
            return "Please specified the name and memory number."
        else:
            self.write(":MEM:STAT:DEF '{}', {}".format(NAME, N))

    def data1_output(self, state="On"):
        """ A property that allow user to set the output state of the DATA1 terminal. 
            On: Enables output of the DATA1 terminal.
            Off: Disables output of the DATA1 terminal."""

        self.output1_state = state
        log.info("DATA1 output is set to {}".format(self.output1_state))

    def data2_output(self, state="On"):
        """ A property that allow user to set the output state of the DATA1 terminal. 
            On: Enables output of the DATA1 terminal.
            Off: Disables output of the DATA1 terminal."""

        self.output2_state = state
        log.info("DATA1 output is set to {}".format(self.output2_state))

    def data3_output(self, state="On"):
        """ A property that allow user to set the output state of the DATA1 terminal. 
            On: Enables output of the DATA1 terminal.
            Off: Disables output of the DATA1 terminal."""

        self.output3_state = state
        log.info("DATA1 output is set to {}".format(self.output3_state))

    def data4_output(self, state="On"):
        """ A property that allow user to set the output state of the DATA1 terminal. 
            On: Enables output of the DATA1 terminal.
            Off: Disables output of the DATA1 terminal."""

        self.output4_state = state
        log.info("DATA1 output is set to {}".format(self.output4_state))

    def input_terminal(self, terminal="A"):
        """ A property that control the input connector.
            A: Single end voltage (terminal A, 1 V max).
            AB: Differential voltage (terminal A-B, 1 V max).
            C: Large amplitude voltage (terminal C, 10 V max).
            I: Current(terminal I, 1 \u03BCAmax when conversion gain is 1 MV/A,
                                   10 nAmax when conversion gain is 100MV/A).
            HF: High frequency voltage (terminal HF, 1 V max). """

        self.route_terminals = terminal
        log.info("The input signal terminal is set to {}".format(self.route_terminals))

    def reference_signal(self, source="Internal"):
        """ A property that control the reference signal source.
            Ref In: Reference input connector.
            Internal: Internal oscillator.
            Signal In: Signal input connector. """

        self.route2_terminals = source
        log.info("The reference signal source is set to {}".format(self.name))

    def auto_measurement(self):
        """ A property that automatically set the sensitivity and time constant once to match the
            reference signal for the signal being measured at the time. This corresponds to the
            panel operation [AUTO]-->[MEASURE]. """

        self.write(":AUTO:ONCE")
        log.info("Auto measurement activated.")

    def auto_current_range(self, state="Off"):
        """ A property that allow user to set the current sensitivity continuous automatic selection function.
            When current sensitivity is set automatically, dynamic reserve is also set automatically.
            On: Enables continuous automatic selection of current sensitivity.
            Off: Disable continuous automatic selection of current sensitivity."""
        
        self.current_ac_range_auto = state
        log.info("The current sensitivity is set to {}".format(self.current_ac_range_auto))

    def auto_current_measurement(self):
        """ A property that allow user to automatically set current sensitivity one time.
            When current senitivity is set automatically, dynamic reserve is also set automatically. """
        
        self.write(":CURR:AC:RANG:AUTO:ONCE")
        log.info("Automatic current sensitivity set to one time.")

    def primary_current_sensitivity(self, range=10E-15):
        """ A property that control the current sensitivity (primary PSD), range from 10E-15, 20E-15, ... 1E-6,
            rounding is applied to arbitrary values specified. Current sensitivity is the product of the current-voltage
            conversion gain and the voltage sensitivity.
            The range of current sensitivity that can be selected is dependent on the current-voltage conversion gain
            that :ROUT command. """
        self.current_ac_range = range
        log.info("Primary current sensitivity is set to {}".format(self.currnet_ac_range))

    def secondary_current_sensitivity(self, range=10E-15):
        """ A property that control the current sensitivity (secondary PSD), range from 10E-15, 20E-15, ... 1E-6,
            rounding is applied to arbitrary values specified. Current sensitivity is the product of the current-voltage
            conversion gain and the voltage sensitivity.
            The range of current sensitivity that can be selected is dependent on the current-voltage conversion gain
            that :ROUT command. """
        self.current2_ac_range = range
        log.info("Secondary current sensitivity is set to {}".format(self.current2_ac_range))      

    def data_sets(self, sets=30):
        """ A property that allow user to set measurement data sets. The data sets will be able to read by the :FETC? query.
            1: STATUS (16 bits), reads the measurement status.
            2: DATA1 (16 bits), reads the value of DATA1.
            4: DATA2 (16 bits), reads the value of DATA2.
            8: DATA3 (16 bits), reads the value of DATA3.
            16: DATA4 (16 bits), reads the value of DATA4.
            32: FREQ (32 bits), records the frequency value.
            Nothing is read if 0 is set."""
        self.data = sets
        log.info("Sets the measurement data set to {}".format(self.data))
    
    def detection_mode(self, mode="Single"):
        """ A property that allow user to set the detection mode.
            Single: 1 frequency x 2 phase (single mode). Only the primary PSD is used. Measure at fundamental wave F 
                    or harmonic (n/m) F of fundamental wave. 
            Dual1: 2 frequencies × 2 phases (2-frequency harmonic mode).
                   Primary PSD: Fundamental wave F or fundamental wave harmonic (n/m) F
                   Secondary PSD: Fundamental wave F or fundamental wave harmonic nF.
            DUAL2: 2 frequencies × 2 phases (2-frequency independent mode).
                   primary PSD: primary frequency Fp
                   Secondary PSD: secondary frequency Fs
            CASCade: 2-frequency cascade connection (2-frequency cascade mode)
                     primary PSD: primary frequency Fp
                     Secondary PSD: secondary frequency Fs
                     Further detection on the detection result Xp of Fp is performed using secondary frequency Fs."""

        self.detector = mode
        log.info("The detection mode is set to {}".format(self.detector))

    def default_dynamic_reserve(self):
        """ Configure the dynamic reserve Sensitivity. """
        self.dynamic_reserve = "Medium"

    def dynamic_reserve_level(self, dr=None):
        """ A property that control the dynamic reserver sensitivity.
            High: High dynamic reserve when noise level is high.
            Medium: Medium dynamic reserve.
            Low: Low dynamic reserve when noise level is low. """
        
        if dr is None:
            self.default_dynamic_reserve()
        else:
            self.dynamic_reserve = dr

        log.info("The dynamic reserve is set to {}".format(self.dynamic_reserve))

    def filter_auto_once(self):
        """Automatically sets the filter time constant according to frequency.
            When the synchronous filter is selected, switching to the time constant filter
            takes place automatically. """
        log.info("Automatically sets the filter time constant.")
        self.write(":FILT:AUTO:ONCE")

    def primary_slope(self, db=6):
        """ A property allow user to set the filter attenuation slope (primary PSD). 
            Range {6|12|18|24}, unit dB/oct}. """

        self.filter_slope = db
        log.info("The filter attenuation slope is set to {}".format(self.filter1_type))

    def primary_time_constant(self, tc=1e-6):
        """ A property allow user to set the filter time constant (primary PSD). 
            Range 1E-6 to 50E+3 1-2-5 sequence, unit s.
            Rounding is applied to arbitrary values specified."""

        self.time_constant = tc
        log.info("The filter time constant is set to {}".format(self.time_constant))

    def primary_filter_type(self, filtertype="Exponential"):
        """ A property that control the filter type (primary PSD). 
            Exponential: Time constant filter
            Moving: Synchronous filter (moving average type)"""

        self.filter_type = filtertype
        log.info("The primary filter type is set to {}".format(self.filter_type))

    def secondary_slope(self, db=6):
        """ A property allow user to set the filter attenuation slope (primary PSD). 
            Range {6|12|18|24}, unit dB/oct}. """

        self.filter2_slope = db
        log.info("The filter attenuation slope is set to {}".format(self.filter2_slope))

    def secondary_time_constant(self, tc=1e-6):
        """ A property allow user to set the filter time constant (primary PSD). 
            Range 1E-6 to 50E+3 1-2-5 sequence, unit s.
            Rounding is applied to arbitrary values specified."""

        self.time_constant2 = tc
        log.info("The filter time constant is set to {}".format(self.time_constant2))

    def secondary_filter_type(self, filtertype="Exponential"):
        """ A property that control the filter type (primary PSD). 
            Exponential: Time constant filter
            Moving: Synchronous filter (moving average type)"""

        self.filter2_type = filtertype
        log.info("The primary filter type is set to {}".format(self.filter2_type))
    
    def primary_harmonic(self, state="On"):
        """ A property allow user to turn off the primary harmonic measurement.
            ON: Enables harmonics measurement.
            OFF: Disables harmonics measurement. """
        self.frequency_harmonic = state
        log.info("Primary harmonics measurement is set to {}".format(self.frequency_harmonic))

    def primary_harmonic_multipliter(self, order=1):
        """ A property allow user to set the harmonic order n for measurement (promary PSD).
            The signal that has n times frequency of the reference signal can be measured. """

        self.frequency_harmonics_multiplier = order
        log.info("The primary harmonic order is set to {}".format(self.frequency_harmonics_multiplier))

    def primary_subharmonic_multipliter(self, order=1):
        """ A property allow user to set the harmonic order n for measurement (promary PSD).
            The signal that has n times frequency of the reference signal can be measured. """

        self.frequency_subharmonic_multiplier = order
        log.info("The primary harmonic order is set to {}".format(self.frequency_subharmonic_multiplier))

    def secondary_harmonic(self, state="Off"):
        """ A property allow user to turn off the secondary harmonic measurement.
            ON: Enables harmonics measurement.
            OFF: Disables harmonics measurement. """
        self.frequency2_harmonic = state
        log.info("Secondary harmonic measurement is set to {}".format(self.frequency2_harmonic))

    def secondary_harmonic_multipliter(self, order=1):
        """ A property allow user to set the harmonic order n for measurement (secondary PSD).
            Secondary PSD harmonic measurement is forcibly disabled in detection modes other than DUAL1. """

        self.frequency2_harmonic_multiplier = order
        log.info("The primary harmonic order is set to {}".format(self.frequency2_harmonic_multiplier))

    def noise(self, coefficient=1):
        """ A property allow user to set the output smoothing coefficient for noise density measurement.
            Setting the coefficient to 4 roughly halves variations in output, but roughly quadruples response time."""

        self.smoothing = coefficient
        log.info("The smoothing coefficient is set to {}".format(self.smoothing))

    def primary_phase_shift(self, shift=0):
        """ A property that allow user to set the phase shift amount (primary PSD). 
            Numeric value, range from -180.000 to +179.999, resolution 0.001, unit °."""
        
        self.phase = shift        
        log.info("The primary frequency phase shift amount is set to {}".format(self.phase))

    def primary_phase_shift_auto(self):
        """Automatically adjusts the phase shift amount so that phase θ (primary PSD) becomes zero."""

        self.write(":PHAS:AUTO:ONCE")
        log.info("Automatically adjusts the phase shift amount.")

    def secondary_phase_shift(self, shift=0):
        """ A property that allow user to set the phase shift amount (primary PSD). 
            Numeric value, range from -180.000 to +179.999, resolution 0.001, unit °."""
        
        self.phase2 = shift        
        log.info("The primary frequency phase shift amount is set to {}".format(self.phase2))

    def secondary_phase_shift_auto(self):
        """Automatically adjusts the phase shift amount so that phase θ (primary PSD) becomes zero."""

        self.write(":PHAS2:AUTO:ONCE")
        log.info("Automatically adjusts the phase shift amount.")

    def reference_frequency(self, SOURCE="Internal"):
        """ A property that control the reference frequency source for frequency synthesis.
            Internal: Internal frequency source
            External: External frequency source (10 MHz IN terminal).

            Even when the reference frequency source is set to external, operation continues with
            the internal reference frequency source until a 10 MHz signal is applied to the 10 MHz IN terminal. """

        self.reference_frequency_source = SOURCE
        log.info("The reference frequency source is set to {}".format(self.reference_frequency_source))

    def auto_voltage_range(self, state="Off"):
        """ A property that allow user to set the voltage sensitivity continuous automatic selection function.
            When voltage sensitivity is set automatically, dynamic reserve is also set automatically.
            On: Enables continuous automatic selection of voltage sensitivity.
            Off: Disable continuous automatic selection of voltage sensitivity."""
        
        self.voltage_ac_range_auto = state
        log.info("The current sensitivity is set to {}".format(self.voltage_ac_range_auto))

    def auto_voltage_measurement(self):
        """ A property that allow user to automatically set current sensitivity one time.
            When current senitivity is set automatically, dynamic reserve is also set automatically. """
        
        self.write(":VOLT:AC:RANG:AUTO:ONCE")
        log.info("Automatic voltage sensitivity set to one time.")