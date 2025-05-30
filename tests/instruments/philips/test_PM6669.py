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

from pymeasure.test import expected_protocol
from pymeasure.instruments.philips.PM6669 import PM6669, Functions


def test_init():
    with expected_protocol(
        PM6669,
        [(b"EOI ON", None), (b"FRUN OFF", None)],
    ):
        pass  # Verify the expected communication.


def test_measuring_function():
    with expected_protocol(
        PM6669,
        [
            (b"EOI ON", None),
            (b"FRUN OFF", None),
            (b"FREQ   A", None),
            (b"FNC?", "FREQ   A\n"),
            (b"FREQ   B", None),
            (b"FNC?", "FREQ   B\n"),
        ],
    ) as inst:
        inst.measuring_function = Functions.FREQUENCY_A
        assert inst.measuring_function == Functions.FREQUENCY_A
        inst.measuring_function = Functions.FREQUENCY_B
        assert inst.measuring_function == Functions.FREQUENCY_B


def test_measurement_time():
    with expected_protocol(
        PM6669,
        [
            (b"EOI ON", None),
            (b"FRUN OFF", None),
            (b"MTIME 1", None),
            (b"MEAC?", b"MTIME 1.00,FRUN OFF\nTOUT 25.5\n"),
            (b"MTIME 10", None),
            (b"MEAC?", b"MTIME 10.00,FRUN OFF\nTOUT 25.5\n"),
        ],
    ) as inst:
        inst.measurement_time = 1
        assert inst.measurement_time == 1
        inst.measurement_time = 10
        assert inst.measurement_time == 10


def test_freerun_enabled_setter():
    with expected_protocol(
            PM6669,
            [(b'EOI ON', None),
             (b"FRUN OFF", None),
             (b'FRUN ON', None)],
    ) as inst:
        inst.freerun_enabled = True


def test_id_getter():
    with expected_protocol(
            PM6669,
            [(b'EOI ON', None),
             (b"FRUN OFF", None),
             (b'ID?', b'PM6669/416/32\n')],
    ) as inst:
        assert inst.id == 'PM6669/416/32'


def test_measurement_settings_getter():
    with expected_protocol(
            PM6669,
            [(b'EOI ON', None),
             (b"FRUN OFF", None),
             (b'MEAC?', b'MTIME 10.00,FRUN OFF\nTOUT 00.0\n')],
    ) as inst:
        assert inst.measurement_settings == ['MTIME 10.00', 'FRUN OFF', 'TOUT 00.0']
