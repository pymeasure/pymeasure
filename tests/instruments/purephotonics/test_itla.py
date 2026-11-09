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
import pytest

from pymeasure.instruments.purephotonics import (
    ITLA,
    FatalStatus,
    ITLAError,
    ITLAExecutionError,
)
from pymeasure.instruments.purephotonics.itla import checksum
from pymeasure.test import expected_protocol


def p(hex_string):
    """Convert a hex string like '54 00 00 10' to bytes."""
    return bytes.fromhex(hex_string)


def read(register):
    """Create the packet to read a register."""
    return ITLA._packet(register)


def write(register, data):
    """Create the packet to write a register."""
    return ITLA._packet(register, data, write=True)


def reply(register, data=0, status=0):
    """Create a valid answer packet of the module."""
    packet = bytearray([status | 0x04, register, (data >> 8) & 0xFF, data & 0xFF])
    packet[0] |= checksum(packet) << 4
    return bytes(packet)


# Request packets of the Pure Photonics operating guide example and answers recorded with a
# PPCL300 (firmware 8.0.9).
NOP = (p("00 00 00 00"), p("54 00 00 10"))


@pytest.mark.parametrize(
    "packet",
    [
        "00 00 00 00",
        "54 00 00 10",
        "61 31 03 E8",
        "81 32 00 08",
        "A1 35 00 C1",
        "E1 36 15 E0",
        "31 30 00 01",
        "A1 90 00 02",
        "41 E4 00 3C",
        "B1 E5 00 01",
        "80 E6 00 00",
        "01 32 00 00",
        "44 31 06 40",
        "D5 31 07 D0",
    ],
)
def test_checksum(packet):
    data = p(packet)
    assert checksum(data) == data[0] >> 4


class TestPacket:
    @pytest.mark.parametrize(
        "register, data, write, packet",
        [
            (0x00, 0, False, "00 00 00 00"),
            (0x31, 1000, True, "61 31 03 E8"),
            (0x35, 193, True, "A1 35 00 C1"),
            (0x36, 5600, True, "E1 36 15 E0"),
            (0x90, 2, True, "A1 90 00 02"),
            (0xE6, 0, False, "80 E6 00 00"),
            (0x62, -1000, True, "F1 62 FC 18"),
        ],
    )
    def test_packet(self, register, data, write, packet):
        assert ITLA._packet(register, data, write) == p(packet)

    def test_packet_out_of_range(self):
        with pytest.raises(ValueError):
            ITLA._packet(0x31, 0x10000, True)


def test_init():
    with expected_protocol(ITLA, []):
        pass


def test_nop():
    with expected_protocol(ITLA, [NOP]) as inst:
        assert inst.nop == 16


def test_module_ready_and_pending():
    with expected_protocol(ITLA, [NOP, (p("00 00 00 00"), p("00 00 01 10"))]) as inst:
        assert inst.module_ready is True
        assert inst.pending == 1


def test_wait_until_ready():
    with expected_protocol(
        ITLA,
        [(p("00 00 00 00"), p("00 00 01 10")), NOP],
    ) as inst:
        inst.wait_until_ready(interval=0)


def test_wait_until_ready_timeout():
    with (
        expected_protocol(ITLA, [(p("00 00 00 00"), p("00 00 01 10"))]) as inst,
        pytest.raises(TimeoutError),
    ):
        inst.wait_until_ready(timeout=0)


def test_manufacturer_aea():
    """Strings are read with automatic extended addressing via register 0x0B."""
    with expected_protocol(
        ITLA,
        [
            (p("20 02 00 00"), p("26 02 00 06")),
            (p("B0 0B 00 00"), p("84 0B 50 75")),
            (p("B0 0B 00 00"), p("94 0B 72 65")),
            (p("B0 0B 00 00"), p("44 0B 50 68")),
        ],
    ) as inst:
        assert inst.manufacturer == "PurePh"


def test_model_aea_strips_null():
    with expected_protocol(
        ITLA,
        [
            (p("30 03 00 00"), p("66 03 00 03")),
            (p("B0 0B 00 00"), p("F4 0B 50 50")),
            (p("B0 0B 00 00"), p("84 0B 43 00")),
        ],
    ) as inst:
        assert inst.model == "PPC"


def test_temperatures_aea_array():
    with expected_protocol(
        ITLA,
        [
            (p("D0 58 00 00"), p("F6 58 00 04")),
            (p("B0 0B 00 00"), p("A4 0B 0C 7E")),
            (p("B0 0B 00 00"), p("64 0B 08 DC")),
        ],
    ) as inst:
        assert inst.temperatures == [31.98, 22.68]


def test_currents_aea_array_signed():
    with expected_protocol(
        ITLA,
        [
            (p("20 57 00 00"), p("06 57 00 04")),
            (p("B0 0B 00 00"), p("E4 0B F8 35")),
            (p("B0 0B 00 00"), p("D4 0B 04 AC")),
        ],
    ) as inst:
        assert inst.currents == pytest.approx([-0.1995, 0.1196])


def test_power_setpoint_getter():
    with expected_protocol(ITLA, [(p("20 31 00 00"), p("44 31 06 40"))]) as inst:
        assert inst.power_setpoint == 16


POWER_LIMITS = [(read(0x50), reply(0x50, 600)), (read(0x51), reply(0x51, 1600))]


def test_power_setpoint_setter():
    """Example of the Pure Photonics operating guide."""
    with expected_protocol(ITLA, POWER_LIMITS + [(p("61 31 03 E8"), p("70 31 03 E8"))]) as inst:
        inst.power_setpoint = 10


@pytest.mark.parametrize("power", [5.99, 16.01, 30])
def test_power_setpoint_out_of_limits(power):
    """Firmware 8.4.0 accepts any value, therefore the driver checks the module limits."""
    with expected_protocol(ITLA, POWER_LIMITS) as inst, pytest.raises(ValueError):
        inst.power_setpoint = power


def test_range_error_of_module():
    with expected_protocol(
        ITLA,
        [(p("91 31 07 D0"), p("D5 31 07 D0")), (NOP[0], p("64 00 00 13"))],
    ) as inst:
        with pytest.raises(ITLAExecutionError) as exc:
            inst.write_register(0x31, 2000)
        assert exc.value.error == ITLAError.RVE
        assert exc.value.register == 0x31


def test_power_disabled():
    with expected_protocol(ITLA, [(p("60 42 00 00"), p("A4 42 80 00"))]) as inst:
        assert inst.power == -327.68


def test_emission_enabled_setter():
    """Example of the Pure Photonics operating guide (answer: command pending)."""
    with expected_protocol(ITLA, [(p("81 32 00 08"), p("B3 32 10 08"))]) as inst:
        inst.emission_enabled = True


def test_emission_disabled_setter():
    with expected_protocol(ITLA, [(p("01 32 00 00"), p("10 32 00 00"))]) as inst:
        inst.emission_enabled = False


@pytest.mark.parametrize("data, value", [("00 08", True), ("00 00", False)])
def test_emission_enabled_getter(data, value):
    response = bytearray(p(f"00 32 {data}"))
    response[0] |= 0x04
    response[0] |= checksum(response) << 4
    with expected_protocol(
        ITLA,
        [(ITLA._packet(0x32), bytes(response))],
    ) as inst:
        assert inst.emission_enabled is value


def test_reset_soft():
    with expected_protocol(ITLA, [(ITLA._packet(0x32, 2, True), p("74 32 00 02"))]) as inst:
        inst.reset()


def test_channel():
    with expected_protocol(
        ITLA,
        [(p("31 30 00 01"), p("20 30 00 01")), (p("30 30 00 00"), p("64 30 00 01"))],
    ) as inst:
        inst.channel = 1
        assert inst.channel == 1


def test_channel_invalid():
    with expected_protocol(ITLA, []) as inst, pytest.raises(ValueError):
        inst.channel = 0


def test_first_channel_frequency_setter():
    """Example of the Pure Photonics operating guide: 193.560 THz."""
    with expected_protocol(
        ITLA,
        [
            (p("70 52 00 00"), p("74 52 00 BF")),  # frequency_min
            (p("60 53 00 00"), p("04 53 13 88")),
            (p("10 54 00 00"), p("D4 54 00 C4")),  # frequency_max
            (p("00 55 00 00"), p("54 55 09 C4")),
            (p("A1 35 00 C1"), p("B0 35 00 C1")),
            (p("E1 36 15 E0"), p("F0 36 15 E0")),
        ],
    ) as inst:
        inst.first_channel_frequency = 193.56e12


def test_first_channel_frequency_out_of_range():
    with (
        expected_protocol(
            ITLA,
            [
                (p("70 52 00 00"), p("74 52 00 BF")),
                (p("60 53 00 00"), p("04 53 13 88")),
                (p("10 54 00 00"), p("D4 54 00 C4")),
                (p("00 55 00 00"), p("54 55 09 C4")),
            ],
        ) as inst,
        pytest.raises(ValueError),
    ):
        inst.first_channel_frequency = 200e12


def test_frequency():
    with expected_protocol(
        ITLA,
        [
            (ITLA._packet(0x40), ITLA._packet(0x40, 194)),
            (ITLA._packet(0x41), ITLA._packet(0x41, 5)),
        ],
    ) as inst:
        assert inst.frequency == pytest.approx(194.0005e12)


def test_grid_spacing():
    with expected_protocol(ITLA, [(p("70 34 00 00"), p("94 34 01 F4"))]) as inst:
        assert inst.grid_spacing == 50e9


def test_fine_tune_frequency_negative():
    with expected_protocol(
        ITLA,
        [
            (read(0x4F), reply(0x4F, 30000)),
            (p("F1 62 FC 18"), p("E0 62 FC 18")),
            (ITLA._packet(0x62), p("A4 62 FC 18")),
        ],
    ) as inst:
        inst.fine_tune_frequency = -1e9
        assert inst.fine_tune_frequency == -1e9


@pytest.mark.parametrize("frequency", [-30.001e9, 30.001e9])
def test_fine_tune_frequency_out_of_range(frequency):
    with (
        expected_protocol(ITLA, [(read(0x4F), reply(0x4F, 30000))]) as inst,
        pytest.raises(ValueError),
    ):
        inst.fine_tune_frequency = frequency


def test_status_fatal():
    with expected_protocol(ITLA, [(ITLA._packet(0x20), p("94 20 C0 30"))]) as inst:
        status = inst.status_fatal
        assert FatalStatus.SRQ in status and FatalStatus.MRL in status
        assert FatalStatus.FPWR not in status


def test_not_implemented_register():
    with expected_protocol(
        ITLA,
        [(ITLA._packet(0xEC), p("75 EC 00 00")), (NOP[0], p("44 00 00 11"))],
    ) as inst:
        with pytest.raises(ITLAExecutionError) as exc:
            inst.read_register(0xEC)  # recorded with firmware 8.0.9
        assert exc.value.error == ITLAError.RNI


class TestCommunicationErrors:
    def test_wrong_checksum_read_retried(self):
        """An invalid answer causes resynchronization and repetition of a read."""
        with expected_protocol(
            ITLA,
            [
                (p("30 30 00 00"), p("F4 30 00 01")),  # wrong checksum
                (b"\x00", b"\x10"),  # resynchronization
                NOP,
                (p("30 30 00 00"), p("64 30 00 01")),
            ],
        ) as inst:
            assert inst.channel == 1

    def test_wrong_register_read_retried(self):
        """An answer for another register indicates lost framing."""
        with expected_protocol(
            ITLA,
            [
                (p("30 30 00 00"), p("54 00 00 10")),
                (b"\x00", b"\x10"),
                NOP,
                (p("30 30 00 00"), p("64 30 00 01")),
            ],
        ) as inst:
            assert inst.channel == 1

    def test_invalid_write_answer_raises(self):
        """A write is not repeated automatically after lost framing."""
        with (
            expected_protocol(
                ITLA,
                [(p("31 30 00 01"), p("54 00 00 10")), (b"\x00", b"\x10"), NOP],
            ) as inst,
            pytest.raises(ConnectionError),
        ):
            inst.channel = 1

    def test_unknown_command(self):
        with expected_protocol(ITLA, []) as inst, pytest.raises(ValueError):
            inst.write("X,0x30")


def test_reply_helper():
    """The helper reproduces answers recorded with a PPCL300."""
    assert reply(0x00, 0x10) == p("54 00 00 10")
    assert reply(0x31, 1600) == p("44 31 06 40")


def test_wrong_register_twice_raises():
    """Firmware 8.0.9 answers a read of 0xE7 with a packet for register 0xE5."""
    with (
        expected_protocol(
            ITLA,
            [(read(0xE7), reply(0xE5, 1)), (b"\x00", b"\x10"), NOP, (read(0xE7), reply(0xE5, 1))],
        ) as inst,
        pytest.raises(ConnectionError, match="received e4 e5 00 01"),
    ):
        inst.read_register(0xE7)


class TestBaudRate:
    def test_baud_rate(self):
        """IOCap value 0x0004 read from a PPCL300: 9600 Bd, maximum 115200 Bd."""
        with expected_protocol(
            ITLA,
            [(read(0x0D), reply(0x0D, 0x0004)), (read(0x0D), reply(0x0D, 0x0004))],
        ) as inst:
            assert inst.baud_rate == 9600
            assert inst.max_baud_rate == 115200

    def test_set_baud_rate(self):
        with expected_protocol(
            ITLA,
            [(read(0x0D), reply(0x0D, 0x1004)), (write(0x0D, 0x1044), reply(0x0D, 0x1044)), NOP],
        ) as inst:
            inst.set_baud_rate(115200)
            assert inst.adapter.connection.baud_rate == 115200

    def test_set_baud_rate_invalid(self):
        with expected_protocol(ITLA, []) as inst, pytest.raises(ValueError):
            inst.set_baud_rate(14400)

    def test_set_baud_rate_above_maximum(self):
        with (
            expected_protocol(ITLA, [(read(0x0D), reply(0x0D, 0x0002))]) as inst,
            pytest.raises(ValueError, match="maximum"),
        ):
            inst.set_baud_rate(115200)


def test_serial_number_embedded_null():
    """A PPCL300 returns 'CRTNH1E00F\\x00001\\x00' as serial number."""
    data = b"CRTNH1E00F\x00001\x00"
    pairs = [(read(0x04), reply(0x04, len(data), status=2))]
    pairs += [
        (read(0x0B), reply(0x0B, int.from_bytes(data[i:i + 2], "big")))
        for i in range(0, len(data), 2)
    ]
    with expected_protocol(ITLA, pairs) as inst:
        assert inst.serial_number == "CRTNH1E00F"
