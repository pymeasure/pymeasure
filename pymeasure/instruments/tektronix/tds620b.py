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
    strict_range, joined_validators
import numpy as np

def capitalize_string(string: str, *args, **kwargs):
    return string.upper()


# Combine the capitalize function and validator
string_validator = joined_validators(capitalize_string, strict_discrete_set)


class TDS620B(Instrument):
    """ Represents the Tektronix TDS 620B Oscilloscope
    and provides a high-level for interacting with the instrument

    .. code-block:: python

        osc= TDS620B("GPIB0::...")
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

    data_encoding = Instrument.control(
        "DATa:ENCdg?", "DATa:ENCdg %s",
        """A string property that sets the data encoding for transfer. """,
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

    def get_waveform_parameters(self, source):
        """
        Get the waveform parameters for a given waveform source.
        """
        self.data_source = source
        return self.ask('WFMPre:'+source+'?')

    def get_binary_curve(self, source='CH1', encoding='RIPBINARY', hires=False):
        """
        Convenience function to get the curve data from the sources available in self.data_source using binary encoding.
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
            if value in TDS620B.Measurement.SOURCE_VALUES:
                self.parent.write("%sSOU %s" % (self.preamble, value))
            else:
                raise ValueError("Invalid source ('%s') provided to %s" % (
                                 self.parent, value))

        @property
        def type(self):
            return self.parent.ask("%sTYP?" % self.preamble).strip()

        @type.setter
        def type(self, value):
            if value in TDS620B.Measurement.TYPE_VALUES:
                self.parent.write("%sTYP %s" % (self.preamble, value))
            else:
                raise ValueError("Invalid type ('%s') provided to %s" % (
                                 self.parent, value))

        @property
        def unit(self):
            return self.parent.ask("%sUNI?" % self.preamble).strip()

        @unit.setter
        def unit(self, value):
            if value in TDS620B.Measurement.UNIT_VALUES:
                self.parent.write("%sUNI %s" % (self.preamble, value))
            else:
                raise ValueError("Invalid unit ('%s') provided to %s" % (
                                 self.parent, value))

    def __init__(self, resourceName, **kwargs):
        super(TDS620B, self).__init__(
            resourceName,
            "Tektronix TDS 620B Oscilliscope",
            **kwargs
        )
        self.measurement = TDS620B.Measurement(self)