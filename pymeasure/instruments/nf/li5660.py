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

    # Current Screen display mod
    display_screen = Instrument.control(
        ":DISP?", ":DISP %s", 
        """There are 3 types of measurement screen display: Normal, Large and Fine Measurement screens""",
        validator = strict_discrete_set,
        values={"Normail": "NORM", "Large": "LARG", "Fine": "FINE"},
        map_values=True
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

    ####################
    # Calculate / Data #
    ####################
    display_format = Instrument.control(
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

    reference_current = Instrument.control(
        ":CALC1:MATH:CURR?",":CALC1:MATH:CURR %g",
        """ A property that allow user to set the current reference value for normalize calculation. """,
        validator=truncated_range,
        values=[1e-15, 1e-6]
    )

    calculation_format = Instrument.control(
        ":CALC1:MATH:EXPR:NAME?", ":CALC1:MATH:EXPR:NAME %s", 
        """ A property that allow user to normalize calculation format. """,
        validator=strict_discrete_set,
        values={"DB": "DB, 'dB'",
                "Reference": "PCNT, ''",
                "Sensitivity": "PCFS, ''",
                },
        map_values=True
    )

    reference_voltage = Instrument.control(
        ":CALC1:MATH:VOLT?", ":CALC1:MATH:VOLT %g",
        """ A property that allow user to set the voltage reference value for normalize calculation. """,
        validator=truncated_range,
        values=[1e-9, 1e+1]
    )

    offset_enable = Instrument.control(
        ":CALC1:OFFS:STAT?", ":CALC1:OFFS:STAT %s",
        """ A property that allow user to enable/disable offset for the primary PSD's X output. """,
        validator=strict_discrete_set,
        values={"On": 1, "Off": 0},
        map_values=True
    )

    primary_offset = Instrument.control(
        "CALC1:OFFS?",":CALC1:OFFS:STAT ON; :CALC1:OFFS %g",
        """ A property that allow user to offset for the primary PSD's X output. """,
        validator=truncated_range,
        values=[-105, 105]
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

    fetch_data = Instrument.measurement(
        ":FETC?",
        """ Queries the most recent measurement data. """
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
    def default_display_screen(self):
        """ Configures the measurement screen. """
        self.display_screen = "Fine"

    def default_dynamic_reserve(self):
        """ Configure the dynamic reserve Sensitivity. """
        self.dynamic_reserve = "Medium"

    def scrn(self, DISPLAY=None):
        """ A property allows user to switch between the 'Standard', 'Expanded', 'Detail' screens. """
        log.info("Screen is display in {}".format(self.name))
        
        if DISPLAY is None:
            self.default_display_screen()
        else:
            self.display_screen = DISPLAY

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

    def set_display_format(self, FORMAT="Real"):
        """ A property that allow user to set the measurement parameters to be displayed and output as DATA1. """
        log.info("The display format is set to {}".format(self.name))

        self.display_format = FORMAT

    def current_reference(self, VALUE=1e-15):
        """ A property that allow user to set the current reference value for normalize calculation. """
        log.info("The current reference value for normalize calculation is set to {}".format(self.name))

        self.reference_current = VALUE

    def set_calculation_format(self, FORMAT="Reference"):
        """ A property that allow user to set the normalize calculation format. """
        log.info("The calculation format is set to {}".format(self.name))

        self.calculation_format = FORMAT

    def voltage_reference(self, VALUE=1e-9):
        """ A property that allow user to set the voltage reference value for normalize calculation. """
        log.info("The voltage reference value for normalize calculation is set to {}".format(self.name))

        self.reference_voltage = VALUE

    def enable_offset(self, STATUS="Off"):
        """ A property that allow user to enable/disable offset for the promary PSD's X output. """
        log.info("The offset adjustment is set to {}".format(self.name))

        self.offset_enable = STATUS

    def set_primary_offset(self, VALUE=0):
        """ A property that allow user to offset for the primary PSD's X output. """
        log.info("The offset for the primary PSD's X output is set to {}".format(self.name))

        self.primary_offset = VALUE

    def set_calculation_method(self, METHOD="Off"):
        """ A property that allow user to set the calculation method for measurement value to be displayed and output. """
        log.info("The calculation method for measurement value is set to {}".format(self.name))

        self.calculation_method = METHOD