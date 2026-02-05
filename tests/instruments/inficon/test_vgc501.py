
from pymeasure.test import expected_protocol
from pymeasure.instruments.inficon import VGC501


def test_init():
    with expected_protocol(
            VGC501,
            [],
    ):
        pass  # Verify the expected communication.


def test_error_status_getter():
    with expected_protocol(
            VGC501,
            [(b'ERR', b'\x06\r\n0000')],
    ) as inst:
        assert inst.error_status == 0.0


def test_information_getter():
    with expected_protocol(
            VGC501,
            [(b'AYT', b'\x06\r\nVGC501,398-481,3658,1.07,1.0')],
    ) as inst:
        assert inst.information == ['VGC501', '398-481', 3658.0, 1.07, 1.0]


def test_pressure_1_getter():
    with expected_protocol(
            VGC501,
            [(b'PR1', b'\x06\r\n0,+7.5500E-02')],
    ) as inst:
        assert inst.pressure == [0.0, 0.0755]
