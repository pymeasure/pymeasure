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

from decimal import Decimal

from pymeasure.errors import Error
from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_discrete_set, strict_range, strict_discrete_range
from pymeasure.units import ureg


def sample_count_function(value, values): return strict_discrete_range(value, values, 4)

SAMPLE_COUNT_VALUES = [8, 128e6]
PRE_TRIG_VALUES = [0, 128e6]
RECORD_COUNT_VALUES = [1, 1024]

TRIGGER_HOLDOFF_VALUES = ureg.Quantity(np.asarray([0, 10]), ureg.s)
TRIGGER_DELAY_VALUES = ureg.Quantity([0, 3600], ureg.s)

def _get_channel_config_process(values):
    result = {
        'range': ureg.Quantity(Decimal(values[0]), ureg.V),
        'coupling': values[1],
        'filter': values[2]
    }
    return result

def _get_acq_config_process(values):
    return {
        'sample_rate': ureg.Quantity(values[0], ureg.Hz),
        'samples_per_record': int(values[1]),
        'pre_trig_samples': int(values[2]),
        'num_records': int(values[3]),
        'trigger_holdoff': ureg.Quantity(values[4], ureg.s),
        'trigger_delay': ureg.Quantity(values[5], ureg.s)
    }


def _set_acq_config_process(value):
    return '{},{},{},{},{},{}'.format(
        value['sample_rate'].m_as(ureg.Hz),
        value['samples_per_record'],
        value['pre_trig_samples'],
        value['num_records'],
        value['trigger_holdoff'].m_as(ureg.s),
        value['trigger_delay'].m_as(ureg.s))


VOLTAGE_RANGE_VALUES = ureg.Quantity(np.asarray([0.25, 0.5, 1, 2, 4, 8, 16, 32, 128, 256]), ureg.V)

COUPLING_VALUES = ['DC', 'AC']
FILTER_VALUES = ['LP_20_MHZ', 'LP_2_MHZ', 'LP_200_KHZ']
    
class AgilentL4534A(Instrument):
    """
    Represents the Agilent L4532A/L4534A digitizers.
    """

    SAMPLE_RATE_VALUES = ureg.Quantity(np.asarray([1000, 2000, 5000, 10000, 20000, 50000,
                                    100000, 200000, 500000, 1000000, 2000000, 5000000, 10000000, 20000000]), ureg.Hz)

    @staticmethod
    def _validate_acq_config(value, values):
        strict_discrete_set(value['sample_rate'], AgilentL4534A.SAMPLE_RATE_VALUES)
        strict_discrete_range(value['samples_per_record'], SAMPLE_COUNT_VALUES, 4)
        strict_discrete_range(value['pre_trig_samples'], PRE_TRIG_VALUES, 4)
        strict_range(value['num_records'], RECORD_COUNT_VALUES)
        strict_range(value['trigger_holdoff'], TRIGGER_HOLDOFF_VALUES)
        strict_range(value['trigger_delay'], TRIGGER_DELAY_VALUES)
        return value

    class Channel(Channel):
        """Implementation of an Agilent L4532A/L4534A channel."""

        def __init__(self, instrument, id):
            super().__init__(instrument, id)

        VOLTAGE_RANGE_VALUES = VOLTAGE_RANGE_VALUES
        COUPLING_VALUES = COUPLING_VALUES
        FILTER_VALUES = FILTER_VALUES

        @staticmethod
        def _validate_channel_config(value, values):
            if not 'range' in value:
                raise ValueError('Requires \'range\'')
            if not 'coupling' in value:
                raise ValueError('Requires \'coupling\'')
            if not 'filter' in value:
                raise ValueError('Requires \'filter\'')

            strict_discrete_set(value['range'], VOLTAGE_RANGE_VALUES)
            strict_discrete_set(value['coupling'], COUPLING_VALUES)
            strict_discrete_set(value['filter'], FILTER_VALUES)
            return value
    
        config = Instrument.control(
            "CONF:CHAN:ATTR? (@{ch})",
            "CONF:CHAN:ATTR (@{ch}),%s",
            """Control Channel configuration with dict containing range (in V), coupling, and filter""",
            set_process=lambda v: '{:.3g},{},{}'.format(
                v['range'].m_as(ureg.V), v['coupling'], v['filter']),
            get_process=_get_channel_config_process,
            validator=_validate_channel_config
        )

        range = Instrument.control(
            "CONF:CHAN:RANG? (@{ch})",
            "CONF:CHAN:RANG (@{ch}),%s",
            """Control Voltage range for this channel
            Ranges: 0.25, 0.5, 1, 2, 4, 8, 16, 32, 128, 256
            """,
            set_process=lambda v: Decimal(v.m_as(ureg.V)).to_eng_string(
            ),  # send the value as V to the device
            get_process=lambda v: ureg.Quantity(v, ureg.V),  # convert to quantity
            validator=strict_discrete_set,
            values=VOLTAGE_RANGE_VALUES
        )

        coupling = Instrument.control(
            "CONF:CHAN:COUP? (@{ch})",
            "CONF:CHAN:COUP (@{ch}),%s",
            """Comtrol channel coupling {AC|DC}""",
            validator=strict_discrete_set,
            values=COUPLING_VALUES
        )

        filter = Instrument.control(
            "CONF:CHAN:FILT? (@{ch})",
            "CONF:CHAN:FILT (@{ch}),%s",
            """Control Filter for this channel (LP_20_MHZ, LP_2_MHZ, LP_200_KHZ)""",
            validator=strict_discrete_set,
            values=FILTER_VALUES
        )

        def _read_data_block(self):
            # Data block has header of form '#<n><n digits>',
            # where <n>specifies the number of digits used to indicate the size of the block,
            # and the <n digits> indicate the block size in bytes.
            digits = self.read_bytes(2).decode()
            if not digits.startswith('#'):
                raise Error()
            bytes = int(self.read_bytes(int(digits[1])).decode())
            # Read specified number of bytes + newline terminator
            buf = memoryview(self.read_bytes(bytes+1))
            # Return view that strips off newline to contain only desired bytes
            return buf[:-1]

        @property
        def voltage(self) -> typing.NDArray[np.float32]:
            """Get voltage measurements for this channel"""
            self.write(f'FETC:WAV:VOLT? (@{self.id})')
            data = self._read_data_block()
            return ureg.Quantity(np.frombuffer(data, dtype='>f4'), ureg.V)

        @property
        def adc(self) -> typing.NDArray[np.int16]:
            """Get raw ADC measurements for this channel in counts (-32,767,+32,767) in current voltage range"""
            self.write(f'FETC:WAV:ADC? (@{self.id})')
            data = self._read_data_block()
            return np.frombuffer(data, dtype='>i2')

    display = Instrument.control(
        'DISP:TEXT?',
        'DISP:TEXT \"%s\"',
        """Control Display text on screen, up to 12 characters""",
        get_process=lambda v: v.strip('\"')
    )

    def clear_display(self):
        return self.write('DISP:TEXT:CLE')

    arm_source = Instrument.control(
        "CONF:ARM:SOUR?",
        "CONF:ARM:SOUR %s",
        """Set the source used to arm the digitizer (IMMediate|EXTernal|SOFTware|TIMer)""",
        validator=strict_discrete_set,
        values=['IMM', 'SOFT', 'EXT', 'TIM']
    )

    ext_slope = Instrument.control(
        "CONF:EXT:INP?",
        "CONF:EXT:INP %s",
        """Set the edge to be used for the external trigger input, NEGative or POSitive""",
        validator=strict_discrete_set,
        values=['NEG', 'POS']
    )

    TRIGGER_SOURCE_VALUES = ['IMM', 'SOFT', 'EXT', 'CHAN', 'OR']

    trigger_source = Instrument.control(
        "CONF:TRIG:SOUR?",
        "CONF:TRIG:SOUR %s",
        """Set the trigger source {IMMediate|SOFTware|EXTernal|CHANnel|OR}""",
        validator=strict_discrete_set,
        values=TRIGGER_SOURCE_VALUES
    )

    sample_rate = Instrument.control(
        "CONF:ACQ:SRAT?",
        "CONF:ACQ:SRAT %d",
        """Set the sample rate in samples/s (Hz):
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
        values=SAMPLE_RATE_VALUES,
        set_process=lambda v: v.m_as(ureg.Hz),  # send the value as Hz to the device
        get_process=lambda v: ureg.Quantity(v, ureg.Hz)  # convert to quantity
    )

    samples_per_record = Instrument.control(
        "CONF:ACQ:SCO?",
        "CONF:ACQ:SCO %d",
        """Control number of samples that will be captured for each trigger, in multiples of 4 (8-128,000,000)""",
        validator=sample_count_function,
        values=SAMPLE_COUNT_VALUES
    )

    pre_trigger_samples = Instrument.control(
        "CONF:ACQ:SPR?",
        "CONF:ACQ:SPR %d",
        """Control number of samples that will captured pre-trigger, in multiples of 4 (8-128,000,000)""",
        validator=sample_count_function,
        values=PRE_TRIG_VALUES
    )

    number_of_records = Instrument.control(
        "CONF:ACQ:REC?",
        "CONF:ACQ:REQ %d",
        """Control number of of records that will be captured before arming is disabled (1-1024)""",
        validator=strict_range,
        values=RECORD_COUNT_VALUES
    )

    trigger_holdoff = Instrument.control(
        "CONF:ACQ:THOL?",
        "CONF:ACQ:THOL %e",
        """Control minimum time between triggers, during which trigger inputs are ignored,
          in decimal seconds (0-10s)""",
        validator=strict_range,
        values=TRIGGER_HOLDOFF_VALUES
    )

    trigger_delay = Instrument.control(
        "CONF:ACQ:TDEL?",
        "CONF:ACQ:TDEL %e",
        """Control delay time after trigger before acquistion starts, in decimal seconds (0-3600s)""",
        validator=strict_range,
        values=TRIGGER_DELAY_VALUES
    )

    maximum_samples = Instrument.measurement(
        "CONF:ACQ:SCO:MAX?",
        """Get Maximum number of samples that can be used in a record"""
    )

    acquisition = Instrument.control(
        "CONF:ACQ:ATTR?",
        "CONF:ACQ:ATTR %s",
        """Control Acquistion settings
        returns: sample_rate, samples_per_record, pre_trig_samples_per_record, num_records, trigger_holdoff, trigger_delay 
        """,
        set_process=_set_acq_config_process,
        get_process=_get_acq_config_process,
        validator=_validate_acq_config
    )

    def arm(self) -> None:
        """
        Trigger ARM condition in software
        """
        self.write('ARM')

    def init(self) -> None:
        """
        Initialize measurement with current configuration.\n
        This puts the instrument in acquisition state and waits for arm condition.\n
        If arm is immediate, it will wait for trigger.\n
        If both arm and trigger are immediate, it will immediately start capturing data.\n
        Instrument will singal complete once capture is finished
        """
        self.write('INIT')

    channels = Instrument.ChannelCreator(Channel, (1, 2, 3, 4))

    def __init__(self, adapter, name="Agilent L4534A Digitizer", **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )