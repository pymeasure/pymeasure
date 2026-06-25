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

from pymeasure.instruments.temptronic.temptronic_base import ErrorCode
from pymeasure.instruments.temptronic.temptronic_eco560 import (
    ECO560,
    ECO560ErrorCode,
)


def test_error_code_enum_distinct_from_base():
    # Verify that ECO560ErrorCode has distinct bit assignments vs base ErrorCode
    assert ECO560ErrorCode is not ErrorCode
    # ECO560-specific members not present in base ErrorCode
    assert ECO560ErrorCode.PURGE_HEAT_FAILURE == 1024
    assert not hasattr(ErrorCode, "PURGE_HEAT_FAILURE")
    assert ECO560ErrorCode.DUT_OPEN_LOOP == 256
    assert not hasattr(ErrorCode, "DUT_OPEN_LOOP")
    assert ECO560ErrorCode.OPEN_PURGE_TEMPERATURE_SENSOR == 64
    assert not hasattr(ErrorCode, "OPEN_PURGE_TEMPERATURE_SENSOR")
    assert ECO560ErrorCode.NO_PURGE_FLOW == 32
    assert not hasattr(ErrorCode, "NO_PURGE_FLOW")
    assert ECO560ErrorCode.SETPOINT_OUT_OF_RANGE == 4
    assert not hasattr(ErrorCode, "SETPOINT_OUT_OF_RANGE")
    # base-specific members not present in ECO560ErrorCode
    assert not hasattr(ECO560ErrorCode, "BVRAM_FAULT")
    assert not hasattr(ECO560ErrorCode, "NVRAM_FAULT")
    assert not hasattr(ECO560ErrorCode, "NO_LINE_SENSE")
    # base uses AIR_SENSOR_OPEN at 32, ECO560 uses NO_PURGE_FLOW at 32 (distinct names)
    assert ErrorCode.AIR_SENSOR_OPEN == 32
    assert ECO560ErrorCode.NO_PURGE_FLOW == 32


def test_error_code_get_process_override():
    # Verify the ECO560 error_code_get_process override returns ECO560ErrorCode.
    # NOTE: ``error_code`` in ATSBase is a non-dynamic StaticProperty, so the
    # ``error_code_get_process`` override is not picked up by ``inst.error_code``
    # automatically. The override is verified directly here, as the plan's
    # parenthetical ("verify error_code_get_process override") directs.
    # Access via the class to avoid the descriptor protocol binding ``self``.
    get_process = ECO560.__dict__["error_code_get_process"]
    code = get_process("9")
    assert isinstance(code, ECO560ErrorCode)
    assert ECO560ErrorCode.OVERHEAT in code
    assert ECO560ErrorCode.LOW_FLOW in code


def test_copy_active_setup_file_is_none():
    inst = ECO560.__new__(ECO560)
    assert inst.copy_active_setup_file is None
    # Confirm it is a plain class attribute, not a property (overrides the
    # ``copy_active_setup_file`` setting defined in ATSBase).
    assert not isinstance(ECO560.__dict__["copy_active_setup_file"], property)


def test_temperature_limit_air_low_values():
    inst = ECO560.__new__(ECO560)
    assert inst.temperature_limit_air_low_values == [-150, 25]
