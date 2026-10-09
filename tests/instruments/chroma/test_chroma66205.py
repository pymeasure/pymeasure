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
from pymeasure.instruments.chroma import Chroma66205


def test_init():
    with expected_protocol(
            Chroma66205,
            [],
    ):
        pass  # Verify the expected communication.


def test_charge_ah_getter():
    with expected_protocol(
            Chroma66205,
            [(b'FETCH? AH', b'-0.0000010\n')],
    ) as inst:
        assert inst.charge_ah == -1e-06


def test_current_dc_getter():
    with expected_protocol(
            Chroma66205,
            [(b'FETCH? IDC', b'-0.0040322\n')],
    ) as inst:
        assert inst.current_dc == -0.0040322


def test_current_peak_neg_getter():
    with expected_protocol(
            Chroma66205,
            [(b'FETCH? IPK-', b'-6.3593586\n')],
    ) as inst:
        assert inst.current_peak_neg == -6.3593586


def test_current_peak_pos_getter():
    with expected_protocol(
            Chroma66205,
            [(b'FETCH? IPK+', b'6.2793033\n')],
    ) as inst:
        assert inst.current_peak_pos == 6.2793033


def test_current_rms_getter():
    with expected_protocol(
            Chroma66205,
            [(b'FETCH? I', b'1.8464582\n')],
    ) as inst:
        assert inst.current_rms == 1.8464582


def test_energy_time_getter():
    with expected_protocol(
            Chroma66205,
            [(b'CONF:ENERGY:TIME?', b'1\n')],
    ) as inst:
        assert inst.energy_time == 1.0


def test_energy_wh_getter():
    with expected_protocol(
            Chroma66205,
            [(b'FETCH? WH', b'-0.0121532\n')],
    ) as inst:
        assert inst.energy_wh == -0.0121532


def test_id_getter():
    with expected_protocol(
            Chroma66205,
            [(b'*IDN?', b'Chroma ATE,66205,662050003223,1.03,1.02,1.00\n')],
    ) as inst:
        assert inst.id == 'Chroma ATE,66205,662050003223,1.03,1.02,1.00'


def test_mode_getter():
    with expected_protocol(
            Chroma66205,
            [(b'CONF:MEAS:MODE?', b'RMS\n')],
    ) as inst:
        assert inst.mode == 'RMS'


def test_phase_getter():
    with expected_protocol(
            Chroma66205,
            [(b'FETCH? DEG', b'121.8150996\n')],
    ) as inst:
        assert inst.phase == 121.8150996


def test_power_apparent_getter():
    with expected_protocol(
            Chroma66205,
            [(b'FETCH? VA', b'110.6944053\n')],
    ) as inst:
        assert inst.power_apparent == 110.6944053


def test_power_dc_getter():
    with expected_protocol(
            Chroma66205,
            [(b'FETCH? WDC', b'-0.0000209\n')],
    ) as inst:
        assert inst.power_dc == -2.09e-05


def test_power_reactive_getter():
    with expected_protocol(
            Chroma66205,
            [(b'FETCH? VAR', b'94.0580139\n')],
    ) as inst:
        assert inst.power_reactive == 94.0580139


def test_power_real_getter():
    with expected_protocol(
            Chroma66205,
            [(b'FETCH? W', b'-58.3332768\n')],
    ) as inst:
        assert inst.power_real == -58.3332768


def test_voltage_dc_getter():
    with expected_protocol(
            Chroma66205,
            [(b'FETCH? VDC', b'0.0051855\n')],
    ) as inst:
        assert inst.voltage_dc == 0.0051855


def test_voltage_peak_neg_getter():
    with expected_protocol(
            Chroma66205,
            [(b'FETCH? VPK-', b'-84.8153858\n')],
    ) as inst:
        assert inst.voltage_peak_neg == -84.8153858


def test_voltage_peak_pos_getter():
    with expected_protocol(
            Chroma66205,
            [(b'FETCH? VPK+', b'84.8395147\n')],
    ) as inst:
        assert inst.voltage_peak_pos == 84.8395147


def test_voltage_rms_getter():
    with expected_protocol(
            Chroma66205,
            [(b'FETCH? V', b'59.9339914\n')],
    ) as inst:
        assert inst.voltage_rms == 59.9339914
