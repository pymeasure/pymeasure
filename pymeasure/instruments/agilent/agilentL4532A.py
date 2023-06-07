#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

import numpy as np
from numpy import typing

from enum import Enum

from pymeasure.errors import Error
from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_discrete_set, strict_range

class AgilentL4532A(Instrument):
    """
    Represents the Agilent L4532A/L4534A digitizers.
    """
    
    class Channel(Channel):
        """Implementation of an Agilent L4532A/L4534A channel."""

        def __init__(self, instrument, id):
            super().__init__(instrument, id)

        config = Instrument.measurement("CONF:CHAN:ATTR? (@{ch})",
                                        """Get Channel configuration (<range>,<coupling>,<filter>)""")
        
        range = Instrument.control("CONF:CHAN:RANG? (@{ch})",
                                   "CONF:CHAN:RANG(@{ch}), %.3g",
                                   """Control Voltage range for this channel""",
                                   validator=strict_discrete_set,
                                   values = [ 0.25, 0.5, 1, 2, 4, 8, 16, 32, 128, 256 ]
                                   )
        
        filter = Instrument.control("CONF:CHAN:FILT? (@{ch})",
                                    "CONF:CHAN:FILT (@{ch}),%s",
                                    """Control Filter for this channel (LP_20_MHZ, LP_2_MHZ, LP_200_KHZ)""",
                                    validator=strict_discrete_set,
                                    values = [ 'LP_20_MHZ', 'LP_2_MHZ', 'LP_200_KHZ' ]
                                    )
        
        
        def read_data_block(self):
            # Data block has header of form '#<n><n digits>', 
            # where <n>specifies the number of digits used to indicate the size of the block, 
            # and the <n digits> indicate the block size in bytes. 
            digits = self.read_bytes(2).decode()
            if not digits.startswith('#'):
                raise Error()
            bytes = int(self.read_bytes(int(digits[1])).decode())
            return self.read_bytes(bytes)
        
        @property
        def voltage(self) -> typing.NDArray[np.float32]:
            """Get voltage measurements for this channel"""
            self.write(f'FETC:WAV:VOLT? (@{self.id})')
            data = self.read_data_block()
            return np.frombuffer(data, dtype=np.float32)
        
        @property
        def adc(self) -> typing.NDArray[np.int16]:
            """Get raw ADC measurements for this channel"""
            self.write(f'FETC:WAV:ADC? (@{self.id})')
            data = self.read_data_block()
            return np.frombuffer(data, dtype=np.int16)

    display = Instrument.control(
        'DISPL:TEXT?',
        'DISPL:TEXT \"%s\"',
        """Control Display text on screen, up to 12 characters"""
    )

    def clear_display(self):
        return self.write('DISPL:TEXT:CLE')

    arm_source = Instrument.control(
        "CONF:ARM:SOUR?",
        "CONF:ARM:SOUR %s",
        """Set the source used to arm the digitizer (IMMediate|EXTernal|SOFTware|TIMer) """,
        validator=strict_discrete_set,
        values = ['IMM', 'SOFT', 'EXT', 'TIM']
        )
    
    ext_slope = Instrument.control(
        "CONF:EXT:INP?",
        "CONF:EXT:INP %s",
        """Set the edge to be used for the external trigger input, NEGative or POSitive""",
        validator=strict_discrete_set,
        values = ['NEG', 'POS']
    )

    trigger_source = Instrument.control(
        "CONF:TRIG:SOUR?",
        "CONF:TRIG:SOUR %s",
        """Set the trigger source {IMMediate|SOFTware|EXTernal|CHANnel|OR}""",
        validator=strict_discrete_set,
        values = ['IMM', 'SOFT', 'EXT', 'CHAN', 'OR']
    )

    sample_rate = Instrument.control(
        "CONF:ACQ:SRAT?",
        "CONF:ACQ:SRAT %d",
        """Set the sample rate:
        1000
        2000
        5000
        10000
        20000
        50000
        100000
        200000
        500000
        1000000
        2000000
        5000000
        10000000
        20000000
        """,
        validator=strict_discrete_set,
        values = [1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000, 2000000, 5000000, 10000000, 20000000]
    )

    samples_per_record = Instrument.control(
        "CONF:ACQ:SCO?",
        "CONF:ACQ:SCO %d",
        """Control number of samples that will be captured for each trigger, in multiples of 4 (8-128,000,000)""",
        validator=strict_range,
        values=[8,128e6]
    )

    number_of_records = Instrument.control(
        "CONF:ACQ:REC?",
        "CONF:ACQ:REQ %d",
        """Control number of of records that will be captured before arming is disabled (1-1024)""",
        validator=strict_range,
        values=[1, 1024])

    maximum_samples = Instrument.measurement(
        "CONF:ACQ:SCO:MAX?",
        """Get Maximum number of samples that can be used in a record""")

    acquisition = Instrument.measurement(
        "CONF:ACQ:ATTR?",
        """Get Acquistion settings
        returns: sample_rate, samples_per_record, pre_trig_samples_per_record, num_records, trigger_holdoff, trigger_delay 
        """
    )

    def config_acquisition(self, sample_rate, samples_per_record,pre_trig_samples_per_record=0,num_records=1,trigger_holdoff=0,trigger_delay=0):
        return self.write(f'CONF:ACQ:ATTR {sample_rate:e},{samples_per_record:d},{pre_trig_samples_per_record:d},{num_records:d},{trigger_holdoff:d},{trigger_delay:d}')
    
    def arm(self) -> None:
        self.write('ARM')

    def init(self) -> None:
        self.write('INIT')
    
    channels = Instrument.ChannelCreator(Channel, (1,2))

    def __init__(self, adapter, name="Agilent L4532A Digitizer", **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )
        # Detect number of supported channels using IDN?
        # id = self.id.split(',')
        
        # if len(id) < 2:
        #     raise Error('Wrong instrument type')
        # if id[1].startswith('L453') and id[5] == 'A':
        #     channel_count = int(id[4])
        # else:
        #     raise Error('Wrong instrument type')
        # self.name = id[0] + ' ' + id[1]

        # # Add channels
        # for ch in range(1, channel_count):
        #     self.add_child(Channel, ch)
        