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
from pymeasure.instruments.hp import HP3478A

VALID_CAL_DATA = [
        0, 0, 0, 0, 3, 0, 8, 2, 15, 4, 4, 0, 13, 11, 0, 0,
        0, 0, 3, 3, 2, 15, 5, 3, 0, 14, 0, 0, 0, 0, 0, 0,
        3, 2, 15, 4, 0, 0, 14, 7, 9, 9, 9, 9, 9, 7, 2, 0,
        15, 3, 12, 10, 11, 9, 9, 9, 9, 9, 9, 2, 0, 14, 15, 14,
        9, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 15, 9,
        9, 8, 6, 0, 9, 2, 14, 14, 0, 12, 10, 12, 9, 9, 9, 9,
        9, 5, 1, 12, 0, 5, 14, 10, 13, 9, 9, 9, 9, 9, 8, 1,
        12, 1, 15, 1, 10, 12, 0, 0, 0, 0, 0, 0, 1, 12, 15, 3,
        0, 14, 0, 9, 9, 9, 9, 9, 9, 1, 12, 13, 2, 14, 9, 15,
        9, 9, 9, 9, 9, 9, 1, 12, 13, 4, 2, 10, 9, 9, 9, 9,
        9, 9, 9, 1, 12, 14, 12, 13, 9, 5, 9, 9, 9, 9, 9, 9,
        1, 12, 2, 1, 15, 10, 10, 0, 0, 0, 0, 4, 2, 3, 0, 0,
        3, 12, 14, 7, 0, 0, 0, 0, 0, 4, 3, 0, 1, 12, 3, 14,
        8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 15, 9, 9,
        8, 6, 0, 9, 3, 14, 3, 1, 1, 12, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0
    ]


def convert_cal_data_to_cal_read_xfers(cal_data):
    # Convert cal_data into 256 single byte 'W' read operations.
    cal_read_xfers = []
    for addr, value in enumerate(cal_data):
        cal_read_xfers.append([bytes([ord('W'), addr]), bytes([value+64])])

    return cal_read_xfers


def convert_cal_data_to_cal_write_xfers(cal_data):
    # Convert cal_data into 256 single byte 'X' write operations.
    cal_write_xfers = []
    for addr, value in enumerate(cal_data):
        cal_write_xfers.append([bytes([ord('X'), addr, value]), None])

    return cal_write_xfers

# ============================================================
# TESTS
# ============================================================


def test_calibration_enabled():
    with expected_protocol(
            HP3478A,
            [
                (b"B", b'\x00\x20\x00\x00\x00'),        # cal_enable bit is set
                (b"B", b'\x00\x00\x00\x00\x00')
            ],
    ) as instr:
        assert instr.calibration_enabled
        assert not instr.calibration_enabled


def test_calibration_data_getter():
    cal_read_xfers = convert_cal_data_to_cal_read_xfers(VALID_CAL_DATA)

    with expected_protocol(
            HP3478A,
            cal_read_xfers
    ) as instr:
        cal_data = instr.calibration_data
        assert instr.verify_calibration_data(cal_data)


def test_calibration_data_setter_cal_disabled():
    with pytest.raises(Exception, match="CAL ENABLE switch not set to ON"):
        with expected_protocol(
                HP3478A,
                # cal_enable cleared. As a result there won't be calibration
                # write transactions.
                [
                    (b"B", b'\x00\x00\x00\x00\x00'),
                ]
        ) as instr:
            instr.calibration_data = VALID_CAL_DATA


def test_calibration_data_setter_pass():
    valid_cal_write_xfers = convert_cal_data_to_cal_write_xfers(VALID_CAL_DATA)

    with expected_protocol(
            HP3478A,
            # setter pass
            [
                (b"B", b'\x00\x20\x00\x00\x00'),
            ] + valid_cal_write_xfers
    ) as instr:
        # Writing correct data
        instr.calibration_data = VALID_CAL_DATA


def test_calibration_data_setter_invalid_data():
    with pytest.raises(ValueError, match="cal_data verification fail"):
        with expected_protocol(
                HP3478A,
                # setter fail due to invalid data
                [
                    (b"B", b'\x00\x20\x00\x00\x00'),
                ]
        ) as instr:
            # Assigning invalid data results in an Exception without data writes
            valid_cal_data_corrupt = VALID_CAL_DATA.copy()
            valid_cal_data_corrupt[1] = 1
            instr.calibration_data = valid_cal_data_corrupt


def test_write_calibration_data():
    invalid_cal_data = VALID_CAL_DATA.copy()
    invalid_cal_data[1] = 1
    invalid_cal_write_xfers = convert_cal_data_to_cal_write_xfers(invalid_cal_data)

    with expected_protocol(
            HP3478A,
            invalid_cal_write_xfers
    ) as instr:
        # Writing invalid data with verification bypass
        instr.write_calibration_data(invalid_cal_data, verify_calibration_data=False)
