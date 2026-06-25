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
    error_code_get_process,
)
from pymeasure.test import expected_protocol


def test_error_code_enum_distinct_from_base():
    """ECO560 uses its own enum with model-specific members.

    The individual bit values rest on the enum definition; the
    protocol-level mapping (including the base-vs-ECO560 collision at bit 32:
    AIR_SENSOR_OPEN for the base, NO_PURGE_FLOW for the ECO-560) is pinned by
    ``test_error_code_protocol_response``.
    """
    assert ECO560ErrorCode is not ErrorCode
    # ECO560-specific member that the base enum does not define
    assert hasattr(ECO560ErrorCode, "PURGE_HEAT_FAILURE")
    assert not hasattr(ErrorCode, "PURGE_HEAT_FAILURE")
    # base member that the ECO560 enum does not need
    assert not hasattr(ECO560ErrorCode, "BVRAM_FAULT")


def test_error_code_get_process_override():
    # Verify the ECO560 error-code conversion returns an ECO560ErrorCode.
    # ATSBase's ``error_code`` property is a StaticProperty (dynamic=False),
    # so the ``get_process`` of an inherited property cannot be overridden via
    # a class attribute; ECO560 therefore redefines ``error_code`` explicitly
    # (see test_error_code_protocol_response for the protocol-level check).
    code = error_code_get_process("9")
    assert isinstance(code, ECO560ErrorCode)
    assert ECO560ErrorCode.OVERHEAT in code
    assert ECO560ErrorCode.LOW_FLOW in code


def test_error_code_protocol_response():
    # Verify that the public `error_code` property returns an
    # ECO560ErrorCode built from the EROR? device response (41 =
    # NO_PURGE_FLOW | LOW_FLOW | OVERHEAT).
    with expected_protocol(
            ECO560,
            [("EROR?", "41")]) as inst:
        code = inst.error_code
        assert isinstance(code, ECO560ErrorCode)
        assert ECO560ErrorCode.NO_PURGE_FLOW in code
        assert ECO560ErrorCode.LOW_FLOW in code
        assert ECO560ErrorCode.OVERHEAT in code

    # 32 is ECO560ErrorCode.NO_PURGE_FLOW on its own.
    with expected_protocol(
            ECO560,
            [("EROR?", "32")]) as inst:
        assert inst.error_code == ECO560ErrorCode.NO_PURGE_FLOW


def test_copy_active_setup_file_is_none():
    """ECO-560 does not implement copy_active_setup_file."""
    inst = ECO560.__new__(ECO560)
    assert inst.copy_active_setup_file is None
    # (It is a plain ``None`` class attribute overriding the InteractiveSetting
    # of ATSBase, not a property on instances.)


def test_temperature_limit_air_low_model_limits():
    """The model-specific air low-limit [-150, 25] feeds the validator."""
    with expected_protocol(ECO560, [("LLIM -150", None)]) as inst:
        # -200 would be clipped to -99 for the ATSBase range [-99, 25], but
        # the ECO-560 silently clips to its own lower bound -150.
        inst.temperature_limit_air_low = -200
