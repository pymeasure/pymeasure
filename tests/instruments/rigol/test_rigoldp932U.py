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

import pytest
from pymeasure.test import expected_protocol
from pymeasure.instruments.rigol.rigol_dp932u import RigolDP932U


def test_init():
    """Test successful initialization of the instrument."""
    with expected_protocol(
        RigolDP932U,
        [],
    ):
        pass  # Verify no errors occur during initialization


def test_active_channel_setter():
    """Test setting the active channel."""
    with expected_protocol(
        RigolDP932U,
        [(b':INSTrument:NSELect 1', None)],
    ) as inst:
        inst.active_channel = 1


def test_active_channel_getter():
    """Test getting the active channel."""
    with expected_protocol(
        RigolDP932U,
        [(b':INSTrument:NSELect?', b'2\n')],
    ) as inst:
        assert inst.active_channel == 2


def test_voltage_setter():
    """Test setting the voltage."""
    with expected_protocol(
        RigolDP932U,
        [(b':SOURce:VOLTage 5.000', None)],
    ) as inst:
        inst.voltage = 5.0


def test_voltage_getter():
    """Test getting the voltage."""
    with expected_protocol(
        RigolDP932U,
        [(b':SOURce:VOLTage?', b'3.000\n')],
    ) as inst:
        assert inst.voltage == 3.0


def test_current_setter():
    """Test setting the current."""
    with expected_protocol(
        RigolDP932U,
        [(b':SOURce:CURRent 1.500', None)],
    ) as inst:
        inst.current = 1.5


def test_current_getter():
    """Test getting the current."""
    with expected_protocol(
        RigolDP932U,
        [(b':SOURce:CURRent?', b'1.200\n')],
    ) as inst:
        assert inst.current == 1.2


def test_output_enabled_setter():
    """Test setting the output enabled state."""
    with expected_protocol(
        RigolDP932U,
        [(b':OUTPut:STATe 1', None)],
    ) as inst:
        inst.output_enabled = True

    with expected_protocol(
        RigolDP932U,
        [(b':OUTPut:STATe 0', None)],
    ) as inst:
        inst.output_enabled = False


def test_output_enabled_getter():
    """Test getting the output enabled state."""
    with expected_protocol(
        RigolDP932U,
        [(b':OUTPut:STATe?', b'1\n')],
    ) as inst:
        assert inst.output_enabled is True

    with expected_protocol(
        RigolDP932U,
        [(b':OUTPut:STATe?', b'0\n')],
    ) as inst:
        assert inst.output_enabled is False


def test_connection_mode_setter():
    """Test setting the connection mode."""
    with expected_protocol(
        RigolDP932U,
        [(b':OUTPut:PAIR SER', None)],
    ) as inst:
        inst.connection_mode = "SER"

    with expected_protocol(
        RigolDP932U,
        [(b':OUTPut:PAIR PAR', None)],
    ) as inst:
        inst.connection_mode = "PAR"


def test_connection_mode_getter():
    """Test getting the connection mode."""
    with expected_protocol(
        RigolDP932U,
        [(b':OUTPut:PAIR?', b'SER\n')],
    ) as inst:
        assert inst.connection_mode == "SER"

    with expected_protocol(
        RigolDP932U,
        [(b':OUTPut:PAIR?', b'PAR\n')],
    ) as inst:
        assert inst.connection_mode == "PAR"


def test_measure_voltage():
    """Test measuring voltage."""
    with expected_protocol(
        RigolDP932U,
        [
            (b':MEASure:VOLTage:DC?', b'12.500\n'),
        ],
    ) as inst:
        assert inst.measure_voltage == 12.5


def test_measure_current():
    """Test measuring current."""
    with expected_protocol(
        RigolDP932U,
        [
            (b':MEASure:CURRent:DC?', b'0.750\n'),
        ],
    ) as inst:
        assert inst.measure_current == 0.75


def test_reset():
    """Test resetting the instrument."""
    with expected_protocol(
        RigolDP932U,
        [
            (b'*RST', None),
        ],
    ) as inst:
        inst.reset()


def test_get_device_id():
    """Test getting the device ID."""
    with expected_protocol(
        RigolDP932U,
        [(b'*IDN?', b'Rigol,DP932U,123456,1.0.0\n')],
    ) as inst:
        assert inst.get_device_id() == "Rigol,DP932U,123456,1.0.0"


def test_check_error_no_error():
    """Test checking for errors when no error is present."""
    with expected_protocol(
        RigolDP932U,
        [(b':SYSTem:ERRor?', b'No error\n')],
    ) as inst:
        assert inst.check_error() == "No error"


def test_check_error_with_error():
    """Test checking for errors when an error is present."""
    with expected_protocol(
        RigolDP932U,
        [(b':SYSTem:ERRor?', b'Error: Voltage out of range\n')],
    ) as inst:
        with pytest.raises(RuntimeError, match="System Error: Error: Voltage out of range"):
            inst.check_error()
