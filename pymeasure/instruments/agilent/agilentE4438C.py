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

from pymeasure.instruments.signal_generator import SignalGenerator
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set, strict_range, joined_validators
import time
class AgilentE4438C(SignalGenerator):
    POWER_RANGE_MIN_dBm = -130.0
    POWER_RANGE_MAX_dBm = 30.0
    POWER_RANGE_dBm = [POWER_RANGE_MIN_dBm, POWER_RANGE_MAX_dBm]

    FREQUENCY_MIN_Hz = 250e3
    FREQUENCY_MAX_Hz = 6e9
    FREQUENCY_RANGE_Hz = [FREQUENCY_MIN_Hz, FREQUENCY_MAX_Hz]

    AMPLITUDE_SOURCES = {
        'internal':'INT',
        'external':'EXT', 'external 2':'EXT2'
    }
    PULSE_SOURCES = {
        'internal':'INT', 'external':'EXT', 'external 2':'EXT2'
    }

    pulse_input = Instrument.property_not_supported() # Not supported
    LOW_FREQUENCY_SOURCES = {
        'internal':'INT', 'function':'FUNC'
    }

    ####################################################################
    # Custom Subsystem-Option 001/601or 002/602 ([:SOURce]:RADio:CUSTom)
    ####################################################################
    CUSTOM_MODULATION_TYPES = ("BPSK", "QPSK", "IS95QPSK", "GRAYQPSK", "OQPSK", "IS95OQPSK", 
                               "P4DQPSK", "PSK8", "PSK16", "D8PSK", "MSK", "FSK2", "FSK4",
                               "FSK8", "FSK16", "C4FM", "QAM4", "QAM16", "QAM32", "QAM64",
                               "QAM128", "QAM256", "UIQ", "UFSK")

    CUSTOM_MODULATION_FILTERS = ("RNYQuist", "NYQuist", "GAUSsian", "RECTangle", "IS95",
                                 "IS95_EQ", "IS95_MOD", "IS95_MOD_EQ", "AC4Fm", "UGGaussian")

    CUSTOM_MODULATION_DATA = {
        'DATA' : "PRAM",
        'External' : "EXT",
        'Random' : "PN9",
        'Pattern' : "FIX4",
    }
    # TODO: map all natives data sources
    # ("PN9", "PN11", "PN15", "PN20", "PN23", "FIX4", "EXT", "P4", "P8", "P16", "P32", "P64", "PRAM")

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
        values=CUSTOM_MODULATION_TYPES
    )

    custom_modulation_filter = Instrument.control(
        ":RADio:CUSTom:FILTER?", ":RADio:CUSTom:FILTER %s", 
        """ A string property that allow to set and read the pre-modulation filter type
        This property can be set. """,
        validator=strict_discrete_set,
        values=CUSTOM_MODULATION_FILTERS
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
        ":RADio:CUSTom:ASK?", ":RADio:CUSTom:ASK %e", 
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
        """ A string property that allow to set and read the data pattern for unframed transmission
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

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Agilent E4438C Signal Generator",
            **kwargs
        )
        self.data_ramping_workaround = True

    def data_load(self, bitsequences, spacings):
        """ Load data into signal generator for transmission, the parameters are:
        bitsequences: list of items. Each item is a string of '1' or '0' in transmission order
        spacing: integer, gap to be inserted between each bitsequence  expressed in number of bit
        """
        data = []
        for bitseq, spacing in zip(bitsequences, spacings):
            for bit in bitseq:
                data.append(0x14+int(bit,2))
            # Add bits with RF off
            data += [0x10]*spacing
        self.write_binary_values("MEM:DATA:PRAM:FILE:BLOCK \"PacketsToTransmit\",", data)
        self.complete
        self.write("RADIO:CUSTOM:DATA:PRAM \"PacketsToTransmit\"")
        self.data_ramping_workaround = True
        self.write_binary_values("MEM:DATA:PRAM:FILE:BLOCK \"RampingWorkaround\",", [0x94])

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


