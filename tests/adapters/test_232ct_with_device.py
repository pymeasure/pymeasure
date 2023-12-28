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

import time
import pytest


from pymeasure.adapters import NI_GPIB_232
from pymeasure.instruments.hp import HP3478A

pytest.skip('Only works with connected hardware', allow_module_level=True)


class Test_NI232CT_3478A:
    """Unit test class for NI GPIB-232CT and one deivce connected on GPIB (HP 3478A).

    To run this test the follow8ing reuirements need to be fulfilled:
        - A NI GPIB-232CT connected via a serial port to the computer running this test,
        - A HP 3748A connected by GPIB to the NI GPIB-232CT

    This test expects the RS232 communication speed as 38400 bps and the HP 3478A on
    GPIB address 23.

    Use 'pytest -k test_232ct_with_device --device-address "ASRL/dev/ttyUSB2::INSTR"'
    to run this test via the serial connection '/dev/ttyUSB2'


    """

    RESO = [3, 4, 5]
    MODES = ['DCV', 'ACV', 'DCI', 'ACI', 'R2W', 'R4W']

    # adapter = NI_GPIB_232(connected_device_address, address=Instr_ID, baud_rate=Baud_Rate)

    @pytest.fixture()
    def adapter(self, connected_device_address):
        Baud_Rate = 38400
        Instr_ID = 23  # GPIB Adress of the HP 3478A on the bus
        return NI_GPIB_232(connected_device_address,
                           address=Instr_ID,
                           baud_rate=Baud_Rate)

    @pytest.fixture()
    def meter(self, adapter):
        return HP3478A(adapter)

    @pytest.fixture
    def make_clean_instrument(self, meter):
        meter.adapter.clear()
        time.sleep(2)  # Wait 2s for the 3478A to collect itself
        return meter

    @pytest.mark.parametrize('res', RESO)
    def test_resolution(self, make_clean_instrument, res):
        dmm = make_clean_instrument
        dmm.resolution = res
        assert dmm.resolution == res

    @pytest.mark.parametrize('mode', MODES)
    def test_mode(self, make_clean_instrument, mode):
        dmm = make_clean_instrument
        dmm.mode = mode
        assert dmm.mode == mode

    def test_voltage_reading(self, make_clean_instrument):
        dmm = make_clean_instrument
        dmm.resolution = 3
        dmm.mode = "DCV"
        value = dmm.measure_DCV
        assert isinstance(value, float)

    def test_current_reading(self, make_clean_instrument):
        dmm = make_clean_instrument
        dmm.resolution = 3
        dmm.mode = "DCI"
        value = dmm.measure_DCI
        assert isinstance(value, float)
