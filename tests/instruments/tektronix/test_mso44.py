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

from pymeasure.test import expected_protocol
from pymeasure.instruments.tektronix.mso44 import MSO44, MeasurementType, Measurement


def test_id():
    with expected_protocol(
        MSO44,
        [("*IDN?", "TEKTRONIX,MSO44,C000000,1.0.0")]
    ) as inst:
        assert inst.id == "TEKTRONIX,MSO44,C000000,1.0.0"


def test_channel_coupling():
    with expected_protocol(
        MSO44,
        [
            ("CH1:COUPling?", "DC"),
            ("CH1:COUPling AC", None),
            ("CH1:COUPling?", "AC")
        ]
    ) as inst:
        assert inst.ch1.coupling == "DC"
        inst.ch1.coupling = "AC"
        assert inst.ch1.coupling == "AC"


def test_add_measurement():
    with expected_protocol(
        MSO44,
        [
            ("MEASUrement:DELETEALL", None),
            ("MEASUrement:LIST?", "\n"),
            ("MEASUrement:LIST?", "\n"),
            ("MEASUrement:ADDMEAS FREQUENCY", None),
            ("MEASUrement:MEAS1:SOUrce CH1", None),
        ]
    ) as inst:
        inst.delete_all_measurements()
        meas_count = inst.get_measurement_count()
        assert meas_count == 0
        meas = inst.add_measurement(MeasurementType.FREQUENCY, "CH1")
        assert isinstance(meas, Measurement)


def test_add_phase_measurement():
    with expected_protocol(
        MSO44,
        [
            ("MEASUrement:DELETEALL", None),
            ("MEASUrement:LIST?", "\n"),
            ("MEASUrement:ADDMEAS PHASE", None),
            ("MEASUrement:MEAS1:SOUrce1 CH1", None),
            ("MEASUrement:MEAS1:SOUrce2 CH2", None),
        ]
    ) as inst:
        inst.delete_all_measurements()
        meas = inst.add_measurement(MeasurementType.PHASE, "CH1", "CH2")
        assert isinstance(meas, Measurement)
