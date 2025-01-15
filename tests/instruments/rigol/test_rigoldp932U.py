import pytest
from pymeasure.test import expected_protocol
from pymeasure.instruments.rigol.Rigol_DP932U import RigolDP932U


def test_init():
    with expected_protocol(
        RigolDP932U,
        [],
    ):
        pass  # Verify the expected communication


def test_init_with_none_adapter():
    with pytest.raises(
            ValueError,
            match="Adapter cannot be None. Provide a valid communication adapter.",
    ):
        RigolDP932U(None)


def test_control_channel_setter():
    with expected_protocol(
        RigolDP932U,
        [(b':INSTrument:NSELect 1', None),
         (b':INSTrument:NSELect?', b'1\n')],
    ) as inst:
        inst.control_channel = 1
        assert inst.control_channel == 1


def test_control_channel_getter():
    with expected_protocol(
        RigolDP932U,
        [(b':INSTrument:NSELect?', b'2\n')],
    ) as inst:
        assert inst.control_channel == 2


def test_control_voltage_setter():
    with expected_protocol(
        RigolDP932U,
        [(b':SOURce:VOLTage 5.000', None)],
    ) as inst:
        inst.control_voltage = 5.0


def test_control_voltage_getter():
    with expected_protocol(
        RigolDP932U,
        [(b':MEASure:VOLTage:DC?', b'3.000\n')],
    ) as inst:
        assert inst.control_voltage == 3.0


def test_control_current_setter():
    with expected_protocol(
        RigolDP932U,
        [(b':SOURce:CURRent 1.500', None)],
    ) as inst:
        inst.control_current = 1.5


def test_control_current_getter():
    with expected_protocol(
        RigolDP932U,
        [(b':MEASure:CURRent:DC?', b'1.200\n')],
    ) as inst:
        assert inst.control_current == 1.2


def test_control_output_state_setter():
    with expected_protocol(
        RigolDP932U,
        [(b':OUTPut:STATe 1', None)],
    ) as inst:
        inst.control_output_state = "ON"


def test_control_output_state_getter():
    with expected_protocol(
        RigolDP932U,
        [(b':OUTPut:STATe?', b'0\n')],
    ) as inst:
        assert inst.control_output_state == "OFF"


def test_control_connection_mode_setter():
    with expected_protocol(
        RigolDP932U,
        [(b':OUTPut:PAIR SER', None)],
    ) as inst:
        inst.control_connection_mode = "SER"


def test_control_connection_mode_getter():
    with expected_protocol(
        RigolDP932U,
        [(b':OUTPut:PAIR?', b'PAR\n')],
    ) as inst:
        assert inst.control_connection_mode == "PAR"


def test_measure_voltage():
    with expected_protocol(
        RigolDP932U,
        [
            (b':MEASure:VOLTage:DC?', b'12.500\n'),
            (b':SYSTem:ERRor?', b'No error\n'),
        ],
    ) as inst:
        assert inst.measure_voltage() == 12.5


def test_decorator_raises_runtime_error():
    with expected_protocol(
        RigolDP932U,
        [
            (b':MEASure:VOLTage:DC?', b'12.500\n'),
            (b':SYSTem:ERRor?', b'Error: Voltage out of range\n'),
        ],
    ) as inst:
        with pytest.raises(RuntimeError, match="System Error: Error: Voltage out of range"):
            inst.measure_voltage()


def test_measure_current():
    with expected_protocol(
        RigolDP932U,
        [
            (b':MEASure:CURRent:DC?', b'0.750\n'),
            (b':SYSTem:ERRor?', b'No error\n'),
        ],
    ) as inst:
        assert inst.measure_current() == 0.75


def test_reset():
    with expected_protocol(
        RigolDP932U,
            [
                (b'*RST', None),  # Reset command
                (b':SYSTem:ERRor?', b'No error\n'),  # Check for errors after reset
            ],
    ) as inst:
        inst.reset()


def test_get_device_id():
    with expected_protocol(
        RigolDP932U,
        [(b'*IDN?', b'Rigol,DP932U,123456,1.0.0\n')],
    ) as inst:
        assert inst.get_device_id() == "Rigol,DP932U,123456,1.0.0"


def test_check_error_no_error():
    with expected_protocol(
        RigolDP932U,
        [(b':SYSTem:ERRor?', b'No error\n')],
    ) as inst:
        assert inst.check_error() == "No error"


def test_check_error_with_error():
    with expected_protocol(
        RigolDP932U,
        [(b':SYSTem:ERRor?', b'Error: Voltage out of range\n')],
    ) as inst:
        with pytest.raises(RuntimeError, match="System Error: Error: Voltage out of range"):
            inst.check_error()


def test_measure_voltage_with_error():
    with expected_protocol(
        RigolDP932U,
        [
            (b':MEASure:VOLTage:DC?', b'12.500\n'),
            (b':SYSTem:ERRor?', b'Error: Voltage measurement failed\n'),
        ],
    ) as inst:
        with pytest.raises(RuntimeError, match="System Error: Error: Voltage measurement failed"):
            inst.measure_voltage()


def test_measure_current_with_error():
    with expected_protocol(
        RigolDP932U,
        [
            (b':MEASure:CURRent:DC?', b'0.750\n'),
            (b':SYSTem:ERRor?', b'Error: Current measurement failed\n'),
        ],
    ) as inst:
        with pytest.raises(RuntimeError, match="System Error: Error: Current measurement failed"):
            inst.measure_current()


def test_reset_with_error():
    with expected_protocol(
        RigolDP932U,
        [
            (b'*RST', None),
            (b':SYSTem:ERRor?', b'Error: Reset failed\n'),
        ],
    ) as inst:
        with pytest.raises(RuntimeError, match="System Error: Error: Reset failed"):
            inst.reset()
