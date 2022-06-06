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
from .rs_waveform import RSGenerator, WaveformTag, TypeTag, CLW4Tag, IntegerTag
from io import BytesIO
import re

class RS_SGT100A(RFSignalGeneratorDM):
    # Define instrument limits according to datasheet
    power_values = (-120.0, 17.0)
    frequency_values = (1e6, 6e9)

    # ALC syntax adaptation
    alc_values = ("ON", "OFF", "AUTO")
    alc_map_values = False

    _iq_data_bits = 16
    _waveform_path = '/var/user/waveform'

    ####################################################################
    # 11.14.2 SOURce:AWGN Subsystem
    ####################################################################
    awgn_mode = Instrument.control(
        ":AWGN:MODE?", ":AWGN:MODE %s", 
        """ A string property that define the mode for generating the interfering signal.
        This property can be set. """,
        validator=strict_discrete_set,
        values=("ONLY", "ADD"),
    )
    awgn_bandwidth = Instrument.control(
        ":AWGN:BWIDth?", ":AWGN:BWIDth %g", 
        """ A float property to set the awgn bandwidth in Hz.
        This property can be set. """,
        validator=strict_range,
        values=(1000, 5e6),
    )

    awgn_cn = Instrument.control(
        ":AWGN:CNRatio?", ":AWGN:CNRatio %g", 
        """ A float property to set or query C/N in the selected bandwidth
        Unit is dB. """,
        validator=truncated_range,
        values=(-50, 40),
    )

    awgn_enable = Instrument.control(
        ":AWGN:STATe?", ":AWGN:STATe %g", 
        """ A bootlean property to enable/disable AWGN. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    ####################################################################
    # 11.14.4 SOURce:BB:ARB Subsystem
    ####################################################################

    CUSTOM_MODULATION_ENABLE_MAP = {
        True: 1,
        False: 0
    }

    custom_modulation_enable = Instrument.control(
        "SOURce1:BB:ARBitrary:STATe?", "SOURce1:BB:ARBitrary:STATe %d", 
        """ A boolean property that activates the standard and deactivates
        all the other digital standards and digital modulation modes in the same path.
        You have to selecta an waveform first.
        This property can be set. """,
        validator=strict_discrete_set,
        values=CUSTOM_MODULATION_ENABLE_MAP,
        map_values=True
    )

    ####################################################################
    # 11.9 MMEMory Subsystem
    ####################################################################
    memory = Instrument.measurement(
        ":MEMory:HFRee?",
        """ This property returns the total physical memory in Kb. """,
        get_process=lambda v: int(v[0]),
    )

    file_list = Instrument.measurement(
        ":MMEMory:CATalog?",
        """ This property returns the list of filenames in the current directory """,
        get_process=lambda v: RS_SGT100A. _get_file_list(v)
    )

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Rohde & Schwarz SGT100A Signal Generator",
            **kwargs
        )

    @staticmethod
    def _get_file_list(command_output):
        """ Extract file names from output of command :MMEMory:CATalog? """
        # Search all the strings between double quotes
        command_output = ",".join([str(v) for v in command_output])
        pattern = r'"([^\"]*)"'
        m = re.findall(pattern, command_output)
        return [v.split(",")[0] for v in m]

    def data_load(self, bitsequences, spacings):
        """ Load data into signal generator for transmission, the parameters are:
        bitsequences: list of items. Each item is a string of '1' or '0' in transmission order
        spacings: integer list, gap to be inserted between each bitsequence  expressed in number of bit
        """
        
        raise NotImplementedError("Method not implemented")

    def enable_modulation(self):
        # Do nothing since  each modulation type should be enabled with relevant command
        pass

    def disable_modulation(self):
        """ Disables the signal modulation. """
        # TBD
        pass

    def data_trigger_setup(self, mode=None):
        """ Configure the trigger system for bitsequence transmission
        """
        self.write(":BB:ARBitrary:TRIGger:SOURce INT")
        playlist = self.ask(":BB:ARBitrary:WSEG:SEQ:SEL?").strip() != '""'
        if (mode is None):
            mode = 'AAUT' if playlist else 'SINGLE'
            
        self.write(f":BB:ARBitrary:TRIGger:SEQ {mode:s}")
        if mode == 'AAUT' and playlist:
            self.write(":BB:ARB:TRIG:SMOD SEQ")
        else:
            self.write(":BB:ARB:TRIG:SMOD NEXT")

    def data_trigger(self):
        """ Trigger a bitsequence transmission
        """
        self.write("BB:ARB:TRIG:EXEC")

    def set_fsk_constellation(self, constellation, fsk_dev):
        """ For multi level FSK modulation, we need to define the constellation mapping.

        For R&S SMIQ06B, there is a dedicated user modulation to define FSK constellation.
        """
        raise NotImplementedError("Method not implemented")

    def _get_markerdata(self, markers_list):
        # Markers are integer from 1 to 4
        data = []
        for i, markers in enumerate(markers_list):
            # Remove duplicates
            markers = list(set(markers))
            # Compute value
            value = sum([1 << (i - 1) for i in markers])
            assert(value <= 15)
            if (i % 2):
                value_byte |= value
                data.append(value_byte)
            else:
                value_byte = (value << 4)

        return data

    def _get_iqdata(self, iq_seq):
        """ Utility method that translate iq samples into a list of integers couples """
        data = []
        iq_data_max_value = 2**(self._iq_data_bits - 1) - 1
        for iq in iq_seq:
            data.append((round(iq.real*iq_data_max_value),
                         round(iq.imag*iq_data_max_value)))
        return data

    def data_iq_load(self, iqdata, sampling_rate, name, markers=None):
        stream = BytesIO()
        waveform_tag = WaveformTag(self._get_iqdata(iqdata))
        tag_list = [TypeTag(magic="SMU-WV"),
                    IntegerTag(name="CLOCK", value=sampling_rate),
                    IntegerTag(name="SAMPLES", value=waveform_tag.samples),
                    waveform_tag,
                    ]
        if markers is not None:
            tag_list.append(CLWTag(self._get_markerdata(markers)))
        
        RSGenerator(tag_list).generate(stream)
        stream.seek(0)
        self.adapter.write_binary_values(f'BB:ARB:WAV:DATA "{name}",',
                                         stream.read(),
                                         datatype='B')
        # self.write(f':BB:ARBitrary:WAVeform:CLOCk "{name}", {sampling_rate:d}')
        # Select waveform
        self.write(f"BB:ARB:WAV:SEL '{name:s}'")

    def data_iq_sequence_load(self, iqdata_seq, name=None, sampling_rate=None):

        if name is None:
            name = "IQSequence"

        # Create configuration file
        conf_file = f"{name:s}_conf.inf_mswv"
        self.delete_file(conf_file)
        self.write(f"BB:ARB:WSEG:CONF:SEL '{conf_file:s}'")

        # Define multisegment file name
        seq_file = f"{name:s}.wv"
        self.delete_file(seq_file)
        self.write(f"BB:ARB:WSEG:CONF:OFIL '{seq_file:s}'")

        # Set sampling rate, if defined
        if sampling_rate is not None:
            self.write(f'BB:ARB:WSEG:CONF:CLOC:MODE USER')
            self.write(f'BB:ARB:WSEG:CONF:CLOC {sampling_rate:d}Hz')
        else:
            self.write(f'BB:ARB:WSEG:CONF:CLOC:MODE UNCHanged')
        self.write('BB:ARB:WSEG:CONF:LEV:MODE UNCHanged')

        # Process list and identify sequences repetitions
        segment_list = self._process_iq_sequence(iqdata_seq)
        # Identify unique segments
        unique_segments = list(set([item[0] for item in segment_list]))
        # Create a convenience dictionary
        unique_segments_idx = {v:i for (i,v) in enumerate(unique_segments)}
        
        for seg_name in unique_segments:
            self.write(f"BB:ARB:WSEG:CONF:SEGM:APP '{seg_name:s}'")

        self.write(f"BB:ARB:WSEG:CRE '{conf_file:s}'")

        # Make playlist
        # Define multisegment file name
        pl_file = f"{name:s}_pl.wvs"
        self.delete_file(pl_file)
        self.write(f"BB:ARB:WSEG:SEQ:SEL '{pl_file:s}'")
        for i, (seg_name, rep) in enumerate(segment_list):
            last = (i == (len(segment_list) - 1))
            next_p = 'BLANK' if last else 'NEXT'
            idx = unique_segments_idx[seg_name]
            self.write(f'BB:ARB:WSEG:SEQ:APP ON,{idx:d},{rep:d},{next_p:s}')
 
        # Select waveform
        self.complete
        self.write(f"BB:ARB:WAV:SEL '{seq_file:s}'")

    def delete_file(self, filename):
        """ Delete a file in the instrument memory """
        if filename in self.file_list:
            self.write(f":MMEM:DEL '{filename:s}'")
