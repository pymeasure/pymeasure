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

from pymeasure.instruments.lakeshore.lakeshore211 import LakeShore211


def test_init():
    with expected_protocol(
            LakeShore211,
            [],
    ):
        pass  # Verify the expected communication.


def test_temp_kelvin():
    with expected_protocol(
            LakeShore211,
            [(b"KRDG?", b"27.1")],
    ) as instr:
        assert instr.temperature_kelvin == 27.1


def test_temp_celsius():
    with expected_protocol(
            LakeShore211,
            [(b"CRDG?", b"27.1")],
    ) as instr:
        assert instr.temperature_celsius == 27.1


def test_set_analog():
    with expected_protocol(
            LakeShore211,
            [(b"ANALOG 0,1", None),
             (b"ANALOG?", b"0,1")],
    ) as instr:
        instr.analog_configuration = (0, 1)
        assert instr.analog_configuration == (0, 1)


def test_set_display():
    with expected_protocol(
            LakeShore211,
            [(b"DISPFLD 1", None),
             (b"DISPFLD?", b"1")],
    ) as instr:
        instr.display_units = 'celsius'
        assert instr.display_units == 'celsius'


def test_alarms():
    with expected_protocol(
            LakeShore211,
            [(b"ALARM?", b"0,+000.0,+000.0,+00.0,0\r\n"),
             (b"ALARM 1,300,10,5,0", None),
             (b"ALARM?", b"1,+300.0,+010.0,+05.0,0\r\n")
             ],
    ) as instr:
        assert instr.get_alarm_status() == {'on': 0, 'high_value': 0.0, 'low_value': 0.0,
                                            'deadband': 0.0, 'latch': 0}
        instr.configure_alarm(on=True, high_value=300, low_value=10, deadband=5, latch=False)
        assert instr.get_alarm_status() == {'on': 1, 'high_value': 300.0, 'low_value': 10.0,
                                            'deadband': 5.0, 'latch': 0}


def test_relays():
    with expected_protocol(
            LakeShore211,
            [(b"RELAY? 1", b"0\r\n"),
             (b"RELAY 1 2", None),
             (b"RELAY? 1", b"2\r\n")
             ],
    ) as instr:
        assert instr.get_relay_mode(1) == 0
        instr.configure_relay(1, 2)
        assert instr.get_relay_mode(1) == 2
