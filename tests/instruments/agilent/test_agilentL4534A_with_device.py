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

import pytest
from pymeasure.instruments.agilent.agilentL4534A import AgilentL4534A
from pyvisa.errors import VisaIOError
from pymeasure.units import ureg

pytest.skip('Only work with connected hardware', allow_module_level=True)

class TestAgilentL4534A:
    """
    Unit tests for TestAgilentL4534A class.

    This test suite, needs the following setup to work properly:
        - A TestAgilentL4534A device should be connected to the computer;
        - The device's address must be set in the RESOURCE constant.
    """

    ###############################################################
    # Agilent34450A device goes here:
    RESOURCE = "TCPIP::169.254.45.32::INSTR"
    ###############################################################

    DIG = AgilentL4534A(RESOURCE)

    ############
    # FIXTURES #
    ############
    @pytest.fixture
    def make_resetted_dig(self) -> AgilentL4534A:
        self.DIG.reset()
        self.DIG.clear()
        return self.DIG
    
    def test_idn(self, make_resetted_dig: AgilentL4534A):
        dig = make_resetted_dig
        assert dig.id.startswith('Agilent Technologies,L4534A')

    def test_selftest(self, make_resetted_dig: AgilentL4534A):
        dig = make_resetted_dig
        test = dig.tst(45)
        assert int(test) == 0, dig.check_errors()
        dig.clear_display()
        
    def test_disp(self, make_resetted_dig: AgilentL4534A):
        dig = make_resetted_dig
        dig.display = 'PyMeasure'
        assert dig.display == 'PyMeasure'
        dig.clear_display()
        assert dig.display == ''

    def test_acquisition_config(self, make_resetted_dig: AgilentL4534A):
        dig = make_resetted_dig
        settings = {
            'sample_rate': ureg.Quantity(1000000, ureg.Hz),
            'samples_per_record': int(1024),
            'pre_trig_samples': int(4),
            'num_records': int(1),
            'trigger_holdoff': ureg.Quantity(0.1, ureg.s),
            'trigger_delay': ureg.Quantity(0, ureg.s)
        }
        dig.acquisition = settings
        assert dig.acquisition == settings
    
    def test_channel_config(self, make_resetted_dig: AgilentL4534A):
        dig = make_resetted_dig
        settings = {
            'range': 0.5 * ureg.V,
            'coupling': 'DC',
            'filter': 'LP_2_MHZ'
        }
        for ch in range(1,5):
            dig.channels[ch].config = settings
            assert dig.channels[ch].config == settings

    def test_measure(self, make_resetted_dig: AgilentL4534A):
        dig = make_resetted_dig
        # Set acquisition settings
        settings = {
            'sample_rate': ureg.Quantity(1000000, ureg.Hz),
            'samples_per_record': int(1024),
            'pre_trig_samples': int(0),
            'num_records': int(1),
            'trigger_holdoff': ureg.Quantity(0, ureg.s),
            'trigger_delay': ureg.Quantity(0, ureg.s)
        }
        dig.acquisition = settings
        # Prepare to capture
        dig.init()
        # Wait for capture to complete
        assert int(dig.complete) == 1
        # Read back both processed and raw results for each channel and check the data looks as is expected
        for ch in range(1,5):
            result = dig.channels[ch].voltage
            assert result.m.dtype == np.float32
            assert result.size == 1024
            result = dig.channels[ch].adc
            assert result.size == 1024
            assert result.dtype == np.int16
        

    