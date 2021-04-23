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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, \
    strict_range, joined_validators, truncated_range
import numpy as np

def capitalize_string(string: str, *args, **kwargs):
    return string.upper()


# Combine the capitalize function and validator
string_validator = joined_validators(capitalize_string, strict_discrete_set)


class TDS6604(Instrument):
    """ Represents the Tektronix TDS 620B Oscilloscope
    and provides a high-level for interacting with the instrument

    .. code-block:: python
        osc= TDS6604("GPIB0::...")
        osc.pretrigger = 1 # set pretrigger to 1% of recorded waveform
        osc.acquire_mode = 'SAMPLE' # the default
        osc.acquire_stop_after = 'SEQUENCE' # Stop recording after 1 waveform after trigger
        osc.data_source = 'CH1' # set data source to channel 1
        #emit trigger somehow
        data = osc.get_binary_curve() # get curve data from channel 1 with default binary encoding
    """

    pretrigger = Instrument.control(
        "HORizontal:TRIGger:POSition?", "HORizontal:TRIGger:POSition %d",
        """A integer property that controls the percent of the recorded
         waveform that occurs before the trigger event. O is no pretrigger,
         100 is all pretrigger.""",
        validator=strict_range,
        values=[0, 100]
    )

    acquire_mode = Instrument.control(
        "ACQuire:MODe?", "ACQuire:MODe %s",
        """A string property that controls how the final value of the acquisition
        interval is generated from the many data samples. Can be set to:
        SAMPLE, PEAKDETECT, AVERAGE, ENVELOPE""",
        validator=string_validator,
        values=['SAMPLE', 'PEAKDETECT', 'AVERAGE', 'ENVELOPE']
    )

    acquire_naverages = Instrument.control(
        "ACQuire:NUMAVg?", "ACQuire:NUMAVg %d",
        """A integer property ranging from 2 to 10,000 that controls the number
        of averages taken if the acquire_mode is AVERAGE.""",
        validator=strict_range,
        values=[2, 10000]
    )

    acquire_num_acq = Instrument.measurement(
        "ACQuire:NUMACq?",
        """A integer property indicating the number of acquisitions that have taken
        place since starting acquisition.""",
    )

    acquire_state = Instrument.control(
        "ACQuire:STATE?", "ACQuire:STATE %s",
        """A string property that starts or stops acquisitions. Equivalent to pressing
         RUN/STOP button on front panel. Can be set to:
        RUN,STOP""",
        validator=string_validator,
        values=['RUN', 'STOP']
    )

    acquire_stop_after = Instrument.control(
        "ACQuire:STOPAfter?", "ACQuire:STOPAfter %s",
        """A string property that sets when to stop taking acquisitions. Can be set to:
        RUNSTOP, SEQUENCE, LIMIT. RUNSTOP -> run until front panel run/stop is pressed,
        SEQUENCE -> stop after collecting trace following a trigger event.
        LIMIT-> stop after limit test condition is met.""",
        validator=string_validator,
        values=['RUNSTOP', 'SEQUENCE', 'LIMIT']
    )

    data = Instrument.control(
        "DATa?", "DATa: %s",
        """A string property that sets the data record start and stop positions through keywords. 
        Options are 'INIT' to return to factory default, and 'SNAP' to snap to vertical cursors""",
        validator=string_validator,
        values=['INIT', 'SNAP']
    )

    data_start = Instrument.control(
        "DATa:STARt?", "DATa:STARt %d",
        """An integer proper that sets the record start point""",
        validator=truncated_range,
        values=[0,124000]
    )


    data_stop = Instrument.control(
        "DATa:STOP?", "DATa:STOP %d",
        """An interger property that sets the data record stop""",
        validator=truncated_range,
        values=[0,124000]
    )

    data_encoding = Instrument.control(
        "DATa:ENCdg?", "DATa:ENCdg %s",
        """A string property that sets the data encoding for transfer. 
        Options are 'RIPBINARY', 'RPBINARY', 'SRIBINARY', 'SRPBINARY'. The 'SRIBINARY' is the default, tested, value
         for the defaults of pymeasure's get_binary_values""",
        validator=string_validator,
        values=['ASCII', 'RIPBINARY', 'RPBINARY', 'SRIBINARY', 'SRPBINARY']
    )

    data_source = Instrument.control(
        "DATa:SOUrce?", "DATa:SOUrce %s",
        """A string property that sets the data source for transfer. """,
        validator=string_validator,
        values=['CH1', 'CH2', 'CH3', 'CH4', 'MATH1', 'MATH2', 'MATH3']
    )

    data_width = Instrument.control(
        "DATa:WIDth?", "DATa:WIDth %d",
        """A string property that sets the data source for transfer. """,
        validator=strict_discrete_set,
        values=[1, 2]
    )

    trigger_details = Instrument.measurement(
        "TRIGGER?",
        """Outputs a semicolon-delimited list of the current trigger parameters of the scope""",
    )

    trigger_main_details = Instrument.measurement(
        "TRIGGER:MAIn:EDGE?",
        """Outputs a semicolon-delimited list of the main trigger parameters of the scope""",
    )

    trigger_main_edge_coupling = Instrument.control(
        "TRIGger:MAIn:EDGE:COUPling?", "TRIGger:MAIn:EDGE:COUPling %s",
        """A string property that sets the main coupling. Options are: 'AC', 'DC', 'HFRej', 'LFRej', 'NOISErej' """,
        validator=string_validator,
        values=['AC', 'DC', 'HFRej', 'LFRej', 'NOISErej']
    )

    trigger_main_edge_slope = Instrument.control(
        "TRIGger:MAIn:EDGE:SLOpe?", "TRIGger:MAIn:EDGE:SLOpe %s",
        """A string property that sets the trigger slope to look at the rising ('RISe') or falling ('FALL') edge  """,
        validator=string_validator,
        values=['FALL', 'RISe']
    )

    trigger_main_edge_source = Instrument.control(
        "TRIGger:MAIn:EDGE:SOUrce?", "TRIGger:MAIn:EDGE:SOUrce %s",
        """A string property that sets the main trigger source. Options are 'CH1', 'CH2', 'CH3', 'CH4', 'LINE' """,
        validator=string_validator,
        values=['CH1', 'CH2', 'CH3', 'CH4', 'LINE']
    )

    trigger_main_holdoff_time = Instrument.control(
        "TRIGger:MAIn:HOLDOff:TIMe?", "TRIGger:MAIn:HOLDOff:TIMe %g",
        """A float property setting the holdoff time in seconds. Limits are 250 ns to 12 s.
          """,
        validator=truncated_range,
        values=[250e-9,12]
    )

    trigger_main_level = Instrument.control(
        "TRIGger:MAIn:LEVel?", "TRIGger:MAIn:LEVel %g",
        """A float property that sets the main trigger level. """,
        validator=truncated_range,
        values=[-10.0,10.0]
    )

    trigger_main_type = Instrument.control(
        "TRIGger:MAIn:TYPe?", "TRIGger:MAIn:TYPe %s",
        """A string property that sets the main trigger type. 'EDGE' is the normal, classic trigger. 
         PULse and LOGIc are also included but untested.""",
        validator=string_validator,
        values=['EDGE', 'LOGIc', 'PULse']
    )

    horizontal_secperdiv = Instrument.control(
        "HORizontal:SECdiv?", "HORizontal:SECdiv %g",
        """A float property that sets seconds per division. Ranges from 200 ps/div to 10 s/div,
        range is not continuous, and I was too lazy to figure out the values. The scope picks the next smallest
        sec/div if you specify one that is not a allowed.""",
        validator=truncated_range,
        values=[500e-12,10]
    )

    horizontal_recordlength = Instrument.control(
        "HORizontal:RECOrdlength?", "HORizontal:RECOrdlength %d",
        """An integer property that sets the length of the waveform record. Values are 500,1000,2500,5000,15000 points.
         Longer records will extend past the end of the scope screen and take longer to transfer. 
         There are 50 points/div""",
        validator=strict_discrete_set,
        values=[500, 2000, 5000, 10000, 25000, 50000, 100000, 124000, 200000]
    )

    CH1 = Instrument.measurement(
        "CH1?",
        """A property that returns all vertical paramters associated with CH1""",
    )

    CH1_bandwidth = Instrument.control(
        "CH1:BANdwidth?", "CH1:BANdwidth %s",
        """
        String parameter that sets the channel bandwidth to 'TWEnty':20 MHz, 'TWOfifty':250 MHz, 'FULl': 500 MHz.
        """,
        validator=string_validator,
        values=['TWEnty', 'TWOfifty', 'FULl']
    )

    CH1_coupling = Instrument.control(
        "CH1:COUPling?", "CH1:COUPling %s",
        """
        String parameter that sets the channel coupling to 'AC', 'DC', 'GND'.
        """,
        validator=string_validator,
        values=['AC', 'DC', 'GND']
    )

    CH1_deskew = Instrument.control(
        "CH1:DESKew?", "CH1:DESKew %g",
        """
        Float parameter in range -25 ns to +25 ns with resolution of 1 ps. Used to compensate for cables of different
        lengths. Implemented for completeness, read about before using.
        """,
        validator=truncated_range,
        values=[-25e-9,25e-9]
    )

    CH1_impedance = Instrument.control(
        "CH1:IMPedance?", "CH1:IMPedance %s",
        """
        String parameter that sets the channel impedance to  'FIFty', 'MEG'.
        """,
        validator=string_validator,
        values=['FIFty', 'MEG']
    )

    CH1_offset = Instrument.control(
        "CH1:OFFSet?", "CH1:OFFSet %g",
        """
        Float parameter that sets the channel offset. There are restrictions based on V/div
        """,
        validator=truncated_range,
        values=[-10,10]
    )

    CH1_scale = Instrument.control(
        "CH1:SCAle?", "CH1:SCAle %g",
        """
        Float parameter that sets the channel scale (V/div), range is 100 mV to 1 mV
        """,
        validator=truncated_range,
        values=[1e-3, 1]
    )

    CH2 = Instrument.measurement(
        "CH2?",
        """A property that returns all vertical paramters associated with CH2""",
    )

    CH2_bandwidth = Instrument.control(
        "CH2:BANdwidth?", "CH2:BANdwidth %s",
        """
        String parameter that sets the channel bandwidth to 'TWEnty':20 MHz, 'TWOfifty':250 MHz, 'FULl': 500 MHz.
        """,
        validator=string_validator,
        values=['TWEnty', 'TWOfifty', 'FULl']
    )

    CH2_coupling = Instrument.control(
        "CH2:COUPling?", "CH2:COUPling %s",
        """
        String parameter that sets the channel coupling to 'AC', 'DC', 'GND'.
        """,
        validator=string_validator,
        values=['AC', 'DC', 'GND']
    )

    CH2_deskew = Instrument.control(
        "CH2:DESKew?", "CH2:DESKew %g",
        """
        Float parameter in range -25 ns to +25 ns with resolution of 1 ps. Used to compensate for cables of different
        lengths. Implemented for completeness, read about before using.
        """,
        validator=truncated_range,
        values=[-25e-9, 25e-9]
    )

    CH2_impedance = Instrument.control(
        "CH2:IMPedance?", "CH2:IMPedance %s",
        """
        String parameter that sets the channel impedance to  'FIFty', 'MEG'.
        """,
        validator=string_validator,
        values=['FIFty', 'MEG']
    )

    CH2_offset = Instrument.control(
        "CH2:OFFSet?", "CH2:OFFSet %g",
        """
        Float parameter that sets the channel offset. There are restrictions based on V/div
        """,
        validator=truncated_range,
        values=[-10, 10]
    )

    CH2_scale = Instrument.control(
        "CH2:SCAle?", "CH2:SCAle %g",
        """
        Float parameter that sets the channel scale (V/div), range is 100 mV to 1 V
        """,
        validator=truncated_range,
        values=[1e-3, 1]
    )


    def force_trigger(self):
        """
        Forces a trigger event to occur
        """
        self.write('TRIGGER FORCe')



    def get_waveform_parameters(self, source):
        """
        Get the waveform parameters for a given waveform source.
        """
        self.data_source = source
        return self.ask('WFMPre:'+source+'?')

    def get_binary_curve(self, source='CH1', encoding='SRIBINARY', hires=False):
        """
        Convenience function to get the curve data from the sources available in self.data_source using binary encoding.
        Transfer is signed, 0 is in center. 5 divs above and below recorded (though only +-4 shown on scope)
        If trigger is unchanged then pulse is starts being measured at 50% of time scale, so halfway
        """
        self.data_encoding = encoding
        self.data_source = source
        if not hires:
            self.data_width = 1
            out = self.binary_values('CURVe?', dtype=np.int8)
        else:
            self.data_width = 2
            out = self.binary_values('CURVe?', dtype=np.int16)

        return out

    def get_ascii_curve(self, source='CH1', hires=False):
        """
        Function to get the curve data from the sources available in self.data_source using ascii encoding.
        """
        self.data_encoding = 'ASCII'
        self.data_source = source
        if not hires:
            self.data_width = 1
        else:
            self.data_width = 2
        out = self.ask('CURVe?')
        return out


    class Measurement(object):

        SOURCE_VALUES = ['CH1', 'CH2', 'MATH']

        TYPE_VALUES = [
            'FREQ', 'MEAN', 'PERI', 'PHA', 'PK2', 'CRM',
            'MINI', 'MAXI', 'RIS', 'FALL', 'PWI', 'NWI'
        ]

        UNIT_VALUES = ['V', 's', 'Hz']

        def __init__(self, parent, preamble="MEASU:IMM:"):
            self.parent = parent
            self.preamble = preamble

        @property
        def value(self):
            return self.parent.values("%sVAL?" % self.preamble)

        @property
        def source(self):
            return self.parent.ask("%sSOU?" % self.preamble).strip()

        @source.setter
        def source(self, value):
            if value in TDS6604.Measurement.SOURCE_VALUES:
                self.parent.write("%sSOU %s" % (self.preamble, value))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                                 self.parent, value))

        @property
        def type(self):
            return self.parent.ask("%sTYP?" % self.preamble).strip()

        @type.setter
        def type(self, value):
            if value in TDS6604.Measurement.TYPE_VALUES:
                self.parent.write("%sTYP %s" % (self.preamble, value))
            else:
                raise ValueError("Invalid type ('%s') provided to %s" % (
                                 self.parent, value))

        @property
        def unit(self):
            return self.parent.ask("%sUNI?" % self.preamble).strip()

        @unit.setter
        def unit(self, value):
            if value in TDS6604.Measurement.UNIT_VALUES:
                self.parent.write("%sUNI %s" % (self.preamble, value))
            else:
                raise ValueError("Invalid unit ('%s') provided to %s" % (
                                 self.parent, value))

    def __init__(self, resourceName, **kwargs):
        super(TDS6604, self).__init__(
            resourceName,
            "Tektronix TDS 620B Oscilliscope",
            **kwargs
        )
        self.measurement = TDS6604.Measurement(self)