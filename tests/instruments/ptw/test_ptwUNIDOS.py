#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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
from pymeasure.test import expected_protocol
from pymeasure.instruments.ptw.ptwUNIDOS import ptwUNIDOS
from pymeasure.instruments.validators import truncated_range

# JSON and methods are tested with the device


def test_autostart_level():
    """Verify the communication of the autostart_level getter/setter."""
    with expected_protocol(
        ptwUNIDOS,
        [('ASL;LOW', 'ASL;LOW'),
         ('ASL', 'ASL;MEDIUM')],
    ) as inst:
        inst.autostart_level = 'LOW'
        assert inst.autostart_level == 'MEDIUM'


def test_id():
    """Verify the communication of the ID getter."""
    with expected_protocol(
        ptwUNIDOS,
        [('PTW', 'PTW;UNIDOS Tango;TM10052;1.2.4;A16')],
    ) as inst:
        assert inst.id == ['UNIDOS Tango', 'TM10052', '1.2.4', 'A16']


@pytest.mark.parametrize("it", (-3, 0, 600, 1E12))
def test_integration_time(it):
    """Verify the communication of the integration_time getter/setter."""
    it_t = truncated_range(it, [1, 3599999])
    with expected_protocol(
        ptwUNIDOS,
        [(f"IT;{it_t}", f"IT;{it_t}"),
         ('IT', f"IT;{it_t}")]
    ) as inst:
        inst.integration_time = it
        assert inst.integration_time == it_t


def test_mac_address():
    """Verify the communication of the mac address getter."""
    with expected_protocol(
        ptwUNIDOS,
        [('MAC', 'MAC;xx-xx-xx-xx-xx-xx')],
    ) as inst:
        assert inst.mac_address == 'xx-xx-xx-xx-xx-xx'


def test_meas_result():
    """Verify the communication of the meas_result getter."""
    with expected_protocol(
        ptwUNIDOS,
        [('MV', 'MV;RES;0.0;E-12;p;C;0.0;E-12;p;A;;0.0;ms;200;V;0x0'),
         ('MV', 'MV;RES;2.6;E-3;m;Gy;5.6;E-09;n;Gy;min;3000.0;ms;300.0;V;0x0')]
    ) as inst:
        assert inst.meas_result == {'status': 'RES',
                                    'charge': 0,
                                    'dose': 0,
                                    'current': 0,
                                    'doserate': 0,
                                    'timebase': '',
                                    'time': 0,
                                    'voltage': 200,
                                    'error': '0x0'}
        assert inst.meas_result == {'status': 'RES',
                                    'charge': 2.6E-3,
                                    'dose': 2.6E-3,
                                    'current': 5.6E-9,
                                    'doserate': 5.6E-9,
                                    'timebase': 'min',
                                    'time': 3000,
                                    'voltage': 300,
                                    'error': '0x0'}


def test_range():
    """Verify the communication of the range getter/setter."""
    with expected_protocol(
        ptwUNIDOS,
        [("RGE;MEDIUM", "RGE;MEDIUM"),
         ("RGE", "RGE;HIGH")],
    ) as inst:
        inst.range = 'MEDIUM'
        assert inst.range == 'HIGH'


def test_range_max():
    """Verify the communication of the range_max getter."""
    with expected_protocol(
        ptwUNIDOS,
        [("MVM", "MVM;MEDIUM;1.65;E-06;µ;Gy;min")]
    ) as inst:
        assert inst.range_max == {'range': 'MEDIUM',
                                  'current': 1.65e-06,
                                  'doserate': 1.65e-06,
                                  'timebase': 'min'}


def test_range_res():
    """Verify the communication of the range_res getter."""
    with expected_protocol(
        ptwUNIDOS,
        [("MVR", "MVR;MEDIUM;0.5;E-12;p;Gy;0.003;E-09;n;Gy;min")]
    ) as inst:
        assert inst.range_res == {'range': 'MEDIUM',
                                  'charge': 5e-13,
                                  'dose': 5e-13,
                                  'current': 3e-12,
                                  'doserate': 3e-12,
                                  'timebase': 'min'}


def test_selftest_result():
    """Verify the communication of the selftest_result getter."""
    with expected_protocol(
        ptwUNIDOS,
        [("ASS", "ASS;Passed;0;89000;Low; 136.6;E-12;p;C;Med; 1.500;E-09;n;C;High; 13.50;E-09;n;C")]
    ) as inst:
        assert inst.selftest_result == {'status': 'Passed',
                                        'time_remaining': 0,
                                        'time_total': 89000,
                                        'LOW': 1.366e-10,
                                        'MEDIUM': 1.5e-09,
                                        'HIGH': 1.35e-08}


def test_serial_number():
    """Verify the communication of the serial_number getter."""
    with expected_protocol(
        ptwUNIDOS,
        [("SER", "SER;123456")]
    ) as inst:
        assert inst.serial_number == 123456


def test_status():
    """Verify the communication of the status getter."""
    with expected_protocol(
        ptwUNIDOS,
        [("S", "S;RES")]
    ) as inst:
        assert inst.status == 'RES'


def test_tfi():
    """Verify the communication of the tfi getter."""
    with expected_protocol(
        ptwUNIDOS,
        [("TFI", "TFI;-")]
    ) as inst:
        assert inst.tfi == '-'


def test_use_autostart():
    """Verify the communication of the use_autostart getter/setter."""
    with expected_protocol(
        ptwUNIDOS,
        [("ASE;true", "ASE;true"),
         ("ASE", "ASE;false")]
    ) as inst:
        inst.use_autostart = True
        assert inst.use_autostart is False


def test_use_autoreset():
    """Verify the communication of the use_autoreset getter/setter."""
    with expected_protocol(
        ptwUNIDOS,
        [("ASR;true", "ASR;true"),
         ("ASR", "ASR;false")]
    ) as inst:
        inst.use_autoreset = True
        assert inst.use_autoreset is False


def test_use_electrical_units():
    """Verify the communication of the use_electrical_units getter/setter."""
    with expected_protocol(
        ptwUNIDOS,
        [("UEL;true", "UEL;true"),
         ("UEL", "UEL;false")]
    ) as inst:
        inst.use_electrical_units = True
        assert inst.use_electrical_units is False


@pytest.mark.parametrize("voltage", (-401, -13, 0, 400, 1E3))
def test_voltage(voltage):
    """Verify the communication of the voltage getter/setter."""
    voltage_t = truncated_range(voltage, [-400, 400])
    with expected_protocol(
        ptwUNIDOS,
        [(f"HV;{voltage_t}", f"HV;{voltage_t}"),
         ('HV', f"HV;{voltage_t}")]
    ) as inst:
        inst.voltage = voltage
        assert inst.voltage == voltage_t


def test_write_enabled():
    """Verify the communication of the write_enabled getter/setter."""
    with expected_protocol(
        ptwUNIDOS,
        [("TOK", "TOK;true"),
         ('TOK;0', "TOK;0;true"),
         ('TOK;1', "TOK;1;true"),
         ('TOK;1', "TOK;1;false")]
    ) as inst:
        inst.write_enabled = True
        inst.write_enabled = False
        assert inst.write_enabled is True
        assert inst.write_enabled is False


def test_zero_result():
    """Verify the communication of the zero_result getter."""
    with expected_protocol(
        ptwUNIDOS,
        [('NUS', 'NUS;Passed;0;82000')]
    ) as inst:
        assert inst.zero_result == {'status': 'Passed',
                                    'time_remaining': 0.0,
                                    'time_total': 82000.0}
