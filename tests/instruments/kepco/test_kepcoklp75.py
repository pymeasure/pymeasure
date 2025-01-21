from pymeasure.test import expected_protocol
from pymeasure.instruments.kepco.kepcoklp75 import KepcoKLP75


def test_init():
    """Test initialization of the instrument."""
    with expected_protocol(KepcoKLP75, []):
        pass


def test_get_id():
    """Test querying the instrument ID."""
    with expected_protocol(
        KepcoKLP75,
        [(b"*IDN?", b"KEPCO,KLP75,123456,V1.0")],
    ) as inst:
        assert inst.get_id() == "KEPCO,KLP75,123456,V1.0"


def test_output_enabled_getter():
    """Test checking if output is enabled."""
    with expected_protocol(
        KepcoKLP75,
        [(b"OUTPut:STATe?", b"1")],
    ) as inst:
        assert inst.output_enabled is True


def test_output_enabled_setter():
    """Test enabling or disabling the output."""
    with expected_protocol(
        KepcoKLP75,
        [(b"OUTPut:STATe 1", None)],
    ) as inst:
        inst.output_enabled = True


def test_voltage_getter():
    """Test reading the output voltage."""
    with expected_protocol(
        KepcoKLP75,
        [(b"MEASure:VOLTage?", b"12.5")],
    ) as inst:
        assert inst.voltage == 12.5


def test_voltage_setpoint_getter():
    """Test querying the voltage setpoint."""
    with expected_protocol(
        KepcoKLP75,
        [(b"SOURce:VOLTage?", b"24.0")],
    ) as inst:
        assert inst.voltage_setpoint == 24.0


def test_voltage_setpoint_setter():
    """Test setting the voltage setpoint."""
    with expected_protocol(
        KepcoKLP75,
        [(b"SOURce:VOLTage 24.0", None)],
    ) as inst:
        inst.voltage_setpoint = 24.0


def test_current_getter():
    """Test reading the output current."""
    with expected_protocol(
        KepcoKLP75,
        [(b"MEASure:CURRent?", b"2.0")],
    ) as inst:
        assert inst.current == 2.0


def test_current_setpoint_getter():
    """Test querying the current setpoint."""
    with expected_protocol(
        KepcoKLP75,
        [(b"SOURce:CURRent?", b"5.0")],
    ) as inst:
        assert inst.current_setpoint == 5.0


def test_current_setpoint_setter():
    """Test setting the current setpoint."""
    with expected_protocol(
        KepcoKLP75,
        [(b"SOURce:CURRent 5.0", None)],
    ) as inst:
        inst.current_setpoint = 5.0


def test_enable_protection():
    """Test enabling overvoltage and overcurrent protection."""
    with expected_protocol(
        KepcoKLP75,
        [
            (b"SOURce:VOLTage:PROTection 30.0", None),
            (b"SOURce:CURRent:PROTection 5.0", None),
        ],
    ) as inst:
        inst.enable_protection(ovp=30.0, ocp=5.0)


def test_enable_protection_invalid_ovp():
    """Test enabling protection with invalid overvoltage protection value."""
    with expected_protocol(
        KepcoKLP75,
        [],
    ) as inst:
        try:
            inst.enable_protection(ovp=100.0)
        except ValueError as e:

            expected_ovp_error = "OVP value 100.0 is out of range (0-75 V)."
            assert str(e) == expected_ovp_error, f"Unexpected error message: {e}"
            print("test_enable_protection_invalid_ovp passed!")


def test_enable_protection_invalid_ocp():
    """Test enabling protection with invalid overcurrent protection value."""
    with expected_protocol(
        KepcoKLP75,
        [],
    ) as inst:
        try:
            inst.enable_protection(ocp=20.0)
        except ValueError as e:

            expected_ocp_error = "OCP value 20.0 is out of range (0.4-16 A)."
            assert str(e) == expected_ocp_error, f"Unexpected error message: {e}"
            print("test_enable_protection_invalid_ocp passed!")


def test_confidence_test():
    """Test performing a confidence self-test."""
    with expected_protocol(
        KepcoKLP75,
        [(b"*TST?", b"0")],
    ) as inst:
        assert inst.confidence_test == 0


def test_status():
    """Test querying the instrument's status."""
    with expected_protocol(
        KepcoKLP75,
        [(b"STATus:QUEStionable?", b"OK")],
    ) as inst:
        assert inst.status() == "OK"


def test_reset():
    """Test resetting the instrument."""
    with expected_protocol(
        KepcoKLP75,
        [(b"*RST", None)],
    ) as inst:
        inst.reset()


def test_clear():
    """Test clearing the error queue."""
    with expected_protocol(
        KepcoKLP75,
        [(b"*CLS", None)],
    ) as inst:
        inst.clear()
