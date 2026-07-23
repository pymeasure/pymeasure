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
from pymeasure.test import expected_protocol
from pymeasure.instruments.koheron import CTL200, KoheronError

# The device replies to every command, settings included, with the echo of the
# command followed by a single value line. Its prompt (">>") terminates neither
# in a newline nor in a space, so it arrives prepended to the echo of the
# following command. A query of the laser current therefore reads on the wire as
#
#     write: b"ilaser\r\n"
#     read:  b"ilaser\r\n200.000\r\n>>"
#
# which is expressed as the two communication pairs
#
#     [("ilaser", "ilaser"), (None, "200.000")]
#
# with every subsequent command echoing as ">>ilaser".

# =============================================================================
# -- Laser Tests
# =============================================================================


def test_laser_enabled():
    """Verify enabling and disabling of the laser output."""
    with expected_protocol(
        CTL200,
        [("lason 1", "lason 1"), (None, "1"),
         ("lason", ">>lason"), (None, "1")],
    ) as inst:
        inst.laser_enabled = True
        assert inst.laser_enabled is True


def test_laser_current_setpoint():
    """Verify laser current setting and its mA to Ampere conversion (scaling
    by 1e3 / 1e-3)."""
    with expected_protocol(
        CTL200,
        [("ilaser 150", "ilaser 150"), (None, "150.000"),
         ("ilaser", ">>ilaser"), (None, "150.000")],
    ) as inst:
        inst.laser_current_setpoint = 0.15
        assert inst.laser_current_setpoint == pytest.approx(0.15)


def test_laser_current_limit():
    """Verify laser current software limit configuration and scaling."""
    with expected_protocol(
        CTL200,
        [("ilmax 500", "ilmax 500"), (None, "500.000"),
         ("ilmax", ">>ilmax"), (None, "500.000")],
    ) as inst:
        inst.laser_current_limit = 0.5
        assert inst.laser_current_limit == pytest.approx(0.5)


def test_laser_current_limit_validator():
    """Verify that strict_range validator blocks current limits outside [0, 1]
    A."""
    with expected_protocol(CTL200, []) as inst:
        with pytest.raises(ValueError):
            inst.laser_current_limit = 1.5


def test_laser_voltage():
    """Verify reading the laser voltage measurement."""
    with expected_protocol(
            CTL200, [("vlaser", "vlaser"), (None, "1.850")]) as inst:
        assert inst.laser_voltage == 1.85


def test_photodiode_current():
    """Verify photodiode current reading and its mA to Ampere scaling
    (1e-3)."""
    with expected_protocol(
            CTL200, [("iphd", "iphd"), (None, "2.500")]) as inst:
        assert inst.photodiode_current == pytest.approx(0.0025)


def test_laser_delay():
    """Verify laser delay control and its ms to seconds scaling."""
    with expected_protocol(
        CTL200,
        [("ldelay 2500", "ldelay 2500"), (None, "2500.000"),
         ("ldelay", ">>ldelay"), (None, "2500.000")],
    ) as inst:
        inst.laser_delay = 2.5
        assert inst.laser_delay == pytest.approx(2.5)


def test_laser_delay_validator():
    """Verify strict_range validator bounds for laser delay ([0.01, 100] s)."""
    with expected_protocol(CTL200, []) as inst:
        with pytest.raises(ValueError):
            inst.laser_delay = 0.005


# =============================================================================
# -- TEC / Temperature Tests
# =============================================================================


def test_tec_enabled():
    """Verify enabling and disabling of the TEC output."""
    with expected_protocol(
        CTL200,
        [("tecon 0", "tecon 0"), (None, "0"),
         ("tecon", ">>tecon"), (None, "0")],
    ) as inst:
        inst.tec_enabled = False
        assert inst.tec_enabled is False


def test_thermistor_setpoint():
    """Verify thermistor resistance setpoint control."""
    with expected_protocol(
        CTL200,
        [("rtset 10000", "rtset 10000"), (None, "10000.000"),
         ("rtset", ">>rtset"), (None, "10000.000")],
    ) as inst:
        inst.thermistor_setpoint = 10000.0
        assert inst.thermistor_setpoint == 10000.0


def test_tec_current():
    """Verify reading the TEC current measurement."""
    with expected_protocol(
            CTL200, [("itec", "itec"), (None, "1.200")]) as inst:
        assert inst.tec_current == 1.2


def test_tec_voltage():
    """Verify reading the TEC voltage measurement."""
    with expected_protocol(
            CTL200, [("vtec", "vtec"), (None, "-0.800")]) as inst:
        assert inst.tec_voltage == -0.8


def test_thermistor_actual():
    """Verify reading the actual thermistor resistance measurement."""
    with expected_protocol(
            CTL200, [("rtact", "rtact"), (None, "9850.500")]) as inst:
        assert inst.thermistor_actual == 9850.5


def test_pid_parameters():
    """Verify control of the proportional, integral, and differential loop
    gains."""
    with expected_protocol(
        CTL200,
        [
            ("pgain 0.1", "pgain 0.1"), (None, "0.100"),
            ("pgain", ">>pgain"), (None, "0.100"),
            ("igain 0.03", ">>igain 0.03"), (None, "0.030"),
            ("igain", ">>igain"), (None, "0.030"),
            ("dgain 0", ">>dgain 0"), (None, "0.000"),
            ("dgain", ">>dgain"), (None, "0.000"),
        ],
    ) as inst:
        inst.pid_proportional = 0.1
        assert inst.pid_proportional == 0.1
        inst.pid_integral = 0.03
        assert inst.pid_integral == 0.03
        inst.pid_differential = 0
        assert inst.pid_differential == 0


@pytest.mark.parametrize("invalid_value", [-0.01, 0.11, -5, 2.0])
def test_pid_parameters_out_of_bounds(invalid_value):
    """Verify that PID gains raise ValueError when set outside the
    [0, 0.1] range."""
    with expected_protocol(CTL200, []) as inst:
        with pytest.raises(ValueError):
            inst.pid_proportional = invalid_value
        with pytest.raises(ValueError):
            inst.pid_integral = invalid_value
        with pytest.raises(ValueError):
            inst.pid_differential = invalid_value


# =============================================================================
# -- Protection Tests
# =============================================================================


def test_temp_protection_enabled():
    """Verify configuration of the temperature protection switch."""
    with expected_protocol(
        CTL200,
        [("tprot 1", "tprot 1"), (None, "1"),
         ("tprot", ">>tprot"), (None, "1")],
    ) as inst:
        inst.temp_protection_enabled = True
        assert inst.temp_protection_enabled is True


def test_thermistor_windows():
    """Verify minimum and maximum thermistor resistance window control."""
    with expected_protocol(
        CTL200,
        [
            ("rtmin 5000", "rtmin 5000"), (None, "5000.000"),
            ("rtmin", ">>rtmin"), (None, "5000.000"),
            ("rtmax 15000", ">>rtmax 15000"), (None, "15000.000"),
            ("rtmax", ">>rtmax"), (None, "15000.000"),
        ],
    ) as inst:
        inst.thermistor_window_min = 5000.0
        assert inst.thermistor_window_min == 5000.0
        inst.thermistor_window_max = 15000.0
        assert inst.thermistor_window_max == 15000.0


def test_tec_voltage_limits():
    """Verify minimum and maximum TEC voltage limit configuration within
    bounds."""
    with expected_protocol(
        CTL200,
        [
            ("vtmin -2.5", "vtmin -2.5"), (None, "-2.500"),
            ("vtmin", ">>vtmin"), (None, "-2.500"),
            ("vtmax 2.5", ">>vtmax 2.5"), (None, "2.500"),
            ("vtmax", ">>vtmax"), (None, "2.500"),
        ],
    ) as inst:
        inst.tec_voltage_limit_min = -2.5
        assert inst.tec_voltage_limit_min == -2.5
        inst.tec_voltage_limit_max = 2.5
        assert inst.tec_voltage_limit_max == 2.5


@pytest.mark.parametrize("invalid_min", [0.5, -3.5])
@pytest.mark.parametrize("invalid_max", [-1.0, 3.5])
def test_tec_voltage_limits_validators(invalid_min, invalid_max):
    """Verify that strict_range validators trigger on invalid TEC voltage
    limits."""
    # vtmin range: [-3.0, 0.0] | vtmax range: [0.0, 3.0]
    with expected_protocol(CTL200, []) as inst:
        with pytest.raises(ValueError):
            inst.tec_voltage_limit_min = invalid_min
        with pytest.raises(ValueError):
            inst.tec_voltage_limit_max = invalid_max


# =============================================================================
# -- Interlock Tests
# =============================================================================


def test_interlock_enabled():
    """Verify hardware interlock switch control."""
    with expected_protocol(
        CTL200,
        [("lckon 1", "lckon 1"), (None, "1"),
         ("lckon", ">>lckon"), (None, "1")],
    ) as inst:
        inst.interlock_enabled = True
        assert inst.interlock_enabled is True


# =============================================================================
# -- Aux Inputs Tests
# =============================================================================


def test_analog_inputs():
    """Verify reading of auxiliary analog input voltages."""
    with expected_protocol(
        CTL200,
        [("ain1", "ain1"), (None, "0.230"),
         ("ain2", ">>ain2"), (None, "1.450")],
    ) as inst:
        assert inst.analog_input_1 == 0.23
        assert inst.analog_input_2 == 1.45


def test_laser_modulation_gain():
    """Verify modulation gain scaling logic for auxiliary input 1."""
    with expected_protocol(
        CTL200,
        [("lmodgain 50", "lmodgain 50"), (None, "50.000"),
         ("lmodgain", ">>lmodgain"), (None, "50.000")],
    ) as inst:
        inst.laser_modulation_gain = 0.05
        assert inst.laser_modulation_gain == pytest.approx(0.05)


def test_laser_modulation_gain_validator():
    """Verify strict_range validator limits for laser modulation gain
    ([-100, 100])."""
    with expected_protocol(CTL200, []) as inst:
        with pytest.raises(ValueError):
            inst.laser_modulation_gain = 150


def test_tec_modulation_gain():
    """Verify temperature modulation gain configuration
    (no internal scaling)."""
    with expected_protocol(
        CTL200,
        [("tmodgain 5000", "tmodgain 5000"), (None, "5000.000"),
         ("tmodgain", ">>tmodgain"), (None, "5000.000")],
    ) as inst:
        inst.tec_modulation_gain = 5000.0
        assert inst.tec_modulation_gain == 5000.0


def test_tec_modulation_gain_validator():
    """Verify strict_range validator bounds for TEC modulation gain
    ([-100000, 100000])."""
    with expected_protocol(CTL200, []) as inst:
        with pytest.raises(ValueError):
            inst.tec_modulation_gain = 200000


# =============================================================================
# -- Misc & Methods Tests
# =============================================================================


def test_versions():
    """Verify firmware and board model identifier acquisition."""
    with expected_protocol(
        CTL200,
        [("version", "version"), (None, "v0.17"),
         ("model", ">>model"), (None, "CTL200-0")],
    ) as inst:
        assert inst.firmware_version == "v0.17"
        assert inst.board_version == "CTL200-0"


def test_serial_number():
    """Verify serial number acquisition."""
    with expected_protocol(
            CTL200, [("serial", "serial"), (None, "0123456789")]) as inst:
        assert inst.serial_number == "0123456789"


def test_baud_rate_setting():
    """Verify configuration of the device UART baud rate."""
    with expected_protocol(
        CTL200,
        [("brate 9600", "brate 9600"), (None, "9600"),
         ("brate", ">>brate"), (None, "9600")],
    ) as inst:
        inst.baud_rate_setting = 9600
        assert inst.baud_rate_setting == 9600


@pytest.mark.parametrize("invalid_value", [4800, 921600])
def test_baud_rate_setting_validator(invalid_value):
    """Verify strict_range validator bounds for the baud rate
    ([9600, 460800])."""
    with expected_protocol(CTL200, []) as inst:
        with pytest.raises(ValueError):
            inst.baud_rate_setting = invalid_value


def test_user_data():
    """Verify writing and reading the user data string."""
    with expected_protocol(
        CTL200,
        [("userdata write TEST", "userdata write TEST"), (None, "TEST"),
         ("userdata", ">>userdata"), (None, "TEST")],
    ) as inst:
        inst.user_data = "TEST"
        assert inst.user_data == "TEST"


def test_user_data_truncation():
    """Verify that the user data string is truncated to 31 characters."""
    long_data = "x" * 40
    with expected_protocol(
        CTL200,
        [("userdata write " + "x" * 31, "userdata write " + "x" * 31),
         (None, "x" * 31)],
    ) as inst:
        inst.user_data = long_data


def test_board_temperature():
    """Verify reading of internal driver board temperature."""
    with expected_protocol(
            CTL200, [("tboard", "tboard"), (None, "34.500")]) as inst:
        assert inst.board_temperature == 34.5


def test_status_property():
    """Verify complex multi-value parsing and custom scaling of the status
    property."""
    status_response = "1 1.8 0.5 2.1 10000.0 1.5 0.05 0.1"
    with expected_protocol(
            CTL200, [("status", "status"), (None, status_response)]) as inst:
        res = inst.status
        assert res["lason"] == 1.0
        assert res["vlaser"] == 1.8
        assert res["itec"] == 0.5
        assert res["vtec"] == 2.1
        assert res["rtact"] == 10000.0
        assert res["iphd"] == pytest.approx(0.0015)
        assert res["ain1"] == 0.05
        assert res["ain2"] == 0.1


def test_commands():
    """Verify command execution for parameter persistence and error clear
    states."""
    with expected_protocol(
        CTL200,
        [("save", "save"), (None, "config saved"),
         ("errclr", ">>errclr"), (None, "ffffffff")],
    ) as inst:
        inst.save()
        inst.clear_error()


@pytest.mark.parametrize("response, expected", [
    ("0", KoheronError.NONE),
    ("1", KoheronError.UART_BUFFER_OVERFLOW),
    ("5", KoheronError.UART_BUFFER_OVERFLOW | KoheronError.LASER_UNDERTEMPERATURE),
    # The error code is returned in hexadecimal format.
    ("a0", KoheronError.CMD_INVALID_ARG | KoheronError.INTERLOCK_TRIGGERED),
])
def test_error_status(response, expected):
    """Verify that the error status is parsed into the matching flags."""
    with expected_protocol(
            CTL200, [("err", "err"), (None, response)]) as inst:
        assert inst.error_status == expected


def test_check_errors_without_error():
    """Verify that no error status yields no errors and does not clear."""
    with expected_protocol(
            CTL200, [("err", "err"), (None, "0")]) as inst:
        assert inst.check_errors() == []


def test_check_errors_with_errors():
    """Verify that a combined error flag is decomposed into its single errors
    and cleared afterwards."""
    # 0x5 == UART_BUFFER_OVERFLOW (0x1) | LASER_UNDERTEMPERATURE (0x4)
    with expected_protocol(
        CTL200,
        [("err", "err"), (None, "5"),
         ("errclr", ">>errclr"), (None, "ffffffff")],
    ) as inst:
        assert inst.check_errors() == [
            "UART_BUFFER_OVERFLOW",
            "LASER_UNDERTEMPERATURE",
        ]
