#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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

import time
from . import sr830
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, \
    strict_discrete_range

class SR850(sr830.SR830):
    EXPANSION_VALUES = None  #[1, 10, 100]
    EXPANSION_RANGE = [1, 256]
    INPUT_CONFIGS = ['A', 'A - B', 'I']
    INPUT_GAINS = ['1 MOhm', '100 MOhm']
    REFERENCE_SOURCES = ['Internal', 'Sweep', 'External']
    SNAP_ENUMERATION = {"x": 1, "y": 2, "r": 3, "theta": 4,
                        "aux in 1": 5, "aux in 2": 6, "aux in 3": 7, "aux in 4": 8,
                        "frequency": 9, "trace 1": 10, "trace 2": 11, 
                        'trace 3': 12, 'trace 4': 13} 
    OUTPUT_INTERFACE = ['RS232', 'GPIB']

    def __init__(self, adapter, name="Stanford Research Systems SR850 Lock-in amplifier",
                 **kwargs):
        # write term lf or cr on RS232, lf or eoi on GPIB
        kwargs.setdefault('write_termination', '\n')  
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        if 'GPIB' in self.name.capitalize():
            self.output_interface = 'GPIB'
    output_interface = Instrument.control(
        "OUTX?", "OUTX %d",
        """ An string property that controls the output interface. Inputs are
        accepted on both remote interfaces, but instrment responses are only
        directed to the selected output interface. 
        Allowed values are: {}""".format(OUTPUT_INTERFACE),
        validator=strict_discrete_set,
        values=OUTPUT_INTERFACE,
        map_values=True
    )
    input_gain = Instrument.control(  # SR830 does not have this
        "IGAN?", "IGAN %d",
        """ An string property that controls the input gain for the current input. Allowed
        values are: {}""".format(INPUT_GAINS),
        validator=strict_discrete_set,
        values=INPUT_GAINS,
        map_values=True
    )
    channel1 = Instrument.control(
        "FOUT?1", "FOUT1,%d",  # differs from SR830, where it is DDEF
        """ A string property that represents the type of front panel Channel 1
        output sources, taking the values X, R, Theta, Trace 1, Trace 2,
        Trace 3, or Trace 4.
        This property can be set.""",
        validator=strict_discrete_set,
        values=['X', 'R', 'Theta', 'Trace 1', 'Trace 2', 'Trace 3', 'Trace 4'],
        map_values=True
    )
    channel2 = Instrument.control(
        "FOUT?2", "FOUT2,%d",  # differs from SR830, where it is DDEF
        """ A string property that represents the type of Channel 2,
        taking the values Y, R, Theta, Trace 1, Trace 2,
        Trace 3, or Trace 4.""",
        validator=strict_discrete_set,
        values=['Y', 'R', 'Theta', 'Trace 1', 'Trace 2', 'Trace 3', 'Trace 4'],
        map_values=True
    )
    input_config = Instrument.control(
        "ISRC?", "ISRC %d",
        """ An string property that controls the input configuration. Allowed
        values are: {}""".format(INPUT_CONFIGS),
        validator=strict_discrete_set,
        values=INPUT_CONFIGS,  # make sure 850.INPUT_CONFIGS overrides 830.INPUT_CONFIGS
        map_values=True
    )
    reference_source = Instrument.control(
        "FMOD?", "FMOD %d",
        """ An string property that controls the reference source. Allowed
        values are: {}""".format(REFERENCE_SOURCES),
        validator=strict_discrete_set,
        values=REFERENCE_SOURCES,
        map_values=True
    )
    def get_scaling(self, channel):
        """ Returns the offset percent and the expansion term
        that are used to scale the channel in question
        """
        if channel not in self.CHANNELS:
            raise ValueError('SR850 channel is invalid')
        channel = self.CHANNELS.index(channel) + 1
        offset, expand = self.ask("OEXP? %d" % channel).split(',')
        return float(offset), int(expand)

    def set_scaling(self, channel, percent, expand=0):
        """ Sets the offset of a channel ('X', 'Y', or 'R') to a
        certain percent (-105% to 105%) of the signal, with
        an optional expansion term (1 <= expand <= 256)
        """
        if channel not in self.CHANNELS:
            raise ValueError('SR850 channel is invalid')
        channel = self.CHANNELS.index(channel) + 1
        expand = strict_discrete_range(expand, self.EXPANSION_RANGE, 1)
        self.write("OEXP %i,%.2f,%i" % (channel, percent, expand))
    
    def quick_range(self):
        """ While the magnitude is out of range, increase
        the sensitivity by one setting
        """
        self.write('LIAE 2,1')
        while self.is_out_of_range():
            self.write("SENS%d" % (int(self.ask("SENS?")) + 1))
            time.sleep(5.0 * self.time_constant)
            self.write("*CLS")
        # Set the range as low as possible
        newsensitivity = 1.15 * abs(self.magnitude)
        # FIXME - double check this
        if self.input_gain in ('1 MOhm', '100 MOhm'):
            newsensitivity = newsensitivity * 1e6
        self.sensitivity = newsensitivity

    def snap(self, val1="X", val2="Y", *vals):
        """ Method that records and retrieves 2 to 6 parameters at a single
        instant. The parameters can be one of: X, Y, R, Theta, Aux In 1,
        Aux In 2, Aux In 3, Aux In 4, Frequency, trace 1, trace 2, trace 3,
        or trace 4.
        Default is "X" and "Y".

        :param val1: first parameter to retrieve
        :param val2: second parameter to retrieve
        :param vals: other parameters to retrieve (optional)
        """
        # sr830.snap calls self.SNAP_ENUMERATION, so this will resolve 
        # correctly. method is written here to update the docstring
        return super().snap(val1, val2, *vals)
    
    @property
    def buffer_count(self):
        """
        unlike SR830, SR850 SPTS queries one of multiple traces (4). Not yet
        implemented.
        Raises
        ------
        NotImplementedError
            _description_
        """
        # note, unlike SR830, SR850 SPTS queries one of multiple traces (4)
        raise NotImplementedError()
    
    def fill_buffer(self, count: int, has_aborted=lambda: False, delay=0.001):
        """ not yet implemented
        """
        raise NotImplementedError()

    def buffer_measure(self, count, stopRequest=None, delay=1e-3):
        """ not yet implemented
        """
        raise NotImplementedError()
    
    def wait_for_buffer(self, count, has_aborted=lambda: False,
                        timeout=60, timestep=0.01):
        """ not yet implemented
        """
        raise NotImplementedError()

    def get_buffer(self, channel=1, start=0, end=None):
        """ not yet implemented
        """
        raise NotImplementedError()
