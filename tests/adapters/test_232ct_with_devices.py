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
from pymeasure.instruments.hp.hpsystempsu import HP6632A

pytest.skip('Only works with connected hardware', allow_module_level=True)


class Test_NI232CT_3478A_6632A:
    """Unit test class for NI GPIB-232CT and deivecs connected on GPIB (HP 3478A, HP6332A).

    To run this test the follow8ing reuirements need to be fulfilled:
        - A NI GPIB-232CT connected via a serial port to the computer running this test,
        - A HP 3748A connected by GPIB to the NI GPIB-232CT
        - A HP 6332A connecte by GBIB
        - test lead connection between the output of the 6332 to the input of 3478

    This test expects the RS232 communication speed as 38400 bps, the HP 3478A on
    GPIB address 23 and the HP 6332A on GPIB address 19.

    Use 'pytest -k test_232ct_with_devices --device-address "ASRL/dev/ttyUSB2::INSTR"'
    to run this test via the serial connection '/dev/ttyUSB2'


    """
    VOLTS = [1.0, 1.5, 2.2, 3.3, 4.7, 6.8, 10, 15]  # E6 series

    @pytest.fixture()
    def adapter(self, connected_device_address):
        Baud_Rate = 38400
        Instr_ID = 23  # GPIB Adress of the HP 3478A on the bus
        return NI_GPIB_232(connected_device_address,
                           address=Instr_ID,
                           baud_rate=Baud_Rate)

    @pytest.fixture()
    def adapter2(self, adapter):
        Instr_ID = 19  # GPIB Adress of the HP 6332A on the bus
        return adapter.gpib(Instr_ID)

    @pytest.fixture()
    def meter(self, adapter):
        return HP3478A(adapter)

    @pytest.fixture()
    def source(self, adapter2):
        return HP6632A(adapter2)

    @pytest.fixture
    def make_clean_instrument(self, meter):
        meter.adapter.clear()
        time.sleep(2)  # Wait 2s for the 3478A to collect itself
        return meter

    @pytest.fixture
    def make_clean_source(self, source):
        source.adapter.clear()
        source.output_enabled = False
        time.sleep(2)  # Wait 2s for the 3478A to collect itself
        return source

    @pytest.mark.parametrize('voltage', VOLTS)
    def test_voltage_reading(self, make_clean_instrument, make_clean_source, voltage):
        dmm = make_clean_instrument
        psu = make_clean_source
        psu.over_voltage_limit = 21  # 21 V over voltage limit
        psu.current = 0.1  # 100 mA current limit
        psu.output_enabled = False
        dmm.resolution = 3
        dmm.mode = "DCV"
        psu.voltage = voltage
        psu.output_enabled = True
        value = dmm.measure_DCV
        psu.output_enabled = False

        assert abs(value - voltage) <= 0.5
