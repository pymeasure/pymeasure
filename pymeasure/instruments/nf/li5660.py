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

    ###################
    # Reference Sigal #
    ###################
    signal_termainal = Instrument.control(
        ":ROUT?", ":ROUT %s",
        """ A property that control the input connector """,
        validator=strict_discrete_set,
        values={"A": "A",
                "AB": "AB",
                "C": "C",
                "Current": "I",
                "HF": "HF"},
        map_values=True

    )

    reference_signal_source = Instrument.control(
        ":ROUT2?", "ROUT2 %s",
        """ A property that control the reference signal source """,
        validator=strict_discrete_set,
        values={"Ref In": "RINP",
                "Internal": "IOSC",
                "Signal": "SINP"},
        map_values=True
    )

    reference_frequency_source = Instrument.control(
        ":ROSC:SOUR?",":ROSC:SOUR %s",
        """ A property that control the reference frequency source for frequency synthesis.""",
        validator=strict_discrete_set,
        values={"Internal": "INT", "External": "EXT"},
        map_values=True
    )

    ###############
    # Sensitivity #
    ###############
    auto = Instrument.measurement(
        ":AUTO:ONCE",
        """ a property that automatically set the sensitivity and time constant once to match the
        reference signal for the signal being measured at the time. Performs auto setting one time """
    )

    auto_current = Instrument.control(
        "CURR:AC:RANG:AUTO?", "CURR:AC:RANG %d",
        """ A property that continuous automatic selection current sensitivity function.
        On(enabled), Off(disabled) and Once(auto sets current sensitivity one time).""",
        values={"On": 1 , "Off": 0, "ONCE": "ONCE"},
        map_values=True
    )

    currnet_range = Instrument.control(
        ":CURR:AC:RANG?", ":CUR:AC:RANG:AUTO 0; :CURR:AC:RANG %g",
        """ A property that control the current sensitivity (primary PSD) """,
        validator=truncated_range,
        values=[10e-15, 1e-6]
    )

    dynamic_reserve = Instrument.control(
        "DRES?", "DRES %s",
        """ A property that control the dynamic reserver sensitivity.
            High dynamic reserve when noise level is high
            Low dynamic reserve when noise level is low
        """,
        validator=strict_discrete_set,
        values={"High": "HIGH", "Medium": "MED", "Low": "LOW"},
        map_values=True
    )

    filter_slope = Instrument.control(
        ":FILT:SLOP?", ":FILT:SLOP %d",
        """ A property that control the filter attenuation slope (primary PSD). """,
        validator=strict_discrete_set,
        values=[6, 12, 18,24],
        map_values=False
    )

    time_constant = Instrument.control(
        ":FILT:TCON?",":FILT:TCON %g",
        """ A property that control the filter time constant (primary PSD). """,
        validator=truncated_range,
        values=[1e-6, 50e+3]
    )

    filter_type = Instrument.control(
        ":FILT:TYPE?",":FILT:TYPE %s",
        """ A property that control the filter type (primary PSD). """,
        validator=strict_discrete_set,
        values={"Time Constant": "EXP", "Synchronous": "MOV"},
        map_values=True
    )

    smoothing = Instrument.control(
        ":NOIS?",":NOIS %d",
        """ A property that control the output smoothing coefficient for noise density measurement. """,
        validator=strict_discrete_set,
        values=[1, 4, 16, 64]
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

    #############
    # Frequency #
    #############
    frequency = Instrument.measurement(
        ":FREQ?",
        """ Return the fundamental wave, primary frequency. """
    )

    harmonics_pre_enable = Instrument.control(
        ":FREQ:HARM?", ":FREQ:HARM %d",
        """ A property that enable/disable the harmonics measurement. """,
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    harmonics_pre_order = Instrument.control(
        ":FREQ:MULT?", ":FREQ:HARM ON; :FREQ:MULT %d",
        """ A property that control the harmonic order n for measurement (Primary PSD) """,
        validator=truncated_range,
        values=[1, 63]
    )
    
    subharmonic_order = Instrument.control(
        "FREQ:SMUL?", ":FREQ:HARM ON; :FREQ:MULT %d",
        """ A property that control the subharmonic order m for measurement (Primary PSD) """,
        validator=truncated_range,
        values=[1, 63]
    )

    secondary_frequency = Instrument.measurement(
        ":FREQ2?",
        """ Return the secondary frequency used with detection modes DUAL2 and CASCADE. """
    )

    harmonics_sec_enable = Instrument.control(
        ":FREQ2:HARM?",":FREQ2:HARM %d",
        """ A property that control the harmonic measurement (enabled or disabled) (secondary PSD)""",
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    harmonics_sec_order = Instrument.control(
        ":FREQ2:MULT?", ":FREQ2:HARM ON; :FREQ:MULT %d",
        """ A property that control the harmonic order n for measurement (secondary PSD) """,
        validator=truncated_range,
        values=[1, 63]
    )

    phase_shift = Instrument.control(
        ":PHAS?", ":PHAS %g",
        """ A property that control the phase shift amount (primary PSD). """,
        validator=truncated_range,
        values=[-180.000, 179.000]
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

    def default_dynamic_reserve(self):
        """ Configure the dynamic reserve Sensitivity. """
        self.dynamic_reserve = "Medium"

    def dr(self, DR=None):
        """ A property allow user to set the sensitivity of the dynamic reserve. """
        log.info("The dynamic reserve is set to {}".format(self.name))
        
        if DR is None:
            self.default_dynamic_reserve()
        else:
            self.dynamic_reserve = DR

    def slope(self, SLOPE=6):
        """ A property allow user to set the filter attenuation slope (primary PSD). """
        log.info("The filter attenuation slope is set to {}".format(self.name))

        if SLOPE==6:
            self.filter_slope = SLOPE
        elif SLOPE==12:
            self.filter_slope = SLOPE
        elif SLOPE==18:
            self.filter_slope = SLOPE
        elif SLOPE==24:
            self.filter_slope = SLOPE
        else:
            return "The value is not in the range, please keyin the vaild value."
        return "The filter attenuation slope is set to {} dB/oct".format(SLOPE)

    def tc(self, TC=1e-6):
        """ A property allow user to set the filter time constant (primary PSD). """
        log.info("The filter time constant is set to {}".format(self.name))

        self.time_constant = TC

    def set_filter_type(self, TYPE="Time Constant"):
        """ A property allow user to set the filter type. """
        log.info("The filter type is set to {}".format(self.name))

        self.filter_type = TYPE

    def primary_harmonic_order(self, ORDER=1):
        """ A property allow user to set the harmonic order n for measurement (promary PSD). """
        log.info("The primary harmonic order is set to {}".format(self.name))

        self.harmonics_pre_order = ORDER
    
    def primary_harmonic(self, STATUS="On"):
        """ A property allow user to turn off the primary harmonic measurement. """
        self.harmonics_pre_enable = STATUS

    def smoothing_coefficient(self, COEFFICIENT=1):
        """ A property allow user to set the output smoothing coefficient for noise density measurement.
            Setting the coefficient to 4 roughly halves variations in output, but roughly quadruples response time."""
        log.info("The smoothing coefficient is set to {}".format(self.name))

        self.smoothing = COEFFICIENT

    def set_phase_shift(self, SHIFT=0):
        """ A property that allow user to set the phase shift amount (primary PSD). """
        log.info("The primary frequency phase shift amount is set to {}".format(self.name))

        self.phase_shift = SHIFT
        
    def reference_source(self, SOURCE="Internal"):
        """ A property that allow user to set the reference frequency source for frequency synthesis. """
        log.info("The reference frequency source is set to {}".format(self.name))

        self.reference_frequency_source = SOURCE

    def reference_signal(self, SIGNAL="Internal"):
        """ A property that allow user to set the reference signal source. """
        log.info("The reference signal source is set to {}".format(self.name))

        self.reference_signal_source = SIGNAL

    def termainal(self, INPUT="A"):
        """ A property that allow user to set the signal input terminal. """
        log.info("The signal input terminal is set to {}".format(self.name))

        self.signal_termainal = INPUT
####################################################################################################################################################
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
            IE6 Conversion gain 1 MV/A, 1uAmax
            IE8 Conversion gain 100 MV/A, 10nAmax """
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