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
    PPCL300,
    ITLAError,
    ITLAExecutionError,
    OperationMode,
)
from pymeasure.instruments.purephotonics.itla import checksum
from pymeasure.test import expected_protocol


def p(hex_string):
    """Convert a hex string like '54 00 00 10' to bytes."""
    return bytes.fromhex(hex_string)


def read(register):
    """Create the packet to read a register."""
    return PPCL300._packet(register)


def write(register, data):
    """Create the packet to write a register."""
    return PPCL300._packet(register, data, write=True)


def reply(register, data=0, status=0):
    """Create a valid answer packet of the module."""
    packet = bytearray([status | 0x04, register, (data >> 8) & 0xFF, data & 0xFF])
    packet[0] |= checksum(packet) << 4
    return bytes(packet)


def test_operation_mode_setter():
    """Example of the Pure Photonics operating guide (answer: command pending)."""
    with expected_protocol(PPCL300, [(p("A1 90 00 02"), p("B3 90 01 00"))]) as inst:
        inst.operation_mode = OperationMode.WHISPER


def test_operation_mode_getter():
    with expected_protocol(PPCL300, [(p("90 90 00 00"), p("D4 90 00 00"))]) as inst:
        assert inst.operation_mode == OperationMode.DITHER


def test_operation_mode_invalid():
    with expected_protocol(PPCL300, []) as inst, pytest.raises(ValueError):
        inst.operation_mode = 3


PROBE_SWEEP = [(read(0xE4), reply(0xE4, 60))]  # clean_sweep_available, tested once
PROBE_JUMP = [(read(0xEA), reply(0xEA, 0))]  # clean_jump_available, tested once


def test_sweep():
    """Example of the Pure Photonics operating guide."""
    with expected_protocol(
        PPCL300,
        [
            (p("41 E4 00 3C"), p("50 E4 00 3C")),
            (p("B1 E5 00 01"), p("A0 E5 00 01")),
            (p("A1 E5 00 00"), p("B0 E5 00 00")),
        ],
    ) as inst:
        inst.sweep_range = 60e9
        inst.sweep_enabled = True
        inst.sweep_enabled = False


@pytest.mark.parametrize("sweep_range", [-1e9, 76e9])
def test_sweep_range_invalid(sweep_range):
    with expected_protocol(PPCL300, []) as inst, pytest.raises(ValueError):
        inst.sweep_range = sweep_range


@pytest.mark.parametrize("data, offset", [("00 1F", 3.1e9), ("FF E1", -3.1e9)])
def test_sweep_offset(data, offset):
    response = bytearray(p(f"04 E6 {data}"))
    response[0] |= checksum(response) << 4
    with expected_protocol(PPCL300, [(p("80 E6 00 00"), bytes(response))]) as inst:
        assert inst.sweep_offset == pytest.approx(offset)


def test_sweep_rate():
    with expected_protocol(PPCL300, [(write(0xF1, 20000), reply(0xF1, 20000))]) as inst:
        inst.sweep_rate = 20e9


def test_sweep_rate_invalid():
    with expected_protocol(PPCL300, []) as inst, pytest.raises(ValueError):
        inst.sweep_rate = -1


LIMITS = [  # frequency_min 191.5 THz, frequency_max 196.25 THz
    (read(0x52), reply(0x52, 191)),
    (read(0x53), reply(0x53, 5000)),
    (read(0x54), reply(0x54, 196)),
    (read(0x55), reply(0x55, 2500)),
]
JUMP = [  # 192.05 THz, 31.58 °C, 95.2 mA
    (write(0xE9, 952), reply(0xE9, 952)),
    (write(0xEA, 192), reply(0xEA, 192)),
    (write(0xEB, 500), reply(0xEB, 500)),
    (write(0xEC, 3158), reply(0xEC, 3158)),
] + [(write(0xED, 1), reply(0xED, 1))] * 4


@pytest.mark.parametrize("reported_ghz_10", [500, 499])
def test_clean_jump(reported_ghz_10):
    """Sequence of the clean jump application note; the module may report 100 MHz less."""
    pairs = PROBE_JUMP + LIMITS + [(read(0x90), reply(0x90, 1))] + JUMP
    pairs += [(read(0x40), reply(0x40, 192)), (read(0x41), reply(0x41, reported_ghz_10))]
    with expected_protocol(PPCL300, pairs) as inst:
        inst.clean_jump(192.05e12, sled_temperature=31.58, diode_current=0.0952)


def test_clean_jump_without_check():
    with expected_protocol(PPCL300, PROBE_JUMP + LIMITS + JUMP) as inst:
        inst.clean_jump(192.05e12, 31.58, 0.0952, check=False)


def test_clean_jump_dither():
    """In DITHER the module acknowledges but ignores the jump: refuse before writing."""
    pairs = PROBE_JUMP + LIMITS + [(read(0x90), reply(0x90, 0))]
    with expected_protocol(PPCL300, pairs) as inst, pytest.raises(ValueError):
        inst.clean_jump(192.05e12, 31.58, 0.0952)


def test_clean_jump_not_executed():
    """The module still reports the old frequency (191.5 THz)."""
    pairs = PROBE_JUMP + LIMITS + [(read(0x90), reply(0x90, 1))] + JUMP
    pairs += [(read(0x40), reply(0x40, 191)), (read(0x41), reply(0x41, 5000))]
    with expected_protocol(PPCL300, pairs) as inst, pytest.raises(RuntimeError):
        inst.clean_jump(192.05e12, 31.58, 0.0952)


@pytest.mark.parametrize(
    "frequency, sled_temperature, diode_current, pairs",
    [
        (191e12, 31.58, 0.0952, PROBE_JUMP + LIMITS),  # below frequency_min
        (192.05e12, 3158, 0.0952, []),  # sled temperature in 0.01 °C instead of °C
        (192.05e12, 31.58, 95.2, []),  # current in mA instead of A
        (192.05e12, -1, 0.0952, []),
    ],
)
def test_clean_jump_invalid(frequency, sled_temperature, diode_current, pairs):
    with expected_protocol(PPCL300, pairs) as inst, pytest.raises(ValueError):
        inst.clean_jump(frequency, sled_temperature, diode_current)


def test_clean_jump_frequency_carry():
    """196.25 THz: 0.1 GHz rounding must not produce 10000 in 0xEB."""
    pairs = PROBE_JUMP + LIMITS
    pairs += [
        (write(0xE9, 1131), reply(0xE9, 1131)),
        (write(0xEA, 196), reply(0xEA, 196)),
        (write(0xEB, 2500), reply(0xEB, 2500)),
        (write(0xEC, 2965), reply(0xEC, 2965)),
    ]
    pairs += [(write(0xED, 1), reply(0xED, 1))] * 4
    with expected_protocol(PPCL300, pairs) as inst:
        inst.clean_jump(196.24999999e12, 29.65, 0.1131, check=False)


MAP = (
    "freq = 191.5 sled = 29.14 f1 = 75.966 f2 = 63.791 f1power = 40.84 f2power = 29.16 "
    "current = 918 power = 1000 ambient = 2551\n"
    "freq = 192.05 sled = 31.58 f1 = 76.56 f2 = 62.435 f1power = 38.96 f2power = 26.09 "
    "current = 952 power = 1000 ambient = 2584\n"
    "\n"
)
SERIAL = b"CRTN000001\x00"


def aea(register, data):
    """Read an AEA string register."""
    pairs = [(read(register), reply(register, len(data), status=2))]
    pairs += [
        (read(0x0B), reply(0x0B, int.from_bytes(data[i:i + 2].ljust(2, b"\x00"), "big")))
        for i in range(0, len(data), 2)
    ]
    return pairs


@pytest.fixture
def map_file(tmp_path):
    path = tmp_path / "CRTN000001_1000_1_12_0_0.map"
    path.write_text(MAP)
    return path


def test_load_clean_jump_map(map_file, recwarn):
    """Serial number checked, power setpoint already at the power of the map: no warning."""
    pairs = aea(0x04, SERIAL) + [(read(0x31), reply(0x31, 1000))]
    with expected_protocol(PPCL300, pairs) as inst:
        inst.load_clean_jump_map(map_file)
        assert inst.clean_jump_targets == (191.5e12, 192.05e12)
    assert len(recwarn) == 0


def test_load_clean_jump_map_power_spread(tmp_path, recwarn):
    """Channel powers of Pure Photonics maps differ by 0.01 dBm (e.g. 999 and 1000)."""
    path = tmp_path / "CRTN000001_1000_1.map"
    path.write_text(MAP + MAP.replace("191.5", "191.6").replace("power = 1000", "power = 999"))
    with expected_protocol(PPCL300, [(read(0x31), reply(0x31, 1000))]) as inst:
        inst.load_clean_jump_map(path, check_serial=False)  # 10 dBm: setpoint unchanged
        assert len(inst.clean_jump_targets) == 3
    assert len(recwarn) == 0


def test_load_clean_jump_map_sets_power(map_file):
    pairs = [
        (read(0x31), reply(0x31, 1600)),
        (read(0x50), reply(0x50, 600)),
        (read(0x51), reply(0x51, 1600)),
        (write(0x31, 1000), reply(0x31, 1000)),
    ]
    with expected_protocol(PPCL300, pairs) as inst, pytest.warns(UserWarning, match="16 dBm"):
        inst.load_clean_jump_map(map_file, check_serial=False)


def test_load_clean_jump_map_wrong_serial(map_file):
    with expected_protocol(PPCL300, aea(0x04, b"CRTN000002\x00")) as inst:
        with pytest.raises(ValueError, match="not for laser CRTN000002"):
            inst.load_clean_jump_map(map_file)
        assert inst.clean_jump_targets == ()


@pytest.mark.parametrize(
    "content",
    [
        "freq = 191.5 sled = 29.14 power = 1000\n",  # no current
        (  # two powers
            "freq = 191.5 sled = 29.14 current = 918 power = 1000\n"
            "freq = 191.55 sled = 30.19 current = 927 power = 700\n"
        ),
        "\n",
    ],
)
def test_load_clean_jump_map_invalid(tmp_path, content):
    path = tmp_path / "CRTN000001_1000_1.map"
    path.write_text(content)
    with expected_protocol(PPCL300, []) as inst, pytest.raises(ValueError):
        inst.load_clean_jump_map(path, check_serial=False)


def loaded(more_pairs):
    """Protocol of loading the map (power unchanged) followed by `more_pairs`."""
    return [(read(0x31), reply(0x31, 1000))] + more_pairs


def test_clean_jump_from_map(map_file):
    pairs = loaded(PROBE_JUMP + LIMITS + [(read(0x90), reply(0x90, 1))] + JUMP)
    pairs += [(read(0x40), reply(0x40, 192)), (read(0x41), reply(0x41, 500))]
    with expected_protocol(PPCL300, pairs) as inst:
        inst.load_clean_jump_map(map_file, check_serial=False)
        inst.clean_jump(192.05e12)


@pytest.mark.parametrize("index", [1, -1])
def test_clean_jump_to_target(map_file, index):
    pairs = loaded(PROBE_JUMP + LIMITS + JUMP)
    with expected_protocol(PPCL300, pairs) as inst:
        inst.load_clean_jump_map(map_file, check_serial=False)
        assert inst.clean_jump_to_target(index, check=False) == 192.05e12


def test_clean_jump_to_target_out_of_range(map_file):
    with expected_protocol(PPCL300, loaded([])) as inst:
        inst.load_clean_jump_map(map_file, check_serial=False)
        with pytest.raises(IndexError):
            inst.clean_jump_to_target(2)


def test_clean_jump_targets_read_only(map_file):
    with expected_protocol(PPCL300, loaded([])) as inst:
        inst.load_clean_jump_map(map_file, check_serial=False)
        with pytest.raises(AttributeError):
            inst.clean_jump_targets = (191.5e12,)
        assert inst.clean_jump_targets == (191.5e12, 192.05e12)


def test_clean_jump_not_in_map(map_file):
    with expected_protocol(PPCL300, loaded([])) as inst:
        inst.load_clean_jump_map(map_file, check_serial=False)
        with pytest.raises(ValueError, match="not in the clean jump map"):
            inst.clean_jump(192.1e12)


def test_clean_jump_without_map():
    with expected_protocol(PPCL300, []) as inst, pytest.raises(ValueError, match="No clean"):
        inst.clean_jump(192.05e12)


def test_clean_jump_only_sled_temperature():
    with expected_protocol(PPCL300, []) as inst, pytest.raises(ValueError, match="both"):
        inst.clean_jump(192.05e12, sled_temperature=31.58)


def test_stop_clean_jump():
    with expected_protocol(PPCL300, [(write(0xED, 0), reply(0xED, 0))]) as inst:
        inst.stop_clean_jump()


def rni(register):
    """Answer XE to a command and RNI to the following NOP query."""
    return [(read(register), reply(register, status=1)), (read(0x00), reply(0x00, 0x11))]


def test_features_available():
    """Each feature is tested once, the result is cached."""
    with expected_protocol(PPCL300, PROBE_SWEEP + PROBE_JUMP) as inst:
        assert inst.clean_sweep_available is True
        assert inst.clean_jump_available is True
        assert inst.clean_sweep_available is True
        assert inst.clean_jump_available is True


def test_features_not_available():
    """Firmware 8.0.9 without clean jump (recorded RNI answer)."""
    with expected_protocol(PPCL300, rni(0xE4) + rni(0xEA)) as inst:
        assert inst.clean_sweep_available is False
        assert inst.clean_jump_available is False


def test_feature_probe_other_error():
    """Errors other than RNI are not interpreted as missing feature."""
    pairs = [(read(0xEA), reply(0xEA, status=1)), (read(0x00), reply(0x00, 0x14))]  # CIP
    with expected_protocol(PPCL300, pairs) as inst:
        with pytest.raises(ITLAExecutionError) as exc:
            _ = inst.clean_jump_available
        assert exc.value.error == ITLAError.CIP


def test_clean_jump_not_available():
    """Without clean jump firmware nothing but the probe is sent."""
    with expected_protocol(PPCL300, rni(0xEA)) as inst:
        with pytest.raises(ITLAExecutionError) as exc:
            inst.clean_jump(192.05e12, 31.58, 0.0952)
        assert exc.value.error == ITLAError.RNI


def test_firmware_version():
    """Release string of a PPCL300, read once and cached."""
    data = b"PV 2.0.0:HW 1.0.1:FW 8.0.9:AS C1:OT 2.2.0\x00"
    pairs = [(read(0x06), reply(0x06, len(data), status=2))]
    pairs += [
        (read(0x0B), reply(0x0B, int.from_bytes(data[i:i + 2].ljust(2, b"\x00"), "big")))
        for i in range(0, len(data), 2)
    ]
    with expected_protocol(PPCL300, pairs) as inst:
        assert inst.firmware_version == "8.0.9"
        assert inst.firmware_version == "8.0.9"
