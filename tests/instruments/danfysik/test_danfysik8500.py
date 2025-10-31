import pytest
from pymeasure.test import expected_protocol
from pymeasure.instruments.danfysik import Danfysik8500
from pymeasure.errors import RangeException

init_comm = [(b"ERRT", None), (b"UNLOCK", None)]


def test_init():
    with expected_protocol(Danfysik8500, init_comm):
        pass


def test_id():
    with expected_protocol(
        Danfysik8500,
        init_comm + [(b"PRINT", b"Danfysik 8500 Serial Number 12345")],
    ) as instr:
        assert instr.id == "Danfysik 8500 Serial Number 12345"


def test_local():
    with expected_protocol(Danfysik8500, init_comm + [(b"LOC", None)]) as instr:
        instr.local()


def test_remote():
    with expected_protocol(Danfysik8500, init_comm + [(b"REM", None)]) as instr:
        instr.remote()


def test_polarity_getter_positive():
    with expected_protocol(Danfysik8500, init_comm + [(b"PO", b"+")]) as instr:
        assert instr.polarity == 1


def test_polarity_getter_negative():
    with expected_protocol(Danfysik8500, init_comm + [(b"PO", b"-")]) as instr:
        assert instr.polarity == -1


def test_polarity_setter_positive():
    with expected_protocol(Danfysik8500, init_comm + [(b"PO +", None)]) as instr:
        instr.polarity = 1


def test_polarity_setter_negative():
    with expected_protocol(Danfysik8500, init_comm + [(b"PO -", None)]) as instr:
        instr.polarity = -1


def test_reset_interlocks():
    with expected_protocol(Danfysik8500, init_comm + [(b"RS", None)]) as instr:
        instr.reset_interlocks()


def test_enable():
    with expected_protocol(Danfysik8500, init_comm + [(b"N", None)]) as instr:
        instr.enable()


def test_disable():
    with expected_protocol(Danfysik8500, init_comm + [(b"F", None)]) as instr:
        instr.disable()


def test_is_enabled_true():
    # Status hex with bit 0x800000 == 0 means enabled
    with expected_protocol(Danfysik8500, init_comm + [(b"S1H", b"Status: 000000")]) as instr:
        assert instr.is_enabled() is True


def test_is_enabled_false():
    # Status hex with bit 0x800000 != 0 means disabled
    with expected_protocol(Danfysik8500, init_comm + [(b"S1H", b"Status: 800000")]) as instr:
        assert instr.is_enabled() is False


def test_status_hex():
    with expected_protocol(Danfysik8500, init_comm + [(b"S1H", b"Status: ABCDEF")]) as instr:
        assert instr.status_hex == 0xABCDEF


def test_status_hex_invalid():
    with pytest.raises(Exception, match="Danfysik status not properly returned"):
        with expected_protocol(Danfysik8500, init_comm + [(b"S1H", b"Invalid status")]) as instr:
            _ = instr.status_hex


def test_current_getter():
    with expected_protocol(Danfysik8500, init_comm + [(b"AD 8", b"1000"), (b"PO", b"+")]) as instr:
        assert instr.current == 10.0  # 1000 * 1e-2 * 1


def test_current_getter_negative():
    with expected_protocol(Danfysik8500, init_comm + [(b"AD 8", b"1000"), (b"PO", b"-")]) as instr:
        assert instr.current == -10.0  # 1000 * 1e-2 * -1


def test_current_setter():
    with expected_protocol(
        Danfysik8500,
        init_comm
        + [
            (b"DA 0,62500", None),  # 10 A * (1e6 / 160) = 62500
        ],
    ) as instr:
        instr.current = 10.0


def test_current_setter_negative():
    with expected_protocol(
        Danfysik8500,
        init_comm
        + [
            (b"DA 0,-62500", None),  # -10 A * (1e6 / 160) = -62500
        ],
    ) as instr:
        instr.current = -10.0


def test_current_setter_out_of_range():
    with pytest.raises(RangeException, match="Danfysik 8500 is only capable of sourcing"):
        with expected_protocol(Danfysik8500, init_comm) as instr:
            instr.current = 200.0  # Exceeds +/- 160 A limit


def test_current_ppm_getter():
    with expected_protocol(Danfysik8500, init_comm + [(b"DA 0", b"DA 500000")]) as instr:
        assert instr.current_ppm == 500000


def test_current_ppm_setter():
    with expected_protocol(Danfysik8500, init_comm + [(b"DA 0,500000", None)]) as instr:
        instr.current_ppm = 500000


def test_current_ppm_setter_out_of_range():
    with pytest.raises(RangeException, match="Danfysik 8500 requires parts per million"):
        with expected_protocol(Danfysik8500, init_comm) as instr:
            instr.current_ppm = 2000000  # Exceeds 1e6 limit


def test_current_setpoint():
    with expected_protocol(
        Danfysik8500,
        init_comm
        + [
            (b"DA 0", b"DA 62500"),  # 62500 ppm
        ],
    ) as instr:
        assert instr.current_setpoint == 10.0  # 62500 * (160 / 1e6)


def test_slew_rate():
    with expected_protocol(Danfysik8500, init_comm + [(b"R3", b"1.5")]) as instr:
        assert instr.slew_rate == 1.5


def test_is_current_stable():
    with expected_protocol(
        Danfysik8500,
        init_comm
        + [
            (b"AD 8", b"1000"),  # Actual current: 10 A
            (b"PO", b"+"),
            (b"DA 0", b"DA 62500"),  # Setpoint: 10 A
        ],
    ) as instr:
        assert instr.is_current_stable() is True


def test_is_current_stable_false():
    with expected_protocol(
        Danfysik8500,
        init_comm
        + [
            (b"AD 8", b"1000"),  # Actual current: 10 A
            (b"PO", b"+"),
            (b"DA 0", b"DA 65000"),  # Setpoint: 10.4 A (difference > 0.02 A)
        ],
    ) as instr:
        assert instr.is_current_stable() is False


def test_is_ready():
    # Status hex with bit 0b10 == 0 means ready
    with expected_protocol(Danfysik8500, init_comm + [(b"S1H", b"Status: 000000")]) as instr:
        assert instr.is_ready() is True


def test_is_ready_false():
    # Status hex with bit 0b10 != 0 means not ready
    with expected_protocol(Danfysik8500, init_comm + [(b"S1H", b"Status: 000002")]) as instr:
        assert instr.is_ready() is False


def test_status():
    with expected_protocol(
        Danfysik8500,
        init_comm
        + [
            (b"S1", b"00000000000000000000000"),  # All indicators normal
        ],
    ) as instr:
        status = instr.status
        assert "Main Power ON" in status
        assert len(status) == 1  # Only main power ON


def test_status_with_errors():
    with expected_protocol(
        Danfysik8500,
        init_comm
        + [
            (b"S1", b"00!0000!000000000000000"),  # Some error indicators
        ],
    ) as instr:
        status = instr.status
        assert "Main Power ON" in status
        assert "Polarity Reversed" in status
        assert "Spare Interlock" in status


def test_clear_ramp_set():
    with expected_protocol(Danfysik8500, init_comm + [(b"RAMPSET C", None)]) as instr:
        instr.clear_ramp_set()


def test_set_ramp_delay():
    with expected_protocol(Danfysik8500, init_comm + [(b"RAMPSET 2.500000", None)]) as instr:
        instr.set_ramp_delay(2.5)


def test_start_ramp():
    with expected_protocol(Danfysik8500, init_comm + [(b"RAMP R", None)]) as instr:
        instr.start_ramp()


def test_add_ramp_step():
    with expected_protocol(
        Danfysik8500,
        init_comm + [(b"R 0.125000", None)],  # 20 A / 160 = 0.125
    ) as instr:
        instr.add_ramp_step(20.0)


def test_stop_ramp():
    with expected_protocol(Danfysik8500, init_comm + [(b"RAMP S", b"RAMP Stopped")]) as instr:
        instr.stop_ramp()


def test_clear_sequence():
    with expected_protocol(Danfysik8500, init_comm + [(b"CSS 5", None)]) as instr:
        instr.clear_sequence(5)


def test_stop_sequence():
    with expected_protocol(Danfysik8500, init_comm + [(b"STOP", None)]) as instr:
        instr.stop_sequence()
