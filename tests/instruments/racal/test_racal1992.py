#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from pymeasure.instruments.racal import Racal1992

# ============================================================
# TESTS
# ============================================================


def test_self_check():
    with expected_protocol(
            Racal1992,
            [
                (' CK', 'CK+010.00000000E+06'),
            ],
    ) as instr:
        instr.operating_mode = 'self_check'
        assert instr.measured_value == 10000000.0


def test_frequency_a():
    with expected_protocol(
            Racal1992,
            [
                (' FA', 'FA+010.00000000E+06'),
            ],
    ) as instr:
        instr.operating_mode = 'frequency_a'
        assert instr.measured_value == 10000000.0


def test_period_a():
    with expected_protocol(
            Racal1992,
            [
                (' PA', 'PA+000100.00000E-09'),
            ],
    ) as instr:
        instr.operating_mode = 'period_a'
        assert instr.measured_value == 100e-9


def test_interval_a_to_b():
    with expected_protocol(
            Racal1992,
            [
                (' TI', 'TI+00000000046.E-09'),
            ],
    ) as instr:
        instr.operating_mode = 'interval_a_to_b'
        assert instr.measured_value == 46e-9


def test_total_a_by_b():
    with expected_protocol(
            Racal1992,
            [
                (' TA', 'TA+00000000001.E+00'),
            ],
    ) as instr:
        instr.operating_mode = 'total_a_by_b'
        assert instr.measured_value == 1


def test_phase_a_rel_b():
    with expected_protocol(
            Racal1992,
            [
                (' PH', 'PH+00000000164.E+00'),
            ],
    ) as instr:
        instr.operating_mode = 'phase_a_rel_b'
        assert instr.measured_value == 164


def test_ratio_a_to_b():
    with expected_protocol(
            Racal1992,
            [
                (' RA', 'RA+00001.000000E+00'),
            ],
    ) as instr:
        instr.operating_mode = 'ratio_a_to_b'
        assert instr.measured_value == 1.0


def test_ratio_c_to_b():
    with expected_protocol(
            Racal1992,
            [
                (' RC', 'RC+00001.000000E+00'),
            ],
    ) as instr:
        instr.operating_mode = 'ratio_c_to_b'
        assert instr.measured_value == 1.0


def test_frequency_c():
    with expected_protocol(
            Racal1992,
            [
                (' FC', 'FC+010.00000000E+06'),
            ],
    ) as instr:
        instr.operating_mode = 'frequency_c'
        assert instr.measured_value == 10000000.0


def test_resolution():
    with expected_protocol(
            Racal1992,
            [
                (' SRS 10', None),
                (' RRS', 'RS+00000000010.E+00')
            ],
    ) as instr:
        instr.resolution = 10
        assert instr.resolution == 10


def test_channel_a_settings():
    with expected_protocol(
            Racal1992,
            [
                (' AAC AAD AAU ALI APS AFE SLA 1.5', None),
                (' ADC AAE AMN AHI ANS AFD', None),
            ],
    ) as instr:
        instr.channel_settings(
            'A',
            coupling='AC',
            attenuation='X1',
            trigger='auto',
            impedance='50',
            slope='pos',
            filtering=True,
            trigger_level=1.5
        )
        instr.channel_settings(
            'A',
            coupling='DC',
            attenuation='X10',
            trigger='manual',
            impedance='1M',
            slope='neg',
            filtering=False,
        )


def test_channel_b_settings():
    with expected_protocol(
            Racal1992,
            [
                (' BAC BAD BAU BLI BPS BCS SLB 1.5', None),
                (' BDC BAE BMN BHI BNS BCC', None),
            ],
    ) as instr:
        instr.channel_settings(
            'B',
            coupling='AC',
            attenuation='X1',
            trigger='auto',
            impedance='50',
            slope='pos',
            input_select='separate',
            trigger_level=1.5
        )
        instr.channel_settings(
            'B',
            coupling='DC',
            attenuation='X10',
            trigger='manual',
            impedance='1M',
            slope='neg',
            input_select='common',
        )


def test_preset():
    with expected_protocol(
            Racal1992,
            [
                (' IP', 'FA+0010.0000000E+06'),
            ],
    ) as instr:
        instr.preset()
        assert instr.measured_value == 10000000.0


def test_reset_measurement():
    with expected_protocol(
            Racal1992,
            [
                (' RE', 'FA+0010.0000000E+06'),
            ],
    ) as instr:
        instr.reset_measurement()
        assert instr.measured_value == 10000000.0


def test_software_version():
    with expected_protocol(
            Racal1992,
            [
                (' RMS', 'MS+00085720404.E+00'),
            ],
    ) as instr:
        assert instr.software_version == 85720404


def test_gpib_software_version():
    with expected_protocol(
            Racal1992,
            [
                (' RGS', 'GS+0000000003.1E+00'),
            ],
    ) as instr:
        assert instr.gpib_software_version == 3.1


def test_math_x():
    with expected_protocol(
            Racal1992,
            [
                (' SMX 1.000000', None),
                (' RMX', 'MX+001.00000000E+00')
            ],
    ) as instr:
        instr.math_x = 1.0
        assert instr.math_x == 1.0


def test_math_z():
    with expected_protocol(
            Racal1992,
            [
                (' SMZ 1.000000', None),
                (' RMZ', 'MZ+001.00000000E+00')
            ],
    ) as instr:
        instr.math_z = 1.0
        assert instr.math_z == 1.0


def test_math_mode():
    with expected_protocol(
            Racal1992,
            [
                (' ME', None),
                (' MD', None),
            ],
    ) as instr:
        instr.math_mode = True
        instr.math_mode = False


def test_device_type():
    with expected_protocol(
            Racal1992,
            [
                (' RUT', 'UT+00000001992.E+00')
            ],
    ) as instr:
        assert instr.device_type == 1992


def test_trigger_level():
    with expected_protocol(
            Racal1992,
            [
                (' SLA 1.500000', None),
                (' SLB 1.500000', None),
                (' RLA', 'LA+000000001.50E+00'),
                (' RLB', 'LB+000000001.50E+00'),
            ],
    ) as instr:
        instr.trigger_level_a = 1.5
        instr.trigger_level_b = 1.5
        assert instr.trigger_level_a == 1.5
        assert instr.trigger_level_b == 1.5


def test_delay_enable():
    with expected_protocol(
            Racal1992,
            [
                (' DE', None),
                (' DD', None),
            ],
    ) as instr:
        instr.delay_enable = True
        instr.delay_enable = False


def test_delay_time():
    with expected_protocol(
            Racal1992,
            [
                (' SDT 1.500000', None),
                (' RDT', 'DT+000000001.50E+00'),
            ],
    ) as instr:
        instr.delay_time = 1.5
        assert instr.delay_time == 1.5


def test_special_function_enable():
    with expected_protocol(
            Racal1992,
            [
                (' SFE', None),
                (' SFD', None),
            ],
    ) as instr:
        instr.special_function_enable = True
        instr.special_function_enable = False
