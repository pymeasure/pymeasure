#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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
import math
from enum import IntFlag
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class HP8116A(Instrument):
    """ Represents the Hewlett-Packard 8116A 50 MHz Pulse/Function Generator
    and provides a high-level interface for interacting
    with the instrument.
    """

    def __init__(self, resourceName, **kwargs):
        kwargs.setdefault('read_termination', '\r\n')
        kwargs.setdefault('write_termination', '\r\n')
        kwargs.setdefault('send_end', True)
        super(HP8116A, self).__init__(
            resourceName,
            'Hewlett-Packard 8116A Pulse/Function Generator',
            includeSCPI=False,
            **kwargs
        )
    
    OPERATING_MODES = {
        'normal': 'M1',
        'triggered': 'M2',
        'gate': 'M3',
        'E.WID': 'M4',
        
        # Option 001 only
        'I.SWP': 'M5',
        'E.SWP': 'M6',
        'I.BUR': 'M7',
        'E.BUR': 'M8',
    }

    CONTROL_MODES = {
        'off': 'CT0',
        'FM': 'CT1',
        'AM': 'CT2',
        'PWM': 'CT3',
        'VCO': 'CT4',
    }

    TRIGGER_SLOPE = {
        'off': 'T0',
        'pos': 'T1',
        'neg': 'T2',
    }

    SHAPES = {
        'dc': 'W0',
        'sine': 'W1',
        'triangle': 'W2',
        'square': 'W3',
        'pulse': 'W4',
    }

    @property
    def operating_mode(self):
        """ The operating mode of the instrument.
        """
        raise NotImplementedError
    
    @operating_mode.setter
    def operating_mode(self, mode):
        mode_set = self.OPERATING_MODES[strict_discrete_set(mode, self.OPERATING_MODES)]
        self.write(mode_set)

    @property
    def control_mode(self):
        """ The control mode of the instrument.
        """
        raise NotImplementedError
    
    @control_mode.setter
    def control_mode(self, mode):
        mode_set = self.CONTROL_MODES[strict_discrete_set(mode, self.CONTROL_MODES)]
        self.write(mode_set)
    
    @property
    def trigger_slope(self):
        """ The trigger slope of the instrument.
        """
        raise NotImplementedError
    
    @trigger_slope.setter
    def trigger_slope(self, slope):
        slope_set = self.TRIGGER_SLOPE[strict_discrete_set(slope, self.TRIGGER_SLOPE)]
        self.write(slope_set)
    
    @property
    def shape(self):
        """ The shape of the waveform.
        """
        raise NotImplementedError
    
    @shape.setter
    def shape(self, shape):
        shape_set = self.SHAPES[strict_discrete_set(shape, self.SHAPES)]
        self.write(shape_set)
    
    @property
    def haversine(self):
        """ With triggered, gate or E.BUR operating mode selected and shape
        set to sine or triangle, this setting shifts the start phase of the
        waveform is -90°. As a result, haversine and havertriangle signals
        can be generated.
        """
        raise NotImplementedError
    
    @haversine.setter
    def haversine(self, haversine):
        haversine_set = int(haversine)
        haversine_cmd = "Z" + str(int(strict_discrete_set(haversine_set, [0, 1])))
        self.write(haversine_cmd)

    @property
    def frequency(self):
        """ A floating point property that controls the frequency of the
        output in Hz. The allowed frequency range is 1 mHz to 52.5 MHz.
        The resolution is 3 digits.
        """
        raise NotImplementedError
    
    @frequency.setter
    def frequency(self, frequency):
        frequency = float(strict_range(frequency, [1e-3, 52.5e6]))

        # Send frequency in mHz, Hz, kHz or MHz as appropriate
        if frequency < 1:
            freq_cmd = f'FRQ {frequency*1e3:.3g} MZ'  # mHz
        elif frequency < 1e3:
            freq_cmd = f'FRQ {frequency:.3g} HZ'
        elif frequency < 1e6:
            freq_cmd = f'FRQ {frequency*1e-3:.3g} KHZ'
        else:
            freq_cmd = f'FRQ {frequency*1e-6:.3g} MHZ'
        
        self.write(freq_cmd)

    @property
    def amplitude(self):
        """ A floating point property that controls the amplitude of the
        output in V. The allowed amplitude range is -10 V to 10 V.
        """
        raise NotImplementedError


