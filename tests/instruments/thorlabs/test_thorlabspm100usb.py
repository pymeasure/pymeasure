#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

from pymeasure.test import expected_protocol
from pymeasure.instruments.thorlabs.thorlabspm100usb import ThorlabsPM100USB

PM100D_INIT_COMMS = ("SYST:SENSOR:IDN?", "S130C,210921324,21-SEP-2021,1,3,33")
PM100D2_INIT_COMMS = ("SYST:SENSOR:IDN?", '"S130C","210921324","21-SEP-2021",1,3,2147484069')


def test_init():
    for protocol in [PM100D_INIT_COMMS, PM100D2_INIT_COMMS]:
        with expected_protocol(ThorlabsPM100USB, [protocol]) as inst:
            assert inst.sensor_name == "S130C"
            assert inst.sensor_sn == "210921324"
            assert inst.sensor_cal_msg == "21-SEP-2021"
            assert inst.sensor_type == 1
            assert inst.sensor_subtype == 3
            assert inst.flags
            assert inst.is_power_sensor
            assert not inst.is_energy_sensor
