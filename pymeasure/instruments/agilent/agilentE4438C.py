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
from pymeasure.instruments.validators import truncated_range, strict_discrete_set, strict_range, joined_validators
import time
class AgilentE4438C(RFSignalGeneratorDM):
    """ Class representing Agilent E4438C RF signal generator """

    # Define instrument limits according to datasheet
    power_values = (-136.0, 10.0)
    frequency_values = (100e3, 6e9)

    # Allow mapping of values for ALC command
    alc_values = {"ON" : 1,
                  "OFF" : 0}
    alc_map_values = True
    
    ####################################################################
    # Custom Subsystem-Option 001/601or 002/602 ([:SOURce]:RADio:CUSTom)
    ####################################################################
    CUSTOM_MODULATION_DATA = {
        'DATA' :        "PRAM",
        'PatternPN9' :  "PN9",
        'Pattern0011' : "FIX4;DATA:FIX4 #B0011",
        'Pattern01' :   "FIX4;DATA:FIX4 #B0101",
        'Pattern' :     "FIX4",
    }
    custom_modulation_enable = Instrument.control(
        ":RADIO:CUSTOM?", ":RADIO:CUSTOM %d", 
        """ A boolean property that enables or disables the Custom modulation. 
        This property can be set. """,
        cast=int
    )

    custom_modulation = Instrument.control(
        ":RADio:CUSTom:MODulation?", ":RADio:CUSTom:MODulation %s", 
        """ A string property that allow to set and read the modulation type for the Custom personality
        This property can be set. """,
        validator=strict_discrete_set,
        values=RFSignalGeneratorDM.MODULATION_TYPES
    )

    custom_modulation_filter = Instrument.control(
        ":RADio:CUSTom:FILTER?", ":RADio:CUSTom:FILTER %s", 
        """ A string property that allow to set and read the pre-modulation filter type
        This property can be set. """,
        validator=strict_discrete_set,
        values=RFSignalGeneratorDM.MODULATION_FILTERS
    )

    custom_modulation_bbt = Instrument.control(
        ":RADio:CUSTom:BBT?", ":RADio:CUSTom:BBT %f", 
        """ A  property that allow to set and read the bandwidth-multiplied-by-bit-time (BbT) filter parameter
        This property can be set. """,
        validator=strict_range,
        values=[0.1,1.0]
    )

    custom_modulation_symbol_rate = Instrument.control(
        ":RADio:CUSTom:SRATe?", ":RADio:CUSTom:SRATe %e", 
        """ A integer property that allow to set and read the transmission symbol rate
        This property can be set. """,
    )

    custom_modulation_ask_depth = Instrument.control(
        ":RADio:CUSTom:MODULATION:ASK:DEPTH?", ":RADio:CUSTom:MODULATION:ASK:DEPTH %e",
        """ An integer property that allow to set and read the depth for the amplitude shift keying (ASK) modulation.
        Depth is set as a percentage of the full power on level.
        This property can be set. """,
        validator=strict_range,
        values=[0, 100]
    )

    custom_modulation_fsk_deviation = Instrument.control(
        ":RADio:CUSTom:MODulation:FSK?", ":RADio:CUSTom:MODulation:FSK %e", 
        """ An integer property that allow to set and read the FSK frequency deviation value.
        Unit is Hz.
        This property can be set. """,
    )
    custom_modulation_data = Instrument.control(
        ":RADio:CUSTom:DATA?", ":RADio:CUSTom:DATA %s", 
        """ A string property that allow to set and read the data pattern source for unframed transmission
        This property can be set. """,
        validator=strict_discrete_set,
        values=CUSTOM_MODULATION_DATA,
        map_values=True
    )

    ####################################################################
    # Memory Subsystem (:MMEMory)
    ####################################################################

    memory = Instrument.measurement(
        ':MMEMory:CATalog? "WFM1"',
        """ This property returns free volatile memory value in bytes """,
        get_process=lambda v: int(v[1]),
    )
    name = "Agilent E4438C Signal Generator"
    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            self.name,
            **kwargs
        )
        self.data_ramping_workaround = True

    def data_load(self, bitsequences, spacings):
        """ Load data into signal generator for transmission, the parameters are:
        :param bitsequences: list of items. Each item is a string of '1' or '0' in transmission order
        :param spacing: list of integer, gap to be inserted between each bitsequence  expressed in number of bit
        """
        data = []
        for bitseq, spacing in zip(bitsequences, spacings):
            for bit in bitseq:
                data.append(0x14+int(bit,2))
            # Add bits with RF off
            data += [0x10]*spacing
        self.adapter.write_binary_values("MEM:DATA:PRAM:FILE:BLOCK \"PacketsToTransmit\",", data, datatype='B')
        self.complete
        self.write("RADIO:CUSTOM:DATA:PRAM \"PacketsToTransmit\"")
        self.data_ramping_workaround = True
        self.adapter.write_binary_values("MEM:DATA:PRAM:FILE:BLOCK \"RampingWorkaround\",", [0x94], datatype='B')

    def data_trigger_setup(self, mode='SINGLE'):
        """ Configure the trigger system for bitsequence transmission
        """
        # Subclasses should implement this
        self.write("RADio:CUSTom:TRIG:SOURCE BUS")
        self.write("RADio:CUSTom:TRIG:TYPE %s"%mode)

    def data_trigger(self):
        """ Trigger a bitsequence transmission
        """
        if (self.data_ramping_workaround):
            self.data_ramping_workaround = False
            self.write("RADIO:CUSTOM:DATA:PRAM \"RampingWorkaround\"")
            self.complete
            self.write("*TRG")
            time.sleep(0.1)
            self.write("RADIO:CUSTOM:DATA:PRAM \"PacketsToTransmit\"")
            self.complete

        self.write("*TRG")

    def enable_modulation(self):
        """ This command enables or disables the modulation of the RF output with the
        currently active modulation type(s). """
        self.write(":OUTPUT:MOD 1")

    def disable_modulation(self):
        """ Disables the signal modulation. """
        self.write(":OUTPUT:MOD 0")

    def set_fsk_constellation(self, constellation, fsk_dev):
        """ For multi level FSK modulation, we need to define the constellation mapping.

        For E4438C we are using the user defined UFSK modulation
        """
        self.bit_per_symbol = len(format(max(constellation.keys()), "b"))
        if (self.bit_per_symbol > 8):
            raise Exception("Multi level FSK is dupported up to 256 levels, i.e 8bit per symbol")

        cmd_params = "{}".format(1<<self.bit_per_symbol)
        for val in sorted(constellation.keys()):
            cmd_params += ",{:.3f}".format(fsk_dev/constellation[val])
        self.write(":MEM:DATA:FSK \"USER_FSK\",{},OFF".format(cmd_params))
        self.write(':RADio:CUSTom:MODulation:UFSK "USER_FSK"')
        self.write(':RADio:CUSTom:MODulation UFSK')
