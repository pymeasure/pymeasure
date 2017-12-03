#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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

import pytest
from unittest import mock

import re

from pymeasure.instruments.srs import SR830

class TestSR830:
    """
    SR830 test suite.

    Does not test commands provided by Instrument.measurement or
    Instrument.control.

    Currently does not test (but should):

    * auto_offset
    * get_scaling
    * set_scaling
    * output_conversion
    * sample_frequency (property, get/set)
    * acquire_on_trigger
    * quick_range
    * buffer_count
    * fill_buffer
    * buffer_measure
    * start_buffer
    * wait_for_buffer
    * get_buffer
    """
    @pytest.mark.parametrize("vals,expect", [
        (['X', 'Y'], '1,2'),
        (['R', 'THETA'], '3,4'),
        (['AUX1', 'AUX2', 'AUX3'], '5,6,7'),
        (['X', 'R', 'AUX1', 'AUX2'], '1,3,5,6'),
        (['AUX1', 'AUX2', 'AUX3', 'AUX4', 'X'], '5,6,7,8,1'),
        (['AUX1', 'AUX2', 'AUX3', 'FREQ', 'CH1', 'CH2'], '5,6,7,9,10,11'),
    ])
    def test_measure_multiple(self, fake_adapter, vals, expect):
        expect_expr = 'SNAP\s*\?\s*' + expect.replace(',', '\s*,\s*') + '$'
        dut = SR830(fake_adapter)

        with mock.patch.object(dut, 'values',
                return_value=list(range(0, len(vals)))) as mock_values:
            output = dut.measure_multiple(vals)

            # verify message sent to instrument
            print(repr(expect_expr))
            print(repr(mock_values.call_args))
            assert re.match(expect_expr, mock_values.call_args[0][0]) is not None

            # verify the zipping of values
            assert output == dict(zip(vals, mock_values.return_value))


    @pytest.mark.parametrize("vals", [
        ['X'], # must request >= 2 values
        ['X', 'Y', 'R', 'THETA', 'AUX1', 'AUX2', 'AUX3'], # must req <= 6 vals
        ['X', 'ASDF'], # unknown name
        ['X', 6] # another invalid type
    ])
    def test_measure_multiple_with_value_errors(self, fake_adapter, vals):
        dut = SR830(fake_adapter)

        with mock.patch.object(dut, 'values',
                return_value=list(range(0, len(vals)))) as mock_values:
            with pytest.raises(ValueError):
                dut.measure_multiple(vals)
            mock_values.assert_not_called()


    def test_measure_multiple_with_invalid_argument_type(self, fake_adapter):
        dut = SR830(fake_adapter)

        with mock.patch.object(dut, 'values') as mock_values:
            with pytest.raises(TypeError):
                dut.measure_multiple(6)
            mock_values.assert_not_called()


    def test_enable_lia_status_nones(self, fake_adapter):
        dut = SR830(fake_adapter)
        fake_adapter.read() # clear the buffer of any init commands
        dut.enable_lia_status(input_=None) # rest implicit nones
        assert not fake_adapter.read()


    def test_enable_lia_status(self, fake_scpi_adapter):
        liae_calls = []
        def liae_handler(args=tuple(), query=False):
            if not query:
                liae_calls.append(args)
            else:
                return liae_calls[-1]
        fake_scpi_adapter.set_handler('LIAE', liae_handler)
        dut = SR830(fake_scpi_adapter)
        dut.enable_lia_status(input_=True, filter_=True, output=True,
            unlock=False, time_constant=True)

        assert len(liae_calls) == 5
        assert (0,1) in liae_calls
        assert (1,1) in liae_calls
        assert (2,1) in liae_calls
        assert (3,0) in liae_calls
        assert (5,1) in liae_calls
