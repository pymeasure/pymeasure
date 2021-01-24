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

from pymeasure.instruments.rf_signal_generator import RFSignalGeneratorDM
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set, strict_range
import struct

class RS_SMIQ06B(RFSignalGeneratorDM):
    # Define instrument limits according to datasheet
    power_values = (-144.0, 16.0)
    frequency_values = (300e3, 6.4e9)

    ####################################################################
    # 3.5.14.5 SOURce:DM (Digital Modulation) Subsystem ([:SOURce]:DM)
    ####################################################################
    CUSTOM_MODULATION_DATA = {
        'Pattern0011' : None, # Not supported
        'Pattern0101' : "PATT;PATT ALT",
        'PatternPN9' :  "PRBS;PRBS 9",
        'DATA' : "DLIST",
    }

    CUSTOM_MODULATION_ENABLE_MAP = {
        1: "ON",
        0: "OFF"
    }

    custom_modulation_enable = Instrument.control(
        ":DM:STATE?", ":DM:STATE %s", 
        """ A boolean property that enables or disables the Custom modulation. 
        This property can be set. """,
        validator=strict_discrete_set,
        values=CUSTOM_MODULATION_ENABLE_MAP,
        map_values=True
    )

    custom_modulation = Instrument.setting(
        ":DM:FORMat %s", 
        """ A string property that allow to selects the modulation. QWCDma is only available with option SMIQB47.
        """,
        validator=strict_discrete_set,
        values=RFSignalGeneratorDM.MODULATION_TYPES
    )

    custom_modulation_filter = Instrument.setting(
        ":DM:FILTer:TYPE %s", 
        """ A string property that allow to set the type of filter.
        """,
        validator=strict_discrete_set,
        values=RFSignalGeneratorDM.MODULATION_FILTERS
    )

    custom_modulation_bbt = Instrument.setting(
        ":DM:FILTer:PARameter %f", 
        """ A  property that allow to set filter parameter (Roff Off or BxT rate).
        """,
        validator=strict_range,
        values=[0.1,1.0]
    )

    custom_modulation_symbol_rate = Instrument.setting(
        ":DM:SRATe %e", 
        """ A integer property that allow to set the transmission symbol rate
        This property can be set. """,
        validator=strict_range,
        values=[1000, 7e6]        
    )

    custom_modulation_ask_depth = Instrument.setting(
        ":DM:ASK:DEPTh %e", 
        """ An integer property that allow to set the depth for the amplitude shift keying (ASK) modulation.
        Depth is set as a percentage of the full power on level.
        """,
        validator=strict_range,
        values=[0, 100]
    )

    custom_modulation_fsk_deviation = Instrument.setting(
        ":DM:FSK:DEViation %e", 
        """ An integer property that allow to set the FSK frequency deviation value.
        Unit is Hz.
        """,
        validator=strict_range,
        values=[100, 2.5e6]
    )

    custom_modulation_data = Instrument.setting(
        ":DM:SOURce %s", 
        """ A string property that allow to set the data source.
        """,
        validator=strict_discrete_set,
        values=CUSTOM_MODULATION_DATA,
        map_values=True
    )

    memory = Instrument.measurement(
        ":DM:DLISt:FREE?",
        """ This property returns a list of data list names separated by commas.""",
        get_process=lambda v: int(v[0]),
    )

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Rohde & Schwarz SMIQ06B Signal Generator",
            **kwargs
        )

    def data_load(self, bitsequences, spacings):
        """ Load data into signal generator for transmission, the parameters are:
        bitsequences: list of items. Each item is a string of '1' or '0' in transmission order
        spacings: integer list, gap to be inserted between each bitsequence  expressed in number of bit
        """

        # Switch line terminator to EOI to send data in packed format
        self.write(":SYST:COMM:GPIB:LTER EOI")
        # Select data list
        self.write("SOURce:DM:DLISt:DELete 'data2tx'")
        self.write("SOURce:DM:DLISt:SELect 'data2tx'")

        # Write data list and store positions when switch between sequence and spacing occurs
        # for bitseq, spacing in zip(bitsequences, spacings):
        bitpos = 0
        ctrls = []
        val = ''
        for bitseq, spacing in zip(bitsequences, spacings):
            ctrls.append(bitpos)
            val += bitseq + "0"*spacing
            bitpos += len(bitseq)
            ctrls.append(bitpos)
            bitpos += spacing
        length = len(val)

        # Pad to have size multiple of 8
        if (length % 8):
            val = val + "0"*(8-(length % 8))
            length = len(val)
            
        values = []
        for i in range(0, length, 8):
            values.append(int(val[i:i+8], 2))
        
        self.adapter.write_binary_values("SOURce:DM:DLISt:DATA ", values, datatype='B')
        self.complete

        # Write control list
        # The control list is used to switch on the RF during sequence transmission and switch it off
        # during spacing
        self.write("SOURce:DM:CLISt:DELete 'datactrl'")
        self.write("SOURce:DM:CLISt:SELect 'datactrl'")
        self.complete

        values = []
        index_mask = (1 << 26) - 1 # 26 bits
        for i,v in enumerate(ctrls):
            # Swtich on the power at the beginning of eache sequence and switch it off at tend of the sequences
            values.append( (((i+1)%2) << 31) + (v & index_mask))
        self.adapter.write_binary_values("SOURce:DM:CLISt:DATA ", values, datatype="I")
        self.complete

        # Switch back to normal mode
        self.write(":SYST:COMM:GPIB:LTER STANDARD")

        self.write(":DM:CLISt:CONTrol ON")
        self.write(":DM:PRAMp:SOURce CLISt")
        self.write(":DM:PRAMp:STATe ON")
        self.complete

    def enable_modulation(self):
        # Do nothing since  each modulation type should be enable with relevant command
        pass

    def disable_modulation(self):
        """ Disables the signal modulation. """
        self.amplitude_modulation_enable = "OFF"
        self.pulse_modulation_enable = "OFF"
        self.custom_modulation_enable = 0
        self.write("SOUR:PDC:STAT OFF")

    def data_trigger_setup(self, mode='SINGLE'):
        """ Configure the trigger system for bitsequence transmission
        """
        self.write(":SOUR:DM:TRIGger:SOURce INT")
        self.write(":SOUR:DM:SEQ %s"%mode)

    def data_trigger(self):
        """ Trigger a bitsequence transmission
        """
        self.write(":TRIG:DM:IMM")
