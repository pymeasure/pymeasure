import pytest
from pymeasure.test import expected_protocol
from src.hardware.Rigol_DP932U import RigolDP932U


def test_init():
    with expected_protocol(
            RigolDP932U,
            [],
    ):
        pass  # Verify the expected communication.


def test_control_channel_setter():
    with expected_protocol(
            RigolDP932U,
            [(b':INSTrument:NSELect 1', None)],
    ) as inst:
        inst.control_channel = 1


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
            [(b':MEASure[:SCALar][:VOLTage][:DC]?', b'3.000\n')],
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
            [(b':MEASure[:SCALar]:CURRent[:DC]?', b'1.200\n')],
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
                (b':INSTrument:NSELect 1', None),  # Select the correct channel
                (b':MEASure:VOLTage:DC?', b'12.500\n'),  # Measure voltage
                (b':SYSTem:ERRor?', b'No error\n'),  # Error check
            ],
    ) as inst:
        inst.control_channel = 1  # Set the channel to be measured
        assert inst.measure_voltage() == 12.5  # Assert the measured value is correct


def test_measure_current():
    with expected_protocol(
            RigolDP932U,
            [
                (b':INSTrument:NSELect 1', None),  # Select the correct channel
                (b':MEASure:CURRent:DC?', b'0.750\n'),  # Measure current
                (b':SYSTem:ERRor?', b'No error\n'),  # Error check
            ],
    ) as inst:
        inst.control_channel = 1  # Set the channel to be measured
        assert inst.measure_current() == 0.75  # Assert the measured value is correct


def test_reset():
    with expected_protocol(
            RigolDP932U,
            [(b'*RST', None)],
    ) as inst:
        inst.reset()


def test_get_device_id():
    with expected_protocol(
            RigolDP932U,
            [(b'*IDN?', b'Rigol,DP932U,123456,1.0.0\n')],
    ) as inst:
        assert inst.get_device_id() == "Rigol,DP932U,123456,1.0.0"


def test_check_error():
    with expected_protocol(
            RigolDP932U,
            [(b':SYSTem:ERRor?', b'No error\n')],
    ) as inst:
        assert inst.check_error() == "No error"
